# ÉTAPE 42 — Deux types de moniteurs identifiés, et la logique de confirmation

---

## 1. ★ `word_CFD4` : un **bit par moniteur** — et deux moniteurs décodés

`loc_A2064`, l. 153294-153338. Le mot est d'abord remis à zéro, puis chaque moniteur peut poser **son
bit**.

### 1.1 Moniteur n°1 — **critère de DURÉE** (l. 153297-153319)

```asm
                mov     word_CFD4, ZEROS
                mov     r4, word_C0BE            ; compteur courant
                cmp     r4, word_F91C
                jmpr    cc_NC, loc_A2084
                mov     r4, word_C0BE
                sub     r4, word_F91C
                sub     r4, #1                   ; ← gestion du REBOUCLAGE
...
loc_A2084:
                mov     r4, word_C0BE
                sub     r4, word_F91C            ; r4 = delta écoulé
loc_A208C:
                mov     r5, word_142A
                mov     r2, [r5+#6]              ; ← SEUIL n°2  = handle + 6
                cmp     r4, r2
                jmpr    cc_C, loc_A20A2
                mov     r4, #1
                mov     word_CFD4, r4            ; ← MONITEUR 1 = bit 0
                mov     word_C0BE, ZEROS
```

**Le delta `word_C0BE − word_F91C` avec correction de rebouclage (`−1`) est le même idiome que le
kilométrage** (étape 31 : `word_C654 − word_E178` avec `word_CF6A`). C'est donc une **mesure de
durée** entre deux instants d'un compteur libre, comparée à un seuil de calibration.
⇒ **Moniteur n°1 = « condition présente plus longtemps que X ».**

### 1.2 Moniteur n°2 — **critère de VALEUR** (l. 153322-153338)

```asm
loc_A20A2:
                movb    rl4, byte_C2F5
                jmpr    cc_NZ, loc_A20D6          ; inhibition
                movb    rl5, byte_CFDC
                jmpr    cc_NZ, loc_A20D6          ; inhibition
                mov     r4, word_C0BC
                jmpr    cc_NZ, loc_A20D6          ; inhibition
                mov     r5, word_C908
                cmp     r5, word_CFB4
                jmpr    cc_SLE, loc_A20D6         ; borne de mesure
                mov     r2, word_142A
                mov     r3, [r2]                  ; ← SEUIL n°1 = handle + 0
                cmp     r3, word_C908
                jmpr    cc_NC, loc_A20D6
                mov     r3, #80h
                or      word_CFD4, r3             ; ← MONITEUR 2 = bit 7
                movb    byte_C2F5, ONES
```

⇒ **Moniteur n°2 = « mesure hors seuil »**, avec en plus une **borne de validité** (`word_CFB4`) et
**trois conditions d'inhibition** (`byte_C2F5`, `byte_CFDC`, `word_C0BC`).

`word_CFD4` est un mot de 16 bits ⇒ jusqu'à **16 moniteurs** ; deux sont identifiés (bit 0 et bit 7),
les autres ne sont pas encore localisés dans le code visible.

---

## 2. ★ `word_142A` est un handle vers une **STRUCTURE**, pas vers une valeur

Deux accès différents au même handle :

```asm
                mov     r5, word_142A
                mov     r2, [r5+#6]      ; seuil n°2  → offset +6
...
                mov     r2, word_142A
                mov     r3, [r2]         ; seuil n°1  → offset +0
```

⇒ **`handle + offset = champ`.** C'est le modèle « identité + type + tag » que tu avais posé au
début de nos travaux : le handle localise un **enregistrement** de calibration, et les **offsets
internes** sélectionnent les champs. **C'est la première fois que nous le voyons utilisé
explicitement avec deux offsets distincts**, ce qui le démontre au lieu de le supposer.

---

## 3. ★ `sub_A1E9E` : la logique de confirmation (défaut « mûr »)

Étiquettes l. 153093-153160. Deux branches selon le sélecteur.

### 3.1 Branche `0xFF` — lecture du **descripteur** du défaut

```asm
                mov     r5, word_CFBC
                movb    rl4, [r5+#1Ch]      ; ← octet +0x1C du DESCRIPTEUR
                movbz   r4, rl4
                and     r4, #3
                cmp     r4, #3
                jmpr    cc_SLT, loc_A1EDE
                movbz   r4, byte_CFBF
                and     r4, #41h
                cmp     r4, #41h
                jmpr    cc_NZ, loc_A1ECE
                movb    rl4, #1
                orb     byte_CFDB, rl4       ; ← bit de statut 1
loc_A1ECE:
                movbz   r4, byte_CFBF
                and     r4, #7
                cmp     r4, #7
                jmpr    cc_NZ, loc_A1EDE
                movb    rl4, #2
                orb     byte_CFDB, rl4       ; ← bit de statut 2
loc_A1EDE:
                movb    rl4, byte_CFBF
                andb    rl4, #40h
                jmpr    cc_Z, locret_A1F4E
                movb    rl5, [r4+#1Ch]
                and     r5, #4
                cmp     r5, #4
                jmpr    cc_NZ, locret_A1F4E
                movb    rl4, #1
                orb     byte_CFDA, rl4       ; ← bit de statut (autre quartet)
```

### 3.2 Branche `≠ 0xFF` — le **compteur de confirmation**

```asm
loc_A1F00:
                mov     r4, word_CFD6
                jmpr    cc_NZ, locret_A1F4E      ; déjà confirmé
                mov     r5, word_CFD4
                and     r5, r12                  ; ← le bit du moniteur doit être posé
                jmpr    cc_Z, locret_A1F4E
                cmp     r12, #80h
                jmpr    cc_NZ, locret_A1F4E
                movb    rl4, byte_CFC2
                jmpr    cc_NZ, locret_A1F4E      ; inhibition 1
                movb    rl5, byte_CFC3
                jmpr    cc_NZ, locret_A1F4E      ; inhibition 2
                movb    rl3, byte_CFC4
                jmpr    cc_Z, locret_A1F4E       ; compteur à zéro -> rien
                subb    rl3, #1
                movb    byte_CFC4, rl3           ; ← DÉCOMPTE
                cmpb    rl3, #0
                jmpr    cc_NZ, loc_A1F4A
                movbz   r4, byte_CFBF
                and     r4, #10h
                jmpr    cc_NZ, loc_A1F4A
                or      word_CFD6, r12           ; ← DÉFAUT CONFIRMÉ
```

**⇒ Le mécanisme complet :**

```
moniteur (bit de word_CFD4)
   ↓  inhibitions : byte_CFC2, byte_CFC3
   ↓  décompte : byte_CFC4  (une décrémentation par appel)
   ↓  quand il atteint 0 et que byte_CFBF.4 est libre
word_CFD6 |= bit du moniteur      ← défaut confirmé
```

C'est un **anti-rebond à compteur** : le défaut n'est déclaré qu'après **N occurrences consécutives**,
avec des conditions d'inhibition. Et **`byte_CFDB` (2 bits) / `byte_CFDA` (1 bit)** publient le
niveau de statut.

---

## 4. ★ Le descripteur par défaut, **confirmé par deux sites indépendants**

| site | code |
|---|---|
| `sub_A1E9E`, l. 153103 | `movb rl4, [r5+#1Ch]` avec `r5 = word_CFBC` |
| l. 230034-230040 | `mov r0, [r0+#0CCB2h]; movb rh0, [r0+#1Ch]; andb rh0, #3` |

Les deux appliquent **`+0x1C` au mot issu de la table `0xCCB2`**, et les deux en extraient des **bits
de statut** (`& 3` d'un côté, `& 3` puis `& 4` de l'autre).

⇒ **Le mot de `0xCCB2[n]` sert d'adresse**, et le descripteur du défaut se trouve à
**`mot + 0x1C`** — donc **dans la couche absente** (`mot ≈ 0x02xx < 0x80000`). Le champ à `+0x1C`
porte : bits 0-1 = classe (`cmp #3`), bit 2 = un drapeau comparé à `byte_CFBF & 0x40`.

**C'est la première assertion forte sur un descripteur de défaut**, et elle repose sur deux
lectures indépendantes.

---

## 5. Tableau de bord

| question | état |
|---|---|
| moniteurs | `word_CFD4`, 1 bit par moniteur ✔ ; **bit 0 = durée**, **bit 7 = valeur** |
| seuils | **structure** derrière `handle + 0 / + 6` ✔ |
| confirmation | compteur `byte_CFC4` + 2 inhibitions → `word_CFD6` ✔ |
| descripteur de défaut | à `mot(0xCCB2) + 0x1C`, **couche absente** ✔ (2 sites) |
| statut publié | `byte_CFDB` (2 bits), `byte_CFDA` (1 bit) ✔ |
| antidémarrage | non localisé |

---

## 6. Prochaines actions

1. **`word_CFD6`** : le mot des défauts **confirmés** — combien de bits, et qui le lit (voyant ?
   mode dégradé ?). C'est le lien direct avec la **conséquence** du défaut.
2. **`byte_C2F5`, `byte_CFDC`, `word_C0BC`** : les trois inhibitions — qui les pose ?
3. **`byte_CFC4`** : sa valeur initiale (pas de compteur = pas d'anti-rebond) → chercher où il est
   chargé.
4. **Antidémarrage** : angle « inhibition » — chercher une écriture de **zéro** sur la quantité
   injectée conditionnée par un drapeau. C'est la seule piste qui n'a pas encore été suivie.
