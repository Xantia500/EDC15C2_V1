# ÉTAPE 88 — Vérification dans le code : ce qui tient, ce qui ne tient pas (errata des « 4 cartes ») · `C562` dans `unk_1FE8`

> Tu avais raison de demander la vérification. Le **mécanisme** est confirmé ligne par ligne.
> Mais **la forme de mes cartes était fausse** : 8 × 8 et non 16 × 8, et elles sont **dix**, pas quatre.
> Et surtout : `unk_2FAC` est un **stub non désassemblé** — donc « interpolateur de grille » est une
> **inférence**, et je dois le dire.

---

## 1. ✅ Vérifié dans le code — le mécanisme complet

### a) Les deux axes (l.237874-237884)

```
mov  r0, word_C42E        ; régime
mov  r1, #0C85Ch
mov  r2, word_C91C
mov  r3, word_1408        ; ← axe
calls 0, unk_2F56
mov  r0, word_C6A2        ; charge
mov  r1, #0C9CCh
mov  r2, word_C94C
mov  r3, word_1410        ; ← axe
calls 0, unk_2F56
```

| handle | EA | tag | n | valeurs |
|---|---|---|---|---|
| `0x1408` | `0xE106E` | **C42E** (régime) | **8** | 200 · 400 · 600 · 1250 · 1750 · 2250 · 2500 · 4000 |
| `0x1410` | `0xE10DE` | **C6A2** (charge) | **8** | 500 · 1000 · 2000 · 4000 · 6000 · 8000 · 11000 · 12000 |

⇒ **grilles 8 × 8 = 64 mots**, indexées **(régime, charge)**.

### b) Les dix objets (l.237890-238124)

`mov r3, word_1Dxx` puis `calls 0, unk_2FAC` — **dix fois** :

| # | handle | pointeur | **EA** | contenu (8×8) | lecture |
|---|---|---|---|---|---|
| 1 | `0x1D9E` | `A958` | `0xEA958` | **−854 … 85** | fortement négatif à haut régime/charge |
| 2 | `0x1DAA` | `AE60` | `0xEAE60` | **plat 1000** | butée |
| 3 | `0x1DA4` | `AB60` | `0xEAB60` | **tout à 0** | **variante désactivée** |
| 4 | `0x1DA6` | `AC60` | `0xEAC60` | **tout à 0** | **variante désactivée** |
| 5 | `0x1DA8` | `AD60` | `0xEAD60` | 100 → **1665** | limite à gradient |
| 6 | `0x1DA2` | `AA60` | `0xEAA60` | 800 → **3000** | limite (lignes plates) |
| 7 | `0x1D96` | `A558` | `0xEA558` | 0 … 85 | correction coin froid/faible charge |
| 8 | `0x1D9A` | `A758` | `0xEA758` | 0 / 85 | masque en escalier |
| 9 | `0x1D9C` | `A858` | `0xEA858` | −72 … 200 | correction riche |
| 10 | **`0x1D98`** | `A658` | **`0xEA658`** | **plat 1280** | **★ le plafond** |

### c) Preuve de la règle `EA = 0xE0000 + pointeur` (test décisif)

| EA | contenu | verdict |
|---|---|---|
| `0xE8444` (règle simple) | `[0xC3C2][16][0 800 1000 … 5200]` puis `[0xC476][16][3000 … 11500]` puis grille — **structure d'axes cohérente** | ✅ **c'est bien là** |
| `0xE4444` (règle « fenêtre 0x8000-0xBFFF ») | 69, −1, 0, 65, −1… — **déchet** | ❌ écartée |

⇒ la règle d'adressage est **re-confirmée par la structure**, pas par convention.

## 2. ⚠ ERRATA de l'étape 87 — ce que j'avais faux

| ce que j'ai écrit | réalité |
|---|---|
| « 4 cartes » | **10 objets** dans le bloc `0x1D96`–`0x1DAA` |
| « 128 mots = 16 × 8 » | **64 mots = 8 × 8** (les axes n'ont que 8 points) |
| tables de `0xEA758` / `0xEA858` sur 4 lignes | **8 lignes** — mes tables étaient décalées d'un bloc |
| « `unk_2FAC` = interpolateur de grille nue » | ⚠ **`unk_2FAC: ds 1`** — IDA **ne l'a jamais désassemblé**. C'est une **inférence de forme d'appel**, pas une lecture. Idem pour `unk_2F56`. |

### Les deux tables corrigées (8 × 8)

`0xEA758` (h `0x1D9A`) — 0 / 85 :

```
  0   0   0   0   0   0   0   0
  0   0   0   0   0   0   0   0
 85  85   0   0   0   0   0   0
 85  85   0   0   0   0   0   0
 85  85   0   0   0   0   0   0
 85  85   0   0   0   0   0   0
 85  85  85   0   0   0   0   0
 85  85  85   0   0   0   0   0
```

`0xEA858` (h `0x1D9C`) — −72 … 200 :

```
   0    0    0    0    0    0  -30  -30
   0    0    0    0    0    0    0  -72
   0    0    0   85   43   15   15  -28
 170  170  170  119  122  142  200  200
 170  170  170  157  128  126  183  183
 170  170  170  121  107  107  176  176
 170  170  170  111   68   60   60   60
 170  170  170  108   43   13   13   13
```

## 3. ✅ Ce qui reste solide : le plafond à **1280**

Ce n'est pas l'étiquette « interpolateur » qui soutient le plafond, c'est **l'arithmétique de la chaîne** :

```
l.238124 : C754 ← sortie de la consultation h 0x1D98
l.241064 : min(r15, word_C754)      ← r15 = avance accumulée
```

Deux grandeurs que l'on compare **partagent forcément la même unité**. La carte d'avance culminant à 25,0°
et le dénominateur étant 15 360 pas/tour, `1280` dans cette unité vaut **30,0°**.
⇒ **plafond = 30,0° avant PMH**, avec **5,0° de marge** au-dessus de la carte principale. **Acquis.**

## 4. `C562` — où le code le met réellement

| fait | preuve |
|---|---|
| **100 références**, **3 écritures** seulement | `word_C562 ← C3FA` (l.232361), `← 0FFh` (l.232352), `← MDL` (l.232870) |
| **argument d'un coordinateur à 10 paramètres** | l.184986 et l.187031 : `mov r2, word_C562` puis empilage de 10 octets, `calls 0, unk_1FE8` |
| entouré de **handles d'axes** `0x14BA` / `0x14BE` et des buffers `D9B6`, `D9C6`, `D9E0`, `D9EA`, `D9F6`, `DA04`, `DA0A` | idem |
| **comparé à des éléments d'axe** pour produire un indice | l.177661 (`[r4+#6]` du handle `0x1B26`), l.159936 (`[r4+#18h]`) |
| identifiant **`0x0F08`** | dictionnaire |

⇒ `C562` est une **grandeur d'entrée de l'arbitrage des limiteurs** (`unk_1FE8`), recopiée d'un paramètre
calibré, **comparée à des axes**. C'est **exactement la place d'une quantité de carburant (IQ / souhait
conducteur)** dans une architecture EDC15 — mais ce n'est pas encore une preuve par le nom.

**Si tu l'as vue ailleurs dans le code, donne-moi le coin** (n° de ligne ou routine voisine) : je la
raccroche immédiatement. De mon côté le seul chemin `C562 → valeur` passe par `C3FA`, qui est lui-même
saturé à `0` / `0x7FFF` et chargé depuis la calibration (handle `0x1470` +6 = **8000**, handle `0x1654`).

## 5. Prochaine cible : `unk_1FE8`

C'est **lui** qui tient `C562`, les axes `0x14BA`/`0x14BE` et huit buffers. Dix paramètres, appelé depuis
tout le segment 015. C'est très probablement le **coordinateur des limiteurs** (couple/quantité) — le
cœur de l'architecture. Le désassembler nommerait `C562` par son rôle, et pas par sa plage.

## 6. Consignation

**`CATALOGUE_MAITRE.md` § 13 B.35** — errata (10 objets, 8×8, `unk_2FAC` = stub), axes `0x1408`/`0x1410`,
table des 10 EA avec contenus, preuve d'adressage `0xE8444` vs `0xE4444`, maintien du plafond à 1 280,
position de `C562` dans `unk_1FE8`.
