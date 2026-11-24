# ÉTAPE 104 — La chaîne `word_D1B6 → word_C594 → word_D1C0` est **calculée, tracée… et jamais appliquée**

> Réponse aux deux questions posées : (1) la limitation par rapport est-elle active d'origine ?
> (2) soustraction directe ou `MIN` ? — Et une découverte de portée générale sur la zone `D1A4-D1D2`.

---

## 1. ★★★ Le résultat : toute la zone `D1B0`-`D1C4` est en **écriture seule**

Table des symboles `clean.asm`, l.52392-52402 — la colonne `DATA XREF` ne contient **que des `↓w`** :

| variable | xrefs | lecteurs |
|---|---|---|
| `word_D1B0` | `seg014:342C↓w` | **0** |
| `word_D1B2` | `3578↓w 359C↓w` | **0** |
| `word_D1B4` | `34B2↓w` | **0** |
| `word_D1B6` | `33B8↓w` | **0** |
| `word_D1B8` | `35B4↓w` | **0** |
| `word_D1BA` | `356C↓w 3594↓w` | **0** |
| `word_D1BC` | `loc_A3448↓w` | **0** |
| `word_D1BE` | `3562↓w 3590↓w` | **0** |
| `word_D1C0` | `loc_A3400↓w` | **0** |
| `word_D1C2` | `3306↓w` | **0** |

Contrôle croisé : **aucun immédiat** `0D1B0h` / `0D1B4h` / `0D1B8h` / `0D1BCh` / `0D1C0h` dans tout
le fichier (**0 occurrence**) ⇒ pas d'accès indirect par construction de pointeur.
La zone voisine `D1A4-D1AE`, `D1C4-D1D2` est dans le même cas.

### ⇒ Réponse à la question 1

**La limitation de couple par rapport est calculée à chaque cycle, écrite en RAM… et aucun code ne
la relit.** Ce n'est donc pas un limiteur : c'est un **bloc de valeurs de contrôle/trace**
(typiquement ce qu'on observe à la valise), alimenté par la tâche quantité.

⇒ **Elle est neutralisée d'origine sur ce firmware** — exactement l'hypothèse que tu proposais pour
les ML5T qui encaissent déjà les 314 Nm du DW12TED4. Le calcul est présent, l'action ne l'est pas.

⚠ Réserve honnête : on a 32 Ko **effacés** (`0x80000-0x87FFF`, voir Étape 101). Si un consommateur
vivait dans cette bibliothèque, il est invisible ici. C'est la seule hypothèse concurrente — mais
elle est peu probable, car un limiteur actif lirait ses entrées en direct, pas via des variables
"trace" distinctes.

---

## 2. ★★ La chaîne, pas à pas (tâche quantité, entrée sans label ≈ `seg014:32A4`)

### 2.1 L'index `word_D1B6` — un indice de charge, pas une vitesse

```asm
155173  mov  r4, word_1472        ; word_1472 -> 0xE226C, [0] = 0x6FFE = 28670
155174  mov  r12, [r4]
155176  mov  r14, #3E8h           ; 1000
155177  calls unk_20AC            ;   r4 = 28670 / 1000 = 28
155179  mov  r12, word_C586
155181  mov  r14, [r0+#8]         ;   = [word_18B2+0x10] + word_C596
155182  calls unk_20AC            ;   r4 = C586 x 28 / [r0+8]
155185  mov  r13, [r0+#20h]       ;   = word_D6D4 (filtre de word_C3E0)
155186  mov  r14, #64h            ; 100
155187  calls unk_20AC            ;   r9 = ... x [r0+20h] / 100
155189  mov  word_D1B6, r9        ; ★ D1B6 = (C586 x 28 / (18B2[+10]+C596)) x D6D4 / 100
```

`word_C596` vient de `word_1878 [+4]` = **`0xE4C0A = 120`** (l.154278-154280) : c'est le **plafond de
débit de référence** (120 mm³/coup), auquel tout le reste est comparé/soustrait.

L'indice `D1B6` est ensuite **lu sur l'échelle 500…11000**, c'est-à-dire la **même échelle que les
`Gangstufen`** (`N/V × 100`) : c'est un **indice de charge normalisé**, exprimé dans l'échelle du
rapport — d'où la parenté, dans le Datensatz, avec les escaliers de `0xE8108`-`0xE8158`.

### 2.2 Les **deux** courbes jumelles, même tag `0xD1B6`, même axe

| handle | EA | tag | axe | valeurs |
|---|---|---|---|---|
| `word_18A2` | `0xE4D14` | **`0xD1B6`** | 500 2000 3000 4000 6000 7000 9000 11000 | **117 266 367 447 542 585 643 655** |
| `word_18A4` | `0xE4D38` | **`0xD1B6`** | *identique* | **15 27 40 58 105 130 185 260** |

Deux courbes au **même tag et au même axe** = les **deux faces d'un même terme de correction**
(la petite et la grande), l'une servant de valeur, l'autre de référence de pente.

### 2.3 Le calcul, et la réponse à la question 2 : **soustraction pondérée, pas `MIN`**

```asm
155190  mov  r12, word_18A4 ; -> C594 = courbe 18A4(D1B6)      [15 .. 260]
155193  mov  word_C594, r4
155194  mov  r12, word_18A0 ; courbe 0xE4CF0, évaluée en word_C5BC
155198  mov  r12, word_C594
155200  mov  r14, #3E8h
155201  mov  [r0+#1Ch], r4  ; [1Ch] = C594 x 18A0(C5BC) / 1000
...
155214  mov  word_D1C0, r7  ; ★ D1C0 = C596 - [1Ch]
155219  mov  r12, word_18A2 ; [1Eh] = 18A2(D1B6) x 189E(C5BC) / 1000
155226  mov  [r0+#1Eh], r4
155228  mov  r8, word_C596
155229  sub  r8, r4
155240  mov  word_D1BC, r8  ; ★ D1BC = C596 - [1Eh]
155241  mov  r4, [r0+#1Eh]
155242  mov  r5, [r0+#1Ch]
155243  sub  r4, r5         ; écart [1Eh] - [1Ch]
155258  mov  r12, [r4+#2]   ; coefficient de word_189C
155260  mov  r14, #2710h    ; 10000
155261  calls unk_20AC      ; = coeff x écart / 10000
155263  mov  r5, r7         ; = D1C0
155264  sub  r5, r4
155279  mov  word_D1B4, r4  ; ★★★ D1B4 = D1C0 - coeff x ([1Eh]-[1Ch]) / 10000
```

Formules finales :

```
D1B6 = (C586 x 28 / ([word_18B2+10h] + C596)) x word_D6D4 / 100
C594 = courbe_18A4(D1B6)                        ; 15..260
D1C0 = C596 - C594 x courbe_18A0(C5BC) / 1000   ; ← limitation "basse"
D1BC = C596 - courbe_18A2(D1B6) x courbe_189E(C5BC) / 1000
D1B4 = D1C0 - coeff_189C x (D1BC' - D1C0') / 10000
```

⇒ **C'est une double soustraction pondérée, pas une sélection de minimum.** L'arbitrage par `MIN`
existe ailleurs dans la même tâche (chaîne de `cmp`/`jmpr cc_SLT/SGT` à partir de l.155378 sur
`word_18A8`, `word_18AC`, `word_18AA` et la structure `word_18B2`) — mais il porte sur les
**candidats de débit classiques**, pas sur la chaîne par rapport.

### 2.4 Le struct de limites `word_18B2 → 0xE4E2C`

`2000 · 1500 · −2000 · −2500 · 5000 · 4500 · 13000 · 1100` — lu par offsets `+0Ch … +1Ah` comme
bornes min/max des candidats, avec `byte_C308` comme drapeau de sélection (`loc_A3558` / `loc_A358C`).
C'est **ce** bloc qui alimente la limitation réellement appliquée au débit injecté.

---

## 3. Un mot sur ton avertissement VAN/BSI — et un second bloc de codage

Tu as raison de séparer les deux cas. Dans **ce** fichier :

| bloc | EA | taille | octets utiles |
|---|---|---|---|
| `word_141C` | `0xE111E` | 42 o | `+2 = 01` → `C2C0 = 1` (BVM) · **`+3 = 00` → `C2BD = 0` (FGR off)** · `+0Eh = 08` → `C2B7` |
| `word_141E` | `0xE1148` | 52 o | `+3 = 08` → `C2BD` (voie directe) · **`+5 = 01` → `byte_C2BC = 1`** (l.200025-200027) |

Le flag FGR est donc **`0x00`** sur ce dump — cohérent avec l'absence de régulateur. Si le véhicule
a un régulateur actif via le BSI, c'est **ce même octet** qui doit être non nul **côté ECU**, sinon
la tâche `0x340` sort en `0x8E` quoi que fasse le BSI. À vérifier en premier sur la voiture.

---

## 4. Bilan de la cartographie « rapport de boîte »

| étage | entrée | sortie | état |
|---|---|---|---|
| calcul du ratio | `C578` (V×256), `C42E` (N) | `C576` / `C93E` (filtré) | **actif** |
| reconnaissance de rapport | `C93E` vs `0xE81A4` | `byte_C330` (0-6, bit `0x40`) | **actif** |
| autorisation FGR | `C93E` vs `0xE2792` (768 = 3) | refus `0x89` | **actif** |
| **limitation de couple par rapport** | `D1B6` → 2 courbes | `D1B0`…`D1C4` | **calculée, jamais relue ⇒ NEUTRALISÉE** |

⇒ Sur ce firmware, le rapport sert bien à (a) l'agrément, (b) l'autorisation du régulateur,
**mais pas** (c) la limitation de couple en 1re/2de : ce dernier étage est présent, documenté, et
volontairement inerte. Exactement ce que tu attendais d'une ML5T derrière un DW12TED4 de 314 Nm.

## 5. Errata
- **E15** : `word_D1C0` n'est **pas** « la limitation appliquée » (Étape 102, formulation prudente mais
  ambiguë) : c'est une **trace**. Le débit réellement limité passe par `word_18B2` / `byte_C308`.
