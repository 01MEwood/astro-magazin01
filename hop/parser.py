"""Liest .hop-Dateien verlustfrei ein.

Jedes Byte der Datei landet im Modell: Kodierung und BOM am Dokument,
Zeilenende an jeder einzelnen Zeile. Unbekannte Zeilen gibt es auf dieser
Ebene nicht, weil keine Zeile gedeutet wird.
"""

from __future__ import annotations

import codecs
import re
from pathlib import Path

from .model import HopDocument, Line

# Nur echte Zeilenenden. str.splitlines() würde auch an \x0b, \x0c, \x1c-\x1e,
# \x85 und U+2028/2029 trennen und damit Zeilen zerreißen.
_EOL = re.compile(r"\r\n|\n|\r")

# Reihenfolge der Versuche. latin-1 bildet jedes Byte ab und ist deshalb der
# letzte Ausweg: der Round-Trip bleibt auch dann bytegenau.
_FALLBACKS = ("ascii", "utf-8", "cp1252", "latin-1")


def _decode(data: bytes) -> tuple[str, str]:
    for encoding in _FALLBACKS:
        try:
            return data.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    raise AssertionError("latin-1 dekodiert jede Bytefolge")


def parse_bytes(data: bytes) -> HopDocument:
    bom = b""
    if data.startswith(codecs.BOM_UTF8):
        bom = codecs.BOM_UTF8
        text, encoding = data[len(bom):].decode("utf-8"), "utf-8"
    else:
        text, encoding = _decode(data)

    lines: list[Line] = []
    pos = 0
    for match in _EOL.finditer(text):
        lines.append(Line(text[pos:match.start()], match.group()))
        pos = match.end()
    if pos < len(text):
        lines.append(Line(text[pos:], ""))
    return HopDocument(lines=lines, encoding=encoding, bom=bom)


def parse_file(path: str | Path) -> HopDocument:
    return parse_bytes(Path(path).read_bytes())
