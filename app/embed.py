"""Turn text into vectors.

Isolated in its own module on purpose: the embedding model is the component
you are most likely to swap. Everything else in the project talks to these two
functions and does not care what is behind them.

We use bge-small-en-v1.5 through fastembed, which runs the model locally via
ONNX Runtime. No PyTorch, no GPU, no API key, no per-query cost. The tradeoff
is quality: a hosted model such as Voyage AI's voyage-3 (Anthropic's
recommended embedding provider -- Anthropic does not serve embeddings itself)
scores better on retrieval benchmarks. Swapping is roughly ten lines here.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np

from app.config import (
    EMBED_BATCH_SIZE,
    EMBED_MAX_WORDS,
    EMBEDDING_MODEL,
    QUERY_PREFIX,
)


@lru_cache(maxsize=1)
def _model():
    """Load the model once per process.

    The first call downloads ~130 MB into fastembed's cache directory; later
    calls are instant. lru_cache is doing the work of a singleton here.
    """
    from fastembed import TextEmbedding

    return TextEmbedding(model_name=EMBEDDING_MODEL)


def _truncate(text: str, max_words: int = EMBED_MAX_WORDS) -> str:
    """Clip text to the model's usable context before embedding it.

    The tokenizer would drop the overflow anyway; doing it explicitly keeps
    memory bounded and makes the limit visible in the code rather than being a
    silent property of a model you didn't write.
    """
    words = text.split()
    return " ".join(words[:max_words]) if len(words) > max_words else text


def embed_documents(texts: list[str], progress: bool = False) -> np.ndarray:
    """Embed passages for storage. Shape: (len(texts), EMBEDDING_DIM)."""
    model = _model()
    vectors: list[np.ndarray] = []

    for start in range(0, len(texts), EMBED_BATCH_SIZE):
        batch = [_truncate(t) for t in texts[start:start + EMBED_BATCH_SIZE]]
        vectors.extend(model.embed(batch, batch_size=len(batch)))
        if progress:
            done = min(start + EMBED_BATCH_SIZE, len(texts))
            print(f"  embedded {done}/{len(texts)}", end="\r", flush=True)

    if progress:
        print()
    return np.array(vectors, dtype=np.float32)


def embed_query(text: str) -> np.ndarray:
    """Embed a user question for search. Shape: (EMBEDDING_DIM,).

    Note the prefix. bge models are trained asymmetrically: passages are
    embedded bare, queries are embedded with an instruction prefix. Skipping it
    still "works" -- you get vectors, you get results, nothing errors -- you
    just quietly lose retrieval accuracy. Silent quality bugs like this are the
    reason the evaluation harness in evaluation/ exists.
    """
    prefixed = f"{QUERY_PREFIX}{text}"
    return np.array(next(iter(_model().embed([prefixed]))), dtype=np.float32)
