"""Measure retrieval quality.

This is the file that turns a weekend RAG demo into an engineering project.
Without it you have opinions about whether a change helped; with it you have a
number.

It scores retrieval only -- not the wording of the final answer. That is a
deliberate choice: retrieval is where these systems actually fail, and it can
be measured objectively against labelled data. Grading generated prose needs a
model-as-judge and a much longer argument about whether the judge is right.

Two metrics:

  Hit@k  -- did any of the top k chunks come from a correct page?
            The blunt question: could the model possibly have answered?

  MRR@k  -- 1/rank of the first correct chunk, averaged over questions.
            The sharper question: was it near the top, or scraping in at #4?
            A system with Hit@4 = 1.0 and MRR = 0.4 is one bad day from
            breaking, because it depends on chunks the model may skim past.

Run:  python -m evaluation.run_eval
      python -m evaluation.run_eval --k 4 --verbose
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.config import TOP_K
from app.retrieve import retrieve

EVAL_DIR = Path(__file__).parent
STRATEGIES = ["vector", "keyword", "hybrid"]

# Two question sets. "main" is the headline number; "identifiers" exists to
# test whether keyword search contributes anything, because the main set is
# almost entirely paraphrased questions and cannot answer that on its own.
QUESTION_SETS = {
    "main": EVAL_DIR / "questions.json",
    "identifiers": EVAL_DIR / "questions_identifiers.json",
}


def load_questions(name: str) -> list[dict]:
    data = json.loads(QUESTION_SETS[name].read_text(encoding="utf-8"))
    return data["questions"]


def evaluate(strategy: str, questions: list[dict], k: int) -> dict:
    """Score one retrieval strategy over the whole question set."""
    hits = 0
    reciprocal_ranks = 0.0
    misses: list[dict] = []

    for item in questions:
        expected = set(item["expected_docs"])
        results = retrieve(item["question"], k=k, strategy=strategy)

        rank_of_first_correct = None
        for rank, hit in enumerate(results, start=1):
            if hit.doc_path in expected:
                rank_of_first_correct = rank
                break

        if rank_of_first_correct is not None:
            hits += 1
            reciprocal_ranks += 1.0 / rank_of_first_correct
        else:
            misses.append(
                {
                    "question": item["question"],
                    "expected": sorted(expected),
                    "got": [hit.doc_path for hit in results],
                }
            )

    total = len(questions)
    return {
        "strategy": strategy,
        "hit_rate": hits / total,
        "mrr": reciprocal_ranks / total,
        "hits": hits,
        "total": total,
        "misses": misses,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Score retrieval strategies.")
    parser.add_argument("--k", type=int, default=TOP_K, help="chunks retrieved per question")
    parser.add_argument("--verbose", action="store_true", help="print every miss")
    parser.add_argument(
        "--strategy",
        choices=STRATEGIES + ["all"],
        default="all",
        help="which retriever to score",
    )
    parser.add_argument(
        "--set",
        dest="question_set",
        choices=list(QUESTION_SETS) + ["all"],
        default="all",
        help="which question set to score",
    )
    args = parser.parse_args()

    strategies = STRATEGIES if args.strategy == "all" else [args.strategy]
    set_names = list(QUESTION_SETS) if args.question_set == "all" else [args.question_set]

    reports = []
    for set_name in set_names:
        questions = load_questions(set_name)
        print(f"\n{set_name}: {len(questions)} questions at k={args.k}")
        print(f"{'strategy':<10} {'Hit@k':>8} {'MRR@k':>8}   {'hits':>9}")
        print("-" * 42)

        for strategy in strategies:
            report = evaluate(strategy, questions, args.k)
            report["set"] = set_name
            reports.append(report)
            print(
                f"{report['strategy']:<10} "
                f"{report['hit_rate']:>7.1%} "
                f"{report['mrr']:>8.3f}   "
                f"{report['hits']:>4}/{report['total']:<4}"
            )

    if args.verbose:
        for report in reports:
            if not report["misses"]:
                continue
            print(f"\nMisses for {report['strategy']} on {report['set']}:")
            for miss in report["misses"]:
                print(f"  Q: {miss['question']}")
                print(f"     expected one of: {', '.join(miss['expected'])}")
                print(f"     retrieved:       {', '.join(miss['got'])}")

    print()


if __name__ == "__main__":
    main()
