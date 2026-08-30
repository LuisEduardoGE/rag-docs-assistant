"""Find the chunks most likely to answer a question.

Three retrievers live here, and the evaluation harness scores all three:

  vector  -- semantic similarity. Handles paraphrase ("can I send this back?"
             finds a passage titled "Returns"), but is blurry on rare literal
             tokens like `response_model` or `HTTPException`.

  keyword -- BM25. Nails exact terms and identifiers, and is helpless when the
             user's words don't appear in the text at all.

  hybrid  -- runs both and fuses the ranked lists with *weighted* Reciprocal
             Rank Fusion, favouring the vector ranking 3:1.

The weighting is the interesting part, and it was not the original plan.
Textbook RRF weights every retriever equally; measured that way, hybrid scored
*worse* than vector search alone (MRR 0.864 vs 0.943), because BM25 is the
weaker retriever on this corpus and an equal vote let it push correct pages out
of the top 4. Weighting toward the stronger retriever keeps BM25's contribution
where it helps -- rare literal identifiers like `HTTPException` -- without
letting it overrule vector search on ordinary paraphrased questions.

The full experiment, including the numbers that killed the first version, is
written up in evaluation/README.md.

RRF fuses *ranks*, not scores, which is the reason to prefer it here: cosine
similarity and BM25 live on completely different scales, and any attempt to
normalise them into a weighted sum needs constants you would have to re-tune
every time the corpus changes.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache

import lancedb

from app.config import (
    CANDIDATE_K,
    LANCEDB_DIR,
    RRF_K,
    RRF_WEIGHT_KEYWORD,
    RRF_WEIGHT_VECTOR,
    TABLE_NAME,
    TOP_K,
)
from app.embed import embed_query

TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")

BM25_K1 = 1.5
BM25_B = 0.75


@dataclass
class Hit:
    """One retrieved chunk, with the score that got it here."""

    id: int
    doc_path: str
    heading_path: str
    text: str
    score: float

    @property
    def source(self) -> str:
        """Human-readable citation, e.g. 'tutorial/first-steps.md > Check it'."""
        return f"{self.doc_path} > {self.heading_path}" if self.heading_path else self.doc_path


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens, plus the parts of any snake_case identifier.

    `response_model` becomes ["response_model", "response", "model"], so a
    question phrased either way can match the same passage.
    """
    tokens: list[str] = []
    for raw in TOKEN_RE.findall(text.lower()):
        tokens.append(raw)
        if "_" in raw:
            tokens.extend(part for part in raw.split("_") if part)
    return tokens


class Store:
    """The index, loaded once and held in memory.

    This corpus is small enough (hundreds of chunks) that BM25 in plain Python
    is instantaneous. At a million chunks you would push keyword search into
    the database instead -- LanceDB has a full-text index for exactly this.
    """

    def __init__(self) -> None:
        if not LANCEDB_DIR.exists():
            raise SystemExit(
                "No index found. Run `python -m app.fetch_docs` then "
                "`python -m app.index` first."
            )

        db = lancedb.connect(LANCEDB_DIR)
        self.table = db.open_table(TABLE_NAME)
        self.rows = self.table.to_pandas().to_dict("records")

        # --- BM25 statistics -------------------------------------------------
        self.doc_tokens: list[Counter] = []
        self.doc_len: list[int] = []
        doc_freq: Counter = Counter()

        for row in self.rows:
            counts = Counter(tokenize(row["text"]))
            self.doc_tokens.append(counts)
            self.doc_len.append(sum(counts.values()))
            doc_freq.update(counts.keys())

        n_docs = len(self.rows)
        self.avg_len = (sum(self.doc_len) / n_docs) if n_docs else 0.0
        self.idf = {
            term: math.log(1 + (n_docs - freq + 0.5) / (freq + 0.5))
            for term, freq in doc_freq.items()
        }

    # --- retrievers ---------------------------------------------------------

    def search_vector(self, question: str, k: int = CANDIDATE_K) -> list[Hit]:
        """Nearest neighbours by cosine similarity."""
        vector = embed_query(question)
        results = (
            self.table.search(vector.tolist())
            .metric("cosine")
            .limit(k)
            .to_list()
        )
        # LanceDB returns cosine *distance* (smaller is closer). Flip it so
        # that everywhere in this codebase, bigger score means better.
        return [
            Hit(
                id=int(row["id"]),
                doc_path=row["doc_path"],
                heading_path=row["heading_path"],
                text=row["text"],
                score=1.0 - float(row["_distance"]),
            )
            for row in results
        ]

    def search_keyword(self, question: str, k: int = CANDIDATE_K) -> list[Hit]:
        """Classic BM25 over the same chunks."""
        query_terms = tokenize(question)
        scored: list[tuple[float, int]] = []

        for i, counts in enumerate(self.doc_tokens):
            score = 0.0
            length = self.doc_len[i]
            for term in query_terms:
                freq = counts.get(term, 0)
                if not freq:
                    continue
                idf = self.idf.get(term, 0.0)
                denominator = freq + BM25_K1 * (
                    1 - BM25_B + BM25_B * length / (self.avg_len or 1)
                )
                score += idf * (freq * (BM25_K1 + 1)) / denominator
            if score > 0:
                scored.append((score, i))

        scored.sort(reverse=True)
        return [self._hit(i, score) for score, i in scored[:k]]

    def search_hybrid(
        self,
        question: str,
        k: int = TOP_K,
        weight_vector: float = RRF_WEIGHT_VECTOR,
        weight_keyword: float = RRF_WEIGHT_KEYWORD,
    ) -> list[Hit]:
        """Fuse the vector and keyword rankings with weighted RRF.

        The weights are not decoration. Measured with equal weights, this
        performed *worse* than vector search alone -- see evaluation/README.md.
        BM25 is the weaker retriever on this corpus, and an equal vote let it
        push correct pages out of the top 4 on ordinary paraphrased questions.
        """
        vector_hits = self.search_vector(question, CANDIDATE_K)
        keyword_hits = self.search_keyword(question, CANDIDATE_K)

        fused: dict[int, float] = {}
        for ranking, weight in ((vector_hits, weight_vector), (keyword_hits, weight_keyword)):
            for rank, hit in enumerate(ranking):
                # rank is 0-based; +1 so the top result contributes w/(K+1).
                fused[hit.id] = fused.get(hit.id, 0.0) + weight / (RRF_K + rank + 1)

        order = sorted(fused.items(), key=lambda pair: pair[1], reverse=True)
        return [self._hit(chunk_id, score) for chunk_id, score in order[:k]]

    # --- helpers ------------------------------------------------------------

    def _hit(self, row_index: int, score: float) -> Hit:
        row = self.rows[row_index]
        return Hit(
            id=int(row["id"]),
            doc_path=row["doc_path"],
            heading_path=row["heading_path"],
            text=row["text"],
            score=float(score),
        )


@lru_cache(maxsize=1)
def get_store() -> Store:
    """Process-wide singleton, so the API doesn't rebuild BM25 per request."""
    return Store()


def retrieve(question: str, k: int = TOP_K, strategy: str = "hybrid") -> list[Hit]:
    """Public entry point used by the API and the evaluation harness."""
    store = get_store()
    if strategy == "vector":
        return store.search_vector(question, k)
    if strategy == "keyword":
        return store.search_keyword(question, k)
    if strategy == "hybrid":
        return store.search_hybrid(question, k)
    raise ValueError(f"Unknown strategy: {strategy!r}")
