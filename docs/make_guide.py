"""Assemble the build-along guide."""
from pathlib import Path

from guide_chapters import build
from guide_shell import render

chapters = build()
html = render(chapters)
out = Path(__file__).parent / "rag-build-guide.html"
out.write_text(html, encoding="utf-8")
print(f"{len(chapters)} chapters -> {out.name} ({len(html)/1024:.0f} KB)")
