# Étape 4 — Résolution des quatre pistes ouvertes

*ECU 0 281 010 877 — EDC15C2 / C167CR-4RM — image `edc.bin`*
*EA = adresse du listing IDA (offset `.bin` = EA − 0x80000). **[constat]** = visible dans le binaire ; **[hypothèse]** = interprétation.*

---

## Piste 1 — Le bloc de mesure `0xF622` : l'ambiguïté est levée

### Le problème posé

À l'étape 3 je butais sur ceci : une copie atomique de 6 mots va de `0xF622` vers `0xF63E`, mais les mêmes mots étaient ensuite utilisés à la fois comme *compteur* (`byte_F63E`), *drapeau* (`byte_F63F`), *index* (`word_F642`) et *tableau de périodes*. Deux lectures incompatibles du même octet.

### Ce que j'ai trouvé en cherchant toutes les constantes

`0F622h` n'apparaît que **4 fois** dans toute l'image — et **aucune d'entre elles ne fait la même chose** :

| EA | Copie | Ligne |
|---|---|---|
| `0xC7621` | **`0xF622` → `0xF65A`** | 217622 |
| `0xC78B2` | **`0xF622` → `0xF64E`** | 217894 |
| `0xC7A3A` | **`0xF622` → `0xF63E`** | 218052 |
| `0xC7764` | **`0xF65A` → `0xF622`** (retour) | 217765 |

**[constat]** Ce ne sont donc pas deux vues du même bloc, mais **quatre** : un bloc partagé `0xF622` et **trois copies de travail** (`0xF63E`, `0xF64E`, `0xF65A`), chacune consommée par un calcul différent. Les quatre copies sont protégées de la même façon :

```
push  PSW
atomic #4
or    PSW, #0F000h        ; masque de priorité : aucune interruption pendant la copie
and   PSW, word_C1A8
nop
mov   r0, #0F622h
mov   r1, #0F63Eh         ; (ou 0F64Eh, ou 0F65Ah)
mov   [r1+], [r0]         ; 6 transferts de mots
...
pop   PSW
```

**[constat]** la protection `atomic #4` + `and PSW, word_C1A8` est identique dans les 4 cas : c'est bien la **même donnée**, copiée pour trois consommateurs.

### Les trois consommateurs, et ce qu'ils y voient

**Consommateur A — `0xF63E` : calcul de vitesse** (étape 2, §3)
`byte[0]` = **nombre d'entrées à additionner**, `word[1..5]` = les entrées.
`régime = K32(word_1702) / Σ` — confirmé par `loc_C7C16` et `loc_C7AD0`.

**Consommateur B — `0xF64E` : normalisation calibrée** (`0xC78B2`, jamais exploité jusqu'ici)
```
movbz r0, word_F64E+1        ; octet haut d'une valeur 32 bits
mov   MDH, r0
movbz r0, word_F64E          ; octet bas = INDEX
mov   r0, [r0+#0F650h]       ; mot lu dans un tableau à 0xF650
mov   MDL, r0
mov   r3, word_1706
mov   r0, [r3+#6]
divl  r0                     ; division 32 bits (DIVL)
mov   r0, [r3+#4]
add   MDL, r0                ; + offset de calibration
mov   r0, [r3+#0] ; cmp ; clamp mini
mov   r3, [r3+#2] ; cmp ; clamp maxi
```
**[constat]** ici `byte[0]` du bloc est un **index** dans un tableau à `0xF650`, et `byte[1]` + `word[1]` forment une **valeur 32 bits**. Elle est divisée par `word_1706[6]`, décalée de `word_1706[4]`, puis bornée à `[word_1706[0], word_1706[2]]`. C'est une **mise à l'échelle calibrée avec saturation** — le schéma classique Bosch « valeur brute → grandeur physique ».

**Consommateur C — `0xF65A` : la quantité 32 bits elle-même**
Deux écrivains, tous deux dans la bibliothèque de mesure ROM :

```
sub_8FA1A:
        movb  rl4, [r0]      ; index passé par l'appelant
        movbz r12, rl4
        mov   r13, #1F4h     ; code de calibration
        calls 8, sub_8FF62   ; -> r4:r5 = valeur 32 bits
        mov   word_F65A, r4  ; MOT HAUT
        mov   word_F65C, r5  ; MOT BAS
```

et l'ISR de dent (`loc_C768E`, EA `0xC768E`) qui y écrit le **delta de capture** :

```
mov  r2, r1
sub  r2, r9                  ; delta des deux derniers horodatages
mov  r3, r10
subcb rl3, #0                ; propagation de retenue (24 bits)
mov  [r4+#0F65Ch], r2        ; mot bas
movb word_F65A+1, rl3        ; octet haut
movb word_F65A, rl4          ; octet bas = compteur de cycle
```

### Réponse

> Il n'y a **pas** de conflit. Le bloc `0xF622` est un **enregistrement de mesure de 12 octets** :
>
> | Offset | Champ | Nature |
> |---|---|---|
> | `+0` (`byte_F622`/`byte_F63E`) | **sélecteur / compteur N** | 0 = pas de mesure |
> | `+1` (`byte_F623`/`byte_F63F`) | octet haut de la valeur | **drapeau** pour le consommateur A |
> | `+2` (`word_F624`/`word_F640`) | **mot bas de la valeur 32 bits** | période de dent |
> | `+4` … `+0Ch` | 5 mots de la même famille | entrées additionnées par A, indexées par B |
>
> Les trois copies ne sont pas redondantes : **chacune fige l'enregistrement au moment où un calcul différent le consomme** — c'est un mécanisme de cohérence, pas une duplication.

**Correction apportée à l'étape 2 :** j'y écrivais « somme de N périodes indépendantes ». La forme est juste (on additionne bien `byte_F63E` entrées), mais les mots additionnés **appartiennent au même enregistrement** et ne sont pas cinq périodes de dents successives. La lecture « historique glissant de 5 périodes » est **abandonnée**.

**Ce qui reste ouvert :** le sens réel de `byte_F624` quand la mesure est invalide. Les écritures `movb word_F624, #14h/#1Eh/#28h/#32h/#3Ch/#46h` de `sub_8F4CC` sont **toutes** sur des chemins de sortie d'erreur (`jmpa cc_UC, loc_8F7BC`). L'explication la plus économique reste une **union** : valeur quand la mesure est valide, code d'étape quand elle ne l'est pas. Vérifiable en posant un point d'arrêt sous IDA sur `0x8F6F8`.

---

## Piste 3 — `word_1432` : table de 16 seuils **régime / temps**

**[constat]** `word_1432` est **déréférencé 29 fois**, toujours avec un offset pair entre `+0Ah` et `+2Eh` → une structure de **16 mots (32 octets)**. Jamais écrite, seulement lue : c'est un pointeur de la mémoire basse.

Table complète, reconstituée à partir de ce qui est comparé :

| Offset | Ce qui est comparé | Sous-programme |
|---|---|---|
| `+0` | recopié dans `word_DB2A` | `sub_AFAA0` |
| `+2` | recopié dans `word_C6C8` (utilisé ensuite comme **décalage** additif) | `sub_AFAA0` |
| `+4`, `+6` | recopiés dans `word_C6D0` / valeurs d'échelle | `sub_AF520` |
| `+8` | `word_F91C − …` (une **durée**) → si dépassée, `word_C10A = 0` | `sub_AFAA0` |
| `+0Ah` / `+0Ch` | deux variantes de `word_DB2C` selon le signe d'une différence | `sub_AFAA0` |
| `+0Eh` | `≥ word_C562` (régime) → bit `2000h` | `sub_AFAA0` |
| `+12h` / `+14h` | **fenêtre basse/haute** vs `word_C91C` → bit `1000h` si dehors | `sub_AFAA0` |
| `+16h` | borne de saturation de `word_DA14` | `sub_B35B6` |
| `+18h` / `+1Ah` | bornes de saturation de `word_C94A` | `sub_AFAA0` |
| `+1Ch` | comparé à `word_DB2A` | `sub_AFAA0` |
| `+1Eh` | **offset ajouté** à une valeur mesurée, avec test de débordement V/N | `sub_B35B6` |
| `+20h` | opérande de `unk_20AC` | `sub_B35B6` |
| `+22h` | `> word_C562` | `sub_AFAA0` (2×) |
| `+24h`, `+26h`, `+28h` | `seuil + word_C6C8` comparé à `word_C91C` → **bandes d'hystérésis** autour d'un régime | `sub_AFAA0`, `sub_B35B6` |
| `+2Ah` | comparé à `word_C658 + word_C65A` | `sub_AFAA0` |
| `+2Ch` | `≥ word_C562` | `sub_AFAA0` |
| `+2Eh` | `≤ word_C93E` | `sub_AF520` |

**Réponse :** `word_1432` n'est pas une cartographie mais un **jeu de seuils de décision** : des bornes de régime (`+0Eh`, `+12h`, `+14h`, `+22h`, `+24h`, `+26h`, `+28h`, `+2Ch`), des durées (`+8`), et des bornes de saturation pour deux grandeurs (`+16h`, `+18h`, `+1Ah`, `+1Ch`, `+1Eh`, `+20h`).
**[hypothèse]** la présence simultanée de régime, de durées et d'une **hystérésis réglable** autour d'un régime correspond au jeu de conditions de **reconnaissance de phase de fonctionnement** (ralenti / conduite / décélération / coupure) — c'est ce que le mot `r8` construit dans `sub_AFAA0` (bits `20h`, `30h`, `100h`, `200h`, `400h`, `1000h`, `2000h`, `40h`) et qui est publié dans **`word_C632`**.

**[constat]** `word_C632 = r8` (ligne 178741) — **c'est le mot d'état de fonctionnement**. Toute la logique de commutation du calculateur se branche là-dessus.

---

## Piste 4 — `word_C562` : le second régime, écrit par un service OS

### Le problème

`word_C562` est lu **29 fois** comme seuil de régime (comparé à `word_1432[0Eh/12h/14h/22h/24h/26h/28h/2Ch]` et à `word_16F0[0]/[2]`), et n'a **aucun écrivain direct** dans l'image.

### Le coupable est trouvé

Une seule référence à la constante `0C562h` dans toute l'image — et c'est bien l'écrivain :

```
sub_9B2B2:
        mov   r12, #0C562h        ; <-- DESTINATION passée au service
        mov   r4, word_1674
        mov   r13, [r4]           ; opérande bas
        mov   r14, [r4+#2]        ; opérande haut  (=> entrée 32 bits)
        calls 0, unk_2172         ; service OS : calcule et écrit à [r12]
        mov   [r0], r4
        cmp   r4, #0
        jmpr  cc_ULE, loc_9B2D2   ; saturation basse à 0
        ...
        cmp   r4, #0FFFEh
        jmpr  cc_NC, loc_9B2E8    ; saturation haute à 0xFFFE
        ...
loc_9B2E8:
        mov   r4, #0FFFEh
```

**[constat]** :
* `word_C562` est écrit par le **service OS `unk_2172`** (qui n'est pas dans l'image — il est en mémoire basse), appelé avec `r12` = adresse de destination ;
* l'entrée est une **valeur 32 bits** lue dans `word_1674[0..2]` ;
* le résultat est **borné à `[0, 0xFFFE]`** ;
* la même valeur est publiée en octets dans `byte_C81B` (haut) et `byte_C81C` (bas).

Le motif `32 bits ÷ constante → saturation` est **exactement celui du calcul de régime** (étape 2, §3 : `K32 / Σpériodes`). D'où :

**Réponse : deux régimes coexistent dans ce calculateur.**

| Variable | Origine | Usage |
|---|---|---|
| `word_C91C` (et `word_C42E` en amont) | tâche de mesure de l'image (`0xC7D34`, `0xC7D46`) | **régime « application »** : axe des cartographies, fenêtres `word_1432[12h/14h]` |
| **`word_C562`** | **service OS `unk_2172`**, entrée `word_1674` (32 bits) | **régime « système »** : machine d'état de synchro (`word_16F0[0]/[2]`) et seuils `word_1432` |

**[hypothèse]** le second est le régime calculé par la couche commune (OS/« BSW ») à partir de sa propre mesure, avec sa propre calibration (`word_1674`), et il sert aux décisions **lentes ou critiques** (synchro, conditions de diagnostic) tandis que le premier, rapide et lié aux événements de dent, sert aux **calculs angulaires**. C'est un dédoublement volontaire : la synchro ne doit pas dépendre d'une valeur recalculée par l'application.

---

## Piste 2 — `sub_94446` : ni sortie d'injection, ni simple test PEC

### Ce que le code fait vraiment

Le routine s'appuie sur **trois** sous-programmes et un mot de contrôle.

**a) `sub_943D4` (EA `0x943D4`) — validation de pointeur par les chip-selects**

```
sub_943D4:
        cmp   r12, #0F7DDh        ; borne du tampon
        ...
        mov   r4, r12
        mov   r5, r4
        shr   r5, #14             ; r5 = adresse / 16 Ko  => n° de bloc
        shl   r5, #1
        mov   r5, [r5+#0FE00h]    ; <-- ADDRSEL1..4 !
        bmov  r4.14, r5.0
        bmov  r4.15, r5.1
        shr   r5, #2
        cmp   r4, word_FCE6       ; comparé à la destination PEC
```

**[constat]** `0xFE00 + 2·(adresse >> 14)` = **ADDRSEL1…ADDRSEL4** du C167. La routine vérifie que le pointeur `word_F7DE` tombe dans un bloc mémoire dont le chip-select est **effectivement armé**, et que sa sélection correspond à `word_FCE6`. C'est une **protection contre les pointeurs fous** avant un transfert PEC.

**b) `sub_8FF62`-like : `sub_943C0` = division saturée**

```
sub_943C0:  mov MDL, r12 ; divu r13 ; jmpr cc_V, loc_943CE
            mov r4, MDL ; rets
loc_943CE:  mov r4, #0FFFFh ; rets      ; débordement -> 0xFFFF
```

**c) Le cœur : compilation du motif `byte_F602` en train d'impulsions** (`loc_948A2`)

```
        cmpb  rl4, #0Ah                      ; état 10 = armé
        bset  word_FD00.0
        mov   r7, #5
        mov   CC2_CC23, r7                   ; première comparaison
        mov   r7, #1A5h                      ; puis 421
        mov   r4, #0F7B6h ; mov word_F7DE, r4   ; pointeur de table
        mov   r8, #2                         ; 2 passes
loc_948C6:
        mov   r4, #0                     ; index = 0
loc_948CC:
        mov   r4, [r0+#4]
        mov   r5, #1
        shl   r5, r4                     ; masque = 1 << index
        movbz r2, byte_F602
        and   r2, r5                     ; <-- bit 'index' du motif 8 bits
        ...
        cmpb  rl4, #0
        bmovn USR0, Z
        bmov  r9.0, USR0                 ; r9.0 = le bit voulu
        bcmp  word_FD00.0, r9.0          ; comparé au NIVEAU COURANT de la ligne
        jmpr  cc_NN, loc_94914           ; identique -> pas de transition
        mov   [r4], r7                   ; transition -> on inscrit la valeur
        add   word_F7DE, #2
        bxor  word_FD00.0, ONES.0        ; bascule l'état de ligne
loc_94914:
        add   r7, #1A0h                  ; 1 bit = 416 ticks
        ...
        cmp   r4, #7 ; jmpr cc_SLE, loc_948CC    ; 8 bits
```

**[constat]** `byte_F602` = un **motif de 8 bits**. Chaque bit dure **416 ticks** (`#1A0h`). Une **transition** (bit ≠ niveau courant) fait écrire une valeur de comparaison supplémentaire dans la table. Il y a ensuite un marqueur de trame (`+340h = 832`, `+2134h = 8500`) et **deux passes** (`r8 = 2`).

Puis l'armement matériel :

```
        mov   CC2_T8, #0
        mov   r4, #0F7B6h
        mov   r5, word_F7DE
        sub   r5, r4
        ashr  r5, #1                       ; nb de mots écrits
        or    r5, #400h
        mov   PECC1, r5                    ; COUNT | bit 10
        mov   r5, #0F7B6h ; mov word_FCE4, r5   ; source  = la table
        mov   r2, #0FE6Eh ; mov word_FCE6, r2   ; dest    = CC23 (FE6Eh)
        extr  #2
        bclr  IR
        bset  IE
        bset  T8R                          ; GO
```

**d) Le retour d'information** — lu sur une **broche** (`loc_94550`) :

```
        mov  r4, P2
        and  r4, #1                        ; <-- P2.0 = CC0IO
        jnb  r4.0, loc_94564
        or   r4, #0FFFEh
loc_94564:
        cmp  r4, #0
        bmovn USR0, Z
        bmov r9.0, USR0                    ; niveau attendu = niveau LU sur la broche
        ...
        bmov word_FD00.0, r9.0
```

Puis, sur les transitions suivantes, `sub_943D4` revalide le pointeur et `sub_943C0` divise par `0x1A0` (416) — **contrôle de la durée réellement écoulée** :

```
        mov  r12, [r0]
        mov  r13, #1A0h
        calls 9, sub_943C0
        add  r4, #1
        shr  r4, #1
```

### Réponse

> `sub_94446` / `sub_94428` / `sub_943D4` forment un **autocontrôle de la chaîne CAPCOM2 + T8 + PEC** :
> 1. un motif de 8 bits (`byte_F602`) est **compilé** en une table de valeurs de comparaison (1 bit = 416 ticks = 52 µs à 8 MHz) ;
> 2. la table est **validée** (ADDRSEL) puis **injectée par PEC1** dans `CC23` et suivants ;
> 3. `T8` est lancé ;
> 4. la **durée réelle** et le **niveau relu sur `P2.0`** sont confrontés au motif attendu ;
> 5. résultat publié dans `word_F7E6` (bits 0…3), `byte_F7E5` (état), `byte_F7E9`, `byte_F7E8` → `byte_D4E8`, et `byte_D4E9…D4ED`.
>
> **Ce n'est pas une sortie d'injection.** Les registres de mode `CC2_M4…M7` ne sont **jamais** écrits (canaux `CC16…CC31` au repos), ce qui interdit un usage en sortie de puissance. **Ce n'est pas non plus un simple test PEC** : la relecture de `P2.0` (CC0IO) et le contrôle de durée en font un **test de bout en bout du sous-système capture/compare**.

**[hypothèse]** c'est le test d'initialisation qui arme la confiance dans le matériel CAPCOM avant d'autoriser la génération d'impulsions — même famille que le contrôle 3-strikes de `sub_88A6C` (étape 3, §2). Le lien physique entre la sortie `CC23` (P8.7 / P1H.x / P7.x selon la banque) et l'entrée `P2.0` reste à établir **sur la carte**, pas dans le code.

---

## Synthèse des quatre pistes

| Piste | Verdict | Impact |
|---|---|---|
| **1. `0xF622`** | **Résolu.** Un enregistrement de mesure de 12 octets, **trois copies de travail** (`0xF63E`, `0xF64E`, `0xF65A`) pour trois consommateurs. `+0` = sélecteur/compteur, `+1` = octet haut, `+2` = mot bas d'une valeur 32 bits. | L'étape 2 est **corrigée** : pas d'« historique de 5 périodes » |
| **3. `word_1432`** | **Résolu structurellement.** Table de **16 mots** de seuils régime/durée/saturation, lue 29 fois, jamais écrite. `word_C632` = mot d'état de fonctionnement. | Le squelette de la commutation d'états est entièrement cartographié |
| **4. `word_C562`** | **Écrivain trouvé** : service OS `unk_2172` depuis `word_1674` (32 bits), saturé à `0xFFFE`. | **Deux régimes** distincts : `C91C` (application) et `C562` (système) |
| **2. `sub_94446`** | **Requalifié** : autocontrôle CAPCOM2/T8/PEC (compilateur de motif 8 bits + relecture `P2.0` + contrôle de durée + validation ADDRSEL). | Ce n'est pas l'étage de sortie d'injection |

---

## Ce qu'il reste, et qui ne dépend plus de la mémoire basse

Trois chantiers encore exploitables **dans l'image seule** :

1. **`byte_F602` et `word_F7E6`** : remonter l'appelant de `sub_94446` (jeton de tâche `0x380`) pour savoir *qui* demande le test et *quand*. Piste : `taches_jeton_CC27.csv` → `0x380` = `sub_94446` (ligne 126336).
2. **`word_1674`** : structure de calibration du régime système. Ses lecteurs sont peu nombreux — les `xrefs` donneront l'origine de la seconde mesure.
3. **Le mot d'état `word_C632`** : ses lecteurs disent *tout* de la stratégie du calculateur (démarrage à froid, ralenti, pleine charge, coupure, post-injection). C'est le meilleur point d'entrée pour la suite du raisonnement.

Et un chantier qu'il faut **arrêter d'espérer dans l'image** : l'écriture effective des valeurs de comparaison d'ouverture/fermeture d'injecteur. Aucune instruction de l'image ne touche `CC8`, `CC9` (hors mode), `CC15` en compare, ni `SRCPx`/`DSTPx`. **Cet étage est dans la moitié basse.** On peut en revanche en déduire le **format** attendu (double-registre `CCx`/`CCz`, étape 3 §1), ce qui suffira à le reconnaître dès qu'on aura le dump.

---

*Livrables de cette étape : le présent document, `taches_jeton_CC27.csv` (étape 3) et `outils/ctx.py` (outil de navigation : `var`, `sub`, `show`, `map`).*
