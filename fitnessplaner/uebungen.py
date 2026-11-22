"""Übungsdatenbank, sortiert nach Muskelgruppe und benötigter Ausrüstung.

"koerper" = nur Körpergewicht (zu Hause machbar)
"studio"  = Geräte/Hanteln im Fitnessstudio
Wer im Studio trainiert, kann zusätzlich alle Körpergewichtsübungen nutzen.
"""

UEBUNGEN: dict[str, dict[str, list[str]]] = {
    "beine": {
        "koerper": ["Kniebeugen", "Ausfallschritte", "Glute Bridge", "Bulgarian Split Squats"],
        "studio": ["Kniebeuge mit Langhantel", "Beinpresse", "Rumänisches Kreuzheben", "Beinbeuger an der Maschine"],
    },
    "brust": {
        "koerper": ["Liegestütze", "Schräge Liegestütze (Füße erhöht)", "Breite Liegestütze"],
        "studio": ["Bankdrücken", "Schrägbankdrücken mit Kurzhanteln", "Butterfly an der Maschine"],
    },
    "ruecken": {
        "koerper": ["Klimmzüge", "Tischrudern (Australian Pull-ups)", "Superman"],
        "studio": ["Latzug", "Rudern am Kabel", "Einarmiges Kurzhantelrudern"],
    },
    "schultern": {
        "koerper": ["Pike Push-ups", "Y-T-W-Heben", "Handstand an der Wand"],
        "studio": ["Schulterdrücken mit Kurzhanteln", "Seitheben", "Face Pulls"],
    },
    "bizeps": {
        "koerper": ["Chin-ups (Untergriff-Klimmzüge)", "Handtuch-Curls"],
        "studio": ["Kurzhantel-Curls", "Hammer Curls"],
    },
    "trizeps": {
        "koerper": ["Dips am Stuhl", "Diamond-Liegestütze"],
        "studio": ["Trizepsdrücken am Kabel", "French Press"],
    },
    "core": {
        "koerper": ["Plank", "Mountain Climbers", "Russian Twists", "Beinheben im Liegen"],
        "studio": ["Cable Crunches", "Hängendes Beinheben"],
    },
    "cardio": {
        "koerper": ["Joggen", "Seilspringen", "Burpee-Intervalle (HIIT)", "Zügiges Gehen"],
        "studio": ["Laufband", "Rudergerät", "Crosstrainer", "Fahrrad-Ergometer"],
    },
}

# Welche Muskelgruppen an welchem Trainingstyp trainiert werden.
# Kommt eine Gruppe mehrfach vor, werden verschiedene Übungen gewählt.
TAGESTYPEN: dict[str, list[str]] = {
    "Ganzkörper": ["beine", "brust", "ruecken", "schultern", "core"],
    "Oberkörper": ["brust", "ruecken", "schultern", "bizeps", "trizeps"],
    "Unterkörper": ["beine", "beine", "beine", "core"],
    "Push": ["brust", "brust", "schultern", "trizeps"],
    "Pull": ["ruecken", "ruecken", "bizeps", "core"],
    "Beine": ["beine", "beine", "beine", "core"],
}


# Übungen, die gehalten statt wiederholt werden.
HALTEUEBUNGEN = {"Plank", "Handstand an der Wand"}


def verfuegbare_uebungen(gruppe: str, ausruestung: str) -> list[str]:
    """Alle Übungen einer Muskelgruppe, die mit der Ausrüstung machbar sind."""
    if gruppe not in UEBUNGEN:
        raise ValueError(f"Unbekannte Muskelgruppe: {gruppe}")
    if ausruestung == "koerper":
        return list(UEBUNGEN[gruppe]["koerper"])
    if ausruestung == "studio":
        return UEBUNGEN[gruppe]["studio"] + UEBUNGEN[gruppe]["koerper"]
    raise ValueError(f"Unbekannte Ausrüstung: {ausruestung}")
