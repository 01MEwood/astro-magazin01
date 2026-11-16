"""Schreibt ein HopDocument bytegenau zurück."""

from __future__ import annotations

from pathlib import Path

from .model import HopDocument


def to_bytes(doc: HopDocument) -> bytes:
    text = "".join(line.text + line.eol for line in doc.lines)
    return doc.bom + text.encode(doc.encoding)


def write_file(doc: HopDocument, path: str | Path) -> None:
    Path(path).write_bytes(to_bytes(doc))
