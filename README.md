# HOP-Werkzeug für Korpuswerk

Python-Werkzeug, das .hop-Dateien liest, schreibt und (später) aus
Korpuswerk-Bauteilen CNC-Programme für die Holzher-Nesting-CNC erzeugt.
Auftrag und Leitplanken: [AUFTRAG.md](AUFTRAG.md). Formatwissen: [FORMAT.md](FORMAT.md).

## Stand

| Stufe | Inhalt | Stand |
|---|---|---|
| 1 | Formatanalyse | wartet auf `samples/` |
| 2 | Parser/Writer | verlustfreie Ebene fertig, Round-Trip grün; Deutung der Zeilen folgt aus Stufe 1 |
| 3-6 | Modell, Postprozessor, Zwei-Gang-Nest, Serie | offen |

## Benutzung

```
pip install -e ".[dev]"
pytest
python -m hop check samples
python -m hop stats samples
```

## Sicherheit

Kein erzeugtes Programm geht ohne Simulation in NC-HOPS an die Maschine.
