import math
from pathlib import Path

import pytest

from korpus import KorpusFehler, erzeuge, lade_projekt
from korpus.__main__ import main
from korpus.generator import verteile_breiten

BEISPIELE = Path(__file__).parent.parent / "beispiele"
KOPF = '[zeile]\ntiefe = 600\nmaterial = "weiss19"\nrueckwand = "hdf8"\n'


def projekt(tmp_path, text):
    pfad = tmp_path / "p.toml"
    pfad.write_text(text, encoding="utf-8")
    return lade_projekt(pfad)


def teil(ergebnis, korpus, name):
    return next(t for t in ergebnis.teile if t.korpus.startswith(korpus) and t.name == name)


def test_gerader_raum(tmp_path):
    p = projekt(tmp_path, "[raum]\nbreite = 2000\nhoehe = 2400\n" + KOPF
                + "passleiste_links = 50\npassleiste_rechts = 50\nsockel = 100\n"
                + "[[korpus]]\nbreite = 700\n[[korpus]]\n[[korpus]]\neinlegeboeden = 1\n")
    assert verteile_breiten(p) == [700, 600, 600]
    e = erzeuge(p)
    seite, boden, rueckwand, eb = (teil(e, "K3", n) for n in ("Seite links", "Boden", "Rückwand", "Einlegeboden 1"))
    assert (seite.laenge, seite.breite, seite.schraegschnitte) == (2300, 600, {})
    assert (boden.laenge, boden.breite) == (600 - 38, 600)
    assert (rueckwand.laenge, rueckwand.breite) == (562 + 16, 2300 - 2 * 11)
    assert (eb.laenge, eb.breite) == (562 - 2, 600 - 20 - 8 - 20)
    assert rueckwand.material.staerke == 8
    assert teil(e, "Zeile", "Sockelblende").laenge == 1900
    assert all(t.rechteckig for t in e.teile)


def test_seitliche_schraege():
    e = erzeuge(lade_projekt(BEISPIELE / "dachschraege.toml"))
    k1 = e.korpusse[0]
    assert (k1.hoehe_links, k1.hoehe_rechts) == pytest.approx((940, 1620))
    assert teil(e, "K1", "Seite links").laenge == pytest.approx(940 + 19)   # langer Punkt innen
    assert teil(e, "K1", "Seite rechts").laenge == pytest.approx(1620)      # langer Punkt außen
    deckel = teil(e, "K1", "Deckel")
    assert deckel.laenge == pytest.approx(642 * math.sqrt(2) + 19)
    assert deckel.schraegschnitte == {"links": 45, "rechts": 45}
    assert not teil(e, "K1", "Rückwand").rechteckig
    assert e.korpusse[2].hoehe_links == e.korpusse[2].hoehe_rechts == 2300
    assert sum(k.breite for k in e.korpusse) == pytest.approx(4000 - 80)
    assert teil(e, "K4", "Boden").material.schluessel == "eiche19"
    assert teil(e, "K5", "Seite rechts").material.schluessel == "eiche19"
    assert teil(e, "K5", "Seite links").material.schluessel == "weiss19"


def test_schraege_rechts_ist_spiegelbild(tmp_path):
    text = (BEISPIELE / "dachschraege.toml").read_text(encoding="utf-8")
    kopf, *korpusse = text.split("[[korpus]]")
    gespiegelt = kopf.replace('"links"', '"rechts"', 1) + "".join("[[korpus]]" + k for k in reversed(korpusse))
    links = erzeuge(lade_projekt(BEISPIELE / "dachschraege.toml"))
    rechts = erzeuge(projekt(tmp_path, gespiegelt))
    assert teil(rechts, "K5", "Seite rechts").laenge == pytest.approx(teil(links, "K1", "Seite links").laenge)
    assert teil(rechts, "K5", "Deckel").laenge == pytest.approx(teil(links, "K1", "Deckel").laenge)


def test_schraege_hinten():
    e = erzeuge(lade_projekt(BEISPIELE / "kniestock.toml"))
    seite = teil(e, "K1", "Seite links")
    knick = (1400 - 800) / math.tan(math.radians(40))
    assert [c for punkt in seite.umriss for c in punkt] == pytest.approx([0, 0, 900, 0, 900, 1400, knick, 1400, 0, 800])
    assert teil(e, "K1", "Deckel").breite == pytest.approx(900 - knick)
    assert teil(e, "K1", "Schrägdeckel").breite == pytest.approx(knick / math.cos(math.radians(40)))
    assert teil(e, "K1", "Deckel").schraegschnitte == {"hinten": 20}
    unten, _, oben = (teil(e, "K1", f"Einlegeboden {i}") for i in (1, 2, 3))
    assert unten.breite == 900 - 20 - 8 - 20
    assert oben.breite < unten.breite and "Schräge" in oben.hinweis


@pytest.mark.parametrize(
    "text, meldung",
    [
        ("[raum]\nbreite = 1000\nhoehe = 2400\n" + KOPF + "[[korpus]]\nbreite = 900\n", r"Differenz \+100.0 mm"),
        ("[raum]\nbreite = 1000\nhoehe = 2400\n" + KOPF + "[[korpus]]\nbreite = 900\n[[korpus]]\n", "Mindestbreite"),
        ('[raum]\nbreite = 3000\nhoehe = 2400\n[raum.schraege]\nrichtung = "links"\nkniestock = 1000\nneigung = 45\n'
         + KOPF + "[[korpus]]\n", "Knick"),
        ('[raum]\nbreite = 3000\nhoehe = 2400\n[raum.schraege]\nrichtung = "links"\nkniestock = 100\nneigung = 45\n'
         + KOPF + "[[korpus]]\nbreite = 600\n[[korpus]]\nbreite = 1700\n[[korpus]]\n", "Mindesthöhe"),
        ('[raum]\nbreite = 1000\nhoehe = 2400\n[zeile]\ntiefe = 600\nmaterial = "gold"\nrueckwand = "hdf8"\n[[korpus]]\n',
         "'gold' steht nicht in der Bibliothek"),
        ("[raum]\nbreite = 1000\nhoehe = 2400\n" + KOPF + '[[korpus]]\ntyp = "Vitrine"\n', "Typ 'Vitrine'"),
        ("[raum]\nbreite = 1000\nhoehe = 2400\n" + KOPF + "[[korpus]]\nbriete = 5\n", "unbekannte Angabe briete"),
        ("[raum]\nbreite = -5\nhoehe = 2400\n" + KOPF + "[[korpus]]\n", "breite muss eine positive Zahl"),
        ("[raum]\nbreite = 1000\nhoehe = 2400\n" + KOPF, "keinen Korpus"),
    ],
)
def test_fehlermeldungen(tmp_path, text, meldung):
    with pytest.raises(KorpusFehler, match=meldung):
        erzeuge(projekt(tmp_path, text))


def test_cli(tmp_path, capsys):
    ziel = tmp_path / "teile.csv"
    assert main([str(BEISPIELE / "dachschraege.toml"), "--csv", str(ziel)]) == 0
    assert "K1 Regal" in capsys.readouterr().out
    zeilen = ziel.read_text(encoding="utf-8-sig").splitlines()
    assert zeilen[0].startswith("korpus;teil;laenge") and len(zeilen) == 43
    assert "959,0" in zeilen[1]
    assert main([str(tmp_path / "fehlt.toml")]) == 1
