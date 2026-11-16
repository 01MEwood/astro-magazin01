"""Erzeugt aus Raum und Schrankzeile alle Teile.

Koordinaten: x entlang der Zeile ab linker Wand, Höhen ab Korpusunterkante
(also über dem Sockel). Maße schräg geschnittener Teile gelten am längsten Punkt.
"""

from __future__ import annotations

import math

from .modell import (
    Beschlag, Ergebnis, KorpusEingabe, KorpusFehler, KorpusMass, Material, Projekt, Teil,
)

EPS = 1e-6


def _rechteck(laenge: float, breite: float):
    return ((0.0, 0.0), (laenge, 0.0), (laenge, breite), (0.0, breite))


def verteile_breiten(projekt: Projekt) -> list[float]:
    z, regeln = projekt.zeile, projekt.regeln
    verfuegbar = projekt.raum.breite - z.passleiste_links - z.passleiste_rechts
    fest = sum(k.breite for k in z.korpusse if k.breite is not None)
    offen = [k for k in z.korpusse if k.breite is None]
    rest = verfuegbar - fest
    if not offen:
        if abs(rest) > 0.05:
            raise KorpusFehler(
                f"Korpusbreiten ergeben {fest:.1f} mm, zwischen den Passleisten sind {verfuegbar:.1f} mm. "
                f"Differenz {rest:+.1f} mm: einen Korpus ohne Breite anlegen oder Passleisten anpassen."
            )
        return [k.breite for k in z.korpusse]
    anteil = rest / len(offen)
    if anteil < regeln.min_breite:
        raise KorpusFehler(
            f"Für {len(offen)} Korpus(se) ohne feste Breite bleiben je {anteil:.1f} mm, "
            f"Mindestbreite ist {regeln.min_breite:.0f} mm."
        )
    return [anteil if k.breite is None else k.breite for k in z.korpusse]


class _Bau:
    def __init__(self, projekt: Projekt):
        self.p = projekt
        self.z = projekt.zeile
        self.r = projekt.regeln
        self.teile: list[Teil] = []
        self.beschlaege: list[Beschlag] = []

    def material(self, k: KorpusEingabe | None, teilname: str, rueckwand: bool = False) -> Material:
        schluessel = self.z.rueckwand if rueckwand else self.z.material
        if k is not None:
            if not rueckwand and k.material:
                schluessel = k.material
            schluessel = k.material_je_teil.get(teilname, schluessel)
        return self.p.materialien[schluessel]

    def teil(self, k, name, umriss, schnitte=None, hinweis="", rueckwand=False):
        korpus = k.name if k else "Zeile"
        schnitte = {kante: round(w, 2) for kante, w in (schnitte or {}).items() if w > EPS}
        self.teile.append(Teil(korpus, name, self.material(k, name, rueckwand), tuple(umriss), schnitte, hinweis))

    def obergrenze(self, k: KorpusEingabe) -> float:
        """Höchste zulässige Korpushöhe ohne Schräge."""
        grenze = self.p.raum.hoehe - self.z.passleiste_oben - self.z.sockel
        return min(grenze, k.hoehe) if k.hoehe is not None else grenze

    def pruefe_hoehe(self, k, hoehe):
        if hoehe < self.r.min_hoehe:
            raise KorpusFehler(
                f"{k.name}: Korpushöhe {hoehe:.0f} mm liegt unter der Mindesthöhe {self.r.min_hoehe:.0f} mm. "
                "Passleiste, Sockel oder Position ändern."
            )

    # ---- gerade Decke oder seitliche Schräge -------------------------------

    def seitlich(self, k: KorpusEingabe, x0: float, breite: float) -> KorpusMass:
        z, r, raum = self.z, self.r, self.p.raum
        x1 = x0 + breite
        grenze = self.obergrenze(k)

        def f(x):
            return min(raum.hoehe_bei(x) - z.passleiste_oben - z.sockel, grenze)

        hl, hr = f(x0), f(x1)
        for i in range(1, 32):
            x = x0 + breite * i / 32
            if abs(f(x) - (hl + (hr - hl) * i / 32)) > 0.01:
                raise KorpusFehler(
                    f"{k.name} (x = {x0:.0f} bis {x1:.0f} mm): Die Oberkante hätte einen Knick, weil die Schräge "
                    "innerhalb des Korpus die Decke oder die Korpushöhe erreicht. Korpusteilung an den Knick legen "
                    "(feste Breiten vergeben)."
                )
        self.pruefe_hoehe(k, min(hl, hr))

        t = self.material(k, "Seite links").staerke
        steigung = (hr - hl) / breite
        winkel = math.degrees(math.atan(abs(steigung)))
        cos = math.cos(math.atan(steigung))
        innen = breite - 2 * t
        if innen <= 0:
            raise KorpusFehler(f"{k.name}: Breite {breite:.0f} mm ist kleiner als zwei Plattenstärken.")

        def linie(x):
            return hl + (x - x0) * steigung

        self.teil(k, "Seite links", _rechteck(max(hl, linie(x0 + t)), z.tiefe), {"oben": winkel})
        self.teil(k, "Seite rechts", _rechteck(max(hr, linie(x1 - t)), z.tiefe), {"oben": winkel})
        self.teil(k, "Boden", _rechteck(innen, z.tiefe))
        self.teil(
            k, "Deckel", _rechteck(innen / cos + t * abs(steigung), z.tiefe),
            {"links": winkel, "rechts": winkel}, "liegt in der Schräge" if winkel > EPS else "",
        )

        n = r.nut_tiefe
        w = innen + 2 * n

        def rw_hoehe(u):
            return linie(x0 + t - n + u) - (t - n) / cos - (t - n)

        self.teil(k, "Rückwand", ((0, 0), (w, 0), (w, rw_hoehe(w)), (0, rw_hoehe(0))), rueckwand=True)

        licht = min(linie(x0 + t), linie(x1 - t)) - t / cos - t
        self.ausstattung(k, innen, t, [(t + licht * (i + 1) / (k.einlegeboeden + 1), 0.0) for i in range(k.einlegeboeden)],
                         "unterhalb der niedrigen Seite verteilt" if winkel > EPS else "")
        return KorpusMass(k.name, x0, breite, hl, hr)

    # ---- Schräge an der Rückwand -------------------------------------------

    def hinten(self, k: KorpusEingabe, x0: float, breite: float) -> KorpusMass:
        z, r, s = self.z, self.r, self.p.raum.schraege
        T = z.tiefe
        grenze = self.obergrenze(k)
        start = s.kniestock - z.passleiste_oben - z.sockel   # Höhe an der Rückwand
        m = s.steigung
        winkel = s.neigung
        cos = math.cos(math.radians(winkel))

        def g(y):   # y = Abstand von der Rückwand
            return min(start + y * m, grenze)

        hinten, vorn = g(0), g(T)
        t = self.material(k, "Seite links").staerke
        self.pruefe_hoehe(k, vorn)
        if hinten < 3 * t:
            raise KorpusFehler(
                f"{k.name}: An der Rückwand bleiben nur {hinten:.0f} mm Höhe. Kniestock zu niedrig für "
                "diesen Sockel und diese Passleiste, oder den Schrank von der Wand abrücken."
            )
        innen = breite - 2 * t
        if innen <= 0:
            raise KorpusFehler(f"{k.name}: Breite {breite:.0f} mm ist kleiner als zwei Plattenstärken.")
        knick = (grenze - start) / m    # hier erreicht die Schräge die Korpusoberkante
        schraeg = knick > EPS
        flach = knick < T - EPS

        if not schraeg:
            seite = _rechteck(T, vorn)
        else:
            seite = [(0, 0), (T, 0), (T, vorn)] + ([(knick, grenze)] if flach else []) + [(0, hinten)]
        # Seitenumriss: erste Koordinate = Abstand von der Rückwand, zweite = Höhe
        self.teil(k, "Seite links", seite)
        self.teil(k, "Seite rechts", seite)
        self.teil(k, "Boden", _rechteck(innen, T))
        gehrung = winkel / 2 if (schraeg and flach) else 0
        if flach:
            self.teil(k, "Deckel", _rechteck(innen, T - max(knick, 0)), {"hinten": gehrung})
        if schraeg:
            self.teil(k, "Schrägdeckel", _rechteck(innen, min(knick, T) / cos),
                      {"vorn": gehrung, "hinten": winkel}, "liegt in der Schräge")
        n = r.nut_tiefe
        self.teil(k, "Rückwand", _rechteck(innen + 2 * n, hinten - (t - n) / cos - (t - n)), rueckwand=True)

        licht = vorn - 2 * t
        lagen = []
        for i in range(k.einlegeboeden):
            hoehe = t + licht * (i + 1) / (k.einlegeboeden + 1)
            # Unterseite des Schrägdeckels auf Höhe der Bodenoberkante
            verlust = max(0.0, (hoehe + t + t / cos - start) / m) if schraeg else 0.0
            lagen.append((hoehe, verlust))
        self.ausstattung(k, innen, t, lagen, "")
        return KorpusMass(k.name, x0, breite, vorn, vorn)

    # ---- gemeinsam ---------------------------------------------------------

    def ausstattung(self, k, innen, t, lagen, hinweis):
        z, r = self.z, self.r
        rueckwand = self.material(k, "Rückwand", rueckwand=True).staerke
        voll = z.tiefe - r.rueckwand_rueckstand - rueckwand - r.einlegeboden_ruecksprung
        for nummer, (hoehe, verlust) in enumerate(lagen, start=1):
            tiefe = min(voll, z.tiefe - verlust - r.einlegeboden_ruecksprung)
            if tiefe < 100:
                raise KorpusFehler(
                    f"{k.name}: Einlegeboden {nummer} auf {hoehe:.0f} mm hätte unter der Schräge nur "
                    f"{tiefe:.0f} mm Tiefe. Weniger Einlegeböden wählen."
                )
            text = f"Unterkante auf {hoehe:.0f} mm"
            if tiefe < voll - EPS:
                text += ", stößt hinten an die Schräge"
            if hinweis:
                text += ", " + hinweis
            self.teil(k, f"Einlegeboden {nummer}", _rechteck(innen - 2 * r.einlegeboden_luft, tiefe), hinweis=text)
        if k.kleiderstange:
            self.beschlaege.append(Beschlag(k.name, "Kleiderstange", innen))
            self.beschlaege.append(Beschlag(k.name, "Stangenlager", None, 2))
        if k.einlegeboeden:
            self.beschlaege.append(Beschlag(k.name, "Bodenträger", None, 4 * k.einlegeboeden))

    def blenden(self, massen: list[KorpusMass]):
        z, raum = self.z, self.p.raum
        a, b = z.passleiste_links, raum.breite - z.passleiste_rechts
        seitlich = raum.schraege is not None and raum.schraege.richtung != "hinten"
        for name, breite, xa, km in (
            ("Passleiste links", z.passleiste_links, 0.0, massen[0]),
            ("Passleiste rechts", z.passleiste_rechts, b, massen[-1]),
        ):
            if breite <= 0:
                continue
            if seitlich:
                umriss = ((0, 0), (breite, 0), (breite, raum.hoehe_bei(xa + breite)), (0, raum.hoehe_bei(xa)))
            else:
                umriss = _rechteck(breite, km.hoehe_links + z.sockel + z.passleiste_oben)
            self.teil(None, name, umriss, hinweis="vor Ort anpassen")
        if z.passleiste_oben > 0:
            punkte = [a, b]
            if seitlich and raum.knick() is not None and a < raum.knick() < b:
                punkte.insert(1, raum.knick())
            for nummer, (xa, xb) in enumerate(zip(punkte, punkte[1:]), start=1):
                laenge = math.hypot(xb - xa, raum.hoehe_bei(xb) - raum.hoehe_bei(xa)) if seitlich else xb - xa
                name = "Passleiste oben" + (f" {nummer}" if len(punkte) > 2 else "")
                self.teil(None, name, _rechteck(laenge, z.passleiste_oben), hinweis="vor Ort anpassen")
        if z.sockel > 0:
            self.teil(None, "Sockelblende", _rechteck(b - a, z.sockel))


def erzeuge(projekt: Projekt) -> Ergebnis:
    bau = _Bau(projekt)
    schraege = projekt.raum.schraege
    methode = bau.hinten if schraege is not None and schraege.richtung == "hinten" else bau.seitlich
    x = projekt.zeile.passleiste_links
    massen = []
    for k, breite in zip(projekt.zeile.korpusse, verteile_breiten(projekt)):
        massen.append(methode(k, x, breite))
        x += breite
    bau.blenden(massen)
    return Ergebnis(massen, bau.teile, bau.beschlaege)
