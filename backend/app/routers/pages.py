from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Page, Book, PageContent
from app.schemas import (
    PageCreate,
    PageUpdate,
    PageOut,
    PageContentCreate,
    PageContentUpdate,
    PageContentOut,
)

router = APIRouter(prefix="/api/books/{book_id}/pages", tags=["pages"])


def _get_book(book_id: int, db: Session):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("", response_model=PageOut, status_code=201)
def create_page(book_id: int, body: PageCreate, db: Session = Depends(get_db)):
    _get_book(book_id, db)
    page = Page(book_id=book_id, **body.model_dump())
    db.add(page)
    db.commit()
    db.refresh(page)
    return page


@router.get("", response_model=list[PageOut])
def list_pages(book_id: int, db: Session = Depends(get_db)):
    _get_book(book_id, db)
    return db.query(Page).filter(Page.book_id == book_id).order_by(Page.page_number).all()


@router.get("/{page_id}", response_model=PageOut)
def get_page(book_id: int, page_id: int, db: Session = Depends(get_db)):
    page = db.query(Page).filter(Page.id == page_id, Page.book_id == book_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page


@router.patch("/{page_id}", response_model=PageOut)
def update_page(book_id: int, page_id: int, body: PageUpdate, db: Session = Depends(get_db)):
    page = db.query(Page).filter(Page.id == page_id, Page.book_id == book_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(page, key, val)
    db.commit()
    db.refresh(page)
    return page


@router.delete("/{page_id}", status_code=204)
def delete_page(book_id: int, page_id: int, db: Session = Depends(get_db)):
    page = db.query(Page).filter(Page.id == page_id, Page.book_id == book_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    db.delete(page)
    db.commit()


# --- PageContent (하위 리소스) ---
@router.post("/{page_id}/contents", response_model=PageContentOut, status_code=201)
def create_content(book_id: int, page_id: int, body: PageContentCreate, db: Session = Depends(get_db)):
    page = db.query(Page).filter(Page.id == page_id, Page.book_id == book_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    content = PageContent(page_id=page_id, **body.model_dump())
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


@router.get("/{page_id}/contents", response_model=list[PageContentOut])
def list_contents(book_id: int, page_id: int, db: Session = Depends(get_db)):
    return db.query(PageContent).filter(PageContent.page_id == page_id).all()


@router.patch("/{page_id}/contents/{content_id}", response_model=PageContentOut)
def update_content(
    book_id: int,
    page_id: int,
    content_id: int,
    body: PageContentUpdate,
    db: Session = Depends(get_db),
):
    content = (
        db.query(PageContent)
        .filter(PageContent.id == content_id, PageContent.page_id == page_id)
        .first()
    )
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(content, key, val)
    db.commit()
    db.refresh(content)
    return content
