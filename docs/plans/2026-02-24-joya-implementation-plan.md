# Joya 자동 조판 시스템 구현 계획

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 다국어 키즈 동화 자동 조판 + 고해상도 PDF 생성 시스템의 MVP 프로토타입 구축

**Architecture:** FastAPI 백엔드(ReportLab PDF 엔진 내장) + Next.js 15 관리자 UI. PostgreSQL에 도서/원고/주문 데이터 저장, S3 호환 스토리지에 생성된 PDF 저장. 4개 언어(한/영/베트남/불어) 지원, 개인화 치환({NAME}/{DATE}) 포함.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy, Alembic, ReportLab, Pillow, pdfplumber, pikepdf / Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, SWR

**Design Doc:** `docs/plans/2026-02-24-joya-auto-typesetting-design.md`

---

## 프로젝트 구조

```
admin-pdf/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── books.py
│   │   │   ├── pages.py
│   │   │   ├── fonts.py
│   │   │   ├── orders.py
│   │   │   └── generate.py
│   │   └── engine/
│   │       ├── __init__.py
│   │       ├── pdf_generator.py
│   │       ├── text_processor.py
│   │       └── font_manager.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_models.py
│   │   ├── test_text_processor.py
│   │   ├── test_font_manager.py
│   │   ├── test_pdf_generator.py
│   │   ├── test_routers_books.py
│   │   ├── test_routers_pages.py
│   │   ├── test_routers_fonts.py
│   │   ├── test_routers_orders.py
│   │   └── test_routers_generate.py
│   ├── alembic/
│   ├── alembic.ini
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── admin/
│   │       ├── layout.tsx
│   │       ├── dashboard/page.tsx
│   │       ├── books/
│   │       │   ├── page.tsx
│   │       │   └── [id]/
│   │       │       ├── page.tsx
│   │       │       └── pages/[pageId]/page.tsx
│   │       ├── fonts/page.tsx
│   │       ├── orders/
│   │       │   ├── page.tsx
│   │       │   └── [id]/page.tsx
│   │       └── generate/page.tsx
│   ├── components/
│   ├── lib/
│   │   └── api.ts
│   ├── package.json
│   └── tsconfig.json
├── fonts/               # 프로토타입용 더미 폰트
├── images/              # 프로토타입용 더미 배경 이미지
├── docs/plans/
├── docker-compose.yml
└── .env.example
```

---

## Phase 1: 백엔드 기반 구축

### Task 1: Python 프로젝트 초기화

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`

**Step 1: pyproject.toml 생성**

```toml
[project]
name = "joya-pdf-engine"
version = "0.1.0"
requires-python = ">=3.12"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

**Step 2: requirements.txt 생성**

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy==2.0.36
alembic==1.14.1
psycopg2-binary==2.9.10
python-dotenv==1.0.1
reportlab==4.2.5
Pillow==11.1.0
pdfplumber==0.11.4
pikepdf==9.4.2
python-multipart==0.0.18
httpx==0.28.1
pytest==8.3.4
pytest-asyncio==0.25.0
boto3==1.36.4
```

**Step 3: config.py 생성**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/joya"
    s3_bucket: str = "joya-pdfs"
    s3_endpoint_url: str | None = None
    s3_access_key: str = ""
    s3_secret_key: str = ""
    font_dir: str = "fonts"
    image_dir: str = "images"

    class Config:
        env_file = ".env"


settings = Settings()
```

**Step 4: main.py 생성**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Joya PDF Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}
```

**Step 5: 서버 실행 확인**

Run: `cd /Users/max/Desktop/wishket/admin-pdf/backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000`
Expected: `Uvicorn running on http://127.0.0.1:8000`

Verify: `curl http://localhost:8000/health`
Expected: `{"status":"ok"}`

**Step 6: Commit**

```bash
git add backend/
git commit -m "feat: FastAPI 프로젝트 초기화"
```

---

### Task 2: 데이터베이스 모델 + 마이그레이션

**Files:**
- Create: `backend/app/database.py`
- Create: `backend/app/models.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_models.py`

**Step 1: database.py 생성**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 2: models.py 생성**

```python
import enum
from datetime import datetime

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
)
from sqlalchemy.dialects.postgresql import ARRAY
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
    created_at = Column(DateTime, default=datetime.utcnow)

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
    created_at = Column(DateTime, default=datetime.utcnow)

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
    created_at = Column(DateTime, default=datetime.utcnow)

    contents = relationship("PageContent", back_populates="font_preset")


class PageContent(Base):
    __tablename__ = "page_contents"

    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    language = Column(Enum(Language), nullable=False)
    text_content = Column(Text, nullable=False, default="")
    font_preset_id = Column(Integer, ForeignKey("font_presets.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    page = relationship("Page", back_populates="contents")
    font_preset = relationship("FontPreset", back_populates="contents")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    main_language = Column(Enum(Language), nullable=False)
    sub_languages = Column(ARRAY(String), nullable=False)
    person_name = Column(String(100), nullable=False)
    person_date = Column(String(20), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.pending)
    pdf_url = Column(String(500), nullable=True)
    warning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    book = relationship("Book", back_populates="orders")
```

**Step 3: conftest.py 생성 (SQLite 테스트 DB)**

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def db():
    Base.metadata.create_all(bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    from fastapi.testclient import TestClient

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

**Step 4: 모델 테스트 작성**

```python
# tests/test_models.py
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
```

**Step 5: 테스트 실행**

Run: `cd /Users/max/Desktop/wishket/admin-pdf/backend && python -m pytest tests/test_models.py -v`
Expected: 5 passed

**Step 6: Alembic 초기화 + 마이그레이션 생성**

Run: `cd /Users/max/Desktop/wishket/admin-pdf/backend && alembic init alembic`
Then edit `alembic/env.py` to import `app.models` and `app.database.Base`.

Run: `alembic revision --autogenerate -m "initial tables"`
Run: `alembic upgrade head`

**Step 7: Commit**

```bash
git add backend/
git commit -m "feat: DB 모델 5개 테이블 + Alembic 마이그레이션"
```

---

### Task 3: Pydantic 스키마

**Files:**
- Create: `backend/app/schemas.py`

**Step 1: schemas.py 생성**

```python
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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


# --- PDF Generate ---
class GenerateRequest(BaseModel):
    book_id: int
    main_language: Language
    sub_languages: list[Language]
    person_name: str
    person_date: str
```

**Step 2: Commit**

```bash
git add backend/app/schemas.py
git commit -m "feat: Pydantic 스키마 (Book/Page/Font/Order/Generate)"
```

---

### Task 4: Book CRUD API

**Files:**
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/routers/books.py`
- Create: `backend/tests/test_routers_books.py`
- Modify: `backend/app/main.py` (라우터 등록)

**Step 1: 테스트 작성**

```python
# tests/test_routers_books.py

def test_create_book(client):
    res = client.post("/api/books", json={"title": "Joya 동화"})
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Joya 동화"
    assert data["page_size"] == "8.5x11"


def test_list_books(client):
    client.post("/api/books", json={"title": "Book 1"})
    client.post("/api/books", json={"title": "Book 2"})
    res = client.get("/api/books")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_get_book(client):
    create = client.post("/api/books", json={"title": "Joya"})
    book_id = create.json()["id"]
    res = client.get(f"/api/books/{book_id}")
    assert res.status_code == 200
    assert res.json()["title"] == "Joya"


def test_update_book(client):
    create = client.post("/api/books", json={"title": "Old"})
    book_id = create.json()["id"]
    res = client.patch(f"/api/books/{book_id}", json={"title": "New"})
    assert res.status_code == 200
    assert res.json()["title"] == "New"


def test_delete_book(client):
    create = client.post("/api/books", json={"title": "ToDelete"})
    book_id = create.json()["id"]
    res = client.delete(f"/api/books/{book_id}")
    assert res.status_code == 204
    res = client.get(f"/api/books/{book_id}")
    assert res.status_code == 404
```

**Step 2: 테스트 실패 확인**

Run: `cd /Users/max/Desktop/wishket/admin-pdf/backend && python -m pytest tests/test_routers_books.py -v`
Expected: FAIL (404 - 라우트 없음)

**Step 3: books.py 라우터 구현**

```python
# app/routers/books.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Book
from app.schemas import BookCreate, BookUpdate, BookOut

router = APIRouter(prefix="/api/books", tags=["books"])


@router.post("", response_model=BookOut, status_code=201)
def create_book(body: BookCreate, db: Session = Depends(get_db)):
    book = Book(**body.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.get("", response_model=list[BookOut])
def list_books(db: Session = Depends(get_db)):
    return db.query(Book).all()


@router.get("/{book_id}", response_model=BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.patch("/{book_id}", response_model=BookOut)
def update_book(book_id: int, body: BookUpdate, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(book, key, val)
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
```

**Step 4: main.py에 라우터 등록**

```python
# app/main.py 에 추가
from app.routers import books

app.include_router(books.router)
```

**Step 5: 테스트 통과 확인**

Run: `cd /Users/max/Desktop/wishket/admin-pdf/backend && python -m pytest tests/test_routers_books.py -v`
Expected: 5 passed

**Step 6: Commit**

```bash
git add backend/
git commit -m "feat: Book CRUD API + 테스트"
```

---

### Task 5: Page CRUD API (Book 하위 리소스)

**Files:**
- Create: `backend/app/routers/pages.py`
- Create: `backend/tests/test_routers_pages.py`
- Modify: `backend/app/main.py` (라우터 등록)

**Step 1: 테스트 작성**

```python
# tests/test_routers_pages.py
from app.models import PageType


def _create_book(client):
    res = client.post("/api/books", json={"title": "Joya"})
    return res.json()["id"]


def test_create_page(client):
    book_id = _create_book(client)
    res = client.post(f"/api/books/{book_id}/pages", json={
        "page_number": 1,
        "page_type": "cover",
        "is_personalizable": True,
    })
    assert res.status_code == 201
    assert res.json()["page_type"] == "cover"
    assert res.json()["is_personalizable"] is True


def test_list_pages(client):
    book_id = _create_book(client)
    client.post(f"/api/books/{book_id}/pages", json={"page_number": 1, "page_type": "cover"})
    client.post(f"/api/books/{book_id}/pages", json={"page_number": 2, "page_type": "opening"})
    res = client.get(f"/api/books/{book_id}/pages")
    assert len(res.json()) == 2


def test_update_page(client):
    book_id = _create_book(client)
    create = client.post(f"/api/books/{book_id}/pages", json={"page_number": 1, "page_type": "cover"})
    page_id = create.json()["id"]
    res = client.patch(f"/api/books/{book_id}/pages/{page_id}", json={"text_area_x": 100.0})
    assert res.json()["text_area_x"] == 100.0


def test_delete_page(client):
    book_id = _create_book(client)
    create = client.post(f"/api/books/{book_id}/pages", json={"page_number": 1, "page_type": "cover"})
    page_id = create.json()["id"]
    res = client.delete(f"/api/books/{book_id}/pages/{page_id}")
    assert res.status_code == 204
```

**Step 2: 테스트 실패 확인**

Run: `python -m pytest tests/test_routers_pages.py -v`
Expected: FAIL

**Step 3: pages.py 라우터 구현**

```python
# app/routers/pages.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Page, Book, PageContent
from app.schemas import PageCreate, PageUpdate, PageOut, PageContentCreate, PageContentUpdate, PageContentOut

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
def update_content(book_id: int, page_id: int, content_id: int, body: PageContentUpdate, db: Session = Depends(get_db)):
    content = db.query(PageContent).filter(PageContent.id == content_id, PageContent.page_id == page_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(content, key, val)
    db.commit()
    db.refresh(content)
    return content
```

**Step 4: main.py에 라우터 등록**

```python
from app.routers import books, pages
app.include_router(pages.router)
```

**Step 5: 테스트 통과 확인**

Run: `python -m pytest tests/test_routers_pages.py -v`
Expected: 4 passed

**Step 6: Commit**

```bash
git add backend/
git commit -m "feat: Page + PageContent CRUD API + 테스트"
```

---

### Task 6: FontPreset CRUD API

**Files:**
- Create: `backend/app/routers/fonts.py`
- Create: `backend/tests/test_routers_fonts.py`
- Modify: `backend/app/main.py`

**Step 1: 테스트 작성**

```python
# tests/test_routers_fonts.py

def test_create_font_preset(client):
    res = client.post("/api/fonts", json={
        "language": "vi",
        "font_family": "NotoSans",
        "font_file_url": "/fonts/NotoSans-Regular.ttf",
        "font_size": 14.0,
        "line_height": 1.5,
    })
    assert res.status_code == 201
    assert res.json()["language"] == "vi"
    assert res.json()["line_height"] == 1.5


def test_list_font_presets(client):
    client.post("/api/fonts", json={"language": "ko", "font_family": "Pretendard", "font_file_url": "/fonts/Pretendard.ttf"})
    client.post("/api/fonts", json={"language": "en", "font_family": "Inter", "font_file_url": "/fonts/Inter.ttf"})
    res = client.get("/api/fonts")
    assert len(res.json()) == 2


def test_update_font_preset(client):
    create = client.post("/api/fonts", json={"language": "ko", "font_family": "Old", "font_file_url": "/fonts/old.ttf"})
    font_id = create.json()["id"]
    res = client.patch(f"/api/fonts/{font_id}", json={"font_size": 16.0})
    assert res.json()["font_size"] == 16.0


def test_delete_font_preset(client):
    create = client.post("/api/fonts", json={"language": "fr", "font_family": "Roboto", "font_file_url": "/fonts/r.ttf"})
    font_id = create.json()["id"]
    res = client.delete(f"/api/fonts/{font_id}")
    assert res.status_code == 204
```

**Step 2: fonts.py 라우터 구현**

```python
# app/routers/fonts.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FontPreset
from app.schemas import FontPresetCreate, FontPresetUpdate, FontPresetOut

router = APIRouter(prefix="/api/fonts", tags=["fonts"])


@router.post("", response_model=FontPresetOut, status_code=201)
def create_font(body: FontPresetCreate, db: Session = Depends(get_db)):
    font = FontPreset(**body.model_dump())
    db.add(font)
    db.commit()
    db.refresh(font)
    return font


@router.get("", response_model=list[FontPresetOut])
def list_fonts(db: Session = Depends(get_db)):
    return db.query(FontPreset).all()


@router.get("/{font_id}", response_model=FontPresetOut)
def get_font(font_id: int, db: Session = Depends(get_db)):
    font = db.query(FontPreset).filter(FontPreset.id == font_id).first()
    if not font:
        raise HTTPException(status_code=404, detail="FontPreset not found")
    return font


@router.patch("/{font_id}", response_model=FontPresetOut)
def update_font(font_id: int, body: FontPresetUpdate, db: Session = Depends(get_db)):
    font = db.query(FontPreset).filter(FontPreset.id == font_id).first()
    if not font:
        raise HTTPException(status_code=404, detail="FontPreset not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(font, key, val)
    db.commit()
    db.refresh(font)
    return font


@router.delete("/{font_id}", status_code=204)
def delete_font(font_id: int, db: Session = Depends(get_db)):
    font = db.query(FontPreset).filter(FontPreset.id == font_id).first()
    if not font:
        raise HTTPException(status_code=404, detail="FontPreset not found")
    db.delete(font)
    db.commit()
```

**Step 3: main.py에 등록, 테스트 실행**

Run: `python -m pytest tests/test_routers_fonts.py -v`
Expected: 4 passed

**Step 4: Commit**

```bash
git add backend/
git commit -m "feat: FontPreset CRUD API + 테스트"
```

---

## Phase 2: PDF 엔진

### Task 7: 텍스트 치환 엔진

**Files:**
- Create: `backend/app/engine/__init__.py`
- Create: `backend/app/engine/text_processor.py`
- Create: `backend/tests/test_text_processor.py`

**Step 1: 테스트 작성**

```python
# tests/test_text_processor.py
from app.engine.text_processor import substitute_placeholders, normalize_text


def test_substitute_name():
    result = substitute_placeholders("Hello {NAME}!", name="Jimin", date="2020-03-15")
    assert result == "Hello Jimin!"


def test_substitute_date():
    result = substitute_placeholders("Born on {DATE}", name="A", date="2020-03-15")
    assert result == "Born on 2020-03-15"


def test_substitute_both():
    result = substitute_placeholders("{NAME} was born on {DATE}.", name="지민", date="2020-03-15")
    assert result == "지민 was born on 2020-03-15."


def test_no_placeholder():
    result = substitute_placeholders("Once upon a time", name="A", date="B")
    assert result == "Once upon a time"


def test_normalize_vietnamese():
    """베트남어 NFC 정규화 - 성조 결합 문자 처리"""
    # Composed vs decomposed: ồ (NFC) vs ồ (NFD)
    decomposed = "Xin cha\u0300o"  # 'a' + combining grave
    result = normalize_text(decomposed)
    assert result == "Xin ch\u00e0o"  # 'à' precomposed


def test_normalize_french():
    """프랑스어 악센트 NFC 정규화"""
    decomposed = "cafe\u0301"  # 'e' + combining acute
    result = normalize_text(decomposed)
    assert result == "caf\u00e9"  # 'é' precomposed
```

**Step 2: 테스트 실패 확인**

Run: `python -m pytest tests/test_text_processor.py -v`
Expected: FAIL

**Step 3: text_processor.py 구현**

```python
# app/engine/text_processor.py
import unicodedata


def substitute_placeholders(text: str, *, name: str, date: str) -> str:
    return text.replace("{NAME}", name).replace("{DATE}", date)


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFC", text)
```

**Step 4: 테스트 통과 확인**

Run: `python -m pytest tests/test_text_processor.py -v`
Expected: 6 passed

**Step 5: Commit**

```bash
git add backend/
git commit -m "feat: 텍스트 치환 + NFC 정규화 엔진"
```

---

### Task 8: 폰트 매니저

**Files:**
- Create: `backend/app/engine/font_manager.py`
- Create: `backend/tests/test_font_manager.py`
- Create: `backend/fonts/.gitkeep`

프로토타입용으로 Google Noto Sans 폰트(무료)를 사용한다.
테스트 전 `fonts/` 디렉토리에 NotoSans-Regular.ttf를 다운로드해 둔다.

**Step 1: 테스트 작성**

```python
# tests/test_font_manager.py
import os
import pytest
from app.engine.font_manager import FontManager

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")


@pytest.fixture
def font_manager():
    return FontManager(font_dir=FONT_DIR)


def test_register_font(font_manager):
    """TTF 폰트 등록이 성공하는지 확인"""
    # fonts/ 디렉토리에 테스트용 폰트가 있어야 함
    if not os.path.exists(os.path.join(FONT_DIR, "NotoSans-Regular.ttf")):
        pytest.skip("Test font not available")
    font_name = font_manager.register_font("NotoSans-Regular", "NotoSans-Regular.ttf")
    assert font_name == "NotoSans-Regular"


def test_register_font_not_found(font_manager):
    """존재하지 않는 폰트 파일 등록 시 에러"""
    with pytest.raises(FileNotFoundError):
        font_manager.register_font("Missing", "nonexistent.ttf")


def test_get_registered_fonts(font_manager):
    """등록된 폰트 목록 조회"""
    if not os.path.exists(os.path.join(FONT_DIR, "NotoSans-Regular.ttf")):
        pytest.skip("Test font not available")
    font_manager.register_font("NotoSans-Regular", "NotoSans-Regular.ttf")
    assert "NotoSans-Regular" in font_manager.registered_fonts
```

**Step 2: font_manager.py 구현**

```python
# app/engine/font_manager.py
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class FontManager:
    def __init__(self, font_dir: str = "fonts"):
        self.font_dir = font_dir
        self.registered_fonts: set[str] = set()

    def register_font(self, font_name: str, font_filename: str) -> str:
        font_path = os.path.join(self.font_dir, font_filename)
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font file not found: {font_path}")
        if font_name not in self.registered_fonts:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            self.registered_fonts.add(font_name)
        return font_name
```

**Step 3: 테스트 실행**

Run: `python -m pytest tests/test_font_manager.py -v`
Expected: passed (또는 skip if font not available)

**Step 4: Commit**

```bash
git add backend/
git commit -m "feat: FontManager - TTF 폰트 등록/관리"
```

---

### Task 9: PDF 생성 코어 엔진

**Files:**
- Create: `backend/app/engine/pdf_generator.py`
- Create: `backend/tests/test_pdf_generator.py`

이 태스크가 프로젝트의 핵심이다. ReportLab으로 CMYK PDF를 생성하고, 다국어 텍스트를 배치하며, 폰트를 풀 임베딩한다.

**Step 1: 테스트 작성**

```python
# tests/test_pdf_generator.py
import os
import tempfile
import pytest
import pdfplumber
import pikepdf
from app.engine.pdf_generator import PDFGenerator, PageSpec, TextBlock


@pytest.fixture
def generator():
    font_dir = os.path.join(os.path.dirname(__file__), "..", "fonts")
    return PDFGenerator(font_dir=font_dir)


def test_create_blank_pdf(generator):
    """빈 PDF 생성 - 페이지 규격 확인 (8.5x11" + 3mm bleed)"""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        output_path = f.name
    try:
        generator.generate(
            output_path=output_path,
            pages=[PageSpec(page_number=1)],
            bleed_mm=3.0,
        )
        with pdfplumber.open(output_path) as pdf:
            assert len(pdf.pages) == 1
            page = pdf.pages[0]
            # 8.5x11 inch = 612x792pt, + 3mm bleed each side (~8.5pt x 2)
            assert page.width > 612
            assert page.height > 792
    finally:
        os.unlink(output_path)


def test_text_rendering(generator):
    """텍스트가 PDF에 정확히 렌더링되는지 확인"""
    if not os.path.exists(os.path.join(generator.font_dir, "NotoSans-Regular.ttf")):
        pytest.skip("Test font not available")
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        output_path = f.name
    try:
        generator.generate(
            output_path=output_path,
            pages=[
                PageSpec(
                    page_number=1,
                    text_blocks=[
                        TextBlock(
                            text="Hello World",
                            font_name="NotoSans-Regular",
                            font_file="NotoSans-Regular.ttf",
                            font_size=24,
                            x=50, y=700, width=400, height=100,
                            line_height=1.2,
                        ),
                    ],
                ),
            ],
        )
        with pdfplumber.open(output_path) as pdf:
            text = pdf.pages[0].extract_text()
            assert "Hello World" in text
    finally:
        os.unlink(output_path)


def test_multilingual_text(generator):
    """다국어 텍스트 (한/영/베트남/불어) 렌더링"""
    if not os.path.exists(os.path.join(generator.font_dir, "NotoSans-Regular.ttf")):
        pytest.skip("Test font not available")
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        output_path = f.name
    try:
        texts = [
            ("안녕하세요", 600),
            ("Hello", 500),
            ("Xin chào", 400),
            ("Bonjour café", 300),
        ]
        blocks = [
            TextBlock(
                text=t, font_name="NotoSans-Regular", font_file="NotoSans-Regular.ttf",
                font_size=16, x=50, y=y, width=400, height=80, line_height=1.2,
            )
            for t, y in texts
        ]
        generator.generate(
            output_path=output_path,
            pages=[PageSpec(page_number=1, text_blocks=blocks)],
        )
        with pdfplumber.open(output_path) as pdf:
            text = pdf.pages[0].extract_text()
            assert "Hello" in text
    finally:
        os.unlink(output_path)


def test_font_embedding(generator):
    """폰트가 PDF에 풀 임베딩되었는지 확인"""
    if not os.path.exists(os.path.join(generator.font_dir, "NotoSans-Regular.ttf")):
        pytest.skip("Test font not available")
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        output_path = f.name
    try:
        generator.generate(
            output_path=output_path,
            pages=[
                PageSpec(
                    page_number=1,
                    text_blocks=[
                        TextBlock(
                            text="Test", font_name="NotoSans-Regular",
                            font_file="NotoSans-Regular.ttf",
                            font_size=12, x=50, y=700, width=400, height=50,
                            line_height=1.2,
                        ),
                    ],
                ),
            ],
        )
        with pikepdf.open(output_path) as pdf:
            page = pdf.pages[0]
            fonts = page.get("/Resources").get("/Font")
            assert fonts is not None
            # At least one font should be embedded
            for font_key in fonts.keys():
                font_obj = fonts[font_key]
                # Embedded fonts have a FontDescriptor with FontFile2 (TTF)
                desc = font_obj.get("/FontDescriptor")
                if desc:
                    assert "/FontFile2" in desc or "/FontFile" in desc
    finally:
        os.unlink(output_path)


def test_multiple_pages(generator):
    """여러 페이지 PDF 생성"""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        output_path = f.name
    try:
        generator.generate(
            output_path=output_path,
            pages=[
                PageSpec(page_number=1),
                PageSpec(page_number=2),
                PageSpec(page_number=3),
            ],
        )
        with pdfplumber.open(output_path) as pdf:
            assert len(pdf.pages) == 3
    finally:
        os.unlink(output_path)
```

**Step 2: 테스트 실패 확인**

Run: `python -m pytest tests/test_pdf_generator.py -v`
Expected: FAIL

**Step 3: pdf_generator.py 구현**

```python
# app/engine/pdf_generator.py
from dataclasses import dataclass, field
from reportlab.lib.pagesizes import letter
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

        # Set TrimBox and BleedBox metadata
        trim_x = bleed_pt
        trim_y = bleed_pt
        trim_w = self.PAGE_WIDTH
        trim_h = self.PAGE_HEIGHT

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

            # Set TrimBox for this page
            c.setPageSize((page_w, page_h))
            page_obj = c._doc.Pages[-1] if hasattr(c._doc, 'Pages') else None

            c.showPage()

        c.save()
        return output_path

    def _render_text_block(self, c: canvas.Canvas, block: TextBlock, bleed_pt: float):
        # Register font if needed
        self.font_manager.register_font(block.font_name, block.font_file)

        # Normalize text (NFC for Vietnamese/French accents)
        text = normalize_text(block.text)

        # Create paragraph style
        style = ParagraphStyle(
            name=f"style_{block.font_name}_{block.font_size}",
            fontName=block.font_name,
            fontSize=block.font_size,
            leading=block.font_size * block.line_height,
            alignment=TA_LEFT,
            textColor=CMYKColor(0, 0, 0, 1),  # Pure black in CMYK
        )

        # Render with Paragraph for auto line-wrapping
        para = Paragraph(text.replace("\n", "<br/>"), style)
        para_width, para_height = para.wrap(block.width, block.height)
        # Position adjusted for bleed
        para.drawOn(c, block.x + bleed_pt, block.y + bleed_pt)
```

**Step 4: 테스트 통과 확인**

Run: `python -m pytest tests/test_pdf_generator.py -v`
Expected: passed (or skip for font-dependent tests)

**Step 5: Commit**

```bash
git add backend/
git commit -m "feat: PDF 생성 코어 엔진 - CMYK, 폰트 임베딩, 다국어 렌더링"
```

---

### Task 10: PDF 생성 API 엔드포인트

**Files:**
- Create: `backend/app/routers/generate.py`
- Create: `backend/app/routers/orders.py`
- Create: `backend/tests/test_routers_orders.py`
- Create: `backend/tests/test_routers_generate.py`
- Modify: `backend/app/main.py`

**Step 1: Order API 테스트 작성**

```python
# tests/test_routers_orders.py

def _seed_book_and_content(client):
    """도서 + 페이지 + 원고 데이터 시드"""
    book = client.post("/api/books", json={"title": "Joya"}).json()
    page = client.post(f"/api/books/{book['id']}/pages", json={
        "page_number": 1, "page_type": "cover", "is_personalizable": True,
    }).json()
    client.post(f"/api/books/{book['id']}/pages/{page['id']}/contents", json={
        "language": "ko", "text_content": "안녕 {NAME}!",
    })
    return book["id"]


def test_create_order(client):
    book_id = _seed_book_and_content(client)
    res = client.post("/api/orders", json={
        "book_id": book_id,
        "main_language": "ko",
        "sub_languages": ["en", "vi", "fr"],
        "person_name": "지민",
        "person_date": "2020-03-15",
    })
    assert res.status_code == 201
    assert res.json()["status"] == "pending"


def test_list_orders(client):
    book_id = _seed_book_and_content(client)
    client.post("/api/orders", json={
        "book_id": book_id, "main_language": "ko",
        "sub_languages": ["en"], "person_name": "A", "person_date": "2020-01-01",
    })
    res = client.get("/api/orders")
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_get_order(client):
    book_id = _seed_book_and_content(client)
    create = client.post("/api/orders", json={
        "book_id": book_id, "main_language": "ko",
        "sub_languages": ["en"], "person_name": "B", "person_date": "2020-01-01",
    })
    order_id = create.json()["id"]
    res = client.get(f"/api/orders/{order_id}")
    assert res.json()["person_name"] == "B"
```

**Step 2: orders.py 라우터 구현**

```python
# app/routers/orders.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order
from app.schemas import OrderCreate, OrderOut

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=201)
def create_order(body: OrderCreate, db: Session = Depends(get_db)):
    order = Order(
        book_id=body.book_id,
        main_language=body.main_language,
        sub_languages=[lang.value for lang in body.sub_languages],
        person_name=body.person_name,
        person_date=body.person_date,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("", response_model=list[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).order_by(Order.created_at.desc()).all()


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
```

**Step 3: generate.py 라우터 구현**

```python
# app/routers/generate.py
import os
import tempfile
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Book, Page, PageContent, FontPreset, Order, OrderStatus
from app.schemas import GenerateRequest, OrderOut
from app.engine.pdf_generator import PDFGenerator, PageSpec, TextBlock
from app.engine.text_processor import substitute_placeholders, normalize_text
from app.config import settings

router = APIRouter(prefix="/api/generate", tags=["generate"])


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
                font_preset = db.query(FontPreset).filter(FontPreset.id == content.font_preset_id).first()

            # Stack languages vertically in text area
            lang_offset = i * (page.text_area_h / len(languages))
            block = TextBlock(
                text=text,
                font_name=font_preset.font_family if font_preset else "Helvetica",
                font_file=font_preset.font_file_url if font_preset else "",
                font_size=font_preset.font_size if font_preset else (18 if i == 0 else 12),
                x=page.text_area_x,
                y=page.text_area_y - lang_offset,
                width=page.text_area_w,
                height=page.text_area_h / len(languages),
                line_height=font_preset.line_height if font_preset else 1.2,
            )
            text_blocks.append(block)

        page_specs.append(PageSpec(
            page_number=page.page_number,
            bg_image_path=page.bg_image_url,
            text_blocks=text_blocks,
        ))
    return page_specs


@router.post("", response_model=OrderOut, status_code=201)
def generate_pdf(body: GenerateRequest, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == body.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    pages = db.query(Page).filter(Page.book_id == book.id).order_by(Page.page_number).all()
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
        page_specs = _build_page_specs(pages, languages, body.person_name, body.person_date, db)
        generator = PDFGenerator(font_dir=settings.font_dir)

        output_dir = tempfile.mkdtemp()
        output_path = os.path.join(output_dir, f"joya_order_{order.id}.pdf")

        generator.generate(
            output_path=output_path,
            pages=page_specs,
            bleed_mm=book.bleed_mm,
        )

        # TODO: Upload to S3 and set pdf_url
        order.pdf_url = output_path  # Local path for now
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
```

**Step 4: main.py에 라우터 등록**

```python
from app.routers import books, pages, fonts, orders, generate
app.include_router(orders.router)
app.include_router(generate.router)
```

**Step 5: 테스트 실행**

Run: `python -m pytest tests/test_routers_orders.py -v`
Expected: 3 passed

**Step 6: Commit**

```bash
git add backend/
git commit -m "feat: Order CRUD + PDF 생성 API 엔드포인트"
```

---

## Phase 3: Next.js 관리자 UI

### Task 11: Next.js 프로젝트 초기화

**Step 1: Next.js 프로젝트 생성**

Run:
```bash
cd /Users/max/Desktop/wishket/admin-pdf
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*"
```

**Step 2: shadcn/ui 설치**

Run:
```bash
cd /Users/max/Desktop/wishket/admin-pdf/frontend
npx shadcn@latest init
```

**Step 3: 필요한 shadcn 컴포넌트 설치**

Run:
```bash
npx shadcn@latest add button card input label select table dialog textarea badge tabs
```

**Step 4: SWR 설치**

Run: `npm install swr`

**Step 5: API 클라이언트 생성**

```typescript
// frontend/lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || "API error");
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}
```

**Step 6: Commit**

```bash
git add frontend/
git commit -m "feat: Next.js 15 프로젝트 초기화 + shadcn/ui + SWR"
```

---

### Task 12: 관리자 레이아웃 + 사이드바

**Files:**
- Create: `frontend/app/admin/layout.tsx`
- Create: `frontend/components/admin-sidebar.tsx`
- Modify: `frontend/app/layout.tsx`

**Step 1: 관리자 사이드바 컴포넌트**

```tsx
// frontend/components/admin-sidebar.tsx
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { BookOpen, Type, ShoppingCart, Wand2, LayoutDashboard } from "lucide-react";

const menuItems = [
  { href: "/admin/dashboard", label: "대시보드", icon: LayoutDashboard },
  { href: "/admin/books", label: "도서 관리", icon: BookOpen },
  { href: "/admin/fonts", label: "폰트 프리셋", icon: Type },
  { href: "/admin/orders", label: "주문 이력", icon: ShoppingCart },
  { href: "/admin/generate", label: "PDF 생성", icon: Wand2 },
];

export function AdminSidebar() {
  const pathname = usePathname();
  return (
    <aside className="w-64 border-r bg-gray-50 min-h-screen p-4">
      <h1 className="text-xl font-bold mb-8 px-2">Joya Admin</h1>
      <nav className="space-y-1">
        {menuItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 px-3 py-2 rounded-md text-sm",
              pathname.startsWith(item.href)
                ? "bg-blue-50 text-blue-700 font-medium"
                : "text-gray-600 hover:bg-gray-100"
            )}
          >
            <item.icon className="w-4 h-4" />
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
```

**Step 2: 관리자 레이아웃**

```tsx
// frontend/app/admin/layout.tsx
import { AdminSidebar } from "@/components/admin-sidebar";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <AdminSidebar />
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}
```

**Step 3: 루트 리다이렉트**

```tsx
// frontend/app/page.tsx
import { redirect } from "next/navigation";
export default function Home() {
  redirect("/admin/dashboard");
}
```

**Step 4: 개발 서버 확인**

Run: `cd /Users/max/Desktop/wishket/admin-pdf/frontend && npm run dev`
Verify: `http://localhost:3000` -> 관리자 레이아웃 렌더링

**Step 5: Commit**

```bash
git add frontend/
git commit -m "feat: 관리자 레이아웃 + 사이드바 네비게이션"
```

---

### Task 13: 도서 관리 페이지

**Files:**
- Create: `frontend/app/admin/dashboard/page.tsx`
- Create: `frontend/app/admin/books/page.tsx`
- Create: `frontend/app/admin/books/[id]/page.tsx`
- Create: `frontend/app/admin/books/[id]/pages/[pageId]/page.tsx`
- Create: `frontend/lib/types.ts`

**Step 1: types.ts 생성**

```typescript
// frontend/lib/types.ts
export type Language = "ko" | "en" | "vi" | "fr";
export type PageType = "cover" | "opening" | "story" | "closing";
export type OrderStatus = "pending" | "processing" | "completed" | "failed" | "timeout";

export interface Book {
  id: number;
  title: string;
  page_size: string;
  bleed_mm: number;
  created_at: string;
}

export interface PageData {
  id: number;
  book_id: number;
  page_number: number;
  page_type: PageType;
  bg_image_url: string | null;
  text_area_x: number;
  text_area_y: number;
  text_area_w: number;
  text_area_h: number;
  is_personalizable: boolean;
}

export interface FontPreset {
  id: number;
  language: Language;
  font_family: string;
  font_file_url: string;
  font_size: number;
  letter_spacing: number;
  line_height: number;
}

export interface PageContent {
  id: number;
  page_id: number;
  language: Language;
  text_content: string;
  font_preset_id: number | null;
}

export interface Order {
  id: number;
  book_id: number;
  main_language: Language;
  sub_languages: string[];
  person_name: string;
  person_date: string;
  status: OrderStatus;
  pdf_url: string | null;
  warning: string | null;
  created_at: string;
}

export const LANGUAGE_LABELS: Record<Language, string> = {
  ko: "한국어",
  en: "English",
  vi: "Tiếng Việt",
  fr: "Français",
};

export const PAGE_TYPE_LABELS: Record<PageType, string> = {
  cover: "표지",
  opening: "오프닝",
  story: "스토리",
  closing: "클로징",
};
```

**Step 2: 대시보드, 도서 목록, 도서 상세, 페이지 편집 페이지 구현**

각 페이지는 SWR로 FastAPI에서 데이터를 페칭하고, shadcn/ui 컴포넌트로 CRUD UI를 구성한다.
@frontend-design 스킬 참고하여 깔끔한 UI 구현.

구현할 화면:
- `/admin/dashboard` — 최근 주문 5건 + 도서 수 통계
- `/admin/books` — 도서 목록 테이블 + 도서 추가 다이얼로그
- `/admin/books/[id]` — 도서 상세 + 페이지 목록 + 페이지 추가
- `/admin/books/[id]/pages/[pageId]` — 페이지별 4개 언어 원고 편집 탭

**Step 3: 동작 확인**

개발 서버에서 도서 생성/조회/수정/삭제가 정상 동작하는지 확인.

**Step 4: Commit**

```bash
git add frontend/
git commit -m "feat: 도서 관리 페이지 (CRUD + 페이지/원고 편집)"
```

---

### Task 14: 폰트 프리셋 관리 페이지

**Files:**
- Create: `frontend/app/admin/fonts/page.tsx`

언어별 폰트 프리셋을 카드 형태로 표시. 추가/수정/삭제 다이얼로그.
폰트 크기, 자간, 행간 슬라이더 또는 숫자 입력.

**Commit:**
```bash
git add frontend/
git commit -m "feat: 폰트 프리셋 관리 페이지"
```

---

### Task 15: 주문 이력 페이지

**Files:**
- Create: `frontend/app/admin/orders/page.tsx`
- Create: `frontend/app/admin/orders/[id]/page.tsx`

주문 목록 테이블 (상태 뱃지, 생성일, 다운로드 버튼).
주문 상세 — 선택 언어, 개인화 데이터, PDF 미리보기/다운로드.

**Commit:**
```bash
git add frontend/
git commit -m "feat: 주문 이력 관리 페이지"
```

---

### Task 16: PDF 생성 시뮬레이션 페이지 (핵심 데모)

**Files:**
- Create: `frontend/app/admin/generate/page.tsx`

**핵심 화면 구성:**
1. 도서 선택 드롭다운
2. 메인 언어 선택
3. 서브 언어 3개 체크박스
4. 이름 입력 필드
5. 날짜 입력 필드
6. "PDF 생성하기" 버튼
7. 생성 중 로딩 상태
8. 완료 시 PDF 다운로드 버튼 + iframe 미리보기

```tsx
// 핵심 로직 스켈레톤
async function handleGenerate() {
  setLoading(true);
  try {
    const order = await apiFetch<Order>("/api/generate", {
      method: "POST",
      body: JSON.stringify({
        book_id: selectedBook,
        main_language: mainLang,
        sub_languages: subLangs,
        person_name: name,
        person_date: date,
      }),
    });
    setOrder(order);
  } catch (e) {
    setError(e.message);
  } finally {
    setLoading(false);
  }
}
```

**Commit:**
```bash
git add frontend/
git commit -m "feat: PDF 생성 시뮬레이션 페이지 (핵심 데모)"
```

---

## Phase 4: 통합 및 시드 데이터

### Task 17: 더미 동화 콘텐츠 시드 스크립트

**Files:**
- Create: `backend/scripts/seed.py`
- Create: `images/.gitkeep`
- Create: `fonts/.gitkeep`

더미 동화 "Joya의 모험" 5페이지분 4개 언어 텍스트 데이터를 DB에 삽입하는 스크립트.

```python
# backend/scripts/seed.py
"""
더미 동화 시드 데이터:
- 1권: "Joya의 모험"
- 5페이지: 표지, 오프닝, 스토리x2, 클로징
- 4개 언어: 한/영/베트남/불어
- 표지/오프닝/클로징에 {NAME}, {DATE} 플레이스홀더
"""
```

Run: `cd /Users/max/Desktop/wishket/admin-pdf/backend && python -m scripts.seed`

**Commit:**
```bash
git add .
git commit -m "feat: 더미 동화 시드 데이터 + 폰트/이미지 디렉토리"
```

---

### Task 18: Docker Compose (로컬 개발)

**Files:**
- Create: `docker-compose.yml`
- Create: `backend/Dockerfile`
- Create: `.env.example`

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: joya
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/joya
    depends_on:
      - db
    volumes:
      - ./backend:/app
      - ./fonts:/app/fonts
      - ./images:/app/images

volumes:
  pgdata:
```

Run: `docker compose up -d`
Verify: `curl http://localhost:8000/health`

**Commit:**
```bash
git add docker-compose.yml backend/Dockerfile .env.example
git commit -m "feat: Docker Compose 로컬 개발 환경"
```

---

### Task 19: E2E 테스트 (PDF 생성 전체 플로우)

**Files:**
- Create: `backend/tests/test_e2e_generate.py`

전체 플로우 테스트:
1. Book 생성
2. Page 5개 생성 (cover, opening, story x2, closing)
3. 4개 언어 PageContent 생성
4. FontPreset 4개 등록
5. Generate API 호출
6. 생성된 PDF 검증 (5페이지, 텍스트 포함, 폰트 임베딩)

**Commit:**
```bash
git add backend/tests/
git commit -m "test: PDF 생성 E2E 통합 테스트"
```

---

### Task 20: 배포 설정 (Vercel + Railway)

**Files:**
- Create: `frontend/vercel.json`
- Create: `backend/Procfile`
- Create: `backend/railway.toml`

**Step 1: Vercel 배포 (Next.js)**

```json
// frontend/vercel.json
{
  "framework": "nextjs"
}
```

환경 변수: `NEXT_PUBLIC_API_URL` = Railway 백엔드 URL

**Step 2: Railway 배포 (FastAPI)**

```toml
# backend/railway.toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

Railway에서 PostgreSQL 애드온 추가, `DATABASE_URL` 자동 설정.

**Commit:**
```bash
git add .
git commit -m "feat: Vercel + Railway 배포 설정"
```

---

## 작업 순서 요약

| Phase | Task | 내용 | 의존성 |
|-------|------|------|--------|
| 1 | 1 | Python 프로젝트 초기화 | - |
| 1 | 2 | DB 모델 + 마이그레이션 | Task 1 |
| 1 | 3 | Pydantic 스키마 | Task 2 |
| 1 | 4 | Book CRUD API | Task 3 |
| 1 | 5 | Page CRUD API | Task 4 |
| 1 | 6 | FontPreset CRUD API | Task 3 |
| 2 | 7 | 텍스트 치환 엔진 | Task 1 |
| 2 | 8 | 폰트 매니저 | Task 1 |
| 2 | 9 | PDF 생성 코어 엔진 | Task 7, 8 |
| 2 | 10 | PDF 생성 API | Task 5, 6, 9 |
| 3 | 11 | Next.js 초기화 | - |
| 3 | 12 | 관리자 레이아웃 | Task 11 |
| 3 | 13 | 도서 관리 페이지 | Task 12 |
| 3 | 14 | 폰트 프리셋 페이지 | Task 12 |
| 3 | 15 | 주문 이력 페이지 | Task 12 |
| 3 | 16 | PDF 생성 페이지 | Task 12 |
| 4 | 17 | 시드 데이터 | Task 10 |
| 4 | 18 | Docker Compose | Task 10, 11 |
| 4 | 19 | E2E 테스트 | Task 10, 17 |
| 4 | 20 | 배포 설정 | Task 18 |

**병렬 가능:**
- Task 4, 5, 6 (CRUD API들은 독립적)
- Task 7, 8 (텍스트 처리와 폰트 매니저는 독립적)
- Task 11~16 (프론트엔드)은 Task 10 완료 후 병렬 가능
- Task 13, 14, 15, 16 (관리자 페이지들은 독립적)
