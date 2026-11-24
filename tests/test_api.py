from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_health_reports_chunk_count(tiny_store):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "chunks": 3}


def test_search_keyword_returns_sources(tiny_store):
    response = client.post("/search", json={"question": "StaticFiles", "strategy": "keyword", "k": 2})
    assert response.status_code == 200
    body = response.json()
    assert body["strategy"] == "keyword"
    assert body["results"][0]["source"] == "reference/staticfiles.md > StaticFiles"


def test_search_defaults_to_hybrid(tiny_store):
    body = client.post("/search", json={"question": "StaticFiles static"}).json()
    assert body["strategy"] == "hybrid"
    assert body["results"][0]["doc_path"] == "tutorial/static-files.md"


def test_search_validates_strategy_and_question():
    assert client.post("/search", json={"question": "x", "strategy": "magic"}).status_code == 422
    assert client.post("/search", json={"question": ""}).status_code == 422


def test_index_page_is_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "<html" in response.text.lower()
