# ÉTAPE 36 — Défauts : 7 × 22 octets. Configuration EEPROM : **triple redondance masquée par XOR**

Deux résultats fermes, et une **correction** de mon étape précédente.

---

## 1. ★ La mémoire des défauts est tranchée : **7 enregistrements de 22 octets**

### 1.1 La boucle de parcours — `sub_CE256`, l. 229616-229650

```asm
loc_CE2CC:
                cmpb    rl2, byte_E466      ; rl2 = index, byte_E466 = nombre
                jmpa    cc_NC, locret_CE43A ; index >= nombre -> fin
                ...
loc_CE2FC:
                add     r2, #1
                add     r3, #16h            ; ← AVANCE DE 0x16 = 22 OCTETS
                jmpr    cc_UC, loc_CE2CC
```

### 1.2 L'indexation — l. 229656-229665

```asm
                cmpb    rl6, byte_E466
                jmpa    cc_NC, locret_CE43A
                movbz   r4, rl6
                mov     r1, #16h
                mulu    r4, r1              ; ← index × 22
                mov     r3, MDL
                add     r3, #0E467h         ; ← base du tableau
                movb    rl2, [r3]           ; octet +0 = numéro de défaut
                movbz   r2, rl2
                mov     MDL, r2
                add     r2, r2
                add     r2, #0CCB2h         ; → table des codes (mots)
```

**⇒ Chaque enregistrement = `0x16` = 22 octets. `154 = 7 × 22` ⇒ 7 emplacements de défaut.**

*(L'ambiguïté « 7 × 22 ou 22 × 7 » de l'étape 35 est levée : `mulu r4,#16h` et `add r3,#16h` sont explicites.)*

### 1.3 Anatomie d'un enregistrement (22 octets), partiellement lue

| offset | rôle | preuve |
|---|---|---|
| **+0** | **numéro de défaut** → index dans la table `0xCCB2` (mots) | l. 229661-229666 |
| **+1** | drapeaux — bit 0 testé | l. 229620-229621 |
| **+2** | masque de bits, **compté** (popcount) | l. 229631-229641 |
| +4 | testé `== 0` | l. 229622-229623 |
| +6 | testé `!= 0` | l. 229625-229626 |
| +3, +5, +7…+15 | **non lus par ce code** → candidats pour les données de contexte | — |

**La freeze frame** est donc l'ensemble des octets non encore identifiés de ces 22 octets. Le
squelette (0, 1, 2, 4, 6) est **prouvé** ; le reste est **à cartographier**.

### 1.4 L'enregistrement « courant »

`0xE501`, **22 octets aussi**, avec `byte_E501` = son numéro, `0xFF` = aucun. Copié tel quel vers la
réponse du service 0x17 en même temps que le code (étape 35 §1.3).

```
0xE466  compteur (0…7)
0xE467  [7 × 22 octets]
0xE501  enregistrement courant (22 octets) — chevauche le suivant de 22 octets exactement
0xE517  fin
0xE5CE  image EEPROM
```

---

## 2. ★ La configuration EEPROM : **triple redondance masquée par XOR** — le bloc des commandes 0x0C / 0x0D

Voilà la « redondance » que tu supposais. Elle est **dans le code, explicite** (l. 127487-127527).

### 2.1 Lecture des champs

```asm
                mov     r12, #0Ch                  ; commande EEPROM 0x0C
                mov     r13, r0
                calls   0Ah, sub_A0002             ; -> handle dans [r0]
                mov     r12, #0F7F6h
                mov     r13, [r0]
                movbz   r14, rl6
                calls   0, unk_2128                ; copie du champ EEPROM vers 0xF7F6
```

et pour la commande **0x0D** → copie vers **`0xF7FD`** (l. 127556).

⇒ **Les commandes 0x0B, 0x0C, 0x0D portent la configuration véhicule**, et elle est **recopiée en
RAM vive** au démarrage pour être vérifiée.

### 2.2 La vérification — trois mots, trois masques

```asm
                mov     r4, word_F7F6
                xor     r4, word_B8E        ; ← masque n°1
                mov     r5, word_F7F8
                xor     r5, word_B90        ; ← masque n°2
                cmp     r4, r5
                jmpr    cc_NZ, loc_94F10    ; différent -> INVALIDE
                mov     r4, word_F7F6
                xor     r4, word_B8E
                mov     r5, word_F7FA
                xor     r5, word_B92        ; ← masque n°3
                cmp     r4, r5
                jmpr    cc_NZ, loc_94F10
                mov     r4, word_F7F8
                xor     r4, word_B90
                mov     r5, word_F7FA
                xor     r5, word_B92
                cmp     r4, r5
                jmpr    cc_Z, loc_94F14     ; les trois égaux -> VALIDE
```

**Trois copies de la même valeur, chacune obfusquée par un masque différent ; validité = les trois
concordent.** C'est une **redondance triple à masques**, pas un checksum.

### 2.3 Les trois octets de la commande 0x0D

```asm
                movb    rl4, byte_F7FD
                cmpb    rl4, byte_F7FE
                jmpr    cc_Z, loc_94FD8
                cmpb    rl4, byte_F7FF
                jmpr    cc_Z, loc_94FD8
                movb    rl5, byte_F7FE
                cmpb    rl5, byte_F7FF
                jmpr    cc_Z, loc_94FD8
```
Même principe, **sans masque** : trois octets identiques ⇒ valide.

### 2.4 Le chemin de réparation — et il est révélateur

Si les trois octets diffèrent (l. 127578-127596) :

```asm
                andb    rl4, #0F8h
                orb     rl4, #2             ; bits [2:0] = 010
                ...
                andb    rl4, #9Fh           ; efface les bits 6 et 5
                movb    byte_F7FD, rl4
```
puis `byte_F800/F801/F802 = 0`, `byte_F608 = 1`, `sub_94C6A(0x0F)`.

⇒ En cas d'incohérence, le calculateur **réécrit une valeur canonique** (`bits[2:0] = 0b010`) et
passe le verdict à « invalide ». **C'est une auto-réparation bornée**, pas un simple refus.

### 2.5 Le second étage : un **vote de majorité sur 9 bits**

`sub_94B1A` (l. 127030-127060) :

```asm
                movb    rl7, #2
loc_94B22:
                mov     r5, r12
                add     r5, r4
                movb    rl4, [r5]
                andb    rl4, #7             ; 3 bits
                xorb    rl4, #2
                ; compte les bits posés de (octet & 7) ^ 2
                subb    rl7, #1
                cmpb    rl7, #0
                jmpr    cc_SGE, loc_94B22   ; 3 octets
                cmpb    rl6, #5
                jmpr    cc_C, loc_94B5A     ; < 5 bits -> 0
                movb    rl4, #1             ; >= 5 bits -> 1
```

**3 octets × 3 bits = 9 bits, seuil 5.** Un vote de majorité appliqué à la configuration.

### 2.6 Les masques sont hors de portée

`word_B8E`, `word_B90`, `word_B92` : **consultés uniquement** (aucun écrivain dans la couche
visible) ⇒ posés par la bibliothèque basse, comme `word_BBE`. **Leurs valeurs sont donc inconnues.**

---

## 3. ★ Correction de mon étape 35

J'y ai écrit, au sujet de `byte_F62E` : « **hypothèse non validée… c'est mon candidat n°1 pour le
verrou d'antidémarrage côté application** ». **Je retire cette hypothèse comme prioritaire.**

Le code montre que `byte_F608` (que `byte_F62E` recopie) est posé par la **vérification de la
configuration EEPROM** (commandes 0x0C/0x0D), pas par une trame d'antidémarrage :

```asm
loc_94F14 (les 3 mots concordent):
                bclr    USR0                ; "valide"
...
loc_94FD8:
                movb    rl4, byte_F80C
                jmpr    cc_Z, loc_94FEA
                mov     r12, #0F7FDh
                calls   9, sub_94B1A        ; vote de majorité
                cmpb    rl4, #0
                jmpr    cc_NZ, loc_94FF8
loc_94FEA:
                movb    byte_F608, #1       ; INVALIDE
                mov     r12, #0Fh
                calls   9, sub_94C6A
loc_94FF8:
                movb    byte_F608, ZEROS    ; VALIDE
                mov     r12, #0F0h
                calls   9, sub_94C6A
```

⇒ **`byte_F62E`/`byte_F608` = « configuration véhicule cohérente »**, protégé par les deux mots
magiques et sanctionné par `bclr IEN`. **Ce n'est pas le verrou d'antidémarrage.** L'antidémarrage
reste à localiser — probablement plus loin dans la chaîne de démarrage.

**Mais la découverte est plus intéressante que l'hypothèse** : on tient le **système d'intégrité du
codage véhicule**, et il est à **triple redondance masquée**. Voilà concrètement ce qu'un outil de
télécodage doit satisfaire pour être accepté.

---

## 4. Les quatre canaux EEPROM : `word_C460…word_C46A`

Déclarations (l. 49445-49453) : six mots **contigus** `0xC460, 0xC462, 0xC464, 0xC466, 0xC468,
0xC46A` (**12 octets**, comme une entrée de descripteur).

Utilisation : ce sont des **pointeurs vers un numéro de commande**, pas des valeurs.

```asm
loc_A1874:
                mov     r4, word_C462
                movb    rl5, [r4]           ; commande = octet pointé
                movbz   r12, rl5
                mov     r13, #0CFA4h
                calls   0Ah, sub_A0002
```

Écrits à l'initialisation (`word_C462` l. 49446 / site 128368-128548 pour `word_C468`). ⇒ **Quatre
canaux, commande choisie à l'exécution** : c'est bien l'**accès indirect** aux blocs EEPROM.

---

## 5. État du chantier

| question | état |
|---|---|
| nombre de défauts | **7** ✔ |
| taille d'un enregistrement | **22 octets** ✔ |
| code défaut | mot à +0, indexé dans `0xCCB2` ✔ |
| statut | octet à +5 (service 0x17) ✔ |
| freeze frame | dans les 22 octets, champs **non cartographiés** |
| redondance EEPROM | **triple + masques XOR** ✔ (masques inconnus) |
| checksum EEPROM | complément à 2 sur mots + quartets (étapes 29-30) ✔ |
| persistance des défauts | **non résolue** |
| antidémarrage | **non localisé** (piste `byte_F62E` écartée) |

---

## 6. Prochaines actions

1. **`sub_FE4AE`** (service 0x21 du boot) — toujours en attente, deux tours de suite : je le traite
   en priorité absolue.
2. **Octets +3, +5, +7…+15** de l'enregistrement de défaut → cartographie de la freeze frame.
3. **Qui écrit `0xE466`/`0xE467`** (la détection de défaut) → remonter à la persistance.
4. **`sub_94C6A`** : ce que signifie `0x0F` / `0xF0`.
