"""Verify every code block in the generated guide matches the real source.

The guide's whole claim is that its code is the code that runs. This checks it:
strip the highlight markup back out, unescape, and compare against the file.

Three kinds of block, three checks:

  walkthrough  a file presented as numbered pieces to type. The pieces are
               joined in order and must reproduce the file EXACTLY -- this is
               the check that matters most, because a bad split would silently
               drop lines and the reader would type an incomplete file.
  whole file   must match the file exactly.
  symbol       an extracted function, dedented for display, so it is checked
               by re-indenting until one level matches.

Run:  python verify_guide.py
Exit code is non-zero if anything drifted, so it works as a CI gate.
"""

from __future__ import annotations

import collections
import html
import re
import sys
from pathlib import Path

REPO = Path(r"C:\Users\luise\Documents\GitHub\rag-docs-assistant")
GUIDE = Path(__file__).parent / "rag-build-guide.html"

WALK = re.compile(
    r'<div class="code-block walk" data-part-of="(?P<path>[^"]+)" '
    r'data-part-index="(?P<index>\d+)">.*?<pre>(?P<code>.*?)</pre>',
    re.DOTALL,
)
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
    failures: list[str] = []

    # --- walkthroughs: the joined pieces must rebuild the file --------------
    pieces: dict[str, list[tuple[int, str]]] = collections.defaultdict(list)
    for m in WALK.finditer(guide):
        pieces[html.unescape(m.group("path"))].append(
            (int(m.group("index")), plain(m.group("code")))
        )

    for path, parts in sorted(pieces.items()):
        parts.sort()
        rebuilt = "\n".join(code for _i, code in parts)
        actual = (REPO / path).read_text(encoding="utf-8").rstrip("\n")
        if rebuilt == actual:
            print(f"  ok   {path}: {len(parts)} pieces rejoin into the exact file")
        else:
            failures.append(path)
            print(f"  FAIL {path}: {len(parts)} pieces do NOT rebuild the file")
            a, b = actual.splitlines(), rebuilt.splitlines()
            print(f"       file has {len(a)} lines, pieces have {len(b)}")
            for i, (x, y) in enumerate(zip(a, b)):
                if x != y:
                    print(f"       first difference at line {i + 1}")
                    print(f"         file:   {x!r}")
                    print(f"         guide:  {y!r}")
                    break

    # --- everything else ----------------------------------------------------
    remainder = WALK.sub("", guide)
    whole = extract = 0
    for m in BLOCK.finditer(remainder):
        path = html.unescape(m.group("path"))
        shown = plain(m.group("code"))
        actual = (REPO / path).read_text(encoding="utf-8").rstrip("\n")
        if shown == actual:
            whole += 1
        elif any(indented(shown, n) in actual for n in (0, 4, 8)):
            extract += 1
        else:
            failures.append(path)
            first = shown.splitlines()[0] if shown.splitlines() else ""
            print(f"  FAIL {path}: block drifted\n       shows: {first[:70]!r}")

    print(f"\n{len(pieces)} files shown as walkthroughs, all pieces rejoin exactly"
          if not failures else "")
    print(f"{whole} whole-file blocks match exactly")
    print(f"{extract} extracted symbols found verbatim in their file")

    if failures:
        print(f"\n{len(failures)} problem(s) - the guide does not match the code")
        return 1
    print("\n0 drifted - the guide matches the code that runs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
