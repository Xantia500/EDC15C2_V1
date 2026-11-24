# ÉTAPE 65 — Zone `0xE1129` → `0xE11DD` (+180 octets) : inventaire complet

> **Correction acceptée d'abord** : `0xE111E` est un **mot**, et l'octet utile est bien **`0xE111F`**
> (`+0x01`). Et celui-là **est lu** : 5 fois. Mes réserves portaient sur `+0x00`, qui est effectivement
> mort — mais il ne faut pas confondre les deux. Détail au § 1.
>
> Ensuite : la zone que tu signales est **effectivement riche**, mais pas là où tu l'attends. Verdict
> franc au § 5.

---

## 1. `0xE111F` = `+0x01` → `byte_C2B1` : **5 lectures**, et un rôle d'interrupteur maître

| site | EA | segment | ce qui est fait |
|---|---|---|---|
| `l.132972` | `0x9800C` | **s13** | `cmpb #1` → si `1`, va lire `word_141E+0x06` et le compare à `2` : **deux conditions enchaînées** |
| `l.133051` | `0x9811x` | **s13** | si `1` : `word_C91C = word_C42E` (axe **régime**) puis lit `word_143A` → **tout un calcul** ; sinon saute à `loc_98984` |
| `l.133879` | `loc_98984` | **s13** | si `1` et `word_CDEA ≠ 0` → `rl4 = 1` (recopie d'état) |
| `l.134610` | `loc_98F70` | **s13** | si `1` → `r4 = 1` (drapeau) |
| `l.219067` | `0xC8400` | **s16** | si `≠ 1` → **`or r7, #80h`** : positionne le **bit 7** d'un octet de statut |

**Lecture** : `0xE111F = 0x01` n'est pas une simple option — c'est un **interrupteur maître** qui
**ouvre ou ferme un chemin de calcul entier dans le segment d'injection** (4 sites) et positionne un
**bit de statut** dans le segment de communication. C'est très cohérent avec « désactive la fonction
principale ». **Ta correction est la bonne** : l'octet qui compte est `0xE111F`, pas `0xE111E`.

---

## 2. Inventaire de la zone — 12 blocs, bornes données par les pointeurs

Les bornes ne sont pas devinées : chaque bloc va du pointeur courant au pointeur suivant.

| handle | EA | taille | contenu | symbole lu dans le code ? | lectures |
|---|---|---|---|---|---|
| `0x141C` | `0xE111E` | 42 o | bloc d'options (étape 62) | `word_141C` | 9 |
| `0x1F8A` | `0xE1127` | 4 o | `30 01 00 00` | **jamais** | 0 |
| `0x232E` | `0xE112B` | 11 o | `01 08 00 01 00 00 00 00 01 0A` +1 | **jamais** | 0 |
| `0x1F0A` | `0xE1136` | 4 o | `02 03 02 01` | **jamais** | 0 |
| `0x23F4` | `0xE113A` | 14 o | `01 00 01 01 00 00 00 00 00 01 00 01 02 C3` | **jamais** | 0 |
| **`0x141E`** (+ alias `0x2148`) | **`0xE1148`** | **52 o** | **bloc d'options** (voir § 3) | `word_141E` | **97** |
| `0x1420` | `0xE117C` | 24 o | **12 × `0xFFFF`** | `word_1420` | 2 (pointeur) |
| `0x1E76` | `0xE1194` | 12 o | **6 × `0xFFFF`** | **jamais** | 0 |
| `0x1422` | `0xE11A0` | 23 o | zéros | `word_1422` | 2 (pointeur) |
| `0x1FE6` | `0xE11B7` | 11 o | zéros | **jamais** | 0 |
| `0x1FC8` | `0xE11C2` | 2 o | `0x0000` | **jamais** | 0 |
| `0x1424` | `0xE11C4` | 40 o | **20 valeurs 16 bits** | `word_1424` | 4 (pointeur) |

### Dump brut de la zone

```
0xE1129 (+  0) : 00 00 01 08 00 01 00 00 00 00 01 0A 02 02 03 02
0xE1139 (+ 16) : 01 01 00 01 01 00 00 00 00 00 01 00 01 02 C3 00
0xE1149 (+ 32) : 00 00 08 04 01 01 00 00 04 00 02 00 00 00 02 00
0xE1159 (+ 48) : 05 00 05 04 84 BE CA 64 00 01 01 01 00 01 96 00
0xE1169 (+ 64) : 00 01 01 01 02 02 00 00 00 02 00 00 00 00 00 01
0xE1179 (+ 80) : 01 00 00 FF FF FF FF FF FF FF FF FF FF FF FF FF
0xE1189 (+ 96) : FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF
0xE1199 (+112) : FF FF FF FF FF FF FF 00 00 00 00 00 00 00 00 00
0xE11A9 (+128) : 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0xE11B9 (+144) : 00 00 00 00 00 00 00 00 00 00 00 10 0F 61 0F 80
0xE11C9 (+160) : 0F FA 0F 8B 0F 30 0F 32 0F 60 0F FC 0F 40 0F 42
0xE11D9 (+176) : 0F 5A 1F 51 1F 64 0F 7F 0F
```

Trois natures bien distinctes :
1. **octets d'options** (`0xE111E`, `0xE1148`) — valeurs 0/1/2/3/4 ;
2. **plages `0xFFFF`** (`0xE117C`, `0xE1194`) — la sentinelle « pas de valeur » : **12 + 6 mots vides** ;
3. **table de 20 valeurs 16 bits** (`0xE11C4`).

**8 handles sur 12 n'ont aucun symbole dans le code** (`0x1F8A`, `0x232E`, `0x1F0A`, `0x23F4`, `0x2148`,
`0x1E76`, `0x1FE6`, `0x1FC8`). `0x2148` est de plus un **alias exact de `0x141E`** (même cible `0xE1148`).
Les autres pointent **à l'intérieur** d'autres blocs : ce sont des **sous-pointeurs** jamais consommés
par nom — soit vestigiaux, soit réservés à un service qui passe par la table et non par le symbole.

---

## 3. Le bloc réellement riche : `0xE1148`, **97 lectures** dans les 5 segments

C'est **lui** qui porte la richesse de la zone. Offsets réellement lus et leur effet :

| offset | sites | segments | effet mesuré |
|---|---|---|---|
| **`+0x0A`** | **16** | s15 | ★ **sélecteur d'échelle** : `cmpb #1` → `r8 = 0` si égal, sinon **`r8 = 0x2710` (10 000)**. Valeur ici `0x30` ≠ 1 ⇒ échelle 10 000 |
| **`+0x14`** | 6 | s13, s14, s15, s16 | **sélecteur à 4 états** : `#2`, `#3`, `#4` → même cible `loc_BF096` ; sinon calcul `r5 = 0x0F − r4` |
| **`+0x09`** | 8 | s13, s14, s16 | sélecteur type (`#4`, `#2`, `#1`) |
| **`+0x06`** | 4 | s13, s16 | sélecteur type (`#4`, `#2`) |
| **`+0x0C`** | 5 | s14 | variante : 5 sauts conditionnels |
| `+0x33` (=51) | 5 | s13, s15 | drapeau de fin de bloc (dernier octet du bloc de 52) |
| `+0x0D`, `+0x19`, `+0x1B`, `+0x21`…`+0x26`, `+0x2A`, `+0x2E`, `+0x2F`…`+0x32` | 1 à 3 chacun | s13→s17 | options de variante |
| `+0x01`, `+0x02` | 4 + 4 | s15 | sélecteurs (états 0/1/2) |
| `+0x1C`…`+0x2D` | 6 | **s17** | options de la couche tâches/CAN |

**Signature de `+0x0A`** (16 fois le même motif, ex. `l.196065` → `0x9E1A`) :

```asm
mov  r4, word_141E
movb rl5, [r4+#0Ah]
cmpb rl5, #1
jmpr cc_NZ, loc_B9E2C
mov  r8, #0            ; octet == 1  -> échelle 0
loc_B9E2C:
mov  r8, #2710h        ; sinon       -> échelle 10 000
```

⇒ ce n'est pas un interrupteur oui/non : c'est un **choix d'unité/échelle (0 ou 10 000)** appliqué à
**16 endroits** du segment de supervision. Le `0x30` de notre fichier ne vaut pas 1 ⇒ **échelle 10 000**
partout.

---

## 4. ★ La zone contient bien du **diagnostic** — mais sous forme de tables, pas de seuils FAP

Trois blocs sont consommés comme **pointeurs de table** :

### 4.1 `sub_BE2BA` — construction de réponse diagnostic

```asm
movb rl6, [r5+#1]                 ; identifiant demandé (octet)
cmpb rl6, #0 / #20h / #40h / #60h / #80h / #A0h / #C0h / #E0h   ; groupes de 32
...
movb rl4, #42h                    ; 0x42 = réponse de service diagnostic
```

et pour les autres identifiants :

```asm
mov r8, word_1424                 ; table de 20 valeurs
loc_BE49E:
  mov   r4, [r8]
  movbz r5, rl6
  cmp   r4, r5                    ; recherche
loc_BE4CE:                        ; marqueur 0xFF
  mov   r5, word_1420             ; -> table 0xE117C (0xFFFF partout)
  add   r5, PID*2 ;  mov [r0], [r5]
loc_BE4C4:                        ; marqueur 0xFE
  mov   r5, word_1422             ; -> table 0xE11A0 (zéros partout)
```
Le marqueur vient de **RAM `0xDC2C + index`**.

### 4.2 `sub_BEF66` — scan de la même table avec un **masque de bits**

```asm
movb rl4, [r0+#12h] ; movbz r4, rl4 ; movbz r5, rl6
and  r4, r5                        ; ★ test de masque
jmpr cc_Z, loc_BF030
mov  r9, #0
mov  r4, word_1424                 ; 0xE11C4
loc_BEFE4:
  mov  r4, [r0] ; add r4, #2 ; r9 += 1
  cmpb rl4, #14h                   ; ★ 20 entrées
```

### 4.3 `loc_CF1F0` (seg016) — recopie **convertie** des 20 valeurs en RAM

```asm
mov r8, #0CC54h
mov r7, word_1424
loc_CF200:
  mov    r1, [r7+]                 ; lit un mot de 0xE11C4
  calls  0Ch, sub_CFEFA            ; conversion
  mov    [r8], r4                  ; stocke un dword
  add    r8, #4
  cmp    r8, #0CCA4h               ; (0xCCA4-0xCC54)/4 = 20 entrées
  jmpr   cc_C, loc_CF200
```

**Conclusion sur `0xE11C4` : table de 20 valeurs 16 bits**, indexée par **position/bit**, recopiée en
RAM `0xCC54+4i` après conversion. **Ce ne sont pas des identifiants de PID** (leurs valeurs dépassent 8
bits) — c'est pour cela que je corrige l'hypothèse « table d'ID » que le premier coup d'œil suggérait.

Et juste après, `loc_CF216` parcourt **96 entrées** (`cmp r3, #60h`) à partir de `0xCCB2` avec
`movb rh2, [r0+#1Ch]` : c'est la **table des défauts** (RAM `0xCCB2`, 96 entrées) — cohérent avec les
« défauts `0xCAD0` / `0xCCB2` » déjà consignés.

---

## 5. Tes hypothèses FAP : verdict honnête

| hypothèse | présence dans `0xE1129` → `0xE11DD` | preuve |
|---|---|---|
| **post-injection** | non (aucun seuil, aucun angle, aucune quantité) | les seules valeurs non binaires sont `0x30`, `0x0A`, `0x03`, et 20 mots `0x0Fxx` |
| **DPF / FAP (suie, km, dP)** | **non** | aucune valeur de masse (g), de pression (hPa) ni de kilométrage cohérente |
| **DTC** | **oui, mais indirectement** | mécanique de réponse diag (`sub_BE2BA`, `0x42+PID`) + table de défauts 96 entrées à `0xCCB2` |
| **surveillance T° / dP** | non dans cette zone | aucune entrée en 0…65 535 se comportant comme une loi de capteur |
| **handles morts** | 8 sur 12 | `0x1F8A 0x232E 0x1F0A 0x23F4 0x2148 0x1E76 0x1FE6 0x1FC8` |

**Ce que cette zone est vraiment** : la **tête du Datensatz** = un **panneau d'options de variante**
(`0xE111E` 42 o + `0xE1148` 52 o) suivi des **tables de service du diagnostic** (deux tables de valeurs
`0xFFFF`/zéro + une table de 20 valeurs converties). **Ce n'est pas** un bloc FAP.

**Où chercher le FAP** — pistes concrètes, dans l'ordre :
1. La **table de défauts `0xCCB2`** (96 entrées) : les enregistrements de défauts contiennent souvent un
   champ pointeur vers les seuils de surveillance associés → **c'est la meilleure porte d'entrée** vers
   les seuils FAP (dP, T°, suie).
2. Les grands blocs de `0xE26C4`, `0xE2xxx` et la famille `0x1B3C…0x1B50` déjà explorée.
3. Une recherche par **échelle** : la suie est en g (valeurs < 100), le dP en hPa (0…1000), le km en
   valeur /10 ou en dword — trois signatures très différentes d'un octet d'option.

---

## 6. Consignation

- **`CATALOGUE_MAITRE.md` § 13 B.11** ajouté : inventaire des 12 blocs, table des 97 lectures de `0xE1148`,
  mécanismes de diagnostic.
- **`zone_0xE1129.csv`** : un enregistrement par bloc (handle, EA, taille, contenu, lectures, segments).
- Catalogue : 2 090 → **2 142 lignes**.

## 7. Prochain pas proposé

1. **`0xCCB2` — table de défauts (96 entrées)** : décoder un enregistrement (taille, champ pointeur) et
   remonter aux seuils de surveillance. C'est la route la plus directe vers le FAP.
2. **Qui remplit RAM `0xDC2C`** (marqueurs `0xFE`/`0xFF` par PID) : la source dira quels identifiants
   sont « sans valeur ».
3. Les **16 sites du sélecteur d'échelle `+0x0A`** : ils forment un groupe homogène, les décoder donnera
   d'un coup ce que le bloc `0xE1148` paramètre vraiment.
