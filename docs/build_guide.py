"""Generate the build-along guide from the real repository files.

The code shown in the guide is read from the working project, never retyped,
so the guide cannot drift out of sync with the code that actually runs.

Syntax highlighting uses Python's own `tokenize` module rather than regular
expressions, so a `#` inside a string is never mistaken for a comment.

Run:  python build_guide.py
"""

from __future__ import annotations

import html
import io
import keyword
import tokenize
from pathlib import Path

REPO = Path(r"C:\Users\luise\Documents\GitHub\rag-docs-assistant")
OUT = Path(__file__).parent / "rag-build-guide.html"

SOFT_KEYWORDS = {"self", "cls"}


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def highlight_python(source: str) -> str:
    """Token-accurate Python highlighting."""
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (tokenize.TokenError, IndentationError):
        return esc(source)

    out: list[str] = []
    last_row, last_col = 1, 0

    for tok in tokens:
        # Skip the structural tokens entirely and let the gap logic below
        # reconstruct whitespace from token positions.
        #
        # NEWLINE/NL must NOT be emitted: tokenize reports their end row as the
        # row they terminate, not the next one, so emitting "\n" here *and*
        # letting the row-gap logic fire produces two newlines per line. The
        # positions alone are enough to rebuild the file exactly.
        if tok.type in (
            tokenize.ENCODING,
            tokenize.ENDMARKER,
            tokenize.NEWLINE,
            tokenize.NL,
            tokenize.INDENT,
            tokenize.DEDENT,
        ):
            continue

        srow, scol = tok.start
        if srow > last_row:
            out.append("\n" * (srow - last_row))
            last_col = 0
        if scol > last_col:
            out.append(" " * (scol - last_col))

        text = esc(tok.string)
        if tok.type == tokenize.COMMENT:
            out.append(f'<span class="c">{text}</span>')
        elif tok.type == tokenize.STRING:
            out.append(f'<span class="s">{text}</span>')
        elif tok.type == tokenize.NUMBER:
            out.append(f'<span class="n">{text}</span>')
        elif tok.type == tokenize.NAME and keyword.iskeyword(tok.string):
            out.append(f'<span class="k">{text}</span>')
        elif tok.type == tokenize.NAME and tok.string in SOFT_KEYWORDS:
            out.append(f'<span class="soft">{text}</span>')
        else:
            out.append(text)

        last_row, last_col = tok.end

    return "".join(out).rstrip("\n")


def read(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8").rstrip("\n")


# --------------------------------------------------------------------------
# Block builders
# --------------------------------------------------------------------------


def prose(*paragraphs: str) -> str:
    body = "\n".join(f"<p>{p}</p>" for p in paragraphs)
    return f'<div class="col">{body}</div>'


def heading(text: str) -> str:
    return f'<div class="col"><h3>{text}</h3></div>'


def callout(kind: str, label: str, *paragraphs: str) -> str:
    body = "\n".join(f"<p>{p}</p>" for p in paragraphs)
    return f'<div class="aside {kind}"><p class="label">{label}</p>{body}</div>'


def code_file(rel: str, note: str = "") -> str:
    """A complete file, read from the repo and highlighted."""
    source = read(rel)
    lang = rel.rsplit(".", 1)[-1]
    body = highlight_python(source) if lang == "py" else esc(source)
    right = f'<p class="label">{note}</p>' if note else ""
    return (
        '<div class="code-block file">'
        f'<div class="bar-label"><p class="label filename">{esc(rel)}</p>{right}</div>'
        f"<pre>{body}</pre></div>"
    )


def code_symbol(rel: str, name: str, note: str = "") -> str:
    """Show one function or class from a real file, extracted with ast.

    Used where a file is built up across several chapters. Extracting by name
    rather than by line number means the guide keeps working when the file
    moves around, and the fidelity checker still compares against source.
    """
    import ast

    source = read(rel)
    tree_ = ast.parse(source)
    lines = source.splitlines()

    def find(nodes):
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name == name:
                    return node
                found = find(node.body)
                if found is not None:
                    return found
        return None

    node = find(tree_.body)
    if node is None:
        raise SystemExit(f"{name!r} not found in {rel}")

    start = min([node.lineno] + [d.lineno for d in node.decorator_list]) - 1
    segment = "\n".join(lines[start:node.end_lineno])
    # Strip the common indent so a method reads as a standalone block.
    indent = len(segment) - len(segment.lstrip(" "))
    if indent:
        segment = "\n".join(
            line[indent:] if line.startswith(" " * indent) else line
            for line in segment.splitlines()
        )

    body = highlight_python(segment)
    right = f'<p class="label">{note}</p>' if note else ""
    return (
        '<div class="code-block">'
        f'<div class="bar-label"><p class="label filename">{esc(rel)}</p>{right}</div>'
        f"<pre>{body}</pre></div>"
    )


def code_snippet(label: str, body: str, right: str = "") -> str:
    # The label is author-written HTML (it carries entities like &middot;),
    # so it is NOT escaped here -- escaping it renders "&middot;" literally.
    # Only `body` is caller-supplied content that needs escaping, and callers
    # do that themselves so they can pass highlighted markup through.
    right_html = f'<p class="label">{right}</p>' if right else ""
    return (
        '<div class="code-block">'
        f'<div class="bar-label"><p class="label">{label}</p>{right_html}</div>'
        f"<pre>{body}</pre></div>"
    )


def terminal(label: str, lines: str) -> str:
    return code_snippet(label, esc(lines))


def tree(entries: list[tuple[int, str, str]], caption: str = "") -> str:
    """Render a project tree.

    entries: (depth, name, state) where state is "new", "done" or "".
    """
    rows = []
    for depth, name, state in entries:
        indent = "&nbsp;&nbsp;" * depth * 2
        cls = {"new": "t-new", "done": "t-done"}.get(state, "t-plain")
        marker = "&larr; write this one" if state == "new" else ""
        mark = f'<span class="t-marker">{marker}</span>' if marker else ""
        rows.append(f'<div class="t-row {cls}">{indent}<span>{esc(name)}</span>{mark}</div>')
    cap = f'<p class="t-cap">{caption}</p>' if caption else ""
    return f'<div class="tree">{cap}{"".join(rows)}</div>'


# --------------------------------------------------------------------------
# The project tree, chapter by chapter
# --------------------------------------------------------------------------

def project_tree(new: str | None, done: set[str]) -> str:
    """Full tree with one file marked new and earlier ones marked done."""
    layout = [
        (0, "rag-docs-assistant/", None),
        (1, ".venv/", None),
        (1, "app/", None),
        (2, "__init__.py", "app/__init__.py"),
        (2, "config.py", "app/config.py"),
        (2, "fetch_docs.py", "app/fetch_docs.py"),
        (2, "chunk.py", "app/chunk.py"),
        (2, "embed.py", "app/embed.py"),
        (2, "index.py", "app/index.py"),
        (2, "retrieve.py", "app/retrieve.py"),
        (2, "generate.py", "app/generate.py"),
        (2, "api.py", "app/api.py"),
        (2, "static/", None),
        (3, "index.html", "app/static/index.html"),
        (1, "evaluation/", None),
        (2, "__init__.py", "evaluation/__init__.py"),
        (2, "questions.json", "evaluation/questions.json"),
        (2, "questions_identifiers.json", "evaluation/questions_identifiers.json"),
        (2, "run_eval.py", "evaluation/run_eval.py"),
        (1, "data/", None),
        (1, "requirements.txt", "requirements.txt"),
        (1, ".gitignore", ".gitignore"),
        (1, ".env.example", ".env.example"),
        (1, "README.md", "README.md"),
    ]

    entries = []
    for depth, name, key in layout:
        if key is None:
            entries.append((depth, name, ""))
        elif key == new:
            entries.append((depth, name, "new"))
        elif key in done:
            entries.append((depth, name, "done"))
        else:
            entries.append((depth, name, "pending"))
    return entries


def tree_for(new: str | None, done: set[str], caption: str = "") -> str:
    rows = []
    for depth, name, state in project_tree(new, done):
        indent = '<span class="t-ind"></span>' * depth
        cls = {"new": "t-new", "done": "t-done", "pending": "t-pending"}.get(state, "t-plain")
        mark = '<span class="t-marker">&larr; this chapter</span>' if state == "new" else ""
        tick = '<span class="t-tick">&#10003;</span>' if state == "done" else '<span class="t-tick"></span>'
        rows.append(f'<div class="t-row {cls}">{indent}{tick}<span class="t-name">{esc(name)}</span>{mark}</div>')
    cap = f'<p class="t-cap">{caption}</p>' if caption else ""
    return f'<div class="tree">{cap}{"".join(rows)}</div>'
