---
title: Architecture
parent: Technical Docs
nav_order: 1
---



{: .label }
Ilja Makarchuk

{: .no_toc }
# Architecture



<details open markdown="block">
{: .text-delta }
<summary>Table of contents</summary>
+ ToC
{: toc }
</details>

## Overview

Dies ist eine Lernplattform namens "KnowHub", die verschiedene interaktive Lernmöglichkeiten bietet. Die Hauptfunktionen sind:

- Ein Quizsystem mit verschiedenen Spielmodi (Multiple Choice, Definitionen zuordnen, Wahr/Falsch)
- Ein Modulsystem, bei dem Nutzer verschiedene Fachbereiche freischalten können
- Ein Punktesystem zur Motivation und zum Freischalten von Inhalten
- Ein Shop zum Erwerb von Tests und Items
- Ein Testsystem für ausführlichere Lernkontrollen

## Codemap

Die wichtigsten Komponenten sind:

1.Benutzer-Management:


- Login/Register/Logout Funktionalität
- Profilsystem mit Passwortänderung
- Session-Management für authentifizierte Nutzer


2.Lernsystem:


Module-Selection: Verwaltung der freigeschalteten und verfügbaren Module
Drei Spieltypen:
  - Quiz (/quiz/<module>)
  - Definition Game (/definition-game/<module>)
  - True/False Game (/true-false-game/<module>)

3.Shop & Belohnungssystem:


- Punktebasierter Shop für Tests und Items
- Fortschrittssystem für gekaufte Tests
- Belohnungssystem basierend auf Punkten

## Cross-cutting concerns

1.Datenbankdesign:


- SQLite als Datenbank
- Verschiedene Modelle für Benutzer, Fragen, Tests etc.
- Automatische Initialisierung mit Beispieldaten


2.Punktemechanik:


- Punkte als zentrale Währung
- Belohnungen für richtige Antworten
- Punktabzug bei falschen Antworten oder Zeitüberschreitung
- Verwendung zum Freischalten von Modulen oder Kauf von Items


3.Modulsystem:


- Module können entweder kostenlos oder mit Punkten freigeschaltet werden
- Jedes Modul enthält verschiedene Lernspiele
- Fortschrittsverfolgung pro Modul
