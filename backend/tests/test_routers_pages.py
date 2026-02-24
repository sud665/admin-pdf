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


def test_create_page_content(client):
    book_id = _create_book(client)
    page = client.post(f"/api/books/{book_id}/pages", json={"page_number": 1, "page_type": "cover"}).json()
    res = client.post(f"/api/books/{book_id}/pages/{page['id']}/contents", json={
        "language": "ko",
        "text_content": "안녕 {NAME}!",
    })
    assert res.status_code == 201
    assert res.json()["language"] == "ko"
    assert "{NAME}" in res.json()["text_content"]


def test_list_page_contents(client):
    book_id = _create_book(client)
    page = client.post(f"/api/books/{book_id}/pages", json={"page_number": 1, "page_type": "cover"}).json()
    client.post(f"/api/books/{book_id}/pages/{page['id']}/contents", json={"language": "ko", "text_content": "한국어"})
    client.post(f"/api/books/{book_id}/pages/{page['id']}/contents", json={"language": "en", "text_content": "English"})
    res = client.get(f"/api/books/{book_id}/pages/{page['id']}/contents")
    assert len(res.json()) == 2


def test_update_page_content(client):
    book_id = _create_book(client)
    page = client.post(f"/api/books/{book_id}/pages", json={"page_number": 1, "page_type": "cover"}).json()
    content = client.post(f"/api/books/{book_id}/pages/{page['id']}/contents", json={
        "language": "ko", "text_content": "Old",
    }).json()
    res = client.patch(
        f"/api/books/{book_id}/pages/{page['id']}/contents/{content['id']}",
        json={"text_content": "New"},
    )
    assert res.json()["text_content"] == "New"
