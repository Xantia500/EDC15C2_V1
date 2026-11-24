# ÉTAPE 37 — Service 0x21 du boot (accès mémoire) et gestionnaire des défauts

Les deux dettes de l'étape 36 sont soldées.

---

## 1. ★ Service 0x21 du boot = `ReadDataByLocalIdentifier` — et **oui, c'est un accès mémoire**

`sub_FE4AE`, l. 405950-406136. Structure :

```asm
                mov     r4, word_FC1A
                mov     [r0+#0Ah], r4
                mov     r9, #0FA24h         ; tampon de réponse
                movb    rl6, [r4+#1]        ; ← IDENTIFIANT LOCAL (1 octet)
                movb    rl4, #61h ; 'a'
                movb    [r5], rl4           ; 0x61 = réponse positive à 0x21 ✔
                movb    [r4], rl6           ; écho de l'identifiant
                cmpb    rl6, #0F0h
                jmpr    cc_NC, loc_FE522
```

### 1.1 Identifiant `0x80` — parcours d'une table par **pointeur 24 bits**

```asm
                extp    #3Eh, #2
                mov     r4, word_FBF38      ; = 0x232C
                mov     r5, word_FBF3A      ; = 0x3E
                mov     [r0], r4
                mov     [r0+#2], r5         ; ← pointeur FAR (offset 0x232C, page 0x3E)
...
loc_FE522:
                mov     r4, [r0]
                mov     r5, [r0+#2]
                mov     r2, r4
                add     r2, #1
                mov     [r0], r2            ; incrémente l'offset
                extp    r5, #1
                movb    rl3, [r4]           ; ← DÉRÉFÉRENCEMENT 24 BITS
                movb    [r4], rl3           ; émission de l'octet
```

Avec `page 0x3E × 0x4000 = 0xF8000`, le pointeur désigne **`EA 0xFA32C`** — dans la zone
application. La limite de parcours est l'octet **`byte_FBEF9`** (`EA 0xFBEF9`) : `0xFF` → octet de
bourrage, `≥ 0xF0` → marqueur, sinon octet de données. **22 octets maximum** (`rl7 ≤ 0x15`).

⇒ **Oui : ce service est une primitive de lecture mémoire**, pilotée par un pointeur stocké en RAM
(`word_FBF38/F3A`). C'est le mécanisme qu'utilise un outil de programmation pour lire des zones
arbitraires.

### 1.2 Identifiant `< 0xF0` — deux blocs de **24 octets**

```asm
                mov     r4, r8
                cmpb    rl4, byte_FB83      ; nombre d'entrées
...
                movbz   r4, rl6
                and     r4, #1              ; ← bit 0 de l'identifiant
                mov     r5, r4
                shl     r5, #2
                sub     r5, r4              ; ×3
                shl     r5, #3              ; ×24
                mov     r10, [r0]
                add     r10, r5             ; décalage de 24 octets
...
loc_FE5E6:
                movb    rl3, [r4]
                movb    [r4], rl3
                addb    rl7, #1
                cmpb    rl7, #18h           ; 24 octets
                jmpr    cc_C, loc_FE5E6
```

Un identifiant `0…0xEF` sélectionne donc **un de deux blocs de 24 octets** selon son **bit 0**
(`r5 = (id&1) × 24`), après une recherche menée par `unk_7038` (**EA `0x07038`**, couche absente) et
bornée par `byte_FB83`. La boucle appelle `srvwdt` (réveil du chien de garde) — cohérent avec une
opération longue.

### 1.3 Au-delà

- identifiant `≥ 0xF0` et `≠ 0x80` → `[r0+#6] = 1` → **NRC 0x12** (l. 405991, 406129).
- La réponse est publiée par `word_FC0C` (l. 406126).

---

## 2. ★ `sub_CE43C` — le gestionnaire des défauts (ajout / suppression / effacement)

`sub_942DE` y mène (via changement de contexte). Sélecteur dans `rh6` :

### 2.1 Sélecteur `0x80` = effacement total

```asm
loc_CE44A:
                cmpb    rh6, #80h
                jmpr    cc_NZ, loc_CE4B6
                movb    rl0, byte_E466
                jmpa    cc_Z, locret_CE57C   ; rien à effacer
                mov     r0, #0E467h
                mov     r1, r0
                movb    [r0], ONES           ; premier octet = 0xFF
                mov     r2, #0E501h
                sub     r2, r0               ; ← LONGUEUR = 0xE501 − 0xE468 = 0x99
                calls   0, unk_2A9A          ; memset
                movb    byte_E501, ONES
                movb    byte_E466, ZEROS     ; compteur = 0
                mov     r0, #0CAD0h
                movb    [r0], ZEROS
                mov     r2, #17Fh            ; ← 383 octets
                calls   0, unk_2A9A
                mov     r0, #0FD21h
                movb    [r0], ZEROS
                mov     r2, #5Fh             ; ← 95 octets
                calls   0, unk_2A9A
```

**Trois confirmations d'un coup :**

1. **`154 = 7 × 22` une troisième fois**, par une voie indépendante : `0xE501 − 0xE468 = 0x99 = 153`,
   plus l'octet initial ⇒ **154 octets** de `0xE467` à `0xE500`. ✔
2. `unk_2A9A` (**EA `0x02A9A`**) est le **`memset`** de la couche absente (le pendant de
   `unk_2144`).
3. ★ **Deux blocs RAM supplémentaires sont liés aux défauts** — je ne les avais pas :
   - **`0xCAD0` … `0xCC4F` (384 octets)**, avec `byte_CCA8` mis à `0xFF` ;
   - **`0xFD21` … `0xFD80` (96 octets)**.

### 2.2 Sélecteur `0xEF` = suppression d'**un** défaut

```asm
loc_CE4C0:
                cmpb    rl0, byte_E466
                jmpr    cc_NC, locret_CE57C      ; fin de liste
                movb    rh5, [r2+#0]             ; numéro du défaut
                cmpb    rh6, #0EFh
                jmpr    cc_NZ, loc_CE4E0
                cmpb    rl6, rh5
                jmpr    cc_NZ, loc_CE512         ; pas celui-là
                bset    r5.0
                bset    r5.1                     ; marqué pour suppression
```

### 2.3 Autres sélecteurs = ajout / mise à jour

`loc_CE4E0` : lit `[r2+#1]` (drapeaux), teste `r3.0`, `r6.13`, `r6.15`, compare `rl1` à `rl6` →
parcours avec compteur. **Je n'ai pas encore décodé cette branche en entier** : elle gère
l'insertion et le comptage des occurrences. **Non conclusif à ce stade.**

---

## 3. ★ Nuance importante sur la persistance des défauts — je corrige ma formulation

À l'étape 35 §1.5 j'ai écrit : « **aucun tableau de défauts n'est présent dans l'image EEPROM** ».
C'est vrai **pour le bloc `0xE5CE`**, mais ma conclusion implicite était trop forte. Ce que
`sub_A0002` construit à `0xE5CE + offset` est **la copie de travail des seuls champs décrits par la
table de descripteurs** (42 commandes, offsets inconnus). **Ce n'est pas l'image complète des
1 024 octets.**

Conséquence logique : **l'EEPROM physique peut parfaitement contenir une zone de défauts en dehors
des 42 champs**, et la couche absente — qui possède la table `0x0BA6`, la table de pages `0x0FE00`
et le power latch — peut recopier n'importe quel bloc RAM vers la puce **sans passer par
`sub_A0002`**.

⇒ **Formulation corrigée** : *rien dans la couche visible ne montre de chemin de persistance des
défauts ; cela ne prouve pas leur non-persistance, puisque la couche qui écrit physiquement la puce
est absente.* Idem pour le kilométrage : celui-là **a** un chemin visible (`word_D7A`), ce qui montre
que la persistance passe bien par les champs décrits — mais seulement pour les quantités que
l'application gère elle-même.

---

## 4. Tableau de bord

| question | état |
|---|---|
| service 0x21 du boot | **décodé** : accès mémoire par pointeur 24 bits ✔ |
| table à `EA 0xFA32C` | **localisée**, contenu non décodé |
| gestionnaire des défauts | **`sub_CE43C`** : 0x80 = tout, 0xEF = un ✔ |
| nombre de défauts | **7 × 22 octets** (3ᵉ confirmation) ✔ |
| blocs liés | `0xCAD0+384`, `0xFD21+96` **nouveaux** |
| persistance | **indécidable dans la couche visible** (formulation corrigée) |
| antidémarrage | non localisé |

---

## 5. Prochaines actions

1. **`0xCAD0` (384 octets)** : structure inconnue liée aux défauts — 384 = 7 × 54,9 ; à cartographier
   par les indexations.
2. **`0xFD21` (96 octets)** : idem.
3. **`byte_FB83` / `byte_FBEF9`** : la table de `EA 0xFA32C` — taille et rôle.
4. **Branche d'ajout de `sub_CE43C`** (l. 229880-230000) : comptage d'occurrences et vieillissement.
5. **L'antidémarrage** : rester sur la chaîne de démarrage (`word_FC10` / `unk_7EC8` / le vote de
   `sub_94B1A`), et chercher une **seconde** variable protégée analogue à `byte_F62E`.
