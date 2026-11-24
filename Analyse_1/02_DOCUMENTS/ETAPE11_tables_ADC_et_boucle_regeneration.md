# ÉTAPE 11 — Les tables ADC (CTP confirmée) et la boucle de régénération FAP

Suite de l'étape 10. Deux objectifs : **(a)** remonter la chaîne ADC → table pour trancher CTP/CTN, **(b)** trouver la boucle qui déclenche la régénération.

---

## 1. Chaîne ADC → table : **votre intuition CTP est confirmée**

J'ai trouvé les **tables de conversion** dans la zone de calibration : ce sont des courbes 1-D dont l'**axe est un code ADC (0…1023)** — donc exactement ce que vous décriviez. En regardant la **monotonie des sorties**, on lit le type de sonde.

| Enreg. | Tag du canal | Axe ADC | Sorties | Unité | Monotonie | **Verdict** |
|---|---|---|---|---|---|---|
| `0xE30EC` | **`0xD04A`** | 10 → 991 (16 pts) | **3731 → 11381** | **K×10 = +100 → +865 °C** | **CROISSANTE** | **CTP — sonde de température gaz / EGT** ✔ |
| `0xE3444` | `0xD05E` | 32 → 969 (10 pts) | 3931 → 2331 | K×10 = +120 → −40 °C | DÉCROISSANTE | **CTN** (eau / air) |
| `0xE3548` | `0xD06C` | 40 → 962 (16 pts) | 4031 → 2331 | K×10 = +130 → −40 °C | DÉCROISSANTE | **CTN** |
| `0xE3842` | `0xD084` | 42 → 1002 (24 pts) | 4032 → 2331 | K×10 = +130 → −40 °C | DÉCROISSANTE | **CTN** |
| `0xE3076` | `0xD048` | 32 → 1023 (16 pts) | 11731 → 2849 | 1173 → 285 K = **+900 → +12 °C** | DÉCROISSANTE | **sonde gaz, 2ᵉ voie** (à confirmer : voir §2) |
| `0xE34F6` | `0xD066` | 192 → 1064 (12 pts) | 55 → 7739 | **convexe croissante** | CROISSANTE | **capteur de pression** (candidat dP FAP) |
| `0xE36D8` / `0xE3700` | `0xD07C` / `0xD07E` | 0 → 1023 | 0 → 4999 | 0…5000 = 0…100 % | linéaire | **paire redondante** (pédale ?) |
| `0xE3218` | `0xD054` | 0 → 1023 | 0 → 5000 | 0…100 % | linéaire | voie normalisée |
| `0xE325C` | `0xD056` | **102 → 922** | 0 → 15000 | — | butées | **sonde ratiométrique 0,5–4,5 V** |
| `0xE31B8` | `0xD052` | **20 → 1003** | 0 → 1000 | — | butées | ratiométrique |
| `0xE34A8` | `0xD060` | 20 → 1023 | 133 → 2500 | — | — | ratiométrique |
| `0xE3646` | `0xD070` | **102 → 691** | 0 → 10000 | 0…100 % | linéaire | ratiométrique 0,5 → 3,4 V |
| `0xE7EA6` | `0xD369` (octet) | 0 → 255 | 0 → 9961 | 0…100 % | CROISSANTE | position / pourcentage |
| `0xE3000` | `0xD03C` | 0 → 788 | 0 → 700 | — | linéaire | petit capteur |
| `0xE2FB2` | `0xD03A` | 485 → 970 | 600 → 1200 | — | croissante | plage haute |

### Conclusions

1. **La sonde de température des gaz est bien une CTP** : `0xD04A`, courbe **croissante** de **+100 °C (code 10) à +865 °C (code 991)**, en K×10. Votre hypothèse est validée par la table elle-même — c'est exactement l'argument que vous proposiez.
2. Les **sondes « classiques » (eau, air, gasoil) sont des CTN** : trois tables **décroissantes** couvrant **−40 → +130 °C** (`D05E`, `D06C`, `D084`). La coexistence des deux types dans le même calculateur est donc prouvée.
3. **Plusieurs canaux sont ratiométriques** avec des butées à **code 102 (~0,5 V) et 921 (~4,5 V)** (`D052`, `D056`, `D060`, `D070`) : c'est la signature des capteurs **0,5–4,5 V**, dont votre **capteur de pression différentielle**.
4. **Deux canaux ont exactement la même loi linéaire 0→5000** (`D07C` et `D07E`) : paire redondante pour contrôle de cohérence (pédale d'accélérateur ou sonde double).
5. Il existe des **tables « pleine échelle » non linéaires** (`D048` : 12 → 900 °C, décroissante ; `D066` : convexe 55 → 7739) qui sont les candidates pour la **2ᵉ sonde de température** et pour la **contre-pression**.

> **Réserve honnête** : la monotonie de la table prouve le **sens de variation code↔température**. La conclusion « CTN/CTP » suppose le montage standard (sonde vers la masse + résistance de tirage vers 5 V). Si le diviseur est inversé sur une voie, la conclusion s'inverse pour cette voie. Ici, la **coexistence** de tables croissantes (100–865 °C) et décroissantes (−40/+130 °C) reste néanmoins l'argument fort : elles ne peuvent pas être toutes du même type.

---

## 2. La boucle de régénération — machine à états trouvée

### 2.1 La machine à états (tâche `0x12C`, EA ≈ `0xA7DF0`)

Entrée conditionnée par le coding FAP `byte_C2BA` (`jmpa cc_Z, loc_A81E8`), puis **table de sauts** :

```asm
movb rl4, byte_C2BA ; jmpa cc_Z, loc_A81E8      ; ← pas de FAP ⇒ sortie
movb rl5, byte_D7A8                             ; ÉTAT COURANT
movb rl3, byte_D7A8
cmpb rl3, #5 ; jmpa cc_UGT, loc_A7F68           ; états 0..5 seulement
movbz r3, rl3 ; shl r3, #1 ; add r3, #0A04h     ; table de sauts en RAM basse 0x0A04
mov  r3, [r3] ; jmpi cc_UC, [r3]
```

Chaque état fait la même chose : **comparer un temporisateur `word_D7AA` à une durée de calibration**, décrémenter, et passer à l'état suivant quand c'est écoulé :

| État | Condition de sortie | Durée utilisée |
|---|---|---|
| `0` | `byte_C31A == 1` **et** `word_D7AA ≥ [word_18F6 + 2]` → état **1** | `[18F6+2]` |
| `1` | `byte_C31A == 2` → état **3** ; `byte_C31A == 3` → état **5** ; sinon `D7AA--` | — |
| `2` | `byte_C31A == 0` → état 0 ; sinon `D7AA ≥ [18F6+4]` → état **2**… | `[18F6+4]` |
| `3` | `word_D7AA ≥ [18F6+6]` → état suivant | `[18F6+6]` |
| `4` | `word_D7AA ≥ [18F6+8]` → état suivant | `[18F6+8]` |

* `byte_D7A8` = **état de régénération** (0…5) : c'est la variable à surveiller sur banc.
* `word_D7AA` = **temporisateur** (décrémenté à chaque appel de tâche).
* `byte_C31A` = **état demandé** (par la supervision).
* `word_18F6` = **bloc de calibration des durées d'état** (`+2`, `+4`, `+6`, `+8`…).

### 2.2 Comment la **demande** est élaborée (dans la tâche EGT, EA `0xA99xx`)

```asm
; rampe en fonction de word_C584 entre deux seuils de calibration
r5 = [word_1952+2Ah] ; r8 = [word_1952+2Ch] − r5
[r0+18h] = unk_20AC(C584 − r5, 10000, r8)        ; 0 → 10000 (0 → 100 %)
[r0+18h] = unk_20AC([r0+18h], [word_1952+2Eh], 10000)   ; × facteur
word_D2BE = [r0+18h]                             ; ← rampe publiée
r9 = unk_1D36(word_1950, word_C586)              ; COURBE SUR L'EGT
cmp r9, word_C584
  si r9 <  C584 → word_D7EE = 0 ; byte_D7EC = 0   (effacement)
  sinon         → 3 jeux de seuils selon le coding :
                    word_D7EE = [1952+37h] / byte_D7EC = [1952+38h]
                    word_D7EE = [1952+32h] / byte_D7EC = [1952+33h]
                    word_D7EE = [1952+39h] / byte_D7EC = [1952+3Ah]

loc_A9AAC:
  r4 = word_D7DA ; cmp r4, word_D7EE
  si D7DA >= D7EE → word_D7DA++ ; word_D7DC = 0 ; word_D2BC = 0 ; byte_C316 bit0 = 0
  sinon          → byte_C316 bit0 = 1              ; ← DEMANDE ACTIVE
                   si (byte_C2FA & 8) == 0 :
                      si byte_D7EC <= word_D7DC → word_D7DC--
                      sinon → [r0+1Ah] += [word_1952+34h] ; word_D2BC = [1952+34h]   ; INTÉGRATEUR
```

| Variable | Rôle |
|---|---|
| **`word_D7EE`** | **seuil de déclenchement** (3 jeux de valeurs selon le coding) |
| **`byte_D7EC`** | **durée exigée** |
| **`word_D7DA`** | compteur de la condition (progressif) |
| **`word_D7DC`** | décompte de durée |
| **`word_D2BC`** | **intégrateur** (charge de suie ?) avec incrément `[1952+34h]` |
| **`word_D2BE`** | **rampe** (0…100 %) sur la température `word_C584` |
| **`byte_C316` bit 0** | **demande de régénération active** |
| **`byte_C2FA` bit 3** | **inhibition** de la demande |
| `word_1950` | **courbe sur l'EGT** `C586` qui autorise la demande |
| `word_1952` | bloc de calibration FAP (offsets `20h`, `26h`, `2Ah`, `2Ch`, `2Eh`, `32h`-`39h`, `3Ch`) |

### 2.3 L'estimateur de charge (candidat « suie »)

EA `0xA40xx` (tâche suivante) :

```asm
word_D756 = min(word_C3E0, 0x7FFF)
mov  word_D1F4, word_D756          ; ← word_D1F4 est un TAG du Datensatz (0…5000, 3 axes !)
mov  word_C8FE, word_C38E          ; ← C38E = voie ADC (626…960)
unk_20AC(D756, D756, 10000)
unk_20AC(word_C588, …, word_C8FE)  ; ← C588 = TEMPÉRATURE (−10…+60 °C)
unk_20AC(…, [word_18E6], 1000)
```

* `word_D756` (27 références) est dérivé de `word_C3E0` (sortie du service indirect `word_1DA8`) ;
* il est **publié dans `word_D1F4`**, qui est un **tag du Datensatz** (axe 0…5000 utilisé par 3 courbes) ⇒ la grandeur est bien réutilisée comme axe de correction ;
* il est combiné à **une voie ADC (`C38E`) et à une température (`C588`)** ⇒ structure typique d'un **estimateur de charge** (débit × température × facteur).

---

## 3. Ce qui reste à trouver (et où chercher précisément)

| Élément de votre liste | État | Piste concrète |
|---|---|---|
| **Seuil kilométrique** | **non trouvé dans cette moitié de flash** | Les compteurs km des EDC15 vivent en **EEPROM** (hors image). Dans l'image, seul le **temporisateur d'états** (`word_D7AA` / `word_18F6`) est présent. À vérifier : `word_19E6`/`word_19DC` (bloc de seuils) et `word_D79E` (compteur 4 refs). |
| **Capteur de pression différentielle** | **candidat identifié, chaîne non bouclée** | Voie **`0xD066`** (courbe convexe 55 → 7739) ou **`0xC38E`** (ADC 626…960). Test : chercher la courbe qui convertit cette voie en **mbar** puis une carte **(débit d'air × dP) → seuil**. |
| **Seuil qui dépend de la pression et du débit** | **non trouvé tel quel** | Les cartes à axe **`C3E6` (débit d'air)** sont `0xE8444` et `0xE8872` : vérifier si l'une d'elles est la **loi de seuil de dP** (l'axe Y d'une carte de seuil serait alors la pression). Recherche à faire sur les 40 cartes restantes avec un axe ADC. |
| **Estimateur de suie** | **candidat : `word_D756` → `word_D1F4`** | Suivre `word_C3E0` jusqu'à son producteur (`word_1DA8`, service indirect) et `word_D1F4` jusqu'aux 3 courbes qui l'utilisent. |
| **Post-injection** | **non localisée** (étape 10) | Le terme additif `word_C69E` reste le seul candidat ; suivre `word_C77C` (somme de 2 courbes dont une en température). |
| **La demande → état** | **prouvé** | `byte_C316` bit 0 (demande) → `byte_C31A` (état demandé) → machine `byte_D7A8` (états 0…5). |

**Le point qui manque pour boucler la boucle** est le lien **`byte_C316` → `byte_C31A`**. Dans la moitié de flash présente, `byte_C316` est écrit mais `byte_C31A` est seulement **lu** dans la machine à états ⇒ ce transfert se fait **dans la moitié basse absente**. C'est le seul chaînon manquant de la boucle.

---

## 4. Ce que je peux affirmer aujourd'hui (synthèse)

| Fait | Preuve |
|---|---|
| **La sonde de température gaz est une CTP** (100 → 865 °C, courbe croissante) | `0xE30EC`, tag `D04A` |
| Les sondes eau/air/gasoil sont des **CTN** (−40 → +130 °C, courbes décroissantes) | `0xE3444`, `0xE3548`, `0xE3842` |
| Plusieurs capteurs sont **ratiométriques 0,5–4,5 V** (butées ADC 102/921) | `D052`, `D056`, `D060`, `D070` |
| La régénération est une **machine à 6 états** (0…5) avec durées calibrées | tâche `0x12C`, `byte_D7A8`, `word_18F6` |
| La **demande** vient d'une **courbe sur l'EGT** + **3 jeux de seuils** selon le coding | `word_1950`, `[1952+32h…3Ah]` |
| Il existe un **intégrateur** (`word_D2BC`) et une **rampe** (`word_D2BE`) | EA `0xA9AF2`-`0xA9B1E` |
| Tout est conditionné par le coding FAP `byte_C2BA` | 63 références |

**Prochaine étape logique** : décoder les **blocs `word_18F6` et `word_1952`** (les durées et seuils de régénération) en retrouvant leurs valeurs dans la zone de calibration, puis boucler sur `byte_C31A` via un point d'arrêt pendant une régénération forcée.
