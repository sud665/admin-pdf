from dataclasses import dataclass, field

from reportlab.lib.units import mm, inch
from reportlab.lib.colors import CMYKColor
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT

from app.engine.font_manager import FontManager
from app.engine.text_processor import normalize_text


@dataclass
class TextBlock:
    text: str
    font_name: str
    font_file: str
    font_size: float
    x: float  # points from left
    y: float  # points from bottom
    width: float  # points
    height: float  # points
    line_height: float = 1.2
    letter_spacing: float = 0.0


@dataclass
class PageSpec:
    page_number: int
    bg_image_path: str | None = None
    text_blocks: list[TextBlock] = field(default_factory=list)


class PDFGenerator:
    # 8.5 x 11 inch in points
    PAGE_WIDTH = 8.5 * inch
    PAGE_HEIGHT = 11 * inch

    def __init__(self, font_dir: str = "fonts"):
        self.font_manager = FontManager(font_dir=font_dir)
        self.font_dir = font_dir

    def generate(
        self,
        output_path: str,
        pages: list[PageSpec],
        bleed_mm: float = 3.0,
    ) -> str:
        bleed_pt = bleed_mm * mm
        page_w = self.PAGE_WIDTH + (bleed_pt * 2)
        page_h = self.PAGE_HEIGHT + (bleed_pt * 2)

        c = canvas.Canvas(output_path, pagesize=(page_w, page_h))

        for page_spec in pages:
            # Background image
            if page_spec.bg_image_path:
                try:
                    c.drawImage(
                        page_spec.bg_image_path,
                        0, 0, page_w, page_h,
                        preserveAspectRatio=False,
                    )
                except Exception:
                    pass  # Skip missing images gracefully

            # Text blocks
            for block in page_spec.text_blocks:
                self._render_text_block(c, block, bleed_pt)

            c.showPage()

        c.save()
        return output_path

    def _render_text_block(self, c: canvas.Canvas, block: TextBlock, bleed_pt: float):
        # Register font if needed (skip for built-in fonts)
        if block.font_file:
            self.font_manager.register_font(block.font_name, block.font_file)

        # Normalize text (NFC for Vietnamese/French accents)
        text = normalize_text(block.text)

        # Escape XML special characters for Paragraph
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        # Create paragraph style
        style = ParagraphStyle(
            name=f"style_{id(block)}",
            fontName=block.font_name,
            fontSize=block.font_size,
            leading=block.font_size * block.line_height,
            alignment=TA_LEFT,
            textColor=CMYKColor(0, 0, 0, 1),  # Pure black in CMYK
        )

        # Render with Paragraph for auto line-wrapping
        para = Paragraph(text.replace("\n", "<br/>"), style)
        para.wrap(block.width, block.height)
        # Position adjusted for bleed
        para.drawOn(c, block.x + bleed_pt, block.y + bleed_pt)
