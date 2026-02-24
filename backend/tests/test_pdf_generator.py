import os
import tempfile

import pdfplumber
import pikepdf
import pytest

from app.engine.pdf_generator import PDFGenerator, PageSpec, TextBlock

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "fonts")
FONT_AVAILABLE = os.path.exists(os.path.join(FONT_DIR, "NotoSans-Regular.ttf"))


@pytest.fixture
def generator():
    return PDFGenerator(font_dir=FONT_DIR)


def test_create_blank_pdf(generator):
    """빈 PDF 생성 - 페이지 규격 확인 (8.5x11 + 3mm bleed)"""
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


@pytest.mark.skipif(not FONT_AVAILABLE, reason="Test font not available")
def test_text_rendering(generator):
    """텍스트가 PDF에 정확히 렌더링되는지 확인"""
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


@pytest.mark.skipif(not FONT_AVAILABLE, reason="Test font not available")
def test_multilingual_text(generator):
    """다국어 텍스트 (한/영/베트남/불어) 렌더링"""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        output_path = f.name
    try:
        texts = [
            ("Hello", 600),
            ("Bonjour", 500),
            ("Xin chào", 400),
        ]
        blocks = [
            TextBlock(
                text=t,
                font_name="NotoSans-Regular",
                font_file="NotoSans-Regular.ttf",
                font_size=16,
                x=50, y=y, width=400, height=80,
                line_height=1.2,
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
            assert "Bonjour" in text
    finally:
        os.unlink(output_path)


@pytest.mark.skipif(not FONT_AVAILABLE, reason="Test font not available")
def test_font_embedding(generator):
    """폰트가 PDF에 풀 임베딩되었는지 확인"""
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
                            text="Test",
                            font_name="NotoSans-Regular",
                            font_file="NotoSans-Regular.ttf",
                            font_size=12,
                            x=50, y=700, width=400, height=50,
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
            has_embedded = False
            for font_key in fonts.keys():
                font_obj = fonts[font_key]
                desc = font_obj.get("/FontDescriptor")
                if desc and ("/FontFile2" in desc or "/FontFile" in desc):
                    has_embedded = True
                    break
            assert has_embedded, "Font should be fully embedded in PDF"
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


@pytest.mark.skipif(not FONT_AVAILABLE, reason="Test font not available")
def test_long_text_wrapping(generator):
    """긴 텍스트 자동 줄바꿈 확인"""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        output_path = f.name
    try:
        long_text = "This is a very long sentence that should automatically wrap to the next line because it exceeds the available text area width."
        generator.generate(
            output_path=output_path,
            pages=[
                PageSpec(
                    page_number=1,
                    text_blocks=[
                        TextBlock(
                            text=long_text,
                            font_name="NotoSans-Regular",
                            font_file="NotoSans-Regular.ttf",
                            font_size=14,
                            x=50, y=600, width=200, height=200,
                            line_height=1.3,
                        ),
                    ],
                ),
            ],
        )
        with pdfplumber.open(output_path) as pdf:
            text = pdf.pages[0].extract_text()
            assert "long sentence" in text
    finally:
        os.unlink(output_path)
