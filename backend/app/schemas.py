from datetime import datetime

from pydantic import BaseModel

from app.models import Language, PageType, OrderStatus


# --- Book ---
class BookCreate(BaseModel):
    title: str
    page_size: str = "8.5x11"
    bleed_mm: float = 3.0


class BookUpdate(BaseModel):
    title: str | None = None
    page_size: str | None = None
    bleed_mm: float | None = None


class BookOut(BaseModel):
    id: int
    title: str
    page_size: str
    bleed_mm: float
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Page ---
class PageCreate(BaseModel):
    page_number: int
    page_type: PageType
    bg_image_url: str | None = None
    text_area_x: float = 50.0
    text_area_y: float = 50.0
    text_area_w: float = 500.0
    text_area_h: float = 300.0
    is_personalizable: bool = False


class PageUpdate(BaseModel):
    page_number: int | None = None
    page_type: PageType | None = None
    bg_image_url: str | None = None
    text_area_x: float | None = None
    text_area_y: float | None = None
    text_area_w: float | None = None
    text_area_h: float | None = None
    is_personalizable: bool | None = None


class PageOut(BaseModel):
    id: int
    book_id: int
    page_number: int
    page_type: PageType
    bg_image_url: str | None
    text_area_x: float
    text_area_y: float
    text_area_w: float
    text_area_h: float
    is_personalizable: bool

    model_config = {"from_attributes": True}


# --- FontPreset ---
class FontPresetCreate(BaseModel):
    language: Language
    font_family: str
    font_file_url: str
    font_size: float = 12.0
    letter_spacing: float = 0.0
    line_height: float = 1.2


class FontPresetUpdate(BaseModel):
    font_family: str | None = None
    font_file_url: str | None = None
    font_size: float | None = None
    letter_spacing: float | None = None
    line_height: float | None = None


class FontPresetOut(BaseModel):
    id: int
    language: Language
    font_family: str
    font_file_url: str
    font_size: float
    letter_spacing: float
    line_height: float

    model_config = {"from_attributes": True}


# --- PageContent ---
class PageContentCreate(BaseModel):
    language: Language
    text_content: str = ""
    font_preset_id: int | None = None


class PageContentUpdate(BaseModel):
    text_content: str | None = None
    font_preset_id: int | None = None


class PageContentOut(BaseModel):
    id: int
    page_id: int
    language: Language
    text_content: str
    font_preset_id: int | None

    model_config = {"from_attributes": True}


# --- Order ---
class OrderCreate(BaseModel):
    book_id: int
    main_language: Language
    sub_languages: list[Language]
    person_name: str
    person_date: str


class OrderOut(BaseModel):
    id: int
    book_id: int
    main_language: Language
    sub_languages: list[str]
    person_name: str
    person_date: str
    status: OrderStatus
    pdf_url: str | None
    warning: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- PDF Generate ---
class GenerateRequest(BaseModel):
    book_id: int
    main_language: Language
    sub_languages: list[Language]
    person_name: str
    person_date: str
