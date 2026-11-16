"""Hilfen für die Formatanalyse (Stufe 1).

Zählt, was in den Beispieldateien tatsächlich vorkommt, und nennt zu jedem
Befund eine Belegstelle (Datei:Zeile). Deutet nichts.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from .parser import parse_file
from .writer import to_bytes

_EOL_NAMES = {"\r\n": "CRLF", "\n": "LF", "\r": "CR", "": "ohne"}
_FIRST_TOKEN = re.compile(r"\s*([A-Za-z_][A-Za-z0-9_]*|\S)")


def find_samples(root: str | Path) -> list[Path]:
    root = Path(root)
    if root.is_file():
        return [root]
    return sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() == ".hop")


def roundtrip_ok(path: Path) -> bool:
    return to_bytes(parse_file(path)) == path.read_bytes()


def stats(paths: list[Path]) -> str:
    encodings: Counter[str] = Counter()
    boms: Counter[str] = Counter()
    eols: Counter[str] = Counter()
    tokens: Counter[str] = Counter()
    evidence: dict[str, str] = {}

    for path in paths:
        doc = parse_file(path)
        encodings[doc.encoding] += 1
        boms["mit BOM" if doc.bom else "ohne BOM"] += 1
        for number, line in enumerate(doc.lines, start=1):
            is_last = number == len(doc.lines)
            eols[_EOL_NAMES[line.eol] + (" (Dateiende)" if is_last else "")] += 1
            match = _FIRST_TOKEN.match(line.text)
            token = match.group(1) if match else "<leer>"
            tokens[token] += 1
            evidence.setdefault(token, f"{path}:{number}")

    out = [f"Dateien: {len(paths)}"]
    for title, counter in (("Kodierung", encodings), ("BOM", boms), ("Zeilenenden", eols)):
        out.append(f"\n{title}:")
        out += [f"  {count:6d}  {key}" for key, count in counter.most_common()]
    out.append("\nZeilenanfänge (erstes Token, Anzahl, erste Belegstelle):")
    out += [f"  {count:6d}  {key:<24} {evidence[key]}" for key, count in tokens.most_common()]
    return "\n".join(out)
