"""Hand-authored SVG diagrams for the build-along guide.

Every diagram shows a mechanism the prose would otherwise have to describe in
sequence: where data flows, what each stage hands the next, what changes
between two options. Colours come from the page's CSS custom properties, so
each figure themes with the page instead of carrying its own palette.
"""

from __future__ import annotations


def figure(svg: str, caption: str, label: str) -> str:
    return (
        f'<figure class="fig"><svg viewBox="{svg[0]}" role="img" aria-label="{label}">'
        f"{svg[1]}</svg>"
        f"<figcaption>{caption}</figcaption></figure>"
    )


def _defs(prefix: str) -> str:
    return (
        "<defs>"
        f'<marker id="{prefix}-a" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="var(--ink-soft)"/></marker>'
        f'<marker id="{prefix}-r" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="var(--rose)"/></marker>'
        f'<marker id="{prefix}-b" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="var(--blue)"/></marker>'
        "</defs>"
    )


def _box(x, y, w, h, title, sub="", tone="plain", rx=12):
    fills = {
        "plain": ("var(--card-2)", "var(--rule)", "1.5"),
        "blue": ("var(--blue-wash)", "var(--blue)", "2"),
        "rose": ("var(--rose-wash)", "var(--rose)", "2"),
        "green": ("var(--green-wash)", "var(--green)", "2"),
    }
    fill, stroke, sw = fills[tone]
    cx = x + w / 2
    ty = y + (h / 2 + 5) if not sub else y + h / 2 - 3
    out = (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
        f'<text class="d-box" x="{cx}" y="{ty}" text-anchor="middle">{title}</text>'
    )
    if sub:
        out += f'<text class="d-sub" x="{cx}" y="{y + h / 2 + 15}" text-anchor="middle">{sub}</text>'
    return out


def _arrow(x1, y1, x2, y2, prefix, tone="ink", label="", dashed=False, lx=None, ly=None):
    colours = {"ink": "var(--ink-soft)", "rose": "var(--rose)", "blue": "var(--blue)"}
    marker = {"ink": "a", "rose": "r", "blue": "b"}[tone]
    dash = ' stroke-dasharray="5 5"' if dashed else ""
    out = (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{colours[tone]}" '
        f'stroke-width="2"{dash} marker-end="url(#{prefix}-{marker})"/>'
    )
    if label:
        tx = lx if lx is not None else (x1 + x2) / 2
        ty = ly if ly is not None else min(y1, y2) - 8
        out += f'<text class="d-edge" x="{tx}" y="{ty}" text-anchor="middle">{label}</text>'
    return out


# --------------------------------------------------------------------------


def two_phases() -> str:
    p = "ph"
    s = _defs(p)
    # Edge labels sit ABOVE the row of boxes rather than in the arrow gaps:
    # "chunk.py" is wider than any sensible gap between two boxes, so putting
    # it inline guarantees a collision at some viewport width.
    s += '<text class="d-title" x="20" y="22" fill="var(--blue)">PHASE 1 &#183; INDEXING &#183; ONCE, OFFLINE</text>'
    s += _box(20, 58, 130, 62, "Your docs", "154 markdown files")
    s += _box(212, 58, 130, 62, "Chunks", "767 passages")
    s += _box(404, 58, 152, 62, "Embedding model", "text &#8594; 384 numbers", "blue")
    s += _box(618, 58, 168, 62, "Vector index", "text + its vector", "blue")

    s += _arrow(154, 89, 208, 89, p, "ink", "chunk.py", ly=48)
    s += _arrow(346, 89, 400, 89, p, "ink", "embed.py", ly=48)
    s += _arrow(560, 89, 614, 89, p, "ink", "index.py", ly=48)

    s += '<line x1="20" y1="152" x2="800" y2="152" stroke="var(--rule)" stroke-dasharray="4 6"/>'
    s += '<text class="d-title" x="20" y="186" fill="var(--rose)">PHASE 2 &#183; ANSWERING &#183; PER QUESTION</text>'

    s += _box(20, 212, 118, 62, "Question", "from a user")
    s += _box(178, 212, 132, 62, "Embedding", "the same model", "blue")
    s += _box(350, 212, 120, 62, "Search", "nearest + BM25", "rose")
    s += _box(510, 212, 122, 62, "Top 4 chunks", "the evidence", "rose")
    s += _box(672, 212, 130, 62, "Claude", "reads, answers", "green")

    s += _arrow(142, 243, 174, 243, p, "rose")
    s += _arrow(314, 243, 346, 243, p, "rose")
    s += _arrow(474, 243, 506, 243, p, "rose")
    s += _arrow(636, 243, 668, 243, p, "rose")

    # The index feeds the search step - the one thing both phases touch.
    s += (
        f'<path d="M 702 124 L 702 166 L 410 166 L 410 208" fill="none" '
        f'stroke="var(--blue)" stroke-width="2" stroke-dasharray="5 5" '
        f'marker-end="url(#{p}-b)"/>'
        '<text class="d-edge" x="556" y="160" text-anchor="middle" fill="var(--blue)">'
        "the only thing the two phases share</text>"
    )
    return ("0 0 820 296", s)


def chunking() -> str:
    p = "ck"
    s = _defs(p)

    # source document
    s += '<rect x="20" y="34" width="150" height="230" rx="12" fill="var(--card-2)" stroke="var(--rule)" stroke-width="1.5"/>'
    s += '<text class="d-sub" x="95" y="24" text-anchor="middle">handling-errors.md</text>'
    s += '<text class="d-mono" x="34" y="58">## Handling Errors</text>'
    ys = [76, 88, 100]
    for y in ys:
        s += f'<line x1="34" y1="{y}" x2="150" y2="{y}" stroke="var(--ink-soft)" stroke-width="3" opacity=".28"/>'
    s += '<text class="d-mono" x="34" y="126">### Validation errors</text>'
    for y in [144, 156, 168, 180]:
        s += f'<line x1="34" y1="{y}" x2="{150 if y != 180 else 118}" y2="{y}" stroke="var(--ink-soft)" stroke-width="3" opacity=".28"/>'
    s += '<text class="d-mono" x="34" y="206">### Custom handlers</text>'
    for y in [224, 236, 248]:
        s += f'<line x1="34" y1="{y}" x2="{150 if y != 248 else 130}" y2="{y}" stroke="var(--ink-soft)" stroke-width="3" opacity=".28"/>'

    s += _arrow(180, 148, 218, 148, p, "ink", "chunk.py", ly=140)

    # chunks
    s += '<rect x="234" y="34" width="330" height="96" rx="12" fill="var(--card-2)" stroke="var(--rose)" stroke-width="2"/>'
    s += '<text class="d-mono" x="248" y="56" fill="var(--rose)">handling-errors.md | Handling Errors</text>'
    s += '<text class="d-sub" x="248" y="76">the heading path, inside the text</text>'
    for y in [92, 106]:
        s += f'<line x1="248" y1="{y}" x2="{540 if y == 92 else 470}" y2="{y}" stroke="var(--ink-soft)" stroke-width="3" opacity=".28"/>'
    s += '<text class="d-sub" x="248" y="124" fill="var(--ink-soft)">chunk 1</text>'

    s += '<rect x="234" y="152" width="330" height="112" rx="12" fill="var(--card-2)" stroke="var(--rose)" stroke-width="2"/>'
    s += '<text class="d-mono" x="248" y="174" fill="var(--rose)">... | Handling Errors &gt; Validation errors</text>'
    # overlap band
    s += '<rect x="244" y="184" width="310" height="22" rx="7" fill="var(--green-wash)" stroke="var(--green)" stroke-width="1.5"/>'
    s += '<text class="d-sub" x="252" y="199" fill="var(--green)">repeated tail of chunk 1 &#8212; the overlap</text>'
    for y in [220, 234]:
        s += f'<line x1="248" y1="{y}" x2="{540 if y == 220 else 500}" y2="{y}" stroke="var(--ink-soft)" stroke-width="3" opacity=".28"/>'
    s += '<text class="d-sub" x="248" y="256" fill="var(--ink-soft)">chunk 2</text>'

    s += f'<path d="M 580 90 L 604 90 L 604 208 L 580 208" fill="none" stroke="var(--green)" stroke-width="1.5"/>'
    s += '<text class="d-edge" x="612" y="152" fill="var(--green)">40 words</text>'
    return ("0 0 700 285", s)


def embedding_space() -> str:
    p = "em"
    s = _defs(p)
    s += '<rect x="30" y="30" width="620" height="280" rx="14" fill="var(--card-2)" stroke="var(--rule)" stroke-width="1.5"/>'
    for y in (100, 170, 240):
        s += f'<line x1="30" y1="{y}" x2="650" y2="{y}" stroke="var(--rule)" opacity=".6"/>'
    for x in (185, 340, 495):
        s += f'<line x1="{x}" y1="30" x2="{x}" y2="310" stroke="var(--rule)" opacity=".6"/>'

    s += '<text class="d-title" x="30" y="20" fill="var(--ink-soft)">A MAP OF MEANING &#183; EACH DOT IS ONE CHUNK</text>'

    clusters = [
        ((115, 95), (150, 82), (135, 118), (168, 108), (100, 126)),
        ((290, 80), (322, 66), (306, 104), (340, 92), (274, 106)),
    ]
    for pts in clusters:
        for cx, cy in pts:
            s += f'<circle cx="{cx}" cy="{cy}" r="6" fill="var(--blue)" opacity=".85"/>'
    s += '<text class="d-edge" x="98" y="158" fill="var(--blue)">SHIPPING &amp; DELIVERY</text>'
    s += '<text class="d-edge" x="272" y="136" fill="var(--blue)">PAYMENTS &amp; INVOICES</text>'

    for cx, cy in ((596, 186), (452, 292), (606, 272)):
        s += f'<circle cx="{cx}" cy="{cy}" r="6" fill="var(--blue)" opacity=".85"/>'
    for cx, cy in ((478, 206), (528, 248), (492, 262)):
        s += f'<circle cx="{cx}" cy="{cy}" r="7.5" fill="var(--rose)"/>'
    s += '<circle cx="503" cy="236" r="62" fill="none" stroke="var(--rose)" stroke-width="1.5" stroke-dasharray="5 5"/>'
    s += '<text class="d-edge" x="642" y="160" text-anchor="end" fill="var(--rose)">RETURNS &amp; REFUNDS</text>'

    s += '<path d="M 503 226 l 6 -12 l 6 12 l 12 4 l -12 4 l -6 12 l -6 -12 l -12 -4 z" fill="var(--rose)" transform="translate(-6,10)"/>'
    s += '<line x1="424" y1="240" x2="486" y2="237" stroke="var(--rose)" stroke-width="1.5"/>'
    s += '<text class="d-edge" x="418" y="234" text-anchor="end" fill="var(--rose)">YOUR QUESTION</text>'
    s += '<text class="d-edge" x="418" y="249" text-anchor="end" fill="var(--rose)">LANDS HERE</text>'
    return ("0 0 680 325", s)


def rrf() -> str:
    p = "rr"
    s = _defs(p)
    s += '<text class="d-title" x="20" y="22" fill="var(--blue)">VECTOR RANKING</text>'
    s += '<text class="d-title" x="250" y="22" fill="var(--rose)">BM25 RANKING</text>'
    s += '<text class="d-title" x="520" y="22" fill="var(--green)">FUSED &#183; 3&#215;VECTOR + 1&#215;BM25</text>'

    vec = ["static-files.md", "frontend.md", "custom-docs.md", "staticfiles.md"]
    bm = ["staticfiles.md", "custom-docs.md", "frontend.md", "static-files.md"]
    fused = ["static-files.md", "staticfiles.md", "frontend.md", "custom-docs.md"]

    def col(x, items, tone, w=200):
        out = ""
        colours = {"blue": "var(--blue)", "rose": "var(--rose)", "green": "var(--green)"}
        for i, name in enumerate(items):
            y = 40 + i * 44
            fill = "var(--card-2)"
            stroke = colours[tone]
            out += (
                f'<rect x="{x}" y="{y}" width="{w}" height="34" rx="10" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="1.5" opacity="{1 - i * 0.13}"/>'
                f'<text class="d-mono" x="{x + 12}" y="{y + 22}">{i + 1}. {name}</text>'
            )
        return out

    s += col(20, vec, "blue")
    s += col(250, bm, "rose")
    s += col(500, fused, "green", 210)

    s += '<text class="d-edge" x="232" y="128" text-anchor="middle">+</text>'
    s += _arrow(462, 118, 494, 118, p, "ink")
    s += (
        '<text class="d-sub" x="20" y="238">Each list votes 1/(60 + rank). The vector list&#8217;s vote counts three times,</text>'
        '<text class="d-sub" x="20" y="256">so the tutorial page wins even though BM25 ranked it last.</text>'
    )
    return ("0 0 740 275", s)


def api_flow() -> str:
    p = "ap"
    s = _defs(p)
    s += _box(20, 92, 120, 58, "Browser", "or curl")
    s += _box(190, 92, 130, 58, "FastAPI", "app/api.py", "blue")
    s += _arrow(144, 121, 186, 121, p)

    s += _box(390, 24, 150, 58, "/search", "retrieval only", "green")
    s += _box(390, 160, 150, 58, "/ask", "retrieval + Claude", "rose")

    s += f'<path d="M 324 110 L 356 110 L 356 53 L 386 53" fill="none" stroke="var(--green)" stroke-width="2" marker-end="url(#{p}-a)"/>'
    s += f'<path d="M 324 132 L 356 132 L 356 189 L 386 189" fill="none" stroke="var(--rose)" stroke-width="2" marker-end="url(#{p}-r)"/>'

    s += _box(600, 24, 170, 58, "Free", "no key, no cost", "green")
    s += _box(600, 160, 170, 58, "Costs tokens", "needs an API key", "rose")
    s += _arrow(544, 53, 596, 53, p)
    s += _arrow(544, 189, 596, 189, p, "rose")

    s += '<text class="d-sub" x="20" y="256">When an answer is wrong, hit /search first: it shows you exactly what the model was given,</text>'
    s += '<text class="d-sub" x="20" y="274">for nothing. Most &#8220;hallucinations&#8221; turn out to be retrieval bugs.</text>'
    return ("0 0 790 290", s)


def git_timeline() -> str:
    p = "gt"
    s = _defs(p)
    s += '<line x1="40" y1="70" x2="840" y2="70" stroke="var(--rule)" stroke-width="3"/>'
    commits = [
        (70, "chore: scaffold", "ch 2"),
        (200, "feat: config", "ch 3"),
        (330, "feat: fetch docs", "ch 5"),
        (460, "feat: chunker", "ch 6"),
        (590, "feat: retrieval", "ch 9-11"),
        (720, "feat: evaluation", "ch 13"),
        (830, "docs: README", "ch 19"),
    ]
    for x, msg, ch in commits:
        s += f'<circle cx="{x}" cy="70" r="9" fill="var(--rose)"/>'
        s += f'<text class="d-edge" x="{x}" y="46" text-anchor="middle" fill="var(--ink-soft)">{ch}</text>'
        s += f'<text class="d-mono" x="{x}" y="100" text-anchor="middle">{msg}</text>'
    s += '<text class="d-sub" x="40" y="140">One commit per chapter. Each is a working state you can return to, and the history</text>'
    s += '<text class="d-sub" x="40" y="158">tells a reviewer how you actually built it &#8212; which is worth reading.</text>'
    return ("0 0 880 175", s)
