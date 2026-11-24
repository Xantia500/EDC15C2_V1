# ÉTAPE 33 — L'accès EEPROM est **centralisé** : 42 commandes, un descripteur de 12 octets, un octet de codage

Cette étape répond enfin à la question posée depuis le début de la session : *où sont les fonctions qui
écrivent l'EEPROM, et comment le « codage » (régulateur, clim…) est-il représenté ?*

---

## 1. Un seul point d'entrée : `sub_A0002(cmd, &out)` — l. 149775-149902

```asm
                mov     r6, r12          ; cmd
                mov     r8, r13          ; pointeur de sortie
                mov     r9, #0
                mov     [r5], r4         ; *out = 0
                cmpb    rl6, #29h        ; cmd > 0x29  ->  rejet
                jmpa    cc_UGT, loc_A010C
                movbz   r4, rl6          ; r4 = cmd
                mov     r5, r4
                shl     r5, #2
                sub     r5, r4
                shl     r5, #2           ; r5 = cmd * 12   ← ENTRÉE DE 12 OCTETS
                movb    rl4, [r5+#0BAEh] ; ← TYPE  (0x0BA6 + 8)
                cmpb    rl4, #1
                jmpr    cc_Z, loc_A0034  ; type 1 -> sub_A09E4
                cmpb    rl4, #4
                jmpr    cc_Z, loc_A0082  ; type 4 -> sub_A0B72
```

**Le nombre de commandes est borné à 42** (`0x00 … 0x29`). C'est le catalogue complet des blocs
EEPROM : **42 entrées**, chacune décrite par **12 octets** dans une table à **`0x0BA6`**.

### Le format du « handle » retourné

```asm
                mov     r4, [r5+#0BA6h]  ; offset du bloc dans l'image
                ...
                mov     r5, [r2+#0BA8h]  ; sous-offset
                add     r4, r5
                mov     r5, #0E5CEh
                add     r5, r4           ; adresse linéaire = 0xE5CE + offset
                mov     r4, r5
                shr     r5, #14          ; bits 15:14 = numéro de page (16 Ko)
                shl     r5, #1
                mov     r5, [r5+#0FE00h] ; ← TABLE DE PAGES (64 entrées de 2 octets)
                bmov    r4.14, r5.0
                bmov    r4.15, r5.1      ; ← on réinjecte le sélecteur dans le handle
```

⇒ **C'est le modèle d'adressage que tu cherchais** : un handle de 16 bits =
**`[2 bits de sélecteur de page] [14 bits d'offset]`**. Le sélecteur n'est pas recopié du numéro de
page : il est **lu dans une table de 64 mots à `0x0FE00`**. Autrement dit, la correspondance
« page logique → page physique » est **paramétrée**, pas figée.

---

## 2. Anatomie du descripteur (12 octets) — le « Datensatz » de l'EEPROM

| position | contenu | preuve |
|---|---|---|
| **+0** (`0x0BA6`) | **offset du bloc** dans l'image (mot) | l. 149806-149810 |
| **+2** (`0x0BA8`) | **sous-offset** (mot), ajouté au précédent | l. 149812-149816 |
| +4, +9, +A | inconnu | — |
| **+6** (`0x0BAC`) | **drapeaux** (mot) : bit 1 testé, **bit 15 = `0x8000`** | l. 150992, 151013 |
| **+8** (`0x0BAE`) | **type** : `1` ou `4` | l. 149791 |
| **+B** (`0x0BB1`) | **masque de présence** (octet) | l. 150998-151003 |

*Le fait que `+8` et `+0B` tombent tous deux dans les 12 octets **re-confirme indépendamment** la
taille d'entrée trouvée à l'étape 30.*

---

## 3. ★ Le mécanisme de codage — la réponse à « la présence du régulateur, de la clim »

`sub_A09E4` (type 1), l. 150996-151007 :

```asm
                mov     r4, word_BBE
                movb    rl5, [r4+#0E5CEh]   ; ← l'OCTET DE CODAGE, à l'offset word_BBE
                movb    rl4, [r2+#0BB1h]    ; ← le MASQUE du descripteur
                andb    rl5, rl4
                jmpr    cc_NZ, loc_A0A36
                or      r14, #8000h          ; ← bit 15 : « champ NON DISPONIBLE »
```

**Traduction** : pour chaque bloc, on lit **un octet de l'image** (à l'offset `word_BBE`) et on le
teste avec **le masque propre au descripteur**. Si le bit est absent → le handle reçoit **`0x8000`**,
c'est-à-dire « équipement non codé / non présent ».

⇒ **Le codage des options est donc un octet de bits**, et chaque bloc sait **lequel de ses bits le
concerne**. Les appelants testent ce bit 15 pour décider. **C'est exactement le mécanisme que tu
supposais** — sauf que :
- l'**offset** de cet octet est `word_BBE`, une **variable RAM** — donc inconnu ;
- `word_BBE`, `word_BC0`, `word_BC4` sont **lus partout et écrits nulle part** dans la couche
  visible ⇒ fixés par la bibliothèque basse (voir §6).

**Conclusion honnête** : le mécanisme est **prouvé**, les valeurs sont **hors de portée**.

---

## 4. Les 20 appelants — la carte des utilisateurs de l'EEPROM

| ligne | commande | sortie | contexte / indice |
|---|---|---|---|
| 127438 | **0x0B** | locale | après `byte_C2EC & 1 → byte_F80C` |
| 127491 | **0x0C** | locale | après `word_1D90` → `unk_FD22.2` |
| 127544 | **0x0D** | locale | après `word_1D8E` → `unk_FD22.3` |
| 128443 | `[word_C186]` | locale | gardé par `byte_F80E == 3` |
| 129015 | **0x1D** | locale | `byte_C2EC → byte_C8F5` |
| **129029** | **0x21** | locale | mémorise un tampon à **`0xF81A`** |
| **129043** | **0x24** | locale | mémorise un tampon à **`0xF822`** |
| **129057** | **0x1E** | locale | mémorise un tampon à **`0xF82A`** |
| **129071** | **0x22** | locale | mémorise un tampon à **`0xF832`** |
| **129085** | **0x25** | locale | mémorise un tampon à **`0xF836`** |
| 129904 | `[word_C18A]` | locale | gardé par `byte_F83D == 3` |
| 152332 | `[word_C462]` | `0xCFA4` | |
| 152521 | `[word_C464]` | `0xCFA4` | |
| 152790 | `[word_C466]` | `0xCFA4` | |
| 152979 | `[word_C468]` | `0xCFA4` | |
| 183817 | **0x02** | `0xD9D8` | gardé par `word_C452` + `byte_D9DA` |
| 200240 | **0x03** | locale | construit un tampon de réponse |
| 206384 | **`(r4÷r5)+0x10`** | locale | commande **dynamique ≥ 0x10** |
| 208185 | **0x03** | locale | `loc_C1A1C`, zone diagnostic |
| 208283 | **0x03** | locale | écrit `0x74` puis appelle |

### ★ Le groupe 0x1E / 0x21 / 0x22 / 0x24 / 0x25

Cinq commandes, chacune précédée d'un `memcpy` (`unk_2128`) vers une **zone RAM contiguë**
`0xF80C → 0xF83D`, avec **un octet d'état avant chaque charge utile** :

```
0xF80C  état          0xF80E  état          0xF819  état
0xF81A  charge utile 8 octets (cmd 0x21)
0xF822  charge utile 8 octets (cmd 0x24)
0xF82A  charge utile 8 octets (cmd 0x1E)
0xF832  charge utile 4 octets (cmd 0x22)
0xF836  charge utile 8 octets (cmd 0x25)      0xF83D  état
```

**Cinq identifiants de ≤ 8 octets, chacun avec un octet d'état, chacun mémorisé par sa propre
commande.** Une charge utile de **8 octets** = exactement la forme « 4 caractères + 4 compléments »
du dossier externe. **C'est structurellement compatible avec les identifiants d'antidémarrage — mais
je ne peux pas le prouver** : ce qui est prouvé, c'est la structure (5 × 8 octets + états + 5
commandes dédiées), pas la nature des données.

---

## 5. Les deux types

| type | handler | rôle |
|---|---|---|
| **1** | `sub_A09E4` | lecture du descripteur, test de présence, **pas de checksum** |
| **4** | `sub_A0B72` | idem **+ checksum de quartets** sur `word_BC0` octets à partir de `word_BBE`, résultat `& 0x0F` |

⇒ **Le type d'un bloc dit s'il est protégé par un checksum.** Ce ne sont donc pas « des pages de
16 octets toutes protégées » (comme le dit le dossier externe), mais **des blocs à protection
optionnelle**, déclarée dans le descripteur.

---

## 6. Le compteur protégé `word_C70A` = `N | (0xFF−N)<<8`

`sub_C008A`, l. 151089-151105 (branche du service **0x04**) :

```asm
                mov     r12, #0C895h
                mov     r13, #0FFh
                mov     r14, #0Ah
                calls   0, unk_2144       ; memset(0xC895, 0xFF, 10)   ← effacement
                movb    byte_C89E, #1     ; ← octet d'ÉTAT = 1
                movbz   r9, byte_DC64
                add     r9, #1
                mov     r4, #0FFh
                sub     r4, r9            ; 0xFF − N
                shl     r4, #8
                or      r9, r4            ; r9 = N | ((0xFF − N) << 8)
                mov     word_C70A, r9
```

**Deux choses :**

1. Le motif « **valeur + son complément à `0xFF`** » décrit par ton dossier **existe réellement** —
   il est ici, dans `word_C70A`, et `word_C70A` est **précisément le mot mémorisé à l'offset +0 du
   groupe `word_C5A`** (étape 30). Le dossier visait juste sur le *principe*, sans le localiser.
2. **`byte_C89E` = l'octet d'état du bloc de 10 octets**, et le service le met à **1** (ou **2** dans
   la branche `loc_C012C`). ⇒ **Le bloc de 10 octets de l'étape 30 est bien un enregistrement
   d'état**, avec un octet d'état en position 9. C'est cohérent avec « virgin / appairé ».

---

## 7. La couche physique, précisément délimitée

| élément | adresse linéaire | dans le dump ? |
|---|---|---|
| `memcpy` (`unk_2128`) | **0x2128** | ✘ |
| `memset` (`unk_2144`) | **0x2144** | ✘ |
| table des 42 descripteurs | **0x0BA6** | ✘ |
| table des 64 pages (sélecteurs) | **0x0FE00** | ✘ |
| image EEPROM | **0xE5CE** | ✔ (RAM) |

`calls 0, unk_2128` ⇒ segment 0 ⇒ cible = **0x2128**, dans la région `0x00000-0x7FFF` **absente**.
Toute la mécanique EEPROM physique — pilote, catalogue d'offsets, power latch — est là.

---

## 8. Correction d'une affirmation de l'étape 30

J'avais écrit que la table `0x0BA6` était « indexée par `byte_CFA0` ». **Faux** : l'index est
**directement le numéro de commande** (`0x00…0x29`). La *taille* de 12 octets était en revanche
juste, et se trouve re-confirmée par `+8` et `+0B`.

---

## 9. Ce qui est maintenant établi, et ce qui reste

**Établi :**
1. un **point d'entrée unique**, **42 blocs**, descripteurs de 12 octets ;
2. **deux types** (avec / sans checksum) déclarés dans le descripteur ;
3. un **octet de codage d'options** testé par **masque**, produisant un bit « non disponible » ;
4. **handles = `[sélecteur de page][offset]`**, sélecteur lu dans une table ;
5. **5 identifiants de ≤ 8 octets** avec octets d'état, mémorisés par 5 commandes ;
6. le motif **`valeur + complément à 0xFF`** localisé (`word_C70A`) ;
7. la **table complète des services KWP2000** (0x04, 0x10, 0x11, 0x14, 0x17, 0x21, 0x27, 0x2C,
   0x30, 0x31, 0x32, 0x34, 0x3E, 0x81, 0x82, 0xA0).

**Reste hors de portée avec ce dump :** les **valeurs** (offsets, masques, type de chaque bloc) —
elles sont dans la table `0x0BA6`, absente. **Aucune invention possible.**

**Pistes suivantes :**
1. `sub_C141E` (**service 0x14, effacement des défauts**) : touche-t-il `sub_A0002` ? → persistance
   des DTC.
2. `sub_C163E` (**service 0x34**) : accès mémoire direct ? → lecture des zones non cartographiées.
3. Les 4 sites `0xCFA4` : comprendre la structure à quatre canaux.
4. `word_C452` / `byte_D9DA` autour de la commande **0x02** → lien avec le mode dégradé.
