from app.chunk import Unit, _clean, _pack, _sections, _split_paragraphs, chunk_markdown


def test_sections_track_heading_path_and_strip_anchors():
    md = "# Page { #page }\nintro\n## Sub\nbody\n# Other\nmore"
    assert _sections(md) == [
        ("Page", "intro"),
        ("Page > Sub", "body"),
        ("Other", "more"),
    ]


def test_hash_inside_code_fence_is_not_a_heading():
    md = "# Page\n```python\n# a comment\nx = 1\n```"
    sections = _sections(md)
    assert len(sections) == 1
    assert "# a comment" in sections[0][1]


def test_clean_drops_admonitions_includes_comments_and_front_matter():
    md = "---\ntitle: x\n---\n/// tip\nkeep me\n///\n{* ../docs_src/a.py *}\n<!-- hidden -->"
    cleaned = _clean(md)
    assert "keep me" in cleaned
    for noise in ("///", "{*", "hidden", "title:"):
        assert noise not in cleaned


def test_split_paragraphs_keeps_code_blocks_whole():
    body = "para one\n\n```\nline a\n\nline b\n```\n\npara two"
    assert _split_paragraphs(body) == ["para one", "```\nline a\n\nline b\n```", "para two"]


def test_pack_isolates_oversized_units_and_merges_runts():
    big = Unit("A", "w " * 70)
    small = Unit("A", "w " * 5)
    groups = _pack([small, big, small], target=20, maximum=65)
    # [small] and [big] are separate groups; the trailing runt merges into [big].
    assert len(groups) == 2
    assert groups[0] == [small]
    assert groups[1] == [big, small]


def test_chunk_markdown_prefixes_doc_and_heading_path():
    md = "# First Steps\n## Check it\n" + "word " * 30
    chunks = chunk_markdown("tutorial/first-steps.md", md)
    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk.heading_path == "First Steps > Check it"
    assert chunk.text.startswith("tutorial/first-steps.md | First Steps > Check it\n\n")
    assert chunk.n_words == len(chunk.text.split())


def test_chunk_markdown_overlaps_consecutive_chunks():
    paragraphs = "\n\n".join(
        " ".join(f"t{i}_{j}" for j in range(150)) for i in range(3)
    )
    chunks = chunk_markdown("doc.md", "# T\n" + paragraphs)
    assert len(chunks) >= 2
    # The second chunk carries the tail of the first one forward.
    assert "t0_149" in chunks[1].text


def test_chunk_markdown_empty_document():
    assert chunk_markdown("empty.md", "") == []
