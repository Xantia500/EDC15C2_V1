# ÉTAPE 80 — ★ Tu avais raison : il y a bien une table **16×16 sans axes**, et j'ai trouvé le mécanisme

> Vérification faite, et elle va plus loin que prévu : les axes ne sont pas « perdus », ils sont dans une
> **banque d'axes** en `EA 0xE100A`–`0xE10F1`, et certaines cartes ne sont qu'une **grille nue** de 256 mots.
> Au passage, une méthode nouvelle et très puissante : **la table des handles donne la taille exacte de
> chaque objet** (écart entre deux pointeurs consécutifs).

---

## 1. La banque d'axes : `EA 0xE100A` – `0xE10F1`

Neuf objets, handles `0x1400` → `0x141A`, **sans aucune grille** — uniquement des points de rupture :

| handle | EA | tag | n | valeurs |
|---|---|---|---|---|
| `0x1400` | `0xE100A` | **C42E** | 8 | 200 400 600 1250 1750 2250 2500 4000 |
| `0x1402` | `0xE101E` | **C42E** | 2 | 650 1200 |
| `0x1404` | `0xE1026` | **C42E** | 16 | 200 400 600 800 1000 1250 1500 1750 2000 2250 2500 3000 3500 4000 4500 5000 |
| `0x1406` | `0xE104A` | **C42E** | 16 | *(identique à 0x1404)* |
| `0x1408` | `0xE106E` | **C42E** | 8 | *(identique à 0x1400)* |
| `0x140A` | `0xE1082` | **C68A** | 16 | 0 200 400 800 1200 1600 2000 2400 2800 3200 3600 4000 4500 5000 6000 7000 |
| `0x140C` | `0xE10A6` | **C68A** | 8 | 400 2000 2800 4000 4500 6000 8000 11000 |
| `0x140E` | `0xE10BA` | **C6A2** | 16 | 0 200 400 800 1200 1600 2000 2400 2800 3200 3600 4000 4500 5000 6000 7000 |
| `0x1410` | `0xE10DE` | **C6A2** | 8 | 500 1000 2000 4000 6000 8000 11000 12000 |
| `0x1412`–`0x141A` | `0xE10F2`–`0xE1112` | — | 1/4/5/6/6 | scalaires |

⇒ **`C68A` et `C6A2` ont exactement les mêmes points de rupture à 16 points** (0 … 7000).
Deux variables **de même nature et de même échelle** : la **quantité de carburant** (étape 79).

## 2. ★ Le mécanisme : `unk_2F56` (position) puis `unk_2FAC` (lecture de grille nue)

```
unk_2F56(&position1, variable1, handle_axe1)     ; calcule la position dans l'axe (3 mots)
unk_2F56(&position2, variable2, handle_axe2)
unk_2FAC(&position1, &position2, handle_grille)  ; lit la GRILLE NUE
```

Preuve, `sub_D4D0A` (l.241558-241576) :

```
mov r1, #0E5B0h ; mov r2, word_C7C2 ; mov r3, word_14D6 ; calls unk_2F56   ← axe 1, variable C7C2
mov r1, #0E5B6h ; mov r2, r14       ; mov r3, word_14D8 ; calls unk_2F56   ← axe 2, variable r14
mov r1, #0E5B0h ; mov r2, #0E5B6h   ; mov r3, r15       ; calls unk_2FAC   ← grille
```

Et `loc_D4848` (l.241049-241050) : `unk_2FAC(0xC9BA, 0xC9C6, word_14C6)` — les positions `0xC9BA`/`0xC9C6`
ayant été calculées plus haut (`0xC9BA` = régime, `0xC9C6` = charge).

**Voilà l'explication mécanique de ta règle** : *« des maps n'ont pas d'axes : pas d'ID ni descripteur+n,
juste la map »*. C'est exact — la grille est nue, les axes sont dans la banque et l'appelant les désigne.

## 3. ★ Les cartes sans axes, trouvées

| EA | handle | taille (mots) | dimension | contenu |
|---|---|---|---|---|
| **`0xE2816`** | `0x14C6` | **256** | **16 × 16** | **tout à zéro** |
| `0xE2B62` | `0x14D0` | 252 | ? (16×16 ≈) | tout à zéro |
| `0xE2D5A` | `0x14D2` | 252 | ? | tout à zéro |
| `0xE130E` | `0x1444` | **81** | **9 × 9** | tout à zéro |
| `0xE2078` | `0x1446` | **81** | **9 × 9** | tout à zéro |
| `0xE211A` | `0x1448` | **81** | **9 × 9** | tout à zéro |

**`0xE2816` = 256 mots = 16 × 16, exactement ce que tu pressentais.** Et ses axes ne sont pas dans les
données : ils sont `word_1404` (régime 16 pts) et `word_140E` (charge 16 pts).
**Mais elle est entièrement nulle** ⇒ dans cette calibration, **la fonction est neutralisée**.

`0xE2B62` et `0xE2D5A` sont **deux variantes de la même table**, sélectionnées par le codage véhicule :

```
movb rl0, byte_C2C1
cmpb rl0, #1  →  grille = word_14D0 (0xE2B62)
cmpb rl0, #3  →  grille = word_14D2 (0xE2D5A)
```

## 4. La méthode nouvelle : **la table des handles donne la taille des objets**

Les handles pointent sur le début de chaque objet ; l'écart entre deux pointeurs consécutifs = **la taille
exacte**. Vérifié deux fois :

| objet | mots entre pointeurs | structure attendue | accord |
|---|---|---|---|
| `0xE7828` (boost limiter) | `0xE7920 − 0xE7828` = **124** | 2 + 10 + 2 + 10 + 100 = **124** | ✔ |
| `0xE2ADC` (f×régime, charge) | `0xE2B62 − 0xE2ADC` = **67** | 2 + 7 + 2 + 7 + 49 = **67** | ✔ |

⇒ on peut désormais **dimensionner n'importe quelle carte sans deviner**, et détecter les grilles nues.
844 handles pointent dans le Datensatz : c'est un plan cadastral complet de la calibration.

## 5. Ce qui reste ouvert

1. **252 mots** : ni 16×16 (256), ni 14×18. Hypothèse : un en-tête de 4 mots dans l'objet précédent, ou une
   dimension 14×18. **Non tranché.**
2. Comment les grilles nues **9×9** (`0xE130E`, `0xE2078`, `0xE211A`) sont consommées : `word_1444` est passée
   en `r14` dans des appels `unk_1D50` — donc parfois la grille nue est utilisée comme *axe* ? À instruire.
3. Les 5 objets scalaires `0xE10F2`–`0xE111D` (1/4/5/6/6 mots).

## 6. Consignation

**`CATALOGUE_MAITRE.md` § 13 B.26** — banque d'axes, mécanisme `unk_2F56`/`unk_2FAC`, cartes sans axes
(16×16 et 9×9), variantes `byte_C2C1`, et la règle de dimensionnement par la table des handles.
