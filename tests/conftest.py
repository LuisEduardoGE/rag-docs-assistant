"""Shared fixtures. Nothing here downloads a model or calls an API.

`tiny_store` writes a three-chunk LanceDB table to a temp dir, with hand-made
vectors, and swaps the query embedder for a fixed vector, so vector, keyword
and hybrid retrieval all run for real without fastembed.
"""

from __future__ import annotations

import lancedb
import numpy as np
import pytest

from app import retrieve as retrieve_mod
from app.config import EMBEDDING_DIM, TABLE_NAME
from app.index import SCHEMA

DOCS = [
    ("tutorial/static-files.md", "Static Files", "Serve a directory of assets by mounting it on the app."),
    ("reference/staticfiles.md", "StaticFiles", "StaticFiles is the class behind mounted directories. StaticFiles StaticFiles."),
    ("tutorial/cookies.md", "Cookie Parameters", "Read a cookie by declaring a Cookie parameter."),
]


def unit_vector(axis: int, sign: float = 1.0) -> list[float]:
    v = np.zeros(EMBEDDING_DIM, dtype=np.float32)
    v[axis] = sign
    return v.tolist()


# Vector ranking for every query: tutorial (same direction), cookies (orthogonal),
# reference (opposite direction).
VECTORS = [unit_vector(0), unit_vector(0, -1.0), unit_vector(2)]


@pytest.fixture
def tiny_store(tmp_path, monkeypatch):
    db_dir = tmp_path / "lancedb"
    rows = [
        {
            "id": i,
            "doc_path": doc_path,
            "heading_path": heading,
            "text": f"{doc_path} | {heading}\n\n{body}",
            "n_words": len(body.split()),
            "vector": VECTORS[i],
        }
        for i, (doc_path, heading, body) in enumerate(DOCS)
    ]
    lancedb.connect(db_dir).create_table(TABLE_NAME, data=rows, schema=SCHEMA)

    # The fake embedder points every question at chunk 0 (the tutorial page).
    monkeypatch.setattr(retrieve_mod, "LANCEDB_DIR", db_dir)
    monkeypatch.setattr(
        retrieve_mod, "embed_query", lambda q: np.array(unit_vector(0), dtype=np.float32)
    )
    retrieve_mod.get_store.cache_clear()
    yield retrieve_mod.get_store()
    retrieve_mod.get_store.cache_clear()
