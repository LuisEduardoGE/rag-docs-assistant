"""HTTP interface.

Three endpoints:

  GET  /health   -- is the index loaded, and how big is it
  POST /search   -- retrieval only. No API key needed, no model call, no cost.
  POST /ask      -- retrieval + generation. Needs ANTHROPIC_API_KEY.

/search exists because retrieval is where RAG systems actually fail, and being
able to inspect it in isolation -- without spending a token -- is the single
most useful debugging affordance in this project.

Run:  uvicorn app.api:app --reload
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.config import TOP_K
from app.retrieve import get_store, retrieve

app = FastAPI(
    title="RAG Docs Assistant",
    description="Ask questions about the FastAPI documentation, answered from source.",
    version="1.0.0",
)

STATIC_DIR = Path(__file__).parent / "static"


class SearchRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    k: int = Field(TOP_K, ge=1, le=20)
    strategy: str = Field("hybrid", pattern="^(hybrid|vector|keyword)$")


class SourceOut(BaseModel):
    source: str
    doc_path: str
    heading_path: str
    score: float
    text: str


class SearchResponse(BaseModel):
    question: str
    strategy: str
    results: list[SourceOut]


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceOut]
    usage: dict


def _to_out(hits) -> list[SourceOut]:
    return [
        SourceOut(
            source=hit.source,
            doc_path=hit.doc_path,
            heading_path=hit.heading_path,
            score=round(hit.score, 4),
            text=hit.text,
        )
        for hit in hits
    ]


@app.get("/health")
def health() -> dict:
    store = get_store()
    return {"status": "ok", "chunks": len(store.rows)}


@app.post("/search", response_model=SearchResponse)
def search(request: SearchRequest) -> SearchResponse:
    hits = retrieve(request.question, k=request.k, strategy=request.strategy)
    return SearchResponse(
        question=request.question,
        strategy=request.strategy,
        results=_to_out(hits),
    )


@app.post("/ask", response_model=AskResponse)
def ask(request: SearchRequest) -> AskResponse:
    # Imported here rather than at module scope so that /search and /health
    # keep working when no API key is configured.
    from app.generate import answer_question

    try:
        result = answer_question(
            request.question, k=request.k, strategy=request.strategy
        )
    except Exception as exc:  # noqa: BLE001 - surfaced to the caller below
        raise HTTPException(
            status_code=502,
            detail=f"Generation failed: {type(exc).__name__}: {exc}",
        ) from exc

    return AskResponse(
        question=request.question,
        answer=result.text,
        sources=_to_out(result.sources),
        usage=result.usage,
    )


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse((STATIC_DIR / "index.html").read_text(encoding="utf-8"))
