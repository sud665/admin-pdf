import os
import tempfile

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.engine.pdf_generator import PDFGenerator, PageSpec, TextBlock
from app.engine.text_processor import normalize_text, substitute_placeholders
from app.models import Book, FontPreset, Order, OrderStatus, Page, PageContent
from app.schemas import GenerateRequest, OrderOut

router = APIRouter(prefix="/api/generate", tags=["generate"])

# Directory for generated PDFs
PDF_OUTPUT_DIR = os.path.join(tempfile.gettempdir(), "joya_pdfs")
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)


def _build_page_specs(
    pages: list[Page],
    languages: list[str],
    person_name: str,
    person_date: str,
    db: Session,
) -> list[PageSpec]:
    page_specs = []
    for page in pages:
        text_blocks = []
        for i, lang in enumerate(languages):
            content = (
                db.query(PageContent)
                .filter(PageContent.page_id == page.id, PageContent.language == lang)
                .first()
            )
            if not content:
                continue

            text = content.text_content
            if page.is_personalizable:
                text = substitute_placeholders(text, name=person_name, date=person_date)
            text = normalize_text(text)

            font_preset = None
            if content.font_preset_id:
                font_preset = (
                    db.query(FontPreset)
                    .filter(FontPreset.id == content.font_preset_id)
                    .first()
                )

            # Stack languages vertically in text area
            lang_height = page.text_area_h / len(languages)
            lang_offset = i * lang_height

            block = TextBlock(
                text=text,
                font_name=font_preset.font_family if font_preset else "Helvetica",
                font_file=font_preset.font_file_url if font_preset else "",
                font_size=font_preset.font_size if font_preset else (18 if i == 0 else 12),
                x=page.text_area_x,
                y=page.text_area_y - lang_offset,
                width=page.text_area_w,
                height=lang_height,
                line_height=font_preset.line_height if font_preset else 1.2,
            )
            text_blocks.append(block)

        bg_path = None
        if page.bg_image_url and os.path.exists(page.bg_image_url):
            bg_path = page.bg_image_url

        page_specs.append(
            PageSpec(
                page_number=page.page_number,
                bg_image_path=bg_path,
                text_blocks=text_blocks,
            )
        )
    return page_specs


@router.post("", response_model=OrderOut, status_code=201)
def generate_pdf(body: GenerateRequest, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == body.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    pages = (
        db.query(Page)
        .filter(Page.book_id == book.id)
        .order_by(Page.page_number)
        .all()
    )
    if not pages:
        raise HTTPException(status_code=422, detail="Book has no pages")

    # Create order
    order = Order(
        book_id=book.id,
        main_language=body.main_language,
        sub_languages=[lang.value for lang in body.sub_languages],
        person_name=body.person_name,
        person_date=body.person_date,
        status=OrderStatus.processing,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Build language list (main first, then subs)
    languages = [body.main_language.value] + [l.value for l in body.sub_languages]

    try:
        page_specs = _build_page_specs(
            pages, languages, body.person_name, body.person_date, db
        )
        generator = PDFGenerator(font_dir=settings.font_dir)

        os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(PDF_OUTPUT_DIR, f"joya_order_{order.id}.pdf")
        generator.generate(
            output_path=output_path,
            pages=page_specs,
            bleed_mm=book.bleed_mm,
        )

        order.pdf_url = output_path
        order.status = OrderStatus.completed
        db.commit()
        db.refresh(order)

    except Exception as e:
        order.status = OrderStatus.failed
        order.warning = str(e)
        db.commit()
        db.refresh(order)
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

    return order


@router.get("/download/{order_id}")
def download_pdf(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not order.pdf_url or not os.path.exists(order.pdf_url):
        raise HTTPException(status_code=404, detail="PDF file not found")
    return FileResponse(
        order.pdf_url,
        media_type="application/pdf",
        filename=f"joya_order_{order.id}.pdf",
    )
