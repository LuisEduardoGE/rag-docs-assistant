"""File walkthroughs: each file broken into pieces to type, with a reason.

Each entry is (anchor, title, why). The anchor is a substring of the first
line of that piece; build_guide slices the real file at those lines, so the
pieces are cut from source and rejoin into the exact file.
"""

from __future__ import annotations

W = "<p>{}</p>"


def p(*paragraphs: str) -> str:
    return "".join(f"<p>{text}</p>" for text in paragraphs)


# ---------------------------------------------------------------- config ---

CONFIG = [
    ("", "The docstring, and why this file exists at all",
     p("A module docstring is the first thing anyone reads, including you in three "
       "months. Say what the file is <em>for</em>, not what it contains &mdash; the code "
       "already says what it contains.",
       "The point of this file is that in chapter 14 you will change one number, re-run "
       "the evaluation, and see whether the score moved. That loop only works if the "
       "numbers are findable.")),

    ("# --- paths", "Paths, derived rather than hardcoded",
     p("<code>Path(__file__).resolve().parent.parent</code> walks up from this file to the "
       "project root. Every other path hangs off it.",
       "The alternative &mdash; writing <code>C:\\Users\\you\\rag-docs-assistant\\data</code> "
       "&mdash; breaks the moment anyone else clones your repo, including future you on a "
       "different machine. Deriving from <code>__file__</code> means the project works "
       "wherever it sits.")),

    ("# --- corpus", "Where the documents come from",
     p("Two constants, so that when the FastAPI repo reorganises its docs &mdash; and it "
       "will &mdash; you fix it in one obvious place instead of hunting through a download "
       "script.",
       "<code>DOCS_SUBPATH</code> is the part most likely to break. It is the only reason "
       "the fetcher knows which files in a 17&nbsp;MB archive are documentation.")),

    ("# --- chunking", "The four numbers that shape retrieval",
     p("These decide how documents are cut up, which decides what retrieval can ever "
       "return. They are measured in <strong>words</strong> rather than tokens on purpose: "
       "words are something you can reason about and count by eye, and the number is a "
       "tuning knob rather than a hard API limit.",
       "<code>CHUNK_MIN_WORDS</code> exists because of a real failure &mdash; without it, 78 "
       "chunks came out under 20 words, which is too little signal to ever win a search. "
       "You will see the numbers in chapter 6.")),

    ("# --- embeddings", "The model, and the limit nobody mentions",
     p("<code>bge-small-en-v1.5</code> runs locally through ONNX: no PyTorch, no GPU, no API "
       "key, no per-query cost. 384 dimensions.",
       "<strong>Read the <code>EMBED_MAX_WORDS</code> comment carefully.</strong> The model has "
       "a 512-token context and silently discards everything past it &mdash; no error, no "
       "warning, just a vector that represents the first third of your chunk. This is why "
       "<code>CHUNK_MAX_WORDS</code> is 400 and not 2000: <em>your chunk size must respect "
       "your embedding model's context window.</em>",
       "<code>QUERY_PREFIX</code> is the other invisible one. bge models are trained "
       "asymmetrically &mdash; passages bare, queries prefixed. Skip it and everything still "
       "runs; you just quietly lose accuracy.")),

    ("# --- retrieval", "Retrieval, including two weights that were measured",
     p("<code>TOP_K</code> is how many chunks the model sees. <code>CANDIDATE_K</code> is how "
       "many each retriever produces before fusion &mdash; wider, because fusion needs "
       "something to work with.",
       "The two <code>RRF_WEIGHT_*</code> values are the only numbers in this file that came "
       "out of an experiment rather than a sensible default. With equal weights, hybrid "
       "retrieval scored <em>worse</em> than vector search alone. Chapter 15 is that story; "
       "for now just type them and note that the comment explains itself.")),

    ("# --- generation", "The model call, and a deliberate choice not to spend",
     p("<code>os.environ.get(..., default)</code> lets you override the model or effort "
       "without editing code &mdash; useful when you want to try a different setting for one "
       "run.",
       "<code>EFFORT</code> is set to <code>low</code> on purpose. Reading four short passages "
       "and quoting the relevant one is not a hard reasoning problem. Spending more here "
       "buys nothing, and knowing <em>when not to spend</em> is worth being able to explain.")),
]


# ------------------------------------------------------------- fetch_docs ---

FETCH = [
    ("", "Docstring and imports",
     p("The docstring earns its length here because it answers a question a reviewer will "
       "have: <em>why isn't the corpus in the repo?</em> Answering that in the file itself "
       "means nobody has to ask.",
       "<code>io</code> and <code>tarfile</code> are standard library; <code>httpx</code> is the "
       "one dependency. Standard library first, third party second, your own code last "
       "&mdash; that grouping is conventional in Python and reviewers read it fast.")),

    ("def fetch_docs", "Download the archive into memory",
     p("<code>follow_redirects=True</code> matters: GitHub's codeload endpoint redirects for "
       "branch references, and without it you get a 302 and no data.",
       "<code>raise_for_status()</code> turns a 404 into a loud exception instead of a "
       "cheerful attempt to untar an HTML error page. One line, and it converts a confusing "
       "failure into an obvious one.",
       "<code>with httpx.Client(...) as client:</code> is a <strong>context manager</strong> &mdash; "
       "it guarantees the connection closes even if something raises inside the block.")),

    ("with tarfile.open", "Extract only what you want",
     p("The archive holds the entire FastAPI repository. We want 155 markdown files out of "
       "several thousand, so every member is filtered twice: it must be a real file ending "
       "in <code>.md</code>, and it must sit under the docs path.",
       "The string surgery on <code>member.name</code> is the fiddly part. GitHub wraps "
       "everything in a top folder named <code>&lt;repo&gt;-&lt;branch&gt;/</code>, so paths arrive "
       "as <code>fastapi-master/docs/en/docs/tutorial/first-steps.md</code>. Strip that first "
       "component, then keep the path <em>inside</em> the docs tree &mdash; that relative path "
       "becomes the document identifier used by every later stage, including the evaluation "
       "labels.",
       "<code>io.BytesIO(response.content)</code> lets tarfile read from memory rather than "
       "requiring a temporary file on disk.")),

    ("if __name__", "The entry point",
     p("This is what makes <code>python -m app.fetch_docs</code> work while "
       "<code>from app.fetch_docs import fetch_docs</code> stays silent. Without the guard, "
       "importing the module would start a 17&nbsp;MB download as a side effect.",
       "Every runnable module in this project ends this way.")),
]


# ------------------------------------------------------------------ chunk ---

CHUNK = [
    ("", "Docstring: the three decisions, stated up front",
     p("This docstring is longer than most, and deliberately so. This is the file an "
       "interviewer will ask about, and the three numbered decisions are the answer. "
       "Writing them here means the reasoning lives next to the code rather than in your "
       "memory.")),

    ("class Unit", "A paragraph that remembers where it came from",
     p("A <strong>dataclass</strong> generates <code>__init__</code>, <code>__repr__</code> and "
       "equality from the field declarations, so this is a real class in five lines.",
       "The important part is <code>heading_path</code>. Each paragraph carries the trail of "
       "headings it was found under, which is what makes it possible in a moment to pack "
       "paragraphs across section boundaries <em>without losing track of which section each "
       "one belonged to</em>.")),

    ("HEADING_RE", "Four regexes, each for one kind of noise",
     p("<code>HEADING_RE</code> matches ATX headings (<code>## Title</code>). "
       "<code>ANCHOR_RE</code> strips the <code>{ #anchor }</code> that FastAPI pins onto "
       "headings for its URLs &mdash; useful to the docs site, pure dilution in an embedding.",
       "<code>ADMONITION_RE</code> and <code>INCLUDE_RE</code> drop MkDocs markers that carry no "
       "meaning for retrieval. <code>HTML_COMMENT_RE</code> uses <code>re.DOTALL</code> so it "
       "spans multiple lines.",
       "Compiling them once at module level rather than inside the loop is the normal habit: "
       "these run against every line of 154 documents.")),

    ("class Chunk", "The output type",
     p("<code>doc_path</code> and <code>heading_path</code> are metadata, but "
       "<code>text</code> is what gets embedded and what the model eventually reads &mdash; and "
       "notice from the docstring that the heading path is <em>inside</em> <code>text</code>, "
       "not only in the metadata field.",
       "That is decision 2, and it is the cheapest large win available: a chunk reading "
       "&ldquo;It defaults to 422.&rdquo; is unfindable, but the same chunk prefixed with "
       "<code>handling-errors.md | Handling Errors &gt; Validation errors</code> contains the "
       "words someone would actually search for.")),

    ("def _clean", "Remove what would only add noise",
     p("Front matter, HTML comments, admonition markers, include directives. None of it "
       "means anything to a reader looking for an answer, and all of it competes for the 512 "
       "tokens the embedding model will actually read.",
       "The leading underscore on <code>_clean</code> is a Python convention meaning "
       "&ldquo;internal to this module&rdquo;. Nothing enforces it; everyone respects it.")),

    ("def _sections", "The heading walker &mdash; and the bug it fixes",
     p("This turns a flat document into <code>(heading_path, body)</code> pairs. The "
       "<code>stack</code> holds the current trail of headings; when a new heading arrives, "
       "pop everything at the same or deeper level (those are siblings or children, not "
       "ancestors) then push the new one.",
       "<strong>The <code>in_fence</code> flag is the whole reason this function is longer than "
       "you would expect.</strong> My first version treated any line starting with "
       "<code>#</code> as a heading. In a corpus full of Python examples, every "
       "<code>#&nbsp;comment</code> inside a code block became a fake section boundary and "
       "shredded the examples.",
       "Ninety percent of chunking bugs have this shape: markup that means something "
       "different inside a code fence.")),

    ("def _split_paragraphs", "Break a section into paragraphs, keeping code whole",
     p("Blank lines separate paragraphs &mdash; except inside a fenced code block, where a "
       "blank line is just a blank line. The same <code>in_fence</code> idea again.",
       "Splitting a code example in half produces two fragments that are individually "
       "meaningless: neither retrieves well, and neither helps the model if it does. Keeping "
       "the fence whole costs nothing and removes that failure.")),

    ("def _pack", "Group paragraphs into chunks &mdash; the measured decision",
     p("This is the function that changed after measurement. Packing runs <em>across</em> "
       "heading boundaries, not within them.",
       "Per-section packing sounds tidier and is what I wrote first. It produced a median "
       "chunk of <strong>72 words</strong> with 78 fragments under 20 words, because the "
       "FastAPI docs have many short subsections. Packing across boundaries moved the median "
       "to <strong>256</strong>. You will reproduce both numbers in the next chapter.",
       "The two escape hatches matter: a single oversized paragraph (usually a long code "
       "block) becomes its own chunk rather than dragging a group over the ceiling, and any "
       "runt at the end is merged backwards into its predecessor.")),

    ("def _tail_words", "The overlap helper",
     p("Five lines, and it implements decision 3. The last <em>n</em> words of the previous "
       "chunk get carried into the next one, so an answer sitting on a boundary is never cut "
       "in half.",
       "It costs a little storage and removes a whole class of silent failure &mdash; the kind "
       "where retrieval returns a chunk that stops mid-sentence just before the useful part.")),

    ("def chunk_markdown", "Assemble one document",
     p("This is where the three decisions come together. Flatten the document into units "
       "that remember their heading, pack them, then build each chunk's text.",
       "Two details worth noticing. When a chunk spans a heading boundary, the new heading is "
       "inserted inline as <code>## Title</code> so the transition stays visible to whoever "
       "reads it. And the header line &mdash; path plus heading path &mdash; is prepended to "
       "the text itself, which is decision 2 finally taking effect.")),

    ("def chunk_corpus", "Walk the corpus",
     p("<code>rglob(\"*.md\")</code> recurses; <code>sorted()</code> makes the chunk ordering "
       "deterministic, which means two runs produce identical IDs and your evaluation numbers "
       "are comparable between runs.",
       "The <code>startswith(\"_\")</code> skip is not cosmetic. <code>_llm-test.md</code> is "
       "tooling scaffolding for the docs site, not documentation &mdash; indexing it means a "
       "user can retrieve it as an answer.")),
]


# ------------------------------------------------------------------ embed ---

EMBED = [
    ("", "Docstring and imports: why this file is isolated",
     p("This is the component you are most likely to replace, so everything else in the "
       "project talks to two functions and knows nothing about what is behind them.",
       "The docstring states the tradeoff explicitly: local and free, versus a hosted model "
       "that would score better. Anthropic does not sell embeddings &mdash; Claude is the "
       "generation half only &mdash; so a hosted option means another vendor.")),

    ("@lru_cache", "Load the model once",
     p("<code>@lru_cache(maxsize=1)</code> is a <strong>decorator</strong>: a function that wraps "
       "another function to change its behaviour. This one caches the return value, so the "
       "model loads on first call and every later call returns the same object instantly.",
       "It does the job of a singleton in three characters. The import sits <em>inside</em> the "
       "function so that merely importing this module does not pull in ONNX Runtime.")),

    ("def _truncate", "Respect the model's context window, visibly",
     p("<strong>This function exists because of a bug that produced no error message.</strong> My "
       "first index build climbed to 10&nbsp;GB of RAM and never finished, because a "
       "1,512-word chunk was being fed to a model with a 512-token context.",
       "The tokenizer would silently discard the overflow anyway. Doing it explicitly bounds "
       "memory and, more importantly, makes the limit <em>visible in the code</em> rather than "
       "being an invisible property of a model you did not write.",
       "Only the embedding is truncated. The full chunk text is still stored and still handed "
       "to Claude, so nothing is lost from the answer &mdash; only from the search key.")),

    ("def embed_documents", "Embed in batches",
     p("Batching in groups of 64 rather than handing the model 767 texts at once is what took "
       "memory from 10&nbsp;GB to 2.6&nbsp;GB.",
       "The <code>progress</code> flag prints a counter that overwrites itself with "
       "<code>\\r</code>. That sounds cosmetic, but this step takes eleven minutes on a laptop "
       "CPU and without it you cannot tell a slow run from a hung one.")),

    ("def embed_query", "Embed a question &mdash; and the prefix that is easy to miss",
     p("Almost identical to <code>embed_documents</code>, with one difference that is the whole "
       "point of having a separate function: the <strong>instruction prefix</strong>.",
       "bge models are trained asymmetrically &mdash; passages embedded bare, queries embedded "
       "with a prefix. Skip it and nothing breaks: you get vectors, no error, plausible "
       "results, and quietly worse retrieval. Silent quality bugs like this are exactly why "
       "the evaluation harness exists.")),
]


# ------------------------------------------------------------------ index ---

INDEX = [
    ("", "Docstring and imports",
     p("The docstring names the thing beginners most often confuse: this is <em>phase one</em>, "
       "it runs offline, and nobody is waiting on it. The fast half comes later.",
       "<code>pyarrow</code> arrives as a LanceDB dependency; you use it directly for the "
       "schema.")),

    ("SCHEMA = pa.schema", "Declare the schema by hand",
     p("You could let LanceDB infer a schema from the first row. Don't.",
       "Inference guesses the vector width from whatever it happens to see first. That turns a "
       "future embedding-model swap into a confusing runtime error deep inside the database, "
       "instead of the clear message raised by the <code>EMBEDDING_DIM</code> check a few lines "
       "further down.",
       "<code>pa.list_(pa.float32(), EMBEDDING_DIM)</code> is a <em>fixed-size</em> list. The "
       "width is part of the type, which is what makes the mismatch detectable at all.")),

    ("def build_index", "Chunk, embed, and check your assumptions",
     p("Three steps with a guard between them. The <code>SystemExit</code> on a missing corpus "
       "gives a person a next action (&ldquo;run fetch_docs first&rdquo;) rather than a "
       "<code>FileNotFoundError</code> traceback.",
       "The dimension check is the interesting one: it compares what the model actually "
       "returned against what the config claims. If you swap models and forget to update "
       "<code>EMBEDDING_DIM</code>, this line tells you exactly that, in one sentence.")),

    ("if rebuild and LANCEDB_DIR.exists()", "Write the table",
     p("<code>shutil.rmtree</code> then <code>mode=\"overwrite\"</code> looks like belt and "
       "braces, and it is. A stale index that <em>partially</em> matches your new chunks is "
       "far more confusing to debug than no index at all &mdash; you get plausible but wrong "
       "results.",
       "Rows are built as plain dictionaries. <code>vectors[i].tolist()</code> converts the "
       "NumPy row into a Python list, which is what Arrow expects.")),

    ("if __name__", "Entry point",
     p("Same guard as every runnable module here, so <code>python -m app.index</code> builds "
       "the index and importing the module does not.")),
]


# --------------------------------------------------------------- retrieve ---

RETRIEVE = [
    ("", "Docstring and imports",
     p("The docstring carries the argument for the whole file: three retrievers, why the "
       "weighting exists, and a pointer to the measurement that produced it. Someone reading "
       "this file cold gets the reasoning before the code.",
       "<code>BM25_K1</code> and <code>BM25_B</code> are the standard tuning constants from the "
       "literature. They live here rather than in <code>config.py</code> because they are "
       "properties of the algorithm, not choices you should be sweeping.")),

    ("class Hit", "One retrieved chunk",
     p("A single type returned by all three retrievers, so callers never have to care which "
       "one produced a result.",
       "<code>@property</code> makes <code>source</code> look like an attribute while being "
       "computed on access. It formats the citation string that ends up in the answer, in one "
       "place, so every part of the system cites identically.")),

    ("def tokenize", "Turn text into terms",
     p("Lowercase word tokens, plus the pieces of any snake_case identifier: "
       "<code>response_model</code> becomes <code>[\"response_model\", \"response\", "
       "\"model\"]</code>.",
       "Without that split, BM25 only fires on an exact identifier match and contributes "
       "almost nothing to normally-phrased questions. With it, a user who asks about "
       "&ldquo;the response model&rdquo; still matches the passage that says "
       "<code>response_model</code>.")),

    ("class Store", "Load once, precompute the statistics",
     p("The constructor does the expensive work: read the table into memory, tokenize every "
       "chunk, and build the BM25 document frequencies and inverse document frequencies.",
       "BM25 needs corpus-wide statistics &mdash; how rare each term is across all documents "
       "&mdash; so they cannot be computed per query. Doing it once at startup is what makes "
       "search instant afterwards.",
       "This is fine at 767 chunks and would not be at a million; there you would push keyword "
       "search into the database, which LanceDB supports with a full-text index. Knowing "
       "<em>when</em> the simple version stops working is more useful than never writing it.")),

    ("def search_vector", "Retriever 1 of 3: nearest neighbours",
     p("You met this in chapter 9. It embeds the question and asks LanceDB for the closest "
       "vectors.",
       "The one line to re-read is <code>1.0 - float(row[\"_distance\"])</code>. LanceDB returns "
       "cosine <em>distance</em> where smaller is closer; everywhere else in this codebase "
       "bigger means better. Converting once, here at the boundary, means no other function "
       "has to remember which convention it is in.")),

    ("def search_keyword", "Retriever 2 of 3: BM25",
     p("Chapter 10's function. For each chunk, sum the contribution of every query term "
       "present, weighted by rarity and damped by document length.",
       "The <code>if score &gt; 0</code> filter matters more than it looks: without it you "
       "would rank all 767 chunks including the ones that matched nothing, and the fusion step "
       "later would be fed pure noise.")),

    ("def search_hybrid", "Retriever 3 of 3: weighted fusion",
     p("Chapter 11's function, and the one with a story. Run both retrievers, then combine "
       "their <em>positions</em> rather than their scores.",
       "The weights are a result, not a preference. With equal weights this scored worse than "
       "vector search alone &mdash; chapter 15 shows the measurement and the single question "
       "that flipped.")),

    ("def _hit", "The small helper that keeps the rest honest",
     p("Both BM25 and the fusion work with row indexes; this converts an index plus a score "
       "into the same <code>Hit</code> type that vector search returns.",
       "Small, boring, and the reason the three retrievers are actually interchangeable rather "
       "than merely similar.")),

    ("@lru_cache", "The public entry point",
     p("<code>get_store()</code> is cached so the BM25 statistics are built once per process "
       "rather than once per request. Without it every question would pay for tokenizing the "
       "whole corpus.",
       "<code>retrieve()</code> is the only function the rest of the project calls. The API and "
       "the evaluation harness both go through it, which is what lets you switch strategy with "
       "a string and compare them fairly.")),
]


# --------------------------------------------------------------- run_eval ---

RUN_EVAL = [
    ("", "Docstring, imports, and the two question sets",
     p("The docstring explains a scoping decision worth defending: this measures "
       "<strong>retrieval only</strong>, not the wording of the final answer.",
       "That is deliberate. Retrieval is where these systems actually fail, and it can be "
       "scored objectively against labelled data. Grading generated prose needs a "
       "model-as-judge and a much longer argument about whether the judge is right.",
       "<code>QUESTION_SETS</code> holds two files. The second exists to test a hypothesis the "
       "first structurally cannot &mdash; chapter 15.")),

    ("def load_questions", "Read a set",
     p("Three lines. The JSON files carry a <code>_comment</code> key alongside "
       "<code>questions</code>, which is the usual way to put explanation in a format that has "
       "no comments &mdash; and it is ignored here simply by reading only the key you want.")),

    ("def evaluate", "Score one strategy",
     p("The core loop: for each question, retrieve, then walk the results looking for the "
       "first hit whose <code>doc_path</code> is in the expected set.",
       "<strong>Hit@k</strong> counts whether that happened at all. <strong>MRR</strong> adds "
       "1/rank, so a correct chunk at position 1 scores 1.0 and at position 4 scores 0.25. You "
       "need both: a system with perfect Hit@4 and poor MRR is one bad day from breaking, "
       "because it depends on chunks the model may skim past.",
       "Collecting <code>misses</code> rather than only counting them is what makes "
       "<code>--verbose</code> useful. A score tells you something is wrong; the miss list "
       "tells you what.")),

    ("def main", "The command line",
     p("<code>argparse</code> gives you <code>--k</code>, <code>--strategy</code>, "
       "<code>--set</code> and <code>--verbose</code> for about fifteen lines.",
       "Being able to say <code>--k 8</code> or <code>--set identifiers</code> without editing "
       "code is what turns this from a script you ran once into a tool you actually use while "
       "tuning.")),

    ("if __name__", "Exit code",
     p("<code>sys.exit(main())</code> rather than a bare call. It costs nothing now and means "
       "the harness can gate a CI job later, once you decide what score counts as a "
       "regression.")),
]


# --------------------------------------------------------------- generate ---

GENERATE = [
    ("", "Docstring and imports",
     p("The docstring contains the single most useful debugging instruction in the project: "
       "if an answer is wrong, print the prompt before touching anything else.",
       "Most of the time you will see immediately that the answer was not in it &mdash; which "
       "makes it a retrieval bug wearing a generation bug's clothes.")),

    ("SYSTEM_PROMPT", "The instructions &mdash; and one real product decision",
     p("Four rules, and each does a specific job. Answer only from the passages. Say so when "
       "they do not contain the answer. Cite inline. Ignore the irrelevant ones, because "
       "retrieval will always return some.",
       "<strong>The second rule is a genuine judgement call and you should make your own.</strong> "
       "Forbidding the model from using its own knowledge of FastAPI is the strict choice: "
       "never wrong, sometimes unhelpful. Letting it answer unsourced while labelling which "
       "parts are unsourced is more useful, but puts a hole in your grounding guarantee.",
       "A legal-documents assistant and a developer-docs assistant should choose differently. "
       "Decide which you are building.")),

    ("@dataclass", "The return type",
     p("Returning a structured <code>Answer</code> rather than a bare string means the caller "
       "gets the sources and the token usage without a second call.",
       "Keeping <code>prompt</code> on it looks redundant until the first time an answer is "
       "wrong. Then it is the first thing you look at.")),

    ("def build_prompt", "Assemble the string",
     p("This is the entire &ldquo;augmented&rdquo; part of Retrieval-Augmented Generation: "
       "numbered passages, then the question. No magic.",
       "Numbering gives the model something concrete to cite. Including each passage's source "
       "path means a citation can be traced back to a file, which is what makes the answer "
       "checkable by a human rather than merely confident.")),

    ("def answer_question", "Retrieve, then generate",
     p("The zero-argument <code>anthropic.Anthropic()</code> resolves credentials from the "
       "environment. Never pass a key as a literal.",
       "<strong>The refusal check is the line reviewers look for.</strong> Claude can decline a "
       "request and returns a normal HTTP&nbsp;200 with an <em>empty</em> content list when it "
       "does. Code that reads <code>response.content[0]</code> unconditionally raises "
       "<code>IndexError</code>, and your API returns a 500 instead of a useful message.",
       "The join over text blocks handles a response arriving in several pieces, which is "
       "normal and easy to get wrong by reading only the first.")),

    ("if __name__", "A command line for one question",
     p("Being able to run <code>python -m app.generate \"...\"</code> without starting a web "
       "server is worth the six lines. It is how you will test this before chapter 17 exists.")),
]


# -------------------------------------------------------------------- api ---

API = [
    ("", "Docstring, imports, and the app",
     p("The docstring states the design decision this file exists to make: "
       "<code>/search</code> runs retrieval with no model call, so you can inspect exactly "
       "what the model was given, for free.",
       "The title and description passed to <code>FastAPI()</code> are not decoration &mdash; "
       "they appear in the generated documentation at <code>/docs</code>.")),

    ("class SearchRequest", "Request and response shapes",
     p("These Pydantic models are the whole reason FastAPI can validate requests, generate "
       "documentation and produce useful error messages without you writing any of it.",
       "<code>Field(..., ge=1, le=20)</code> means a caller asking for 5000 chunks gets a clear "
       "422 rather than exhausting your memory. The <code>pattern</code> on "
       "<code>strategy</code> rejects anything that is not one of the three retrievers, so an "
       "invalid value never reaches your code.",
       "Declaring response models too means the documentation shows what comes back, and "
       "anything your handler returns is checked against it.")),

    ("def _to_out", "One conversion, in one place",
     p("Internal <code>Hit</code> objects become the public <code>SourceOut</code> shape here and "
       "nowhere else.",
       "Keeping the boundary explicit means you can rename an internal field without changing "
       "your API, and the rounding of <code>score</code> happens once rather than in two "
       "endpoints that might drift apart.")),

    ('@app.get("/health")', "Health",
     p("Three lines that answer a real question: is the index loaded, and how big is it? "
       "Calling <code>get_store()</code> also forces the lazy load, so a request to "
       "<code>/health</code> warms the process.",
       "Any service you intend to run should have one of these.")),

    ('@app.post("/search"', "Retrieval, free",
     p("The endpoint that costs nothing. No API key, no tokens, no latency beyond the search "
       "itself.",
       "It is the most useful debugging tool in the project, and it is also what lets someone "
       "clone your repo and explore the retrieval system <em>without</em> a key &mdash; the "
       "difference between a reviewer trying it and closing the tab.")),

    ('@app.post("/ask"', "Retrieval plus generation",
     p("<strong>Note where the import sits.</strong> Importing <code>answer_question</code> at the "
       "top of the file would execute <code>app/generate.py</code> at startup, and constructing "
       "the Anthropic client without a key raises &mdash; taking <code>/health</code> and "
       "<code>/search</code> down with it.",
       "Moving the import inside the function keeps the free endpoints working when no key is "
       "configured, which is the entire point of having them.",
       "Catching the exception and re-raising as a 502 with the exception type in the message "
       "turns an opaque 500 into something a caller can act on.")),

    ('@app.get("/", response_class', "Serve the page",
     p("One line to read the static file and return it as HTML. No template engine, no "
       "asset pipeline.",
       "Reading it per request rather than caching means you can edit the page and refresh "
       "without restarting the server &mdash; which, while you are building the UI, is worth "
       "more than the microseconds it costs.")),
]
