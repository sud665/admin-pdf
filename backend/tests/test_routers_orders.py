def _seed_book_and_content(client):
    """도서 + 페이지 + 원고 데이터 시드"""
    book = client.post("/api/books", json={"title": "Joya"}).json()
    page = client.post(
        f"/api/books/{book['id']}/pages",
        json={"page_number": 1, "page_type": "cover", "is_personalizable": True},
    ).json()
    client.post(
        f"/api/books/{book['id']}/pages/{page['id']}/contents",
        json={"language": "ko", "text_content": "안녕 {NAME}!"},
    )
    return book["id"]


def test_create_order(client):
    book_id = _seed_book_and_content(client)
    res = client.post(
        "/api/orders",
        json={
            "book_id": book_id,
            "main_language": "ko",
            "sub_languages": ["en", "vi", "fr"],
            "person_name": "지민",
            "person_date": "2020-03-15",
        },
    )
    assert res.status_code == 201
    assert res.json()["status"] == "pending"


def test_list_orders(client):
    book_id = _seed_book_and_content(client)
    client.post(
        "/api/orders",
        json={
            "book_id": book_id,
            "main_language": "ko",
            "sub_languages": ["en"],
            "person_name": "A",
            "person_date": "2020-01-01",
        },
    )
    res = client.get("/api/orders")
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_get_order(client):
    book_id = _seed_book_and_content(client)
    create = client.post(
        "/api/orders",
        json={
            "book_id": book_id,
            "main_language": "ko",
            "sub_languages": ["en"],
            "person_name": "B",
            "person_date": "2020-01-01",
        },
    )
    order_id = create.json()["id"]
    res = client.get(f"/api/orders/{order_id}")
    assert res.json()["person_name"] == "B"
