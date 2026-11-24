"""Download the FastAPI documentation corpus.

We deliberately do NOT commit the docs into this repository:
  - they are someone else's content, with their own licence
  - a repo that vendors 300 markdown files is annoying to review

Instead we fetch them on demand. The GitHub tarball endpoint gives us the whole
repo in one request, and we extract only the English markdown docs.

Run:  python -m app.fetch_docs
"""

from __future__ import annotations

import io
import tarfile
from pathlib import Path

import httpx

from app.config import CORPUS_DIR, DOCS_SUBPATH, DOCS_TARBALL_URL


def fetch_docs(dest: Path = CORPUS_DIR) -> int:
    """Download the docs tarball and write every .md file under dest.

    Returns the number of files written.
    """
    dest.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {DOCS_TARBALL_URL} ...")
    # follow_redirects: codeload issues a redirect for branch refs
    with httpx.Client(follow_redirects=True, timeout=120.0) as client:
        response = client.get(DOCS_TARBALL_URL)
        response.raise_for_status()

    print(f"  {len(response.content) / 1_000_000:.1f} MB downloaded, extracting...")

    written = 0
    with tarfile.open(fileobj=io.BytesIO(response.content), mode="r:gz") as tar:
        for member in tar.getmembers():
            if not member.isfile() or not member.name.endswith(".md"):
                continue

            # member.name looks like "fastapi-master/docs/en/docs/tutorial/first-steps.md".
            # Strip the leading "<repo>-<branch>/" component the tarball adds.
            parts = member.name.split("/", 1)
            if len(parts) != 2:
                continue
            relative = parts[1]

            if not relative.startswith(DOCS_SUBPATH):
                continue

            # Path *inside* the docs tree: "tutorial/first-steps.md"
            doc_path = relative[len(DOCS_SUBPATH):].lstrip("/")

            extracted = tar.extractfile(member)
            if extracted is None:
                continue

            out_path = dest / doc_path
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(extracted.read())
            written += 1

    print(f"  wrote {written} markdown files to {dest}")
    return written


if __name__ == "__main__":
    fetch_docs()
