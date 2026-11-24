# ÉTAPE 81 — **Tu avais raison sur toute la ligne.** `0xE2816` n'est pas à zéro : c'est très probablement l'avance (SOI)

> Mon erreur : j'ai lu **les six premiers mots** d'une grille de 256 et j'ai écrit « tout à zéro ».
> C'est faux, et c'est exactement le genre de raccourci qu'il ne faut pas prendre. Correction complète,
> table intégrale, vérification de la méthode de dimensionnement (34 accords, **3 contre-exemples**),
> et les trois autres cartes identifiées par leurs axes.

---

## 1. Correction : les cartes ne sont pas à zéro

| EA | mots | non nuls | min | max |
|---|---|---|---|---|
| **`0xE2816`** | 256 (16×16) | **229 / 256** | **−37** | **1067** |
| `0xE130E` | 81 (9×9) | **64 / 81** | 0 | 15437 |
| `0xE2078` | 81 (9×9) | **64 / 81** | 0 | 17920 |
| `0xE211A` | 81 (9×9) | **64 / 81** | 0 | 13184 |
| `0xE2B62` | 252 | 147 | 0 | **200** |
| `0xE2D5A` | 252 | 134 | **−175** | 0 |

Seuls les **premiers mots** étaient nuls (coin « moteur non tournant »). Toutes sont des cartes vivantes.

## 2. `0xE2816` : 16 × 16 = **f(régime, charge)** — table intégrale

Axes, prouvés par le code (l.239933-239968) :

```
unk_2F56(0xC9BA, word_C91C (= C42E régime), word_1404)   ← axe 16 points, 200 … 5000
unk_2F56(0xC9C6, word_C94C (= C6A2 charge), word_140E)   ← axe 16 points, 0 … 7000
unk_2FAC(0xC9BA, 0xC9C6, word_14C6)  → grille 0xE2816     (l.241049)
```

| régime \ charge | 0 | 200 | 400 | 800 | 1200 | 1600 | 2000 | 2400 | 2800 | 3200 | 3600 | 4000 | 4500 | 5000 | 6000 | 7000 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **200** | 0 | 0 | 0 | 0 | 0 | 0 | 43 | 43 | 43 | 128 | 128 | 85 | 0 | 0 | 0 | 0 |
| **400** | 0 | 0 | 0 | 0 | 0 | 0 | 43 | 43 | 43 | 128 | 128 | 85 | 0 | 0 | 0 | 0 |
| **600** | −37 | −37 | −37 | −36 | −36 | 0 | 43 | 43 | 43 | 128 | 128 | 43 | 8 | 0 | 0 | 0 |
| **800** | −37 | −37 | −37 | −37 | −35 | 0 | 20 | 36 | 40 | 72 | 80 | 44 | 44 | 44 | 44 | 44 |
| **1000** | 25 | 25 | 12 | 0 | 0 | 8 | 12 | 21 | 32 | 60 | 79 | 101 | 120 | 128 | 128 | 128 |
| **1250** | 94 | 94 | 45 | 33 | 21 | 21 | 21 | 21 | 29 | 51 | 71 | 97 | 124 | 144 | 152 | 152 |
| **1500** | 126 | 126 | 68 | 46 | 29 | 29 | 29 | 29 | 29 | 49 | 79 | 106 | 139 | 171 | 232 | 272 |
| **1750** | 142 | 142 | 84 | 46 | 37 | 37 | 37 | 37 | 37 | 57 | 86 | 122 | 164 | 196 | 285 | 324 |
| **2000** | 153 | 153 | 104 | 61 | 52 | 52 | 52 | 52 | 53 | 76 | 107 | 141 | 188 | 228 | 320 | 362 |
| **2250** | 186 | 170 | 121 | 82 | 73 | 73 | 73 | 73 | 77 | 89 | 132 | 173 | 220 | 267 | 356 | 398 |
| **2500** | 229 | 205 | 171 | 100 | 93 | 93 | 93 | 97 | 102 | 126 | 166 | 212 | 267 | 315 | 387 | 427 |
| **3000** | 296 | 276 | 256 | 149 | 129 | 152 | 192 | 233 | 283 | 331 | 369 | 395 | 419 | 443 | 469 | 469 |
| **3500** | 388 | 364 | 338 | 277 | 275 | 324 | 366 | 404 | 454 | 520 | 571 | 606 | 638 | 667 | 683 | 683 |
| **4000** | 497 | 478 | 460 | 455 | 498 | 540 | 584 | 624 | 664 | 712 | 764 | 824 | 884 | 896 | 896 | 896 |
| **4500** | 597 | 598 | 637 | 743 | 809 | 853 | 896 | 917 | 937 | 957 | 972 | 981 | 981 | 981 | 981 | 981 |
| **5000** | 683 | 683 | 725 | 811 | 881 | 935 | 960 | 977 | 990 | 1003 | 1015 | 1028 | 1043 | 1056 | 1067 | 1067 |

**Croissance dans les deux directions** (charge ↑ ⇒ valeur ↑ ; régime ↑ ⇒ valeur ↑) : signature d'une
**avance**, pas d'une durée ni d'une pression. Et le plancher négatif (−37) à bas régime est typique d'une
correction d'avance au ralenti.

## 3. ★ Le consommateur : une chaîne de corrections additives

`loc_D4798` → `loc_D483C` (l.240996-241052) :

```
r15 =  word_C756
r15 += word_C73E
r15 += word_C74E
r15 += word_C748
r15 += word_C766
r15 += word_C770                     ← six termes correctifs
word_D518 = r15
si word_FD20.2 :
    r15 += unk_2FAC(0xC9BA, 0xC9C6, word_14C6)   ← LA CARTE 0xE2816
    r15 = min(r15, word_C754)                     ← plafond
    word_D51A = carte
```

**Base + corrections + plafond** : c'est la structure exacte d'un calcul d'**avance à l'injection**.
Ton hypothèse SOI = f(IQ, RPM) est donc **cohérente au niveau de la structure, de la forme de la surface
et du signe des valeurs**. Ce qui manque pour la certitude : `word_D518`/`word_D51A` n'ont que des **écritures**
traçables par IDA — la valeur est consommée indirectement (export de mesure ou pointeur). L'unité (0,02 °CA ?
→ 21,3° max) reste à établir.

## 4. Vérification de la méthode de dimensionnement

Test systématique : pour chaque objet commençant par un tag, on calcule sa taille
`2 + n1 + 2 + n2 + n1·n2` et on la compare à l'écart avec le handle suivant.

| résultat | nombre |
|---|---|
| **tailles calculées = écart** | **34** |
| désaccords | **3** |

Désaccords — la méthode **n'est pas infaillible** :

| EA | écart | taille calculée | cause probable |
|---|---|---|---|
| `0xE39C0` | 12 | 6 | un handle pointe **à l'intérieur** de l'objet précédent |
| `0xE6952` | 66 | 18 | objet voisin non référencé (calibration « orpheline ») |
| `0xE6E7E` | 102 | 18 | idem |

⇒ **Règle validée mais à double contrôle** : l'écart donne une *borne* ; il faut le confirmer par la
structure interne. Les 3 exceptions sont à instruire (des objets non pointés existent donc).

## 5. `0xE2B62` / `0xE2D5A` : dimension **résolue** — 14 × 18

`252 = 14 × 18` ✔ (mon « ? » de l'étape 80 est levé). Axes, lus dans le code (`sub_D4D0A`, l.241558-241576) :

| handle | EA | tag | n | valeurs |
|---|---|---|---|---|
| `0x14D6` | `0xE2F6A` | **C7C2** | 14 | 1190 1200 2000 3000 4000 5000 6000 7000 8000 9000 10000 11000 12000 13500 |
| `0x14D8` | `0xE2F8A` | **C78A** | 18 | 0 200 1000 1500 2000 3000 4000 6000 7000 **7100 7200 7300 7400 7500 7600 7700 7800 7900** |

Deux remarques fortes :
- **`C7C2` : 1190 → 13500** en 14 points. Décade et points de rupture d'une **pression rail × 0,1 bar**
  (119 bar → **1350 bar**, la pression max d'un common rail EDC15C2).
- **`C78A`** : axis 0 → 7900 avec **une série fine au pas de 100 entre 7000 et 7900** — signature d'un axe
  de **débit/quantité** dont on veut la précision en haut de plage.

Et les deux grilles forment un **couple d'offsets opposés** : `0xE2B62` ∈ **[0 … +200]**, `0xE2D5A` ∈ **[−175 … 0]**,
sélectionnées par `byte_C2C1` (1 → 0x14D0, 3 → 0x14D2). Symétrie parfaite ⇒ **deux variantes d'une même
correction additive** (l'une positive, l'autre négative) selon le codage véhicule.

## 6. Les trois grilles 9×9

Axes 9 points disponibles dans la banque :

| handle | EA | tag | valeurs |
|---|---|---|---|
| `0x144A` | `0xE13B0` | **C42E** | 0 700 1000 1500 2000 3000 3500 4000 4500 |
| `0x144C` | `0xE13C6` | **C6A2** | 0 1000 2000 3000 4000 5000 6000 7000 8000 |
| `0x144E` | `0xE13DC` | **C63C** | 0 1707 3413 5120 6827 8533 10667 12800 15360 |

`C63C : 0 → 15360` ⇒ **encore une pression rail × 0,1 bar** (0 → **1536 bar**).

Consommateur (l.177865-177910) :

```
r7 = <grandeur> − word_C678        ; écart, borné ≥ 0
unk_1D6C(&pos, r7, word_144E)      ; position dans l'axe C63C (9 pts)
word_1D94(0xC83E, pos, word_1446)  ; lecture de la grille 9×9 (0xE2078)
... → [r0+#8], puis orb byte_C335, #8
```

Tracé de `0xE2078` (axes : rangée = C63C 9 pts, colonne = 9 pts) :

```
       0     0     0     0     0     0     0     0     0
       0  1460  3100  4608  6144  7808 10768 14096 17920
       0   800  1538  2532  3605  4762  8582 12212 15540
       0   800  1492  2434  3336  4310  5593  6920  8480
       0   880  1587  2492  3278  4023  5066  6142  8067
       0   830  1495  2402  3236  3980  4926  6025  7853
       0   800  1481  2299  3098  3869  4960  6132  7650
       0   800  1372  2097  2901  3761  4920  6692 10710
       0   720  1301  2123  2956  3905  5465  7348 11264
```

**Lecture retenue (hypothèse)** : la structure « **écart** → **position dans un axe de pression rail** →
**grille** » est celle d'une **carte de correction de débit/durée en fonction de l'écart de pression rail**
(correction de dérive d'injecteur), pas d'une consigne. Les valeurs (max 17920) seraient alors en
**µs × 0,1** (1,79 ms) ou en unités de durée interne. **Non tranché** : il faut le coefficient appliqué
après `[r0+#8]`.

## 7. Ce qui est acquis / ce qui ne l'est pas

| point | statut |
|---|---|
| les 6 cartes ne sont pas à zéro | **acquis** (correction de mon erreur) |
| `0xE2816` = 16×16 = f(régime C42E, charge C6A2) | **acquis** (axes prouvés par le code) |
| `0xE2816` = avance (SOI) | **très probable** (structure + forme + signe) — unité à établir |
| `0xE2B62`/`0xE2D5A` = 14×18, axes C7C2 × C78A | **acquis** |
| ce couple = deux offsets opposés (±) | **acquis** (symétrie des plages) |
| `C7C2` et `C63C` = pression rail × 0,1 bar | **probable** (décades 1350 / 1536 bar) |
| rôle exact des 9×9 | **hypothèse** (correction liée à l'écart de pression rail) |
| méthode de dimensionnement | **validée** (34 accords) mais **3 exceptions** à instruire |

## 8. Prochaines cibles

1. **L'unité de l'avance** : suivre `word_D518` par le mécanisme d'export de mesure (`0xCCB2`) ou les tables
   de scaling, pour convertir 1067 en degrés.
2. **Les 3 objets orphelins** (`0xE39C0`, `0xE6952`, `0xE6E7E`) : des calibration non pointées existent.
3. Nommer `C7C2`, `C78A`, `C63C` : trois variables de plus dans le vocabulaire.

## 9. Consignation

**`CATALOGUE_MAITRE.md` § 13 B.27** — correction des « cartes à zéro », table 16×16 intégrale de `0xE2816`,
chaîne de corrections additives, vérification de la méthode de dimensionnement, `0xE2B62`/`0xE2D5A` en 14×18,
axes `C7C2` / `C78A` / `C63C`.
