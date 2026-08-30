"""Split markdown documents into retrievable chunks.

This is the single highest-leverage file in the repository. Retrieval can only
return chunks you created, so a bad split puts the right answer permanently out
of reach -- no prompt engineering downstream can recover it.

Three decisions are made here, and each one is defended in the README:

1. Split on markdown headings first, not on a fixed character count.
   A heading is the author telling you where one idea ends and the next begins.
   Ignoring that and slicing every 1000 characters is the most common reason a
   first RAG build retrieves garbage.

2. Prepend the heading path to every chunk.
   A chunk that reads "It defaults to 422." is useless on its own. The same
   chunk prefixed with "Tutorial > Handling Errors > Validation errors" is
   findable, because the words a user would search for are now inside it.

3. Overlap consecutive chunks by a few sentences.
   An answer that straddles a boundary would otherwise be cut in half and match
   nothing well. Overlap costs a little storage and removes that failure mode.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path

from app.config import (
    CHUNK_MAX_WORDS,
    CHUNK_MIN_WORDS,
    CHUNK_OVERLAP_WORDS,
    CHUNK_TARGET_WORDS,
)


@dataclass
class Unit:
    """A paragraph, plus the heading trail it was found under."""

    heading_path: str
    text: str

# ATX headings: "## Some heading". Setext headings (underlined with ===) are
# not used anywhere in the FastAPI docs, so we don't handle them.
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*$")

# FastAPI's docs pin anchors onto headings: "## Query Parameters { #query-params }".
# The anchor is for the site's URLs, not for a reader, so it only dilutes the
# embedding.
ANCHOR_RE = re.compile(r"\s*\{\s*#[-\w]+\s*\}\s*$")

# MkDocs admonition markers ("/// tip", "///") carry no meaning for retrieval.
ADMONITION_RE = re.compile(r"^/// ?.*$")

# FastAPI's docs pull code in with {* ../../docs_src/foo.py *}. The include
# marker itself is noise; the referenced code is not in the markdown at all.
INCLUDE_RE = re.compile(r"^\{\*.*\*\}$")

HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


@dataclass
class Chunk:
    """One retrievable passage.

    `text` is what gets embedded and what the model eventually reads, so the
    heading path lives inside it rather than only in the metadata.
    """

    doc_path: str      # "tutorial/first-steps.md"
    heading_path: str  # "First Steps > Check it"
    text: str
    n_words: int

    def to_dict(self) -> dict:
        return asdict(self)


def _clean(markdown: str) -> str:
    """Remove markup that would only add noise to an embedding."""
    markdown = HTML_COMMENT_RE.sub("", markdown)

    # Drop YAML front matter if present.
    if markdown.startswith("---\n"):
        end = markdown.find("\n---", 4)
        if end != -1:
            markdown = markdown[end + 4:]

    kept = [
        line
        for line in markdown.splitlines()
        if not ADMONITION_RE.match(line.strip())
        and not INCLUDE_RE.match(line.strip())
    ]
    return "\n".join(kept)


def _sections(markdown: str) -> list[tuple[str, str]]:
    """Split a document into (heading_path, body) pairs.

    The heading path is the trail of enclosing headings, so a level-3 heading
    inside a level-1 section comes back as "Page title > Subsection".
    """
    sections: list[tuple[str, str]] = []
    stack: list[tuple[int, str]] = []   # (level, title)
    body: list[str] = []
    in_fence = False

    def flush() -> None:
        text = "\n".join(body).strip()
        if text:
            sections.append((" > ".join(title for _, title in stack), text))
        body.clear()

    for line in markdown.splitlines():
        # A "#" inside a fenced block is a Python comment, not a heading.
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            body.append(line)
            continue

        match = None if in_fence else HEADING_RE.match(line)
        if match:
            flush()
            level = len(match.group(1))
            title = ANCHOR_RE.sub("", match.group(2)).strip()
            # Pop any headings at the same or deeper level -- they are siblings
            # or children of the heading we just found, not ancestors of it.
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
        else:
            body.append(line)

    flush()
    return sections


def _split_paragraphs(body: str) -> list[str]:
    """Break a section body into paragraph-sized units.

    Fenced code blocks are kept whole: splitting one in half produces two
    fragments that are individually meaningless.
    """
    units: list[str] = []
    current: list[str] = []
    in_fence = False

    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            current.append(line)
            continue

        if not in_fence and not line.strip():
            if current:
                units.append("\n".join(current).strip())
                current = []
        else:
            current.append(line)

    if current:
        units.append("\n".join(current).strip())

    return [unit for unit in units if unit]


def _pack(units: list[Unit], target: int, maximum: int) -> list[list[Unit]]:
    """Greedily group paragraphs into chunks of roughly `target` words.

    Packing runs across heading boundaries, not within them. Doing it per
    section sounds tidier but produces a corpus of 40-word fragments whenever
    the source has many short subsections -- which is exactly what the FastAPI
    docs look like. A fragment that short carries too little signal to be
    matched reliably.
    """
    groups: list[list[Unit]] = []
    current: list[Unit] = []
    current_words = 0

    for unit in units:
        words = len(unit.text.split())

        # A single oversized paragraph (usually a long code block) becomes its
        # own chunk rather than dragging a whole group over the ceiling.
        if words > maximum:
            if current:
                groups.append(current)
                current, current_words = [], 0
            groups.append([unit])
            continue

        if current and current_words + words > target:
            groups.append(current)
            current, current_words = [], 0

        current.append(unit)
        current_words += words

    if current:
        groups.append(current)

    # Merge any runt back into its predecessor. A 12-word chunk is not a useful
    # retrieval target; it is a chunk that will never win a search and will
    # never help the model if it somehow does.
    merged: list[list[Unit]] = []
    for group in groups:
        words = sum(len(u.text.split()) for u in group)
        if merged and words < CHUNK_MIN_WORDS:
            merged[-1].extend(group)
        else:
            merged.append(group)

    return merged


def _tail_words(text: str, n: int) -> str:
    words = text.split()
    return " ".join(words[-n:]) if len(words) > n else text


def chunk_markdown(doc_path: str, markdown: str) -> list[Chunk]:
    """Turn one markdown document into a list of chunks."""
    cleaned = _clean(markdown)

    # Flatten the document into paragraph units that each remember which
    # section they came from.
    units: list[Unit] = []
    for heading_path, body in _sections(cleaned):
        for paragraph in _split_paragraphs(body):
            units.append(Unit(heading_path=heading_path, text=paragraph))

    if not units:
        return []

    chunks: list[Chunk] = []
    previous_text: str | None = None

    for group in _pack(units, CHUNK_TARGET_WORDS, CHUNK_MAX_WORDS):
        # When a chunk spans a heading boundary, keep the boundary visible so
        # the reader (and the model) can tell where the topic changed.
        pieces: list[str] = []
        seen_heading = group[0].heading_path
        for unit in group:
            if unit.heading_path != seen_heading:
                seen_heading = unit.heading_path
                last_segment = unit.heading_path.split(" > ")[-1]
                pieces.append(f"## {last_segment}")
            pieces.append(unit.text)
        core = "\n\n".join(pieces)

        # Decision 3: carry the tail of the previous chunk forward.
        if previous_text and CHUNK_OVERLAP_WORDS:
            overlap = _tail_words(previous_text, CHUNK_OVERLAP_WORDS)
            core_with_overlap = f"{overlap}\n\n{core}"
        else:
            core_with_overlap = core
        previous_text = core

        # Decision 2: the heading path is part of the embedded text.
        heading_path = group[0].heading_path
        header = f"{doc_path} | {heading_path}" if heading_path else doc_path
        text = f"{header}\n\n{core_with_overlap}".strip()

        chunks.append(
            Chunk(
                doc_path=doc_path,
                heading_path=heading_path,
                text=text,
                n_words=len(text.split()),
            )
        )

    return chunks


def chunk_corpus(corpus_dir: Path) -> list[Chunk]:
    """Chunk every markdown file under corpus_dir."""
    all_chunks: list[Chunk] = []
    for path in sorted(corpus_dir.rglob("*.md")):
        # Files like _llm-test.md are tooling scaffolding for the docs site,
        # not documentation. Indexing them means a user can retrieve them.
        if path.name.startswith("_"):
            continue
        relative = path.relative_to(corpus_dir).as_posix()
        markdown = path.read_text(encoding="utf-8", errors="replace")
        all_chunks.extend(chunk_markdown(relative, markdown))
    return all_chunks
