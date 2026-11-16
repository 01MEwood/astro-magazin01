"""Liest auftraege.csv und verluste.csv und fasst sie zusammen.

Verträgt Excel-Exporte: Trennzeichen ; oder , und Dezimalkomma,
Kodierung UTF-8 (mit oder ohne BOM) oder Windows-1252.
"""

from __future__ import annotations

import csv
import io
from collections import defaultdict
from pathlib import Path

KATEGORIEN = ("Warten", "Suchen", "Nachfragen", "Nacharbeit")


class EingabeFehler(ValueError):
    pass


def lies_csv(path: Path, pflicht: tuple[str, ...]) -> list[dict[str, str]]:
    data = path.read_bytes()
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = data.decode("cp1252")
    kopf = text.splitlines()[0] if text.strip() else ""
    delimiter = ";" if kopf.count(";") >= kopf.count(",") else ","
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    spalten = [(s or "").strip().lower() for s in (reader.fieldnames or [])]
    fehlend = [s for s in pflicht if s not in spalten]
    if fehlend:
        raise EingabeFehler(f"{path.name}: Spalte fehlt: {', '.join(fehlend)}")
    zeilen = []
    for nummer, roh in enumerate(reader, start=2):
        zeile = {(k or "").strip().lower(): (v or "").strip() for k, v in roh.items()}
        if any(zeile.values()):
            zeile["_ort"] = f"{path.name}:{nummer}"
            zeilen.append(zeile)
    return zeilen


def zahl(zeile: dict[str, str], spalte: str, leer_erlaubt: bool = False) -> float | None:
    wert = zeile[spalte]
    if not wert:
        if leer_erlaubt:
            return None
        raise EingabeFehler(f"{zeile['_ort']}: {spalte} ist leer")
    try:
        ergebnis = float(wert.replace(",", "."))
    except ValueError:
        raise EingabeFehler(f"{zeile['_ort']}: {spalte} ist keine Zahl: {wert!r}") from None
    if ergebnis < 0:
        raise EingabeFehler(f"{zeile['_ort']}: {spalte} ist negativ")
    return ergebnis


def _kategorie(zeile: dict[str, str]) -> str:
    for name in KATEGORIEN:
        if zeile["kategorie"].lower() == name.lower():
            return name
    raise EingabeFehler(
        f"{zeile['_ort']}: unbekannte Kategorie {zeile['kategorie']!r}, "
        f"erlaubt: {', '.join(KATEGORIEN)}"
    )


def _tabelle(titel: str, summen: dict[str, float], gesamt: float) -> list[str]:
    out = [f"\n{titel}"]
    for name, minuten in sorted(summen.items(), key=lambda kv: -kv[1]):
        anteil = f"{minuten / gesamt:5.0%}" if gesamt else "     "
        out.append(f"  {minuten:8.0f} min  {anteil}  {name}")
    return out


def auswerten(ordner: str | Path) -> str:
    ordner = Path(ordner)
    auftraege = lies_csv(ordner / "auftraege.csv", ("auftrag", "bereich", "soll_min", "ist_min"))
    verluste_pfad = ordner / "verluste.csv"
    verluste = (
        lies_csv(verluste_pfad, ("auftrag", "bereich", "kategorie", "minuten", "ursache"))
        if verluste_pfad.exists()
        else []
    )

    soll: dict[str, float] = defaultdict(float)
    ist_mit_soll: dict[str, float] = defaultdict(float)
    ist: dict[str, float] = defaultdict(float)
    ohne_soll = 0
    for zeile in auftraege:
        bereich = zeile["bereich"] or "(ohne Bereich)"
        ist_min = zahl(zeile, "ist_min")
        soll_min = zahl(zeile, "soll_min", leer_erlaubt=True)
        ist[bereich] += ist_min
        if soll_min is None:
            ohne_soll += 1
        else:
            soll[bereich] += soll_min
            ist_mit_soll[bereich] += ist_min

    ist_gesamt = sum(ist.values())
    nummern = {z["auftrag"] for z in auftraege}
    out = [f"Aufträge: {len(nummern)}   Ist-Zeit gesamt: {ist_gesamt:.0f} min ({ist_gesamt / 60:.1f} h)"]

    out.append("\nSoll gegen Ist je Bereich (nur Zeilen mit Soll-Angabe)")
    out.append(f"  {'Bereich':<16}{'Soll':>8}{'Ist':>8}{'Abw.':>8}{'':>2}{'%':>6}")
    for bereich in sorted(soll, key=lambda b: soll[b] - ist_mit_soll[b]):
        s, i = soll[bereich], ist_mit_soll[bereich]
        prozent = f"{(i - s) / s:+6.0%}" if s else "     -"
        out.append(f"  {bereich:<16}{s:8.0f}{i:8.0f}{i - s:+8.0f}  {prozent}")
    if not soll:
        out.append("  keine Soll-Zeiten angegeben")
    if ohne_soll:
        out.append(f"  ({ohne_soll} Zeilen ohne Soll-Zeit nicht verglichen)")

    out += _tabelle("Ist-Zeit je Bereich", ist, ist_gesamt)

    if not verluste:
        out.append("\nKeine Verluste erfasst (verluste.csv fehlt oder ist leer).")
        return "\n".join(out)

    je_kategorie: dict[str, float] = defaultdict(float)
    je_bereich: dict[str, float] = defaultdict(float)
    je_ursache: dict[str, float] = defaultdict(float)
    faelle: dict[str, int] = defaultdict(int)
    unbekannt = set()
    for zeile in verluste:
        minuten = zahl(zeile, "minuten")
        je_kategorie[_kategorie(zeile)] += minuten
        je_bereich[zeile["bereich"] or "(ohne Bereich)"] += minuten
        ursache = zeile["ursache"] or "(ohne Ursache)"
        je_ursache[ursache] += minuten
        faelle[ursache] += 1
        if zeile["auftrag"] not in nummern:
            unbekannt.add(zeile["auftrag"])

    verlust_gesamt = sum(je_kategorie.values())
    anteil = f" = {verlust_gesamt / ist_gesamt:.0%} der Ist-Zeit" if ist_gesamt else ""
    out.append(f"\nVerluste gesamt: {verlust_gesamt:.0f} min ({verlust_gesamt / 60:.1f} h){anteil}")
    out += _tabelle("Verluste nach Kategorie", je_kategorie, verlust_gesamt)
    out += _tabelle("Verluste nach Bereich", je_bereich, verlust_gesamt)
    mit_faellen = {f"{u} ({faelle[u]}x)": m for u, m in je_ursache.items()}
    out += _tabelle("Verluste nach Ursache", mit_faellen, verlust_gesamt)
    if unbekannt:
        out.append(
            "\nHinweis: Verluste zu Aufträgen ohne Zeile in auftraege.csv: "
            + ", ".join(sorted(unbekannt))
        )
    return "\n".join(out)
