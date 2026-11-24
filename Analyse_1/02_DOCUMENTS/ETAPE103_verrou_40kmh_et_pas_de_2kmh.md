# ÉTAPE 103 — ★★★ Le verrou des 40 km/h, le pas de ±2 km/h, et les 16 bits d'inhibition

> Tu avais raison sur le pas : **±2 km/h**. Et le blocage à 40 km/h **existe bien** — je le croyais
> dans `FGR_vMin`, il est en réalité dans un **second bloc de calibration** que je n'avais pas encore
> résolu : **`word_14AA → 0xE2762`**.

---

## 1. ★★★ `word_14AA → 0xE2762` : le bloc « consigne » (9 mots)

```
EA E2762 | 40    0    200   500   20000  4000   400   0
EA E2772 | 100   300
   octets : 28 00 | 00 00 | C8 00 | F4 01 | 20 4E | A0 0F | 90 01 | 00 00 | 64 00 | 2C 01
```

| off | EA | valeur | rôle | preuve |
|---|---|---|---|---|
| +0 | `0xE2762` | **40** | temporisation appui bouton | l.185096 `cmp r4,[r2]` |
| +2 | `0xE2764` | 0 | seuil 0 | l.185391 |
| **+4** | **`0xE2766`** | **200** | **★ PAS = ±2,00 km/h** | l.185135 `add r2, word_C562` / l.185275 `sub r3, r2` |
| +6 | `0xE2768` | **500** | tolérance 5 km/h avant re-synchro | l.185128 |
| +8 | `0xE276A` | **20000** | **plafond de consigne = 200 km/h** | l.185157 |
| **+A** | **`0xE276C`** | **4000** | **★★★ PLANCHER = 40 km/h** | l.185291 / **185301** / 185806 / 185856 |
| +C | `0xE276E` | 400 | incrément appui long = 4 km/h | l.185028 `add r3, word_D9CE` |
| +E | `0xE2770` | **0** | **masque d'options** (tout désactivé) | 10 sites |
| +10 | `0xE2772` | 100 | temporisation 1 s | l.183752 |
| +12 | `0xE2774` | 300 | (recoupe `word_14AC+0`) | — |

### Le pas, exactement

```asm
; appui « + » court — l.185128-185142
mov  r5, word_14AA
mov  r2, [r5+#6]          ; 500 = tolérance
cmp  r4, r2               ; |filtre(C562−D9CE)| ≤ 5 km/h ?
...
mov  r2, [r5+#4]          ; ★ 200
add  r2, word_C562        ; consigne = vitesse courante + 200
cmp  r2, [r5+#8]          ; ≤ 20000 ?
mov  word_D9CE, r2
```

```asm
; appui « − » court — l.185275-185278
mov  r2, [r5+#4]          ; ★ 200
mov  r3, word_C562
sub  r3, r2               ; consigne = vitesse courante − 200
mov  word_D9CE, r3
```

⇒ **`0xE2766 = 200` = ±2,00 km/h par impulsion courte.** Pour **±1,00 km/h** : `200 → 100`.

**Errata E13** : j'avais présenté `0xE279E` / `0xE27A2` (`+71` / `−71`) comme « le pas du commodo ».
Faux : ce sont des **seuils de bande morte** (±0,71 km/h autour de `word_C552`) qui décident
seulement si la consigne doit être recalée. Le pas, c'est `0xE2766`.

### ★★★ Le verrou des 40 km/h — quatre sites, tous concordants

```asm
; l.185291 — la consigne ne peut PAS descendre sous 40 km/h
mov  r4, word_14AA
mov  r5, [r4+#0Ah]        ; ★ 4000
cmp  r5, word_D9CE
jmpr cc_SLE, loc_B474A
mov  r5, [r4+#0Ah]
mov  word_D9CE, r5        ; ★ D9CE = 4000 (clamp)
```

```asm
; l.185299 — et l'engagement est REFUSÉ si la vitesse réelle < 40 km/h
mov  r5, [r4+#0Ah]        ; ★ 4000
cmp  r5, word_C562
jmpr cc_SLE, loc_B476A
movb rl4, #60h
movb byte_D9CC, rl4       ; ★ état 0x60 = attente / refus
```

```asm
; l.185806 et l.185856 — recalage forcé de la consigne à 40 km/h
mov  r5, [r4+#0Ah]
cmp  r5, word_C562
jmpr cc_SLT, loc_B4CDC
mov  r5, [r4+#0Ah]
mov  word_D9CE, r5        ; D9CE = D9C4 = 4000
```

⇒ **C'est ça, le « bloqué à 40 km/h ».** Ce n'est ni `FGR_vMin` (25 km/h, `0xE2788`), ni le rapport,
ni `C2BD` : c'est le **plancher de consigne `0xE276C = 4000`**, qui agit *deux fois* — il clampe la
consigne **et** il interdit l'engagement tant que `C562 < 4000`.

**Cohérence totale** : `0xE2788 = 2500` (autorisation) et `0xE276C = 4000` (consigne). Le plus
contraignant des deux gagne ⇒ **40 km/h en pratique**. Les deux blocs sont cohérents avec ton
observation de terrain, et **ta valeur de 40 km/h était juste** — simplement pas au même endroit.

---

## 2. ★★ Les 16 bits d'inhibition (`l.184447-184660`)

Motif répété 16 fois — `D9B2 = 2` et `D9B3 = 0x8E` (même refus que `C2BD = 0`) :

```asm
movb rl4, word_FD20+1     ; un drapeau RAM
jmpr cc_Z, suivant
mov  r4, word_14A8
mov  r5, [r4]             ; ★ [0xE275C] = 0xBFFE = masque d'activation
and  r5, #1               ; un bit par inhibition
jmpr cc_Z, suivant
movb rl4, #2
movb byte_D9B2, rl4       ; ★ refus
movb rl5, #8Eh
movb byte_D9B3, rl5       ; ★ cause
```

Drapeaux identifiés : `word_FD28+1` (bit #10), `word_FD2A+1` (#20), `word_FD3E+1` (#80),
`byte_FD57` (#400), `word_FD3A+1` (#4000), `word_FD20+1` (#1), `byte_FD23` (#2).

**Masque `0xE275C = 0xBFFE`** = `1011 1111 1111 1110` ⇒ **seuls les bits 0 et 14 sont désactivés**
(toutes les autres inhibitions sont armées). Le bit 14 correspond à `word_FD3A+1`, le bit 0 à
`word_FD20+1` — c'est le crochet `word_FD3A.7` qui produisait déjà `D9B0 = 6` / `D9B2 = 2`.

⇒ **Réponse à ta question** : le blocage vient bien, *in fine*, d'un `D9B2 = 2` / `D9B3 = 0x8E`
écrit par **`C2BD = 0`** ou par **l'un des 16 bits** ci-dessus. Mais le verrou des 40 km/h, lui, est
**en aval** de tout ça, dans `0xE276C` : c'est un comportement nominal, pas un refus.

---

## 3. Les blocs voisins, résolus dans la foulée

### `word_14B2 → 0xE27B6` — rampes de consigne
`500 · 400 · masque 0xFFFE · 45 · 3 · 100 · 108 · 3 · 100 · 600 · 2500 · 5000`
- `+0 = 500` : `rampe = 500 × C562 / 10000` (l.185766-185768) → `D9BC = rampe + [+2]=400`
- `D9C0 = D9BC / 50`, `D9BE = (D9BC/50) × 1310` (l.185774-185786) — ✎ recoupe les rampes déjà connues
  (`D9BC = 500·v/10000 + 400`, état 3) ✔
- `+8 = 3` : `shl #1` puis `add` → **pas de 6** dans `sub_B3572` (l.183541), l'avance fine de consigne
- `+4 = 0xFFFE` : second masque d'options, comparé à `C552` (l.185870, l.185904)

### `word_14AC → 0xE2774` — ★ un jeu de seuils **× 256** non référencé
`300 · 1024 · 512 · 768 · 8 · 10000 · 896 · 896 · 0 · 8 · 2500 · 25000`

| EA | valeur | ÷256 |
|---|---|---|
| `0xE2776` | **1024** | **4** |
| `0xE2778` | **512** | **2** |
| `0xE277A` | **768** | **3** |

⇒ **`4 / 2 / 3` en Q8.8**, exactement les valeurs de `GangMin` que tu cherchais ! Mais **aucune
référence code** à `word_14AC` dans `clean.asm` : ce sont des **seuils de réserve**, présents dans le
Datensatz mais non lus par cette version de logiciel. Le seuil réellement utilisé reste
**`0xE2792 = 768` (= 3)**.

---

## 4. Ce qu'il faut modifier, et où — récapitulatif

| objectif | EA | actuel | cible | copies |
|---|---|---|---|---|
| **autoriser l'engagement à 25 km/h** | **`0xE276C`** | **4000** | **2500** | `+0x10000` |
| passer le pas à ±1 km/h | `0xE2766` | 200 | 100 | `+0x10000` |
| autoriser la 2e | `0xE2792` | 768 (3) | 512 (2) | `+0x10000` |
| abaisser la borne basse (déjà 25) | `0xE2788` | 2500 | — | — |
| **activer le régulateur** | `0xE111E+3` | **`0x00`** | **`0x01`** | `+0x10000` |

⚠ Chaque modification = **deux blocs** (`0xE…` et `0xF…`) **et** recalcul des checksums
(`0xE0FF6`/`0xE0FFA`, `0xEBCF2`). Et **rien ne fonctionnera** tant que `byte_C2BD = 0` : commence
par `0xE111E+3`, sinon les autres valeurs ne seront jamais lues.

## 5. Errata
- **E13** : `0xE279E`/`0xE27A2` (`±71`) ne sont **pas** le pas du commodo mais une **bande morte**
  de ±0,71 km/h. Le pas est `0xE2766 = 200` (±2,00 km/h).
- **E14** : `0xE276C = 4000` n'est **ni** une temporisation (Étape 102) **ni** un seuil de refus :
  c'est le **plancher de consigne 40 km/h** — le verrou observé sur le véhicule.
