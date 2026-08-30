# Evaluation

Retrieval quality, measured. This directory is the reason the project is worth reading.

```bash
python -m evaluation.run_eval                    # both sets, all three retrievers
python -m evaluation.run_eval --verbose          # show every miss
python -m evaluation.run_eval --set identifiers  # one set
python -m evaluation.run_eval --k 8              # widen the window
```

## What is measured

Retrieval only — not the wording of the final answer. That is deliberate: retrieval is where RAG systems actually fail, and it can be scored objectively against labelled data. Grading generated prose needs a model-as-judge and a much longer argument about whether the judge is right.

- **Hit@k** — did a correct page appear in the top *k* chunks? The blunt question: *could* the model have answered?
- **MRR@k** — 1/(rank of the first correct chunk), averaged. The sharper question: was it at the top, or scraping in at position 4?

## Results

k = 4, the same four chunks the model receives.

**`main` — 22 paraphrased questions** (how a real user asks, before they know the vocabulary):

| strategy | Hit@4 | MRR@4 |
|---|---:|---:|
| vector | 100.0% | 0.943 |
| keyword | 90.9% | 0.663 |
| **hybrid (3:1)** | **100.0%** | **0.943** |

**`identifiers` — 8 queries built on rare literal tokens** (`HTTPException`, `jsonable_encoder`, `APIRouter`):

| strategy | Hit@4 | MRR@4 |
|---|---:|---:|
| vector | 100.0% | 0.812 |
| keyword | 87.5% | 0.562 |
| **hybrid (3:1)** | **100.0%** | **0.875** |

## How hybrid retrieval nearly got cut

The plan was to build hybrid search, show it beating both single retrievers, and move on. The measurement said otherwise.

**With textbook equal-weight RRF, hybrid was *worse* than vector search alone** — 95.5% / 0.864 against 100% / 0.943. Running with `--verbose` showed exactly one question flipping:

```
Q: How do I serve static files like CSS and images?
   expected:  tutorial/static-files.md
   retrieved: reference/staticfiles.md, how-to/custom-docs-ui-assets.md, ...
```

BM25 saw the literal string `StaticFiles` in the API reference page and ranked it first. Vector search had correctly preferred the tutorial. Equal-weight fusion let the weaker retriever overrule the stronger one.

Two things follow, and both are the point of having an evaluation harness at all:

**1. The fix is weighting, not deletion.** Favouring the vector ranking 3:1 restored the main-set score to 100% / 0.943 — no worse than vector alone.

**2. But that only shows hybrid does no *harm*.** To justify the extra code it has to do some *good*, and the main question set could never show that: 22 paraphrased questions is vector search's home turf, and contains almost no queries where exact-token matching matters. So the `identifiers` set was written specifically to probe the case where BM25 should earn its place — and there, hybrid beats vector 0.875 to 0.812.

That is the argument for shipping hybrid: it costs nothing on the questions vector already handles, and it wins on a query class that vector alone handles less well.

### On the weight itself

The best value on the main set was 4:1 (MRR 0.955). The shipped value is 3:1.

4:1 was chosen by looking at the answers, on 22 questions, with no held-out set. The gain over 3:1 was 0.012 MRR — one question moving one position. That is noise, and tuning a parameter to it would be fitting the test set rather than the problem. 3:1 is a round number in the same region that does not pretend to a precision the evidence does not support.

## Honest limitations

- **30 questions total, written by one person** — mine, so they carry my blind spots about what users ask.
- **No held-out set.** Every number here was measured on data I could see while tuning. The 3:1 weight is a deliberate hedge against that, not a solution to it.
- **Retrieval only.** A correct chunk in position 1 and a good final answer are not the same thing.
- **Labels are judgement calls.** For *"How do I serve static files?"*, I labelled the tutorial page correct and the API reference page wrong. That is defensible for a how-to question, but someone could reasonably disagree — and the hybrid result above turns on exactly that call.
