import os


def _seed_full_book(client):
    """도서 + 페이지 3개 + 원고 데이터 시드 (cover, story, closing)"""
    book = client.post("/api/books", json={"title": "Joya 모험"}).json()
    book_id = book["id"]

    # Cover page (personalizable)
    cover = client.post(
        f"/api/books/{book_id}/pages",
        json={
            "page_number": 1,
            "page_type": "cover",
            "is_personalizable": True,
            "text_area_x": 50,
            "text_area_y": 600,
            "text_area_w": 400,
            "text_area_h": 200,
        },
    ).json()
    client.post(
        f"/api/books/{book_id}/pages/{cover['id']}/contents",
        json={"language": "ko", "text_content": "{NAME}의 모험"},
    )
    client.post(
        f"/api/books/{book_id}/pages/{cover['id']}/contents",
        json={"language": "en", "text_content": "{NAME}'s Adventure"},
    )

    # Story page
    story = client.post(
        f"/api/books/{book_id}/pages",
        json={
            "page_number": 2,
            "page_type": "story",
            "text_area_x": 50,
            "text_area_y": 600,
            "text_area_w": 400,
            "text_area_h": 200,
        },
    ).json()
    client.post(
        f"/api/books/{book_id}/pages/{story['id']}/contents",
        json={"language": "ko", "text_content": "옛날 옛적에 숲 속에 작은 집이 있었어요."},
    )
    client.post(
        f"/api/books/{book_id}/pages/{story['id']}/contents",
        json={"language": "en", "text_content": "Once upon a time, there was a small house in the forest."},
    )

    # Closing page (personalizable)
    closing = client.post(
        f"/api/books/{book_id}/pages",
        json={
            "page_number": 3,
            "page_type": "closing",
            "is_personalizable": True,
            "text_area_x": 50,
            "text_area_y": 600,
            "text_area_w": 400,
            "text_area_h": 200,
        },
    ).json()
    client.post(
        f"/api/books/{book_id}/pages/{closing['id']}/contents",
        json={"language": "ko", "text_content": "{NAME}, {DATE}에 만든 특별한 책"},
    )
    client.post(
        f"/api/books/{book_id}/pages/{closing['id']}/contents",
        json={"language": "en", "text_content": "A special book made for {NAME} on {DATE}"},
    )

    return book_id


def test_generate_pdf(client):
    """PDF 생성 전체 플로우 테스트"""
    book_id = _seed_full_book(client)
    res = client.post(
        "/api/generate",
        json={
            "book_id": book_id,
            "main_language": "ko",
            "sub_languages": ["en"],
            "person_name": "지민",
            "person_date": "2020-03-15",
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "completed"
    assert data["pdf_url"] is not None
    # Verify PDF file was created
    assert os.path.exists(data["pdf_url"])


def test_generate_pdf_no_pages(client):
    """페이지 없는 도서로 생성 시도하면 422 에러"""
    book = client.post("/api/books", json={"title": "Empty Book"}).json()
    res = client.post(
        "/api/generate",
        json={
            "book_id": book["id"],
            "main_language": "ko",
            "sub_languages": ["en"],
            "person_name": "A",
            "person_date": "2020-01-01",
        },
    )
    assert res.status_code == 422


def test_generate_pdf_book_not_found(client):
    """존재하지 않는 도서로 생성 시도하면 404 에러"""
    res = client.post(
        "/api/generate",
        json={
            "book_id": 9999,
            "main_language": "ko",
            "sub_languages": ["en"],
            "person_name": "A",
            "person_date": "2020-01-01",
        },
    )
    assert res.status_code == 404
