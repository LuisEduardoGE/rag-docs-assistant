"""Every tunable value in one place.

Keeping settings here (rather than scattered as literals) is what makes the
evaluation harness useful: you change CHUNK_TARGET_WORDS or TOP_K, re-run
`python -m evaluation.run_eval`, and see whether the number moved.
"""

from __future__ import annotations

import os
from pathlib import Path

# --- paths -----------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CORPUS_DIR = DATA_DIR / "corpus"          # raw markdown, downloaded
LANCEDB_DIR = DATA_DIR / "lancedb"        # the vector index
TABLE_NAME = "chunks"

# --- corpus ----------------------------------------------------------------

DOCS_TARBALL_URL = "https://codeload.github.com/fastapi/fastapi/tar.gz/refs/heads/master"
DOCS_SUBPATH = "docs/en/docs"

# --- chunking --------------------------------------------------------------
# Chunks are measured in words, not tokens. Words are easier to reason about
# and roughly 0.75 tokens each for English prose, which is close enough when
# the number is a tuning knob rather than a hard limit.

CHUNK_TARGET_WORDS = 220   # aim for chunks around this size
CHUNK_MAX_WORDS = 400      # hard ceiling before we force a split
CHUNK_MIN_WORDS = 60       # anything smaller gets merged into its neighbour
CHUNK_OVERLAP_WORDS = 40   # repeated tail of the previous chunk

# --- embeddings ------------------------------------------------------------
# bge-small-en-v1.5 runs locally through ONNX (no PyTorch, no GPU, no API key).
# 384 dimensions, ~130 MB download on first use.
#
# Anthropic does not serve an embeddings endpoint. If you later want a hosted
# model, Anthropic recommends Voyage AI (voyage-3 and friends). Swapping is a
# change to this one module -- see app/embed.py.

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIM = 384

# bge-small has a 512-token context. Anything past that is silently dropped by
# the tokenizer -- no error, no warning, just a vector that ignores the tail of
# your chunk. 512 tokens is roughly 380 English words, so we truncate at 350 to
# leave headroom for code, which tokenizes far less efficiently than prose.
#
# Only the *embedding* is truncated. The full chunk text is still stored and
# still handed to Claude, so nothing is lost from the answer -- only from the
# search key. This is why CHUNK_MAX_WORDS is 400 and not 2000.
EMBED_MAX_WORDS = 350

# Embed in modest batches. The default batch size holds far more activations in
# memory at once than this workload needs.
EMBED_BATCH_SIZE = 64

# bge models are trained with an instruction prefix on the *query* side only.
# Forgetting this quietly costs you a few points of retrieval accuracy, which
# is exactly the kind of bug an evaluation harness exists to catch.
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

# --- retrieval -------------------------------------------------------------

TOP_K = 4              # chunks handed to the model
CANDIDATE_K = 20       # chunks pulled from each retriever before fusion
RRF_K = 60             # Reciprocal Rank Fusion damping constant (standard value)

# Fusion weights. Textbook RRF weights every retriever equally, and measuring
# that showed it actively hurting: BM25 is the weaker retriever here, and an
# equal vote let it drag correct pages out of the top 4. Weighting the fusion
# toward the stronger retriever keeps BM25's contribution where it helps
# (rare literal identifiers) without letting it overrule vector search on
# ordinary paraphrased questions.
#
# 3:1 is deliberately a round number rather than the exact optimum. The best
# value on the eval set was 4:1, but that was chosen by looking at the answers,
# with no held-out set to check it against -- so the extra decimal place would
# be fitting noise, not signal. See evaluation/README.md.
RRF_WEIGHT_VECTOR = 3.0
RRF_WEIGHT_KEYWORD = 1.0

# --- generation ------------------------------------------------------------

ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-5")
MAX_TOKENS = 8000

# Grounded question answering is not a hard reasoning task: the answer is
# sitting in the retrieved text. "low" effort keeps latency and cost down with
# no measurable quality loss here. Raise it if you start asking the model to
# synthesise across many chunks.
EFFORT = os.environ.get("ANTHROPIC_EFFORT", "low")
