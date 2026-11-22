"""Kernlogik: Wochenplan erzeugen, speichern, laden und exportieren."""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

from .uebungen import HALTEUEBUNGEN, TAGESTYPEN, UEBUNGEN, verfuegbare_uebungen

WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

ZIELE = {
    "muskelaufbau": "Muskelaufbau",
    "abnehmen": "Abnehmen",
    "ausdauer": "Ausdauer",
    "fitness": "Allgemeine Fitness",
}
NIVEAUS = {"anfaenger": "Anfänger", "fortgeschritten": "Fortgeschritten"}
AUSRUESTUNGEN = {"koerper": "Nur Körpergewicht", "studio": "Fitnessstudio"}

RUHETAG = "Ruhetag"
CARDIO = "Cardio"

# An welchen Wochentagen (Index 0 = Montag) bei X Trainingstagen trainiert wird.
# Die Tage sind so verteilt, dass möglichst Pausen dazwischen liegen.
TRAININGSTAGE_INDEX = {
    1: [2],
    2: [0, 3],
    3: [0, 2, 4],
    4: [0, 1, 3, 4],
    5: [0, 1, 2, 4, 5],
    6: [0, 1, 2, 3, 4, 5],
    7: [0, 1, 2, 3, 4, 5, 6],
}

# (Sätze Anfänger, Sätze Fortgeschritten, Wiederholungen, Pause in Sekunden)
INTENSITAET = {
    "muskelaufbau": (3, 4, "8–12", 90),
    "abnehmen": (3, 4, "12–15", 45),
    "ausdauer": (2, 3, "15–20", 30),
    "fitness": (3, 3, "10–12", 60),
}


@dataclass
class PlanUebung:
    name: str
    saetze: int | None = None
    wiederholungen: str | None = None
    pause_sek: int | None = None
    dauer_min: int | None = None

    def beschreibung(self) -> str:
        if self.dauer_min is not None:
            return f"{self.name}: {self.dauer_min} Min"
        return f"{self.name}: {self.saetze} × {self.wiederholungen}, {self.pause_sek} s Pause"


@dataclass
class Trainingstag:
    wochentag: str
    typ: str
    uebungen: list[PlanUebung] = field(default_factory=list)
    erledigt: bool = False
    notiz: str = ""

    @property
    def ist_ruhetag(self) -> bool:
        return self.typ == RUHETAG


@dataclass
class Wochenplan:
    ziel: str
    niveau: str
    tage_pro_woche: int
    ausruestung: str
    erstellt_am: str
    tage: list[Trainingstag]

    # ---------- Fortschritt ----------

    def trainingstage(self) -> list[Trainingstag]:
        return [t for t in self.tage if not t.ist_ruhetag]

    def fortschritt(self) -> tuple[int, int]:
        """(erledigte Einheiten, geplante Einheiten)"""
        training = self.trainingstage()
        return sum(t.erledigt for t in training), len(training)

    def tag(self, wochentag: str) -> Trainingstag:
        for t in self.tage:
            if t.wochentag.lower() == wochentag.lower():
                return t
        raise KeyError(f"Unbekannter Wochentag: {wochentag}")

    # ---------- Darstellung ----------

    def kopfzeile(self) -> str:
        return (
            f"Ziel: {ZIELE[self.ziel]} | Niveau: {NIVEAUS[self.niveau]} | "
            f"{self.tage_pro_woche} Trainingstage | {AUSRUESTUNGEN[self.ausruestung]}"
        )

    def als_text(self) -> str:
        erledigt, gesamt = self.fortschritt()
        zeilen = [
            "=" * 60,
            "  FITNESS-WOCHENPLAN",
            "=" * 60,
            self.kopfzeile(),
            f"Erstellt am: {self.erstellt_am} | Fortschritt: {erledigt}/{gesamt} {fortschrittsbalken(erledigt, gesamt)}",
            "",
        ]
        for t in self.tage:
            haken = "✔" if t.erledigt else ("·" if t.ist_ruhetag else "☐")
            zeilen.append(f"{haken} {t.wochentag:<10} – {t.typ}")
            for u in t.uebungen:
                zeilen.append(f"      • {u.beschreibung()}")
            if t.notiz:
                zeilen.append(f"      📝 {t.notiz}")
            zeilen.append("")
        return "\n".join(zeilen).rstrip() + "\n"

    def als_markdown(self) -> str:
        erledigt, gesamt = self.fortschritt()
        zeilen = [
            "# Fitness-Wochenplan",
            "",
            f"**{self.kopfzeile()}**  ",
            f"Erstellt am {self.erstellt_am} · Fortschritt: {erledigt}/{gesamt}",
            "",
        ]
        for t in self.tage:
            haken = "x" if t.erledigt else " "
            if t.ist_ruhetag:
                zeilen.append(f"## {t.wochentag} – {t.typ} 😴")
            else:
                zeilen.append(f"## [{haken}] {t.wochentag} – {t.typ}")
                zeilen.append("")
                zeilen.append("| Übung | Sätze | Wdh / Dauer | Pause |")
                zeilen.append("|---|---|---|---|")
                for u in t.uebungen:
                    if u.dauer_min is not None:
                        zeilen.append(f"| {u.name} | – | {u.dauer_min} Min | – |")
                    else:
                        zeilen.append(f"| {u.name} | {u.saetze} | {u.wiederholungen} | {u.pause_sek} s |")
            if t.notiz:
                zeilen.append("")
                zeilen.append(f"> 📝 {t.notiz}")
            zeilen.append("")
        return "\n".join(zeilen)

    # ---------- Speichern / Laden ----------

    def als_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def aus_dict(cls, daten: dict) -> Wochenplan:
        tage = [
            Trainingstag(
                wochentag=t["wochentag"],
                typ=t["typ"],
                uebungen=[PlanUebung(**u) for u in t.get("uebungen", [])],
                erledigt=t.get("erledigt", False),
                notiz=t.get("notiz", ""),
            )
            for t in daten["tage"]
        ]
        return cls(
            ziel=daten["ziel"],
            niveau=daten["niveau"],
            tage_pro_woche=daten["tage_pro_woche"],
            ausruestung=daten["ausruestung"],
            erstellt_am=daten["erstellt_am"],
            tage=tage,
        )


def fortschrittsbalken(erledigt: int, gesamt: int, breite: int = 10) -> str:
    if gesamt == 0:
        return "[" + " " * breite + "]"
    voll = round(breite * erledigt / gesamt)
    return "[" + "█" * voll + "░" * (breite - voll) + "]"


# ---------- Plan-Erzeugung ----------


def waehle_split(tage: int, niveau: str) -> list[str]:
    """Welche Krafttrainings-Typen bei wie vielen Tagen sinnvoll sind."""
    if tage <= 2:
        return ["Ganzkörper"] * tage
    if tage == 3:
        if niveau == "anfaenger":
            return ["Ganzkörper"] * 3
        return ["Push", "Pull", "Beine"]
    if tage == 4:
        return ["Oberkörper", "Unterkörper", "Oberkörper", "Unterkörper"]
    if tage == 5:
        return ["Push", "Pull", "Beine", "Oberkörper", "Unterkörper"]
    # 6 oder 7 Tage
    split = ["Push", "Pull", "Beine", "Push", "Pull", "Beine"]
    return split + [CARDIO] * (tage - 6)


def tagestypen_fuer_ziel(ziel: str, tage: int, niveau: str) -> list[str]:
    """Passt den Kraft-Split an das Trainingsziel an."""
    if ziel == "ausdauer":
        # Abwechselnd Cardio und Ganzkörper, Cardio überwiegt.
        return [CARDIO if i % 2 == 0 else "Ganzkörper" for i in range(tage)]
    typen = waehle_split(tage, niveau)
    if ziel == "abnehmen" and tage >= 4:
        # Letzte Krafteinheit durch eine reine Cardio-Einheit ersetzen.
        typen[-1] = CARDIO
    return typen


def cardio_dauer(ziel: str, niveau: str) -> int:
    basis = 25 if niveau == "anfaenger" else 40
    if ziel == "ausdauer":
        basis += 15
    return basis


def erstelle_uebungen(typ: str, ziel: str, niveau: str, ausruestung: str, rng: random.Random) -> list[PlanUebung]:
    if typ == CARDIO:
        name = rng.choice(verfuegbare_uebungen("cardio", ausruestung))
        return [PlanUebung(name=name, dauer_min=cardio_dauer(ziel, niveau))]

    saetze_anf, saetze_fort, wdh, pause = INTENSITAET[ziel]
    saetze = saetze_anf if niveau == "anfaenger" else saetze_fort

    uebungen: list[PlanUebung] = []
    bereits_gewaehlt: set[str] = set()
    for gruppe in TAGESTYPEN[typ]:
        moeglich = [u for u in verfuegbare_uebungen(gruppe, ausruestung) if u not in bereits_gewaehlt]
        # Im Studio zuerst Geräteübungen nehmen, Körpergewicht nur als Ergänzung.
        bevorzugt = [u for u in moeglich if u in UEBUNGEN[gruppe]["studio"]]
        name = rng.choice(bevorzugt or moeglich)
        bereits_gewaehlt.add(name)
        wiederholungen = "30–60 s halten" if name in HALTEUEBUNGEN else f"{wdh} Wdh"
        uebungen.append(PlanUebung(name=name, saetze=saetze, wiederholungen=wiederholungen, pause_sek=pause))

    if ziel == "abnehmen":
        cardio = rng.choice(verfuegbare_uebungen("cardio", ausruestung))
        uebungen.append(PlanUebung(name=f"Cardio-Finisher: {cardio}", dauer_min=15))
    return uebungen


def erstelle_plan(
    ziel: str,
    niveau: str,
    tage_pro_woche: int,
    ausruestung: str,
    seed: int | None = None,
    heute: date | None = None,
) -> Wochenplan:
    """Erzeugt einen kompletten Wochenplan (Montag bis Sonntag)."""
    if ziel not in ZIELE:
        raise ValueError(f"Unbekanntes Ziel: {ziel}")
    if niveau not in NIVEAUS:
        raise ValueError(f"Unbekanntes Niveau: {niveau}")
    if ausruestung not in AUSRUESTUNGEN:
        raise ValueError(f"Unbekannte Ausrüstung: {ausruestung}")
    if tage_pro_woche not in TRAININGSTAGE_INDEX:
        raise ValueError("Trainingstage pro Woche müssen zwischen 1 und 7 liegen.")

    rng = random.Random(seed)
    typen = tagestypen_fuer_ziel(ziel, tage_pro_woche, niveau)
    index_zu_typ = dict(zip(TRAININGSTAGE_INDEX[tage_pro_woche], typen))

    tage = []
    for i, name in enumerate(WOCHENTAGE):
        typ = index_zu_typ.get(i, RUHETAG)
        uebungen = [] if typ == RUHETAG else erstelle_uebungen(typ, ziel, niveau, ausruestung, rng)
        tage.append(Trainingstag(wochentag=name, typ=typ, uebungen=uebungen))

    return Wochenplan(
        ziel=ziel,
        niveau=niveau,
        tage_pro_woche=tage_pro_woche,
        ausruestung=ausruestung,
        erstellt_am=(heute or date.today()).isoformat(),
        tage=tage,
    )


def speichern(plan: Wochenplan, pfad: str | Path) -> None:
    Path(pfad).write_text(json.dumps(plan.als_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def laden(pfad: str | Path) -> Wochenplan:
    return Wochenplan.aus_dict(json.loads(Path(pfad).read_text(encoding="utf-8")))
