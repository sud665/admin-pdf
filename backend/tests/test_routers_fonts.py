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
