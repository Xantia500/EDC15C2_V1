# ÉTAPE 49 — ★★★ Les `word_D6xx` sont des **compteurs de confirmation**, et les blocs sont validés

---

## 1. ★★★ Le mécanisme complet, décodé sur `word_D6EE` (l. 155393-155448)

**Ce n'est pas un seuil : c'est un comparateur à hystérésis avec temporisation.**

```asm
                mov     r12, word_18AC
                mov     r13, word_C5A8
                calls   0, unk_1D36              ; ← COURBE 1-D n°1 sur word_C5A8
                cmp     r4, word_C596            ; ← comparé à une référence
                jmpr    cc_SGE, loc_A3614        ; si supérieur-ou-égal → autre branche

                ; ---- branche « en dessous » ----
                movbz   r4, rl6
                and     r4, #2                   ; ← bit 1 de rl6 = ÉTAT courant
                jmpr    cc_Z, loc_A35FA
                mov     word_D6EE, ZEROS         ; état déjà posé → compteur à zéro
                jmpr    cc_UC, loc_A364C
loc_A35FA:
                mov     r4, word_1474
                mov     r5, [r4]                 ; = 360
                cmp     r5, word_D6EE
                jmpr    cc_C, loc_A360C          ; 360 < compteur → on bascule
                sub     word_D6EE, ONES          ; sinon DÉCRÉMENTE
                jmpr    cc_UC, loc_A364C
loc_A360C:
                orb     rl6, #2                  ; ★ POSE le bit d'état
                mov     word_D6EE, ZEROS         ; et remet le compteur à zéro
```

et symétriquement (l. 155411-155449) :

```asm
loc_A3614:
                mov     r12, word_18AA
                mov     r13, word_C5A8
                calls   0, unk_1D36              ; ← COURBE 1-D n°2, même entrée
                cmp     r4, word_C596
                jmpr    cc_SLE, loc_A364C
                ...
loc_A3644:
                andb    rl6, #0FDh               ; ★ EFFACE le bit d'état
                mov     word_D6EE, ZEROS
```

### Décodage

| élément | rôle |
|---|---|
| **`word_18AA`, `word_18AC`** | **deux courbes 1-D** appliquées à **la même entrée** `word_C5A8` ⇒ **les deux bornes d'une fenêtre** |
| **`word_C596`** | référence comparée au résultat de la courbe |
| **`unk_1D36`** | **l'interpolateur de courbe 1-D** — son usage ici confirme définitivement ce que l'étape 25 avait seulement supposé |
| **`word_D6EE`** | **compteur de confirmation** : part de 0, **décrémenté** à chaque cycle où la condition tient |
| **`[word_1474 + n]`** | **nombre de cycles à parcourir** — c'est une **DURÉE**, pas un seuil physique |
| **`rl6` bit 1** | **l'état** (posé / effacé) |
| `word_D6EE` remis à 0 | **à chaque bascule et à chaque cycle non conforme** ⇒ pas d'accumulation, il faut N cycles **consécutifs** |

**⇒ C'est un anti-rebond à hystérésis sur une comparaison de courbe, avec un nombre de cycles
configurable.**

---

## 2. ★★ ERratum à l'étape 48 §5 — et conséquence sur `word_C5B8`

J'ai écrit : « `word_1474` est un bloc de **seuils indépendants** ». **C'est faux.** Ce sont des
**durées de confirmation**, exprimées en **cycles de tâche** :

| offset | valeur | nature |
|---|---|---|
| `+0x00` | **360** | 360 cycles de confirmation pour l'état 0 |
| `+0x02` | 60 | 60 cycles, état 1 |
| `+0x04` | 60 | 60 cycles, partagé par **4** états |
| `+0x06` | 325 | 325 cycles |
| `+0x1A` | **250** | 250 cycles |

**Conséquence en chaîne, que je dois signaler contre mes propres conclusions :**

- l'étape 46 §2 voyait dans le **250** un défaut « copie d'une valeur de calibration » : c'est
  cohérent, mais **250 est une durée**, pas un plafond physique ;
- l'étape 47 §3 supposait que 250 pouvait être la **Vmax** : **cette piste s'affaiblit fortement** ;
- l'étape 47 §4 concluait que `word_C5B8` était une « petite grandeur physique » comparée à 2 et 120 :
  comme **120 et 325 sont désormais des durées**, `word_C5B8` est **probablement un compteur lui
  aussi**, et non une grandeur mesurée. **Je retire la qualification « grandeur physique ».**

**Ce qui reste, et qui est solide :** `word_C5B8` est **persisté en EEPROM**, **historisé sur 5
valeurs**, **moyenné**, et comparé à des durées. C'est un **compteur persistant**, pas une mesure
instantanée. La question « que compte-t-il » reste ouverte.

**Et `word_D6FA`** est chargé avec `[word_1474+0x1A] = 250` puis décrémenté (l. 156042-156056) :
**confirmation directe** que la valeur est un **compteur de départ**, pas une limite.

---

## 3. Action 3 — le motif `02 01 00 08 0F` n'existe que **deux fois**, et c'est une bonne nouvelle

Recherche du motif complet dans les 512 Ko :

| offset fichier | EA | handle |
|---|---|---|
| `0x64962` | `0xE4962` | **`word_1818`** |
| `0x74962` | `0xF4962` | **aucun** |

**⇒ Présent à l'identique dans les deux versions du Datensatz (`0xE0000` et `0xF0000`), et une seule
fois dans chacune.**

Trois conclusions :

1. **Il n'existe pas de second handle portant une table de bits de niveaux** : le mécanisme est
   **unique** dans ce calculateur — 5 niveaux, pas plus.
2. **La version `0xF0000` partage cette table à l'identique** : cohérent avec les **14 octets d'écart**
   relevés à l'étape 38 — l'écart est **ailleurs**.
3. La sixième entrée potentielle (l'octet `0xC3` qui suit) est **du remplissage** : aucune autre
   occurrence du motif ne permet d'imaginer une variante à 6 niveaux.

---

## 4. Action 4 — ★ la zone `0xE6306-0xE648C` est un **tableau régulier**, et `word_1952` le confirme

Douze handles **consécutifs** délimitent douze blocs contigus :

| handle | début | taille |
|---|---|---|
| `word_1946` | `0xE6306` | 32 o |
| `word_1948` | `0xE6326` | 32 o |
| `word_194A` | `0xE6346` | 28 o |
| `word_194C` | `0xE6362` | 28 o |
| `word_194E` | `0xE637E` | 28 o |
| `word_1950` | `0xE639A` | 36 o |
| **`word_1952`** | `0xE63BE` | **62 o** ← l'anomalie |
| `word_1954` | `0xE63FC` | 28 o |
| `word_1956` | `0xE6418` | 28 o |
| `word_1958` | `0xE6434` | 32 o |
| `word_195A` | `0xE6454` | 28 o |
| `word_195C` | `0xE6470` | 28 o |

**Le motif est net : 28 ou 32 octets, sauf `word_1952` à 62 — soit ≈ 2 × 28/32.**

### J'ai formé l'hypothèse « pointeur manquant », et le code la **réfute**

Si `word_1952` valait deux blocs accolés, le code ne devrait pas dépasser `+0x1C`. **Or les offsets
réellement lus, relevés sur les 25 sites (l. 166370-166813), vont jusqu'à `+0x3C` :**

```
+0x3Bh ×2   +0x3Ch ×1   +0x34h ×2   +0x30h ×2
+0x2Ch ×2   +0x2Ah ×3   +0x24h ×4   +0x1Ah ×3   +0x10h ×2
```

**`+0x3C = 60 < 62` : les 62 octets sont pleinement utilisés.**

⇒ **`word_1952` est bien UN bloc**, volontairement plus grand que ses voisins. **Hypothèse
« pointeur manquant » retirée.**

### Ce que cette action valide — et c'est le plus important

**Les bornes de blocs calculées depuis la table des pointeurs sont exactes** : la taille déduite
(62 o) encadre **exactement** le plus grand offset lu (60). C'est la **quatrième** validation
indépendante de la méthode de l'étape 48 §1.

⇒ **Un handle = un conteneur de paramètres**, de taille connue, lu à des offsets arbitraires par un
sous-programme. Le modèle « identité + type + tag » se précise : **la « taille » fait partie de
l'identité**, et elle est **calculable**.

---

## 5. Bilan des quatre actions

| action | verdict |
|---|---|
| 1. `word_D6EE…D6FA` | **★ Fermé** : compteurs de confirmation (hystérésis + N cycles) ; `unk_1D36` = interpolateur 1-D confirmé |
| 2. `byte_D6FC` | bits d'état ; **bit 0** et **bit 1** identifiés (`rl6` porte les mêmes) |
| 3. table de 5 niveaux | **unique**, identique dans les deux versions du Datensatz |
| 4. zone `0xE63xx` | **tableau régulier 28/32 o** ; `word_1952` = conteneur de 62 o **réellement utilisé** ; méthode des bornes **validée** |

**Trois de mes affirmations tombent** (§2 : « seuils » ; étape 47 §3 : piste Vmax 250 ; étape 47 §4 :
« grandeur physique »). **Un mécanisme entier est acquis** (§1). **Une méthode est validée** (§4).

---

## 6. Prochaines actions

1. **`word_C5A8`** : l'entrée des deux courbes. C'est **la** grandeur surveillée par ce comparateur à
   hystérésis — et donc un candidat de premier ordre pour être **la pression de suralimentation** ou
   **le débit d'air** (tes deux grandeurs de référence).
2. **`word_C596`** : la référence comparée — une valeur fixe ou calculée ?
3. **`word_18AA` / `word_18AC`** : les deux courbes de la fenêtre. **Lire leurs valeurs** avec l'outil
   de l'étape 47 — une fenêtre en mg/s ou en mbar **identifierait la grandeur**.
4. **`byte_D6FC`** : les 6 autres bits, non encore attribués.
