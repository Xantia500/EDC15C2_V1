# ÉTAPE 86 — ★★★★★ LA CARTE D'AVANCE DU 4HX, EN DEGRÉS : `0xE2816` = SOI f(régime, charge), 0 → 25,0° avant PMH

> Ton facteur `0,0234375` (= 360 / 15 360) ferme la question. La carte se lit maintenant comme une vraie
> cartographie d'avance, et **la physique valide** : 0° au ralenti à faible charge, **25,0° BTDC** à
> 5 000 tr/min pleine charge, croissance monotone dans les deux directions.
> Bonus : le même facteur **réinterprète `C63C` comme un ANGLE** — ce n'est pas une pression, c'est une
> position vilebrequin 0 → 360°.

---

## 1. La carte d'avance, en degrés avant PMH (BTDC)

Facteur : **`0,0234375 °CRK` par LSB** (360° / 15 360 pas). Offset **0** (convention PSA).
Axes : **régime `C42E`** (16 pts, 200 → 5 000 tr/min) × **charge `C6A2`** (16 pts, 0 → 7 000).

| IQ \ tr/min | 200 | 400 | 600 | 800 | 1000 | 1250 | 1500 | 1750 | 2000 | 2250 | 2500 | 3000 | 3500 | 4000 | 4500 | 5000 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **0** | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 1,0 | 1,0 | 1,0 | 3,0 | 3,0 | 2,0 | 0,0 | 0,0 | 0,0 | 0,0 |
| **200** | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 0,0 | 1,0 | 1,0 | 1,0 | 3,0 | 3,0 | 2,0 | 0,0 | 0,0 | 0,0 | 0,0 |
| **400** | −0,9 | −0,9 | −0,9 | −0,8 | −0,8 | 0,0 | 1,0 | 1,0 | 1,0 | 3,0 | 3,0 | 1,0 | 0,2 | 0,0 | 0,0 | 0,0 |
| **800** | −0,9 | −0,9 | −0,9 | −0,9 | −0,8 | 0,0 | 0,5 | 0,8 | 0,9 | 1,7 | 1,9 | 1,0 | 1,0 | 1,0 | 1,0 | 1,0 |
| **1200** | 0,6 | 0,6 | 0,3 | 0,0 | 0,0 | 0,2 | 0,3 | 0,5 | 0,8 | 1,4 | 1,9 | 2,4 | 2,8 | 3,0 | 3,0 | 3,0 |
| **1600** | 2,2 | 2,2 | 1,1 | 0,8 | 0,5 | 0,5 | 0,5 | 0,5 | 0,7 | 1,2 | 1,7 | 2,3 | 2,9 | 3,4 | 3,6 | 3,6 |
| **2000** | 3,0 | 3,0 | 1,6 | 1,1 | 0,7 | 0,7 | 0,7 | 0,7 | 0,7 | 1,1 | 1,9 | 2,5 | 3,3 | 4,0 | 5,4 | 6,4 |
| **2400** | 3,3 | 3,3 | 2,0 | 1,1 | 0,9 | 0,9 | 0,9 | 0,9 | 0,9 | 1,3 | 2,0 | 2,9 | 3,8 | 4,6 | 6,7 | 7,6 |
| **2800** | 3,6 | 3,6 | 2,4 | 1,4 | 1,2 | 1,2 | 1,2 | 1,2 | 1,2 | 1,8 | 2,5 | 3,3 | 4,4 | 5,3 | 7,5 | 8,5 |
| **3200** | 4,4 | 4,0 | 2,8 | 1,9 | 1,7 | 1,7 | 1,7 | 1,7 | 1,8 | 2,1 | 3,1 | 4,1 | 5,2 | 6,3 | 8,3 | 9,3 |
| **3600** | 5,4 | 4,8 | 4,0 | 2,3 | 2,2 | 2,2 | 2,2 | 2,3 | 2,4 | 3,0 | 3,9 | 5,0 | 6,3 | 7,4 | 9,1 | 10,0 |
| **4000** | 6,9 | 6,5 | 6,0 | 3,5 | 3,0 | 3,6 | 4,5 | 5,5 | 6,6 | 7,8 | 8,6 | 9,3 | 9,8 | 10,4 | 11,0 | 11,0 |
| **4500** | 9,1 | 8,5 | 7,9 | 6,5 | 6,4 | 7,6 | 8,6 | 9,5 | 10,6 | 12,2 | 13,4 | 14,2 | 15,0 | 15,6 | 16,0 | 16,0 |
| **5000** | 11,6 | 11,2 | 10,8 | 10,7 | 11,7 | 12,7 | 13,7 | 14,6 | 15,6 | 16,7 | 17,9 | 19,3 | 20,7 | 21,0 | 21,0 | 21,0 |
| **6000** | 14,0 | 14,0 | 14,9 | 17,4 | 19,0 | 20,0 | 21,0 | 21,5 | 22,0 | 22,4 | 22,8 | 23,0 | 23,0 | 23,0 | 23,0 | 23,0 |
| **7000** | 16,0 | 16,0 | 17,0 | 19,0 | 20,6 | 21,9 | 22,5 | 22,9 | 23,2 | 23,5 | 23,8 | 24,1 | 24,4 | 24,8 | **25,0** | **25,0** |

**Plage brute** : −37 … 1067 ⇒ **−0,87° … +25,01°**.

### Ce que la physique dit (et qui valide le facteur)

| contrôle | résultat |
|---|---|
| avance maxi obtenue | **25,0° BTDC** — valeur canonique d'un 2,2 HDi |
| ralenti (800 tr/min, faible IQ) | **0,0 à −0,9°** — normal, diesel quasi-PMH au ralenti |
| sens de variation en régime | croissant (16,0 → 25,0° sur la ligne pleine charge) |
| sens de variation en charge | croissant (0,0 → 16,0° dans la colonne 200 tr/min) |
| plateau pleine charge 3 500–5 000 | 24,4 → 25,0° — saturation attendue |

Un facteur faux ne produit pas une surface dont le maximum tombe pile à 25° **et** dont le ralenti est à 0°.
⇒ **facteur acquis**, carte identifiée.

## 2. ⚠ ERRATA : `C63C` n'est **pas** une pression, c'est un **ANGLE**

L'axe 9 points `0, 1707, 3413, 5120, 6827, 8533, 10667, 12800, 15360`, relu avec **le même facteur** :

| brut | 0 | 1707 | 3413 | 5120 | 6827 | 8533 | 10667 | 12800 | 15360 |
|---|---|---|---|---|---|---|---|---|---|
| **angle** | **0°** | **40°** | **80°** | **120°** | **160°** | **200°** | **250°** | **300°** | **360°** |

Des valeurs **parfaitement rondes** en degrés, jusqu'à **un tour complet (360° = 15 360)**.
Mon interprétation « pression rail × 0,1 bar (0 → 1 536 bar) » de l'étape 81 est **FAUSSE**.
`C63C` (identifiant **`0x2109`**) est une **position angulaire vilebrequin**.

⇒ **les trois grilles 9 × 9 (`0xE130E`, `0xE2078`, `0xE211A`) sont indexées par l'ANGLE vilebrequin**.
Elles servent donc à des injections **positionnées en angle** : pré-injection, post-injection, ou
**correction de débit par événement angulaire** — pas à une correction de pression.

## 3. `C7C2` confirmé : P_rail × 10

`1190 1200 2000 3000 … 13500` → **119 · 120 · 200 · 300 · … · 1350 bar**. Ta valeur (1350 bar max) tombe pile.
⇒ la carte 14 × 18 (`0xE2B62` / `0xE2D5A`) est bien indexée par **[pression rail, `C78A`]**.

## 4. `C562` a un identifiant : **`0x0F08`** — et ton hypothèse IQ tient

Je m'étais trompé en disant « aucun identifiant » : `C562` **est** dans le dictionnaire, **`0x0F08`**, soit
en plein **bloc capteurs `0x0F0x`** (`0x0F00` = T_LDR, `0x0F01` = `C3BA`, `0x0F02` = T carburant).

Et son axe, relu en quantité de carburant, donne des valeurs **remarquablement rondes** :

| brut | 0 | 300 | 10 000 | 12 000 | 14 016 | 18 000 |
|---|---|---|---|---|---|---|
| **en mg/cycle (÷1000)** | **0** | **0,3** | **10** | **12** | **14** | **18** |

Et surtout, la grille de la carte 6 × 6 prend tout son sens :

- **IQ = 0 → durée = 0** (colonnes nulles en première position) : pas d'injection quand il n'y a pas de débit ;
- IQ ≥ 0,3 mg → durée **constante par ligne** ;
- durée qui **s'effondre avec la température** : 9230 à −30 °C → 0 à +10 °C.

⇒ cette carte n'est pas un préchauffage de bougies : c'est une **durée d'injection additionnelle
(post-injection / post-chauffage) = f(T_LDR, IQ)**, plafonnée à **9230 µs ≈ 9,2 ms**.

## 5. `0xF884` vs `0xEF880` — deux choses différentes

| écriture | nature | vérification |
|---|---|---|
| `#0F884h` dans le code (l.213595, 214368…) | **adresse RAM `0xF884`** (bloc `0xFxxx` où vivent aussi `F99E`, `FD40`…) | n'est pas un symbole nommé ⇒ **pointeur de structure** |
| **EA `0xEF880`** | **hors Datensatz** | le Datensatz s'arrête à `EA 0xEBFB9` ⇒ **oui, padding / vide** ✔ ton intuition est juste |

Le `[0xF884]` que lit `C3AE` est donc une **case RAM**, pas de la calibration. Reste à savoir qui l'écrit.

## 6. `C3BA`

D'accord sur le principe : c'est bien une **température** (même clé Kelvin ×10, 12 axes la portent).
L'hypothèse « homonyme sans carte directe » est cohérente : **aucune de ses 12 occurrences n'est une grille**,
toutes sont des **axes**. Elle peut donc être un **doublon de conditionnement** (même sonde vue deux fois,
par exemple avant/après filtrage) — à confronter à ses 14 DTC pour trancher entre air d'admission,
huile et EGR.

## 7. Consignation

**`CATALOGUE_MAITRE.md` § 13 B.32** — carte d'avance complète en degrés, facteur 0,0234375 acquis,
errata `C63C` = angle, `C7C2` = P_rail × 10, `C562` = identifiant `0x0F08` + hypothèse IQ (0 → 18 mg),
distinction `0xF884` (RAM) / `EA 0xEF880` (padding), note `C3BA`.
