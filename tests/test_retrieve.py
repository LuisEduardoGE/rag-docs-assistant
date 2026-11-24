import pytest

from app.config import RRF_K
from app.retrieve import Hit, retrieve, tokenize


def test_tokenize_lowercases_and_splits_snake_case():
    assert tokenize("Use response_model, OK?") == ["use", "response_model", "response", "model", "ok"]


def test_tokenize_ignores_punctuation_only_input():
    assert tokenize("--- ... !!!") == []


def test_hit_source_includes_heading_when_present():
    assert Hit(1, "a.md", "Intro > Setup", "", 0.0).source == "a.md > Intro > Setup"
    assert Hit(1, "a.md", "", "", 0.0).source == "a.md"


def test_keyword_search_prefers_literal_identifier(tiny_store):
    hits = tiny_store.search_keyword("StaticFiles")
    assert hits[0].doc_path == "reference/staticfiles.md"
    assert all(h.score > 0 for h in hits)


def test_keyword_search_returns_nothing_for_unknown_terms(tiny_store):
    assert tiny_store.search_keyword("websocket") == []


def test_vector_search_flips_distance_to_similarity(tiny_store):
    hits = tiny_store.search_vector("anything", k=3)
    assert hits[0].doc_path == "tutorial/static-files.md"
    assert hits[0].score == pytest.approx(1.0)


def test_hybrid_rrf_weights_decide_disagreements(tiny_store):
    # Vector ranks tutorial > cookies > reference; BM25 ranks reference > tutorial.
    question = "StaticFiles static"
    assert tiny_store.search_keyword(question)[0].doc_path == "reference/staticfiles.md"

    favour_vector = tiny_store.search_hybrid(question, k=2, weight_vector=3.0, weight_keyword=1.0)
    assert favour_vector[0].doc_path == "tutorial/static-files.md"

    favour_keyword = tiny_store.search_hybrid(question, k=2, weight_vector=1.0, weight_keyword=3.0)
    assert favour_keyword[0].doc_path == "reference/staticfiles.md"


def test_hybrid_score_is_weighted_reciprocal_rank(tiny_store):
    top = tiny_store.search_hybrid("serve", k=1, weight_vector=3.0, weight_keyword=1.0)[0]
    # The tutorial page is rank 0 for both retrievers ("serve" only appears there).
    assert top.doc_path == "tutorial/static-files.md"
    assert top.score == pytest.approx(3.0 / (RRF_K + 1) + 1.0 / (RRF_K + 1))


def test_retrieve_rejects_unknown_strategy(tiny_store):
    with pytest.raises(ValueError):
        retrieve("q", strategy="magic")
