"""Assemble the build-along guide.

Prints the chapter-to-file mapping, so the "one step per file" rule is
visible every time the guide is rebuilt rather than merely asserted in prose.
"""

from pathlib import Path

from guide_chapters import build
from guide_shell import render

chapters = build()
html = render(chapters)
out = Path(__file__).parent / "rag-build-guide.html"
out.write_text(html, encoding="utf-8")

files = [(i, c["file"]) for i, c in enumerate(chapters) if c.get("file")]
concepts = [c["key"] for c in chapters if not c.get("file")]

print(f"{len(chapters)} chapters -> {out.name} ({len(html) / 1024:.0f} KB)")
print(f"\n{len(files)} chapters create exactly one file each:\n")
for i, name in files:
    print(f"  chapter {i:<2}  {name}")
print(f"\n{len(concepts)} chapters create no file: {', '.join(concepts)}")
