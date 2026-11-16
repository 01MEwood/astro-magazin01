import pytest

from auswertung.__main__ import main
from auswertung.auswertung import EingabeFehler, auswerten

# Erfundene Zahlen, nur zum Prüfen der Rechnung.
AUFTRAEGE = "auftrag;bereich;soll_min;ist_min\nA1;CNC;60;90\nA1;Montage;120;120\nA2;CNC;;30,5\n"
VERLUSTE = (
    "auftrag;bereich;kategorie;minuten;ursache;notiz\n"
    "A1;CNC;suchen;20;Programm fehlt;\n"
    "A1;CNC;Nacharbeit;10;Programm fehlt;\n"
    "A3;Montage;Warten;30;Beschlag fehlt;\n"
)


def schreibe(tmp_path, auftraege=AUFTRAEGE, verluste=VERLUSTE, encoding="utf-8"):
    (tmp_path / "auftraege.csv").write_text(auftraege, encoding=encoding)
    if verluste is not None:
        (tmp_path / "verluste.csv").write_text(verluste, encoding=encoding)
    return tmp_path


def test_summen(tmp_path):
    out = auswerten(schreibe(tmp_path))
    assert "Aufträge: 2" in out
    assert "Ist-Zeit gesamt: 240 min" in out          # 90 + 120 + 30,5 gerundet
    assert "CNC                   60      90     +30    +50%" in out
    assert "(1 Zeilen ohne Soll-Zeit nicht verglichen)" in out
    assert "Verluste gesamt: 60 min (1.0 h) = 25% der Ist-Zeit" in out
    assert "30 min    50%  Programm fehlt (2x)" in out
    assert "ohne Zeile in auftraege.csv: A3" in out


def test_komma_als_trennzeichen_und_cp1252(tmp_path):
    out = auswerten(schreibe(tmp_path, "Auftrag,Bereich,Soll_min,Ist_min\nA1,Bankraum Süd,10,20\n", None, "cp1252"))
    assert "Bankraum Süd" in out and "Keine Verluste erfasst" in out


@pytest.mark.parametrize(
    "auftraege, verluste, text",
    [
        ("auftrag;bereich;ist_min\nA1;CNC;5\n", None, "Spalte fehlt: soll_min"),
        ("auftrag;bereich;soll_min;ist_min\nA1;CNC;1;abc\n", None, "auftraege.csv:2: ist_min ist keine Zahl"),
        ("auftrag;bereich;soll_min;ist_min\nA1;CNC;1;\n", None, "ist_min ist leer"),
        (AUFTRAEGE, "auftrag;bereich;kategorie;minuten;ursache\nA1;CNC;Pause;5;x\n", "unbekannte Kategorie 'Pause'"),
    ],
)
def test_fehler_mit_fundstelle(tmp_path, auftraege, verluste, text):
    with pytest.raises(EingabeFehler, match=text):
        auswerten(schreibe(tmp_path, auftraege, verluste))


def test_cli(tmp_path, capsys):
    assert main([str(schreibe(tmp_path))]) == 0
    assert main([str(tmp_path / "gibtsnicht")]) == 1
    assert main([]) == 2
