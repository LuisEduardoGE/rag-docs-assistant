"""Build the vector index: corpus -> chunks -> vectors -> LanceDB.

This is phase one of a RAG system. It runs offline, on a schedule or whenever
the docs change, and nobody is waiting on it. Phase two (app/retrieve.py) is
the one that has to be fast.

Run:  python -m app.index
"""

from __future__ import annotations

import shutil
import time

import lancedb
import pyarrow as pa

from app.chunk import chunk_corpus
from app.config import (
    CORPUS_DIR,
    EMBEDDING_DIM,
    LANCEDB_DIR,
    TABLE_NAME,
)
from app.embed import embed_documents

# An explicit Arrow schema, rather than letting LanceDB infer one from the
# first row. Inference guesses the vector width from whatever it sees first,
# which turns an embedding-model swap into a confusing runtime error instead
# of a clear one.
SCHEMA = pa.schema(
    [
        pa.field("id", pa.int32()),
        pa.field("doc_path", pa.string()),
        pa.field("heading_path", pa.string()),
        pa.field("text", pa.string()),
        pa.field("n_words", pa.int32()),
        pa.field("vector", pa.list_(pa.float32(), EMBEDDING_DIM)),
    ]
)


def build_index(rebuild: bool = True) -> int:
    """Chunk the corpus, embed every chunk, and write the LanceDB table.

    Returns the number of chunks indexed.
    """
    if not CORPUS_DIR.exists():
        raise SystemExit(
            "No corpus found. Run `python -m app.fetch_docs` first."
        )

    started = time.perf_counter()

    print("Chunking corpus...")
    chunks = chunk_corpus(CORPUS_DIR)
    print(f"  {len(chunks)} chunks from {len({c.doc_path for c in chunks})} documents")

    print(f"Embedding {len(chunks)} chunks (first run downloads the model)...")
    vectors = embed_documents([c.text for c in chunks], progress=True)
    print(f"  vectors: {vectors.shape}")

    if vectors.shape[1] != EMBEDDING_DIM:
        raise SystemExit(
            f"Model returned {vectors.shape[1]}-dim vectors but config says "
            f"{EMBEDDING_DIM}. Update EMBEDDING_DIM in app/config.py."
        )

    if rebuild and LANCEDB_DIR.exists():
        shutil.rmtree(LANCEDB_DIR)
    LANCEDB_DIR.mkdir(parents=True, exist_ok=True)

    rows = [
        {
            "id": i,
            "doc_path": chunk.doc_path,
            "heading_path": chunk.heading_path,
            "text": chunk.text,
            "n_words": chunk.n_words,
            "vector": vectors[i].tolist(),
        }
        for i, chunk in enumerate(chunks)
    ]

    db = lancedb.connect(LANCEDB_DIR)
    db.create_table(TABLE_NAME, data=rows, schema=SCHEMA, mode="overwrite")

    elapsed = time.perf_counter() - started
    print(f"Indexed {len(rows)} chunks into {LANCEDB_DIR} in {elapsed:.1f}s")
    return len(rows)


if __name__ == "__main__":
    build_index()
