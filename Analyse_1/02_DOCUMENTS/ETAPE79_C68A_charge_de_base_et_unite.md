# ÉTAPE 79 — `C68A` (0x0F80) nommé : **la charge de base**. Et la réponse à « charge de quoi ? »

> Le chaînon suivant est cassé dans le bon sens : `C68A` — l'identifiant le plus fréquent des records DTC —
> n'est pas une inconnue isolée, c'est **le frère de `C6A2`**, produit dans la *même* routine, à partir de la
> *même* limite de fumée. Et il devient la source de `C60E`, qui elle-même indexe la **consigne de
> suralimentation** — que j'ai décodée. Conclusion : la « charge » est une **quantité de carburant**.

---

## 1. `C68A` = 0x0F80 : la charge de base (chaîne prouvée)

`C68A` n'a **que deux écrivains** dans tout le firmware : `= 0` (l.189568) et `= r6` (l.189836).
Tout se joue donc dans le bloc `seg015 0xB71xx–0xB73xx`, le même que `C6A2` :

```
C690 = unk_1D50(handle 0x1B40 = EA 0xE8444, régime C42E, air C3E6)   ← carte de LIMITE DE FUMÉE
C6B0 = sub_B33DC(C6BA)                                              (l.178866)
C6BC = min( C690 − C69C , C6B0 )                                    (l.178878-178894)
        ↓
C68A = C6BC + C69C          (l.189637 + 189836)   ← charge de BASE
C6A2 = r9, borné par [word_142C+#0Eh] + C690        (l.189624 + 189839)   ← charge FINALE
C694 = C6A0 + r9                                    (l.189632)
```

| RAM | rôle | preuve |
|---|---|---|
| **`C68A`** | **charge de base** = valeur de la limite de fumée, écrêtée puis ré-offsetée | l.189836 |
| **`C6A2`** | **charge finale** (celle qui indexe les cartes) | l.189839 |
| `C690` | sortie de la carte de fumée `0xE8444` | l.181906-181912 |
| `C6BC` | limite de fumée moins l'offset `C69C`, plafonnée par `C6B0` | l.178878 |
| `C69C` | offset de charge | l.178866 |
| `C6B0` | plafond secondaire (`sub_B33DC`) | l.178872 |

`C68A` est ensuite utilisé comme **axe d'interpolation** : l.190628, 195721, 197906, 197911, 204199
(`mov r13, word_C68A` puis `calls unk_1D36/1D50`).

## 2. `C60E` = la charge retenue, et ses trois variantes

`loc_AE2B6` → `loc_AE2D4` (l.174194-174217) :

| variante `word_141E+0x26` | source de `C60E` |
|---|---|
| 0 ou 1 | **`C68A`** (= 0x0F80, la charge de base) |
| 2 | `C6B6` = `D9A6 + C69E` (l.183252) |
| 3 | `C6B8` = `C6A6 + C69E` (l.182757) |

⇒ **`C68A`, `C6B6`, `C6B8`, `C60E` sont quatre formes de la même grandeur** : la **charge demandée**.
Ce que je cherchais depuis deux étapes est donc résolu : `0F80` n'est pas un capteur, c'est **la charge
de référence injectée dans tout le diagnostic**.

## 3. ★ La carte de consigne de suralimentation, décodée

`unk_1D50(word_1A4C ou 1A4A, régime, C60E)` (l.172680) et `unk_1D50(word_1A46, patmo, C60E)` → consignes.
La carte `EA 0xE7A00` (handle `0x1A4A`) :

```
[ C42E ][16]  0 400 1000 1250 1500 1750 2000 2250 2500 3000 3500 4000 4250 4500 5000 5500
[ C60E ][10]  0 800 2000 3200 3600 4000 4500 5000 6000 7000
```

| régime \ C60E | 0 | 800 | 2000 | 3200 | 3600 | 4000 | 4500 | 5000 | 6000 | 7000 |
|---|---|---|---|---|---|---|---|---|---|---|
| **0** | 800 | 800 | 800 | 800 | 800 | 800 | 800 | 800 | 800 | 800 |
| **1000** | 1030 | 1030 | 1040 | 1090 | 1110 | 1150 | 1175 | 1200 | 1200 | 1200 |
| **1500** | 1050 | 1060 | 1080 | 1204 | 1272 | 1370 | 1490 | 1580 | 1755 | 1800 |
| **2000** | 1070 | 1080 | 1150 | 1354 | 1452 | 1540 | 1660 | 1780 | 1980 | 2100 |
| **2500** | 1090 | 1110 | 1250 | 1462 | 1556 | 1645 | 1765 | 1870 | 2050 | 2200 |
| **3000** | 1110 | 1124 | 1308 | 1570 | 1650 | 1740 | 1835 | 1930 | 2110 | 2200 |
| **4000** | 1110 | 1130 | 1330 | 1624 | 1722 | 1810 | 1900 | 2000 | 2130 | 2150 |
| **5500** | 1110 | 1130 | 1330 | 1508 | 1574 | 1630 | 1680 | 1740 | 1830 | 1830 |

**800 → 2200 = 0.8 → 2.2 bar absolus** ⇒ c'est bien une **consigne de pression de suralimentation**,
cohérente avec la limite `C614` (max 2370 mbar) trouvée à l'étape 78. Et son axe 2 est la **charge**.

Deux courbes d'asservissement de la même grandeur :

| EA | axe | valeurs | lecture |
|---|---|---|---|
| `0xE65A4` | C60E 800…7000 (14 pts) | **1050 → 1200** | plancher de pression (1050 mbar) qui monte avec la charge |
| `0xE7936` | C60E 0…7000 (9 pts) | **−300 … −400** | offset négatif appliqué à la consigne |
| `0xE6D28` | `C6B6` 0…10000 (8 pts) | 0 partout | correction de la variante 2, **neutralisée** |

## 4. ★ Réponse à ta question : « charge » de QUOI ?

Deux candidats de même décade. **Le faisceau d'indices pointe le carburant** :

| indice | calcul | verdict |
|---|---|---|
| Sortie de la **carte de fumée** `0xE8444` | grille 1750 → 7600 | une carte de fumée **limite du carburant** ⇒ 17.5 → 76 mg/tour si ×100 : **parfait pour un 2.2 HDi** |
| Axes de la famille `C6A2` | 500, 1500, 6000, 7000, 8000, 9000, 10000 | ⇒ **5, 15, 60, 70, 80, 90, 100 mg** : les points de rupture canoniques d'une cartographie d'injection |
| Axe de `C6B6` (`0xE6D28`) | 0 → **10000** | 0 → **100 mg** : plafond exact du limiteur de débit |
| Structure | consigne de suralimentation = f(régime, **charge**) | sur un common rail, la pression est toujours cartographiée en f(régime, **quantité injectée**), jamais en f(air) |

⇒ **`C6A2` et `C68A` sont des quantités de CARBURANT, en mg/tour × 100.**
La « charge » de ce calculateur, c'est **la charge de carburant à injecter** — et non une charge d'air.

**Statut** : hypothèse **fortement étayée** (4 indices convergents), pas encore *prouvée* au sens strict,
car je n'ai pas encore trouvé le point où `C6A2` est converti en temps d'injection.

## 5. ⚠ Révision de l'étape 77 : le décompte des « cartes à axe C6A2 »

En revérifiant, **plusieurs des 11 « axes `C6A2` » étaient des courbes 1-D dont les valeurs ressemblent à
un axe** (ex. `0xE609A` = courbe 1-D sur C6A2 valant 10000 partout ; `0xE5610` = la première ligne de la
carte voisine). Test appliqué désormais : **l'axe n'est retenu que si `n1 × n2` mots tiennent entre l'axe et
la structure suivante, avec deux suites strictement croissantes.**

| statut | EA |
|---|---|
| **carte 2-D fermement établie** (`f(régime, charge)`, offsets −160…0) | **`0xE2ADC`** (7 × 7) |
| cartes 2-D probables | `0xE13C6`, `0xE7DAC` |
| **bloc de 4 descripteurs d'axes, sans grille** — point ouvert | `0xE1082` : `C68A`(16) · `C68A`(8) · `C6A2`(16) · `C6A2`(8), puis 22 mots de scalaires, puis le bloc `0xE111E` |
| courbes 1-D sur la charge | `0xE609A`, `0xE6102`, `0xE61B2`, `0xE622E`, `0xE627A`, `0xE62C6`, `0xE8E12`, `0xE8EE0`, `0xE963A`, `0xEAFBA`, `0xEB6CE`, `0xE6D28` |

Le bloc `0xE1082` est le plus intrigant : **quatre déclarations d'axes consécutives** (charge grossière 16 pts,
charge fine 8 pts, puis les mêmes pour `C6A2`) **sans grille adjacente**. Deux lectures possibles — descripteurs
d'axes partagés, ou variantes 16×16 / 8×8 de cartes stockées ailleurs. **Je ne tranche pas.**

## 6. Ce que ça change

- `0F80` → `C68A` : **charge de base** (n'était plus une inconnue) — 27 records DTC éclairés.
- `C60E`, `C6B6`, `C6B8` : **variantes de la charge**.
- La **consigne de suralimentation** est une carte identifiée (`0xE7A00`, 800-2200 mbar).
- La « charge » est du **carburant**.

## 7. Prochaines cibles

1. **Le temps d'injection** : trouver `f(C6A2, pression rail)` → durée, ce qui prouverait définitivement l'unité.
2. Le **bloc `0xE1082`** (4 descripteurs d'axes).
3. `unk_20AC(x, y, 10000)` : sémantique exacte (appelé 3 fois avec `C68A` en `r12`).
4. `C6A6` / `D9A6` / `C69E` : les entrées de `C6B6` et `C6B8`.

## 8. Consignation

**`CATALOGUE_MAITRE.md` § 13 B.25** — `C68A` chargé de base, chaîne `C690 → C6BC → C68A → C6A2`, les trois
variantes de `C60E`, la carte `0xE7A00` décodée, l'unité carburant (4 indices), la révision du décompte des
cartes à axe `C6A2`.
