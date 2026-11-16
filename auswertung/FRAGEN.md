# Auftragsanalyse: Fragen und Unterlagen

Ziel: herausfinden, wo in der Fertigung Zeit liegen bleibt und welche
Vorbereitung aus der AV das verhindert hätte. Daraus folgt, welcher Teil der
Auftragsmappe zuerst gebaut wird.

## A. Was je Auftrag mitkommen sollte

Alles optional, aber je mehr, desto genauer. Kundendaten bitte schwärzen oder
weglassen, sie werden nicht gebraucht.

- [ ] Angebot oder Auftragsbestätigung (Positionen, Preis)
- [ ] Zeichnung oder Planung (PDF, Export aus dem CAD)
- [ ] Stückliste, Zuschnittliste, Kantenliste, Beschlagliste
- [ ] CNC-Programme (.hop) und, falls vorhanden, das Nest-Programm
- [ ] Vorkalkulation: geplante Stunden je Bereich
- [ ] Ist-Zeiten: Stundenzettel oder Zeiterfassung je Bereich
- [ ] Was die Werkstatt tatsächlich in die Hand bekommen hat (Foto der Mappe genügt)
- [ ] Reklamationen, Nacharbeit, Nachbestellungen zu diesem Auftrag

## B. Fragen je Auftrag

Kurz beantworten, Stichworte reichen. "Weiß ich nicht" ist eine gültige Antwort
und selbst ein Befund.

**Einordnung**
1. Welcher Möbeltyp, wie viele Korpusse, wie viele Teile ungefähr?
2. Standard oder Sonderbau? Was genau war das Besondere?
3. Wer hat geplant, wer hat gefertigt, wer montiert?

**Vorbereitung (AV)**
4. Wie lange hat die AV gedauert, und womit ging die meiste Zeit weg?
5. Welche Unterlagen wurden von Hand erstellt oder abgetippt?
6. Was wurde nach Fertigungsbeginn noch geändert, und warum?

**Fertigung**
7. An welcher Station stand der Auftrag am längsten, ohne dass gearbeitet wurde?
8. Welche Rückfragen kamen aus der Werkstatt? An wen, wie lange bis zur Antwort?
9. Was musste gesucht werden (Teile, Beschläge, Zeichnung, Programm, Werkzeug)?
10. Was wurde falsch oder doppelt gefertigt? Ursache?
11. Fehlte Material oder Beschlag bei Fertigungsbeginn?
12. Welche Bearbeitung wurde von Hand gemacht, obwohl die CNC sie könnte?

**Montage**
13. Was fehlte auf der Baustelle oder passte nicht?
14. Gab es eine zweite Anfahrt? Warum?

**Ergebnis**
15. Geplante gegen tatsächliche Stunden: wo liegt die größte Abweichung?
16. Welche eine Information hätte der Werkstatt am meisten geholfen?

## C. Fragen zum Betrieb (einmalig)

1. Welche Stationen gibt es, in welcher Reihenfolge läuft ein Auftrag?
2. Wie viele Mitarbeiter in der Fertigung, wie viele in der Montage?
3. Wie werden Zeiten heute erfasst (gar nicht, Zettel, Software)?
4. Wie erfährt ein Mitarbeiter morgens, was er als Nächstes tut?
5. Wie werden Teile nach der CNC wiedergefunden (Etikett, Beschriftung, gar nicht)?
6. Welche Konstruktionsregeln sind fest (Plattenstärken, Verbinder, Rückwand, Sockel)?
7. Welcher Anteil der Aufträge ist Standard, welcher Sonderbau (geschätzt)?
8. Was kann der digitale Werkstattleiter heute schon, und wer nutzt ihn?

## D. Erfassung für die Auswertung

Zwei Tabellen, Vorlagen liegen in `auswertung/vorlagen/`. In Excel ausfüllen und
als CSV speichern.

**auftraege.csv**, eine Zeile je Auftrag und Bereich:

| Spalte | Inhalt |
|---|---|
| auftrag | Auftragsnummer oder Kürzel |
| bereich | z. B. AV, Zuschnitt, CNC, Kante, Bankraum, Oberfläche, Montage |
| soll_min | geplante Minuten (leer, wenn nicht geplant) |
| ist_min | tatsächliche Minuten |

**verluste.csv**, eine Zeile je Vorfall:

| Spalte | Inhalt |
|---|---|
| auftrag | wie oben |
| bereich | wo es passiert ist |
| kategorie | Warten, Suchen, Nachfragen oder Nacharbeit |
| minuten | verlorene Zeit, geschätzt reicht |
| ursache | kurzes Stichwort, möglichst immer dasselbe Wort für dieselbe Ursache |
| notiz | frei |

Auswertung:

```
python -m auswertung <Ordner mit den beiden CSV-Dateien>
```

Sie zeigt Soll gegen Ist je Bereich, Verluste nach Kategorie, Bereich und
Ursache sowie den Anteil der Verluste an der Ist-Zeit.

## E. Was die Analyse beantworten soll

1. In welchem Bereich geht die meiste Zeit verloren?
2. Welche Verlustart überwiegt: Warten, Suchen, Nachfragen, Nacharbeit?
3. Welche drei Ursachen machen den größten Teil aus?
4. Welche davon hätte eine vollständige Auftragsmappe verhindert?
5. Wo weicht die Vorkalkulation am stärksten ab (Grundlage für spätere Zeitwerte)?
