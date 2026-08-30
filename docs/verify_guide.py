"""Verify every code block in the generated guide matches the real source.

The guide's whole claim is that its code is the code that runs. This checks it:
strip the highlight markup back out, unescape, and compare against the file.

Whole-file blocks must match exactly. Extracted symbols are dedented for
display, so they are checked by re-indenting until one indent level matches.

Run:  python verify_guide.py
Exit code is non-zero if anything drifted, so it works as a CI gate.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

REPO = Path(r"C:\Users\luise\Documents\GitHub\rag-docs-assistant")
GUIDE = Path(__file__).parent / "rag-build-guide.html"

BLOCK = re.compile(
    r'<p class="label filename">(?P<path>[^<]+)</p>.*?<pre>(?P<code>.*?)</pre>',
    re.DOTALL,
)


def plain(markup: str) -> str:
    """Undo the highlighter: drop the spans, unescape the entities."""
    return html.unescape(re.sub(r"<[^>]+>", "", markup))


def indented(text: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else line for line in text.splitlines())


def main() -> int:
    guide = GUIDE.read_text(encoding="utf-8")
    whole = extract = 0
    failures: list[str] = []

    for match in BLOCK.finditer(guide):
        path = html.unescape(match.group("path"))
        shown = plain(match.group("code"))
        actual = (REPO / path).read_text(encoding="utf-8").rstrip("\n")

        if shown == actual:
            whole += 1
            continue

        # An extracted symbol: dedented for display, so try putting the
        # indentation back. 4 and 8 cover a method and a nested function.
        if any(indented(shown, n) in actual for n in (0, 4, 8)):
            extract += 1
            continue

        failures.append(path)
        first = shown.splitlines()[0] if shown.splitlines() else ""
        print(f"  DRIFTED  {path}\n           guide shows: {first[:72]!r}")

    print(f"\n{whole} whole files match exactly")
    print(f"{extract} extracted symbols found verbatim in their file")
    if failures:
        print(f"{len(failures)} block(s) drifted from source")
        return 1
    print("0 drifted - the guide matches the code that runs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
