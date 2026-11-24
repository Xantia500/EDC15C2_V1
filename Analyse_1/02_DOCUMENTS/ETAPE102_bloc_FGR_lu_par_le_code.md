# ÉTAPE 102 — Le bloc FGR lu **par le code** : chaque seuil, sa variable, son code de refus

> Test de la recette hexadécimale (`A0 0F` / `94 11` / `88 13` / `70 17` + `F0 55` / `A8 61` +
> `B0 04` / `14 05` + `04 00`) sur `edc.bin`, puis vérification **site par site dans `clean.asm`**.

---

## 1. Ce que donne la recherche hexadécimale brute

| motif | valeur | occurrences dans tout le fichier |
|---|---|---|
| `A0 0F` | 4000 | **323** |
| `94 11` | 4500 | 144 |
| `88 13` | 5000 | 385 |
| `70 17` | 6000 | 267 |
| `F0 55` | 22000 | **29** |
| `A8 61` | 25000 | **3** |
| `B0 04` | 1200 | 140 |
| `14 05` | 1300 | 111 |

**`A8 61` (25000) n'existe que 3 fois** dans les 512 Ko :

| fo | EA | quoi |
|---|---|---|
| `0x14368` | `0x94368` | **code** (`SGE`/comparaison dans une fonction) |
| `0x6278A` | **`0xE278A`** | **Datensatz, bloc A** ★ |
| `0x7278A` | **`0xF278A`** | Datensatz, bloc B (copie) |

Test de co-occurrence (`vMin` ∈ {4000,4500,5000,6000} + `vMax` ∈ {20000,22000,25000} +
`nMin` ∈ {1200,1300} dans un rayon de 70 octets) : **24 sites**, qui se réduisent à **3 zones**
(dupliquées en A/B) :

| zone | contenu | verdict |
|---|---|---|
| `0xE4CF0-0xE4DE0` | 22000, 4000, 1300, 1200… | **faux positif** : suite de **courbes 1-D** |
| `0xE6AB0-0xE6B20` | 5000, 1200, 1300, 20000 | courbe 2-D / grille |
| `0xE9370-0xE9470` | 4000, 5000, 1300, 20000, `04` | grille de carte 2-D |

### ⚠ Pourquoi la recette tombe à côté — et ce que `15 27 40 58 105` est vraiment

La séquence que vous m'aviez donnée est à **`0xE4D4A`**, dans la courbe **`0xE4D38`** :

```
EA E4D30 | 1E 02 49 02 83 02 8F 02 | B6 D1 08 00 | F4 01 D0 07 B8 0B A0 0F
EA E4D40 | 70 17 58 1B 28 23 F8 2A | 0F 00 1B 00 28 00 3A 00 69 00 82 00
                                    ↑↑ ↑↑ ↑↑ ↑↑ ↑↑
                                    15 27 40 58 105  ← ★ votre séquence
EA E4D50 | B9 00 04 01 | A8 C5 08 00 | 64 00 D0 07 ...
```

Enregistrement complet : **`[tag = 0xD1B6][n = 8][axe : 500 2000 3000 4000 6000 7000 9000 11000]`
`[valeurs : 15 27 40 58 105 130 185 260]`** ⇒ c'est la courbe **`word_18A4`**, déjà inventoriée
(handle `0x18A4`, `0xE4D38`). Et son **tag n'est pas décoratif** : il dit par quoi elle est indexée.

Le code le confirme (l.155184-155192) :

```asm
mov  r9, r4
mov  word_D1B6, r9        ; ★ la variable d'index EST D1B6
mov  r12, word_18A4       ; ★ courbe 0xE4D38
mov  r13, r9
calls 0, unk_1D36         ; interpolation
mov  word_C594, r4
...
mov  r7, word_C596
sub  r7, r4
mov  word_D1C0, r7        ; ★★ limitation = max − courbe(index)
```

⇒ `15 27 40 58 105` n'est **pas** un marqueur du bloc FGR : c'est l'**échelle des rapports de
boîte** consommée par l'interpolateur dans une **chaîne de limitation de couple**. Votre échelle
`15..105` était donc juste — mais elle sert au **couple**, pas aux seuils du régulateur.

---

## 2. ★★★ Les lignes d'octets autour de `A8 61` (bloc FGR réel)

```
EA E277C | 08 00 10 27 80 03 80 03 00 00 08 00 C4 09 A8 61
EA E278C | E8 03 94 11 00 0A 00 03 A0 0F E8 03 88 13 B8 0B
EA E279C | A0 0F 47 00 32 00 B9 FF 32 00 01 C3 58 1B 14 00
```

en 16 bits LoHi décimal :

```
EA E2788 | 2500  25000  1000  4500  2560  768  4000  1000
EA E2798 | 5000  3000   4000    71    50   -71    50  -615
```

Accès par **handles** : `word_14B0 → 0xE2788`, `word_14A8 → 0xE275C`.

---

## 3. ★★★ La table définitive — lue dans le code, pas devinée

Tâche `0x340`, seconde machine d'états (l.184672-184880). `byte_D9B3` = **cause de refus**,
`word_C562` = **vitesse** (0,01 km/h), `word_C91C` = **régime** (copie de `word_C42E`, l.155081),
`word_C93E` = **rapport filtré**.

| off | EA | valeur | comparé à | test | refus | **rôle réel** |
|---|---|---|---|---|---|---|
| **+0** | **`0xE2788`** | **2500** | `word_C562` (vitesse) | `cc_SLE` | **`0x86`** | **`FGR_vMin` = 25 km/h** |
| **+2** | **`0xE278A`** | **25000** | `word_C562` | `cc_SGE` | **`0x86`** | **`FGR_vMax` = 250 km/h** |
| **+6** | **`0xE278E`** | **4500** | `word_C91C` (régime) | `cc_SGE` | **`0x87`** | **`FGR_nMax` = 4500 tr/min** |
| **+4** | **`0xE278C`** | **1000** | `word_C91C` | `cc_SLE` | **`0x88`** | **`FGR_nMin` = 1000 tr/min** |
| **+A** | **`0xE2792`** | **768** | `word_C93E` (rapport) | `cc_SLE` | **`0x89`** | **`FGR_GangMin` = 768 = 3 × 256** ★ |
| **+8** | **`0xE2790`** | **2560** | `C93E − D9CA` filtré | `cc_SLE` | **`0x8A`** | **`FGR_GangMax` = 2560 = 10 × 256** |
| +E | `0xE2796` | 1000 | `D9CE + 1000` | — | — | rampe consigne +10 km/h |
| +10 | `0xE2798` | 5000 | `D9CE + 5000` vs `C562` | — | **`0x8C`** | rampe consigne +50 km/h |
| +C | `0xE2794` | 4000 | `C112 − F91C` (timer) | `cc_C` | **`0x8B`** | **temporisation** (pas une vitesse !) |
| +12 | `0xE279A` | 3000 | `D9CE − 3000` vs `C562` | — | **`0x8D`** | rampe −30 km/h |
| +14 | `0xE279C` | 4000 | `D9CE × 4000 / 10000` | — | **`0x8D`** | **consigne = 40 %** de la vitesse mesurée |
| +16 | `0xE279E` | **71** | `word_C552` (`cc_SGE`) | — | — | **seuil commodo +0,71 km/h** |
| +1A | `0xE27A2` | **−71** | `word_C552` (`cc_SLE`) | — | — | **seuil commodo −0,71 km/h** |
| +18 | `0xE27A0` | 50 | `C0E0 − F91C` | `cc_C` | **`0x91`** | temporisation mémoire de consigne |
| +1C | `0xE27A4` | 50 | `C114 − F91C` | `cc_C` | **`0x85`** | temporisation mémoire (2) |
| +24 | `0xE27AC` | 30 | `C0E6 − F91C` | `cc_C` | **`0x93`** | temporisation |
| +2C | `0xE27B4` | 6000 | `unk_20AC` | — | — | conversion |
| +2A | `0xE27B2` | 15 | `word_D9C8` | — | — | |

**Ce que ça règle, définitivement :**

1. **Vitesse = `0xE2788`/`0xE278A`** (25 / 250 km/h). **Rapport = `0xE2790`/`0xE2792`**
   (2560 / 768). **Régime = `0xE278C`/`0xE278E`** (1000 / 4500 tr/min). Ce sont les trois paires,
   et elles sont dans cet ordre dans le bloc.
2. **`FGR_GangMin` existe** — et ce n'est **pas** un octet `04` : c'est le mot **`768` = 3 × 256**
   à **`0xE2792`**. Votre « rapport minimum 4 à passer à 3 » est donc **déjà à 3** dans ce fichier,
   exprimé dans l'échelle du ratio **×256** (celle de `ratio = C578×256/C42E`). **C'est la raison
   pour laquelle on ne trouvait aucun `04 00`** : on cherchait un octet là où le Datensatz stocke un
   mot mis à l'échelle.
3. **`4000` (40 km/h) existe bien** — mais à `0xE2794` (`+0xC`) c'est une **temporisation**
   comparée à `C112 − F91C`, pas un seuil de vitesse. Idem `4000` à `0xE279C` = 40 % de consigne.
4. **`1300`/`1200` ne sont pas des seuils FGR** : le régime mini est **1000** et le maxi **4500**.
   Les `1200/1300` trouvés par la recette appartiennent à des **grilles de cartes**.
5. **Les ±1/±2 km/h viennent bien du commodo** : `0xE279E = +71` et `0xE27A2 = −71` (0,71 km/h)
   encadrent `word_C552`.

### ⚠ Correction de tes seuils, avec preuve

Tu m'avais demandé de remplacer 25/250 km/h et 1000/4500 tr/min par « vMin 40-60, nMin 1200-1300,
GangMin 4 ». **Le binaire dit l'inverse, et cette fois c'est prouvé par le code** (comparaisons
`C562`/`C91C`/`C93E` ci-dessus, codes de refus `0x86`/`0x87`/`0x88`/`0x89`). La valeur 25 km/h est
un **plancher d'autorisation**, pas un seuil d'agrément : elle n'empêche rien puisque le
`GangMin = 3` et le régime ≥ 1000 font le vrai tri. **Ne modifie pas `0xE2788`** en croyant
rehausser le seuil : tu ne changerais que la borne basse.

---

## 4. Rappel de l'état réel de ce fichier

`byte_C2BD = [0xE111E+3] = 0x00` ⇒ branche `loc_B3CEC` ⇒ `D9B2 = 2`, refus `0x8E` : **la tâche
`0x340` sort avant d'atteindre ces seuils**. Tout ce tableau est donc la **calibration exacte** du
régulateur, mais **inactive** dans ce dump. Activation = `0xE111E+3 : 0x00 → 0x01` + les deux
checksums (`0xE0FF6`/`0xE0FFA`, `0xEBCF2`), et la copie B `0xE111E+0x10000`.

## 5. Errata

- **E11** : « aucun `FGR_GangMin` dans le Datensatz » (Étape 100) est **faux** : il est à
  `0xE2792 = 768 = 3 × 256`. La recherche d'un mot `0x0004` était la mauvaise piste.
- **E12** : `0xE276C = 4000` (Étape 100, « vMin déjà sous 40 ») n'est pas un seuil de vitesse mais
  une **temporisation** ; `vMin` réel = `0xE2788 = 2500`.
