"""Chapter content for the build-along guide.

Prose lives here; code is pulled from the real repository by build_guide.py,
and diagrams come from guide_diagrams.py.
"""

from build_guide import (
    callout,
    code_file,
    code_symbol,
    code_walkthrough,
    heading,
    prose,
    terminal,
    tree_for,
)
import guide_walkthroughs as wt
import guide_diagrams as dia
from guide_diagrams import figure

P0 = "Preface"
P1 = "Part one &middot; Set up"
P2 = "Part two &middot; Build the index"
P3 = "Part three &middot; Make it find things"
P4 = "Part four &middot; Make it answer"
P5 = "Part five &middot; Ship it"

_written: set[str] = set()


def _qa(pairs):
    items = []
    for question, answers in pairs:
        body = "".join(f"<p>{a}</p>" for a in answers)
        items.append(
            f'<details class="qa"><summary>{question}</summary>'
            f'<div class="body">{body}</div></details>'
        )
    return f'<div class="qa-wrap">{"".join(items)}</div>'


def commit(message: str, extra: str = "") -> str:
    """The end-of-chapter commit. One commit per chapter, deliberately."""
    body = extra + "\n" if extra else ""
    return terminal(
        "git &middot; end of chapter",
        f'{body}git add -A\ngit commit -m "{message}"',
    )


def _chapter(cid, part, eyebrow, title, deck, blocks, adds=()):
    ch = {
        "id": cid, "part": part, "eyebrow": eyebrow,
        "title": title, "deck": deck, "body": "\n".join(blocks),
    }
    for path in adds:
        _written.add(path)
    return ch


def build() -> list[dict]:
    C: list[dict] = []

    # ============================================================ PREFACE ===
    C.append(_chapter(
        "ch0", P0, "Preface", "How to use this guide",
        "Type the files. Run the commands. Commit at the end of every chapter.",
        [
            prose(
                "This is a build-along. Every chapter creates or runs exactly one thing, and by the end you "
                "have a working retrieval system on your laptop and a git history that shows how you got "
                "there.",
                "Four rules that decide whether you finish with a repo, or with a repo you can "
                "<strong>talk about</strong>:"),
            prose(
                "<strong>1. Type the code, do not paste it.</strong> Typing is slow, and that is the point &mdash; "
                "it forces you through every line instead of over it.",
                "<strong>2. Run the command at the end of every chapter.</strong> Each one ends with something "
                "you can execute and the output you should see. If yours differs, stop and find out why. A "
                "broken step three chapters back is miserable to debug.",
                "<strong>3. Commit at the end of every chapter.</strong> You get a working state you can always "
                "return to, and a history a reviewer can actually read.",
                "<strong>4. Read the &ldquo;why&rdquo; boxes.</strong> The code is the easy part. The reasoning is "
                "what an interviewer asks about, and what you will need when you point this at your own "
                "documents."),
            heading("What you are building"),
            prose(
                "A question-answering service over the FastAPI documentation. You ask &ldquo;How do I set a "
                "cookie?&rdquo;, it finds the right passages among 154 pages and answers from them, with "
                "citations.",
                "Every RAG system is two systems that run at completely different times and share exactly one "
                "thing. Almost all beginner confusion comes from mixing them up, so start with this picture:"),
            figure(dia.two_phases(),
                   "<b>Phase 1</b> is a batch job: slow, offline, nobody waiting. <b>Phase 2</b> is a lookup "
                   "that must finish before a user gets bored. They meet only at the vector index &mdash; which "
                   "is why the same embedding model has to appear in both.",
                   "Two-phase RAG architecture: indexing runs offline to build a vector index; answering "
                   "embeds the question, searches that index, and sends the top chunks to Claude."),
            heading("The shape of the finished project"),
            tree_for(None, set(), "Twenty-four chapters, roughly one file each."),
            callout("gotcha", "Before you start &mdash; Windows only",
                    "The FastAPI docs contain emoji. Windows terminals default to the <code>cp1252</code> "
                    "character set, which cannot print them, so any script that prints document text dies with "
                    "<code>UnicodeEncodeError</code>. It looks like a bug in your code. It is not.",
                    "Run <code>$env:PYTHONIOENCODING = \"utf-8\"</code> once per PowerShell session."),
        ]))

    # =========================================================== PART ONE ===
    C.append(_chapter(
        "ch1", P1, "Chapter one", "Create the project",
        "A folder, a virtual environment, and five libraries &mdash; with a reason for each.",
        [
            prose(
                "A <strong>virtual environment</strong> is a private copy of Python for one project. Without it "
                "every project on your machine shares one set of libraries, and two projects needing different "
                "versions of the same library break each other. There is no case where skipping it is correct."),
            terminal("PowerShell &middot; create and activate",
                     "mkdir rag-docs-assistant\n"
                     "cd rag-docs-assistant\n\n"
                     "python -m venv .venv\n"
                     ".venv\\Scripts\\activate\n\n"
                     "# Your prompt now starts with (.venv) - that is how you know it worked.\n"
                     "# macOS / Linux instead:  source .venv/bin/activate"),
            heading("Install the five libraries"),
            terminal("PowerShell",
                     'pip install fastapi "uvicorn[standard]" httpx lancedb fastembed anthropic'),
            prose("Know what each one is for before installing it blindly:"),
            '<div class="table-scroll"><table>'
            '<thead><tr><th>Library</th><th>Why this project needs it</th></tr></thead><tbody>'
            '<tr><td><code>httpx</code></td><td>Makes HTTP requests. Used once, in chapter 4, to download the documentation.</td></tr>'
            '<tr><td><code>fastembed</code></td><td>Turns text into vectors locally via ONNX Runtime. No GPU, no API key, no per-query cost.</td></tr>'
            '<tr><td><code>lancedb</code></td><td>The vector database. Embedded like SQLite &mdash; a folder on disk, no server to run.</td></tr>'
            '<tr><td><code>anthropic</code></td><td>The official Claude SDK. Not needed until chapter 16.</td></tr>'
            '<tr><td><code>fastapi</code> + <code>uvicorn</code></td><td>The web layer. FastAPI defines the API; uvicorn is the server that runs it.</td></tr>'
            '</tbody></table></div>',
            heading("Create the folders"),
            terminal("PowerShell",
                     "mkdir app, app\\static, evaluation\n\n"
                     "# Python treats a folder as an importable package when it contains\n"
                     "# __init__.py. Without these two files, `python -m app.config`\n"
                     "# fails with ModuleNotFoundError.\n"
                     "New-Item app\\__init__.py -ItemType File\n"
                     "New-Item evaluation\\__init__.py -ItemType File"),
            callout("note", "Why __init__.py matters here",
                    "Every command in this guide runs as <code>python -m app.something</code> rather than "
                    "<code>python app/something.py</code>. The module form sets imports up correctly, so "
                    "<code>from app.config import ...</code> resolves no matter which directory you are in. That "
                    "only works if <code>app</code> is a real package &mdash; which is exactly what the empty "
                    "<code>__init__.py</code> declares."),
            heading("Check it worked"),
            terminal("PowerShell",
                     'python -c "import fastapi, httpx, lancedb, fastembed, anthropic; print(\'all five imported\')"\n\n'
                     "all five imported"),
        ],
        adds=["app/__init__.py", "evaluation/__init__.py"]))

    done = set(_written)
    C.append(_chapter(
        "ch2", P1, "Chapter two", "Git, before you write anything",
        "The .gitignore comes first, not last. Here is the expensive reason why.",
        [
            prose(
                "Most tutorials put git at the end. That is backwards, and it is how API keys end up in public "
                "repositories.",
                "The moment you run <code>git init</code>, everything you create afterwards is a candidate for "
                "your history. Write the <code>.gitignore</code> <em>before</em> the first commit and the "
                "dangerous files never enter it. Add it afterwards and you are cleaning up a history that may "
                "already have been pushed."),
            heading("Initialise, and exclude first"),
            terminal("PowerShell", "git init"),
            tree_for(".gitignore", done),
            code_file(".gitignore", "write this before your first commit"),
            callout("gotcha", "What each of these lines is actually preventing",
                    "<code>data/</code> keeps 18&nbsp;MB of someone else's documentation and a stale vector index "
                    "out of your history. Vector indexes are binary, change completely on every rebuild, and "
                    "make your repository grow forever.",
                    "<code>.env</code> keeps your API key out of it. A key committed to a public repo is scraped "
                    "within <em>minutes</em> &mdash; bots watch the GitHub event firehose for exactly this. And "
                    "rotating the key is the only real fix: deleting the commit does not help, because the "
                    "history has already been cloned."),
            heading("Tell git who you are"),
            terminal("PowerShell",
                     'git config user.name "Your Name"\n'
                     'git config user.email "you@example.com"\n\n'
                     "# Add --global to either line to set it for every repo on this machine."),
            heading("The first commit"),
            terminal("PowerShell",
                     "git add -A\n"
                     "git status --short          # look before you commit, every time\n\n"
                     "A  .gitignore\n"
                     "A  app/__init__.py\n"
                     "A  evaluation/__init__.py"),
            callout("note", "Read that output before committing",
                    "<code>git status --short</code> is the thirty-second habit that prevents the expensive "
                    "mistake. You are checking for one thing: that nothing appears which should not be there. "
                    "No <code>data/</code>, no <code>.env</code>, no <code>.venv/</code>.",
                    "Do it before <em>every</em> commit, not just this one."),
            commit("chore: project scaffold and gitignore"),
            heading("One commit per chapter, from here on"),
            figure(dia.git_timeline(),
                   "Each chapter ends with one commit. The message says what changed and why, so the history "
                   "reads as the story of the build &mdash; which is something a reviewer will actually look at.",
                   "A timeline of commits, one per chapter, from project scaffold through configuration, "
                   "fetching, chunking, retrieval, evaluation and the README."),
            callout("note", "Why the commit messages have prefixes",
                    "<code>feat:</code> for a new capability, <code>fix:</code> for a repair, <code>chore:</code> for "
                    "scaffolding, <code>docs:</code> for documentation. This is the Conventional Commits "
                    "convention, and it costs nothing to adopt.",
                    "It is not just tidiness &mdash; it makes <code>git log --oneline</code> scannable, and it "
                    "signals to a reviewer that you have worked somewhere with a review process."),
        ],
        adds=[".gitignore"]))

    done = set(_written)
    C.append(_chapter(
        "ch3", P1, "Chapter three", "config.py &mdash; every decision in one place",
        "The file that makes the evaluation harness in chapter 14 actually useful.",
        [
            prose(
                "Start with settings, before any logic. Every tunable number in the project lives here rather "
                "than scattered as literals across eight files.",
                "This is not tidiness for its own sake. In chapter 14 you build a harness that scores retrieval "
                "quality, and it is only useful if changing one number and re-running takes five seconds. That "
                "requires the numbers to be in one findable place."),
            tree_for("app/config.py", done),
            code_walkthrough("app/config.py", wt.CONFIG),
            callout("note", "The three groups that matter",
                    "<strong>Chunking</strong> controls how documents are cut up (chapters 5&ndash;6). "
                    "<strong>Embedding</strong> controls how text becomes numbers (chapter 7). "
                    "<strong>Retrieval</strong> controls how results are ranked (chapters 9&ndash;12). Every "
                    "constant carries a comment explaining not just what it does, but why it holds that value."),
            callout("gotcha", "Read the EMBED_MAX_WORDS comment twice",
                    "It documents a failure that is completely invisible at runtime: the embedding model has a "
                    "512-token limit, and everything past it is silently discarded by the tokenizer. No error, "
                    "no warning. Chapter 7 covers what happened when I hit it.",
                    "It is also why <code>CHUNK_MAX_WORDS</code> is 400 and not 2000 &mdash; your chunk size must "
                    "respect your embedding model's context window."),
            commit("feat: project configuration"),
        ],
        adds=["app/config.py"]))

    # =========================================================== PART TWO ===
    done = set(_written)
    C.append(_chapter(
        "ch4", P2, "Chapter four", "fetch_docs.py &mdash; get the documents",
        "Download the corpus with a script, and never commit it.",
        [
            prose(
                "You need documents to search. We use the FastAPI docs: real, current, technical, and &mdash; "
                "crucially &mdash; something you can personally judge the answers against. When you debug "
                "retrieval you need to know whether an answer is actually right.",
                "<strong>Do not commit the documents into your repo.</strong> They are someone else's content "
                "under their own licence, and a repository carrying 18&nbsp;MB of vendored markdown is "
                "unpleasant to review. That is what chapter 2's <code>.gitignore</code> was for."),
            tree_for("app/fetch_docs.py", done),
            code_walkthrough("app/fetch_docs.py", wt.FETCH),
            callout("note", "Python you just used",
                    "<code>with ... as x:</code> is a <strong>context manager</strong>. It guarantees cleanup &mdash; "
                    "the connection closes, the archive closes &mdash; even if an error is thrown inside the "
                    "block. Any time a library hands you something openable, open it with <code>with</code>."),
            callout("note", "Why the string surgery on member.name",
                    "GitHub's tarball wraps everything in a top-level folder named "
                    "<code>&lt;repo&gt;-&lt;branch&gt;/</code>, so every path arrives as "
                    "<code>fastapi-master/docs/en/docs/tutorial/first-steps.md</code>. We strip that first "
                    "component, then keep only paths under the docs directory. Without the strip you would "
                    "write files into a folder named after whichever branch you downloaded."),
            heading("Run it"),
            terminal("PowerShell",
                     "python -m app.fetch_docs\n\n"
                     "Downloading https://codeload.github.com/fastapi/fastapi/tar.gz/refs/heads/master ...\n"
                     "  17.7 MB downloaded, extracting...\n"
                     "  wrote 155 markdown files to data\\corpus"),
            heading("Check the gitignore is doing its job"),
            terminal("PowerShell",
                     "git status --short\n\n"
                     "?? app/fetch_docs.py\n\n"
                     "# data/ does NOT appear, even though you just wrote 155 files into it.\n"
                     "# That is chapter 2 paying off."),
            callout("gotcha", "If you get 0 files",
                    "The FastAPI repo's default branch or docs path has moved. Open <code>DOCS_TARBALL_URL</code> "
                    "in a browser, look at the archive layout, and fix <code>DOCS_SUBPATH</code> in "
                    "<code>config.py</code> to match. This is the normal failure mode of any script that targets "
                    "someone else's repository layout."),
            commit("feat: download the documentation corpus"),
        ],
        adds=["app/fetch_docs.py"]))

    done = set(_written)
    C.append(_chapter(
        "ch5", P2, "Chapter five", "chunk.py &mdash; three decisions you must defend",
        "Retrieval can only return chunks you created. This is the highest-leverage file in the project.",
        [
            prose(
                "A bad split puts the answer permanently out of reach, and no amount of prompt engineering "
                "recovers it. It is also the first thing a good interviewer asks about.",
                "The naive approach &mdash; slice every 1000 characters &mdash; is the most common reason a first "
                "RAG build retrieves garbage. Three decisions instead."),
            figure(dia.chunking(),
                   "The heading path is carried <b>inside</b> the chunk text, not just stored beside it, so the "
                   "words a user would search for are physically in the thing being embedded. The green band is "
                   "the overlap: the tail of one chunk repeated at the head of the next.",
                   "A markdown document split into two chunks. Each chunk begins with its file path and "
                   "heading trail, and the second chunk repeats the last forty words of the first."),
            heading("Decision 1 &mdash; split on headings, not a character count"),
            prose(
                "A markdown heading is the author explicitly telling you where one idea ends and the next "
                "begins. That is free structural information, and a fixed-width slicer throws it away. We parse "
                "the document into sections and track the <em>heading path</em>, so a level-3 heading inside a "
                "level-1 section becomes <code>Handling Errors &gt; Validation errors</code>."),
            heading("Decision 2 &mdash; put the heading path inside the chunk text"),
            prose(
                "The cheapest big win in all of RAG. A chunk reading <em>&ldquo;It defaults to 422.&rdquo;</em> is "
                "unfindable &mdash; it contains none of the words anyone would search for. Prefixed with its "
                "heading path it is suddenly retrievable."),
            heading("Decision 3 &mdash; overlap consecutive chunks"),
            prose(
                "An answer sitting on a chunk boundary would otherwise be cut in half and match nothing well. "
                "Carrying the last 40 words of each chunk into the next costs a little storage and removes the "
                "failure mode entirely."),
            tree_for("app/chunk.py", done),
            code_walkthrough("app/chunk.py", wt.CHUNK),
            callout("gotcha", "The bug hiding in _sections()",
                    "My first version treated any line starting with <code>#</code> as a heading. In a "
                    "documentation corpus full of <strong>Python code blocks</strong>, every "
                    "<code>#&nbsp;comment</code> inside a code example became a fake section boundary, shredding "
                    "the examples.",
                    "The <code>in_fence</code> flag is the fix. Ninety percent of chunking bugs have this shape: "
                    "markup that means something different inside a code fence."),
            commit("feat: markdown-aware chunker"),
        ],
        adds=["app/chunk.py"]))

    C.append(_chapter(
        "ch6", P2, "Chapter six", "Measure the chunker before you trust it",
        "The step most tutorials skip, and the one that changed this file's design.",
        [
            prose(
                "You have written a chunker. You have not yet established that it produces anything useful. "
                "Look at what it actually made."),
            terminal("PowerShell",
                     'python -c "import statistics; from app.chunk import chunk_corpus; '
                     "from app.config import CORPUS_DIR; c=chunk_corpus(CORPUS_DIR); "
                     "w=[x.n_words for x in c]; print(f'chunks {len(c)}'); "
                     "print(f'median {statistics.median(w)}'); "
                     "print(f'runts  {sum(1 for v in w if v<60)}')\"\n\n"
                     "chunks 767\n"
                     "median 256\n"
                     "runts  21"),
            prose(
                "Those numbers are the entire reason <code>_pack()</code> groups paragraphs <em>across</em> "
                "heading boundaries rather than inside them. My first version split strictly per section, which "
                "sounded tidier:"),
            '<div class="table-scroll"><table>'
            '<thead><tr><th>&nbsp;</th><th class="num">Chunks</th><th class="num">Median words</th><th class="num">Under 20 words</th></tr></thead>'
            '<tbody>'
            '<tr><td>Split per section</td><td class="num">1,971</td><td class="num">72</td><td class="num">78</td></tr>'
            '<tr class="best"><td>Pack across sections</td><td class="num">767</td><td class="num">256</td><td class="num">0</td></tr>'
            '</tbody></table></div>',
            prose(
                "A median of 72 words means most chunks were fragments, and 78 were under 20 words &mdash; too "
                "little signal to ever win a search, and useless to the model if they somehow did. The FastAPI "
                "docs simply have many short subsections.",
                "That change &mdash; found by printing statistics, not by intuition &mdash; more than tripled the "
                "median chunk size. <strong>This is the story to tell in an interview.</strong>"),
            heading("The packing function, close up"),
            code_symbol("app/chunk.py", "_pack", "extracted from the file you just wrote"),
            callout("note", "Python you just used",
                    "<code>[x.n_words for x in c]</code> is a <strong>list comprehension</strong>: build a new list "
                    "by looping over an existing one. <code>sum(1 for v in w if v&lt;60)</code> is the same idea "
                    "without brackets &mdash; a <strong>generator</strong>, producing values one at a time rather "
                    "than building the whole list in memory."),
            callout("task", "Try it yourself",
                    "Change <code>CHUNK_TARGET_WORDS</code> in <code>config.py</code> to 80, re-run the command "
                    "above, and watch the median collapse. Then set it to 600 and watch the chunk count fall. "
                    "Put it back to 220 when you are done.",
                    "You have just done your first parameter sweep. In chapter 14 you will be able to score "
                    "whether such a change actually helped, rather than only observing that it changed "
                    "something."),
            commit("chore: verify chunk size distribution"),
        ]))

    done = set(_written)
    C.append(_chapter(
        "ch7", P2, "Chapter seven", "embed.py &mdash; text becomes coordinates",
        "Two functions, one silent trap, and the reason this file is isolated from everything else.",
        [
            prose(
                "An <strong>embedding model</strong> reads text and outputs a list of numbers &mdash; here, 384 of "
                "them. Texts that mean similar things get similar lists. That is the whole trick: searching "
                "becomes &ldquo;which lists are closest to this list?&rdquo;, a geometry problem a computer solves "
                "in milliseconds."),
            figure(dia.embedding_space(),
                   "The map really has 384 dimensions; two is the only lie in the picture, and it changes "
                   "nothing about how it works. <b>Ask &ldquo;can I send this back?&rdquo;</b> and you land next to a "
                   "passage titled &ldquo;Returns &amp; refunds&rdquo; despite sharing no words with it &mdash; which "
                   "a keyword search would miss entirely.",
                   "A scatter plot where each dot is a chunk. Dots cluster by topic; the question lands inside "
                   "the returns cluster and the three nearest chunks are highlighted."),
            prose(
                "Keep this in its own file. It is the component you are most likely to swap, and everything "
                "else should talk to two functions without caring what is behind them."),
            callout("note", "Anthropic does not sell embeddings",
                    "Claude is the generation half only. The embedding model here runs locally through ONNX "
                    "Runtime &mdash; no PyTorch, no GPU, no API key, no cost per query. If you later want a hosted "
                    "embedding model, Anthropic points at Voyage AI, and swapping is roughly ten lines in this "
                    "one file."),
            tree_for("app/embed.py", done),
            code_walkthrough("app/embed.py", wt.EMBED),
            callout("note", "Python you just used",
                    "<code>@lru_cache(maxsize=1)</code> is a <strong>decorator</strong> &mdash; a function wrapping "
                    "another function to change its behaviour. This one caches the result, so the model loads "
                    "once and every later call returns the same object instantly. It does the job of a singleton "
                    "in three characters."),
            callout("gotcha", "The bug that cost me an hour, and it is invisible",
                    "My first index build climbed to <strong>10&nbsp;GB of RAM</strong> and never finished. The "
                    "cause was a chunk of 1,512 words being fed to a model with a <strong>512-token "
                    "context</strong>. Everything past that limit is silently dropped by the tokenizer &mdash; no "
                    "error, no warning, just a vector that ignores most of your chunk.",
                    "<code>_truncate()</code> plus batching is the fix. Memory dropped from 10&nbsp;GB to "
                    "2.6&nbsp;GB. Note that only the <em>embedding</em> is truncated &mdash; the full chunk text is "
                    "still stored and still handed to Claude, so nothing is lost from the answer, only from the "
                    "search key."),
            callout("gotcha", "The prefix on embed_query is not decoration",
                    "bge models are trained asymmetrically: passages are embedded bare, queries get an "
                    "instruction prefix. Skip it and everything still &ldquo;works&rdquo; &mdash; you get vectors, "
                    "nothing errors &mdash; you just quietly lose retrieval accuracy. Silent quality bugs like "
                    "this are exactly why chapter 14 exists."),
            commit("feat: local embeddings via fastembed"),
        ],
        adds=["app/embed.py"]))

    done = set(_written)
    C.append(_chapter(
        "ch8", P2, "Chapter eight", "index.py &mdash; build the vector store",
        "The slow, offline half. Run it once and forget it until the documents change.",
        [
            prose(
                "LanceDB is embedded, like SQLite: a folder on disk, no server, no Docker. For a portfolio "
                "project that matters more than it sounds, because anyone who clones your repo can run it in "
                "two minutes."),
            tree_for("app/index.py", done),
            code_walkthrough("app/index.py", wt.INDEX),
            callout("note", "Why the schema is declared by hand",
                    "You could let LanceDB infer a schema from the first row. Don't. Inference guesses the "
                    "vector width from whatever it sees first, which turns a future embedding-model swap into a "
                    "baffling runtime error rather than the clear one raised by the <code>EMBEDDING_DIM</code> "
                    "check a few lines below."),
            heading("Run it &mdash; and be patient"),
            terminal("PowerShell",
                     "python -m app.index\n\n"
                     "Chunking corpus...\n"
                     "  767 chunks from 154 documents\n"
                     "Embedding 767 chunks (first run downloads the model)...\n"
                     "  embedded 767/767\n"
                     "  vectors: (767, 384)\n"
                     "Indexed 767 chunks into data\\lancedb in 655.0s"),
            callout("gotcha", "Eleven minutes is normal",
                    "Embedding 767 chunks on a laptop CPU took <strong>eleven minutes</strong> on my machine, and "
                    "the first run also downloads about 130&nbsp;MB of model. It is a one-time cost that only "
                    "repeats when the documents change &mdash; but the first time, do not assume it has hung. The "
                    "progress counter is there so you can tell the difference."),
            commit("feat: build the LanceDB vector index"),
        ],
        adds=["app/index.py"]))

    # ========================================================= PART THREE ===
    C.append(_chapter(
        "ch9", P3, "Chapter nine", "Vector search &mdash; nearest neighbours",
        "The first of three retrievers. Build them one at a time so you can tell them apart.",
        [
            prose(
                "<code>retrieve.py</code> ends up holding three ways to search. We build it across four chapters "
                "rather than dropping 227 lines on you at once, because the interesting part is <em>why there "
                "are three</em>.",
                "Start with the store: load the table once, hold it in memory, and find nearest neighbours by "
                "cosine similarity."),
            code_symbol("app/retrieve.py", "search_vector", "the vector retriever"),
            callout("note", "Why flip the distance into a score",
                    "LanceDB returns cosine <em>distance</em>, where smaller means closer. Everywhere else in "
                    "this codebase bigger means better. Converting once, here at the boundary, means no other "
                    "function has to remember which convention it is in &mdash; and mixed conventions are a "
                    "classic source of silently inverted rankings."),
            callout("note", "Why metric(\"cosine\") is explicit",
                    "LanceDB's default is L2 (straight-line) distance. For normalised embeddings cosine and L2 "
                    "rank identically, so leaving the default would appear to work &mdash; right up until you "
                    "swap in a model that does not normalise, and your results quietly degrade. State the metric "
                    "you mean."),
        ]))

    C.append(_chapter(
        "ch10", P3, "Chapter ten", "BM25 &mdash; the keyword retriever",
        "Twenty-five year old information retrieval, and it still earns its place.",
        [
            prose(
                "Vector search is blurry on rare literal tokens. Ask about <code>response_model</code> and the "
                "embedding smears it toward every neighbouring concept. BM25 is the opposite: exact on "
                "identifiers, helpless when the user's words do not appear in the text at all.",
                "BM25 scores a document by how often the query's terms appear in it, weighted by how rare each "
                "term is across the whole corpus, and damped so a long document cannot win just by being long."),
            code_symbol("app/retrieve.py", "search_keyword", "the keyword retriever"),
            heading("The tokenizer matters more than the formula"),
            code_symbol("app/retrieve.py", "tokenize", "how text becomes terms"),
            callout("note", "Why snake_case is split",
                    "<code>response_model</code> becomes <code>[\"response_model\", \"response\", \"model\"]</code>, so "
                    "a question phrased either way matches the same passage. Without this, BM25 only fires on an "
                    "exact identifier match and contributes almost nothing to ordinary questions."),
            callout("note", "Why plain Python is fine here",
                    "Scoring 767 chunks in a Python loop is instantaneous. At a million chunks it would not be, "
                    "and you would push keyword search into the database &mdash; LanceDB has a full-text index for "
                    "exactly this. Knowing <em>when</em> the simple thing stops working is more useful than never "
                    "writing it."),
        ]))

    C.append(_chapter(
        "ch11", P3, "Chapter eleven", "Fusing the two with RRF",
        "How to combine two rankings whose scores are not comparable.",
        [
            prose(
                "You now have two ranked lists that disagree. Combining them sounds like it should be a "
                "weighted sum of their scores &mdash; and that is the trap."),
            figure(dia.rrf(),
                   "Cosine similarity runs 0&ndash;1; BM25 is unbounded and depends on your corpus. "
                   "<b>Reciprocal Rank Fusion throws the scores away and uses only the positions</b>, which makes "
                   "the two systems comparable by construction. This is a very common interview question.",
                   "Two ranked lists of four documents each, fused into a single ranking by summing "
                   "reciprocal-rank votes, with the vector list weighted three times the keyword list."),
            code_symbol("app/retrieve.py", "search_hybrid", "the fusion"),
            callout("gotcha", "The weights are a result, not a guess",
                    "With textbook <em>equal</em> weights this scored worse than vector search alone. Chapter 15 "
                    "shows the measurement and the single question that flipped. Leave the 3:1 as it is until "
                    "you have run the evaluation yourself and can explain it."),
            callout("note", "Why 60?",
                    "The constant in <code>1/(60 + rank)</code> flattens the curve so the top result does not "
                    "dominate completely. 60 is the value from the original 2009 paper and has been the default "
                    "ever since &mdash; it works across a wide range of corpora, which is exactly what you want "
                    "from a constant you are not going to tune."),
        ]))

    done = set(_written)
    C.append(_chapter(
        "ch12", P3, "Chapter twelve", "retrieve.py &mdash; the finished file",
        "The three retrievers, assembled, with the plumbing that holds them together.",
        [
            prose(
                "Here is everything from the last three chapters in one file, plus the <code>Store</code> class "
                "that loads the table and precomputes BM25 statistics once per process."),
            tree_for("app/retrieve.py", done),
            code_walkthrough("app/retrieve.py", wt.RETRIEVE),
            callout("note", "Why get_store() is cached",
                    "Building the BM25 statistics means tokenizing all 767 chunks. Doing that per request would "
                    "add a needless delay to every question. <code>@lru_cache</code> makes it happen once per "
                    "process, on the first call."),
            heading("Try all three by hand"),
            terminal("PowerShell",
                     "python -m evaluation.run_eval --strategy vector --set main\n\n"
                     "main: 22 questions at k=4\n"
                     "strategy      Hit@k    MRR@k        hits\n"
                     "------------------------------------------\n"
                     "vector      100.0%    0.943     22/22"),
            prose(
                "Three retrievers, and no way yet to say which is <em>right</em> in general. That is the next "
                "part of the guide."),
            commit("feat: vector, BM25 and hybrid retrieval"),
        ],
        adds=["app/retrieve.py"]))

    done = set(_written)
    C.append(_chapter(
        "ch13", P3, "Chapter thirteen", "questions.json &mdash; write the test set",
        "Labelled by reading the docs &mdash; not by running your own retriever.",
        [
            prose(
                "Before you can improve retrieval you need to score it. That means questions a real user would "
                "ask, each paired with the page that genuinely answers it.",
                "<strong>Write the labels by reading the documentation.</strong> If you instead run your "
                "retriever and record what it returned, the test set only ever confirms what the system already "
                "does &mdash; it can never tell you the system is wrong."),
            tree_for("evaluation/questions.json", done),
            code_file("evaluation/questions.json", "the whole file"),
            callout("note", "Look at how the questions are phrased",
                    "&ldquo;How do I run something after returning a response?&rdquo; does not contain the words "
                    "&ldquo;background task&rdquo;. &ldquo;How do I allow requests from a different origin?&rdquo; does "
                    "not say &ldquo;CORS&rdquo;. That is deliberate: questions phrased in the documentation's own "
                    "vocabulary test nothing, because real users do not know the vocabulary yet &mdash; which is "
                    "precisely why they are asking."),
            callout("note", "Why some questions list two acceptable pages",
                    "A question with two correct sources is not a weaker test, it is an honest one. Forcing a "
                    "single right answer where the documentation genuinely covers a topic twice would just be "
                    "scoring your own labelling, not the retriever."),
            heading("The second question set"),
            prose(
                "One more file, for a reason that becomes clear in chapter 15: the main set is almost entirely "
                "paraphrased questions, which is vector search's home turf. It structurally cannot show whether "
                "keyword search contributes anything."),
            code_file("evaluation/questions_identifiers.json", "the whole file"),
            commit("feat: labelled retrieval evaluation sets"),
        ],
        adds=["evaluation/questions.json", "evaluation/questions_identifiers.json"]))

    done = set(_written)
    C.append(_chapter(
        "ch14", P3, "Chapter fourteen", "run_eval.py &mdash; the scoring harness",
        "Two metrics, and why you need both.",
        [
            prose(
                "Almost every RAG demo on GitHub stops at &ldquo;it returns plausible answers.&rdquo; Yours is "
                "about to have a number."),
            tree_for("evaluation/run_eval.py", done),
            code_walkthrough("evaluation/run_eval.py", wt.RUN_EVAL),
            callout("note", "Hit@k and MRR@k",
                    "<strong>Hit@k</strong> asks whether a correct page appeared in the top k chunks at all &mdash; "
                    "the blunt question of whether the model <em>could</em> have answered. <strong>MRR@k</strong> "
                    "asks where it landed: the average of 1/(rank of the first correct chunk).",
                    "You need both. A system with a perfect Hit@4 and a poor MRR is one bad day from breaking, "
                    "because it depends on chunks sitting at position four that the model may skim past."),
            heading("Run it"),
            terminal("PowerShell",
                     "python -m evaluation.run_eval\n\n"
                     "main: 22 questions at k=4\n"
                     "strategy      Hit@k    MRR@k        hits\n"
                     "------------------------------------------\n"
                     "vector      100.0%    0.943     22/22\n"
                     "keyword      90.9%    0.663     20/22\n"
                     "hybrid      100.0%    0.943     22/22\n\n"
                     "identifiers: 8 questions at k=4\n"
                     "strategy      Hit@k    MRR@k        hits\n"
                     "------------------------------------------\n"
                     "vector      100.0%    0.812      8/8\n"
                     "keyword      87.5%    0.562      7/8\n"
                     "hybrid      100.0%    0.875      8/8"),
            commit("feat: retrieval evaluation harness"),
        ],
        adds=["evaluation/run_eval.py"]))

    C.append(_chapter(
        "ch15", P3, "Chapter fifteen", "The measurement that changed the design",
        "My favourite idea lost. This is the most valuable chapter in the guide.",
        [
            prose(
                "I built hybrid retrieval expecting it to beat both single retrievers. With textbook "
                "<strong>equal-weight</strong> RRF it scored 95.5% / 0.864 &mdash; <em>worse</em> than plain vector "
                "search at 100% / 0.943.",
                "Every article says hybrid wins. My measurement said it lost. This is the moment the evaluation "
                "harness paid for itself."),
            heading("Find out why, do not guess"),
            terminal("PowerShell",
                     "python -m evaluation.run_eval --verbose\n\n"
                     "Misses for hybrid on main:\n"
                     "  Q: How do I serve static files like CSS and images?\n"
                     "     expected one of: tutorial/static-files.md\n"
                     "     retrieved:       reference/staticfiles.md, how-to/custom-docs-ui-assets.md, ..."),
            prose(
                "Exactly one question had flipped. BM25 saw the literal string <code>StaticFiles</code> in the "
                "API <em>reference</em> page and ranked it first; vector search had correctly preferred the "
                "<em>tutorial</em> page. Equal weights let the weaker retriever overrule the stronger one."),
            heading("The fix, and what it does not prove"),
            prose(
                "Weighting the fusion 3:1 toward vector restored the score to 100% / 0.943. But look carefully "
                "at what that establishes: only that hybrid does no <strong>harm</strong>.",
                "To justify the extra code it has to do some <strong>good</strong> &mdash; and the main question set "
                "structurally could not show that, because 22 paraphrased questions is vector search's home "
                "turf. That is why the identifiers set exists, and there hybrid wins 0.875 to 0.812.",
                "That is a defensible reason to ship hybrid retrieval, and a far better interview answer than "
                "&ldquo;I used hybrid search because it is best practice.&rdquo;"),
            '<div class="table-scroll"><table>'
            '<thead><tr><th>Strategy</th><th class="num">main &middot; MRR@4</th><th class="num">identifiers &middot; MRR@4</th></tr></thead>'
            '<tbody>'
            '<tr><td>vector</td><td class="num">0.943</td><td class="num">0.812</td></tr>'
            '<tr><td>keyword (BM25)</td><td class="num">0.663</td><td class="num">0.562</td></tr>'
            '<tr class="best"><td>hybrid, weighted 3:1</td><td class="num">0.943</td><td class="num">0.875</td></tr>'
            '</tbody></table></div>',
            callout("gotcha", "Resist the urge to over-tune",
                    "The best weight on my eval set was 4:1, scoring 0.955. I shipped 3:1 anyway. The gain was "
                    "0.012 MRR &mdash; <strong>one question moving one position</strong> &mdash; picked by looking at "
                    "the answers, on 22 questions, with no held-out set. That is fitting the test rather than "
                    "the problem.",
                    "An interviewer who asks &ldquo;how do you know that is not noise?&rdquo; will find out in one "
                    "question whether you thought about it."),
            callout("task", "Reproduce it yourself",
                    "Set <code>RRF_WEIGHT_VECTOR = 1.0</code> in <code>config.py</code>, re-run "
                    "<code>python -m evaluation.run_eval --verbose</code>, and watch hybrid drop below vector. "
                    "Put it back to 3.0.",
                    "You have now personally seen a best practice fail on your own data. That experience is the "
                    "thing this whole project exists to give you."),
            commit("docs: record the hybrid retrieval measurement"),
        ]))

    # ========================================================== PART FOUR ===
    done = set(_written)
    C.append(_chapter(
        "ch16", P4, "Chapter sixteen", "generate.py &mdash; assemble the prompt, call Claude",
        "Everything in the previous fifteen chapters exists to make one string good.",
        [
            prose(
                "The whole generation step is: paste the retrieved passages above the question, add "
                "instructions, send. If an answer is ever wrong, print this string before you touch anything "
                "else &mdash; most of the time you will see immediately that the answer simply was not in it."),
            heading("Get an API key first"),
            prose(
                "Create one at <code>console.anthropic.com</code>, then put it in your environment. This is the "
                "first chapter that needs it &mdash; everything so far runs for free."),
            terminal("PowerShell",
                     '$env:ANTHROPIC_API_KEY = "sk-ant-..."\n\n'
                     "# Set it permanently for your user account instead:\n"
                     '# [Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-...", "User")'),
            callout("gotcha", "Never put the key in a file you commit",
                    "Not in <code>config.py</code>, not in a notebook, not &ldquo;temporarily&rdquo;. Environment "
                    "variable or <code>.env</code> only &mdash; and <code>.env</code> is already ignored by the "
                    "<code>.gitignore</code> you wrote in chapter 2."),
            tree_for("app/generate.py", done),
            code_walkthrough("app/generate.py", wt.GENERATE),
            callout("note", "Why effort is set to low",
                    "Effort controls how much the model thinks before answering. Reading four short passages "
                    "and quoting the relevant one is not a hard reasoning problem &mdash; the answer is sitting in "
                    "the text. Low effort gives the same answer for less latency and cost. Raise it when you "
                    "start asking questions that need synthesis across many sources.",
                    "Knowing <em>when not to spend</em> is a senior instinct, and worth being able to explain."),
            callout("gotcha", "Why the refusal check exists",
                    "Claude can decline a request outright, and when it does it returns a normal HTTP&nbsp;200 "
                    "with an <em>empty</em> content list. Code that reads <code>response.content[0]</code> "
                    "unconditionally raises <code>IndexError</code>, and your API returns a 500 instead of a "
                    "useful message."),
            heading("Run it"),
            terminal("PowerShell",
                     'python -m app.generate "How do I declare an optional query parameter?"\n\n'
                     "To declare an optional query parameter, give it a default value of None...\n\n"
                     "Sources:\n"
                     "  [1] tutorial/query-params.md > Query Parameters > Optional parameters\n"
                     "  [2] tutorial/query-params-str-validations.md > ...\n\n"
                     "Tokens: {'input_tokens': 1834, 'output_tokens': 191}"),
            callout("task", "Your turn &mdash; this one is a real decision",
                    "Look at <code>SYSTEM_PROMPT</code>. One rule in it is a genuine product judgement, and I made "
                    "it one way: <em>&ldquo;If the passages do not contain the answer, say so plainly and stop. Do "
                    "not fall back on your own knowledge of FastAPI.&rdquo;</em>",
                    "That is the <strong>strict</strong> choice: never wrong, sometimes unhelpful. The alternative "
                    "is to let it answer from general knowledge while labelling which parts are unsourced &mdash; "
                    "more useful, but your &ldquo;grounded&rdquo; guarantee now has a hole in it.",
                    "Rewrite those two sentences to encode <em>your</em> call, and be ready to say why. A legal "
                    "assistant and a developer-docs assistant should choose differently."),
            commit("feat: grounded answer generation with Claude"),
        ],
        adds=["app/generate.py"]))

    done = set(_written)
    C.append(_chapter(
        "ch17", P4, "Chapter seventeen", "api.py &mdash; three endpoints, one of them free",
        "The debugging affordance that costs nothing and saves hours.",
        [
            prose(
                "The design decision worth defending here is <code>/search</code>: retrieval with <strong>no "
                "model call</strong>. No API key, no cost, no latency."),
            figure(dia.api_flow(),
                   "Splitting retrieval onto its own endpoint means you can inspect exactly what the model was "
                   "given, for free, without running generation. It also means anyone can clone your repo and "
                   "explore the retrieval system <b>without an API key</b> &mdash; which for a portfolio piece is "
                   "the difference between a reviewer trying it and closing the tab.",
                   "A request flows from the browser into FastAPI, then splits: /search returns retrieved "
                   "passages for free, while /ask additionally calls Claude and costs tokens."),
            tree_for("app/api.py", done),
            code_walkthrough("app/api.py", wt.API),
            callout("note", "Why answer_question is imported inside the function",
                    "Importing it at the top of the file would execute <code>app/generate.py</code> at startup, "
                    "and constructing the Anthropic client without a key raises. Moving the import inside "
                    "<code>ask()</code> keeps <code>/health</code> and <code>/search</code> working when no key is "
                    "configured &mdash; which is the whole point of having a free endpoint."),
            callout("note", "What FastAPI gives you for free here",
                    "It reads the type hints on <code>SearchRequest</code> and generates request validation, error "
                    "messages, and interactive documentation at <code>/docs</code>. The "
                    "<code>Field(..., ge=1, le=20)</code> constraint means a caller asking for 5000 chunks gets a "
                    "clear 422 rather than exhausting your memory."),
            heading("Run the server"),
            terminal("PowerShell",
                     "uvicorn app.api:app --reload\n\n"
                     "INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)"),
            heading("Test retrieval without spending anything"),
            terminal("PowerShell &middot; second terminal",
                     "curl -s -X POST http://127.0.0.1:8000/search `\n"
                     '  -H "content-type: application/json" `\n'
                     '  -d \'{\"question\":\"How do I set a cookie on the response?\"}\'\n\n'
                     "advanced/response-cookies.md > Response Cookies > Return a `Response` directly\n"
                     "reference/responses.md > Custom Response Classes ...\n"
                     "tutorial/cookie-param-models.md > Cookie Parameter Models ...\n"
                     "advanced/response-change-status-code.md > Response - Change Status Code"),
            callout("gotcha", "The debugging habit to build now",
                    "When an answer is wrong, <strong>always check retrieval first</strong>. Hit "
                    "<code>/search</code> with the same question. If the right page is not in the results, the "
                    "problem is upstream and no prompt change will fix it. Then compare "
                    "<code>\"strategy\": \"vector\"</code> against <code>\"keyword\"</code> to see which half failed.",
                    "Most people spend hours rewriting prompts to fix what is actually a retrieval bug."),
            commit("feat: FastAPI service with a key-free search endpoint"),
        ],
        adds=["app/api.py"]))

    done = set(_written)
    C.append(_chapter(
        "ch18", P4, "Chapter eighteen", "index.html &mdash; something to screenshot",
        "One self-contained page, because a project people can see beats one they must imagine.",
        [
            prose(
                "No build step, no framework, no npm. One HTML file that FastAPI serves at <code>/</code>, which "
                "keeps the whole project to a single <code>pip install</code> and makes the screenshot for your "
                "README about ninety seconds of work.",
                "Note the two buttons: <strong>Ask</strong> calls <code>/ask</code> and costs tokens, "
                "<strong>Search only</strong> calls <code>/search</code> and costs nothing. Exposing that "
                "distinction in the interface is the previous chapter's philosophy made visible."),
            tree_for("app/static/index.html", done),
            code_file("app/static/index.html", "the whole file"),
            callout("gotcha", "The one security detail in this file",
                    "<code>esc()</code> escapes <code>&amp;</code>, <code>&lt;</code> and <code>&gt;</code> before any "
                    "retrieved text reaches <code>innerHTML</code>. Your corpus is documentation full of HTML "
                    "examples; without escaping, a passage containing a <code>&lt;script&gt;</code> tag would "
                    "execute in your page. Worth the habit even when you control the corpus."),
            heading("Look at it, then screenshot it"),
            terminal("PowerShell",
                     "uvicorn app.api:app --reload\n"
                     "# open http://127.0.0.1:8000 - ask something, then screenshot it\n"
                     "# for the README in chapter 20."),
            commit("feat: minimal browser UI"),
        ],
        adds=["app/static/index.html"]))

    # ========================================================== PART FIVE ===
    done = set(_written)
    C.append(_chapter(
        "ch19", P5, "Chapter nineteen", "The two files that make it installable",
        "requirements.txt and .env.example &mdash; small files, large consequences.",
        [
            prose(
                "You already wrote <code>.gitignore</code> in chapter 2. Two short files remain between a folder "
                "on your laptop and something another engineer can clone and run."),
            tree_for("requirements.txt", done),
            code_file("requirements.txt"),
            callout("note", "Why the versions are ranges, not pins",
                    "<code>&gt;=0.115,&lt;1.0</code> says &ldquo;any 0.x from 0.115&rdquo;, which lets security patches "
                    "through while blocking the 1.0 release that might break the API. Pinning exactly "
                    "(<code>==0.115.2</code>) is right for a deployed service where reproducibility beats "
                    "freshness; ranges are right for a portfolio project someone will clone in six months."),
            tree_for(".env.example", done),
            code_file(".env.example"),
            callout("note", "Why commit an example but not the real thing",
                    "<code>.env.example</code> documents which variables exist without revealing any values. "
                    "Someone cloning your repo copies it to <code>.env</code>, fills in their own key, and "
                    "<code>.gitignore</code> keeps that copy out of git. It is the standard pattern and reviewers "
                    "look for it."),
            heading("Prove the quickstart actually works"),
            terminal("PowerShell",
                     "# The only honest test of your own instructions:\n"
                     "Remove-Item -Recurse -Force data\n"
                     "python -m app.fetch_docs\n"
                     "python -m app.index\n"
                     "python -m evaluation.run_eval"),
            commit("chore: requirements and env example"),
        ],
        adds=["requirements.txt", ".env.example"]))

    done = set(_written)
    C.append(_chapter(
        "ch20", P5, "Chapter twenty", "README.md &mdash; the file that gets read",
        "Most people who open your repo read one file. Budget your effort accordingly.",
        [
            prose(
                "A mediocre project with an excellent README outperforms the reverse, every time. Four things "
                "yours must do, in this order:"),
            '<div class="col"><ol class="steps">'
            '<li><strong>Say what it is in one sentence</strong>, before any setup instructions.</li>'
            '<li><strong>Show the evaluation table near the top.</strong> It is your differentiator &mdash; do not bury it under installation steps.</li>'
            '<li><strong>Give a quickstart that works from a clean clone</strong> &mdash; the one you just tested in chapter 19.</li>'
            '<li><strong>Include a &ldquo;What I&rsquo;d do next&rdquo; section.</strong> Naming your own project&rsquo;s limits reads as senior, not weak. Reviewers who spot a gap you already listed think &ldquo;they know&rdquo;; reviewers who spot one you missed think something else.</li>'
            '</ol></div>',
            tree_for("README.md", done),
            callout("note", "Put the honest result in it",
                    "The strongest paragraph in this project's README is the one admitting that hybrid search "
                    "made things worse at first, and explaining what I did about it. Anyone can write &ldquo;uses "
                    "hybrid retrieval&rdquo;. Almost nobody can show the measurement that nearly killed it."),
            callout("note", "Embed the screenshot",
                    "Put the image from chapter 18 in <code>docs/screenshot.png</code> and reference it near the "
                    "top with <code>![alt text](docs/screenshot.png)</code>. A reviewer decides whether to keep "
                    "reading in about four seconds, and a picture of a working thing buys you those seconds."),
            commit("docs: README with evaluation results"),
        ],
        adds=["README.md"]))

    C.append(_chapter(
        "ch21", P5, "Chapter twenty-one", "Push it to GitHub",
        "Remotes, branches, and the check you run before every push.",
        [
            heading("The check, one more time"),
            terminal("PowerShell",
                     "git status --short          # nothing unexpected\n"
                     "git log --oneline           # a readable history\n\n"
                     "a1b2c3d docs: README with evaluation results\n"
                     "e4f5g6h chore: requirements and env example\n"
                     "i7j8k9l feat: minimal browser UI\n"
                     "..."),
            callout("gotcha", "Check what is tracked, not just what is staged",
                    "<code>git status</code> shows uncommitted changes. To see what is <em>in</em> the repository "
                    "&mdash; which is what gets pushed &mdash; list the tracked files instead:",
                    "<code>git ls-files | Select-String \"^(data/|\\.env$)\"</code> should print <strong>nothing at "
                    "all</strong>. If it prints anything, stop and fix it before pushing."),
            heading("Create the remote and push"),
            terminal("PowerShell &middot; with the GitHub CLI",
                     "gh repo create rag-docs-assistant --public --source=. --push\n\n"
                     "# Without gh, create the repo in the browser first, then:\n"
                     "# git remote add origin https://github.com/YOU/rag-docs-assistant.git\n"
                     "# git branch -M main\n"
                     "# git push -u origin main"),
            callout("note", "What -u does",
                    "<code>git push -u origin main</code> sets the <em>upstream</em>: it tells your local "
                    "<code>main</code> which remote branch it tracks. After that first push, plain "
                    "<code>git push</code> and <code>git pull</code> know where to go."),
            heading("Working on it afterwards"),
            prose(
                "Once it is public, stop committing straight to <code>main</code>. Branch, push the branch, open "
                "a pull request &mdash; even working alone. It costs one extra command and it means your repo "
                "demonstrates the workflow every team uses."),
            terminal("PowerShell &middot; the loop you will use from now on",
                     "git checkout -b feat/add-reranker\n\n"
                     "# ... make changes, run the evaluation ...\n\n"
                     "git add -A\n"
                     'git commit -m "feat: cross-encoder reranker"\n'
                     "git push -u origin feat/add-reranker\n\n"
                     "gh pr create --fill"),
            callout("task", "Put the numbers in the pull request",
                    "When you open that PR, paste the before-and-after evaluation table into the description. "
                    "That is what a good engineer's PR looks like, and it is a habit worth forming on a project "
                    "where nobody is watching yet."),
        ]))

    C.append(_chapter(
        "ch22", P5, "Chapter twenty-two", "Write about it",
        "Lead with the finding, not the stack.",
        [
            prose(
                "&ldquo;I built a RAG app with FastAPI and Claude&rdquo; is a sentence thousands of people posted "
                "this year, and it invites no questions. &ldquo;My hybrid search made retrieval worse, and here is "
                "what I found&rdquo; invites a conversation.",
                "You have something most posts do not: a measurement that contradicted the received wisdom, and "
                "a reasoned response to it. Lead with that."),
            heading("The shape of a post worth reading"),
            '<div class="col"><ol class="steps">'
            '<li><strong>The surprising result, in the first two lines.</strong> Before any context. That is all most people will read.</li>'
            '<li><strong>The cause,</strong> concretely &mdash; the one question that flipped, and why BM25 won it.</li>'
            '<li><strong>What you did about it,</strong> including the part where the fix only proved the idea did no harm.</li>'
            '<li><strong>The general lesson,</strong> in one sentence: write the evaluation before you tune anything.</li>'
            '<li><strong>The stack,</strong> last and briefly. It is the least interesting thing about the project.</li>'
            '</ol></div>',
            callout("note", "Three practical details",
                    "Put the repo link in the <strong>first comment</strong>, not the post body &mdash; LinkedIn "
                    "suppresses reach on posts with external links. <strong>Attach the screenshot</strong> from "
                    "chapter 18. And do not claim it is production-ready: &ldquo;a small system I built to "
                    "understand retrieval properly&rdquo; is both true and more credible."),
            callout("gotcha", "Expect this comment",
                    "Someone will ask &ldquo;why not just use LangChain?&rdquo; A good answer: the whole point was to "
                    "understand each step, and every abstraction between me and the retrieval would have hidden "
                    "exactly the bugs I found. You can add the framework once you know what it is doing for you."),
        ]))

    C.append(_chapter(
        "ch23", P5, "Chapter twenty-three", "The viva",
        "Nine questions you will actually be asked, and what a good answer sounds like.",
        [
            prose(
                "Work through these out loud, without notes. Any answer that feels shaky is the one you will be "
                "asked &mdash; go back to that chapter."),
            _qa([
                ("Why did you chunk it that way?",
                 ["Split on markdown headings, because a heading is the author marking where an idea ends "
                  "&mdash; free structure a fixed-width slicer throws away. Prepend the heading path so the "
                  "searchable words are physically inside the embedded text. Overlap by 40 words so an answer on "
                  "a boundary is not cut in half.",
                  "<strong>Then the strong part:</strong> I measured it. Splitting strictly per-section gave a "
                  "median chunk of 72 words with 78 unusable fragments. Packing across headings moved the median "
                  "to 256 and eliminated them."]),
                ("How do you know your retrieval is any good?",
                 ["30 hand-labelled questions across two sets, scored on Hit@4 and MRR@4. Labels written by "
                  "reading the docs, not by recording what the retriever returned &mdash; otherwise the test only "
                  "confirms what the system already does.",
                  "100% Hit@4 and 0.943 MRR@4 on the main set. And I can tell you where it fails, which matters "
                  "more."]),
                ("Why hybrid search? Why not just vectors?",
                 ["<strong>Have a real story for this one.</strong> Vector search generalises across wording but is "
                  "blurry on rare literal tokens; BM25 is the opposite. The failure modes look complementary "
                  "&mdash; but when I measured equal-weight fusion, hybrid came out <em>worse</em> than vector alone "
                  "(0.864 vs 0.943), because BM25 is the weaker retriever here and an equal vote let it overrule "
                  "the stronger one.",
                  "Weighting 3:1 fixed that but only proved it did no harm. So I wrote a second question set on "
                  "exact identifiers &mdash; where BM25 should help &mdash; and there hybrid wins 0.875 to 0.812. "
                  "That is why it ships."]),
                ("How did you pick the fusion weight?",
                 ["Deliberately imprecisely. 4:1 scored highest (0.955) but I shipped 3:1, because the gap was "
                  "0.012 MRR &mdash; one question moving one rank &mdash; chosen by looking at the answers on 22 "
                  "questions with no held-out set. Tuning to that is fitting the test, not the problem.",
                  "Done properly: split into a tuning set and a held-out set, or write enough questions that "
                  "real differences clear the noise floor."]),
                ("What is RRF and why not just add the scores?",
                 ["Reciprocal Rank Fusion scores each document as the sum of 1/(K + rank) across every ranked "
                  "list it appears in. It uses <strong>positions, not scores</strong>. Cosine similarity is "
                  "0&ndash;1 and BM25 is unbounded and corpus-dependent, so a weighted sum needs normalisation "
                  "constants you would re-tune whenever the corpus changed."]),
                ("The model gave a wrong answer. How do you debug it?",
                 ["Check retrieval before touching the prompt. Hit <code>/search</code> with the same question and "
                  "look at what came back. Almost every &ldquo;hallucination&rdquo; in a RAG system is the model "
                  "answering faithfully from the wrong passages.",
                  "If the right page is not there, compare vector against keyword to see which half failed. If it "
                  "<em>is</em> there and the answer is still wrong, only then is it a prompt problem."]),
                ("Why not just fine-tune a model on the docs?",
                 ["Different problems. RAG supplies <strong>facts</strong>; fine-tuning changes "
                  "<strong>behaviour</strong> &mdash; tone, format, structure. For a docs assistant the facts change "
                  "every release, and re-indexing costs cents while re-training does not. RAG also gives "
                  "citations, so a human can verify the answer."]),
                ("What would you do differently at 10 million documents?",
                 ["BM25 in Python over an in-memory corpus stops working &mdash; push keyword search into the "
                  "database, which LanceDB supports with a full-text index. Indexing becomes incremental rather "
                  "than a full rebuild. Add an approximate-nearest-neighbour index instead of an exhaustive "
                  "scan. And a reranker matters much more, because the candidate pool gets noisier as the corpus "
                  "grows."]),
                ("What is the weakest part of this project?",
                 ["Answer honestly &mdash; this tests self-awareness, and claiming there are no weaknesses fails "
                  "it. Real answers: no reranker; a small local embedding model chosen for zero setup rather "
                  "than quality; the evaluation covers retrieval but not answer quality; and the eval set is 30 "
                  "questions I wrote myself, so it carries my blind spots."]),
            ]),
        ]))

    return C
