"""Liest Projektdatei, Bibliothek und Regeln (TOML)."""

from __future__ import annotations

import tomllib
from pathlib import Path

from .modell import KorpusEingabe, KorpusFehler, Material, Projekt, Raum, Regeln, Schraege, Zeile

DATEN = Path(__file__).parent / "daten"
_KORPUS_FELDER = {"breite", "hoehe", "einlegeboeden", "kleiderstange", "material", "material_je_teil"}


def _toml(path: Path) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def _positiv(tabelle: dict, feld: str, wo: str, null_erlaubt: bool = False) -> float:
    if feld not in tabelle:
        raise KorpusFehler(f"{wo}: {feld} fehlt")
    wert = tabelle[feld]
    if isinstance(wert, bool) or not isinstance(wert, (int, float)) or wert < 0 or (wert == 0 and not null_erlaubt):
        raise KorpusFehler(f"{wo}: {feld} muss eine positive Zahl sein, ist {wert!r}")
    return float(wert)


def lade_projekt(
    path: str | Path,
    bibliothek: str | Path = DATEN / "bibliothek.toml",
    regeln: str | Path = DATEN / "regeln.toml",
) -> Projekt:
    daten, bib = _toml(Path(path)), _toml(Path(bibliothek))
    materialien = {
        k: Material(k, v["name"], float(v["staerke"])) for k, v in bib.get("material", {}).items()
    }
    typen = bib.get("typ", {})

    r = daten.get("raum", {})
    schraege = None
    if "schraege" in r:
        s = r["schraege"]
        if s.get("richtung") not in ("links", "rechts", "hinten"):
            raise KorpusFehler("raum.schraege: richtung muss links, rechts oder hinten sein")
        neigung = _positiv(s, "neigung", "raum.schraege")
        if neigung >= 90:
            raise KorpusFehler("raum.schraege: neigung muss unter 90 Grad liegen")
        schraege = Schraege(s["richtung"], _positiv(s, "kniestock", "raum.schraege", True), neigung)
    raum = Raum(_positiv(r, "breite", "raum"), _positiv(r, "hoehe", "raum"), schraege)

    z = daten.get("zeile", {})
    for feld in ("material", "rueckwand"):
        if z.get(feld) not in materialien:
            raise KorpusFehler(
                f"zeile: {feld} = {z.get(feld)!r} steht nicht in der Bibliothek "
                f"(vorhanden: {', '.join(sorted(materialien))})"
            )
    zeile = Zeile(
        tiefe=_positiv(z, "tiefe", "zeile"),
        material=z["material"],
        rueckwand=z["rueckwand"],
        **{
            f: _positiv(z, f, "zeile", True)
            for f in ("passleiste_links", "passleiste_rechts", "passleiste_oben", "sockel")
            if f in z
        },
    )

    for nummer, eintrag in enumerate(daten.get("korpus", []), start=1):
        wo = f"korpus {nummer}"
        eintrag = dict(eintrag)
        typ = eintrag.pop("typ", None)
        if typ is not None and typ not in typen:
            raise KorpusFehler(f"{wo}: Typ {typ!r} steht nicht in der Bibliothek (vorhanden: {', '.join(sorted(typen))})")
        werte = {**typen.get(typ, {}), **eintrag}
        unbekannt = set(werte) - _KORPUS_FELDER
        if unbekannt:
            raise KorpusFehler(f"{wo}: unbekannte Angabe {', '.join(sorted(unbekannt))}")
        for feld in ("breite", "hoehe"):
            if feld in werte:
                werte[feld] = _positiv(werte, feld, wo)
        for schluessel in [werte.get("material"), *werte.get("material_je_teil", {}).values()]:
            if schluessel is not None and schluessel not in materialien:
                raise KorpusFehler(f"{wo}: Material {schluessel!r} steht nicht in der Bibliothek")
        zeile.korpusse.append(KorpusEingabe(name=f"K{nummer} {typ or 'Korpus'}", **werte))
    if not zeile.korpusse:
        raise KorpusFehler("Das Projekt enthält keinen Korpus")

    return Projekt(raum, zeile, materialien, Regeln(**_toml(Path(regeln))))
