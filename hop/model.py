"""Datenmodell der verlustfreien Ebene.

Bewusst formatneutral: eine Datei ist eine Folge von Zeilen, jede Zeile
behält ihren Originaltext und ihr eigenes Zeilenende. Die fachliche Deutung
(Kopf, Variablen, Bearbeitungen, Makroaufrufe) kommt erst dazu, wenn sie in
FORMAT.md mit Belegstelle aus samples/ abgesichert ist.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Line:
    text: str
    """Zeileninhalt ohne Zeilenende, unverändert."""
    eol: str
    """Zeilenende dieser Zeile: "\\r\\n", "\\n", "\\r" oder "" (letzte Zeile ohne Umbruch)."""


@dataclass
class HopDocument:
    lines: list[Line] = field(default_factory=list)
    encoding: str = "ascii"
    """Kodierung, mit der gelesen wurde und wieder geschrieben wird."""
    bom: bytes = b""
    """Byte Order Mark am Dateianfang, falls vorhanden."""
