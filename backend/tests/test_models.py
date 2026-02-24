from app.models import Book, Page, PageType, FontPreset, Language, PageContent, Order, OrderStatus


def test_create_book(db):
    book = Book(title="Joya Test", page_size="8.5x11", bleed_mm=3.0)
    db.add(book)
    db.commit()
    db.refresh(book)
    assert book.id is not None
    assert book.title == "Joya Test"


def test_create_page_with_book(db):
    book = Book(title="Joya Test")
    db.add(book)
    db.commit()
    page = Page(book_id=book.id, page_number=1, page_type=PageType.cover, is_personalizable=True)
    db.add(page)
    db.commit()
    assert page.book_id == book.id
    assert page.is_personalizable is True


def test_create_font_preset(db):
    preset = FontPreset(
        language=Language.vi,
        font_family="NotoSans",
        font_file_url="/fonts/NotoSans-Regular.ttf",
        font_size=14.0,
        line_height=1.5,
    )
    db.add(preset)
    db.commit()
    assert preset.line_height == 1.5


def test_create_page_content_with_placeholder(db):
    book = Book(title="Joya Test")
    db.add(book)
    db.commit()
    page = Page(book_id=book.id, page_number=1, page_type=PageType.cover)
    db.add(page)
    db.commit()
    content = PageContent(
        page_id=page.id,
        language=Language.ko,
        text_content="안녕하세요 {NAME}님, {DATE}에 태어났군요!",
    )
    db.add(content)
    db.commit()
    assert "{NAME}" in content.text_content


def test_create_order(db):
    book = Book(title="Joya Test")
    db.add(book)
    db.commit()
    order = Order(
        book_id=book.id,
        main_language=Language.ko,
        sub_languages=["en", "vi", "fr"],
        person_name="지민",
        person_date="2020-03-15",
    )
    db.add(order)
    db.commit()
    assert order.status == OrderStatus.pending
    assert len(order.sub_languages) == 3
