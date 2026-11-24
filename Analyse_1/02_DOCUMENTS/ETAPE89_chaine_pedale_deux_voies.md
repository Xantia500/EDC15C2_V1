# ÉTAPE 89 — La chaîne pédale est retrouvée : deux voies `0x0F844` / `0x0F854`, fenêtres `20/102/921/1003`, **moyennage** et **delta `C3A6`**

> Confirmé : c'est la tâche **`0x326`**, elle lit **deux** résultats ADC dans le même passage, applique
> **deux portes de plausibilité indépendantes**, fait la **moyenne** (`add` + `shr #1`) et calcule un
> **delta** (`word_C3A6 = référence − valeur`) avec drapeau et bornage. Le tout avec des seuils qui
> tombent exactement sur **0,1 V / 0,5 V / 4,5 V / 4,9 V**.

---

## 1. Le bloc, tel qu'il est écrit (l.213301-213400)

```c
scxt  CC2_CC27, #326h            ; tâche 0x326  = la pédale
movbz r11, byte_C9F1
bmov  r11.4, r11.3               ; recopie d'un bit d'état

mov   r0, word_151C              ; descripteur de conversion (calibration)
mov   r9, #0F844h                ; ← voie 1 (résultat ADC)
calls 0Ch, sub_C4AAE             ;   conversion brut → grandeur
mov   r1, word_151E
calls 0Ch, sub_C46D2             ;   porte de plausibilité + delta
mov   word_D04E, r9              ; valeur voie 1
mov   word_D052, r8
push  r11 ; push r8 ; mov r12, r10

mov   r0, word_151C
mov   r9, #0F854h                ; ← voie 2 (résultat ADC)
calls 0Ch, sub_C4AAE
mov   r1, word_151E
calls 0Ch, sub_C46D2
mov   word_D050, r9              ; valeur voie 2

jnb   r11.2, loc_C48B8
mov   word_C36C, r10             ; ← sélection par le bit r11.2
jmpr  loc_C48BC
loc_C48B8: mov word_C36C, r12

loc_C48BC:  add r10, r12         ; ★ MOYENNE des deux voies
            shr r10, #1
```

**Deux voies, un seul descripteur, une moyenne.** Et un **aiguillage** `r11.2` qui choisit l'une ou l'autre
selon l'état du diagnostic.

| grandeur | rôle |
|---|---|
| `word_D04E` | valeur voie 1 (`0x0F844`) |
| `word_D050` | valeur voie 2 (`0x0F854`) |
| `word_D052` | grandeur annexe voie 1 |
| `word_C36C` | **valeur retenue** (moyenne, ou voie choisie) |
| `word_C3A4` | valeur par défaut, recopiée depuis `[h 0x151C + 8]` |

## 2. `sub_C46D2` — la porte de plausibilité et le delta (l.213203)

```c
r10 = [r0+#2] ; if (r10 <  r9) → erreur  (bfldl r11, #7, #5)   ; trop bas
r10 = [r0+#4] ; if (r9 < r10)  → erreur  (bfldl r11, #7, #6)   ; trop haut
sinon r10 = r9 ; bfldl r11, #7, #0                              ; bits d'erreur remis à 0
```

Puis, sous conditions d'activation (régime `C91C` ≥ `[r2+#0Ch]`, `C5FE`, `C5A4`, `byte_C8F9`) :

```c
r3 = [r2+#6] − r9
word_C3A6 = r3            ; ★ LE DELTA
byte_C216 = 1             ; drapeau « delta calculé »
```

puis **bornage du delta** entre `[r2+#0Ah]` et `[r2+#8]`.

Et un **compteur de temporisation** : `addb byte_C9F2, ONES` — c'est le filtre/décompte qui interdit de
valider un défaut sur un seul échantillon. C'est la structure classique « erreur → décompte → défaut ».

## 3. Les seuils, et pourquoi ils tombent juste

Le descripteur `word_1528` → **`EA 0xE31FE`** :

| offset | valeur | lecture |
|---|---|---|
| `+#0` | **3131** | seuil haut (40,0 °C si Kelvin ×10) |
| `+#2` | **3031** | 30,0 °C |
| `+#4` | **2831** | 10,0 °C |
| `+#6` | **102** | référence du delta |
| `+#8` | **9** | borne haute du delta |
| `+#0Ah` | **−12** | borne basse du delta |
| `+#0Ch` | **100** | seuil d'activation (régime) |

Et le descripteur de fenêtre `word_151E` → **`EA 0xE31B8`** : `[4]` puis **`20 · 102 · 921 · 1003`**.

Sur un convertisseur **0…5 V en 1023 pas** :

| brut | tension | rôle |
|---|---|---|
| **20** | **0,10 V** | plancher absolu |
| **102** | **0,50 V** | **début de course utile** |
| **921** | **4,50 V** | **fin de course utile** |
| **1003** | **4,90 V** | plafond absolu |

⇒ **c'est exactement la spécification que tu décris** (deux signaux dans 0,5-4,5 V, l'un la moitié de
l'autre), et c'est bien la tâche `0x326` que la table des voies ADC associait à « 0 sous 0,5 V,
100 % entre 0,5 et 4,5 V ».

## 4. Ce qui reste à établir

| point | état |
|---|---|
| deux voies lues séparément | ✅ lu dans le code |
| fenêtres 0,5-4,5 V | ✅ lues dans la calibration (`0xE31B8`) |
| moyenne des deux voies | ✅ `add` + `shr #1` |
| delta + drapeau + bornage | ✅ `word_C3A6`, `byte_C216`, bornes −12/+9 |
| temporisation anti-rebond | ✅ `byte_C9F2` décrémenté |
| **rapport 2:1 entre les deux voies** | ⏳ non vu explicitement : il est probablement **dans la courbe de conversion** (`sub_C4AAE` + descripteur `0x151C`) et non dans un test arithmétique |
| conversion finale en **0…10 000** | ⏳ pas encore localisée (identifiant de `C36C` à vérifier) |
| **delta « éco / sport »** | ⏳ `word_C3A6` est lu en `l.151547`, `l.151904` et dans `sub_A0CCC+246` — c'est là qu'il faut aller |

## 5. `C562` n'est pas dans cette chaîne

Vérifié : la chaîne pédale écrit `D04E`, `D050`, `D052`, `C36C`, `C3A4`, `C3A6`, `byte_C216`, `byte_C9F2` —
**jamais `C562`**. `C562` n'apparaît que comme **argument de `unkà1FE8`** (étape 88 §4).
⇒ ton intuition « c'est lié à l'IQ, c'est dans le code qui gère l'injection » reste la bonne piste, mais
elle se joue **en aval** de la pédale : la pédale sort `C36C`, et c'est **plus loin** que la grandeur
devient une demande d'injection.

## 6. Consignation

**`CATALOGUE_MAITRE.md` § 13 B.36** — tâche `0x326`, deux voies `0x0F844`/`0x0F854`, `sub_C4AAE`
(conversion) et `sub_C46D2` (plausibilité/delta), moyenne `add`+`shr #1` → `C36C`, seuils `20/102/921/1003`
= 0,1/0,5/4,5/4,9 V, delta `C3A6` borné −12/+9, `byte_C9F2` anti-rebond, et constat que `C562` est en aval.
