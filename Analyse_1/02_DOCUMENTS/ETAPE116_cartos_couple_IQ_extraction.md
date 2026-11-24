# ÉTAPE 116 — Les cartos couple → IQ sont bien là : extraction complète

> ## ⚠️ PÉRIMÉ (audit Étape 123)
>
> L'interprétation « cartes couple → IQ avec axe X de 8 points » est **RETIRÉE** (errata **E27**).
> Les blocs `0xE2078`/`0xE211A` sont **utilisés** comme tables 2-D par le code (12 sites `word_1D94`),
> mais leur **découpage interne en 7×8 est une hypothèse**, non un fait. Voir `ETAPE118` et `ETAPE123`.
> L'annexe des handles reste valable.


**★ Errata E26 : la §4 de l'Étape 115 était fausse.** Je m'étais arrêté aux **12 premiers octets**
des emplacements `0x1446`/`0x1448`, qui sont à zéro — mais ce sont des **en-têtes**, et les cartos
commencent juste derrière. **Les deux cartos sont extraites ci-dessous.**

---

## 1. Correction de méthode : la table des handles est indexée en OCTETS

```python
EA = 0xE0000 + u16[ 0x61400 + (handle − 0x1400) ]      # table à fo 0x61400 = EA 0xE1400
```
⇒ **seuls les handles PAIRS sont valides** (un handle impair lit un mot désaligné et renvoie une
valeur fantôme). C'est ce qui a produit le faux « slot vide ».

## 2. Format d'une carto de limitation — 162 octets, 7 × 8

```
[ 10 mots d'en-tête (à zéro) ]          20 o
[ axe : 8 points ]                      16 o
[ 7 lignes × (1 séparateur 0 + 8 valeurs) ]  126 o
                                        ─────
                                        162 o (0xA2)
```
Vérifié par arithmétique : `0xE211A − 0xE2078 = 0xA2` **exactement**. ✔

## 3. ★ Carto n°1 — `handle 0x1446` → EA `0xE2078` (mode 0, offset `C678`)

**Axe (8 points)** : `1460 · 3100 · 4608 · 6144 · 7808 · 10768 · 14096 · 17920`

| ligne | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 |
|---|---|---|---|---|---|---|---|---|
| **1** | 800 | 1538 | 2532 | 3605 | 4762 | 8582 | 12212 | **15540** |
| **2** | 800 | 1492 | 2434 | 3336 | 4310 | 5593 | 6920 | 8480 |
| **3** | 880 | 1587 | 2492 | 3278 | 4023 | 5066 | 6142 | 8067 |
| **4** | 830 | 1495 | 2402 | 3236 | 3980 | 4926 | 6025 | 7853 |
| **5** | 800 | 1481 | 2299 | 3098 | 3869 | 4960 | 6132 | 7650 |
| **6** | 800 | 1372 | 2097 | 2901 | 3761 | 4920 | 6692 | 10710 |
| **7** | 720 | 1301 | 2123 | 2956 | 3905 | 5465 | 7348 | 11264 |

## 4. ★ Carto n°2 — `handle 0x1448` → EA `0xE211A` (mode 1, offset `C67A`)

**Axe (8 points)** : `1080 · 2710 · 4200 · 5632 · 7040 · 8960 · 10880 · 13184`

| ligne | c1 | c2 | c3 | c4 | c5 | c6 | c7 | c8 |
|---|---|---|---|---|---|---|---|---|
| **1** | 660 | 1340 | 2110 | 3243 | 4424 | 6224 | 8112 | 10544 |
| **2** | 700 | 1409 | 2273 | 3173 | 4040 | 5265 | 6578 | 9087 |
| **3** | 610 | 1465 | 2279 | 3058 | 3920 | 4910 | 5970 | 8070 |
| **4** | 690 | 1401 | 2157 | 2903 | 3699 | 4720 | 5784 | 8103 |
| **5** | 640 | 1428 | 2230 | 3030 | 3790 | 4860 | 6110 | 7856 |
| **6** | 750 | 1372 | 2260 | 3060 | 3850 | 5000 | 6692 | 10710 |
| **7** | 800 | 1430 | 2240 | 3080 | 4050 | 5465 | 7342 | 10964 |

## 5. Lecture physique

- Les deux cartos ont **exactement la même forme** : colonne 1 quasi constante (610-880), montée
  régulière, **colonnes 7-8 très dispersées** selon la ligne (6800 → 15 540).
- Les lignes **1, 6 et 7** portent les valeurs hautes en bout de plage ; les lignes **2-5** restent
  basses. C'est le profil d'une carto dont **les lignes extrêmes autorisent plus** de couple.
- Carto n°1 est systématiquement **plus permissive** que la n°2 (ex. ligne 1 col. 8 : 15 540 vs 10 544).
  ⇒ cohérent avec « mode 0 / mode 1 » sélectionnés par `byte_C339`.

**Unités — hypothèse, non tranchée** :
- l'axe `1460 → 17920` se lit naturellement en **vitesse (0,01 km/h)** : 14,6 → 179,2 km/h ;
- les valeurs `600 → 15 540` se lisent en **couple (0,01 Nm)** : 6 → 155 Nm.
  (En 0,01 mm³ d'IQ, 15 540 = 155 mm³, impossible : le maximum du souhait est 80 mm³.)
- La **conversion finale couple → IQ est faite dans `word_1D94`**, routine de bibliothèque absente
  du dump. C'est pour cela que `C682`/`C688` (en 0,01 mm³ dans la cascade) ne peuvent pas être
  recalculés à la main à partir de ces tables.

⚠ **Conséquence importante** : les cartos contiennent bien du couple, pas de l'IQ. Un patch « couple
max » sur ces tables a donc un effet **indirect**, via la conversion bibliothèque.

## 6. Annexe — table des handles 0x1440 → 0x1470 (référence utile)

| handle | EA | contenu |
|---|---|---|
| `0x1440` | `0xE12F6` | courbe, `tagY = 0xC42E`, 2 pts |
| `0x1442` | `0xE1E30` | courbe, `tagY = 0xC42E`, `n = 16` |
| `0x1444` | `0xE130E` | zone à zéro (en-tête) |
| **`0x1446`** | **`0xE2078`** | ★ **carto couple n°1 (7×8)** |
| **`0x1448`** | **`0xE211A`** | ★ **carto couple n°2 (7×8)** |
| `0x144A` | `0xE13B0` | courbe, `tagY = 0xC42E`, 9 pts |
| `0x144C` | `0xE13C6` | courbe, `tag 0xC6A2`, 9 pts |
| **`0x144E`** | **`0xE13DC`** | ★ courbe `0xC63C`, **9 pts** (entrée des limiteurs) |
| `0x1454` | `0xE21BC` | table de 24 octets |
| `0x1470` | `0xE225A` | bloc plafond du ratio (Étape 109) |

## 7. Ce que cela débloque

Le levier « couple max » est maintenant **localisé et chiffré** :

| levier | adresse | remarque |
|---|---|---|
| carto couple **mode 0** | `0xE2078` (162 o) | 7 lignes × 8 valeurs |
| carto couple **mode 1** | `0xE211A` (162 o) | 7 lignes × 8 valeurs |
| plage d'entrée | courbe `0xE13DC` (9 pts) | `D904 − C678/67A` |
| sélection du mode | `byte_C339` | `(C68A >= C626)` |

**Restant à faire** : lever l'ambiguïté d'unité (vitesse vs couple) en identifiant à quoi correspond
réellement la valeur passée en `r13` à `word_1D94` — c'est-à-dire **ce que vaut `0xC83E`** (le tampon
passé en `r12`). C'est le dernier maillon avant de pouvoir modifier les cartos en connaissance de cause.
