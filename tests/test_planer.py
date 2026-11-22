from datetime import date

import pytest

from fitnessplaner import planer
from fitnessplaner.planer import CARDIO, RUHETAG, WOCHENTAGE, erstelle_plan
from fitnessplaner.uebungen import UEBUNGEN


@pytest.mark.parametrize("ziel", list(planer.ZIELE))
@pytest.mark.parametrize("niveau", list(planer.NIVEAUS))
@pytest.mark.parametrize("ausruestung", list(planer.AUSRUESTUNGEN))
@pytest.mark.parametrize("tage", range(1, 8))
def test_jede_kombination_ergibt_gueltigen_plan(ziel, niveau, ausruestung, tage):
    plan = erstelle_plan(ziel, niveau, tage, ausruestung, seed=1)

    assert [t.wochentag for t in plan.tage] == WOCHENTAGE
    assert len(plan.trainingstage()) == tage
    for t in plan.tage:
        if t.ist_ruhetag:
            assert t.uebungen == []
        else:
            assert t.uebungen, f"{t.wochentag} hat keine Übungen"
            namen = [u.name for u in t.uebungen]
            assert len(namen) == len(set(namen)), "Übung doppelt am selben Tag"


def test_koerpergewicht_plan_nutzt_keine_geraete():
    studio_uebungen = {u for gruppe in UEBUNGEN.values() for u in gruppe["studio"]}
    plan = erstelle_plan("muskelaufbau", "fortgeschritten", 6, "koerper", seed=3)
    for t in plan.trainingstage():
        for u in t.uebungen:
            assert u.name not in studio_uebungen


def test_trainingstage_sind_verteilt():
    plan = erstelle_plan("fitness", "anfaenger", 3, "koerper", seed=0)
    assert [t.wochentag for t in plan.trainingstage()] == ["Montag", "Mittwoch", "Freitag"]
    assert plan.tag("Dienstag").typ == RUHETAG


def test_fortgeschritten_3_tage_bekommt_push_pull_beine():
    plan = erstelle_plan("muskelaufbau", "fortgeschritten", 3, "studio", seed=0)
    assert [t.typ for t in plan.trainingstage()] == ["Push", "Pull", "Beine"]
    assert all(u.saetze == 4 for t in plan.trainingstage() for u in t.uebungen)


def test_abnehmen_hat_cardio_finisher_und_cardio_tag():
    plan = erstelle_plan("abnehmen", "anfaenger", 4, "studio", seed=0)
    typen = [t.typ for t in plan.trainingstage()]
    assert typen[-1] == CARDIO
    for t in plan.trainingstage()[:-1]:
        assert t.uebungen[-1].name.startswith("Cardio-Finisher")


def test_ausdauer_hat_ueberwiegend_cardio():
    plan = erstelle_plan("ausdauer", "anfaenger", 3, "koerper", seed=0)
    typen = [t.typ for t in plan.trainingstage()]
    assert typen.count(CARDIO) == 2


def test_gleicher_seed_gleicher_plan():
    a = erstelle_plan("fitness", "anfaenger", 3, "studio", seed=42, heute=date(2026, 1, 1))
    b = erstelle_plan("fitness", "anfaenger", 3, "studio", seed=42, heute=date(2026, 1, 1))
    assert a == b


@pytest.mark.parametrize(
    "args",
    [
        ("schnell", "anfaenger", 3, "studio"),
        ("fitness", "profi", 3, "studio"),
        ("fitness", "anfaenger", 0, "studio"),
        ("fitness", "anfaenger", 8, "studio"),
        ("fitness", "anfaenger", 3, "garten"),
    ],
)
def test_ungueltige_eingaben(args):
    with pytest.raises(ValueError):
        erstelle_plan(*args)


def test_fortschritt():
    plan = erstelle_plan("fitness", "anfaenger", 3, "koerper", seed=0)
    assert plan.fortschritt() == (0, 3)
    plan.tag("montag").erledigt = True
    assert plan.fortschritt() == (1, 3)
    assert planer.fortschrittsbalken(1, 3) == "[███░░░░░░░]"


def test_speichern_und_laden(tmp_path):
    plan = erstelle_plan("abnehmen", "fortgeschritten", 5, "studio", seed=7)
    plan.tag("Montag").erledigt = True
    plan.tag("Montag").notiz = "Neuer Rekord beim Bankdrücken!"
    datei = tmp_path / "plan.json"

    planer.speichern(plan, datei)
    assert planer.laden(datei) == plan


def test_ausgabe_enthaelt_alle_tage():
    plan = erstelle_plan("muskelaufbau", "anfaenger", 3, "studio", seed=0)
    text = plan.als_text()
    markdown = plan.als_markdown()
    for name in WOCHENTAGE:
        assert name in text
        assert name in markdown
    assert "| Übung | Sätze |" in markdown


def test_studio_bevorzugt_geraeteuebungen():
    plan = erstelle_plan("muskelaufbau", "anfaenger", 3, "studio", seed=0)
    montag = [u.name for u in plan.tag("Montag").uebungen]
    for gruppe, name in zip(["beine", "brust", "ruecken", "schultern", "core"], montag):
        assert name in UEBUNGEN[gruppe]["studio"]


def test_plank_wird_gehalten():
    plan = erstelle_plan("fitness", "anfaenger", 7, "koerper", seed=0)
    planks = [u for t in plan.trainingstage() for u in t.uebungen if u.name == "Plank"]
    assert planks, "Seed liefert keinen Plank – Test anpassen"
    assert all(u.wiederholungen == "30–60 s halten" for u in planks)
