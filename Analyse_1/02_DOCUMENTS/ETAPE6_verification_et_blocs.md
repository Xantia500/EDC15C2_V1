# Étape 6 — Vérification de la quantité d'injection, bloc diagnostic, et régulateur de ralenti

*ECU 0 281 010 877 — EDC15C2 / C167CR-4RM — image `edc.bin`*
*EA = adresse du listing IDA (offset `.bin` = EA − 0x80000). **[constat]** = visible dans le binaire ; **[hypothèse]** = interprétation.*

---

## 0. « Comment as-tu trouvé la quantité d'injection ? En es-tu sûr ? »

Bonne question, et la réponse honnête est : **la conclusion tient, mais une des preuves que j'avais avancée était fausse.** Je détaille.

### 0.1 La chaîne telle que je l'avais établie (étape 5)

```
word_C6BA  +  word_C69E  →  word_D844 / word_D304
     ↑            ↑
 quantité      correction du régulateur
 de base
```

### 0.2 Ce que j'ai vérifié après ta question

**a) D'où vient réellement `word_C6BA` ?**  **[constat]**

```
loc_BABD8 (EA 0xBABD8) :
        mov  r12, word_C91C          ; <-- RÉGIME MESURÉ
        mov  r13, word_C952          ; <-- seconde grandeur (charge)
        calls 0Bh, sub_B56F8         ; <-- LECTURE DE CARTOGRAPHIE
        mov  word_C6A6, r4
```

et `sub_B56F8` ne fait rien d'autre qu'aiguiller entre **deux cartographies** puis appeler le service d'interpolation :

```
sub_B56F8:
        mov  r4, word_C576
        mov  word_C93E, r4
        mov  r5, word_1B6A
        mov  r2, [r5]
        cmp  r2, word_C93E
        jmpr cc_SLE, loc_B5722
        mov  r12, word_1B68          ; variante A
        mov  r13, r9   (régime)
        mov  r14, r8   (charge)
        calls 0, unk_1D50            ; interpolation
        ...
loc_B5722:
        mov  r12, word_1B66          ; variante B
        mov  r13, r9
        mov  r14, r8
        calls 0, unk_1D50
```

**→ `word_C6A6` = sortie d'une cartographie 2D (régime × charge).** Ça, c'est solide : c'est la signature d'une **cartographie d'injection**.

**b) Ce que devient cette valeur.**  **[constat]** une cascade de limitations, toutes sur la même variable `word_D9A6` :

```
loc_B2E3C (EA 0xB2E3C) :
        word_D9A6 = word_C6A6 + word_C69E      ; base + correction régulateur, sat. 7FFF/8000
        word_C6B8 = word_D9A6
        max(word_D9A6, word_C680) -> word_D3E2
        min(word_D9A6, word_C67E) -> word_C6A4
        min(word_D9A6, word_C696)
        ...
        min(word_D9A6, word_C688) -> word_D3E8, word_C6AE
        min(word_D9A6, word_C682) -> word_C6AA
        min(word_D9A6, word_C6C0)
```

Sept limitations successives, chacune avec sa variable de publication. **C'est exactement la structure d'une grandeur de consigne fortement bornée** (limite de fumée, limite de couple, limite de surrégime, correction d'altitude…). **[hypothèse forte]**

**c) Mon erreur.** À l'étape 5 j'avais écrit :

> ~~« `sub_B33DC` : quantité → DURÉE → `word_C6B0` »~~

**C'est faux.** J'ai relu `sub_B33DC` : c'est un **limiteur**, pas un convertisseur.

```
sub_B33DC(r12):
        si byte_C2BA!=0 et byte_C33B==0 et word_C562==0 et word_C5AC>0 :
                retour = word_C5AC              ; valeur de substitution (moteur arrêté)
        si byte_C2C0 != 1 et word_C692 < 7FFF :
                retour = min(r12, word_C692)    ; LIMITE par word_C692
        retour = r12
```

Donc `word_C6B0` n'est **pas une durée** : c'est **la même quantité, écrêtée par `word_C692`** (quantité maximale), avec une valeur de remplacement quand le moteur ne tourne pas. Toute la phrase de l'étape 5 qui en découlait est à corriger.

**d) Et la conversion quantité → durée ?** **[constat négatif]** Je ne l'ai pas trouvée dans cette moitié de flash. Mon autre piste (`unk_1D50(word_1B5E, word_C91C, word_D9AA) → byte_C8F8`) ne tient pas non plus : `byte_C8F8` n'est qu'une **copie de `byte_C337`** (une recopie d'un octet d'état), pas une durée — il est ensuite multiplié par `0x28` dans `sub_9AE42`, ce qui ne correspond pas à une durée d'injection.

### 0.3 Verdict, avec le degré de confiance

| Affirmation | Preuve | Confiance |
|---|---|---|
| `word_C6A6` = sortie d'une cartographie 2D (régime, charge) | appel `unk_1D50(word_1B66/1B68, word_C91C, word_C952)` en `0xBABD8` | **très haute** |
| `word_D9A6 = word_C6A6 + word_C69E` = grandeur régulée | `loc_B2E3C` | **très haute** |
| `word_D9A6` subit 6-7 limitations en cascade | `loc_B2E6E` → `loc_B2F50` | **très haute** |
| `word_C6BA` = cette grandeur après limitations | `loc_B33C2` + `word_147E[0]/[2]` | **haute** |
| C'est la **quantité d'injection** | convergence des trois indices ci-dessus + le fait que `word_C69E` (sortie d'un régulateur de régime) y soit ajouté | **haute, mais par inférence** |
| `word_C6B0` = **durée** | — | **FAUX** (corrigé au §1.c) |
| La conversion quantité → durée est dans l'image | — | **non trouvée** |
| Les unités (mg/Hub, mm³/Hub) | — | **inconnues** |

> **En une phrase :** je peux affirmer que `word_C6BA` est **la grandeur de consigne issue de la cartographie principale, corrigée par le régulateur de régime et fortement limitée** — c'est très probablement la quantité d'injection, mais **je ne peux pas le prouver par les unités**, et la conversion vers une durée n'est **pas** dans cette moitié de flash.

---

## 1. Piste 1 — le bloc de mesure du diagnostic (`0xBD00` → `0xDF00`)

### 1.1 Le descripteur et le matérialisateur  **[constat]**

```
sub_BDB22 (EA 0xBDB22) :
        mov  r12, #0BD00h
        mov  r9,  #0DF00h
        mov  r13, [r12]              ; mot de contrôle
        mov  r4, #100h
        and  r4, r13                 ; bit 0100h = autorisation
        jmpr cc_Z, loc_BDB66         ; sinon : rien
        mov  r14, #0FFh
        and  r14, r13                ; octet bas = NOMBRE d'entrées
        mov  r15, #0
loc_BDB40:
        add  r12, #2
        mov  r4, [r12]               ; pointeur d'entrée
        movb [r9], [r4]              ; byte[0xDF00+k] = byte[*ptr]
        add  r9, #1
        add  r15, #1
loc_BDB4A:
        r4 = min(r14, 1Ch)           ; <-- PLAFOND À 28 ENTRÉES
        if r15 < r4 -> loc_BDB40
        mov  word_DFB6, #7
        mov  word_DFFC, #0
```

> **`word_BD00` = descripteur d'un bloc de mesure** : `[0100h]` = autorisation, octet bas = nombre d'entrées (plafonné à **28**), puis une **liste de pointeurs** à `0xBD02, 0xBD04, …`. Chaque pointeur désigne **un octet** qui est recopié dans **`0xDF00 + k`**.

### 1.2 Le lecteur, côté testeur  **[constat]**

```
loc_A2134 (EA 0xA2134) :
        calls 0Ah, sub_A1E9E          ; r12 = 80h : sélection du bloc
        calls 0Ah, sub_A1E9E          ; r12 = FFh : sélection du bloc
        mov  r4, word_CFD6
        jmpr cc_Z, loc_A2164
        movbz r12, byte_CFBE
        add  r12, #0EF00h             ; <-- BLOC 1 = 0xEF00 + index
        calls 9, sub_942DE
        mov  word_CFB8, r4
        jmpr cc_UC, loc_A2188
loc_A2164:
        mov  r4, word_CFD8
        jmpr cc_Z, loc_A217E
        movbz r12, byte_CFBE
        add  r12, #0DF00h             ; <-- BLOC 2 = 0xDF00 + index
        mov  r13, #0CFBCh
        calls 9, sub_942CA
        mov  word_CFB8, r4
```

avec, en aval, le transport :
```
sub_942CA  ->  sub_CE256
sub_942DE  ->  sub_CE43C
```

### 1.3 Réponse

> Le calculateur expose **deux blocs de mesure** au testeur, adressés par un index `byte_CFBE` :
>
> | Bloc | Adresse de base | Construit par | Taille |
> |---|---|---|---|
> | 1 | **`0xEF00`** | non identifié dans l'image (écrivains indirects) | — |
> | 2 | **`0xDF00`** | `sub_BDB22`, via le descripteur `word_BD00` | ≤ **28 octets** |
>
> La sélection se fait par les octets de service `80h` / `FFh` passés à `sub_A1E9E`. C'est le mécanisme « **lire un bloc de valeurs mesurées** » d'un dialogue diagnostic de type KWP.
>
> **[constat négatif]** la **liste de pointeurs** (`0xBD02…`) n'est écrite **nulle part** dans l'image : `0xBD00` n'apparaît qu'une seule fois, en `0xBDB22`, comme constante immédiate. Les pointeurs sont donc posés par des écritures indirectes (`mov [r4], rX` avec `r4` calculé), ou par la moitié basse. **C'est le seul verrou restant sur cette piste** — mais il est franchissable : il suffit de poser un point d'arrêt sur `0xBDB40` sous IDA et de lire la liste en mémoire.

---

## 2. Piste 2 — `word_147E`, `word_1438`, `word_1434` : bornes et bits d'autorisation

### 2.1 `word_147E` — bornes d'une grandeur  **[constat]**

| Offset | Usage |
|---|---|
| `+0`, `+2` | bornes **basse / haute** de `word_C6BA` (`0xB3388` : `cmp r9,[r2]` puis `cmp r9,[r4+#2]`) |
| `+8`, `+0Ah` | bornes **basse / haute** d'une seconde grandeur (`word_D400/D402`, `0xB5D96`) |

Lu 9 fois, jamais écrit → pointeur de la mémoire basse. **Deux grandeurs bornées, deux paires de limites** : très probablement la **quantité** et son **correspondant en durée/angle**.

### 2.2 `word_1438` — bornes de débit  **[constat]**

| Offset | Usage |
|---|---|
| `+0Ah` | seuil bas : si `word_C6BA + word_C69E < [0Ah]` → **bit 2 de `byte_C190`** (`loc_975D0`) |
| `+10h` | borne suivante (`loc_975EA`) |
| `+12h` | seuil de **temps** : `word_C07E − word_F91C` comparé à `[12h]` (`loc_975B6`) |

### 2.3 `word_1434` — **bits d'autorisation**  **[constat]**

Motif systématique :
```
mov r4, word_1434
mov r5, [r4+#4]
and r5, #1        ; puis #2, #4, #8 ...
jmpr cc_NZ, ...
mov word_C924, ZEROS   ; <- si le bit est absent, la valeur est FORCÉE À ZÉRO
```

Utilisé aussi avec `[+0] & 80h`, `[+2] & 2`, `[+8] & 80h`. C'est une **table de masques de validation** : chaque bit autorise (ou inhibe) une grandeur. **Deux octets de masques (`+0`, `+2`), un octet à `+4`, un à `+8`.**

### Réponse

> Ces trois structures (`0x147E`, `0x1434`, `0x1438`) forment, avec `word_1432` (étape 4), un **jeu cohérent de tables de calibration rangées dans la mémoire basse** :
> * `word_1432` = seuils de **régime** et de **temps** ;
> * `word_147E` = bornes de **grandeurs** (quantité, et une seconde) ;
> * `word_1438` = bornes de **débit** et **seuil de temps** ;
> * `word_1434` = **masques binaires d'autorisation**.
>
> Les adresses sont contiguës (`0x1432`, `0x1434`, `0x1438`, …) : ce sont des **pointeurs consécutifs dans une table de structures de la mémoire basse**, très probablement construite par le code d'initialisation absent.

---

## 3. Piste 3 — qui écrit `word_C6C8` : le régulateur de ralenti complet

**[constat]** trois écritures seulement, toutes dans la même routine (`loc_B7726`, EA `0xB7726`) :

```
loc_B7706:
        mov  r12, word_C6CE
        calls 0Ah, sub_AF6E8             ; correction / limite
        mov  word_C646, r4
        mov  r5, word_C6CE
        cmp  r5, word_C646
        jmpr cc_SLE, loc_B7722
        mov  r4, word_C6CE
        jmpr cc_UC, loc_B7726
loc_B7722:
        mov  r4, word_C646
loc_B7726:
        mov  word_C6C8, r4               ; <-- CONSIGNE = min(C6CE, C646)
        cmp  r4, word_C6C2
        jmpr cc_SGT, loc_B7738
        mov  r5, word_C6C2
        mov  word_C6C8, r5               ; <-- plancher C6C2
loc_B7738:
        mov  r4, word_C6C8
        mov  word_C6D2, r4               ; publication
        ...
loc_B7744:
        mov  r5, word_1432
        mov  r2, [r5+#2]
        mov  word_C6C8, r2               ; <-- REPLI = word_1432[2]
```

et en amont, l'origine de `word_C6CE` :

```
loc_B76FE:
        mov  r4, word_DB2A
        mov  word_C6CE, r4               ; si pas de courbe
        ...
        calls 0, word_1DDA               ; sinon : interpolation (r12 = index<<3, r14 = word_DB2C)
        mov  word_DB32, r4
        ashr r4, #3
        mov  word_C6CE, r4
```

et l'origine de `word_DB2A` (`loc_B7496`) :
```
loc_B7496:
        mov  r4, word_1432
        mov  word_DB2A, [r4]             ; <-- word_1432[0] = consigne de référence
```

### Réponse

> **`word_C6C8` est la consigne de régime**, construite ainsi :
>
> ```
> word_1432[0]  ──────────────► word_DB2A
>                                     │
>                     courbe (word_1DDA, index word_DB2C)
>                                     ▼
>                               word_C6CE
>                                     │
>                     sub_AF6E8 (correction)
>                                     ▼
>        word_C6C8 = min(word_C6CE, word_C646)
>        word_C6C8 = max(word_C6C8, word_C6C2)      ← plancher
>        repli : word_C6C8 = word_1432[2]
>                                     ▼
>                       écart avec word_C91C → régulateur sub_B35B6
> ```
>
> **Le régulateur de ralenti est donc complet et documenté** : consigne (`word_C6C8`), mesure (`word_C91C`), écart, régulateur P/I (`sub_B35B6`), correction (`word_C69E`), réinjection dans la quantité (`word_C6BA + word_C69E`), bornage de la consigne (`word_C6C2`, `word_C646`), et repli dégradé (`word_1432[2]`).

---

## 4. Tableau de confiance de toute l'analyse

| # | Affirmation | Statut |
|---|---|---|
| 1 | Capteur vilebrequin = `P2.6` → capture `CC6` → PEC5 → `0F8DEh` | **constat** |
| 2 | Grille 16 mots `0xD926` = 2 × 8 événements/cycle | **constat** |
| 3 | Double grille 32 bits `0xD5C0` indexée par `byte_C8F3` | **constat** |
| 4 | Machine d'état de synchro `byte_CA39` (états 0…20h) | **constat** |
| 5 | Phase AAC = `byte_CA3A`/`byte_CA38` → `word_C416` bit 9 | **constat** |
| 6 | Gap : fenêtre `K/période` + timeout `K×période` + DTC `2FEh` | **constat** |
| 7 | Enregistrement de mesure `0xF622` + 3 instantanés (`F63E`/`F64E`/`F65A`) | **constat** |
| 8 | `word_1432` = 16 seuils régime/temps/saturation | **constat** |
| 9 | `word_C562` = second régime, écrit par le service OS `unk_2172` | **constat** |
| 10 | `sub_94446` = autocontrôle CAPCOM2/T8/PEC (motif `byte_F602`) | **constat** |
| 11 | `word_C6A6` = cartographie (régime × charge) | **constat** |
| 12 | `word_C632` = mot d'état gardant le régulateur | **constat** |
| 13 | `word_C6BA` = **quantité d'injection** | **inférence haute** |
| 14 | `word_C6B0` = durée d'injection | **FAUX** (était une erreur de l'étape 5) |
| 15 | Conversion quantité → durée | **absente de l'image** |
| 16 | Étage de sortie (compare d'injecteur) | **absent de l'image** |

---

## 5. Ce qui reste vraiment à faire

1. **La liste de pointeurs `0xBD02…`** (bloc diagnostic) : la seule inconnue franchissable **sans** la mémoire basse — par point d'arrêt sur `0xBDB40`.
2. **`word_1B66` / `word_1B68`** : les deux cartographies d'injection. Leurs adresses sont dans la mémoire basse, mais **elles pointent dans le Datensatz présent dans l'image** (`0xE0000–0xEBFFF`) — donc en croisant les pointeurs du Datensatz (151 pointeurs 32 bits à `0xE0008`), on peut **retrouver les tables physiques** et éventuellement les lire.
3. **`word_1470`, `word_147E`, `word_1434`, `word_1438`, `word_1432`, `word_1438`, `word_1668`, `word_1674`** : tous des pointeurs consécutifs `0x143x`–`0x16xx`. Cette **table de pointeurs de la mémoire basse** est le chaînon manquant n°1 de toute l'analyse.

---

*Livrables cumulés : `ENQUETE_capteur_regime_60-2.md`, `ETAPE1` → `ETAPE6`, `taches_jeton_CC27.csv`, `outils/ctx.py`.*
