"""Parametrischer Korpusgenerator: Raum + Schrankzeile -> Teile mit Maßen."""

from .generator import erzeuge
from .laden import lade_projekt
from .modell import KorpusFehler

__all__ = ["erzeuge", "lade_projekt", "KorpusFehler"]
