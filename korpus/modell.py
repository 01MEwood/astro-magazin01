from __future__ import annotations

import math
from dataclasses import dataclass, field

Punkt = tuple[float, float]


class KorpusFehler(ValueError):
    """Eingabe lässt sich nicht bauen; die Meldung sagt, was zu ändern ist."""


@dataclass(frozen=True)
class Schraege:
    richtung: str      # "links"/"rechts": niedrige Seite an dieser Wand; "hinten": Schräge an der Rückwand
    kniestock: float   # Höhe der Schräge an der Wand
    neigung: float     # Grad gegen die Waagerechte

    @property
    def steigung(self) -> float:
        return math.tan(math.radians(self.neigung))


@dataclass(frozen=True)
class Raum:
    breite: float
    hoehe: float
    schraege: Schraege | None = None

    def hoehe_bei(self, x: float) -> float:
        """Raumhöhe an der Stelle x (von der linken Wand), bei seitlicher Schräge."""
        s = self.schraege
        if s is None or s.richtung == "hinten":
            return self.hoehe
        abstand = x if s.richtung == "links" else self.breite - x
        return min(self.hoehe, s.kniestock + abstand * s.steigung)

    def knick(self) -> float | None:
        """x, an dem die seitliche Schräge die Decke erreicht."""
        s = self.schraege
        if s is None or s.richtung == "hinten" or s.kniestock >= self.hoehe:
            return None
        abstand = (self.hoehe - s.kniestock) / s.steigung
        x = abstand if s.richtung == "links" else self.breite - abstand
        return x if 0 < x < self.breite else None


@dataclass(frozen=True)
class Material:
    schluessel: str
    name: str
    staerke: float


@dataclass(frozen=True)
class Regeln:
    nut_tiefe: float
    rueckwand_rueckstand: float
    einlegeboden_ruecksprung: float
    einlegeboden_luft: float
    min_breite: float
    min_hoehe: float


@dataclass
class KorpusEingabe:
    name: str
    breite: float | None = None    # None = teilt sich die Restbreite
    hoehe: float | None = None     # None = so hoch wie der Raum erlaubt
    einlegeboeden: int = 0
    kleiderstange: bool = False
    material: str | None = None
    material_je_teil: dict[str, str] = field(default_factory=dict)


@dataclass
class Zeile:
    tiefe: float
    material: str
    rueckwand: str
    passleiste_links: float = 0
    passleiste_rechts: float = 0
    passleiste_oben: float = 0
    sockel: float = 0
    korpusse: list[KorpusEingabe] = field(default_factory=list)


@dataclass
class Projekt:
    raum: Raum
    zeile: Zeile
    materialien: dict[str, Material]
    regeln: Regeln


@dataclass
class Teil:
    korpus: str
    name: str
    material: Material
    umriss: tuple[Punkt, ...]
    """Eckpunkte in der Plattenebene, Maße am längsten Punkt."""
    schraegschnitte: dict[str, float] = field(default_factory=dict)
    """Kante -> Winkel in Grad gegen den rechtwinkligen Schnitt."""
    hinweis: str = ""

    @property
    def laenge(self) -> float:
        return max(p[0] for p in self.umriss) - min(p[0] for p in self.umriss)

    @property
    def breite(self) -> float:
        return max(p[1] for p in self.umriss) - min(p[1] for p in self.umriss)

    @property
    def rechteckig(self) -> bool:
        ecken = {(round(x, 6), round(y, 6)) for x, y in self.umriss}
        return len(ecken) == 4 and len({x for x, _ in ecken}) == 2 and len({y for _, y in ecken}) == 2


@dataclass
class Beschlag:
    korpus: str
    name: str
    laenge: float | None = None
    anzahl: int = 1


@dataclass
class KorpusMass:
    name: str
    x: float
    breite: float
    hoehe_links: float
    hoehe_rechts: float


@dataclass
class Ergebnis:
    korpusse: list[KorpusMass]
    teile: list[Teil]
    beschlaege: list[Beschlag]
