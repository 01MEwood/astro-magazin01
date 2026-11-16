from __future__ import annotations

import csv
import io

from .modell import Ergebnis, Teil

SPALTEN = ("korpus", "teil", "laenge", "breite", "staerke", "material", "schraegschnitte", "hinweis")


def _zeile(t: Teil) -> list[str]:
    hinweis = t.hinweis
    if not t.rechteckig:
        ecken = " ".join(f"{x:.1f}/{y:.1f}" for x, y in t.umriss)
        hinweis = (hinweis + "; " if hinweis else "") + f"Umriss {ecken}"
    schnitte = ", ".join(f"{k} {w:g}°" for k, w in t.schraegschnitte.items())
    return [t.korpus, t.name, f"{t.laenge:.1f}", f"{t.breite:.1f}", f"{t.material.staerke:g}",
            t.material.name, schnitte, hinweis]


def als_csv(ergebnis: Ergebnis) -> str:
    puffer = io.StringIO()
    writer = csv.writer(puffer, delimiter=";", lineterminator="\n")
    writer.writerow(SPALTEN)
    for t in ergebnis.teile:
        writer.writerow([z.replace(".", ",") if i in (2, 3, 4) else z for i, z in enumerate(_zeile(t))])
    return puffer.getvalue()


def als_text(ergebnis: Ergebnis) -> str:
    out = ["Korpusse (Lage ab linker Wand, Höhe ohne Sockel):"]
    for k in ergebnis.korpusse:
        hoehe = f"{k.hoehe_links:.1f}" if abs(k.hoehe_links - k.hoehe_rechts) < 0.05 else f"{k.hoehe_links:.1f} bis {k.hoehe_rechts:.1f}"
        out.append(f"  {k.name:<22} x {k.x:7.1f}  Breite {k.breite:7.1f}  Höhe {hoehe}")
    out.append(f"\nTeile ({len(ergebnis.teile)}):")
    out.append(f"  {'Korpus':<20}{'Teil':<19}{'Länge':>8}{'Breite':>8}{'St.':>5}  Material / Schnitte / Hinweis")
    for t in ergebnis.teile:
        z = _zeile(t)
        rest = "  ".join(s for s in z[5:] if s)
        out.append(f"  {z[0]:<20}{z[1]:<19}{z[2]:>8}{z[3]:>8}{z[4]:>5}  {rest}")
    if ergebnis.beschlaege:
        out.append("\nBeschläge:")
        for b in ergebnis.beschlaege:
            laenge = f"  Länge {b.laenge:.1f}" if b.laenge is not None else ""
            out.append(f"  {b.korpus:<20}{b.anzahl:3d} x {b.name}{laenge}")
    return "\n".join(out)
