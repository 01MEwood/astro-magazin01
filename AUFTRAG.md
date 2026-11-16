# Auftrag: HOP-Werkzeug für Korpuswerk

Übergabe an Claude Code. Stand 16.11.2026.

## Ziel

Ein eigenes Python-Werkzeug, das .hop-Dateien liest, schreibt und aus Korpuswerk-Bauteilen fertige CNC-Programme für die Holzher-Nesting-CNC erzeugt. Es ersetzt nicht NC-HOPS, sondern nimmt uns die Handarbeit davor ab. NC-HOPS und betterNEST bleiben für Simulation, Nesting und Maschinenübergabe im Einsatz.

## Leitplanke: Black-Box, kein Eingriff ins Programm

Reverse Engineering heißt hier ausschließlich: das Dateiformat aus unseren eigenen Dateien ableiten.

Erlaubt:
- eigene .hop-Dateien, eigene Makros und die Schnittstellenbeschreibung auswerten
- in NC-HOPS eine Datei gezielt ändern, speichern und den Unterschied in der Datei ansehen
- Herstellermakros (z.B. BN_NestKontur) aus erzeugten Programmen aufrufen

Nicht erlaubt:
- EXE, DLL oder andere Programmdateien von NC-HOPS/betterNEST dekompilieren, disassemblieren oder auslesen
- Lizenz- oder Dongle-Prüfung anfassen
- Inhalt von Herstellermakros nachbauen oder kopieren, sie werden nur aufgerufen
- Oberfläche oder Programmlogik von NC-HOPS nachbilden

Was sich aus den Beispieldateien nicht sicher ableiten lässt, wird in FORMAT.md als "unklar" markiert und bei Mario nachgefragt. Nicht raten.

## Eingangsmaterial (von Mario bereitzustellen)

```
samples/
  einfach/      3-5 Teile mit wenigen Bearbeitungen (Bohrung, Nut, Kontur)
  korpus/       ein kompletter Schrank, alle Teile
  nest/         ein Nest-Programm mit Vorfräsen/Fertigfräsen
  serie/        je eine LI- und RE-Platte aus der Wandverkleidung
  makros/       eigene Makros
  doku/         Schnittstellenbeschreibung
```

Hilfreich sind Paare: dieselbe Datei einmal vor und einmal nach einer einzelnen Änderung in NC-HOPS.

## Stufen

### 1. Formatanalyse
- Korpus aus samples/ einlesen, Zeilentypen und Aufbau erfassen (Kopf, Variablen, Bearbeitungen, Makroaufrufe, Kodierung, Zeilenenden)
- Ergebnis: FORMAT.md mit Belegstelle je Regel (Datei und Zeile)

### 2. Parser und Writer
- hop/parser.py und hop/writer.py
- Pflichttest: jede Beispieldatei einlesen und wieder schreiben, Ergebnis identisch zum Original (Round-Trip)
- Unbekannte Zeilen bleiben unverändert erhalten, nichts wird stillschweigend verworfen

### 3. Datenmodell
- Werkstück (Maße, Material, Dicke), Variablen, Bearbeitungen, Makroaufrufe mit Parametern
- Spiegeln LI/RE als Operation auf dem Modell

### 4. Postprozessor für Korpuswerk
- Eingang: Korpuswerk-Bauteil mit seinen Bearbeitungen
- Ausgang: eine .hop je Teil
- Prinzip aus Korpuswerk bleibt: Bearbeitungen hängen am Teil, die Rückwand bringt die Nut mit und gibt sie an die Gegenteile weiter
- Verbinder (Clamex, Cabineo) als Makroaufruf, Clamex 90° zur Gehrungsfläche

### 5. Zwei-Gang-Formatierung im Nest
- Gang 1 Vorfräsen: eigener Fräser, 1 mm Abstand zur Fertigkontur, 1 mm Restdicke stehen lassen, nicht durchfräsen
- Gang 2 Fertigfräsen: anderer Fräser, auf Fertigmaß und durch
- Werkzeugnummern, Vorschübe und Abstände in einer Konfigurationsdatei, nicht im Code

### 6. Serien-Ausspielung
- Aus einer Vorlage plus Tabelle (CSV) viele Programme erzeugen
- Referenzfall: Wandverkleidung, 40 Räume, LI/RE gespiegelt, je 5 Platten BL1-BL5

### 7. Später
- Viewer/Prüfansicht im Browser, Anbindung als MCP-Tool an Korpuswerk

## Abnahme und Sicherheit

- Kein erzeugtes Programm geht ohne Simulation in NC-HOPS an die Maschine
- Je Stufe ein Referenzteil: von Hand in NC-HOPS programmiert, gegen die erzeugte Datei verglichen (diff)
- Prüfungen im Code vor dem Schreiben: Bearbeitung innerhalb der Teilemaße, Tiefe kleiner oder gleich Dicke (außer bewusst durch), Werkzeug in der Konfiguration vorhanden
- Erstes echtes Teil auf Restmaterial fahren

## Technik

- Python, pytest, keine Abhängigkeit von NC-HOPS zur Laufzeit
- Struktur: hop/ (parser, writer, model), post/ (Korpuswerk-Anbindung), nest/ (Zwei-Gang), serie/, tests/, samples/
- Kleine Schritte, je Stufe ein Commit mit grünen Tests

## Offene Fragen an Mario

1. Liegt Korpuswerk in einem Git-Repo, in das das Werkzeug als Modul kommt, oder als eigenes Projekt?
2. Werkzeugnummern und Daten der beiden Fräser für Gang 1 und Gang 2?
3. Übergabe an betterNEST: Einzel-.hop je Teil oder fertiges Nest-Programm?
4. Welche eigenen Makros sind Pflicht für den ersten Schrank?

## Erster Arbeitsschritt für Claude Code

samples/ sichten, FORMAT.md anlegen, Parser/Writer bis zum grünen Round-Trip-Test bauen. Erst danach Stufe 4.
