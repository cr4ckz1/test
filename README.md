# 💪 Fitness-Wochenplaner

Ein Python-Programm für das Terminal, das dir einen persönlichen Trainingsplan
für eine Woche erstellt. Du kannst dort abhaken, welche Einheiten du schon gemacht hast.

## Funktionen

- **Persönlicher Plan** aus vier Angaben:
  - Ziel: Muskelaufbau, Abnehmen, Ausdauer oder allgemeine Fitness
  - Niveau: Anfänger oder Fortgeschritten
  - Ort: zu Hause (nur Körpergewicht) oder im Fitnessstudio
  - Trainingstage pro Woche: 1 bis 7
- **Passender Trainingsaufbau**: Ganzkörper, Oberkörper/Unterkörper oder Push/Pull/Beine,
  je nach Anzahl der Tage und Erfahrung. Dazu Cardio-Einheiten beim Ziel Abnehmen oder Ausdauer.
- **Sätze, Wiederholungen und Pausen** passend zum Ziel
- **Ruhetage** sind sinnvoll über die Woche verteilt
- **Fortschritt**: Einheiten abhaken, mit Fortschrittsbalken
- **Notizen** zu jedem Tag, z. B. Gewichte oder Rekorde
- **Automatisches Speichern** in `fitnessplan.json`
- **Export als Markdown**, z. B. zum Ausdrucken oder fürs Handy

Es werden keine zusätzlichen Pakete benötigt, nur Python 3.10 oder neuer.

## Starten

```bash
python3 -m fitnessplaner
```

Weitere Optionen:

```bash
python3 -m fitnessplaner --anzeigen          # gespeicherten Plan nur anzeigen
python3 -m fitnessplaner --datei mein.json   # andere Speicherdatei verwenden
```

## Beispiel

```
============================================================
  FITNESS-WOCHENPLAN
============================================================
Ziel: Muskelaufbau | Niveau: Anfänger | 3 Trainingstage | Fitnessstudio
Erstellt am: 2026-11-22 | Fortschritt: 1/3 [███░░░░░░░]

✔ Montag     – Ganzkörper
      • Beinpresse: 3 × 8–12 Wdh, 90 s Pause
      • Bankdrücken: 3 × 8–12 Wdh, 90 s Pause
      ...
· Dienstag   – Ruhetag
```

## Tests

```bash
pip install pytest
python3 -m pytest
```

## Projektstruktur

```
fitnessplaner/
├── uebungen.py   # Übungsdatenbank und Trainingstypen
├── planer.py     # Plan erzeugen, speichern, laden, exportieren
├── cli.py        # Interaktives Menü
└── __main__.py   # Startpunkt für "python -m fitnessplaner"
tests/
└── test_planer.py
```

Eigene Übungen kannst du einfach in `fitnessplaner/uebungen.py` ergänzen.

---

# 📱 Trainingsplan – Web-App fürs Handy

Im Ordner [`docs/`](docs/) liegt eine einfache Web-App, mit der du planst,
**an welchen Tagen und um wie viel Uhr** du trainierst. Du kannst sie auf den Home-Bildschirm legen.

- Wochentage per Schalter an- und ausschalten, jeweils mit Uhrzeit und Dauer
- Anzeige des nächsten Trainings mit Countdown
- Übersicht: wie oft pro Woche und wie viele Stunden insgesamt
- „In Kalender eintragen“: wöchentliche Termine mit Erinnerung 30 Minuten vorher (.ics-Datei)
- Funktioniert offline, die Daten bleiben nur auf deinem Gerät
- Heller und dunkler Modus

Es gibt keine Abhängigkeiten. Die App besteht nur aus HTML, CSS und JavaScript.

**Lokal ausprobieren:** `cd docs && python3 -m http.server`, danach http://localhost:8000 öffnen.
