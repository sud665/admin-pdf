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
