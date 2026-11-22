"""Interaktives Menü im Terminal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import planer
from .planer import AUSRUESTUNGEN, NIVEAUS, ZIELE, Wochenplan

STANDARD_DATEI = "fitnessplan.json"


class Abbruch(Exception):
    """Wird ausgelöst, wenn der Nutzer die Eingabe abbricht (Strg+C / Strg+D)."""


def eingabe(frage: str) -> str:
    try:
        return input(frage).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        raise Abbruch from None


def auswahl(frage: str, optionen: dict[str, str]) -> str:
    """Zeigt nummerierte Optionen und gibt den Schlüssel der Wahl zurück."""
    schluessel = list(optionen)
    print(f"\n{frage}")
    for nr, k in enumerate(schluessel, start=1):
        print(f"  {nr}) {optionen[k]}")
    while True:
        antwort = eingabe("Deine Wahl: ")
        if antwort.isdigit() and 1 <= int(antwort) <= len(schluessel):
            return schluessel[int(antwort) - 1]
        print(f"Bitte eine Zahl zwischen 1 und {len(schluessel)} eingeben.")


def zahl(frage: str, minimum: int, maximum: int) -> int:
    while True:
        antwort = eingabe(f"{frage} ({minimum}–{maximum}): ")
        if antwort.isdigit() and minimum <= int(antwort) <= maximum:
            return int(antwort)
        print(f"Bitte eine Zahl zwischen {minimum} und {maximum} eingeben.")


def waehle_trainingstag(plan: Wochenplan):
    training = plan.trainingstage()
    optionen = {
        t.wochentag: f"{t.wochentag} – {t.typ} {'✔' if t.erledigt else ''}".rstrip() for t in training
    }
    return plan.tag(auswahl("Welcher Tag?", optionen))


def neuer_plan() -> Wochenplan:
    print("\n--- Neuen Wochenplan erstellen ---")
    ziel = auswahl("Was ist dein Trainingsziel?", ZIELE)
    niveau = auswahl("Wie erfahren bist du?", NIVEAUS)
    ausruestung = auswahl("Wo trainierst du?", AUSRUESTUNGEN)
    tage = zahl("\nWie viele Tage pro Woche möchtest du trainieren?", 1, 7)
    if tage == 7:
        print("Hinweis: Ohne Ruhetag fehlt die Erholung – 3 bis 5 Tage sind meist optimal.")
    return planer.erstelle_plan(ziel, niveau, tage, ausruestung)


def lade_plan(pfad: Path) -> Wochenplan | None:
    if not pfad.exists():
        return None
    try:
        return planer.laden(pfad)
    except (json.JSONDecodeError, KeyError, TypeError) as fehler:
        print(f"Warnung: {pfad} konnte nicht gelesen werden ({fehler}). Starte ohne Plan.")
        return None


def hauptmenue(pfad: Path) -> None:
    plan = lade_plan(pfad)
    print("💪 Willkommen beim Fitness-Wochenplaner!")
    if plan:
        print(f"Gespeicherter Plan aus {pfad} geladen.")

    while True:
        optionen = {"neu": "Neuen Wochenplan erstellen"}
        if plan:
            optionen |= {
                "anzeigen": "Plan anzeigen",
                "erledigt": "Training als erledigt markieren / zurücksetzen",
                "notiz": "Notiz zu einem Tag speichern",
                "reset": "Neue Woche starten (Haken zurücksetzen)",
                "export": "Als Markdown-Datei exportieren",
            }
        optionen["ende"] = "Beenden"

        try:
            wahl = auswahl("Was möchtest du tun?", optionen)
        except Abbruch:
            wahl = "ende"
        if wahl == "ende":
            print("Bis zum nächsten Training! 👋")
            return

        try:
            if wahl == "neu":
                if plan and auswahl("Den bestehenden Plan überschreiben?", {"ja": "Ja", "nein": "Nein"}) == "nein":
                    continue
                plan = neuer_plan()
                print("\n" + plan.als_text())
            elif wahl == "anzeigen":
                print("\n" + plan.als_text())
            elif wahl == "erledigt":
                tag = waehle_trainingstag(plan)
                tag.erledigt = not tag.erledigt
                erledigt, gesamt = plan.fortschritt()
                status = "erledigt ✔" if tag.erledigt else "offen"
                print(f"{tag.wochentag} ist jetzt {status}. Fortschritt: {erledigt}/{gesamt}")
                if erledigt == gesamt:
                    print("🎉 Alle Einheiten dieser Woche geschafft – stark!")
            elif wahl == "notiz":
                tag = waehle_trainingstag(plan)
                tag.notiz = eingabe("Notiz (leer lassen zum Löschen): ")
                print("Notiz gespeichert.")
            elif wahl == "reset":
                for t in plan.tage:
                    t.erledigt = False
                print("Alle Haken zurückgesetzt – auf in die neue Woche!")
            elif wahl == "export":
                ziel = pfad.with_suffix(".md")
                ziel.write_text(plan.als_markdown(), encoding="utf-8")
                print(f"Exportiert nach {ziel}")
        except Abbruch:
            print("Abgebrochen – zurück zum Menü.")
            continue

        if plan:
            planer.speichern(plan, pfad)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Fitness-Trainingswochenplaner")
    parser.add_argument("--datei", default=STANDARD_DATEI, help=f"Speicherdatei (Standard: {STANDARD_DATEI})")
    parser.add_argument("--anzeigen", action="store_true", help="Gespeicherten Plan nur anzeigen und beenden")
    args = parser.parse_args(argv)
    pfad = Path(args.datei)

    if args.anzeigen:
        plan = lade_plan(pfad)
        print(plan.als_text() if plan else f"Kein Plan in {pfad} gefunden.")
        return
    hauptmenue(pfad)
