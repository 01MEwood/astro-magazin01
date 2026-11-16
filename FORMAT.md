# FORMAT.md – Aufbau der .hop-Dateien

Stand 16.11.2026. **Noch keine Beispieldateien vorhanden** (`samples/` ist leer).
Deshalb steht hier bisher keine einzige belegte Formatregel.

Regel für dieses Dokument: Jede Aussage über das Format braucht eine Belegstelle
(`Datei:Zeile`) aus `samples/`. Was sich nicht belegen lässt, bleibt "unklar" und
wird bei Mario nachgefragt. Es wird nicht geraten, auch nicht aus Vorwissen über
NC-HOPS.

## Belegt

Noch nichts.

## Unklar (wartet auf samples/)

| Thema | Frage | Status |
|---|---|---|
| Kodierung | ASCII, Windows-1252, UTF-8? Mit oder ohne BOM? | unklar |
| Zeilenenden | CRLF durchgehend? Umbruch nach der letzten Zeile? | unklar |
| Kopf | Welche Kopfzeilen gibt es, welche sind Pflicht, feste Reihenfolge? | unklar |
| Werkstück | Wo stehen Länge, Breite, Dicke, Material? | unklar |
| Variablen | Syntax, Datentypen, Dezimaltrennzeichen, Ausdrücke/Formeln | unklar |
| Bearbeitungen | Zeilentypen für Bohrung, Nut, Kontur; Parameterreihenfolge | unklar |
| Makroaufrufe | Aufrufsyntax, Parameterübergabe (Position oder Name) | unklar |
| Kommentare | Kommentarzeichen, Kommentare am Zeilenende | unklar |
| Groß/Klein | Ist das Format case-sensitiv? | unklar |
| Leerraum | Sind Einrückung und Leerzeichen bedeutungstragend? | unklar |
| Spiegeln LI/RE | Was ändert NC-HOPS beim Spiegeln in der Datei? | unklar |
| Nest | Aufbau eines Nest-Programms, Vorfräsen/Fertigfräsen | unklar |

## Was der Code heute schon zusichert (formatunabhängig)

Das ist keine Aussage über das HOP-Format, sondern über `hop/parser.py` und
`hop/writer.py`:

- Jede Datei wird bytegenau wieder geschrieben, egal was drinsteht
  (`tests/test_roundtrip.py`, auch mit allen 256 Bytewerten).
- Jede Zeile behält ihr eigenes Zeilenende (CRLF, LF, CR oder keines).
- Es wird keine Zeile gedeutet, also auch keine verworfen.
- Kodierung wird in der Reihenfolge ASCII, UTF-8, Windows-1252, Latin-1 versucht.
  Das dient nur dem Lesen als Text; welche Kodierung NC-HOPS erwartet, ist oben
  als unklar geführt.

## Vorgehen, sobald Dateien da sind

```
python -m hop check samples    # Round-Trip je Datei
python -m hop stats samples    # Kodierung, Zeilenenden, Zeilenanfänge mit Belegstelle
```

`stats` liefert die Rohdaten für die Tabelle "Belegt". Besonders ergiebig sind
Paare (dieselbe Datei vor und nach genau einer Änderung in NC-HOPS).
