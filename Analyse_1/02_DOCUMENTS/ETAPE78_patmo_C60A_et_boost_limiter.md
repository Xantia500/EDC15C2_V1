# ÉTAPE 78 — `C60A` : **pression atmosphérique**, confirmé. Et la carte que tu as trouvée est bien le *boost limiter*

> Tu avais raison, et ta piste est meilleure que la mienne : `0xE67858` n'est pas un début de carte,
> c'est **la grille** de la carte `EA 0xE7828`, dont l'axe 1 est `C60A`. Le rapport de compression constant
> dans cette grille prouve à lui seul que `C60A` est la **pression atmosphérique**.
> Et cela m'oblige à un **ERRATA** sur l'étape 77.

---

## 1. Ta piste, décodée : `fo 0x67858` = `EA 0xE7858`

`fo 0x67858` → `EA 0xE7858` (convention `EA = fo + 0x80000`). Calcul indépendant de la structure :

```
EA 0xE7828 : [C60A][10] 600 700 750 800 850 900 925 950 975 1050
EA 0xE7840 : [C42E][10] 1000 1250 1500 2000 2500 3000 3500 4000 4500 5000
EA 0xE7858 : ←—— grille 10 × 10 (100 mots) = exactement fo 0x67858
```

**Handle `0x1A44` → ptr `0x7828` → `EA 0xE7828`**, et le consommateur est sans ambiguïté (l.174279-174282) :

```
mov r12, word_1A44          ; la carte
mov r13, word_C940          ; = C60A  (pression atmosphérique)
mov r14, word_C91C          ; = C42E  (régime)
calls 0, unk_1D50           ; interpolation 2-D
...
calls 9, sub_9FF46          ; avec la consigne  → word_C946
```

Puis `loc_AE4DA` (l.174392) : **`word_C614 ← word_C946`** ⇒ **`C614` est la pression maximale autorisée**.

## 2. ★ La preuve par le rapport de compression

Grille complète, avec le rapport `valeur / Patmo` :

| Patmo \ régime | 1000 | 1250 | 1500 | 2000 | 2500 | 3000 | 3500 | 4000 | 4500 | 5000 |
|---|---|---|---|---|---|---|---|---|---|---|
| **600** | 1000 (1.67) | 1030 (1.72) | 1120 (1.87) | 1325 (2.21) | 1375 (2.29) | 1415 (**2.36**) | 1455 (2.42) | 1355 (2.26) | 1295 (2.16) | 1159 (1.93) |
| **700** | 1000 (1.43) | 1030 (1.47) | 1250 (1.79) | 1520 (2.17) | 1605 (2.29) | 1645 (**2.35**) | 1635 (2.34) | 1520 (2.17) | 1490 (2.13) | 1359 (1.94) |
| **750** | 1020 (1.36) | 1100 (1.47) | 1340 (1.79) | 1635 (2.18) | 1725 (2.30) | 1760 (**2.35**) | 1730 (2.31) | 1620 (2.16) | 1595 (2.13) | 1465 (1.95) |
| **800** | 1040 (1.30) | 1180 (1.48) | 1440 (1.80) | 1745 (2.18) | 1835 (2.29) | 1880 (**2.35**) | 1830 (2.29) | 1725 (2.16) | 1700 (2.12) | 1570 (1.96) |
| **850** | 1100 (1.29) | 1260 (1.48) | 1540 (1.81) | 1860 (2.19) | 1950 (2.29) | 2005 (**2.36**) | 1940 (2.28) | 1840 (2.16) | 1790 (2.11) | 1675 (1.97) |
| **900** | 1170 (1.30) | 1330 (1.48) | 1640 (1.82) | 1960 (2.18) | 2070 (2.30) | 2130 (**2.37**) | 2045 (2.27) | 1950 (2.17) | 1880 (2.09) | 1780 (1.98) |
| **925** | 1200 (1.30) | 1380 (1.49) | 1690 (1.83) | 2015 (2.18) | 2130 (2.30) | 2200 (**2.38**) | 2105 (2.28) | 2015 (2.18) | 1935 (2.09) | 1820 (1.97) |
| **950** | 1240 (1.31) | 1460 (1.54) | 1750 (1.84) | 2070 (2.18) | 2200 (2.32) | 2270 (**2.39**) | 2200 (2.32) | 2130 (2.24) | 2010 (2.12) | 1840 (1.94) |
| **975** | 1310 (1.34) | 1600 (1.64) | 1850 (1.90) | 2150 (2.21) | 2370 (2.43) | 2370 (2.43) | 2300 (2.36) | 2150 (2.21) | 2050 (2.10) | 1840 (1.89) |
| **1050** | 1330 (1.27) | 1600 (1.52) | 1850 (1.76) | 2150 (2.05) | 2370 (2.26) | 2370 (2.26) | 2300 (2.19) | 2150 (2.05) | 2050 (1.95) | 1840 (1.75) |

À régime fixe, la valeur suit la première colonne **à rapport de pression constant ≈ 2.35** (colonne 3000 tr/min :
2.36 / 2.35 / 2.35 / 2.35 / 2.36 / 2.37 / 2.38 / 2.39). C'est le comportement d'un **compresseur** : la pression
absolue atteignable = ratio × pression d'entrée. **Seule une pression atmosphérique en axe peut produire cela.**
(Ces valeurs seraient absurdes pour un ΔP : 1000 mbar de ΔP à 600 hPa.)

Valeurs 1000 → 2370 = **1.0 → 2.37 bar absolus** ; axe `C60A` 600 → 1050 **hPa** (l'Everest est à 330 hPa,
600 hPa ≈ 4400 m d'altitude : l'axe couvre très largement le raisonnable).

## 3. Les quatre autres preuves que `C60A` = Patmo

1. **Valeur de repli en calibration** : `loc_AD342` (l.172644-172645) — `word_C60A ← word_C38E`, avec
   `word_C38E = [word_1418 + 8]` (l.212327) = **constante de calibration** (patmo par défaut, capteur absent).
2. **`C60A` est figée dans le contexte de *tous* les diagnostics** : `mov r4, word_C60A / mov word_C940, r4`
   dans chaque routine de défaut (l.131371, 133066, 134627, 166288, 170987, 171250). L'altitude est une
   condition de test, comme la température.
3. **Filtrage lent** : `loc_AD54C` (l.1727xx) — `C940 = (C940 + D854 + courbe(régime)) / 2` : moyenne glissante,
   comportement d'une référence lente (la patmo ne bouge pas en roulant).
4. **13 courbes et 3 cartes l'utilisent comme axe** (cf. § 5) — un axe « altitude » typique.

## 4. ★ ERRATA étape 77 : P0470 n'est pas la pression d'échappement

Le record P0470 porte `0F41 → C60A`, `0F40 → C612`, `0F42 → C614` :

| identifiant | RAM | ce que c'est maintenant |
|---|---|---|
| `0F41` | **`C60A`** | **pression atmosphérique** |
| `0F40` | **`C612`** | **pression d'admission absolue** (axes 1000 → 2200 mbar) |
| `0F42` | **`C614`** | **pression maximale autorisée** (boost limiter) |

⇒ la surveillance compare **patmo / mesure / limite** : c'est le **capteur de pression d'admission** et sa
cohérence avec la pression atmosphérique, **pas** le ΔP du FAP. **Le ΔP FAP reste donc à identifier** —
je le retire de la liste des acquis (mais `C60A` reste la première zone FAP… non : rien).
Seule certitude conservée : `C612`/`C614` appartiennent au circuit de suralimentation.

## 5. La chaîne de pression complète (nouvelle, et elle est belle)

```
C3B2 (entrée brute) → unk_1E50(word_19FA, C3B2, #0D852h) → D854
                                        ↓
                    C612 = D854 + C3B4        (l.172880) ← C3B4 = offset capteur
                    C60A = repli/filtre       (l.172882, l.172645)
                                        ↓
C60E = C68A | C6B6 | C6B8          (l.174217, choix par word_141E+0x26)
   ├─ unk_1D50(word_1A4C/1A4A, régime,  C60E) → D348 = consigne
   ├─ unk_1D50(word_1A46,      Patmo,   C60E) → D344
   └─ unk_1D50(word_1A44,      Patmo,   régime) → D34A = **boost limiter**
                                        ↓
                    sub_9FF46(consigne D34E, limiteur D34A) → C946 → C614
```

| RAM | rôle | preuve |
|---|---|---|
| `C60A` | **pression atmosphérique** (hPa) | § 2 et § 3 |
| `C612` | **pression d'admission absolue** (mbar) | axes `0xE3B3C` 1000→2200 ; `C612 = D854 + C3B4` |
| `C614` | **pression maximale autorisée** | `C614 ← C946` après `sub_9FF46(consigne, limiteur)` |
| `C60E` | valeur d'entrée du calcul de consigne (sélectionnée) | l.174217 |
| `C3B4` | offset du capteur de pression | `C944 = D854 + C3B4` |
| `C38E` | patmo de repli (constante de calibration) | l.212327 |

## 6. La famille « altitude » : 13 courbes + 3 cartes sur `C60A`

| EA | type | axe | valeurs / rôle |
|---|---|---|---|
| **`0xE7828`** | **2-D** | C60A × C42E | **boost limiter absolu**, 1000 → 2370 mbar ★ |
| `0xE71F6` | 2-D | C60A × D004 | 9 × 9 |
| `0xE7920` | 2-D | C60A × C60E | 9 × 9 |
| `0xE3EF4` | 1-D | 743…1100 | **11000 … 10000** — la seule vraie correction (× 1.10 → × 1.00) ; l'axe 743-750 (pas de 1) = **patmo mémorisée** |
| `0xE69FA` | 1-D | 700…1050 | 10000 10000 10000 **7500 5000 0 0 0** ⇒ **dérate altitude** : tout tombe à 0 sous 850-900 hPa |
| `0xE6050` | ambigu | 820…1060 | axe de 9 points suivi de 8 valeurs → **structure non résolue**, ne rien en tirer |
| `0xE3C64`, `0xE6038`, `0xE6066`, `0xE620A`, `0xE6ACE` | 1-D | 0…1800 | **10000 partout = gain × 1.000 : correction neutre** |
| `0xE39B0`, `0xE6A5E`, `0xE6B46`, `0xE6B86`, `0xEBA58` | 1-D | 0…1800 | **0 partout** : correction sœur laissée à zéro |
| `0xE39C8` | 1-D | 700…1000 | 10000 partout |

**Conclusion majeure** : l'ECU possède tout un **sous-système altitude** keyé sur `C60A`, mais dans *cette*
calibration **presque toutes les corrections sont neutres (10000 = 1.000)**. L'altitude n'agit réellement que
par **deux leviers** : la carte boost limiter `0xE7828` et le dérate `0xE69FA`.

## 7. Ce que ça change dans le catalogue

- `C60A` : **pression atmosphérique** — acquis.
- `C612` / `C614` : pression d'admission mesurée / limite — acquis.
- **P0470** : capteur de pression d'admission + cohérence patmo (ERRATA).
- La famille altitude devient une **section à part entière** du document maître.

## 8. Prochaines cibles

1. `D854` / `word_19FA` / `#0D852h` : la linéarisation du capteur de pression (`unk_1E50`).
2. **`C60E`** et ses trois sources `C68A` / `C6B6` / `C6B8` : c'est la variable qui entre dans *toutes* les
   consignes de pression — et `C68A` est justement `0F80`, l'identifiant le plus fréquent des DTC (27).
3. Retrouver le **vrai ΔP FAP** (P1435 / P1442 / P1446), maintenant qu'il ne peut plus être `C60A`.

## 9. Consignation

**`CATALOGUE_MAITRE.md` § 13 B.24** — verdict `C60A`, la carte `0xE7828` avec la preuve du rapport de
compression, la chaîne de pression, la famille altitude, et l'ERRATA sur P0470.
