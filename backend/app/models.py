import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Boolean,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Language(str, enum.Enum):
    ko = "ko"
    en = "en"
    vi = "vi"
    fr = "fr"


class PageType(str, enum.Enum):
    cover = "cover"
    opening = "opening"
    story = "story"
    closing = "closing"


class OrderStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    timeout = "timeout"


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    page_size = Column(String(20), nullable=False, default="8.5x11")
    bleed_mm = Column(Float, nullable=False, default=3.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    pages = relationship("Page", back_populates="book", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="book")


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    page_type = Column(Enum(PageType), nullable=False)
    bg_image_url = Column(String(500), nullable=True)
    text_area_x = Column(Float, nullable=False, default=50.0)
    text_area_y = Column(Float, nullable=False, default=50.0)
    text_area_w = Column(Float, nullable=False, default=500.0)
    text_area_h = Column(Float, nullable=False, default=300.0)
    is_personalizable = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    book = relationship("Book", back_populates="pages")
    contents = relationship("PageContent", back_populates="page", cascade="all, delete-orphan")


class FontPreset(Base):
    __tablename__ = "font_presets"

    id = Column(Integer, primary_key=True, index=True)
    language = Column(Enum(Language), nullable=False)
    font_family = Column(String(255), nullable=False)
    font_file_url = Column(String(500), nullable=False)
    font_size = Column(Float, nullable=False, default=12.0)
    letter_spacing = Column(Float, nullable=False, default=0.0)
    line_height = Column(Float, nullable=False, default=1.2)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    contents = relationship("PageContent", back_populates="font_preset")


class PageContent(Base):
    __tablename__ = "page_contents"

    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    language = Column(Enum(Language), nullable=False)
    text_content = Column(Text, nullable=False, default="")
    font_preset_id = Column(Integer, ForeignKey("font_presets.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    page = relationship("Page", back_populates="contents")
    font_preset = relationship("FontPreset", back_populates="contents")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    main_language = Column(Enum(Language), nullable=False)
    sub_languages = Column(JSON, nullable=False)
    person_name = Column(String(100), nullable=False)
    person_date = Column(String(20), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.pending)
    pdf_url = Column(String(500), nullable=True)
    warning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    book = relationship("Book", back_populates="orders")
