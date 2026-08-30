"""Assemble the prompt and ask Claude.

Everything the retrieval half of this project does exists to make this one
string good. If an answer is wrong, print the prompt before you touch anything
else -- most of the time you will see immediately that the answer simply
wasn't in it, which is a retrieval bug wearing a generation bug's clothes.
"""

from __future__ import annotations

from dataclasses import dataclass

import anthropic

from app.config import ANTHROPIC_MODEL, EFFORT, MAX_TOKENS, TOP_K
from app.retrieve import Hit, retrieve

SYSTEM_PROMPT = """\
You are a documentation assistant for the FastAPI web framework.

Answer using only the numbered passages provided in the user's message. The \
passages are excerpts from the official FastAPI documentation.

Rules:
- If the passages do not contain the answer, say so plainly and stop. Do not \
fall back on your own knowledge of FastAPI, even when you are confident.
- Cite the passage number inline, like [2], for every claim you make.
- Some passages will be irrelevant. Ignore them rather than working them in.
- Prefer showing a short code example when the passages contain one.
- Be concise. Answer the question that was asked."""


@dataclass
class Answer:
    text: str
    sources: list[Hit]
    prompt: str
    usage: dict


def build_prompt(question: str, hits: list[Hit]) -> str:
    """Format retrieved chunks plus the question into a single user turn.

    Passages are numbered so the model has something concrete to cite, and
    each carries its source path so a citation can be traced back to a file.
    """
    blocks = []
    for i, hit in enumerate(hits, start=1):
        blocks.append(f"[{i}] source: {hit.source}\n{hit.text}")
    passages = "\n\n---\n\n".join(blocks)

    return (
        "Here are the documentation passages retrieved for this question.\n\n"
        f"{passages}\n\n"
        "---\n\n"
        f"Question: {question}"
    )


def answer_question(
    question: str,
    k: int = TOP_K,
    strategy: str = "hybrid",
    client: anthropic.Anthropic | None = None,
) -> Answer:
    """Retrieve, then generate a grounded answer."""
    hits = retrieve(question, k=k, strategy=strategy)
    prompt = build_prompt(question, hits)

    # Zero-arg constructor: the SDK resolves ANTHROPIC_API_KEY, then
    # ANTHROPIC_AUTH_TOKEN, then a profile stored by `ant auth login`.
    client = client or anthropic.Anthropic()

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        # Grounded extraction from four short passages is not a hard reasoning
        # problem. Low effort keeps latency and cost down; raise it if you
        # start asking questions that need synthesis across many sources.
        output_config={"effort": EFFORT},
        messages=[{"role": "user", "content": prompt}],
    )

    # Claude can decline a request outright. On a refusal the content list is
    # empty, so reading content[0] without this check raises IndexError and
    # your API returns a 500 instead of a useful message.
    if response.stop_reason == "refusal":
        text = "The model declined to answer this question."
    else:
        text = "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()

    return Answer(
        text=text,
        sources=hits,
        prompt=prompt,
        usage={
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    )


if __name__ == "__main__":
    import sys

    question = " ".join(sys.argv[1:]) or "How do I declare a query parameter as optional?"
    result = answer_question(question)

    print(result.text)
    print("\nSources:")
    for i, hit in enumerate(result.sources, start=1):
        print(f"  [{i}] {hit.source}")
    print(f"\nTokens: {result.usage}")
