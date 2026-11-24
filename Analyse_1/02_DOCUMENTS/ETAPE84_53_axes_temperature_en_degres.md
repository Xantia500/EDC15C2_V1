# ÉTAPE 84 — ★★★ La clé Kelvin ×10 est **validée** : 53 axes de température lisibles · `C3BA` est une **température** de plus

> 53 axes du Datensatz portent une température. Décodés avec `T[°C] = valeur/10 − 273,1`,
> **98 % des points tombent sur des entiers** et les grilles deviennent les classiques
> `−30 / −20 / −10 / 0 / 10 / 20 / 40 / 60 / 80 / 100`. Et un troisième tag de température apparaît : `C3BA`.

---

## 1. Le test décisif

| contrôle | résultat |
|---|---|
| axes de température détectés (`C3D2`, `C3B0`, `C3BA`) | **53** |
| valeurs d'axe tombant sur un **entier de °C** | **283 / 290 = 98 %** |

Une clé fausse ne peut pas produire 98 % d'entiers sur 290 valeurs réparties sur 53 objets indépendants.
⇒ **`T[°C] = valeur/10 − 273,1` est acquise** (les 2 % restants sont des faux positifs de détection,
reconnaissables à leurs valeurs bancales : −19,4 / 143,3 / 133,6).

## 2. Les 53 axes de température, en °C

| EA | grandeur | n | points (°C) |
|---|---|---|---|
| `0xE2F52` | T_LDR | 5 | 17 40 60 80 100 |
| `0xE3820` | T_LDR | 4 | −30 −10 10 30 |
| `0xE38E0` | **C3BA** | 6 | −15 0 10 17 37 60 |
| `0xE3918` | T_LDR | 6 | −20 −10 0 15 20 40 |
| `0xE39C0` | **C3BA** | 2 | −20 60 |
| `0xE3CF0` | T_LDR | 2 | −20 0 |
| `0xE3E50` | **C3BA** | 4 | −5 17 35 50 |
| `0xE68D0` | T_LDR | 8 | −30 10 17 19 25 50 70 80 |
| `0xE68FC` | T_LDR | 4 | −25 −18 −10 −1 |
| `0xE6946` | T_LDR | 2 | −20 0 |
| `0xE69D6` | **C3BA** | 8 | −25 −18 −10 0 10 17 30 40 |
| `0xE6A1E` | T_LDR | 6 | −25 −18 20 60 80 100 |
| `0xE6A3A` | **C3BA** | 8 | −30 −10 0 10 20 30 40 60 |
| `0xE6A6A` | T_LDR | 8 | −25 −18 −10 0 10 30 60 80 |
| `0xE6A8E` | **T_carb** | 6 | 54 64 74 84 93 120 |
| `0xE6AAA` | **C3BA** | 8 | −35 −30 −20 −10 0 15 17 20 |
| `0xE6AF2` | T_LDR | 8 | −25 −18 −10 0 10 30 60 70 |
| `0xE6B16` | **T_carb** | 2 | −20 0 |
| `0xE6B52` | T_LDR | 12 | 0 10 30 40 50 51 80 100 101 102 103 104 |
| `0xE6B92` | T_LDR | 2 | −50 150 |
| `0xE6B9E` | T_LDR | 8 | −25 −18 −10 0 10 30 60 70 |
| `0xE6BC2` | T_LDR | 8 | −25 −18 −10 0 10 30 60 80 |
| `0xE6BE6` | **T_carb** | 6 | 54 64 74 84 93 120 |
| `0xE6DBC` | T_LDR | 6 | −50 −20 0 50 100 150 |
| `0xE6E7E` | **C3BA** | 8 | −20 −10 0 10 20 40 60 80 |
| `0xE6F4A` | **C3BA** | 6 | −50 0 28 40 50 100 |
| `0xE6FDE` | T_LDR | 10 | −25 −20 −15 −10 −5 0 5 10 30 50 |
| `0xE7440` | C3BA | 2 | (−19,4 / 100) ⚠ |
| `0xE7CF8` | C3BA | 2 | (−19,4 / 0,5) ⚠ — **objet déjà décodé étape 78** |
| `0xE7E18` | T_LDR | 6 | −25 −18 −10 0 15 20 |
| `0xE7F1E` | T_LDR | 2 | (−48 / 143,3) ⚠ |
| `0xE7F92` | **T_carb** | 4 | 87 91 93 102 |
| `0xE8014` | **T_carb** | 6 | 32 54 64 84 93 102 |
| `0xE8084` | T_LDR | 6 | −20 −10 0 20 50 65 |
| `0xE80B4` | T_LDR | 10 | −25 −18 −10 0 10 20 40 60 80 100 |
| `0xE816C` | T_LDR | 6 | −18 −10 0 30 50 90 |
| `0xE8188` | T_LDR | 6 | −30 −25 −10 10 80 100 |
| `0xE81E2` | T_LDR | 8 | −30 −20 −10 0 20 40 60 80 |
| `0xE8386` | T_LDR | 2 | 0 100 |
| `0xE839A` | T_LDR | 2 | 0 100 |
| **`0xE868C`** | T_LDR | 6 | **−30 −20 −10 0 10 110** ← la carte 6×6 de l'étape 83 |
| `0xE870C` | T_LDR | 9 | −30 −20 −10 0 10 20 40 60 80 |
| `0xE881A` | T_LDR | 6 | 111 112 113 116 119 122 |
| `0xE8F88` | C3BA | 2 | −40 0 |
| `0xE91D8` | T_LDR | 2 | (−38,4 / 133,6) ⚠ |
| `0xE91E4` | T_LDR | 9 | −30 −20 0 25 40 60 80 95 110 |
| `0xE9E72` | T_LDR | 8 | −20 0 20 40 60 80 100 120 |
| `0xEAFCA` | T_LDR | 2 | −30 60 |
| `0xEB9DA` | T_LDR | 2 | −30 −20 |
| `0xEBA64` | T_LDR | 2 | −30 10 |
| `0xEBA78` | T_LDR | 2 | 0 140 |
| `0xEBB54` | T_LDR | 5 | −30 0 20 60 100 |
| `0xEBBDC` | C3BA | 10 | (−50 … 135) ⚠ partiellement faux |

## 3. ★ `C3BA` est une **troisième température**

| tag | identifiant | axes | rôle |
|---|---|---|---|
| `0xC3D2` | `0x0F00` | **36** | T **liquide de refroidissement** (connu) |
| `0xC3B0` | `0x0F02` | **5** | T **carburant** (connu) |
| **`0xC3BA`** | **`0x0F01`** | **12** | **troisième température** — identifiée à l'instant |

Elle se décode avec **la même clé** ⇒ même famille de capteur. Ses axes réels : `−35 −30 −20 −10 0 10 20 40 60 80`
(`0xE6E7E`), `−30 −10 0 10 20 30 40 60` (`0xE6A3A`), `−40 0` (`0xE8F88`).

**Candidats** : T **air d'admission**, T **huile moteur**, T **EGR**. Le groupe DTC de `C3BA` compte 14 codes
(étape 77) — l'instruction se fera en croisant ses DTC, exactement comme pour `C3D2` (P0115…).

## 4. `C562` : un paramètre **adapté**, pas une mesure

| site | écriture |
|---|---|
| `sub_CF8C8` l.232358 | `word_C562 ← word_C3FA` |
| `sub_CF8A4` l.232352 | `word_C562 ← 0xFF` (**défaut**) |
| l.232870 | `word_C562 ← MDL` |
| l.139595 (reset) | `word_C3FA ← [handle 0x1654]` = `[0xE400A]` = **0** |
| l.142744 (adaptation) | `word_C3FA ← [handle 0x1470 + 6]` = `[0xE2260]` = **8000** |

⇒ `C562` est un **paramètre recopié puis réappris** : remis à 0 au reset, chargé depuis la calibration
(`0xE2260` = 8000) quand l'adaptation l'autorise, avec `0xFF` en valeur de secours. Ce n'est pas une mesure.

## 5. `sub_CE9B4` (l.230432) : le gestionnaire d'états par item

```
add  r3, #21D4h                        ; table d'états
shl  r5, #2 ; add r5, #0CAD0h          ; 4 octets par item
movb rl4, [r4+#0FD21h]                 ; masque par item
bmovn r0.1, Z                          ; drapeau « valide »
extp #3, #1
mov  [r3], word_E1D2                   ; compteur/état écrit
```

Employé partout avec `bmov word_FD40.x, USR0` : c'est le mécanisme **« valeur apprise / valeur valide »**
qui pilote `C3FA`, `C562` et l'apprentissage. Les appels observés portent tous
`r2 = #1FFDh / #1FFEh / #3DEFh` (codes d'item) et `r1 = word_1686 / word_185E / word_1862` (handles).

## 6. Ce qui bloque encore : la carte des DPP

Le code emploie `DPP0 = 0x22`, `DPP1 = 0x21`, `DPP2 = 0x24 / 0x48`, `DPP3 = 3` (l.96805-96808, 125397, 233064).
Tant que la correspondance `DPP × 0x4000 → adresse linéaire` n'est pas établie, **toutes les lectures
indirectes** (`[r4+#6]`, `[r5+#3]`…) restent ambiguës — c'est le dernier verrou du projet.

## 7. Consignation

**`CATALOGUE_MAITRE.md` § 13 B.30** — clé Kelvin ×10 validée (98 %), les 53 axes en °C, `C3BA` température
identifiée (12 axes, identifiant `0x0F01`), `C562` paramètre adapté, `sub_CE9B4` gestionnaire d'états,
verrou des DPP.
