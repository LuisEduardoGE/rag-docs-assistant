from types import SimpleNamespace

from app import generate
from app.embed import _truncate
from app.retrieve import Hit
from evaluation import run_eval

HITS = [
    Hit(1, "tutorial/cookies.md", "Cookies", "Use Cookie().", 0.9),
    Hit(2, "tutorial/headers.md", "", "Use Header().", 0.5),
]


def test_truncate_clips_to_word_limit():
    assert _truncate("a b c d", max_words=2) == "a b"
    assert _truncate("a b", max_words=5) == "a b"


def test_build_prompt_numbers_passages_with_sources():
    prompt = generate.build_prompt("How do cookies work?", HITS)
    assert "[1] source: tutorial/cookies.md > Cookies" in prompt
    assert "[2] source: tutorial/headers.md" in prompt
    assert prompt.endswith("Question: How do cookies work?")


class FakeClient:
    """Stands in for anthropic.Anthropic, so no key or network is needed."""

    def __init__(self, response):
        self.messages = SimpleNamespace(create=lambda **kwargs: response)


def _response(stop_reason, content):
    return SimpleNamespace(
        stop_reason=stop_reason,
        content=content,
        usage=SimpleNamespace(input_tokens=10, output_tokens=3),
    )


def test_answer_question_joins_text_blocks(monkeypatch):
    monkeypatch.setattr(generate, "retrieve", lambda q, k, strategy: HITS)
    blocks = [
        SimpleNamespace(type="text", text="Use "),
        SimpleNamespace(type="text", text="Cookie() [1]."),
    ]
    answer = generate.answer_question("q", client=FakeClient(_response("end_turn", blocks)))
    assert answer.text == "Use Cookie() [1]."
    assert answer.sources == HITS
    assert answer.usage == {"input_tokens": 10, "output_tokens": 3}


def test_answer_question_handles_refusal_with_empty_content(monkeypatch):
    monkeypatch.setattr(generate, "retrieve", lambda q, k, strategy: HITS)
    answer = generate.answer_question("q", client=FakeClient(_response("refusal", [])))
    assert answer.text == "The model declined to answer this question."


def test_evaluate_computes_hit_rate_and_mrr(monkeypatch):
    ranked = {
        "q1": ["a.md", "b.md"],  # correct at rank 1
        "q2": ["x.md", "b.md"],  # correct at rank 2
        "q3": ["x.md", "y.md"],  # miss
    }
    monkeypatch.setattr(
        run_eval,
        "retrieve",
        lambda question, k, strategy: [Hit(0, p, "", "", 0.0) for p in ranked[question]],
    )
    questions = [
        {"question": "q1", "expected_docs": ["a.md"]},
        {"question": "q2", "expected_docs": ["b.md"]},
        {"question": "q3", "expected_docs": ["z.md"]},
    ]
    report = run_eval.evaluate("hybrid", questions, k=2)
    assert report["hits"] == 2
    assert report["hit_rate"] == 2 / 3
    assert report["mrr"] == (1 + 0.5) / 3
    assert [m["question"] for m in report["misses"]] == ["q3"]


def test_question_sets_are_labelled():
    for name in run_eval.QUESTION_SETS:
        questions = run_eval.load_questions(name)
        assert questions
        assert all(q["question"] and q["expected_docs"] for q in questions)
