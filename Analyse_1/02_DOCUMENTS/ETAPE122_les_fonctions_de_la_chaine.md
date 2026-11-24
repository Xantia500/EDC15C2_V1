# ÉTAPE 122 — LES FONCTIONS DE LA CHAÎNE : entrées, sorties, ce qu'elles font

Complément de l'Étape 121. Deux catégories, séparées nettement :

- **A. Routines de la bibliothèque** : présentes dans le dump comme **`ds` (vides)** ⇒ convention
  d'appel déduite du code, comportement déduit de l'usage. **Aucune invention.**
- **B. Fonctions réellement désassemblées** : corps cité, entrées/sorties réelles.

---

## A. Les routines de la bibliothèque (absentes du dump)

Toutes sont déclarées `ds 1` ou `ds 2` dans `clean.asm` — la bibliothèque n'a pas été désassemblée.
Ce qu'on sait vient **des sites d'appel**, sur 385 appels inventoriés (`registre_appels_interpolation.csv`).

| routine | entrées | sortie | comportement déduit | appels |
|---|---|---|---|---|
| **`unk_1D50`** | `r12` = pointeur de carte, `r13` = **X (valeur)**, `r14` = **Y (valeur)** | `r4` | **interpolation 2-D**, axes fournis **par valeur** | 72 |
| **`word_1D94`** | `r12` = **pointeur X**, `r13` = **pointeur Y**, `r14` = pointeur de carte | `r4` | **interpolation 2-D**, axes fournis **par pointeur** (variables RAM) | 64 |
| **`unk_1D6C`** | `r12` = pointeur de destination, `r13` = X (valeur), `r14` = pointeur de courbe | `r4` **et** `[r12]` | **courbe 1-D** ; le résultat est écrit **dans le buffer** pointé par `r12` | 44 |
| **`unk_1D36`** | `r12` = pointeur de courbe, `r13` = X (valeur) | `r4` | **courbe 1-D** simple | 168 |
| **`unk_20AC`** | `r12` = valeur, `r13` = référence/offset, `r14` = **échelle** | `r4` | **conversion échelonnée**. Preuve de l'échelle : `unk_20AC(résultat, [r0], #2710h)` (l.131283) et `unk_20AC(r9, r8, #2710h)` (l.182266) ⇒ **`0x2710` = 10000 = pleine échelle** | 251 |
| **`word_1DDA`** | `r12` = valeur courante, `r13` = candidat, `r14` = **étiquette de source** | `r4` + drapeau `USR0` | **sélection de minimum avec étiquette de source**. Preuve l.180159-163 : `word_1DDA(0x7FFF, D904, D906)` → `mov word_D904, r4` puis `bmovn word_FD16.14, USR0` ⇒ **`D906` mémorise quel limiteur a gagné** | 35 |
| **`unk_1E50`** | `r12` = pointeur de paramètre, `r13` = entrée, `r14` = pointeur d'état | `r4` | **pas de filtre du 1er ordre** (état dans `D8C0`/`D8C2`) | 1 |
| **`unk_1E34`** | `r12/r13/r14/r15` = pointeurs de travail | `r4` | routine de gestion de vecteur (l.188585) | 2 |
| **`word_1E08`** | `r12` = pointeur, `r13` = valeur | `r4` | conversion simple | 2 |
| **`word_1DA8`** | `r12` = pointeur de variable | `r4` | lecture/validation d'un compteur (`#0D9E0h`, l.185126) | — |

★ **Le mécanisme `word_1DDA` est une découverte importante** : `D904` = le minimum courant,
**`D906` = l'étiquette du limiteur gagnant**. C'est la variable qui dit « **c'est la fumée / la
température / le rapport qui limite en ce moment** ».

---

## B. Les fonctions désassemblées

### B.1 `sub_B56F8` — sélecteur du souhait (l.186821-186849)

```asm
sub_B56F8:
    mov  [-r0], r9
    mov  [-r0], r8
    mov  r8, r13          ; Y = pédale
    mov  r9, r12          ; X = régime
    mov  r4, word_C576
    mov  word_C93E, r4    ; C93E := code de rapport
    mov  r5, word_1B6A    ; → EA 0xE8C58
    mov  r2, [r5]         ; seuil = 539
    cmp  r2, word_C93E
    jmpr cc_SLE, loc_B5722
    mov  r12, word_1B68   ; → 0xE8BD4
    mov  r13, r9
    mov  r14, r8
    calls 0, unk_1D50
    jmpr cc_UC, loc_B572E
loc_B5722:
    mov  r12, word_1B66   ; → 0xE8B50
    mov  r13, r9
    mov  r14, r8
    calls 0, unk_1D50
loc_B572E:
    mov  r8, [r0+]
    mov  r9, [r0+]
    rets
```

| | |
|---|---|
| **entrées** | `r12` = régime (`C91C`), `r13` = pédale (`C952`) |
| **sortie** | `r4` = souhait en mm³ (0,01 mm³) → stocké dans **`C6A6`** par l'appelant (l.195506) |
| **effet de bord** | `C93E := C576` (trace du rapport utilisé) |
| **ce qu'elle fait** | choisit **une** des deux cartes de souhait selon `C576` vs le seuil **539** lu dans `0xE8C58`, puis interpole |

### B.2 `sub_AF75A` — filtre conditionnel du 1er ordre (l.177009-177040)

```asm
sub_AF75A:
    mov  r9, r12                    ; mémorise l'entrée
    movb rl4, byte_C2C0
    cmpb rl4, #4                    ; variante 4 ?
    jmpr cc_NZ, loc_AF790           ; non -> pas de filtre
    movb rl5, byte_C227
    andb rl5, #2                    ; bit de filtrage ?
    jmpr cc_Z, loc_AF790            ; non -> pas de filtre
    jnb  word_FD16.13, loc_AF77C    ; premier passage ?
    mov  word_D8C2, r9              ;   -> réinitialise l'état
    mov  word_D8C0, ZEROS
    bclr word_FD16.13
loc_AF77C:
    mov  r12, word_1A96             ; → EA 0xE7FF2
    mov  r13, r9
    mov  r14, #0D8C0h               ; état
    calls 0, unk_1E50
    mov  r4, word_D8C2
    jmpr cc_UC, loc_AF794
loc_AF790:
    bset word_FD16.13               ; marque « non filtré »
    mov  r4, r9                     ; sortie = entrée brute
```

| | |
|---|---|
| **entrée** | `r12` = IQ |
| **sortie** | `r4` = IQ filtré (ou brut) |
| **ce qu'elle fait** | filtre du 1er ordre **uniquement si `byte_C2C0 == 4` ET `byte_C227 & 2`** ; sinon transparence. `word_FD16.13` sert de drapeau « filtre amorcé » |

### B.3 `sub_B33DC` — limiteur d'IQ par `C692` (l.183315-183356)

```asm
sub_B33DC:
    movb rl4, byte_C33B
    movb byte_C8F9, rl4
    movb rl5, byte_C2BA
    jmpr cc_Z, loc_B3400
    cmpb rl4, #0
    jmpr cc_NZ, loc_B3400
    mov  r4, word_C562
    jmpr cc_NZ, loc_B3400           ; véhicule roule -> cas général
    mov  r5, word_C5AC
    cmp  r5, #0
    jmpr cc_SLE, loc_B3400
    mov  r4, r5
    rets                            ; ★ à l'ARRÊT : renvoie C5AC
loc_B3400:
    movb rl4, byte_C2C0
    cmpb rl4, #1
    jmpr cc_Z, loc_B3422            ; variante 1 -> pas de limite
    mov  r4, word_C692
    cmp  r4, #7FFFh
    jmpr cc_SGE, loc_B3422          ; sentinelle -> pas de limite
    cmp  r12, word_C692
    jmpr cc_SGE, loc_B341C
    mov  r4, r12                    ; min(r12, C692)
    ...
```

| | |
|---|---|
| **entrée** | `r12` = IQ à limiter |
| **sortie** | `r4` = IQ limité |
| **ce qu'elle fait** | ① si véhicule **à l'arrêt** (`C562 == 0`) et condition de codage ⇒ renvoie **`C5AC`** ; ② sinon renvoie **`min(r12, C692)`**, avec `0x7FFF` = « aucune limitation » |

### B.4 `sub_AFA42` — instantané + carte T° LDR démarrage (l.177370-177380)

```asm
sub_AFA42:
    mov  r4, word_C42E
    mov  word_C91C, r4        ; C91C := régime
    mov  r5, word_C3D2
    mov  word_C908, r5        ; C908 := T° LDR
    mov  r12, word_1A8C       ; → EA 0xE80A0
    mov  r13, r4
    mov  r14, r5
    calls 0, unk_1D50
    rets
```

| | |
|---|---|
| **entrées** | aucune (lit `C42E`, `C3D2`) |
| **sorties** | `r4` = valeur de la carte `0xE80A0` ; effet de bord `C91C`, `C908` |
| **ce qu'elle fait** | effectue l'instantané régime/T° puis interpole la carte **T° LDR × régime** de démarrage |

### B.5 `sub_972FA` — carte `0xE3908` (l.131297-131309)

```asm
sub_972FA:
    mov  r4, word_C42E
    mov  word_C91C, r4        ; C91C := régime
    mov  r5, word_C3D2
    mov  word_C908, r5        ; C908 := T° LDR
    mov  r12, word_15E4       ; → EA 0xE3908
    mov  r13, r4
    mov  r14, r5
    calls 0, unk_1D50
    rets
```

Identique à B.4 mais avec **`0xE3908`** (T° LDR froid, 2531-3131 = −20…+40 °C). Sortie `r4`.

### B.6 `sub_972CA` — carte `0xE38D8` + conversion (l.131274-131291)

```asm
sub_972CA:
    mov  r4, word_C42E
    mov  word_C91C, r4
    mov  r5, word_C3BA
    mov  word_C904, r5        ; C904 := T° (axe C3BA)
    mov  r12, word_15E2       ; → EA 0xE38D8
    mov  r13, r4
    mov  r14, r5
    calls 0, unk_1D50
    mov  r12, r4
    mov  r13, [r0]
    mov  r14, #2710h          ; échelle 10000
    calls 0, unk_20AC
```

| | |
|---|---|
| **entrées** | paramètre sur pile `[r0]` |
| **sorties** | `r4` = résultat converti ; `C904` = T° `C3BA` |
| **ce qu'elle fait** | interpole `0xE38D8` (régime × `C3BA`), puis **remet à l'échelle sur 10000** via `unk_20AC` |

### B.7 `sub_BAC40` — anti-rebond / maintien de condition (l.195544-195590)

```asm
sub_BAC40:
    mov  r4, [r13]              ; compteur pointé par r13
    cmp  r4, #0FFh
    jmpr cc_NZ, loc_BAC4E
    mov  r4, [r13]
    add  r4, #1
    mov  [r13], r4              ; incrémente, plafonné à 0xFF
loc_BAC4E:
    mov  r4, [r13]
    cmp  r4, #0FFh
    jmpr cc_ULE, loc_BAC6C
    movb rl4, #1
    movb byte_DB84, rl4         ; ★ débordement -> condition validée
    mov  r4, [r13]
    and  r4, #0FFh
    mov  [r13], r4
    mov  word_DB86, r12
    mov  r4, #1
    rets
...
loc_BAC82:
    movb byte_DB84, ZEROS
    mov  r4, [r13]
    cmp  r12, r4
    jmpr cc_ULE, loc_BAC90
    mov  r4, #0
    rets
loc_BAC90:
    mov  r4, #1
    rets
```

| | |
|---|---|
| **entrées** | `r12` = valeur à comparer, `r13` = **pointeur** vers un compteur octet |
| **sortie** | `r4` = **1 ou 0** (booléen) |
| **ce qu'elle fait** | incrémente un compteur à chaque appel ; quand il dépasse `0xFF`, la condition est **validée** et `DB86` mémorise la valeur ; ensuite renvoie `1` tant que `r12 ≤ compteur`. C'est un **temporisateur de maintien** (« condition vraie pendant N cycles ») |

### B.8 `sub_A7D96` — décodage d'état (l.163166-163189)

```asm
sub_A7D96:
    movb rl4, byte_C307
    cmpb rl4, #6
    jmpr cc_Z, loc_A7DA2
    cmpb rl4, #2
    jmpr cc_NZ, loc_A7DA6
loc_A7DA2:
    movb byte_C31A, ZEROS       ; si état 6 ou 2 -> remet C31A à 0
loc_A7DA6:
    movb rl4, byte_C31A
    jmpr cc_Z, loc_A7DB6
    movb rl5, byte_C307
    jmpr cc_NZ, loc_A7DB6
    movb rl4, #1
    rets
loc_A7DB6:
    movb rl4, byte_C307
    rets
```

| | |
|---|---|
| **entrées** | aucune (lit `byte_C307`, `byte_C31A`) |
| **sortie** | `r4` (octet) |
| **ce qu'elle fait** | **décodeur d'état** : renvoie `C307`, ou `1` si `C31A ≠ 0` **et** `C307 == 0` ; remet `C31A` à zéro quand l'état vaut 6 ou 2 |

### B.9 `sub_BF750` — test de drapeaux (l.203990-204006)

```asm
sub_BF750:
    movb rl4, word_FD26+1
    jmpr cc_NZ, loc_BF75C
    movb rl4, word_FD28
    jmpr cc_Z, loc_BF760
loc_BF75C:
    mov  r4, #1
    jmpr cc_UC, locret_BF762
loc_BF760:
    mov  r4, #0
locret_BF762:
    rets
```

| | |
|---|---|
| **entrées** | aucune (lit deux octets d'état `FD26+1`, `FD28`) |
| **sortie** | `r4` = **1 ou 0** |
| **ce qu'elle fait** | **test booléen** de deux drapeaux système |

### B.10 `sub_AFAA0` — réinitialisation (l.177430-177439)

```asm
sub_AFAA0:
    mov  r4, word_1AA8
    mov  word_D8F2, r4        ; D8F2 := [0x1AA8]
    mov  r5, word_1AFE
    mov  word_D8F4, r5        ; D8F4 := [0x1AFE]
    movb rl4, #0FFh
    orb  byte_D8F6, rl4       ; invalide D8F6
    orb  byte_D8F7, rl4       ; invalide D8F7
    rets
```

| | |
|---|---|
| **entrées** | aucune |
| **sorties** | `D8F2`, `D8F4` (valeurs de calibration), `D8F6`/`D8F7` = `0xFF` |
| **ce qu'elle fait** | **réinitialise** deux valeurs et **invalide** deux compteurs/drapeaux (`0xFF` = invalide) |

### B.11 `sub_B64A8` — bloc de calcul des limites (l.188256-188684, 428 lignes)

**Entrées** : `r12`, `r13` (sauvegardés puis utilisés), lecture de `byte_DA4C`, `word_DA32`,
`word_DA38`, `word_DA40`, `byte_C2E7`, `word_C6A2`, `word_C6B8`.

**Sorties écrites** : `D412`, `C914`, `C94C`, `DA4E`, **`C664`**.

**Ce qu'elle fait** — trois blocs successifs :

| bloc | code | effet |
|---|---|---|
| 1 | `mov r4, word_1BE8 / [r4] / [r4+1]` … `divu word_DA42` | **calcul d'un index de rampe** à partir de paramètres pointés, puis division |
| 2 | `word_1E08(r12=0x1BD8, r13)` · `C914 := C41A` | conversion + recopie d'une valeur |
| 3 | `C94C := C6A2` (charge) → `unk_1D36(word_1BEC, charge)` → `DA4E` → `+ C662` → **`C664`** | **limiteur de charge** (smoke partiel) |
| — | `word_1BE0 … 0x1BEC`, `word_1BD8/1BDA`, `word_1E08`, `unk_1E34`, `0DAE0h`, `0DA5Ch` | tableaux de travail indexés par `word_DA38` |

### B.12 `sub_97FF8` — coquille (l.132954-132958)

```asm
sub_97FF8:
    movb [r12], [r12]
    movb [r13], [r13]
    rets
```

**Aucun effet** (auto-affectations). C'est un **artefact de désassemblage** d'un appel vers une zone
non couverte. Corollaire : les cartes attribuées à cette « fonction » dans l'Étape 119 le sont par
proximité de label, **pas** par appartenance réelle.

---

## C. Table des pointeurs utilisés dans la chaîne

| pointeur | EA | carte |
|---|---|---|
| `0x1B66` | `0xE8B50` | souhait A (rapport ≥ 539) |
| `0x1B68` | `0xE8BD4` | souhait B (rapport < 539) |
| `0x1B6A` | `0xE8C58` | seuil **539** |
| `0x1B40` | `0xE8444` | **smoke map** (régime × air) |
| `0x1B46` | `0xE87D6` | variante démarrage à froid |
| `0x1A84` | `0xE8000` | T° carburant |
| `0x1A82` | `0xE7F7E` | T° carburant chaude |
| `0x1A8C` | `0xE80A0` | T° LDR démarrage |
| `0x1B44` | `0xE86F4` | T° LDR ralenti |
| `0x1B42` | `0xE868C` | T° LDR × vitesse |
| `0x1B4A` | `0xE880A` | T° LDR surchauffe |
| `0x1B48` | `0xE87EE` | correcteur lié à `C562` |
| `0x15E2` | `0xE38D8` | T° (`C3BA`) × régime |
| `0x15E4` | `0xE3908` | T° LDR froid × régime |
| `0x1B5E` | `0xE8A06` | **commande de pompe HP** |
| `0x144A` | `0xE13B0` | régime × charge |
| `0x144C` | `0xE13C6` | charge × `C63C` |
| `0x1444` | `0xE130E` | `C3EE` × `C3EE` |
| `0x1446` | `0xE2078` | limiteur mode 0 → `C682` |
| `0x1448` | `0xE211A` | limiteur mode 1 → `C688` |
| `0x144E` | `0xE13DC` | courbe 9 pts du limiteur |
| `0x1BEE` | `0xE8E26` | bloc utilisé avec `+C67A` |
| `0x1BEC` | `0xE8E12` | paramètre du limiteur de charge |
| `0x1BD8` / `0x1BDA` | `0xE8DEE` / `0xE8DF8` | paramètres de conversion |
| `0x1A96` | `0xE7FF2` | paramètre du filtre `sub_AF75A` |

---

## D. Ce que ça ajoute à la compréhension

1. **`D906` = l'étiquette du limiteur gagnant** (`word_1DDA`) : c'est la variable à observer pour
   savoir *qui* bride à un instant donné. Nouveauté par rapport à l'Étape 121.
2. **`unk_20AC` a trois arguments** (`valeur`, `référence`, `échelle`) et l'échelle `0x2710` = 10000
   apparaît explicitement ⇒ les conversions finales sont des **mises à l'échelle**, pas des courbes.
3. **`sub_B33DC`** traite un cas **véhicule à l'arrêt** (`C562 == 0` → `C5AC`) : c'est probablement
   le régime de **post-démarrage / ralenti accéléré**.
4. Les cartes « T° » passent par des **fonctions dédiées** (`sub_AFA42`, `sub_972FA`, `sub_972CA`) qui
   prennent un **instantané** `C91C`/`C904`/`C908` avant d'interpoler — d'où la cohérence des axes.
