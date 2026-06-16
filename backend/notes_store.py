"""Note storage: markdown files with frontmatter are the source of truth.

Implements CRUD over the notes/ directory. The retrieval index is built
on top of this and is always rebuildable from these files. See spec §6.
"""

from pathlib import Path

NOTES_DIR = Path(__file__).resolve().parent.parent / "notes"


def list_notes(limit: int = 20):
    """Return metadata (id, title, dates) for recent notes. No bodies."""
    raise NotImplementedError("M1")


def read_note(note_id: str) -> str:
    """Return the full body of one note."""
    raise NotImplementedError("M1")


def write_note(title: str, body: str) -> str:
    """Create a new note; return its id. (Triggers index update at M3.)"""
    raise NotImplementedError("M1")


def update_note(note_id: str, body: str) -> bool:
    """Edit an existing note. (Triggers index update at M3.)"""
    raise NotImplementedError("M1")
