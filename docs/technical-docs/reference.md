---
title: Reference
parent: Technical Docs
nav_order: 3
---

{: .attention }
> Der Rest wird später gelöscht und dient jetzt als Vorlage und Orientierung

{: .label }
Ilja Makarchuk

{: .no_toc }
# Reference documentation

{: .attention }
> This page collects internal functions, routes with their functions, and APIs (if any).
> 
> See [Uber](https://developer.uber.com/docs/drivers/references/api) or [PayPal](https://developer.paypal.com/api/rest/) for exemplary high-quality API reference documentation.
>
> You may delete this `attention` box.

<details open markdown="block">
{: .text-delta }
<summary>Table of contents</summary>
+ ToC
{: toc }
</details>

## Modul-Selektion

### `module_selection()`

**Route:** `/module-selection`

**Methods:** `GET`

**Purpose:** Zeigt dem Benutzer alle verfügbaren Lernmodule an und verwaltet deren Freischaltungsstatus. Unterscheidet zwischen bereits freigeschalteten und noch gesperrten Modulen. Zeigt außerdem die verbleibenden kostenlosen Freischaltungen und den Punktestand an.

**Sample output:**

Verfügbare Module:
- VWL [Freigeschaltet]
- Rechnungswesen [Gesperrt]
Freie Freischaltungen: 2
Punktestand: 150

---

## Quiz

### `quiz()`

**Route:** `/quiz/<module>`

**Methods:** `GET` `POST`

**Purpose:** Implementiert das Quiz-Spiel für ein spezifisches Modul. Wählt zufällig eine Frage aus, verarbeitet die Benutzerantwort und aktualisiert den Punktestand (+10 für richtige, -5 für falsche Antworten oder Zeitablauf).

**Sample output:**

Frage: Was ist VWL?
A) Volkswirtschaftslehre
B) Versicherung und Leben
C) Verbrauchswirtschaft
Timer: 10s

---

## Definition-Spiel

### `definition_game()`

**Route:** `/definition-game/<module>`

**Methods:** `GET` `POST`

**Purpose:** Stellt ein Zuordnungsspiel bereit, bei dem Begriffe ihren korrekten Definitionen zugeordnet werden müssen. Bewertet die Antworten und vergibt Punkte basierend auf der Genauigkeit der Zuordnungen.

**Sample output:**

Begriffe:          Definitionen:
1. Angebot        [ ] Die Menge an Gütern, die Konsumenten kaufen möchten
2. Nachfrage      [ ] Die Menge an Gütern, die Produzenten verkaufen möchten
Timer: 20s
---

## Test-Anzeige

### `show_test_question()`

**Route:** `/show-test-question/<int:test_id>/<int:question_number>` 

**Methods:** `GET`

**Purpose:**  Präsentiert dem Benutzer eine spezifische Frage aus einem gekauften Test. Verfolgt den Fortschritt des Benutzers und kontrolliert die Anzeige der Antworten basierend auf dem Benutzerfortschritt.

**Sample output:**

Test: VWL Grundlagen Test
Frage 1 von 2:
"Erkläre den Begriff 'Opportunitätskosten' und gib ein Beispiel."
[Antwort anzeigen] [Nächste Frage]