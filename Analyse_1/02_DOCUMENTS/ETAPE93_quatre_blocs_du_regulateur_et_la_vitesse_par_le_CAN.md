# ÉTAPE 93 — Les quatre blocs demandés, deux errata, et **la vitesse trouvée dans le code**

Cette étape répond point par point à tes quatre questions de dump, et elle apporte deux
corrections qui changent des choses établies. Le dénouement : **les ID CAN `0x38D` et `0x412` sont
écrits en clair dans le code**, et la chaîne vitesse est reconstituée de bout en bout.

---

## 1. ★★★ PREMIER ERRATA — `0x1DDA` n'est **pas** une courbe de température

Tu demandes, à juste titre, « pourquoi une température, de surcroît basse ? ». Réponse : **il n'y en
a pas.** L'étape 92 avait pris la valeur de la table des *handles* pour une adresse de **données**.
C'est faux pour cette cellule.

```asm
calls   0, word_1DDA          ; 35 sites — c'est un APPEL INDIRECT
```

`calls 0, …` signifie **segment 0**, dont la base est `0x80000` — c'est prouvé par les appels
directs de la même famille : `calls 9, sub_9CF70` avec `sub_9CF70 = 0x9CF70 = 0x90000 + 0xCF70`.

| cellule | valeur (table 0x61400) | cible réelle | lecture |
|---|---|---|---|
| `word_1D94` | `0xA556` | **EA `0x8A556`** | code (`64` appels) |
| `word_1DDA` | `0xB9DA` | **EA `0x8B9DA`** (fo `0xB9DA`) | code (`2A 02 F6 F4 D2 FB E6 F5 0E C4…`) |
| `word_1DA8` | `0xAD60` | **EA `0x8AD60`** | code |
| `word_1E08` | `0xBAB0` | **EA `0x8BAB0`** | code |
| `word_1DEC` | `0xBA40` | **EA `0x8BA40`** | code |
| `word_1DBC` | `0xAFD6` | — | **tout à zéro** (inutilisé) |

**Règle générale désormais acquise** : une valeur de handle est un **décalage 16 bits** ; le segment
est donné par l'usage —
**donnée** ⇒ `EA = 0xE0000 + valeur`, **code (`calls 0,`) ⇒ `EA = 0x80000 + valeur`.**

> **Ce que j'avais lu à `fo 0x6B9DA`** (`C3D2 · 2 · 2431 2531 · 0 0 · C7C2 · 2 · 6 40 …`) existe bien,
> mais ce n'est **pas** la cible : c'est une **bibliothèque de petites courbes 1-D** posée là, sans
> rapport avec le régulateur. L'« axe −30 / −20 °C » était une **coïncidence d'adressage**.
> ⇒ **ERRATA 92** : la ligne « `0x1DDA` = axe `C3D2` −30/−20 °C » est annulée.

---

## 2. ★★★ SECOND ERRATA — `C562` est la **VITESSE VÉHICULE**, pas la quantité

C'est le point le plus important de l'étape, et il découle directement de ta question sur le CAN.

### 2.1 La preuve par l'axe d'une carte

La carte `0xE868C` (handle `0x1B42`, déjà connue comme « 6×6 sur `C3D2` × `C562` ») porte, en clair
dans le fichier, **le tag `C562` sur son second axe** :

```
[C3D2][6][2431 2531 2631 2731 2831 3831]        ; T° eau : -30 / -20 / -10 / 0 / +10 / +110 °C
[C562][6][0 300 10000 12000 14016 18000]        ; 0 / 3 / 100 / 120 / 140,16 / 180
grille  : ligne -30 °C → [0, 9230, 9230, 9230, 9230, 9230]
          ligne -20 °C → [0, 8150, 8150, 8150, 8150, 8150]
          ligne -10 °C → [0, 4210, 4210, 4210, 4210, 4210]
          ligne   0 °C → [0, 1280, 1280, 1280, 1280, 1280]
```

Trois signatures, sans ambiguïté :

1. **un axe de quantité n'atteint jamais 18 000** ; en vitesse (0,01 km/h) c'est **180 km/h**, avec
   les points de rupture typiques **100 / 120 / 140 / 180** ;
2. la sortie est une **durée en µs** (9230 µs à −30 °C, 0 à +20 °C) indexée par la **température
   d'eau** : c'est le **post-chauffage / post-injection** ;
3. **la colonne 0 km/h vaut 0 dans toutes les lignes** ⇒ l'injection additionnelle est **coupée à
   l'arrêt** (ou quand la vitesse est invalide). Un axe « quantité » ne produit pas une colonne
   nulle à l'origine.

### 2.2 Les valeurs de repli le confirment

| calibration | valeur | lecture vitesse | lecture « quantité » |
|---|---|---|---|
| `[word_1470+6]` | **8000** | **80,00 km/h** (défaut si signal perdu) | 80 mg |
| `[word_1470+0x0E]` | 31621 | borne haute | absurde |
| `[word_1470+0x10]` | 2560 | **timeout** de la mesure | absurde |
| saturation des limiteurs | `0x7FFF` / `0x8000` | ±327,67 km/h | ±327 mg |

### 2.3 Conséquence

Toutes les comparaisons `cmp rX, word_C562` (≈ 90 sites) sont des **limitations par la vitesse** :
coupure du post-chauffage, EGR, couple, et surtout **le régulateur**. Et les deux *sources* de
`C562` sont, elles aussi, des vitesses (voir §6).

> **ERRATA 88 / 91** : « `C562` = quantité de référence en mg » est **annulé**.
> `C562` = **vitesse véhicule, 0,01 km/h**. Les deux cartes de souhait conducteur (`0xE8B50`,
> `0xE8BD4`) restent bien des cartes **mg** — elles ne passent pas par `C562`, mais par `C6DA`/`C952`.

---

## 3. `0xE1148` — la configuration véhicule (handle `0x141E`)

**56 octets utiles, puis `0xFF` de remplissage à partir de `+0x38`** (donc bloc de 56 octets, pas plus).

```
+0x00 : 00 00 00 08 04 01 01 00 00 04 00 02 00 00 00 02
+0x10 : 00 05 00 05 04 84 BE CA 64 00 01 01 01 00 01 96
+0x20 : 00 00 01 01 01 02 02 00 00 00 02 00 00 00 00 00
+0x30 : 01 01 00 00 FF FF FF FF FF FF FF FF …
```

Ce ne sont **pas des paramètres physiques** : c'est un **bloc de codage**, et le code le lit
**octet par octet**, chaque octet allant dans une variable `C2xx` distincte :

| offset | valeur ici | copiée dans | rôle établi |
|---|---|---|---|
| `+0x03` | `0x08` | `byte_C2BD` | codage (l.200013) |
| **`+0x05`** | **`0x01`** | **`byte_C2BC`** | ★ **origine de la vitesse/distance : `1` = impulsions filaires, `4` / `8` = CAN** (l.200027 → 143295 → 232484) |
| `+0x09` | `0x04` | — | variante : `== 4` ouvre le chemin `byte_C2BA` (l.142343, 142404) |
| `+0x0E` | `0x00` | `byte_C2B7` | ★ **masque de trames CAN** (bit0 = boîte `0x349`, bit3 = bloc ESP `0x412`/`0x50E`/`0x7E2`/`0x0A8`, `&6 == 6` = variante `0x34D`) |
| `+0x15` | `0x04` | `byte_C2C0` | — |
| `+0x16` | `0x00` | `byte_C2BF` | — |
| `+0x17` | `0x05` | `byte_C2B8` | — |
| `+0x19` | `0x05` | `byte_C2D0` | — |
| `+0x1A` | `0x04` | `byte_C2D1` | — |
| `+0x1B` | `0x84` | `byte_C2CC` | — |
| `+0x1C` | `0xBE` | `byte_C2C7` | — |
| `+0x1D` | `0xCA` | `byte_C2C3` | — |
| `+0x1E` | `0x64` | `byte_C2CE` | — |
| `+0x1F` | `0x00` | `byte_C2CF` | — |
| `+0x20` | `0x01` | `byte_C2CB` | — |
| `+0x21` | `0x01` | `byte_C2CD` | — |
| `+0x22` | `0x01` | `byte_C2C8` | — |
| `+0x23` | `0x00` | `byte_C2BE` | — |
| `+0x24` | `0x01` | `byte_C2C6` | — |
| `+0x25` | `0x96` | `byte_C2CA` | — |
| `+0x26` | `0x00` | `byte_C2C4` | (même offset que le `C60E` vu ailleurs) |
| `+0x28` | `0x01` | `byte_C2C1` | — |
| `+0x33` | `0x00` | — | conditionne la demande de la trame `0x34D` (l.139368) |

**Sept octets sont nuls en `+0x2A`…`+0x37` et `+0x38`–`+0x57` valent `0xFF`** : le bloc est
**rempli à `0xFF` = « non codé »** au-delà de `+0x37`.

⇒ Pour un 4HX **entièrement multiplexé**, c'est `+0x05` qui doit valoir `8` (CAN) et non `1`
(impulsions). **Dans ce dump il vaut `1`** : la calibration présente est réglée sur la **voie filaire**.
C'est un fait à vérifier sur ton véhicule — c'est exactement le champ qui décide de tout le §6.

---

## 4. `0xE2728` — paramètres (handle `0x14A2`)

Ce n'est **pas** un bloc PI/PID : c'est un **jeu de seuils de surveillance + une table d'identifiants**.
Seuls `+0x02` à `+0x0C` sont lus par le code.

| offset | mot | valeur | lecture |
|---|---|---|---|
| `+0x00` | 0 | `2000` | 2 000 (ms ? tr/min ?) |
| `+0x02` | 1 | **`2000`** | **lu** — temporisation/haute |
| `+0x04` | 2 | **`20`** | **lu** — petit seuil |
| `+0x06` | 3 | **`20`** | **lu** |
| `+0x08` | 4 | **`0`** | **lu** |
| `+0x0A` | 5 | **`0` / `68`** | **lu** — c'est ce `68` comparé à la pression rail dans `sub_AC65E` |
| `+0x0C` | 6 | `20` | **lu** |
| `+0x12` | 9 | `1384` | — |
| `+0x1A`…`+0x22` | 13-17 | **`0F10` `0F70` `0F08` `0F65` `0F7F`** | ★ **cinq identifiants de mesure** (dans la plage `0x0Fxx` du bloc de §7 de l'étape 92) |
| `+0x3C`+ | … | `C302 BFFE 1 1 40 0 200 500 20000 4000 400 0 100 300 1024 512 768 8 10000 896 896 0 8 2500 25000 …` | famille des blocs de **limitation** du §5 |

⇒ **Pour la régulation PI/PID, ce n'est pas ici.** Les seuls termes « intégrateur / gain » que j'aie
identifiés dans le régulateur sont les deux filtres `unk_24BA` de `loc_CFC6C` (états `word_F914` et
`word_F916`, descripteurs `word_1866` et `word_1864`) — voir §6.5.

---

## 5. `0xE4584` — **descripteurs de moniteurs de défaut** (handle `0x17B2`)

Ta question : « est-ce les appuis sur +/− ? » — **non**. La preuve est le site d'appel :

```asm
loc_AC9A4:                     ; l.171630
  mov  r3, #0EEh
  mov  r2, #267Fh              ; ← code de défaut 0x267F
  mov  r1, word_17B2           ; ← notre bloc, en argument descripteur
  calls 0Ch, sub_CE9B4         ; ← API moniteur (2 autres sites : 0xACA60, 0xACA74)
```

`word_17B2` n'apparaît **que** comme `r1` de `sub_CE9B4` (3 sites, tous dans
`sub_AC65E`-périphérie). **Aucun `[rN+#xx]`** n'est pris dessus : le bloc est consommé **en bloc**.

Contenu — et il est très lisible comme **couple (seuil, incrément/décrément)** :

```
1000  -1 |  69  -1 |   0   1 |  -1   0 |   1  -1 |   0   1 |  -1   0 |   1  -1 |   0   1
 500 | 100 |  65 | 500 | 100 |  81 |  -1   0 |   1  -1 |   0   1 | -2  0 | …
```

- `0xFFFF` (= −1) = **« pas de limite / pas d'incrément »** ;
- les paires alternées `(−1, 0)` / `(0, 1)` / `(1, −1)` = **tables de transition d'états du moniteur**
  (rien / montée / descente) ;
- `500`, `100`, `65`, `500`, `100`, `81` = **seuils d'appui** (durées ou counts).

⇒ Ce sont les **paramètres des moniteurs** (confirmation / effacement de défaut) du bloc pression
rail, pas des appuis de commande au volant.

---

## 6. `0xE964A` — le bloc d'état (handle `0x1C94`) : scalaires + courbe + **carte 8×8**

Là, il y a une vraie découverte : le bloc **contient une carte 2-D complète**, tags compris.

```
+0x00  500   150   300         ; ← les trois seuils lus par sub_AC65E (C91C = régime)
+0x06  1000  3000              ; ← lus aussi ([+0x06] et [+0x08])
+0x0A  [D4AC][2][1000 3000] → [5000 5000]        ; courbe sur 0xD4AC (plate = 50 bar ?)
+0x16  [C42E][8][200 500 750 1000 1500 2000 3000 4000]     ; ★ axe RÉGIME
+0x2A  [C7B8][8][2000 3000 5000 7000 9000 10000 11000 13000]  ; ★ axe C7B8
+0x3E  grille 8×8 :
       2000 2000 2000 2850 3300 3800 4200 4850
       2000 2000 2000 2850 3300 3800 4200 4850
       2000 2000 2850 3300 3800 4200 4850 1430
       1650 2150 2738 3250 3812 4196 4836 1408
       1650 2150 2700 3200 3762 4146 4836 1280
       1600 2100 2650 3150 3712 4096 4786 1152
       1500 2050 2550 3000 3700 4050 4736 1024
       1408 2000 2550 3000 3550 3900 4500  896
```

**Lecture** : une carte `[régime 200-4000] × [C7B8 2000-13000]` dont les valeurs vont de **896 à
4 850**, avec une **décroissance nette sur la dernière colonne** (4 850 → 896) et une colonne
d'entrée quasi nulle.

C'est la signature d'une **durée d'injection en µs** (0,9 à 4,85 ms) indexée par le régime et par un
axe de débit/pression. `C7B8` est **écrit** en `190859` (`mov word_C7B8, r4`) et relu en `192139`
(`add r6, word_C7B8`). **Je ne tranche pas** entre « consigne de débit (0,01 mg) » et « pression
rail ×10 » : les deux donnent un axe 2000-13000 plausible pour la plage. C'est en file d'attente.

Et, à propos de la question « pourquoi une température basse » : **`sub_AC65E` n'est pas le
régulateur de vitesse**, c'est la **machine à états de la pression rail** — les grandeurs comparées
sont `C91C` (régime) et **`word_C7C2` (pression rail ×10, acquis antérieur)**, avec cinq états,
`C140`/`C786`/`C7DE` en drapeaux et `word_F91C` comme horloge. Les `150 / 300` de `[0x1C94+2/+4]`
sont un **seuil de « moteur tourne »**, pas une température.

---

## 7. ★★★ LE CAN : `0x38D` et `0x412` sont **écrits en clair dans le code**

### 7.1 Le configurateur de réception

`sub_9A8B8` (l.139242) configure les objets du contrôleur CAN externe :

```asm
mov  r12, #0Bh        ; slot 11
mov  r13, #412h       ; ★ ID CAN 0x412
mov  r14, #0
mov  r15, #8          ; 8 octets
calls 9, sub_9CF70
…
mov  r12, #0Ch        ; slot 12
mov  r13, #38Dh       ; ★ ID CAN 0x38D
mov  r14, #0
mov  r15, #5          ; 5 octets lus
calls 9, sub_9CF70
```

`sub_9CF70(r12=slot, r13=ID, r14=bit de contrôle, r15=longueur)` écrit l'objet **16 octets** à
`0xEF00 + 16×slot` : `[+0] = 0x5595` (objet armé), `[+2] = ID encodé`, `[+4] = 0`, `[+6] = (len<<4)|0xFF00`
(+ bit3 si `r14 = 1`).

### 7.2 La table complète de réception (16 slots)

| slot | objet | ID CAN | long. | condition d'armement | destination RAM | décodeur |
|---|---|---|---|---|---|---|
| 1 | `0xEF10` | `0x208` | 8 | toujours | ? | ? |
| 2 | `0xEF20` | `0x348` | 5 | toujours | ? | ? |
| 3 | `0xEF30` | `0x488` | 8 | toujours | ? | ? |
| 4 | `0xEF40` | `0x072` **puis `[word_1650]`** | 5 **/ 8** | `[word_1650] ≠ 0` | ? | ? (ID **programmable** ⇒ candidat pour `0x468`) |
| 5 | `0xEF50` | `0x788` | 6 | toujours | ? | ? |
| 7 | `0xEF70` | `0x388` | 5 | toujours | ? | ? |
| 8 | `0xEF80` | `0x7E2` | 6 | `byte_C2B7 & 8` | `0xC82B` | `sub_9C43A` |
| **9** | `0xEF90` | **`0x349`** | **7** | **`byte_C2B7 & 1`** | **`0xC86E`** | **`sub_9B796` → rapport de boîte** |
| 10 | `0xEFA0` | `0x50E` | 3 | `byte_C2B7 & 8` | `0xC7E8` | `sub_9C206` |
| **11** | **`0xEFB0`** | **`0x412`** | **8** | **`byte_C2B7 & 8`** | **`0xC87D`** | **`sub_9C23E`** |
| **12** | **`0xEFC0`** | **`0x38D`** | **5** | ★ **`byte_C2BC == 8`** | **`0xC811`** | **`sub_9C56A`** |
| 13 | `0xEFD0` | `0x389` | 5 | `byte_C2B7 & 1` | `0xC816` | `sub_9C76A` |
| 14 | `0xEFE0` | `0x34D` | 6 **ou 5** | `byte_C2B7 & 6 == 6`, longueur selon `[0x141E+0x33]` | `0xC825` | ? |
| 15 | `0xEFF0` | `0x0A8` | 5 | `byte_C2B7 & 8` | ? | ? |

**`0x468` : absent du fichier** (aucune occurrence de `#468h`). Mais l'objet **4** a un ID
**programmable par la calibration** (`word_1650`) avec une longueur de 8 octets : c'est la place
naturelle d'une trame variable selon la génération de bloc ABS/ESP. Hypothèse, pas lecture.

### 7.3 Deux confirmations croisées indépendantes

La table ci-dessus (configurateur) et la table de **lecture** `sub_9D166` (étape 25) donnent
exactement les mêmes longueurs :

| slot | ID | long. | destination | destination vue par `sub_9D166` |
|---|---|---|---|---|
| 9 | `0x349` | 7 | `0xC86E` | `0xC86E`, 7 octets ✔ |
| 11 | `0x412` | 8 | `0xC87D` | `0xC87D`, 8 octets ✔ |
| 12 | `0x38D` | 5 | `0xC811` | `0xC811`, 5 octets ✔ |
| 13 | `0x389` | 5 | `0xC816` | `0xC816`, 5 octets ✔ |
| 14 | `0x34D` | 5/6 | `0xC825` | `0xC825`, 5 octets ✔ |

---

## 8. La chaîne vitesse, de la trame à la régulation

### 8.1 Trame `0x38D` → `C811…C815` → `sub_9C56A` (l.142630)

```asm
movb [r0+#1], byte_C811      ; octet 0  (poids fort)
movb [r0+#0], byte_C812      ; octet 1  (poids faible)  → mot 16 bits big-endian
movb [r0+#3], byte_C813      ; octets 2-3 = compteur / odomètre
movb [r0+#2], byte_C814
```

| octets | usage | destination | traitement |
|---|---|---|---|
| **0-1** | **valeur 16 bits** | **`word_C3FA`** | `0xFFFF` = invalide → défaut `[word_1470+6] = 8000` ; sinon `unk_2196(x, gain, offset)` avec le descripteur **`0xE407E` = (1024, 0)**, borné **0…0x7FFF** |
| **2-3** | **compteur continu** | **`word_C406`** | `unk_2196` (descripteur **`0xE406E` = (10240, 0)**) puis **différence** avec `word_CF7E` (valeur précédente) → **incrément de distance** |
| 4 | **états ABS/ESP** | **`word_C3F2`** | `0xFF` = invalide ; sinon `unk_2184` (descripteur `0xE3FFC`) + **filtre `unk_1E50`** (état `word_CF7A`) |
| — | fanions de validité | `word_FD00.13`, `byte_C23E` | bits 0/2/4 = « valeur fraîche » par champ |

La trame `0x389` (slot 13, `0xC816`, décodeur `sub_9C76A`) a **exactement la même structure**
(mot 0-1 → `C3FA`, mot 2-3 → `C406`, octet 4 → `C3F2`) : ce sont **deux sources redondantes**, la
seconde étant armée par `byte_C2B7 & 1` (codage boîte) et non par `C2BC`.

### 8.2 Trame `0x412` → `C87D…C884` → `sub_9C23E` (l.142258)

| bits lus | destination |
|---|---|
| `C87D` bit 5, sous condition `byte_C255 == 0xAA` | `byte_C229` |
| `C87E` bit 1, et bits 4-5 (`& 0x30 >> 4`) | `byte_C23D` |
| `C880` `>> 6` | `byte_C23F` |
| `C883 & 3` | `byte_C248` |
| **`C884`** | `unk_20AC(x, 4, 1)` + offset → **`word_C3F8`**, borné 0…0x7FFF |
| sinon (défaut) | `word_C3F8 = [word_1658+0x16]` |

Et `byte_C23E & 3` sert **justement** dans le bloc de sélection de source (§8.4) : c'est le drapeau
« vitesses de roues cohérentes / ESP actif ».

### 8.3 La distance → l'odomètre (`l.153570`, dispatch sur `byte_C2F8`)

```asm
cmpb rl4, #4  → loc_A23E6
cmpb rl4, #1  → source IMPULSIONS : C838 += C56C × [word_1470+2] / 4   (bouclage à 0x55D5)
cmpb rl4, #8  → source CAN       : C838 = 0 ; accumulateur 32 bits C83A/C83C += word_C406
```

⇒ **`byte_C2BC` / `byte_C2F8` = sélecteur de la source vitesse/distance** :
`1` = impulsions (CC1), `4` = variante, `8` = CAN. Et `0xE1148+5 = 1` **dans cette calibration**.

### 8.4 Le sommet : `C3FA`/`C578` → **`C562`**

Trois écrivains seulement (plus un quatrième indirect via `sub_9B2B2`, l.140311, qui pose une
« caractéristique » dans `#0C562h` par `unk_2172` — non élucidé) :

| site | écriture | condition |
|---|---|---|
| `232350` (`sub_CF8C8`) | **`C562 = C3FA`** (CAN) ; `C552 = C3F2` | `byte_C2F8 == 8` |
| `232362` | `C568 = 1`, `C566 = C3FA` | si `byte_C23E & 3` |
| **`232870`** (`loc_CFDD2`) | **`C562 = C578`** (impulsions) ; `C552 = byte_F91A` | `byte_C2F8 == 1` |

`sub_CF8A4` (variante `4`) pose **`C562 = 0xFF`** (= 2,55 km/h, « non disponible »).

### 8.5 La mesure par impulsions : `loc_CFB36` → `sub_CF774` (l.232620)

C'est une **mesure de période sur capture CC1** :

```asm
mov r5, CC1_T0 ; subb rh2, PECC2 ; mov PECC2, #64h      ; lecture de la capture
…
word_C56C = (période >> 8)                               ; période grossière
add word_F90E, (F910 − F912) ; byte_F919 (débordements, 0x80 = remise à zéro)
word_F908 = C578 ; mulu C556, r2 ; divlu r6              ; ← C556 = [word_1470+2] = 17578
word_C566 = résultat                                     ; vitesse lissée sur la fenêtre
…
loc_CFC6C :
  r2 = |C578 − F90C| ; divlu F910      →  dérivée = Δv / Δt
  r3 = word_1864 ; unk_24BA(…)         →  filtre (état word_F916)
  bornes [word_1470+0x0C] / [+0x0D]    →  byte_F91A
```

⇒ **`C578` = vitesse mesurée (impulsions), `byte_F91A` = son accélération filtrée**, et `C552`
reçoit cette accélération. **Voilà le « delta » du régulateur** — il est en **km/h par unité de
temps**, pas en pourcentage de pédale.

Et `sub_CF774` (l.232170) termine par :

```asm
r4 = C578 ; MDH = rh4 ; shl r4, #8 ; divlu r0
r0 = [word_1470+0x0E] (= 31621) ; cmp r0, MDL      ; borne haute
C56A = unk_24BA(filtre, word_185C, MDL, C93E)
C93E = C576 ; C576 = C93E                          ; ★ le mode recopié
```

---

## 9. Lu / inféré

| affirmation | statut |
|---|---|
| `calls 0, word_1DDA` → code en `0x8B9DA` ; la « courbe −30 °C » était un artefact | **lu** (valeur `0xB9DA`, segment 0 = `0x80000`, code à fo `0x0B9DA`) |
| `C562` = vitesse (axe `[C562][6][0 300 10000 12000 14016 18000]` de `0xE868C`) | **lu** ; interprétation 0,01 km/h **très solide** |
| défaut `8000` = 80,00 km/h | **lu** ; unité **inférée** |
| `0xE1148+5` → `byte_C2BC` → sélecteur de source vitesse/distance | **lu** (l.200027, 143295, 153570, 232484) |
| `0xE4584` = descripteurs de moniteurs (argument `r1` de `sub_CE9B4`) | **lu** ; sémantique des paires **inférée** |
| `0xE964A` contient une carte 8×8 `C42E × C7B8` | **lu** (tags et axes ascendants) |
| IDs `0x38D` / `0x412` reçus, slots 12 / 11 | **lu** (l.139313, 139360) + **recoupé** par `sub_9D166` |
| `0x468` absent du fichier | **lu** ; l'objet 4 à ID programmable est une **hypothèse** |
| physique du bus (250 kbit/s, 10-20 ms) | **hors fichier** — je n'ai aucun moyen de la vérifier ici |

---

## 10. File d'attente (mise à jour)

1. **`word_C7B8`** : qui l'écrit (`190859`) → tranche « débit » vs « pression rail » pour la carte
   `0xE964A`.
2. **Interrupteur de frein et d'embrayage** : les ports numériques ne sont pas symbolisés dans
   `clean.asm` (aucun `P2_`/`P3_`). Méthode à essayer : partir des **conditions de sortie d'état** du
   régulateur (`word_C7DE` bits 4 et 8, `byte_D82A`) et remonter aux bits d'entrée.
3. **`C576` / `C93E`** : c'est le même mot recopié (`C93E = C576`) ; seuil **539** dans `sub_B56F8`
   et **10000** en `loc_B58F0`. Trouver qui écrit `C576` **autrement que par recopie**.
4. **`unk_2172`** (écrivain indirect de `C562`) et **`unk_24BA`** (filtre) : bibliothèque segment 0.
5. Cartes « inversées » du régulateur : maintenant qu'on sait que `C562` est une **vitesse**, chercher
   les cartes à axe vitesse **décroissant** dans la zone `0xE86xx`–`0xE8Cxx`.
