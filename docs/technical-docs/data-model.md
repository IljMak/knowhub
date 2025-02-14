---
title: Data Model
parent: Technical Docs
nav_order: 2
nav_exclude: true
---

{: .label }
Ilja Makarchuk

{: .no_toc }
# Data model

<details open markdown="block">
{: .text-delta }
<summary>Table of contents</summary>
+ ToC
{: toc }
</details>

Falls das Datamodel nicht funktioniert, habe ich es nochmal als Datei bei der Abgabe angeheftet.

Unsere wichtigsten Hauptentitäten sind User, Lernmodule, Tests und ShopItems. Dabei ist das Herzstück der User, der mit allen anderen Entitäten verbunden ist, denn der User kann Module, Tests oder Shopitems kaufen und diese dann benutzen. Bei den Lernmodulen kann er dazu noch die verschiedenen Spielmodis entscheiden. Die Tests sind so aufgebaut, dass der Nutzer seine Wissen testen kann aber auch als Merkzettel benutzen und somit sich für eine mögliche Klausur vorbereiten. Die ShopItems geben dem Nutzer die Möglichkeiten weitere Belohnungen freizuschalten und somit mehr spielspaß zu haben.


Datamodel:
![get_DataModel](assets/images/DataModel.png)