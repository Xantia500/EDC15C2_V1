# ÉTAPE 95 — La bibliothèque est **effacée** · le rapport engagé : test BVM · le bloc de paramètres du régulateur

Trois résultats durs cette fois, dont un qui **borne définitivement** ce qui est prouvable dans ce
dump : la bibliothèque de calculs (interpolations, rampes, filtres) **n'est pas dans le fichier**.

---

## 1. ★★★ La bibliothèque de primitives est **remplie de `0xC3`**

J'ai suivi les appels indirects de l'étape 93 jusqu'au bout : les 77 cibles `unk_XXXX` du **segment
0** (base `0x80000`) sont **vides**.

| mesure | valeur |
|---|---|
| plages de `0xC3` ≥ 32 octets | **27** |
| total d'octets `0xC3` | **108 490** (≈ 106 Ko) |
| **tête du segment 0** (`fo 0x00000` → `0x07FFF`) | **32 768 octets `0xC3`** — les 32 premiers Ko |
| autre grande plage | `fo 0x0DAD0`, 1 424 o |

Vérification directe des cibles :

```
fo 0x1D36 : C3 C3 C3 …      unk_1D36  (interpolation 1-D)
fo 0x1D50 : C3 C3 C3 …      unk_1D50  (interpolation 2-D)
fo 0x1FE8 : C3 C3 C3 …      unk_1FE8  (coordinateur / rampe)
fo 0x20AC : C3 C3 C3 …      unk_20AC  (mise à l’échelle)
fo 0x2160 · 0x2196 · 0x24BA · 0x2EE2 : C3 …
```

### Les 12 primitives les plus appelées (toutes effacées)

| primitive | appels | rôle déduit des sites |
|---|---|---|
| `unk_20AC` | **250** | mise à l'échelle multiplicative |
| `unk_1D36` | **168** | interpolation **1-D** |
| `unk_7C2` / `unk_7B4` | 110 + 110 | entrée/sortie de section critique (verrous `CC2_CC27`) |
| `unk_1D50` | **72** | interpolation **2-D** |
| `unk_1D7E` / `unk_1D6C` | 54 / 44 | non identifiés |
| `unk_2160` | 27 | conversion (état/vitesse) |
| `unk_2128` | 24 | non identifié |
| `unk_2A9A` / `unk_2EBA` / `unk_20F6` | 20 / 17 / 16 | non identifiés |

**77 primitives distinctes**, de l'ordre de **1 000 sites d'appel** : c'est le cœur calculatoire du
calculateur, et il est **absent**. Conséquence méthodologique à consigner : *toute* conclusion sur un
quotient, une rampe ou un filtrage passe obligatoirement par les **conventions d'appel**, jamais par
le corps.

---

## 2. ★★ Les conventions d'appel, déduites par les sites (acquis)

### 2.1 `unk_1D36` = interpolation 1-D : `(r12 = EA de la courbe, r13 = X)`

Preuve par `sub_B2A02` (l.182240) :

```asm
mov r12, word_1B48        ; 0xE87EE = [C562][6][1500 2100 7000 9000 11500 20000] → [0 10000 10000 20496 20496 0]
mov r13, word_C562        ; ★ X = la vitesse
calls 0, unk_1D36
```

### 2.2 ★★ `unk_1D50` = interpolation 2-D : `(r12 = EA de la carte, r13 = variable du **tagY**, r14 = variable du **tagX**)`

Preuve par `locs_B28AA` (l.182104) :

```asm
mov r12, word_1B42        ; 0xE868C = [C3D2][6][…] × [C562][6][…]
mov r13, word_C908        ; = C3D2  (température d’eau)  ← PREMIER axe du tag
mov r14, word_C562        ; = vitesse                     ← SECOND axe du tag
calls 0, unk_1D50
```

⇒ **l'ordre est (Y, X)** : `r13` reçoit la variable du **premier** axe écrit dans la carte, `r14`
celle du **second**. C'est une convention utilisable partout désormais.

### 2.3 `unk_20AC` = `(r12 = a, r13 = b, r14 = 10000) → a × b / 10000`

```asm
mov r12, r9               ; A
mov r13, r8               ; B
mov r14, #2710h           ; 10000
calls 0, unk_20AC         ; → A·B/10000
```

### 2.4 `unk_1FE8` = coordinateur à **10 arguments** (4 registres + 5 sur la pile)

Deux sites seulement ; voici leur dépouillement comparé.

| emplacement | site A — `loc_B5904` (l.187031, **régulateur**) | site B — `loc_BB566` (l.196459, bloc `DB64…`) |
|---|---|---|
| `r12` | `word_1B78` **ou** `word_1B76` (calibration) | `#0DBAEh` (RAM) |
| `r13` | `word_1B74` **ou** `word_1B72` (calibration) | `#0DBA4h` (RAM) |
| `r14` | `#0DA0Ah` (état) | `r7` (état) |
| `r15` | `#0D9FEh` (état) | `#0DB6Ah` (état) |
| pile 1 (dernier poussé) | **`word_C562`** — la vitesse | `word_C990` |
| pile 2 | `r9` (vitesse courante / objectif) | `r8` |
| pile 3 | `#0DA04h` | `#0DB64h` |
| pile 4 | `#0D9F6h` | `#0DB68h` |
| pile 5 | `0` | `[r0]` (valeur d'entrée) |

**Lecture** : `(r12, r13)` = **couple de taux (montée, descente)** — en calibration fixe au site A,
en **RAM mutable** au site B (taux adaptatifs) ; `r14`, `r15` et deux pointeurs de pile = **états
internes** ; le premier argument de pile = la **grandeur d'entrée**, qui est **`C562`, la vitesse**,
dans le régulateur.

⇒ **C'est le « coordinateur » de la demande : il prend la vitesse, un objectif, un couple de taux et
des états, et sort une valeur rampe.** Le corps étant effacé, la formule exacte reste hors d'atteinte
— mais **la structure de la reprise est là** : c'est le seul endroit où vitesse, objectif et taux se
rencontrent.

---

## 3. Le rapport engagé (BVM) — le test, et sa réponse

### 3.1 Ce que dit le fichier

| fait | mesure |
|---|---|
| écrivains de `byte_C240` (code rapport) | **4** : trois défauts `[word_1658+8]` (l.139477, 140993, 141203) + **un nibble CAN** `byte_C871 >> 4` (l.141208) |
| **lecteurs** de `byte_C240` | **UN SEUL** : `loc_AFBE8`, **l.177553** |
| divisions (124 sites) touchant `C562` | **0** |
| sites combinant `C562` **et** `C91C` dans un calcul | **1** : `sub_B2A02` (un **produit** de corrections, pas un quotient) |

### 3.2 Ce que fait ce lecteur unique

```asm
loc_AFBE8:                              ; l.177553
  movb rl4, byte_C240
  andb rl4, #0Fh                        ; code 0…14
  cmpb rl4, #0Eh
  jmpr cc_UGT, loc_AFCB4                ; > 14 → repli sur l'indice 0
  movbz r4, rl4
  shl  r4, #1
  add  r4, #0A2Ch                       ; ★ table de sauts à 0xA2C + 2×code
  jmpi cc_UC, [r4]
; 15 branches identiques, une par rapport :
  mov  r4, word_1B22
  movb rl5, [r4+#k]                     ; k = 0 … 14
  movbz r9, rl5
```

Et `word_1B22` → **EA `0xE835A`**, **15 octets** :

```
+0  0x30      = 48        ; code 0   (point mort / inconnu ?)
+1  0x01      =  1        ; code 1
+2  0x02      =  2        ; code 2
+3  0x03      =  3        ; code 3
+4  0x04      =  4        ; code 4
+5…+8   0     =  0        ; codes 5..8
+9  0x0B      = 11        ; code 9
+10…+14 0     =  0
```

⇒ Le rapport engagé est utilisé comme **index d'une table de 15 octets**, qui donne une valeur
`r9` (0→48, 1→1, … 9→11) : une **identification de rapport** (pas un quotient).

### 3.3 Verdict, et le test qui trancherait

**Dans le code visible, le rapport n'est pas calculé.** Trois refuges possibles :

1. **le CAN** — mais `byte_C2B7 & 1 = 0` dans cette calibration (`0x141C+0x0E = 0x08`) ⇒ la trame
   `0x349` **n'est pas armée** ;
2. **le défaut figé** `[word_1658+8]` — c'est ce que le code fait réellement aujourd'hui ;
3. **la bibliothèque effacée** (§1) — un quotient peut y être caché, y compris sous forme de
   multiplication par l'inverse fixe-point, ce que mon filtre ne peut pas voir.

**Le test décisif, sur le banc** : relever `byte_C240` (ou la mesure diag qui l'expose) **au ralenti,
en 3ᵉ à 50 km/h puis en 5ᵉ à 50 km/h**.

- si le code **change** ⇒ il est calculé (quelque part, y compris dans la bibliothèque) ;
- si le code **reste identique** ⇒ il est figé au défaut, et les cartes « par rapport » travaillent
  toutes sur la même ligne.

C'est le seul moyen de fermer la question : le fichier ne la contient pas.

---

## 4. ★★ Une carte de **protection thermique** à très haute température, modulée par la vitesse

`sub_B2A02` (l.182240) — le seul endroit qui combine régime, température **et** vitesse :

```asm
C908 = C3D2 ; C91C = C42E
r12 = word_1B4A ; r13 = C91C (régime) ; r14 = C908 (T° eau) ; calls unk_1D50
r9  = résultat                                  ; carte A
r12 = word_1B48 ; r13 = C562 ;                 calls unk_1D36
r8  = résultat                                  ; courbe B (sur la VITESSE)
r12 = r9 ; r13 = r8 ; r14 = #2710h ;           calls unk_20AC
→ A × B / 10000
```

| élément | EA | contenu |
|---|---|---|
| carte A (`0x1B4A`) | `0xE880A` | `[C42E][6][1300 1800 2200 2800 3300 4000]` × `[C3D2][6][`**`3841 3851 3861 3891 3921 3951`**`]` |
| courbe B (`0x1B48`) | `0xE87EE` | `[C562][6][1500 2100 7000 9000 11500 20000]` → `[0 10000 10000 20496 20496 0]` |

L'axe de température **111 / 112 / 113 / 116 / 119 / 122 °C** est un **seuil de surchauffe** : la
carte n'agit que dans cette fenêtre très étroite. Et la courbe de vitesse **double le facteur**
(10 000 → 20 496 = ×2,05) entre 21 et 70 km/h, puis **l'annule à 200 km/h**.

⇒ **Correction de protection thermique, amplifiée en roulage, coupée à très haute vitesse.** C'est
un candidat sérieux pour le **protoxyde / post-injection de refroidissement** — à confirmer en
identifiant le consommateur de `sub_B2A02` (`seg015:27E6`).

---

## 5. Le bloc de paramètres du régulateur (`0xE8C5A` → `0xE8CD0`)

| handle | EA | contenu | rôle |
|---|---|---|---|
| `0x1B6C` | `0xE8C5A` | `FFFF · 0 · 0x41 · FFFE · 0 · 0 · 0 …` | descripteur du **défaut `0x40DF`** (seuils, `0xFFFF` = pas de limite) |
| `0x1B6E` | `0xE8C60` | `FFFE · 0 …` puis **`0F10 · 0F08 · 0F80`** | trois **identifiants de mesure** `0x0Fxx` (même famille que `0xE2728`) |
| `0x1B70` | `0xE8C80` | `0 · 30000 · 0 · 35536 · 30000 · 0 · 10000 · 0 · 0 · 0 · 0 · 2` | **seuils** : `+30000` (300 km/h), `35536` = **−29968** en signé, `10000` = 100 km/h ; `2` en fin |
| `0x1B7A` | `0xE8CB6` | `1 · 1000 · 820 · 220 · 512 · 1024 · 1024 · 9` | entrée de la **table des rampes** |
| `0x1B7C` | `0xE8CB8` | `1000 · 820 · 220 · 512 · 1024 · 1024 · 9 · 3840` | |
| `0x1B7E` | `0xE8CBC` | `220 · 512 · 1024 · 1024 · 9 · 3840 · 8 · 4480` | |
| `0x1B80` | `0xE8CC6` | `3840 · 8 · 4480 · 8 · 2560 · 8 · 0 · 8` | ★ paires `(3840, 8)` `(4480, 8)` `(2560, 8)` `(0, 8)` `(0, 8)` |
| `0x1B82` | `0xE8CCA` | `4480 · 8 · 2560 · 8 · 0 · 8 · 0 · 8` puis `500 · 500` | |
| `0x1B84` | `0xE8CCE` | `2560 · 8 · 0 · 8 · 0 · 8 · 500 · 500 · 500 · 600 · 600 · 1152` | |

Les couples `(3840, 8)`, `(4480, 8)`, `(2560, 8)`, `(0, 8)` et la suite `500/500/500/600/600/1152`
sont la **matière des rampes** : paliers de vitesse/vitesses cibles et durées. `3840 = 38,40 km/h`,
`4480 = 44,80`, `2560 = 25,60`, `500 = 5,00 km/h` — **ce sont des vitesses**, ce qui est cohérent avec
un régulateur qui **mémorise et rappelle des vitesses** (`+`/`−` par paliers de 1 km/h, rappel de la
vitesse mémorisée).

---

## 6. Lu / inféré

| affirmation | statut |
|---|---|
| segment 0 = 32 768 o de `0xC3` ; 108 490 o de `0xC3` au total ; 77 primitives effacées | **lu** |
| `unk_1D36` = (courbe, X) ; `unk_1D50` = (carte, tagY, tagX) ; `unk_20AC` = a·b/10000 | **lu** (sites) |
| `unk_1FE8` : 4 registres + 5 arguments de pile, entrée = `C562` au site régulateur | **lu** (l.187031) |
| `byte_C240` : un seul lecteur, indexe `word_1B22` (15 octets) | **lu** |
| le rapport **n'est pas calculé** dans le code visible | **inféré, solide** (0 division, 0 écrivain calculé) ; la bibliothèque reste un refuge |
| `0xE880A` = protection à 111-122 °C modulée par la vitesse | **lu** ; le rôle « refroidissement » est **inféré** |
| le bloc `0x1B70`…`0x1B84` = seuils et paliers de vitesse du régulateur | **lu** ; l'affectation `+`/`−` est **inférée** |

---

## 7. Suite

1. **`sub_B2A02`** : remonter à son appelant (`seg015:27E6`) pour nommer la grandeur corrigée.
2. **Le PI `unk_2020`** (l.196447) : relever gains et sortie → c'est le vrai régulateur continu, et
   il est **dans le code visible** (pas dans la bibliothèque).
3. **`word_C6D8` / `word_C6AA` / `byte_C244` (`0x80`/`0x81`)** : apparaissent juste après le rapport
   (`loc_AFCD4`) et comparent `word_C562` à `[word_1B26+6]` — **le seuil de vitesse lié au rapport**.
   C'est très probablement là que se décide « trop haut / trop bas » pour le régulateur.
4. **`byte_C32E` (`or #0A1h`) / `byte_C332`** : drapeaux de **coupure** posés dans ce même bloc —
   candidats pour la désactivation par frein/embrayage.
