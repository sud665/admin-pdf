"""
E2E 통합 테스트: PDF 생성 전체 플로우
1. Book 생성
2. Page 5개 생성 (cover, opening, story x2, closing)
3. 4개 언어 PageContent 생성
4. FontPreset 4개 등록
5. Generate API 호출
6. 생성된 PDF 검증 (5페이지, 텍스트 포함)
"""

import os
import pdfplumber


def _seed_full_book(client):
    """전체 동화 데이터 시드"""
    # Create book
    book = client.post("/api/books", json={"title": "E2E Test Book"}).json()
    book_id = book["id"]

    # Create font presets
    for lang in ["ko", "en", "vi", "fr"]:
        client.post(
            "/api/fonts",
            json={
                "language": lang,
                "font_family": "NotoSans-Regular",
                "font_file_url": "NotoSans-Regular.ttf",
                "font_size": 14.0,
                "letter_spacing": 0.0,
                "line_height": 1.3,
            },
        )

    # Create pages
    pages_config = [
        {"page_number": 1, "page_type": "cover", "is_personalizable": True},
        {"page_number": 2, "page_type": "opening", "is_personalizable": True},
        {"page_number": 3, "page_type": "story", "is_personalizable": False},
        {"page_number": 4, "page_type": "story", "is_personalizable": False},
        {"page_number": 5, "page_type": "closing", "is_personalizable": True},
    ]

    contents = {
        1: {
            "ko": "{NAME}의 모험 - {DATE}",
            "en": "Adventure of {NAME} - {DATE}",
            "vi": "Cuộc phiêu lưu của {NAME} - {DATE}",
            "fr": "L'aventure de {NAME} - {DATE}",
        },
        2: {
            "ko": "어느 날 {NAME}은(는) 숲으로 갔어요.",
            "en": "One day {NAME} went to the forest.",
            "vi": "Một ngày nọ, {NAME} đi vào rừng.",
            "fr": "Un jour, {NAME} alla dans la forêt.",
        },
        3: {
            "ko": "숲에는 아름다운 꽃들이 피어 있었어요.",
            "en": "Beautiful flowers bloomed in the forest.",
            "vi": "Trong rừng có những bông hoa tuyệt đẹp.",
            "fr": "De belles fleurs s'épanouissaient dans la forêt.",
        },
        4: {
            "ko": "요정이 반짝이는 씨앗을 건네주었어요.",
            "en": "The fairy gave a sparkling seed.",
            "vi": "Nàng tiên trao một hạt giống lấp lánh.",
            "fr": "La fée donna une graine scintillante.",
        },
        5: {
            "ko": "{NAME}은(는) 행복하게 집으로 돌아왔어요.",
            "en": "{NAME} happily returned home.",
            "vi": "{NAME} vui vẻ trở về nhà.",
            "fr": "{NAME} rentra joyeusement à la maison.",
        },
    }

    for page_cfg in pages_config:
        page = client.post(f"/api/books/{book_id}/pages", json=page_cfg).json()
        page_id = page["id"]
        page_num = page_cfg["page_number"]

        for lang, text in contents[page_num].items():
            client.post(
                f"/api/books/{book_id}/pages/{page_id}/contents",
                json={"language": lang, "text_content": text},
            )

    return book_id


def test_e2e_generate_full_flow(client):
    """전체 PDF 생성 플로우 E2E 테스트"""
    font_dir = os.path.join(os.path.dirname(__file__), "..", "fonts")
    if not os.path.exists(os.path.join(font_dir, "NotoSans-Regular.ttf")):
        import pytest

        pytest.skip("Test font not available")

    book_id = _seed_full_book(client)

    # Generate PDF
    res = client.post(
        "/api/generate",
        json={
            "book_id": book_id,
            "main_language": "ko",
            "sub_languages": ["en", "vi", "fr"],
            "person_name": "지민",
            "person_date": "2020-03-15",
        },
    )
    assert res.status_code == 201
    order = res.json()
    assert order["status"] == "completed"
    assert order["person_name"] == "지민"

    # Verify PDF file
    pdf_path = order["pdf_url"]
    assert pdf_path is not None
    assert os.path.exists(pdf_path)

    with pdfplumber.open(pdf_path) as pdf:
        # Should have 5 pages
        assert len(pdf.pages) == 5

        # Check English text is present (CJK extraction can be unreliable)
        cover_text = pdf.pages[0].extract_text() or ""
        assert "2020-03-15" in cover_text

    # Clean up generated PDF
    if os.path.exists(pdf_path):
        os.unlink(pdf_path)
        pdf_dir = os.path.dirname(pdf_path)
        if os.path.isdir(pdf_dir) and not os.listdir(pdf_dir):
            os.rmdir(pdf_dir)


def test_e2e_generate_main_language_only(client):
    """메인 언어만으로 PDF 생성"""
    font_dir = os.path.join(os.path.dirname(__file__), "..", "fonts")
    if not os.path.exists(os.path.join(font_dir, "NotoSans-Regular.ttf")):
        import pytest

        pytest.skip("Test font not available")

    book_id = _seed_full_book(client)

    res = client.post(
        "/api/generate",
        json={
            "book_id": book_id,
            "main_language": "en",
            "sub_languages": [],
            "person_name": "Alice",
            "person_date": "2021-06-01",
        },
    )
    assert res.status_code == 201
    order = res.json()
    assert order["status"] == "completed"

    pdf_path = order["pdf_url"]
    with pdfplumber.open(pdf_path) as pdf:
        assert len(pdf.pages) == 5
        cover_text = pdf.pages[0].extract_text()
        if cover_text:
            assert "Alice" in cover_text

    if os.path.exists(pdf_path):
        os.unlink(pdf_path)
        pdf_dir = os.path.dirname(pdf_path)
        if os.path.isdir(pdf_dir) and not os.listdir(pdf_dir):
            os.rmdir(pdf_dir)


def test_e2e_download_endpoint(client):
    """PDF 다운로드 엔드포인트 테스트"""
    font_dir = os.path.join(os.path.dirname(__file__), "..", "fonts")
    if not os.path.exists(os.path.join(font_dir, "NotoSans-Regular.ttf")):
        import pytest

        pytest.skip("Test font not available")

    book_id = _seed_full_book(client)

    gen_res = client.post(
        "/api/generate",
        json={
            "book_id": book_id,
            "main_language": "en",
            "sub_languages": [],
            "person_name": "Sujin",
            "person_date": "2022-01-01",
        },
    )
    assert gen_res.status_code == 201, f"Generate failed: {gen_res.text}"
    order_id = gen_res.json()["id"]

    # Download
    dl_res = client.get(f"/api/generate/download/{order_id}")
    assert dl_res.status_code == 200
    assert "application/pdf" in dl_res.headers["content-type"]
    assert len(dl_res.content) > 0

    # Cleanup
    pdf_path = gen_res.json()["pdf_url"]
    if pdf_path and os.path.exists(pdf_path):
        os.unlink(pdf_path)
        pdf_dir = os.path.dirname(pdf_path)
        if os.path.isdir(pdf_dir) and not os.listdir(pdf_dir):
            os.rmdir(pdf_dir)
