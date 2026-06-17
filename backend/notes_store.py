"""Note storage: markdown files with frontmatter are the source of truth.

CRUD over the notes/ directory (spec §6). The retrieval index is built on
top of this and is always rebuildable from these files.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import frontmatter

NOTES_DIR = Path(__file__).resolve().parent.parent / "notes"


def _now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-") or "note"


def _path_for(note_id: str) -> Path:
    return NOTES_DIR / f"{note_id}.md"


def _load(path: Path) -> frontmatter.Post:
    return frontmatter.load(path)


def list_notes(limit: int = 20) -> list[dict]:
    """Metadata (id, title, dates, tags) for recent notes. No bodies."""
    NOTES_DIR.mkdir(exist_ok=True)
    metas = []
    for p in NOTES_DIR.glob("*.md"):
        post = _load(p)
        metas.append(
            {
                "id": post.get("id", p.stem),
                "title": post.get("title", p.stem),
                "created": post.get("created", ""),
                "updated": post.get("updated", ""),
                "tags": post.get("tags", []),
            }
        )
    metas.sort(key=lambda m: str(m.get("updated") or m.get("created")), reverse=True)
    return metas[:limit]


def iter_notes() -> list[dict]:
    """All notes WITH bodies — used by retrieval. [{id, title, body, tags}]."""
    NOTES_DIR.mkdir(exist_ok=True)
    out = []
    for p in NOTES_DIR.glob("*.md"):
        post = _load(p)
        out.append(
            {
                "id": post.get("id", p.stem),
                "title": post.get("title", p.stem),
                "body": post.content,
                "tags": post.get("tags", []),
            }
        )
    return out


def read_note(note_id: str) -> str:
    """Full body of one note. Raises FileNotFoundError if missing."""
    path = _path_for(note_id)
    if not path.exists():
        raise FileNotFoundError(f"No note with id {note_id!r}")
    return _load(path).content


def write_note(title: str, body: str, tags: list[str] | None = None) -> str:
    """Create a new note; return its id. id = <date>-<slug(title)>."""
    NOTES_DIR.mkdir(exist_ok=True)
    now = _now_iso()
    note_id = f"{now[:10]}-{_slugify(title)}"
    # de-dupe id if a note with the same title was made today
    candidate, n = note_id, 2
    while _path_for(candidate).exists():
        candidate = f"{note_id}-{n}"
        n += 1
    note_id = candidate

    post = frontmatter.Post(
        body,
        id=note_id,
        title=title,
        created=now,
        updated=now,
        tags=tags or [],
    )
    _path_for(note_id).write_text(frontmatter.dumps(post), encoding="utf-8")
    return note_id


def update_note(note_id: str, body: str) -> bool:
    """Replace the body of an existing note; bump updated. Returns True."""
    path = _path_for(note_id)
    if not path.exists():
        raise FileNotFoundError(f"No note with id {note_id!r}")
    post = _load(path)
    post.content = body
    post["updated"] = _now_iso()
    path.write_text(frontmatter.dumps(post), encoding="utf-8")
    return True
