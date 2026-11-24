# ÉTAPE 62 — `0x6111E` : le bloc d'options de 42 octets

> Ta question : **qui lit `0x6111F` (`0x6111E`), qu'est-ce qui est fait, quelle zone est touchée ?**
> Réponse complète. Et au passage : ce bloc est le **voisin immédiat** de la grosse structure
> d'options `0xE1148` dont on parlait à l'étape 61 — ils forment une seule zone.

---

## 1. Résolution de l'adresse (chaîne complète, vérifiable)

| étape | valeur | preuve |
|---|---|---|
| offset fichier | `0x6111E` (et `0x6111F` = son octet `+1`) | `edc.bin` : `00 01 01 00 00 01 00 01 00 01 30 00 …` |
| Datensatz = fichier `0x60000` | ⇒ **EA `0xE111E`** | règle `EA = offset + 0x80000` sur la copie `0xE…` |
| entrée de pointeur | **n° 14** de la table `fichier 0x61400` = EA `0xE1400` | `0x6141C` contient `1e 11` = `0x111E` (recherche exhaustive : **2 occurrences**, `0x6141C` et `0x7141C` = les deux copies) |
| handle | **`0x141C`** | `handle = 0x1400 + 2 × index` |
| symbole code | **`word_141C`** (RAM `EXT_MEM`, `clean.asm` l.5162) | `word_141C: ds 2` ; vaut donc `0x111E`, résolu par DPP page `0x38` |

**Bornes du bloc — preuve arithmétique, pas une estimation :**

- pointeur précédent : `word_141A = 0x1112` → EA `0xE1112`
- **ce bloc : `word_141C = 0x111E` → EA `0xE111E`**
- pointeur suivant : `word_141E = 0x1148` → EA `0xE1148`
- or **`0xE111E + 42 = 0xE1148`** ⇒ le bloc fait **exactement 42 octets**.

**Correction au passage** : le bloc `0xE1148` ne fait pas 60 octets mais **52** (`0xE1148 → 0xE117C`,
pointeur `word_1420 = 0x117C`). Le « 60 » de l'étape 60 était un décompte de sites, pas une taille.

---

## 2. Ce que c'est : un bloc de paramètres, **pas une carte**

Aucun tag, aucun `n`, aucune valeur d'axe. C'est exactement le cas « map sans en-tête » : ici, ce n'est
même pas une map, c'est une **table d'octets d'option**.

```
  +00  00 01 01 00 00 01 00 01 00 01 30 00 00 01
  +14  08 00 01 00 00 00 00 01 0a 02 02 03 02 01
  +28  01 00 01 01 00 00 00 00 00 01 00 01 02 c3
```

Presque tout est `0x00`/`0x01` — mais **pas tout**, et c'est important :

| offset | valeur | offset | valeur |
|---|---|---|---|
| `+0x0A` | **`0x30`** (= 48) | `+0x19` | **`0x03`** |
| `+0x0E` | **`0x08`** | `+0x1A` | **`0x02`** |
| `+0x16` | **`0x0A`** (10) | `+0x27` | `0x01` |
| `+0x17` | **`0x02`** | `+0x28` | **`0x02`** |
| `+0x18` | **`0x02`** | | |

`+0x0A = 0x30`, `+0x16 = 0x0A`, `+0x19 = 0x03` **ne sont pas des booléens** : ce sont des **données**
(indice, seuil, compteur). Même leçon qu'à l'étape 61 : octet de calibration ≠ interrupteur.

---

## 3. Qui lit : **9 sites, aucun autre dans tout le listing**

`word_141C` apparaît **9 fois** dans `clean.asm` — et jamais comme destination. Trois comportements
distincts, pas un seul.

### 3.1 Trois recopies en RAM (31 octets)

| site | fonction réelle | octets recopiés | destinations RAM |
|---|---|---|---|
| `l.151755` `loc_A11BA` | bloc non nommé (seg014) | **10** | `C2B1 C2B2 C2B0 C2C5 C2C9 C2B3 C2B9 C2BB C2B4 C2BA` |
| `l.199982` `loc_BD7D6` | `sub_BD464` | **20** | `C2BF C2CC C2C7 C2B8 C2C3 C2B7 C2C0 C2D0 C2D1 C2CE C2CF C2CB C2CD C2C8 C2BE C2C6 C2CA C2BD C2C4 C2C1` |
| `l.200395` | bloc non nommé (seg015) | **1** | `C2B6` (= `+0x10`), puis **teste** `+0x11` |

Chaque octet de calibration a donc **son** octet RAM nommé, et **c'est ce nom-là** qui sert ensuite
partout dans le code. **Consommation totale des miroirs : ≈ 341 références.** Le plus utilisé est
`byte_C2BA` (`+0x27`) avec **63 références**.

### 3.2 Cinq tests directs (5 octets)

| site | octet | test |
|---|---|---|
| `l.196409` | `+0x0B` | `jmpr cc_NZ` (**deux** fois, deux branches) |
| `l.196438` | `+0x0B` | idem |
| `l.196446` | `+0x0C` | `jmpr cc_NZ` |
| `l.195999` | `+0x0D` | `cmpb rl5, #1` |
| `l.200413` | `+0x11` | `cmpb rl5, #1` |

### 3.3 Inventaire : 35 octets lus sur 42

**Jamais lus** : `+0x00`, `+0x05`, `+0x07`, `+0x12`, `+0x13`, `+0x14`, `+0x29`.
Sept octets réservés / inutilisés dans cette version du firmware — intéressant en soi : des emplacements
prévus par le constructeur et laissés vides.

---

## 4. ★ Ce que ces octets FONT

### `+0x0B` = `0x00` — annulation de la consigne

```asm
movb rl4, [r3+#0Bh]
jmpr cc_NZ, loc_BB548        ; NON NUL -> word_DB64 = 0 ET word_DB66 = 0
mov  r4, word_1468
mov  r1, [r4]
and  r1, #800h
jmpr cc_Z, loc_BB542         ; bit 0x800 absent -> word_DB66 = [r0] (valeur interpolée)
mov  r1, [r4]
and  r1, #200h
jmpr cc_NZ, loc_BB542
mov  r1, word_C506           ; bit 0x800 présent et bit 0x200 absent -> constante calibrée
mov  word_DB66, r1
```

**Trois sources possibles pour la même consigne** : zéro (désactivé), la carte interpolée, ou une
**constante de calibration** `word_C506` choisie par un état logé dans `[word_1468]`. C'est un
**mécanisme de repli** (valeur de secours calibrée), pas un simple oui/non.

### `+0x0C` = `0x00` — ★ **il choisit la structure du régulateur**

```asm
movb rl5, [r4+#0Ch]
jmpr cc_NZ, loc_BB5A6        ; NON NUL -> régulateur par unk_2020
                             ; NUL     -> régulateur par unk_1FE8
```

C'est le switch le plus important du bloc : **deux implantations différentes de la même régulation**,
sélectionnées en calibration. Voir § 5.

### `+0x0D` = `0x01` — code d'état

```asm
movb rl5, [r4+#0Dh]
cmpb rl5, #1
jmpr cc_NZ, loc_BB0FA        ; != 1 -> byte_DB73 = 4
movb rl4, #5
movb byte_DB73, rl4          ; == 1 -> byte_DB73 = 5
```

`byte_DB73` est l'**index d'état** d'une machine à 14 états (voir § 6).

### `+0x10` / `+0x11` — ★ un **verrou à mémoire**

```asm
movb rl4, byte_C2B6
movb byte_C8EB, rl4          ; C8EB := C2B6   (restauration)
movbz r4, rl4
movbz r5, byte_C2B5
add  r4, r5
cmp  r4, #1
jmpr cc_NZ, loc_BDBCA        ; (C2B6 + C2B5) != 1 -> on ne touche à rien
movb rl5, [r4+#11h]
cmpb rl5, #1
jmpr cc_NZ, loc_BDBB8        ; +0x11 != 1 -> C8EB = 0, C2B5 = 1
movb byte_C8EB, #1 ; movb byte_C2B5, ZEROS
```

Ce n'est pas un interrupteur, c'est **une bascule avec état mémorisé** : la paire `C2B6`/`C2B5` doit
valoir « exactement un des deux à 1 » pour que l'octet de calibration soit réévalué, et l'octet `+0x11`
**force le sens** de la bascule. Autrement dit : *l'octet décide, et le couple de variables se souvient
que la décision a déjà eu lieu.* Exactement le genre de logique que « switch » ne décrit pas.

### `+0x0E` = `0x08` — deux identifiants de diagnostic

```asm
movbz r4, byte_C2B7
and   r4, #1
jmpr  cc_Z, loc_9A95A        ; bit 0 seul compte -> les autres bits de 0x08 = 0
mov   r12, #9     ; mov r13, #349h   ; mov r14, #0 ; mov r15, #7
calls 9, sub_9CF70
mov   r12, #0Dh   ; mov r13, #389h   ; mov r14, #0 ; mov r15, #5
calls 9, sub_9CF70
```

Le `0x08` **n'est pas** un booléen : seul son **bit 0** est testé. Deux requêtes diagnostiques
(`9 / 0x349`) et (`0x0D / 0x389`) sont enregistrées ou non.

### `+0x02` et `+0x27` — corrections liées au régime / état

- `+0x02` → `byte_C2C5` : si nul, tout un étage de calcul est sauté ; sinon
  `word_C91C = word_C42E` (axe **régime**), différence `word_C6D8 − word_D84C`, appel `word_1DA8`,
  puis division par `0x2710` (échelle ×10000). **Correction de consigne en fonction du régime.**
- `+0x27` → `byte_C2BA` (63 références) : pilote un indicateur d'état (`USR0`, `word_FD82.3/.5`).
  C'est le seul octet du bloc utilisé à cette échelle : **à traiter à part** dans la prochaine étape.

---

## 5. ★★ Le régulateur : `unk_2020` (PI) avec saturation et butées

Les deux branches de `+0x0C` :

```asm
loc_BB5A6:                          ; +0x0C NON NUL
                mov  r12, #0DBAEh
                mov  r13, #0DBA4h
                mov  r14, r7
                mov  r15, #0DB6Ah
                calls 0, unk_2020
loc_BB5D6:
                mov  word_D4B2, word_DB68      ; sortie 1
                mov  word_D4B0, word_DB66      ; sortie 2
                mov  r12, #0DB98h
                mov  r13, #0DB96h
                mov  r14, word_DB6A
                mov  r15, #0DB70h
                calls 0, unk_1EBC
                mov  word_D4AE, word_DB6E
                mov  word_DB70, word_DB6A
                mov  word_D48E, word_DB6A
                add  r2, word_DB6E            ; ★ somme = intégrateur
                jnb  V, loc_BB638
                jnb  N, loc_BB632
                mov  r3, #7FFFh                ; ★ saturation positive
                mov  r4, #8000h                ; ★ saturation négative
loc_BB638:
                cmp  r5, [r7]                 ; ★ butée basse
                jmpr cc_SLE, loc_BB642
                mov  [r0], [r7]
                cmp  r5, [r7+#2]              ; ★ butée haute
```

**C'est bien un PI(D) :** somme accumulée du terme précédent (`word_D48E`, `word_DB70`) et du terme
courant (`word_DB6E`), avec **saturation `0x7FFF`/`0x8000`** et **butées min/max aux adresses
`[r7]`/`[r7+2]`** = anti-emballement classique.

Le second site (`l.173370`, seg014) confirme la signature : **6 arguments dont deux pointeurs de
structure** (`#0D860h`, `#0D85Ch`), une entrée (`word_C610`), un retour dans `r4` → `word_C936`.

**Nouvelle famille « couche absente » (corps `ds 1`, couche non désassemblée) :**

| routine | appels | rôle observé |
|---|---|---|
| **`unk_2020`** | **2** | régulateur principal (arguments = 2 structures + entrée + sortie) |
| `unk_1FE8` | **8** | variante appelée par `+0x0C = 0` |
| `unk_1EBC` | **2** | étage de lissage sur `DB6A/DB6C/DB6E` |
| `word_1DA8` | **14** | appelé avec `r13 = #2710h` (échelle ×10000) |

**Bilan de la chasse au PID** : ce n'est pas un PID unique mais **une famille de régulateurs
paramétrés**, choisis par octet de calibration. Le `P`/`I` reste dans la couche absente — mais la
**structure** (états, saturation, butées, échelle) est maintenant connue.

---

## 6. ★ La zone touchée : une machine à états de supervision à 14 états

`byte_DB73` est écrit par **~30 sites**, puis :

```asm
movb  rl4, byte_C35C
cmpb  rl4, #1
jmpr  cc_Z, loc_BAEC8
cmpb  rl4, #3
jmpa  cc_Z, loc_BB65E              ; famille d'états n° 3
jmpa  cc_UC, loc_BBAF6             ; autre famille
loc_BAEC8:
                movb  rl4, byte_DB73
                cmpb  rl4, #0Dh
                jmpa  cc_UGT, loc_BB496
                movbz r4, rl4
                shl   r4, #1
                add   r4, #0AE6h           ; ★ table de saut
                mov   r4, [r4]
                jmpi  cc_UC, [r4]
```

**Table de saut à EA `0xE0AE6`** — 14 entrées, offsets 16 bits dans le segment 015 :

`0xAEE0  0xAFB0  0xB03C  0xB0D4  0xB16A  0xB134  0xB1E2  0xB22C  0xB25C  0xB27E  0xB1A2  0xB08C  0xB2D6  0xB3D8`

Avec `byte_C35C` (1 / 3 / autre) en amont : **deux niveaux** de sélection avant d'atteindre l'état.

---

## 7. ★★ Découverte de structure : `0xE0000–0xE1000` **n'est pas de la calibration**

En cherchant cette table de saut je suis tombé sur quelque chose d'important : les tables de saut de la
couche code ne sont pas dans le code, elles sont **au début du Datensatz**. Sept bases recensées :

`0xE0966` · `0xE0970` · `0xE098E` · `0xE09C6` · `0xE09DC` · `0xE0A62` · **`0xE0AE6`**

Motif constant : `movbz rN, rlN ; shl rN, #1 ; add rN, #0XXXh ; mov rN, [rN] ; jmpi cc_UC, [rN]`.
Contenu = **offsets de segment** (ex. `0xE0966` → `0x95C6 0x95E0 0x965A 0x96A4 0x96EE 0xCB56 0xCB7E …`).

**Conséquence sur le décompte de couverture** : les affirmations « 97,9 % de `0xE1000–0xEC000` » ne
disent rien de `0xE0000–0xE1000`, qui contient du **pilotage de code par table** — à inventorier
séparément. À ne pas confondre avec de la donnée moteur.

⚠ Piège confirmé : `add rN, #0AE6h` **n'est pas** l'adresse `0x0AE6` (RAM) — c'est `DPP 0x38 × 0x4000
+ 0xAE6 = EA 0xE0AE6`. Le piège de pagination déjà vu (`#0E5CEh ≠ 0xE25CE`).

---

## 8. Synthèse : quelle zone, en une phrase

> **`0xE111E` (42 octets) est le bloc d'options « supervision » du calculateur.** Il ne contient aucune
> donnée moteur : il contient des **choix**, recopiés dans 31 variables `byte_C2Bx`, qui décident
> *quelle* stratégie s'applique — quelle source de consigne d'air, **quel implant de régulateur PI**,
> quel code d'état, quels identifiants de diagnostic répondent. Il est lu **uniquement** par le segment
> CAN/diagnostic et le segment de supervision, mais il agit **partout** via ses miroirs (≈ 341 références).

---

## 9. Consignation

- **`CATALOGUE_MAITRE.md` : § 13 B.8** ajouté (1 900 → **1 985 lignes**).
- **`bloc_options_0xE111E.csv`** : les 35 octets lus, avec site, miroir RAM et nombre de références.

## 10. Ce qui reste ouvert sur ce bloc

1. **`byte_C2BA` (`+0x27`, 63 réf.)** : le seul octet à fort rayonnement ; il faut le suivre jusqu'à sa sortie.
2. **Les 7 octets jamais lus** (`+0, +5, +7, +0x12–0x14, +0x29`) : réservés ? variantes d'autres marchés ?
3. **`+0x0A = 0x30`** : valeur non booléenne dont je n'ai pas encore trouvé le consommateur réel
   (`byte_C2C9`, 9 références — à décoder).
4. **Le corps de `unk_2020`** : la couche `ds 1` n'est pas désassemblée ; les gains restent invisibles.
