# CATALOGUE MAÎTRE — ECU Bosch EDC15C2 / PSA 2.2 4HX FAP

**Réf. calculateur** : `0 281 010 877` — version **multiplexée (full mux)**  
**Véhicule** : Peugeot 406 2.2 HDi 4HX avec FAP  
**Document régénéré le** : 2026-11-23 — par `outils/genere_catalogue.py`

> **Document vivant.** Il est régénéré automatiquement à partir du binaire, du désassemblage et des
> CSV d’annotation. Chaque trouvaille ajoute une ligne ou une nuance ; les affirmations retirées
> restent visibles au § 9 (registre des erratas) pour ne pas être réintroduites par erreur.

---

## 1. Conventions et niveaux de confiance

| niveau | sens |
|---|---|
| **lu** | établi par lecture directe du binaire ou du code, avec n° de ligne `clean.asm` |
| **util** | donnée fournie par l’utilisateur, non vérifiable ici |
| **inf** | inférence forte, appuyée sur plusieurs observations concordantes |
| **?** | inconnu — aucune conclusion |

**Adressage.** `EA = 0xE0000 + valeur de la table des pointeurs`. La table des pointeurs est à
l’adresse `0xE1400` (**offset fichier `0x61400`**), une valeur 16 bits par handle, handle `word_1400`
étant l’entrée 0. **Offset fichier = `0x60000 + valeur`.** Le Datensatz dupliqué est à `0xF0000`
(**offset fichier `0x70000`**).

**Bornes de bloc.** Le bloc d’un handle va de sa valeur à la valeur suivante (ordre croissant).
Méthode validée quatre fois indépendamment (étapes 48 à 51).

**Grandeurs internes** : `0…10000` = `0…100 %` (convention utilisateur). Les axes portent leur
propre échelle ; une valeur d’axe n’a pas d’unité en soi.

---

## 2. Les gabarits d’enregistrement identifiés

| type | gabarit | taille | preuve |
|---|---|---|---|
| **Courbe 1-D** | `[adresse variable][n][axe : n mots][valeurs : n mots]` | `4 + 4n` | **181 tailles exactes** sur 248 (étape 51) |
| **Carte 2-D** | `[tagY][nY][axeY][tagX][nX][axeX][grille : nY×nX mots]` | `8 + 2nY + 2nX + 2·nY·nX` | **66 tailles exactes sur 66** (étape 51) |
| **Paramètre scalaire** | un seul mot de calibration | 2 | blocs de 2 octets, étape 52 |
| **Bloc réservé** | `0xFFFE` suivi de zéros | 32 | **7 blocs vides** repérés, étape 52 |
| **Table d’index** | `0xFFF2` puis une suite d’entiers consécutifs | 32 | `1136, 1137, 1138…`, étape 52 |
| **Bloc balayé** | aucun en-tête — lu **mot après mot** de `0x00` à la fin | = taille du bloc | **46 blocs** (étape 54) |
| **Enregistrement triple EEPROM** | `1 octet de tag` + valeur **en trois exemplaires** | 7 ou 4 | étapes 45-46 |

**★ Point capital** : un enregistrement **nomme sa variable**. Le premier mot d’une courbe ou d’une
carte est l’**adresse RAM** de la grandeur traitée (étape 50). C’est ce qui rend le Datensatz
auto-descriptif — et ce qui permet l’annotation automatique du § 4.

---

## 2 bis. Répartition réelle par gabarit, et trois constats

| gabarit | nombre |
|---|---|
| **courbes 1-D** (`4 + 4n`, taille exacte) | 182 |
| **cartes 2-D** (`8 + 2nY + 2nX + 2·nY·nX`, taille exacte) | 66 |
| **blocs d’axe** (`[adresse variable][n][n valeurs]`, `4 + 2n`) | 31 |
| **blocs réservés** (`0xFFFE`…`0xFF00 0xC300`) | 7 |
| **paramètres scalaires** (bloc de 1 mot) | 91 |
| **non classés** (dont les blocs d’axe ci-dessus) | 927 |

### ★ Constat 1 — le Datensatz est **dominé par des blocs de taille fixe**

Répartition de **tous** les blocs par nombre de mots (toutes catégories confondues) :

| taille | nombre de blocs |
|---|---|
| **1 mots** (2 o) | 91 |
| **2 mots** (4 o) | 94 |
| **3 mots** (6 o) | 364 |
| **4 mots** (8 o) | 53 |
| **5 mots** (10 o) | 65 |
| **6 mots** (12 o) | 136 |
| **7 mots** (14 o) | 10 |
| **8 mots** (16 o) | 16 |
| **9 mots** (18 o) | 17 |
| **10 mots** (20 o) | 24 |
| **11 mots** (22 o) | 5 |
| **12 mots** (24 o) | 35 |
| **13 mots** (26 o) | 2 |
| **14 mots** (28 o) | 37 |
| **15 mots** (30 o) | 4 |
| **16 mots** (32 o) | 119 |
| **17 mots** (34 o) | 6 |
| **18 mots** (36 o) | 48 |
| **19 mots** (38 o) | 1 |
| **20 mots** (40 o) | 1 |

**Le plus fréquent est 3 mots (364 blocs).** Ce ne sont ni des courbes ni des cartes : ce sont des
**paquets de paramètres lus à offsets fixes** par un sous-programme. `word_142A` (5 mots, § 7) en est
l’exemple type : `[+0] [+2] [+4] [+6]` sont **le 1er, 2e, 3e et 4e mot**, pas des champs typés.

### ★ Constat 2 — un marqueur récurrent dans les blocs de 32 octets

Sur **119 blocs de 32 octets**, le mot d’offset `+0x12` vaut :

| valeur | nombre |
|---|---|
| `0x0F10` | 56 |
| `0x0000` | 10 |
| `0x0F00` | 8 |
| `0x0F60` | 4 |
| `0x0005` | 4 |
| `0x000A` | 4 |

**Les valeurs dominantes sont dans la bande `0x0Fxx`** — un marqueur régulier à position fixe. **Son sens
n’est pas établi** ; il est noté comme **point de contrôle**, pas comme résultat.

### ★ Constat 3 — blocs d’axe : hypothèse testée et **réfutée**

31 blocs ont la forme `[adresse variable][n][n valeurs]`. Le premier, `word_1400`, décrit une
**échelle de régime à 8 points (200…4000)** sur `word_C42E`. J’ai testé l’idée qu’il s’agisse d’une
**bibliothèque d’axes partagés** : sur ces 31 blocs, **2 seulement sont réutilisés tels quels** comme axe
d’une carte. **⇒ l’hypothèse est réfutée**, ce ne sont pas des axes partagés.

En revanche, une observation utile subsiste : **les handles `1400`, `1402`, `1404`, `1406`, `1408` sont
cinq blocs consécutifs décrivant tous `word_C42E`** (8, 2, 16, 16 et 8 points). Cinq échelles de régime
distinctes et voisines — la signature d’une **famille d’axes**, utilisée par la couche absente.

---

### ★ Constat 4 — décodage **par usage** : 270 handles sont lus par le code

| | |
|---|---|
| handles du Datensatz avec au moins un accès identifiable | **270 / 1304** |
| dont **balayage séquentiel** (`0x00, 0x02, 0x04, 0x06…`) | **46** |

**Un « balayage séquentiel » = le bloc est lu mot après mot depuis `0x00` jusqu’à la fin.** C’est un
**gabarit supplémentaire** : le bloc n’a pas de champs nommés, il est **parcouru intégralement**.

| handle | taille du bloc | dernier offset lu | concordance |
|---|---|---|---|
| `word_14A0` | 100 | `0x62` | **exacte** |
| `word_18C2` | 78 | `0x4C` | **exacte** |
| `word_161A` | 66 | `0x40` | **exacte** |
| `word_1C3E` | 66 | `0x40` | **exacte** |
| `word_1952` | 62 | `0x3C` | **exacte** |
| `word_18F2` | 58 | `0x38` | **exacte** |
| `word_1972` | 56 | `0x36` | **exacte** |
| `word_1432` | 48 | `0x2E` | **exacte** |
| `word_14B0` | 46 | `0x2C` | **exacte** |
| `word_1DB0` | 46 | `0x2A` | ≤ |
| `word_1904` | 42 | `0x28` | **exacte** |
| `word_18EE` | 38 | `0x24` | **exacte** |

**Trois cas vérifiables tombent juste à l’octet** : `word_1952` (bloc 62, dernier offset `0x3C`),
`word_18F2` (bloc 58, dernier offset `0x38`), et la liste ci-dessus. **C’est la cinquième validation
indépendante des bornes de blocs.**

> **Méthode à retenir** : pour nommer un handle, il faut **le sous-programme qui le lit et les
> offsets qu’il touche**. Les tableaux complets sont dans `usage_handles_resume.csv` et
> `usage_handles_offsets.csv`.

---

### ★★★ Constat 5 — le Datensatz est **rangé par FONCTION CONSOMMATRICE**

En associant chaque accès du code à sa fonction englobante (`outils/consommateurs.py`), on obtient :

| fonction | handles distincts | accès |
|---|---|---|
| **`sub_AFAA0`** | 17 | 160 |
| **`sub_A1E9E`** | 15 | 219 |
| **`sub_B64A8`** | 13 | 68 |
| **`sub_C4AAE`** | 12 | 41 |
| **`sub_ACD4A`** | 10 | 49 |
| **`sub_B7FD4`** | 9 | 241 |
| **`sub_A7D96`** | 9 | 252 |
| **`sub_B35B6`** | 9 | 150 |
| **`sub_C8012`** | 8 | 115 |
| **`sub_BAC40`** | 7 | 128 |
| **`sub_A5C92`** | 7 | 143 |
| **`sub_D2EAA`** | 7 | 111 |

**Chaque routine possède 7 à 19 blocs de calibration et rien d’autre.** La calibration n’est donc
**pas rangée par grandeur physique, mais par consommateur.** C’est le principe d’organisation du
Datensatz, et il donne une **méthode de nommage** : le rôle de la fonction nomme ses blocs.

#### La preuve par recoupement : `sub_A1E9E`

`sub_A1E9E` est la **routine de confirmation des défauts**, décodée à l’étape 42. Voici les blocs
qu’elle consomme :

| handle | taille | déjà identifié par une autre voie ? |
|---|---|---|
| `word_18C2` | 78 | non — **nouveau**, 78 octets, 45 champs |
| `word_1474` | 34 | **oui** — durées de confirmation (étape 49) |
| `word_18B2` | 30 | **oui** — masque de variante (étape 50) |
| `word_189C` | 18 | non — **rattaché par cette voie** |
| `word_1874` | 16 | non — **rattaché par cette voie** |
| `word_189A` | 12 | non — **rattaché par cette voie** |
| `word_186A` | 12 | non — **rattaché par cette voie** |
| `word_142A` | 10 | **oui** — seuils du moniteur (étape 42) |
| `word_1818` | 6 | **oui** — numéros de bits 2,1,0,8,15 (étape 47) |
| `word_1878` | 6 | **oui** — source de `word_C596` (étape 50) |
| `word_187A` | 2 | non — **rattaché par cette voie** |
| `word_1896` | 2 | non — **rattaché par cette voie** |
| `word_1898` | 2 | non — **rattaché par cette voie** |
| `word_1472` | 2 | non — **rattaché par cette voie** |
| `word_18E6` | 2 | non — **rattaché par cette voie** |

**Six blocs sur quinze avaient été identifiés séparément, par des chemins totalement différents.**
Que la même routine les consomme tous est une **cinquième validation croisée** — et elle porte sur
l’**interprétation**, pas seulement sur les tailles.

Les neuf autres blocs (`18C2`, `189A`, `186A`, `1874`, `189C`, `187A`, `1896`, `1898`, `18E6`) sont
désormais **rattachés au sous-système de diagnostic** : leur rôle est connu, leurs champs non.

### ★ Observation : le numéro de handle **classe** le bloc

| sous-système | plage de handles dominante |
|---|---|
| diagnostic / moniteurs (`sub_A1E9E`) | **`0x18xx`** |
| surveillance `word_C5B8` (`sub_A5C92`) | **`0x18Ex…0x18Fx`** |
| `sub_A7D96` | **`0x19xx`** |
| `sub_BAC40` | **`0x14xx`** et `0x1Cxx` |

**Le handle n’est pas une adresse arbitraire : c’est un index de classement.** Les blocs voisins
appartiennent au même sous-système. **Cela permet de prédire à quel ensemble appartient un bloc
non encore identifié, à partir de son seul numéro.**

---

## 2 ter. ★ Le Datensatz est stocké en DEUX exemplaires complets

**0xE0000-0xEBFFF et 0xF0000-0xFBFFF sont identiques à 14 octets près.** Vérifié octet par octet.
Ce ne sont pas deux zones différentes : c’est **la même calibration, écrite deux fois**.

### Les 14 octets qui diffèrent — les cinq seules différences

| exemplaire E | exemplaire F | taille | E | F | lecture |
|---|---|---|---|---|---|
| `0xE0FF6` | `0xF0FF6` | 4 | `3d d3 3d d3` | `c3 c3 00 00` | champ de contrôle n°1 (deux mots) — renseigné en E, **remplissage** en F |
| `0xE0FFC` | `0xF0FFC` | 4 | `c9 32 05 b2` | `d4 cd c0 17` | champ de contrôle n°2 (double mot) — renseigné dans les deux, valeurs différentes |
| `0xE434D` | `0xF434D` | 1 | `23` | `03` | un octet de calibration diffère entre les deux variantes |
| `0xEBCFC` | `0xFBCFC` | 4 | `dd 35 d9 5b` | `20 5c 77 af` | champ de contrôle de queue (double mot) — différent dans chaque exemplaire |
| `0xEBF1B` | `0xFBF1B` | 1 | `57` | `46` | « W » (0x57) contre « F » (0x46) dans la chaîne __N**x**GDWPF1 |

**Ce que ces cinq différences disent :**

1. **`0xE0FF6` et `0xE0FFC` = deux champs de contrôle en tête du Datensatz.** Dans l’exemplaire E ils
   portent des valeurs concrètes (`0xD33D` **deux fois**, puis `0xB20532C9`) ; dans l’exemplaire F,
   les deux mots valent `0xC3C3` et `0x0000` — c’est-à-dire **le remplissage**, non renseigné.
   **⇒ L’exemplaire E est la calibration active ; F est un miroir dont les champs de contrôle
   n’ont pas été remplis.**
2. **`0xEBCFC` = un second champ de contrôle en queue de Datensatz**, différent dans chaque
   exemplaire — donc **il dépend bien des données**, ce qui est le comportement d’une somme de
   contrôle. ⚠ **On sait donc OÙ sont les sommes de contrôle, mais toujours pas COMMENT elles sont
   calculées** : 15 algorithmes testés (sommes, CRC-16 CCITT/XMODEM/IBM, CRC-32, compléments)
   **sans succès**. C’est un progrès de localisation, pas une résolution.
3. **`0xEBF1B` : l’octet passe de `0x57` (« W ») à `0x46` (« F »)** dans la chaîne
   `__NWGDWPF1` / `__NFGDWPF1`. **Hypothèse (non prouvée)** : `F` = **FAP**, `W` = sans filtre.
   Ce serait l’identifiant de la variante — cohérent avec un véhicule FAP dont le calculateur
   contient aussi la calibration sans filtre.
4. **`0xE434D` : un octet `0x23` → `0x03`** au milieu d’une structure. Différence de calibration
   entre les deux variantes ; **laquelle est utilisée n’est pas établi**.

### Ce que cela change pour tout le reste du catalogue

**Rien, et c’est important** : la table de pointeurs de `0xE1400` est **identique dans les deux
exemplaires**, et ses valeurs sont des **offsets relatifs** (0x100A … 0xBC38). Le même handle
désigne donc **la même structure dans les deux exemplaires**. Toutes les adresses EA du catalogue
sont données **dans l’exemplaire E** ; ajouter `0x10000` donne l’exemplaire F.

*Preuve : `outils/tables_oubliees.py` → `duplication_datensatz.csv`.*

---

## 3. Inventaire des variables (les « tags »)

Une même variable peut servir d’entrée à plusieurs enregistrements. Le nombre d’axes et la plage
globale sont calculés automatiquement : **la plage est le premier indice d’identification**.

| variable | axes (1-D / 2-D) | plage globale | grandeur | unité | statut |
|---|---|---|---|---|---|
| **word_C42E** | 42 / 49 | 0 … 6000 | régime moteur | tr/min | lu+plage 0-6000 |
| **word_C3D2** | 27 / 8 | 2231 … 4231 | température liquide de refroidissement | K ×10 | lu (chaîne 0x318) |
| **word_C60A** | 11 / 5 | 0 … 1800 | ? | ? | ? |
| **word_C6A2** | 1 / 14 | 0 … 10000 | grandeur de charge | 0…100 % (×100) | lu (plage 0-10000) |
| **word_C3BA** | 9 / 4 | 2231 … 4081 | température air d’admission | K ×10 | lu (chaîne 0x30E) |
| **word_C7C2** | 3 / 6 | 0 … 14000 | ? | ? | ? |
| **word_C5A8** | 5 / 0 | 100 … 11000 | masse d’air par tour | mg ×10 | inf (étape 50) |
| **word_C3B0** | 3 / 2 | 2531 … 3931 | température gasoil | K ×10 | lu (chaîne 0x310) |
| **word_C3C2** | 1 / 3 | 0 … 678 | rapport cyclique (RCO ?) | 0…1000 | inf |
| **word_D004** | 0 / 4 | 0 … 7000 | ? | ? | ? |
| **word_C5BC** | 3 / 0 | -32768 … -29408 | ? | ? | ? |
| **word_D1F4** | 2 / 1 | 0 … 5000 | ? | ? | ? |
| **word_C562** | 2 / 1 | 0 … 20000 | ? | ? | ? |
| **word_C586** | 3 / 0 | 3731 … 8731 | ? | ? | ? |
| **byte_D36A** | 3 / 0 | 0 … 255 | ? | ? | ? |
| **word_D5AE** | 3 / 0 | 1 … 30000 | ? | ? | ? |
| **word_C3EE** | 0 / 3 | 0 … 4910 | ? | ? | ? |
| **word_C60E** | 0 / 3 | 0 … 7000 | ? | ? | ? |
| **word_C77A** | 2 / 0 | 6667 … 31667 | ? | ? | ? |
| **word_C38E** | 2 / 0 | 626 … 960 | ? | ? | ? |
| **word_D1B6** | 2 / 0 | 500 … 11000 | ? | ? | ? |
| **word_C5A4** | 2 / 0 | 2431 … 3331 | masse d’air par tour | mg ×10 | inf |
| **byte_D369** | 2 / 0 | 0 … 255 | ? | ? | ? |
| **word_D36C** | 2 / 0 | 0 … 14701 | ? | ? | ? |
| **word_C7C6** | 1 / 1 | 1000 … 12000 | ? | ? | ? |
| **word_C3A8** | 0 / 2 | 400 … 2400 | ? | ? | ? |
| **word_C612** | 0 / 2 | 700 … 2200 | ? | ? | ? |
| **word_C3E6** | 0 / 2 | 0 … 11500 | débit d’air | mg/s (axe ×10) | util |
| **word_C6DA** | 0 / 2 | 118 … 10000 | ? | ? | ? |
| **word_D03A** | 1 / 0 | 485 … 970 | ? | ? | ? |
| **word_D03C** | 1 / 0 | 0 … 788 | ? | ? | ? |
| **word_D044** | 1 / 0 | 20 … 1003 | ? | ? | ? |
| **word_D048** | 1 / 0 | 32 … 1023 | ? | ? | ? |
| **word_D04A** | 1 / 0 | 10 … 991 | ? | ? | ? |
| **word_D04C** | 1 / 0 | 51 … 972 | ? | ? | ? |
| **word_D052** | 1 / 0 | 20 … 1003 | ? | ? | ? |
| **word_D054** | 1 / 0 | 0 … 1023 | ? | ? | ? |
| **word_D056** | 1 / 0 | 102 … 922 | ? | ? | ? |
| **word_D05E** | 1 / 0 | 32 … 969 | ? | ? | ? |
| **word_D060** | 1 / 0 | 20 … 1023 | ? | ? | ? |
| **word_D066** | 1 / 0 | 192 … 1064 | ? | ? | ? |
| **word_D06C** | 1 / 0 | 40 … 962 | ? | ? | ? |
| **word_D06E** | 1 / 0 | 59 … 328 | ? | ? | ? |
| **word_D070** | 1 / 0 | 102 … 691 | ? | ? | ? |
| **word_D072** | 1 / 0 | 2 … 4 | ? | ? | ? |
| **word_D07C** | 1 / 0 | 0 … 1023 | ? | ? | ? |
| **word_D07E** | 1 / 0 | 0 … 1023 | ? | ? | ? |
| **word_D080** | 1 / 0 | 2 … 4 | ? | ? | ? |
| **word_D082** | 1 / 0 | 2 … 4 | ? | ? | ? |
| **word_C3AA** | 1 / 0 | 57 … 340 | ? | ? | ? |
| **word_D084** | 1 / 0 | 42 … 1002 | ? | ? | ? |
| **word_C4CE** | 1 / 0 | 0 … 3000 | ? | ? | ? |
| **word_C3DA** | 1 / 0 | 6667 … 28333 | ? | ? | ? |
| **word_D17C** | 1 / 0 | 0 … 180 | ? | ? | ? |
| **word_C7CA** | 1 / 0 | 500 … 1000 | ? | ? | ? |
| **word_C4D8** | 1 / 0 | 400 … 5000 | ? | ? | ? |
| **byte_C337** | 1 / 0 | 0 … 250 | ? | ? | ? |
| **word_C3F8** | 1 / 0 | 32 … 1013 | ? | ? | ? |
| **word_C596** | 1 / 0 | 0 … 3000 | ? | ? | ? |
| **word_C588** | 1 / 0 | 2631 … 3331 | ? | ? | ? |
| **word_C61C** | 1 / 0 | 0 … 7000 | ? | ? | ? |
| **word_D1FE** | 1 / 0 | 500 … 6000 | ? | ? | ? |
| **word_D230** | 1 / 0 | 2731 … 2931 | ? | ? | ? |
| **word_D232** | 1 / 0 | 2531 … 2931 | ? | ? | ? |
| **word_D234** | 1 / 0 | 2531 … 2931 | ? | ? | ? |
| **word_D240** | 1 / 0 | -27269 … 32731 | ? | ? | ? |
| **word_D242** | 1 / 0 | -27269 … 32731 | ? | ? | ? |
| **word_D244** | 1 / 0 | -27269 … 32731 | ? | ? | ? |
| **word_C5FA** | 1 / 0 | 2331 … 3031 | ? | ? | ? |
| **word_C58E** | 1 / 0 | 0 … 1 | ? | ? | ? |
| **word_D354** | 1 / 0 | -5000 … 6000 | ? | ? | ? |
| **byte_D366** | 1 / 0 | 0 … 224 | ? | ? | ? |
| **word_D3CC** | 1 / 0 | 2231 … 4231 | ? | ? | ? |
| **word_C63C** | 1 / 0 | -4267 … 17493 | ? | ? | ? |
| **word_D4AC** | 1 / 0 | 1000 … 3000 | ? | ? | ? |
| **word_C7C4** | 1 / 0 | 1000 … 2500 | ? | ? | ? |
| **word_D014** | 1 / 0 | 0 … 9000 | ? | ? | ? |
| **word_C3E4** | 1 / 0 | -6000 … 8000 | ? | ? | ? |
| **word_C3E8** | 1 / 0 | 0 … 2000 | ? | ? | ? |
| **word_D5A2** | 1 / 0 | 4731 … 5731 | ? | ? | ? |
| **word_D002** | 0 / 1 | 0 … 500 | ? | ? | ? |
| **—** | 0 / 1 | 0 … 1200 | ? | ? | ? |
| **—** | 0 / 1 | 0 … 1280 | ? | ? | ? |
| **word_D012** | 0 / 1 | 0 … 14000 | ? | ? | ? |
| **word_C78A** | 0 / 1 | 200 … 6000 | ? | ? | ? |
| **word_D094** | 0 / 1 | 2731 … 4051 | ? | ? | ? |
| **word_D092** | 0 / 1 | 700 … 2002 | ? | ? | ? |
| **word_D1E6** | 0 / 1 | 0 … 20000 | ? | ? | ? |
| **word_D1F6** | 0 / 1 | 500 … 6000 | ? | ? | ? |
| **word_D202** | 0 / 1 | 1000 … 3000 | ? | ? | ? |
| **word_C590** | 0 / 1 | 0 … 90 | ? | ? | ? |
| **word_C6B6** | 0 / 1 | 0 … 10000 | ? | ? | ? |
| **—** | 0 / 1 | -5500 … -4490 | ? | ? | ? |
| **word_C3EC** | 0 / 1 | 700 … 850 | ? | ? | ? |
| **word_D3D4** | 0 / 1 | 0 … 8000 | ? | ? | ? |
| **word_C7B8** | 0 / 1 | 2000 … 13000 | ? | ? | ? |
| **word_D556** | 0 / 1 | 0 … 14000 | ? | ? | ? |
| **word_D578** | 0 / 1 | 0 … 1923 | ? | ? | ? |
| **word_D590** | 0 / 1 | 0 … 7000 | ? | ? | ? |
| **—** | 0 / 1 | 100 … 500 | ? | ? | ? |

---

## 4. Courbes 1-D — table exhaustive (182)

`ID` = handle (`word_xxxx`), c’est **l’identifiant de stockage**. `EA` = adresse logique dans le
Datensatz. Les valeurs sont données dans l’ordre des points de l’axe.

**Nom explicite** : `Loi <grandeur d’entrée> → sortie`. Quand la sortie n’est pas identifiée,
c’est écrit tel quel — **aucun nom inventé**.

> ⚠ `—` dans la colonne « consommateur » signifie *non établi*, **pas « non consommée »**.

| ID | EA | nom explicite | n | axe | axe en °C | valeurs | sortie observée | consommateur (si établi) |
|---|---|---|---|---|---|---|---|---|
| `14C8` | `0xE2A16` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 5 | 6667 → 28333 | — | 0, 5000, 10000, 10000, 0 | 0 … 10000 | — |
| `14CC` | `0xE2AC4` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 5 | 8333 → 31667 | — | 10000, 10000, 10000, 10000, 10000 | 10000 … 10000 | — |
| `14D4` | `0xE2F52` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 5 | 2901 → 3731 | +17.0 C … +100.0 C | 13000, 13000, 11000, 8000, 7000 | 7000 … 13000 | — |
| `14DA` | `0xE2FB2` | **Loi** non identifiée → *sortie non identifiée* | 2 | 485 → 970 | — | 600, 1200 | 600 … 1200 | — |
| `14E8` | `0xE3000` | **Loi** non identifiée → *sortie non identifiée* | 2 | 0 → 788 | — | 0, 700 | 0 … 700 | — |
| `14F2` | `0xE302A` | **Loi** non identifiée → *sortie non identifiée* | 4 | 20 → 1003 | — | 500, 500, 2500, 2500 | 500 … 2500 | — |
| `14FC` | `0xE3076` | **Loi** non identifiée → *sortie non identifiée* | 16 | 32 → 1023 | — | 11731, 9751, 8791, 7831, 7383, 6841, 6349, 6137, … (16 pts) | 2849 … 11731 | — |
| `1506` | `0xE30EC` | **Loi** non identifiée → *sortie non identifiée* | 16 | 10 → 991 | — | 3731, 4121, 4441, 4761, 5061, 5281, 5481, 5781, … (16 pts) | 3731 … 11381 | — |
| `1512` | `0xE316E` | **Loi** non identifiée → *sortie non identifiée* | 2 | 51 → 972 | — | 667, 20667 | 667 … 20667 | — |
| `151E` | `0xE31B8` | **Loi** non identifiée → *sortie non identifiée* | 4 | 20 → 1003 | — | 0, 0, 1000, 1000 | 0 … 1000 | — |
| `152C` | `0xE3218` | **Loi** non identifiée → *sortie non identifiée* | 2 | 0 → 1023 | — | 0, 5000 | 0 … 5000 | — |
| `1536` | `0xE325C` | **Loi** non identifiée → *sortie non identifiée* | 4 | 102 → 922 | — | 0, 0, 15000, 15000 | 0 … 15000 | — |
| `154E` | `0xE3444` | **Loi** non identifiée → *sortie non identifiée* | 10 | 32 → 969 | — | 3931, 3731, 3531, 3331, 3131, 2931, 2731, 2531, … (10 pts) | 2331 … 3931 | — |
| `1558` | `0xE34A8` | **Loi** non identifiée → *sortie non identifiée* | 4 | 20 → 1023 | — | 133, 133, 2500, 2500 | 133 … 2500 | — |
| `1560` | `0xE34CE` | **Loi** Régime moteur → *sortie non identifiée* | 6 | 0 → 5000 | — | 4000, 4000, 3000, 3000, 2000, 1000 | 1000 … 4000 | — |
| `1564` | `0xE34F6` | **Loi** non identifiée → *sortie non identifiée* | 12 | 192 → 1064 | — | 55, 185, 388, 697, 1088, 1629, 2225, 2980, … (12 pts) | 55 … 7739 | — |
| `156E` | `0xE3548` | **Loi** non identifiée → *sortie non identifiée* | 16 | 40 → 962 | — | 4031, 3831, 3631, 3531, 3431, 3331, 3231, 3131, … (16 pts) | 2331 … 4031 | — |
| `1578` | `0xE35C4` | **Loi** non identifiée → *sortie non identifiée* | 2 | 59 → 328 | — | 0, 10000 | 0 … 10000 | — |
| `158E` | `0xE3646` | **Loi** non identifiée → *sortie non identifiée* | 2 | 102 → 691 | — | 0, 10000 | 0 … 10000 | — |
| `159C` | `0xE3694` | **Loi** non identifiée → *sortie non identifiée* | 2 | 2 → 4 | — | 0, 0 | 0 … 0 | — |
| `15A6` | `0xE36D8` | **Loi** non identifiée → *sortie non identifiée* | 6 | 0 → 1023 | — | 0, 1000, 2000, 3000, 4000, 4999 | 0 … 4999 | — |
| `15AA` | `0xE3700` | **Loi** non identifiée → *sortie non identifiée* | 6 | 0 → 1023 | — | 0, 1000, 2000, 3000, 4000, 4999 | 0 … 4999 | — |
| `15BA` | `0xE3780` | **Loi** non identifiée → *sortie non identifiée* | 2 | 2 → 4 | — | 0, 0 | 0 … 0 | — |
| `15C4` | `0xE37C4` | **Loi** non identifiée → *sortie non identifiée* | 2 | 2 → 4 | — | 0, 0 | 0 … 0 | — |
| `15CE` | `0xE3808` | **Loi** non identifiée → *sortie non identifiée* | 2 | 57 → 340 | — | 1000, 6000 | 1000 … 6000 | — |
| `15D4` | `0xE3820` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 4 | 2431 → 3031 | -30.0 C … +30.0 C | 12000, 10000, 8000, 1800 | 1800 … 12000 | — |
| `15D8` | `0xE3842` | **Loi** non identifiée → *sortie non identifiée* | 24 | 42 → 1002 | — | 4032, 3932, 3831, 3731, 3631, 3531, 3431, 3331, … (24 pts) | 2331 … 4032 | — |
| `15E6` | `0xE3970` | **Loi** Régime moteur → *sortie non identifiée* | 6 | 1500 → 4000 | — | 15000, 15000, 15000, 15000, 15000, 15000 | 15000 … 15000 | — |
| `15E8` | `0xE398C` | **Loi** Régime moteur → *sortie non identifiée* | 6 | 1500 → 4000 | — | 0, 0, 0, 0, 0, 0 | 0 … 0 | — |
| `1608` | `0xE3C64` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 2 | 800 → 900 | — | 10000, 10000 | 10000 … 10000 | — |
| `160C` | `0xE3CF0` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 2 | 2531 → 2731 | -20.0 C … -0.0 C | 10000, 10000 | 10000 … 10000 | — |
| `1628` | `0xE3E3C` | **Loi** non identifiée → *sortie non identifiée* | 4 | 850 → 960 | — | 2050, 1700, 1350, 1000 | 1000 … 2050 | — |
| `162A` | `0xE3E50` | **Loi** Température air d’admission → *sortie non identifiée* | 4 | 2681 → 3231 | -5.0 C … +50.0 C | 12000, 1000, 1000, 12000 | 1000 … 12000 | — |
| `162C` | `0xE3E64` | **Loi** Régime moteur → *sortie non identifiée* | 6 | 800 → 2520 | — | 1600, 1800, 2600, 2600, 2600, 3000 | 1600 … 3000 | — |
| `162E` | `0xE3E80` | **Loi** Régime moteur → *sortie non identifiée* | 6 | 800 → 2520 | — | 400, 600, 600, 800, 1800, 2000 | 400 … 2000 | — |
| `1638` | `0xE3EF4` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 15 | 743 → 1100 | — | 11000, 11000, 11000, 11000, 11000, 11000, 11000, 11000, … (15 pts) | 10000 … 11000 | — |
| `163C` | `0xE3F3E` | **Loi** non identifiée → *sortie non identifiée* | 2 | 0 → 3000 | — | 10000, 10000 | 10000 … 10000 | — |
| `1640` | `0xE3F5C` | **Loi** non identifiée → *sortie non identifiée* | 5 | 6667 → 28333 | — | 0, 5000, 10000, 10000, 0 | 0 … 10000 | — |
| `170E` | `0xE42D4` | **Loi** non identifiée → *sortie non identifiée* | 4 | 0 → 180 | — | 2749, 31393, -31394, -2750 | -31394 … 31393 | — |
| `1800` | `0xE48DC` | **Loi** non identifiée → *sortie non identifiée* | 2 | 500 → 1000 | — | 1000, 1000 | 1000 … 1000 | — |
| `180A` | `0xE4900` | **Loi** non identifiée → *sortie non identifiée* | 10 | 400 → 5000 | — | 0, 200, 400, 600, 790, 1016, 1240, 1450, … (10 pts) | 0 … 2020 | — |
| `1814` | `0xE4954` | **Loi** non identifiée → *sortie non identifiée* | 2 | 0 → 250 | — | 1000, 9000 | 1000 … 9000 | — |
| `186C` | `0xE4B9A` | **Loi** non identifiée → *sortie non identifiée* | 16 | 32 → 1013 | — | 11381, 10381, 9441, 8781, 7881, 6921, 6441, 6181, … (16 pts) | 3731 … 11381 | — |
| `189E` | `0xE4CCC` | **Loi** *** ANOMALIE *** → *sortie non identifiée* | 8 | -32768 → -29408 | — | 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000 | 1000 … 1000 | — |
| `18A0` | `0xE4CF0` | **Loi** *** ANOMALIE *** → *sortie non identifiée* | 8 | -32768 → -29408 | — | 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200 | 1200 … 1200 | — |
| `18A2` | `0xE4D14` | **Loi** non identifiée → *sortie non identifiée* | 8 | 500 → 11000 | — | 117, 266, 367, 447, 542, 585, 643, 655 | 117 … 655 | — |
| `18A4` | `0xE4D38` | **Loi** non identifiée → *sortie non identifiée* | 8 | 500 → 11000 | — | 15, 27, 40, 58, 105, 130, 185, 260 | 15 … 260 | — |
| `18A6` | `0xE4D5C` | **Loi** Masse d’air par tour → *sortie non identifiée* | 8 | 100 → 11000 | — | 7000, 12500, 15000, 17000, 18232, 19000, 19756, 22000 | 7000 … 22000 | — |
| `18A8` | `0xE4D80` | **Loi** non identifiée → *sortie non identifiée* | 6 | 0 → 3000 | — | 3000, 3000, 1300, 1300, 1300, 1300 | 1300 … 3000 | — |
| `18AA` | `0xE4D9C` | **Loi** Masse d’air par tour → *sortie non identifiée* | 8 | 1300 → 11000 | — | 0, 0, 0, 15, 15, 15, 15, 15 | 0 … 15 | — |
| `18AC` | `0xE4DC0` | **Loi** Masse d’air par tour → *sortie non identifiée* | 8 | 1300 → 11000 | — | 0, 0, 0, 15, 15, 15, 15, 15 | 0 … 15 | — |
| `18AE` | `0xE4DE4` | **Loi** Masse d’air par tour → *sortie non identifiée* | 8 | 500 → 11000 | — | 254, 481, 627, 743, 874, 890, 890, 890 | 254 … 890 | — |
| `18B0` | `0xE4E08` | **Loi** Masse d’air par tour → *sortie non identifiée* | 8 | 500 → 11000 | — | 264, 491, 637, 753, 884, 900, 900, 900 | 264 … 900 | — |
| `18B4` | `0xE4E4A` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 8 | 0 → 5000 | — | 0, 0, 0, 0, 0, 0, 0, 0 | 0 … 0 | — |
| `18B6` | `0xE4E6E` | **Loi** non identifiée → *sortie non identifiée* | 8 | 2631 → 3331 | — | 10, 10, 10, 20, 30, 40, 40, 40 | 10 … 40 | — |
| `18B8` | `0xE4E92` | **Loi** Régime moteur → *sortie non identifiée* | 10 | 0 → 4500 | — | 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, … (10 pts) | 10000 … 10000 | — |
| `18BA` | `0xE4EBE` | **Loi** Régime moteur → *sortie non identifiée* | 10 | 0 → 4500 | — | 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, … (10 pts) | 10000 … 10000 | — |
| `18BC` | `0xE4EEA` | **Loi** Régime moteur → *sortie non identifiée* | 10 | 0 → 4500 | — | 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, … (10 pts) | 10000 … 10000 | — |
| `18BE` | `0xE4F16` | **Loi** Régime moteur → *sortie non identifiée* | 10 | 0 → 4500 | — | 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, … (10 pts) | 10000 … 10000 | — |
| `18C0` | `0xE4F42` | **Loi** Température (sonde non tranchée) → *sortie non identifiée* | 4 | 2431 → 3331 | — | 10000, 10000, 10000, 10000 | 10000 … 10000 | — |
| `18C4` | `0xE4FA4` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 8 | 0 → 20000 | — | 0, 5000, 6000, 7000, 8000, 9000, 11000, 20000 | 0 … 20000 | — |
| `18C6` | `0xE4FC8` | **Loi** non identifiée → *sortie non identifiée* | 8 | 0 → 7000 | — | 100, 100, 100, 100, 100, 100, 100, 100 | 100 … 100 | — |
| `18CE` | `0xE5080` | **Loi** non identifiée → *sortie non identifiée* | 4 | 500 → 6000 | — | -550, -230, -170, -150 | -550 … -150 | — |
| `18D4` | `0xE51E4` | **Loi** Température (sonde non tranchée) → *sortie non identifiée* | 8 | 2431 → 3331 | — | 300, 300, 300, 300, 300, 300, 300, 300 | 300 … 300 | — |
| `18D6` | `0xE5208` | **Loi** non identifiée → *sortie non identifiée* | 5 | 2731 → 2931 | — | 0, 100, 400, 1200, 2000 | 0 … 2000 | — |
| `18D8` | `0xE5220` | **Loi** non identifiée → *sortie non identifiée* | 5 | 2531 → 2931 | — | 10000, 1500, 0, 1100, 10000 | 0 … 10000 | — |
| `18DA` | `0xE5238` | **Loi** non identifiée → *sortie non identifiée* | 5 | 2531 → 2931 | — | 7000, 1200, 0, 900, 10000 | 0 … 10000 | — |
| `18DC` | `0xE5250` | **Loi** non identifiée → *sortie non identifiée* | 5 | -27269 → 32731 | — | 32700, 32700, 32700, 32700, 32700 | 32700 … 32700 | — |
| `18DE` | `0xE5268` | **Loi** non identifiée → *sortie non identifiée* | 5 | -27269 → 32731 | — | 32700, 32700, 32700, 32700, 32700 | 32700 … 32700 | — |
| `18E0` | `0xE5280` | **Loi** non identifiée → *sortie non identifiée* | 5 | -27269 → 32731 | — | 32700, 32700, 32700, 32700, 32700 | 32700 … 32700 | — |
| `18E2` | `0xE5298` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 8 | 100 → 3500 | — | 1, 1, 1, 1, 1, 1, 1, 1 | 1 … 1 | — |
| `18EA` | `0xE52CE` | **Loi** *** ANOMALIE *** → *sortie non identifiée* | 5 | -32768 → -29408 | — | 0, 300, 800, 1500, 2700 | 0 … 2700 | — |
| `18F4` | `0xE5350` | **Loi** non identifiée → *sortie non identifiée* | 5 | 2331 → 3031 | — | 3231, 3281, 3331, 3331, 3331 | 3231 … 3331 | — |
| `191A` | `0xE5F34` | **Loi** Régime moteur → *sortie non identifiée* | 12 | 970 → 3000 | — | 14000, 700, 700, 700, 700, 700, 700, 700, … (12 pts) | 700 … 14000 | — |
| `191C` | `0xE5F68` | **Loi** Régime moteur → *sortie non identifiée* | 12 | 990 → 3000 | — | 14000, 900, 900, 900, 900, 900, 900, 900, … (12 pts) | 900 … 14000 | — |
| `191E` | `0xE5F9C` | **Loi** Température d’échappement (probable) → *sortie non identifiée* | 2 | 5231 → 8231 | +250.0 C … +550.0 C | 100, 3200 | 100 … 3200 | — |
| `1922` | `0xE5FC0` | **Loi** Température d’échappement (probable) → *sortie non identifiée* | 2 | 5231 → 8731 | +250.0 C … +600.0 C | 100, 32767 | 100 … 32767 | — |
| `192A` | `0xE6038` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 5 | 0 → 1800 | — | 10000, 10000, 10000, 10000, 10000 | 10000 … 10000 | — |
| `192E` | `0xE6066` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 8 | 0 → 1800 | — | 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000 | 10000 … 10000 | — |
| `193E` | `0xE620A` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 5 | 0 → 1800 | — | 10000, 10000, 10000, 10000, 10000 | 10000 … 10000 | — |
| `1950` | `0xE639A` | **Loi** Température d’échappement (probable) → *sortie non identifiée* | 8 | 3731 → 8531 | +100.0 C … +580.0 C | 7231, 6531, 5881, 5331, 5181, 5131, 5131, 5131 | 5131 … 7231 | — |
| `1976` | `0xE657C` | **Loi** non identifiée → *sortie non identifiée* | 2 | 0 → 1 | — | 32767, 32767 | 32767 … 32767 | — |
| `1992` | `0xE68D0` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 8 | 2431 → 3531 | -30.0 C … +80.0 C | 18000, 18000, 18000, -25536, -25536, 0, 0, 0 | -25536 … 18000 | — |
| `1996` | `0xE6918` | **Loi** Régime moteur → *sortie non identifiée* | 6 | 0 → 2250 | — | 13000, 13000, 13000, 3200, 3200, 0 | 0 … 13000 | — |
| `199A` | `0xE6946` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 2 | 2531 → 2731 | -20.0 C … -0.0 C | 450, 450 | 450 … 450 | — |
| `199E` | `0xE69D6` | **Loi** Température air d’admission → *sortie non identifiée* | 8 | 2481 → 3131 | -25.0 C … +40.0 C | 10000, 10000, 10000, 10000, 6000, 0, 0, 0 | 0 … 10000 | — |
| `19A0` | `0xE69FA` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 8 | 700 → 1050 | — | 10000, 10000, 10000, 7500, 5000, 0, 0, 0 | 0 … 10000 | — |
| `19A2` | `0xE6A1E` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 6 | 2481 → 3731 | -25.0 C … +100.0 C | 3000, 1190, 1190, 1190, 1190, 1190 | 1190 … 3000 | — |
| `19A4` | `0xE6A3A` | **Loi** Température air d’admission → *sortie non identifiée* | 8 | 2431 → 3331 | -30.0 C … +60.0 C | 0, 0, 0, 0, 0, 0, 0, 0 | 0 … 0 | — |
| `19A6` | `0xE6A5E` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 2 | 800 → 900 | — | 0, 0 | 0 … 0 | — |
| `19A8` | `0xE6A6A` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 8 | 2481 → 3531 | -25.0 C … +80.0 C | 15000, 15000, 10000, 10000, 10000, 10000, 5000, 0 | 0 … 15000 | — |
| `19AA` | `0xE6A8E` | **Loi** Température carburant → *sortie non identifiée* | 6 | 3271 → 3931 | +54.0 C … +120.0 C | 0, 2800, 4200, 6500, 10000, 21000 | 0 … 21000 | — |
| `19AC` | `0xE6AAA` | **Loi** Température air d’admission → *sortie non identifiée* | 8 | 2381 → 2931 | -35.0 C … +20.0 C | 10000, 10000, 10000, 10000, 10000, 10000, 5000, 0 | 0 … 10000 | — |
| `19AE` | `0xE6ACE` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 8 | 800 → 1500 | — | 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000 | 10000 … 10000 | — |
| `19B0` | `0xE6AF2` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 8 | 2481 → 3431 | -25.0 C … +70.0 C | 14000, 20000, 10000, 10000, 10000, 10000, 10000, 0 | 0 … 20000 | — |
| `19B2` | `0xE6B16` | **Loi** Température carburant → *sortie non identifiée* | 2 | 2531 → 2731 | -20.0 C … -0.0 C | 10000, 10000 | 10000 … 10000 | — |
| `19B4` | `0xE6B22` | **Loi** Rapport cyclique (RCO) → *sortie non identifiée* | 8 | 297 → 593 | — | 4884, 4000, 2900, 2300, 1750, 1450, 1100, 1050 | 1050 … 4884 | — |
| `19B6` | `0xE6B46` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 2 | 800 → 900 | — | 0, 0 | 0 … 0 | — |
| `19B8` | `0xE6B52` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 12 | 2731 → 3771 | -0.0 C … +104.0 C | 0, 0, 0, 0, 0, 1000, 1000, 1000, … (12 pts) | 0 … 1000 | — |
| `19BA` | `0xE6B86` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 2 | 0 → 1800 | — | 0, 0 | 0 … 0 | — |
| `19BC` | `0xE6B92` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 2 | 2231 → 4231 | -50.0 C … +150.0 C | 1000, 1000 | 1000 … 1000 | — |
| `19BE` | `0xE6B9E` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 8 | 2481 → 3431 | -25.0 C … +70.0 C | 30000, 30000, 21000, 18000, 15500, 11000, 5000, 0 | 0 … 30000 | — |
| `19C0` | `0xE6BC2` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 8 | 2481 → 3531 | -25.0 C … +80.0 C | 10000, 10000, 10000, 10000, 10000, 8400, 5000, 0 | 0 … 10000 | — |
| `19C2` | `0xE6BE6` | **Loi** Température carburant → *sortie non identifiée* | 6 | 3271 → 3931 | +54.0 C … +120.0 C | 0, 2800, 4200, 6500, 10000, 21000 | 0 … 21000 | — |
| `19C8` | `0xE6C10` | **Loi** Régime moteur → *sortie non identifiée* | 8 | 1000 → 4500 | — | -1500, -1500, -1000, 0, 0, 0, 0, 0 | -1500 … 0 | — |
| `19CA` | `0xE6C34` | **Loi** Régime moteur → *sortie non identifiée* | 8 | 1000 → 4500 | — | 6500, 6500, 7200, 8000, 9000, 9000, 9000, 9000 | 6500 … 9000 | — |
| `19CC` | `0xE6C58` | **Loi** Régime moteur → *sortie non identifiée* | 8 | 1000 → 4500 | — | 6200, 6200, 6800, 7500, 8000, 8000, 8000, 8000 | 6200 … 8000 | — |
| `19CE` | `0xE6C7C` | **Loi** Régime moteur → *sortie non identifiée* | 12 | 1000 → 4500 | — | 10000, 11200, 12500, 13650, 14450, 15400, 15600, 15400, … (12 pts) | 10000 … 15600 | — |
| `19D0` | `0xE6CB0` | **Loi** Régime moteur → *sortie non identifiée* | 8 | 1000 → 4500 | — | 50, 50, 50, 25, 1, 1, 1, 1 | 1 … 50 | — |
| `19D8` | `0xE6DBC` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 6 | 2231 → 4231 | -50.0 C … +150.0 C | 0, 0, 0, 0, 0, 0 | 0 … 0 | — |
| `19F6` | `0xE6E6C` | **Loi** Régime moteur → *sortie non identifiée* | 2 | 612 → 5506 | — | 0, 0 | 0 … 0 | — |
| `19FE` | `0xE6F4A` | **Loi** Température air d’admission → *sortie non identifiée* | 6 | 2231 → 3731 | -50.0 C … +100.0 C | 10000, 10000, 10000, 9400, 9000, 7000 | 7000 … 10000 | — |
| `1A08` | `0xE6F96` | **Loi** Régime moteur → *sortie non identifiée* | 8 | 0 → 5500 | — | 9500, 9500, 9500, 9500, 9000, 7500, 7000, 7000 | 7000 … 9500 | — |
| `1A0A` | `0xE6FBA` | **Loi** Régime moteur → *sortie non identifiée* | 8 | 0 → 5000 | — | 500, 500, 500, 500, 500, 500, 500, 500 | 500 … 500 | — |
| `1A0C` | `0xE6FDE` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 10 | 2481 → 3231 | -25.0 C … +50.0 C | 0, 0, 0, 0, 0, 0, 0, 0, … (10 pts) | 0 … 0 | — |
| `1A0E` | `0xE700A` | **Loi** Régime moteur → *sortie non identifiée* | 10 | 800 → 3000 | — | 2800, 3600, 3800, 2000, 2000, 2000, 2000, 1500, … (10 pts) | 0 … 3800 | — |
| `1A10` | `0xE7036` | **Loi** Régime moteur → *sortie non identifiée* | 10 | 800 → 3000 | — | 3200, 4000, 4200, 2400, 2400, 2400, 2400, 1800, … (10 pts) | 400 … 4200 | — |
| `1A1A` | `0xE7440` | **Loi** Température air d’admission → *sortie non identifiée* | 2 | 2537 → 3731 | -19.4 C … +100.0 C | 10000, 10000 | 10000 … 10000 | — |
| `1A1E` | `0xE75C8` | **Loi** Régime moteur → *sortie non identifiée* | 10 | 250 → 4500 | — | 2800, 2800, 2800, 2800, 300, 0, 0, 0, … (10 pts) | 0 … 2800 | — |
| `1A20` | `0xE75F4` | **Loi** Régime moteur → *sortie non identifiée* | 10 | 250 → 4500 | — | 3200, 3200, 3200, 3200, 700, 400, 400, 400, … (10 pts) | 400 … 3200 | — |
| `1A4E` | `0xE7CF8` | **Loi** Température air d’admission → *sortie non identifiée* | 2 | 2537 → 2736 | -19.4 C … +0.5 C | 10000, 10000 | 10000 … 10000 | — |
| `1A50` | `0xE7D04` | **Loi** non identifiée → *sortie non identifiée* | 12 | -5000 → 6000 | — | 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, … (12 pts) | 10000 … 10000 | — |
| `1A52` | `0xE7D38` | **Loi** non identifiée → *sortie non identifiée* | 2 | 626 → 700 | — | 10000, 10000 | 10000 … 10000 | — |
| `1A5A` | `0xE7E18` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 6 | 2481 → 2931 | -25.0 C … +20.0 C | 9898, 9898, 9898, 9898, 9898, 10000 | 9898 … 10000 | — |
| `1A62` | `0xE7E60` | **Loi** non identifiée → *sortie non identifiée* | 8 | 0 → 255 | — | 0, 0, 0, 0, 0, 0, 360, 360 | 0 … 360 | — |
| `1A66` | `0xE7EA6` | **Loi** non identifiée → *sortie non identifiée* | 5 | 0 → 255 | — | 0, 2500, 5000, 7500, 9961 | 0 … 9961 | — |
| `1A68` | `0xE7EBE` | **Loi** non identifiée → *sortie non identifiée* | 8 | 0 → 255 | — | 0, 0, 0, 0, 0, 0, 3000, 8000 | 0 … 8000 | — |
| `1A6A` | `0xE7EE2` | **Loi** non identifiée → *sortie non identifiée* | 8 | 0 → 224 | — | 0, 0, 0, 0, 0, 0, 136, 136 | 0 … 136 | — |
| `1A6C` | `0xE7F06` | **Loi** non identifiée → *sortie non identifiée* | 2 | 193 → 204 | — | 136, 255 | 136 … 255 | — |
| `1A6E` | `0xE7F12` | **Loi** non identifiée → *sortie non identifiée* | 2 | 181 → 204 | — | 0, 255 | 0 … 255 | — |
| `1A70` | `0xE7F1E` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 2 | 2251 → 4164 | -48.0 C … +143.2 C | 0, 255 | 0 … 255 | — |
| `1A7A` | `0xE7F44` | **Loi** non identifiée → *sortie non identifiée* | 5 | 0 → 12336 | — | 0, 0, 136, 187, 255 | 0 … 255 | — |
| `1A7C` | `0xE7F5C` | **Loi** non identifiée → *sortie non identifiée* | 5 | 0 → 14701 | — | 0, 0, 136, 187, 255 | 0 … 255 | — |
| `1A8A` | `0xE8084` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 6 | 2531 → 3381 | -20.0 C … +65.0 C | 1100, 1000, 900, 800, 780, 750 | 750 … 1100 | — |
| `1A8E` | `0xE816C` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 6 | 2551 → 3631 | -18.0 C … +90.0 C | 1100, 1100, 1000, 800, 800, 750 | 750 … 1100 | — |
| `1A92` | `0xE8188` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 6 | 2431 → 3731 | -30.0 C … +100.0 C | 32767, 32767, 32767, 32767, 32767, 32767 | 32767 … 32767 | — |
| `1AA0` | `0xE81E2` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 8 | 2431 → 3531 | -30.0 C … +80.0 C | 11200, 9000, 7990, 5160, 3300, 2530, 1390, 900 | 900 … 11200 | — |
| `1B28` | `0xE8386` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 2 | 2731 → 3731 | -0.0 C … +100.0 C | 1000, 1000 | 1000 … 1000 | — |
| `1B3E` | `0xE83F4` | **Loi** Régime moteur → *sortie non identifiée* | 19 | 0 → 5200 | — | 0, 3516, 3516, 4485, 5800, 6660, 7060, 7430, … (19 pts) | 0 … 7430 | — |
| `1B48` | `0xE87EE` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 6 | 1500 → 20000 | — | 0, 10000, 10000, 20496, 20496, 0 | 0 … 20496 | — |
| `1B4E` | `0xE88DA` | **Loi** non identifiée → *sortie non identifiée* | 6 | 2231 → 4231 | — | 0, 0, 0, 0, 0, 0 | 0 … 0 | — |
| `1B54` | `0xE8906` | **Loi** Régime moteur → *sortie non identifiée* | 15 | 635 → 4000 | — | 3516, 3516, 3516, 4485, 5800, 6660, 6400, 6350, … (15 pts) | 3516 … 6660 | — |
| `1B56` | `0xE8946` | **Loi** Régime moteur → *sortie non identifiée* | 15 | 635 → 4000 | — | 3516, 3516, 3516, 4485, 5800, 6660, 6400, 6350, … (15 pts) | 3516 … 6660 | — |
| `1B58` | `0xE8986` | **Loi** Régime moteur → *sortie non identifiée* | 15 | 635 → 4000 | — | 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000, … (15 pts) | 10000 … 10000 | — |
| `1B5A` | `0xE89C6` | **Loi** Régime moteur → *sortie non identifiée* | 12 | 0 → 5000 | — | 0, 3800, 3800, 3800, 3600, 3400, 3000, 2000, … (12 pts) | 0 … 3800 | — |
| `1B5C` | `0xE89FA` | **Loi** Régime moteur → *sortie non identifiée* | 2 | 635 → 680 | — | 10000, 10000 | 10000 … 10000 | — |
| `1B62` | `0xE8B04` | **Loi** Régime moteur → *sortie non identifiée* | 2 | 200 → 400 | — | 10000, 10000 | 10000 … 10000 | — |
| `1B64` | `0xE8B10` | **Loi** Régime moteur → *sortie non identifiée* | 15 | 635 → 4000 | — | 3516, 3516, 3516, 4485, 5800, 6660, 6400, 6350, … (15 pts) | 3516 … 6660 | — |
| `1BEC` | `0xE8E12` | **Loi** Grandeur de charge → *sortie non identifiée* | 4 | 0 → 5000 | — | 500, 500, 500, 500 | 500 … 500 | — |
| `1BF4` | `0xE8F74` | **Loi** Régime moteur → *sortie non identifiée* | 2 | 750 → 4000 | — | 0, 0 | 0 … 0 | — |
| `1C00` | `0xE9100` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 2 | -4267 → 17493 | — | 500, 9500 | 500 … 9500 | — |
| `1C06` | `0xE91B0` | **Loi** Régime moteur → *sortie non identifiée* | 6 | 0 → 4000 | — | 0, 6890, 10538, 12849, 12849, 9687 | 0 … 12849 | — |
| `1C08` | `0xE91CC` | **Loi** Régime moteur → *sortie non identifiée* | 2 | 750 → 4000 | — | 0, 0 | 0 … 0 | — |
| `1C0A` | `0xE91D8` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 2 | 2347 → 4067 | -38.4 C … +133.6 C | 500, 9500 | 500 … 9500 | — |
| `1C3C` | `0xE9354` | **Loi** Régime moteur → *sortie non identifiée* | 8 | 0 → 5000 | — | 8000, 8000, 8000, 8000, 110, 110, 110, 110 | 110 … 8000 | — |
| `1C5A` | `0xE93EE` | **Loi** Régime moteur → *sortie non identifiée* | 6 | 1300 → 2001 | — | 2300, 2700, 2700, 3500, 3500, 4000 | 2300 … 4000 | — |
| `1C5C` | `0xE940A` | **Loi** Régime moteur → *sortie non identifiée* | 6 | 1300 → 2001 | — | 965, 1340, 1340, 1760, 1760, 2500 | 965 … 2500 | — |
| `1C5E` | `0xE9426` | **Loi** Régime moteur → *sortie non identifiée* | 6 | 0 → 5000 | — | 10000, 10000, 10000, 10000, 10000, 10000 | 10000 … 10000 | — |
| `1C60` | `0xE9442` | **Loi** Régime moteur → *sortie non identifiée* | 6 | 1300 → 3501 | — | 720, 1000, 1000, 1700, 1700, 0 | 0 … 1700 | — |
| `1C90` | `0xE9626` | **Loi** non identifiée → *sortie non identifiée* | 2 | 1000 → 3000 | — | 0, 0 | 0 … 0 | — |
| `1C96` | `0xE9654` | **Loi** non identifiée → *sortie non identifiée* | 2 | 1000 → 3000 | — | 5000, 5000 | 5000 … 5000 | — |
| `1C9C` | `0xE970C` | **Loi** non identifiée → *sortie non identifiée* | 2 | 1000 → 2500 | — | 1000, 1000 | 1000 … 1000 | — |
| `1CA4` | `0xE9724` | **Loi** non identifiée → *sortie non identifiée* | 8 | 0 → 9000 | — | 0, 0, 3000, 5000, 6000, 8000, 9000, 10000 | 0 … 10000 | — |
| `1CAE` | `0xE9B4C` | **Loi** non identifiée → *sortie non identifiée* | 8 | -6000 → 8000 | — | 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000 | 10000 … 10000 | — |
| `1CB8` | `0xE9E72` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 8 | 2531 → 3931 | -20.0 C … +120.0 C | 10000, 10000, 10000, 10000, 10000, 10000, 10000, 10000 | 10000 … 10000 | — |
| `1DBA` | `0xEAFCA` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 2 | 2431 → 3331 | -30.0 C … +60.0 C | 0, 0 | 0 … 0 | — |
| `1DCC` | `0xEB6F2` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 16 | 1200 → 13500 | — | 40, 40, 20, 20, 35, 70, 102, 127, … (16 pts) | 20 … 148 | — |
| `1DCE` | `0xEB736` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 16 | 1200 → 13500 | — | 157, 120, 109, 109, 67, 70, 100, 130, … (16 pts) | 67 … 157 | — |
| `1DDA` | `0xEB9DA` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 2 | 2431 → 2531 | -30.0 C … -20.0 C | 0, 0 | 0 … 0 | — |
| `1DE8` | `0xEBA28` | **Loi** non identifiée → *sortie non identifiée* | 2 | 0 → 2000 | — | 10000, 10000 | 10000 … 10000 | — |
| `1DEA` | `0xEBA34` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 2 | 1190 → 1200 | — | 0, 0 | 0 … 0 | — |
| `1DF2` | `0xEBA58` | **Loi** Grandeur non identifiée → *sortie non identifiée* | 2 | 900 → 920 | — | 0, 0 | 0 … 0 | — |
| `1DF4` | `0xEBA64` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 2 | 2431 → 2831 | -30.0 C … +10.0 C | 10000, 10000 | 10000 … 10000 | — |
| `1DF8` | `0xEBA78` | **Loi** Température liquide de refroidissement → *sortie non identifiée* | 2 | 2731 → 4131 | -0.0 C … +140.0 C | 10000, 10000 | 10000 … 10000 | — |
| `1DFA` | `0xEBA84` | **Loi** non identifiée → *sortie non identifiée* | 2 | 4731 → 5731 | — | 10000, 10000 | 10000 … 10000 | — |
| `1E10` | `0xEBADA` | **Loi** non identifiée → *sortie non identifiée* | 6 | 3 → 30000 | — | 46, 58, 71, 80, 160, 6400 | 46 … 6400 | — |
| `1E12` | `0xEBAF6` | **Loi** non identifiée → *sortie non identifiée* | 6 | 1 → 240 | — | 80, 107, 320, 640, 32000, 32000 | 80 … 32000 | — |
| `1E14` | `0xEBB12` | **Loi** non identifiée → *sortie non identifiée* | 8 | 2 → 120 | — | 3, 7, 10, 16, 20, 30, 120, 240 | 3 … 240 | — |
| `1E26` | `0xEBBD0` | **Loi** Régime moteur → *sortie non identifiée* | 2 | 525 → 5355 | — | 8500, 8500 | 8500 … 8500 | — |
| `1E28` | `0xEBBDC` | **Loi** Température air d’admission → *sortie non identifiée* | 10 | 2231 → 4081 | -50.0 C … +135.0 C | 3521, 3521, 3521, 3521, 3486, 3461, 3436, 3411, … (10 pts) | 2331 … 3521 | — |
| `1E2A` | `0xEBC08` | **Loi** Régime moteur → *sortie non identifiée* | 2 | 525 → 5355 | — | 9500, 9500 | 9500 … 9500 | — |
| `1E2E` | `0xEBC38` | **Loi** Température air d’admission → *sortie non identifiée* | 3 | 2681 → 2832 | -5.0 C … +10.1 C | 3486, 3411, 2331 | 2331 … 3486 | — |

---

## 5. Cartes 2-D — table exhaustive (66)

> ⚠️ **CORRIGÉ À L'AUDIT (Étape 123, C2)** : le titre ci-dessus est **périmé**. Compte réel :
> **86 cartes à axes explicites** (scan par signature, toutes pointées par un handle) **+ 5 à
> identifier** = **91** (errata #57 du § 10). Liste à jour : `inventaire_cartes_2D_axes_v2.csv`.
> Les 20 cartes manquantes de la table ci-dessous : `0xE100A`…`0xE10BA` (8), `0xE12CE`, `0xE12E2`,
> `0xE13B0`, `0xE13C6`, `0xE2F6A`, `0xE2F8A`, `0xE5564`, `0xE5602`, `0xE6050`, `0xE6306`, `0xE6588`,
> `0xEBA20`.


**Nom explicite** : `CARTE <lignes> × <colonnes>`. La **sortie** est décrite par sa *magnitude*
observée (minimum et maximum de la grille), ce qui oriente sans affirmer.

> ⚠ **La colonne « consommateur » ne doit pas être mal lue.** Un `—` signifie *non établi par notre
> outil*, **PAS « non consommée »**. Les cartes sont lues par l’interpolateur à travers un handle
> passé en paramètre — motif que `outils/usage_handles.py` ne détecte pas encore. Leur non-consommation
> a d’ailleurs été **réfutée** dès l’étape 25.

| ID | EA | nom explicite de la carte | dim. | Y | X | magnitude de sortie | consommateur (si établi) |
|---|---|---|---|---|---|---|---|
| `1440` | `0xE12F6` | **CARTE Régime moteur × Grandeur non identifiée** | 2×2 | 600 → 800 | 0 → 4910 | 0 … 0 | — |
| `1442` | `0xE1E30` | **CARTE Régime moteur × Grandeur non identifiée** | 16×16 | 725 → 2650 | 0 → 4500 | 2250 … 12000 | — |
| `147C` | `0xE22B2` | **CARTE Régime moteur × Grandeur non identifiée** | 2×2 | 0 → 400 | 0 → 500 | 0 … 700 | — |
| `1482` | `0xE22F4` | **CARTE Régime moteur × non identifiée** | 2×2 | 0 → 1000 | 0 → 1200 | 0 … 4992 | — |
| `1484` | `0xE230C` | **CARTE Régime moteur × non identifiée** | 2×2 | 0 → 400 | 0 → 1280 | 0 … 600 | — |
| `1498` | `0xE23B4` | **CARTE Grandeur non identifiée × Grandeur non identifiée** | 16×20 | 1190 → 14000 | 0 → 14000 | 0 … 9610 | — |
| `14CA` | `0xE2A2E` | **CARTE Grandeur non identifiée × Grandeur non identifiée** | 8×7 | 2000 → 13000 | 200 → 6000 | 0 … 350 | — |
| `14CE` | `0xE2ADC` | **CARTE Régime moteur × Grandeur de charge** | 7×7 | 750 → 5000 | 500 → 10000 | -160 … 0 | — |
| `1542` | `0xE32AC` | **CARTE Régime moteur × Grandeur non identifiée** | 6×12 | 750 → 3500 | 400 → 2400 | 15000 … 15000 | — |
| `1544` | `0xE3368` | **CARTE Régime moteur × Grandeur non identifiée** | 6×12 | 750 → 3500 | 500 → 2400 | 0 … 0 | — |
| `15E2` | `0xE38D8` | **CARTE Régime moteur × Température air d’admission** | 2×6 | 1000 → 2000 | 2581 → 3331 | 10000 … 20500 | — |
| `15E4` | `0xE3908` | **CARTE Régime moteur × Température liquide de refroidissement** | 6×6 | 1000 → 2500 | 2531 → 3131 | 0 … 4200 | — |
| `15EA` | `0xE39A8` | **CARTE Grandeur non identifiée × Grandeur non identifiée** | 2×2 | 700 → 850 | 700 → 750 | 0 … 0 | — |
| `15EC` | `0xE39C0` | **CARTE Température air d’admission × Grandeur non identifiée** | 2×2 | 2531 → 3331 | 700 → 1000 | 10000 … 10000 | — |
| `15EE` | `0xE39D8` | **CARTE Grandeur non identifiée × non identifiée** | 10×10 | 2731 → 4051 | 700 → 2002 | 650 … 2280 | — |
| `15FC` | `0xE3B2C` | **CARTE Régime moteur × Grandeur non identifiée** | 6×6 | 1000 → 4000 | 1000 → 2200 | 4992 … 10750 | — |
| `1642` | `0xE3F74` | **CARTE Régime moteur × Grandeur non identifiée** | 6×6 | 800 → 2650 | 1000 → 4500 | -150 … 0 | — |
| `172E` | `0xE4356` | **CARTE Régime moteur × Rapport cyclique (RCO)** | 8×8 | 500 → 6000 | 0 → 508 | 1944 … 1944 | — |
| `18C8` | `0xE4FEC` | **CARTE non identifiée × non identifiée** | 8×6 | 0 → 20000 | 500 → 6000 | -400 … 870 | — |
| `18D0` | `0xE5094` | **CARTE Régime moteur × Grandeur non identifiée** | 8×8 | 0 → 5000 | 100 → 3500 | 0 … 0 | — |
| `18D2` | `0xE513C` | **CARTE non identifiée × non identifiée** | 8×8 | 1000 → 3000 | 0 → 90 | 1005 … 1459 | — |
| `18FC` | `0xE5450` | **CARTE Régime moteur × Grandeur de charge** | 10×5 | 800 → 3000 | 900 → 5000 | 0 … 0 | — |
| `18FE` | `0xE54DA` | **CARTE Régime moteur × Grandeur de charge** | 10×5 | 800 → 3000 | 900 → 5000 | 0 … 0 | — |
| `1930` | `0xE608A` | **CARTE Régime moteur × Grandeur de charge** | 6×6 | 0 → 5000 | 900 → 5000 | 10000 … 10000 | — |
| `1932` | `0xE60F2` | **CARTE Régime moteur × Grandeur de charge** | 6×6 | 0 → 5000 | 900 → 5000 | 10000 … 10000 | — |
| `193C` | `0xE61A2` | **CARTE Régime moteur × Grandeur de charge** | 6×6 | 0 → 5000 | 900 → 5000 | 10000 … 10000 | — |
| `1940` | `0xE6222` | **CARTE Régime moteur × Grandeur de charge** | 4×6 | 0 → 3000 | 400 → 2500 | 10000 … 10000 | — |
| `1942` | `0xE626E` | **CARTE Régime moteur × Grandeur de charge** | 4×6 | 0 → 3000 | 400 → 2500 | 10000 … 10000 | — |
| `1944` | `0xE62BA` | **CARTE Régime moteur × Grandeur de charge** | 4×6 | 0 → 3000 | 400 → 2500 | 10000 … 10000 | — |
| `1994` | `0xE68F4` | **CARTE Rapport cyclique (RCO) × Température liquide de refroidissement** | 2×4 | 673 → 678 | 2481 → 2721 | 0 … 1500 | — |
| `199C` | `0xE6952` | **CARTE Rapport cyclique (RCO) × non identifiée** | 8×6 | 255 → 678 | 3000 → 12000 | 74 … 120 | — |
| `19D6` | `0xE6D14` | **CARTE Régime moteur × non identifiée** | 8×8 | 500 → 5400 | 0 → 10000 | 0 … 0 | — |
| `19FC` | `0xE6E7E` | **CARTE Température air d’admission × Régime moteur** | 8×10 | 2531 → 3531 | 700 → 5012 | 3500 … 3500 | — |
| `1A14` | `0xE707A` | **CARTE Régime moteur × Grandeur non identifiée** | 16×10 | 800 → 5500 | 0 → 7000 | 2000 … 8000 | — |
| `1A16` | `0xE71F6` | **CARTE Grandeur non identifiée × Grandeur non identifiée** | 9×9 | 600 → 1024 | 0 → 4000 | 0 … 1000 | — |
| `1A18` | `0xE72C4` | **CARTE Régime moteur × Grandeur non identifiée** | 16×10 | 800 → 5500 | 0 → 7000 | 2650 … 8000 | — |
| `1A1C` | `0xE744C` | **CARTE Régime moteur × Grandeur non identifiée** | 16×10 | 800 → 5500 | 0 → 7000 | 1500 … 9000 | — |
| `1A44` | `0xE7828` | **CARTE Grandeur non identifiée × Régime moteur** | 10×10 | 600 → 1050 | 1000 → 5000 | 1000 … 2370 | — |
| `1A46` | `0xE7920` | **CARTE Grandeur non identifiée × Grandeur non identifiée** | 9×9 | 600 → 1000 | 0 → 7000 | -400 … 0 | — |
| `1A4A` | `0xE7A00` | **CARTE Régime moteur × Grandeur non identifiée** | 16×10 | 0 → 5500 | 0 → 7000 | 800 … 2200 | — |
| `1A4C` | `0xE7B7C` | **CARTE Régime moteur × Grandeur non identifiée** | 16×10 | 0 → 5500 | 0 → 7000 | 800 … 2200 | — |
| `1A54` | `0xE7D44` | **CARTE non identifiée × Régime moteur** | 6×6 | -5500 → -4490 | 1000 → 2200 | 0 … 50 | — |
| `1A56` | `0xE7DAC` | **CARTE Grandeur de charge × Régime moteur** | 6×6 | 0 → 6000 | 1000 → 2600 | 4830 … 5520 | — |
| `1A82` | `0xE7F7E` | **CARTE Régime moteur × Température carburant** | 8×4 | 800 → 4800 | 3601 → 3751 | 1500 … 7630 | — |
| `1A84` | `0xE8000` | **CARTE Régime moteur × Température carburant** | 8×6 | 800 → 4800 | 3051 → 3751 | 1500 … 7600 | — |
| `1A8C` | `0xE80A0` | **CARTE Régime moteur × Température liquide de refroidissement** | 8×10 | 100 → 1000 | 2481 → 3731 | 1300 … 12500 | — |
| `1B2A` | `0xE8392` | **CARTE Régime moteur × Température liquide de refroidissement** | 2×2 | 0 → 5000 | 2731 → 3731 | 10 … 10 | — |
| `1B40` | `0xE8444` | **CARTE Régime moteur × Quantité d’air mesurée par le débitmètre — abscisse de la smoke map** | 16×16 | 0 → 5200 | 3000 → 11500 | 0 … 7600 | — |
| `1B42` | `0xE868C` | **CARTE Température liquide de refroidissement × Grandeur non identifiée** | 6×6 | 2431 → 3831 | 0 → 18000 | 0 … 9230 | — |
| `1B44` | `0xE86F4` | **CARTE Régime moteur × Température liquide de refroidissement** | 10×9 | 0 → 1760 | 2431 → 3531 | 0 … 9230 | — |
| `1B46` | `0xE87D6` | **CARTE Régime moteur × non identifiée** | 2×2 | 200 → 620 | 700 → 850 | 8000 … 8000 | — |
| `1B4A` | `0xE880A` | **CARTE Régime moteur × Température liquide de refroidissement** | 6×6 | 1300 → 4000 | 3841 → 3951 | 0 … 7040 | — |
| `1B4C` | `0xE8872` | **CARTE Régime moteur × Quantité d’air mesurée par le débitmètre — abscisse de la smoke map** | 6×6 | 0 → 5000 | 0 → 10000 | 0 … 0 | — |
| `1B5E` | `0xE8A06` | **CARTE Régime moteur × non identifiée** | 10×10 | 0 → 5002 | 0 → 8000 | 0 … 250 | — |
| `1B66` | `0xE8B50` | **CARTE Régime moteur × non identifiée** | 8×6 | 0 → 5000 | 118 → 10000 | 0 … 8000 | — |
| `1B68` | `0xE8BD4` | **CARTE Régime moteur × non identifiée** | 8×6 | 0 → 5000 | 118 → 10000 | 0 … 8000 | — |
| `1BF2` | `0xE8ECC` | **CARTE Régime moteur × Grandeur de charge** | 8×8 | 0 → 4500 | 0 → 7000 | 0 … 75 | — |
| `1BF6` | `0xE8F80` | **CARTE Régime moteur × Température air d’admission** | 2×2 | 0 → 1600 | 2331 → 2731 | 0 … 0 | — |
| `1C92` | `0xE9632` | **CARTE Régime moteur × Grandeur de charge** | 2×2 | 650 → 1200 | 0 → 500 | 0 … 0 | — |
| `1C98` | `0xE9660` | **CARTE Régime moteur × non identifiée** | 8×8 | 200 → 4000 | 2000 → 13000 | 896 … 4850 | — |
| `1DB8` | `0xEAFB2` | **CARTE Régime moteur × Grandeur de charge** | 2×2 | 200 → 6000 | 0 → 3500 | 0 … 0 | — |
| `1DC4` | `0xEB3E2` | **CARTE Grandeur non identifiée × non identifiée** | 16×20 | 1190 → 14000 | 0 → 14000 | 0 … 9610 | — |
| `1DCA` | `0xEB6CE` | **CARTE Grandeur de charge × Grandeur non identifiée** | 2×4 | 0 → 10000 | 0 → 12000 | 10000 … 10000 | — |
| `1DD0` | `0xEB77A` | **CARTE Grandeur non identifiée × non identifiée** | 2×2 | 1200 → 14000 | 0 → 1923 | 0 … 0 | — |
| `1DDC` | `0xEB9E6` | **CARTE Grandeur non identifiée × non identifiée** | 2×2 | 6 → 40 | 0 → 7000 | 0 … 0 | — |
| `1E1A` | `0xEBB46` | **CARTE non identifiée × Température liquide de refroidissement** | 5×5 | 100 → 500 | 2431 → 3731 | 0 … 0 | — |

---

## 5 bis. Signification des axes — ce qui est prouvé, ce qui est supposé

> ### ⚠ Règle de prudence (correction de l’étape 56)
>
> **Une plage de valeurs ne prouve JAMAIS une grandeur.** 2 200 … 4 300 est aussi bien une
> température en K × 10 qu’une masse d’air en mg/tour × 10, ou un régime partiel. Les trois
> variables `word_C3D2`, `word_C3BA`, `word_C3B0` avaient été annotées « masse d’air par tour »
> **sur la seule foi de leur plage** : c’était faux (ERRATA 56).
>
> **Un axe n’est nommé que si la chaîne qui le produit est identifiée** — capteur → voie ADC →
> courbe → variable de travail. La plage ne sert qu’à **vérifier la vraisemblance**, jamais à
> conclure.

**Convention établie (fournie par l’utilisateur, et vérifiée par recoupement) : les températures sont
codées en KELVIN × 10.** Le contrôle est net : **2731 = 0 °C** et **3531 = 80 °C**.

**C’est cette convention qui donne son sens à toute une famille d’axes :**

| variable | plage d’axe | en Kelvin | **en °C** | grandeur | confiance |
|---|---|---|---|---|---|
| `word_C3D2` | 2231 … 4231 | 223.1 … 423.1 K | **-50.0 C … +150.0 C** | Température liquide de refroidissement | CONFIRMÉ utilisateur, 100 % |
| `word_C3BA` | 2231 … 4081 | 223.1 … 408.1 K | **-50.0 C … +135.0 C** | Température air d’admission | lu |
| `word_C3B0` | 2531 … 3931 | 253.1 … 393.1 K | **-20.0 C … +120.0 C** | Température carburant | CONFIRMÉ utilisateur |
| `word_C5A4` | 2431 … 3331 | 243.1 … 333.1 K | **-30.0 C … +60.0 C** | Température (sonde non tranchée) | inf |
| `word_C586` | 3731 … 8731 | 373.1 … 873.1 K | **+100.0 C … +600.0 C** | Température d’échappement (probable) | inf |

**Lecture** : −50…+150 °C pour le liquide de refroidissement, −50…+135 °C pour l’air d’admission,
−20…+120 °C pour le gasoil, +100…+600 °C pour l’échappement. Ce sont **exactement les plages
attendues** d’un moteur diesel, et elles **recoupent** les bornes annoncées par l’utilisateur
(−40…+120 °C pour les axes de température). Le recoupement est un **contrôle indépendant** : la
convention Kelvin × 10 n’a pas été choisie pour faire coïncider ces plages.

### ⚠ Deux échelles de température coexistent — précision importante

| famille de capteur | échelle | preuve |
|---|---|---|
| **CTN** (LDR, air, gasoil) | **Kelvin × 10** | 2731 = 0 °C et 3531 = 80 °C (utilisateur, vérifié) ; plages −50…+150 °C cohérentes |
| **thermocouple d’échappement** | **°C × 10** | la valeur de repli de la 2ᵉ EGT vaut **6231**, soit **623,1 °C** — lue °C × 10, c’est la valeur par défaut attendue ; la même loi monte à **11731 = 1173,1 °C**, ce qui est un maximum d’échappement réaliste |

**Les deux lectures ne peuvent pas être fusionnées** : en Kelvin × 10, la température LDR donnerait
233 °C à −40 °C, ce qui est absurde ; en °C × 10, la même valeur serait correcte mais la plage
−40…+120 °C des axes CTN deviendrait inatteignable. **Ce sont donc bien deux conventions distinctes,
une par famille de capteur** — et c’est cohérent avec le fait que la loi d’une CTN produit
naturellement des Kelvin alors qu’un thermocouple fournit des °C.

`word_C586` (axes 3731…8731) et `word_C5A4` (2431…3331) restent **d’échelle non tranchée** : les deux
lectures y sont données.

### Les autres axes

| variable | nom explicite | unité / échelle | confiance | note |
|---|---|---|---|---|
| `word_C42E` | Régime moteur | tr/min | lu | plage 0…6000, 91 axes — axe dominant du calculateur |
| `word_C3E6` | Quantité d’air mesurée par le débitmètre — abscisse de la smoke map | mg ×10 (500 mg = 5000 en flash) | CONFIRMÉ utilisateur, 100 % | vérifié : carte 0xE8444 = régime × C3E6, 16×16 |
| `word_C5A4` | Température (sonde non tranchée) | échelle non tranchée | inf | axes 2431…3331 → −30…+60 °C si K×10, ou 243…333 °C si °C×10 |
| `word_C6A2` | Grandeur de charge | 0…100 % (×100) | lu | plage 0…10000 ; presque toujours en X |
| `word_C3C2` | Rapport cyclique (RCO) | 0…1000 | inf | plage 0…678 — électrovannes / EGR / N75 |
| `word_C5A8` | Masse d’air par tour | mg ×10 | inf | axes 1300…11000 = 130…1100 mg/tour |
| `word_C7C2` | Grandeur non identifiée | ? | ? | plage très large 6…14000 |
| `word_C60A` | Grandeur non identifiée | ? | ? | plage étroite 600…1800 |
| `word_D004` | Grandeur non identifiée | ? | ? | plage 0…7000 |
| `word_C3EE` | Grandeur non identifiée | ? | ? | plage 0…4910 |
| `word_C60E` | Grandeur non identifiée | ? | ? | plage 0…7000 |
| `word_C3A8` | Grandeur non identifiée | ? | ? | plage 400…2400 |
| `word_C612` | Grandeur non identifiée | ? | ? | plage 700…2200 |
| `word_C77A` | Grandeur non identifiée | profil de limitation | inf | valeurs 0,5000,10000,10000,0 |
| `word_C562` | Grandeur non identifiée | ? | ? | plage 0…20000 |
| `word_D1F4` | Grandeur non identifiée | ? | ? | plage 0…5000 |
| `word_C68A` | Grandeur non identifiée | ? | ? |  |
| `word_C78A` | Grandeur non identifiée | ? | ? |  |
| `word_D012` | Grandeur non identifiée | ? | ? |  |
| `word_D002` | Grandeur non identifiée | ? | ? |  |
| `word_D006` | Grandeur non identifiée | ? | ? |  |
| `word_D094` | Grandeur non identifiée | ? | ? |  |
| `word_C63C` | Grandeur non identifiée | ? | ? |  |
| `word_C5BC` | *** ANOMALIE *** | axe négatif | ? | axe −32768…−29408 : alignement à vérifier |

---

## 5 ter. Boucles réellement comprises — schémas

*Chaque schéma ci-dessous correspond à du code lu, avec ses numéros de ligne dans les étapes
correspondantes. Ce qui n’est pas compris est écrit « manquant » et n’est pas dessiné.*


### Boucle A — Acquisition capteur → grandeur physique

Tout passe par une **tâche périodique** identifiée par un numéro (`0x302`, `0x308`, `0x318`…).
La chaîne est toujours la même :

```
   capteur            ADC                descripteur          COURBE 1-D
 (CTN, débitmètre) ──► voie n ──► [EA descripteur] ──► [EA courbe] ──► valeur
                          │            (0xE349C)          (0xE34A8)     physique
                          │                                              │
                          │                                              ▼
                          │                                    word_D0xx  (valeur brute + copie)
                          │                                              │
                          │                                              ▼
                          └──────────────► chemin de défaut (r3) ──► word_C3xx (copie de travail)
                                                                         │
                                                                         ▼
                                                              word_C9xx  (instantané du diagnostic)
                                                                         │
                                                                         ▼
                                                          cartes / courbes (axe = cette variable)
```

**Preuve de bout en bout (voie 6, air d'admission)** :
`0xE353C` (descripteur) → `0xE3548` (courbe 16 pts, 4031…2331) → `word_D06C` →
`word_C3BA` → `word_C904` → `word_D094`.
Ce chaînage est **établi** (étape 13) et c'est lui qui donne le sens de l'axe.

**Table complète : voir § 12.**

---

### Boucle B — Diagnostic : du seuil au défaut mémorisé

```
   grandeur mesurée (word_C3D2 = température LDR)
            │
            ▼
   instantané  word_C908  ◄── copie à chaque cycle (l. 153232)
            │
            ▼
   MONITEUR  ──►  word_CFD4 : 1 bit par moniteur (16 max)
            │        bit 0 = critère de DURÉE   (seuil n°2, [word_142A+6])
            │        bit 7 = critère de VALEUR  (seuil n°1, [word_142A+0])
            │
            │  inhibitions : byte_C2F5, byte_CFDC, word_C0BC
            │  inhibition globale : word_FD2E
            │  power latch : word_FD0C.15 GÈLE l'évaluation (l. 153175)
            ▼
   CONFIRMATION  sub_A1E9E
            │        and word_CFD4, r12
            │        décompte byte_CFC4   (anti-rebond)
            ▼
   word_CFD6  = DÉFAUT CONFIRMÉ  (1 bit par moniteur)
            │
            ▼
   mémoire des défauts  0xCAD0 : 96 × 4 octets  (+0 drapeau, +2 mot)
            │            byte_E466 = nombre mémorisé (0…7)
            │            0xE467 : 7 enregistrements × 22 octets
            ▼
   code transmis  0xCCB2 : 96 mots  →  descripteur au mot + 0x1C
            │                         bits 0-1 = classe, bit 2 = drapeau
            ▼
   services 0x04 (ajout/mise à jour) · 0x14 (compter + effacer) · 0x17 (lecture)
```

**Boucle de comptage, établie (l. 231394)** :

```
   pour les 96 entrées de 0xCAD0 :
        si bit 0 de l'entrée est posé  (= défaut PRÉSENT)
        alors lire [entrée + 0x1C], puis pour chaque bit haut à 1 :
                 incrémenter 0xC9F3 + n
   puis : 0xC9F3+n ≠ 0  ──►  poser le bit [word_1818 + n]
                             (word_1818 = 02 01 00 08 0F)
                             ──►  word_C548 bits 0,1,2  et  word_C54A bits 8,15
```

**Seuils réels du moniteur LDR** (`word_142A`, EA `0xE122C`) — et ils sont **parlant** une fois
les températures décodées :

| offset | valeur | lecture |
|---|---|---|
| `+0` | **3431** | **343,1 K = +70 °C** — seuil d'activation du moniteur |
| `+2` | 220 | 22 K d'incrément → borne **3651 = +92 °C** |
| `+4` | 100 | autorisation (≠ `0xFFFF`) |
| `+6` | 100 | 10 K — critère de durée |

**⇒ Le moniteur de température LDR s'active entre 70 °C et 92 °C : c'est le domaine du thermostat.
Un défaut n'est confirmé qu'à l'intérieur de cette fenêtre** — comportement exactement attendu d'un
diagnostic qui ne veut juger qu'à chaud.

---

### Boucle C — Surveillance à hystérésis et anti-rebond

```
   entrée commune  word_C5A8   (masse d'air par tour, mg ×10 ; axe 1300…11000)
            │
      ┌─────┴─────┐
      ▼           ▼
  courbe       courbe
  word_18AA    word_18AC        (les DEUX BORNES d'une fenêtre)
  borne basse  borne haute
      │           │
      └─────┬─────┘
            ▼
   comparé à  word_C596   (référence, avec valeur de repli word_CFF2)
            │
            ▼
   état courant dans  rl6 bit 1  /  byte_D6FC
            │
            ▼
   DÉCOMPTE  word_D6EE … word_D6FA   (7 compteurs)
            │   durée = [word_1474 + n]   (360, 60, 60, 325, 250 cycles)
            ▼
   à zéro ──► BASCULE de l'état  (orb / andb sur le bit)
   condition non tenue ──► compteur remis à 0  ⇒ il faut N cycles CONSÉCUTIFS
```

**⇒ Comparateur de Schmitt logiciel.** C'est un mécanisme **générique**, répliqué sept fois.

---

### Boucle D — Anti-falsification (et pourquoi il n'y a pas de checksum)

```
   valeur courante  word_C5B8   (PERSISTÉE en EEPROM)
            │
            ├──► historique 5 niveaux  C5D2, C5D4, C5D6, C5D8, C5DA
            │        (tourne à chaque mise à jour — l. 161143)
            │        PERSISTÉ en EEPROM  ⇒ survit à la coupure du contact
            │        │
            │        ▼
            │    moyenne  word_C5AE  (somme / 5, via sub_97DDC)
            │        ▼
            │    comparée à [word_18F2 + 0x14] = 120
            │
            └──► comparée à [word_18F2 + 0x38] = 2
                 comparée à [word_1474 + 0x06] = 325 ──► décompte word_D6FE ──► byte_C317
```

**Sept algorithmes de checksum ont été testés sans succès sur les 512 Ko.** La protection réelle est
cet **historique persistant** : on ne peut pas falsifier une valeur sans falsifier en même temps ses
cinq dernières valeurs et leur moyenne, ni sans franchir des seuils dont les valeurs sont dans le
**Datensatz** — donc hors de l'EEPROM.

---

### Boucle E — EEPROM : trois couches

```
   applicatif
      │
      ▼
   GESTIONNAIRE  0x94Axx … 0x94Cxx        redondance, rythme, options
      │  sub_94AE8  lecture avec consensus (vote à 3 copies)
      │  sub_94BB6  écriture triple
      │  sub_94BDC  gestionnaire (teste, décrémente, assainit)
      │  sub_94C6A  verrou à gâchette (mémorise le PREMIER code)
      ▼
   PILOTE  sub_A0002 (l. 149775)          handle = [2 bits page][14 bits offset]
      │  descripteur 12 octets @ 0x0BA6 ; table de 64 mots @ 0x0FE00
      │  adresse = 0xE5CE + offset
      ▼
   IMAGE  RAM  0xE5CE  (1 Ko)            13 groupes
```

**Confinement prouvé** : les **74 occurrences** de la constante `0xE5CE` sont **toutes** entre les
lignes **149820 et 152100**. Aucune fonction applicative ne calcule jamais une adresse EEPROM.

---

### Boucle F — Codage de variante : le Datensatz propose, le CAN choisit

```
   Lexia / Diagbox
        │  code le BSI
        ▼
   trame CAN ──► word_FD38 · word_FD38+1 · word_FD7A · word_FD7A+1 · word_FD7C
        │
        ▼
   [word_18B2 + 0x12]   masque de variante, bits 2 à 7
        │   bit 2 : inconditionnel
        │   bit 3 : armé par word_FD38
        │   bit 4 : armé par word_FD38+1
        │   bit 5 : armé par word_FD7A
        │   bit 6 : armé par word_FD7A+1
        │   bit 7 : armé par word_FD7C
        ▼
   groupe de quatre valeurs du Datensatz : +0x14, +0x16, +0x18, +0x1A
        │
        ▼
   word_D1BE · word_D1BA · word_D1B2 · word_C5A8     (+ byte_C308 = « chargées »)
```

**Et la moitié EEPROM** : quatre enregistrements à tag, à valeur unique **écrite en triple copie**,
sélectionnés par le masque `byte_F80D`, persistés par la commande `0x0B`.

**Limite** : le lien entre ces drapeaux et **le régulateur, la clim, BVM/BVA** n'est **pas** établi.
La correspondance « bit ↔ option » est dans la **couche absente**.

---

### Boucle G — Chaîne d'injection : ce qui est établi, et ce qui manque

**Statut honnête : la chaîne complète n'est PAS établie.** Voici les fragments qui le sont.

```
   [ÉTABLI]  couple demandé / limiteur
             cartes de couple : X = RÉGIME, résultat en mm³ × 100
             limiteur principal appliqué EN DERNIER
                    │
                    ▼
   [FRAGMENT] masse d'air par tour  word_C5A8  (130…1100 mg, axe mg ×10)
              et débit d'air  word_C3E6  (mg/s)
                    │
                    ▼
   [MANQUANT]  calcul de la masse de carburant (mm³ par tour)
               → conversion mm³ → durée d'injection
               → avance / pilotage des injecteurs
```

**Ce que l'on sait avec certitude :**
- les **cartes de couple** existent et sont **consommées** (leur non-consommation a été réfutée) ;
- leur **X est le régime** (`word_C42E`, 0…6000) et leur **résultat est en mm³ × 100** ;
- le **limiteur principal est appliqué en dernier** ;
- les grandeurs internes se lisent en `0…10000` = `0…100 %`.

**Ce que l'on ne sait pas** : la **conversion mm³ → temps d'ouverture des injecteurs**, l'**avance**,
et le **pilotage final**. Ces éléments sont dans la **couche absente** (bloc `0xFC000-0xFFFFF`, programme
autonome) — et **on ne les inventera pas**.


---

## 5 quater. Entrées et sorties : chaîne complète

*Source : `capteurs_ADC_et_chaines_de_mesure.csv` (étape 13), complété par les étapes 47 à 55.*

| tâche | voie | capteur | courbe | n | sortie | variable brute (RAM) | copie de travail | défaut | note |
|---|---|---|---|---|---|---|---|---|---|
| `0x302` | 0 | **non identifié** | `0xE35D6` | 10 | 0…1540 | `C3D0` | `` | 0x5C | non instruite a l'etape 13 |
| `0x304` | 1 | **non identifié** | `0xE35D6` | 10 | 0…1540 | `word_D06E` | `word_C3CE` | 0x6C | non instruite a l'etape 13 |
| `0x306` | 2 | **Voie ratiométrique redondante (0,5-4,5 V)** | `0xE302A` | 4 | 500…2500 | `word_D044+word_D046` | `word_C362` | 0xA2/0xA0 | paire redondante - controle croise, pas de conversion physique |
| `0x308` | 3 | **Débitmètre (2 éléments)** | `0xE34A8` | 4 | 133…2500 | `word_D060+word_D062` | `word_C378` | 0x96 | DEBITMETRE element A - loi 0xE34A8 (133..2500 mg/coup) - valeur physique C3B2/C902 |
| `0x30A` | 4 | **Débitmètre (2 éléments)** | `0xE34F6` | 12 | 55…7739 | `word_D066 (+D068/D06A)` | `word_C3B6+word_C37A` | 0xAC | DEBITMETRE 2e vue - loi cubique 0xE34F6 (55..7739 mg/s) - C3B6=C37A moyenne brute bornee |
| `0x30C` | 5 | **Pression d’environnement (mbar)** | `0xE2FB2` | 2 | 600…1200 | `word_D03A` | `word_C360` | 0xA4/0xA6 | PRESSION D'ENVIRONNEMENT 600-1200 mbar -> C38E/C60A/C940, axe des cartes 15EA/15EE |
| `0x30E` | 6 | **Température air d’admission (CTN)** | `0xE3548` | 16 | 4031…2331 | `word_D06C` | `word_C3BA -> C904` | non identifie | AIR D'ADMISSION (prouve : C3BA -> C904 -> D094, axe de la carte de densite 15EE) |
| `0x310` | 7 | **Température gasoil (CTN)** | `0xE3444` | 10 | 3931…2331 | `word_D05E` | `word_C3B0 -> C900` | non identifie | GASOIL (probable : courbes sollicitees > +60 C, repli carburant tiede) |
| `0x312` | 8 | **Température d’échappement (thermocouple)** | `0xE3076` | 16 | 11731…2849 | `word_D048` | `word_C366 -> word_C394` | 0x82/0x80 | EGT mesuree - loi decroissante, remplacement 96 C |
| `0x314` | 9 | **Température d’échappement (thermocouple)** | `0xE30EC` | 16 | 3731…11381 | `word_D04A` | `word_C368` | 0x88/0x86 | 2e EGT - le repli 623,1 C est la preuve logicielle du cas "une seule sonde" |
| `0x318` | 11 | **Température LDR (CTN)** | `0xE3842` | 24 | 4032…2331 | `word_D084` | `word_C3D2 -> C908` | non identifie | LIQUIDE DE REFROIDISSEMENT (tres probable : 24 pts, 31 courbes, repli froid) |
| `0x31A` | 12 | **non identifié** | `0xE35D6` | 10 | 0…1540 | `word_D080` | `word_C388` | n.d. | non instruite a l'etape 13 |
| `0x31C` | 13 | **non identifié** | `0xE35D6` | 10 | 0…1540 | `word_D082` | `word_C38A` | n.d. | non instruite a l'etape 13 |
| `0x31E` | 14 | **non identifié** | `0xE316E` | 2 | 667…20667 | `word_D04C` | `word_C36A` | 0x9E/0x9A | non instruite a l'etape 13 |
| `0x320` | 15 | **non identifié** | `0xE3808` | 2 | 1000…6000 | `word_C370` | `` | 0x6E | non instruite a l'etape 13 |
| `0x322` | 16 | **non identifié** | `0xE3000` | 2 | 0…700 | `word_D042+word_D040` | `` | 0x140/0x142 | non instruite a l'etape 13 |
| `0x326` | 18 | **Voie de plausibilité (pas de conversion)** | `0xE31B8` | 4 | 0…1000 | `word_D04E+word_D050` | `word_C36C` | 0x20A/0x208 | FENETRE DE VALIDITE SEULE - aucune conversion physique du signal |
| `0x406` | 6 | **non identifié** | `0xE3694` | 2 | 0…0 | `word_D072` | `word_C382 -> C906` | 0x58 | non instruite a l'etape 13 |
| `0x408` | 8 | **non identifié** | `0xE3218` | 2 | 0…5000 | `word_D054` | `word_C36E` | non identifie | conversion brut -> mV (0..5000) - PAS de conversion en mbar |
| `0x602` | 2 | **Voie de plausibilité (pas de conversion)** | `0xE325C` | 4 | 0…15000 | `word_D056` | `word_C3CA -> C372` | 0x40 | FENETRE DE VALIDITE - pas de conversion physique |
| `0x606` | 6 | **Sonde CTN (2ᵉ gamme)** | `0xE3436` | 10 | 3931…2331 | `word_D05A` | `word_C374 -> word_C3AE` | 0x42 | 2e gamme de la MEME CTN que D05E (double gamme) |

### Où chaque grandeur est traitée

| grandeur | variable de travail | instantané diagnostic | handle d’axe | consommateur identifié |
|---|---|---|---|---|
| Régime moteur | `word_C42E` | — | 91 axes | cartes de couple, surveillance |
| Température LDR | `word_C3D2` | **`word_C908`** | 36 axes | **`sub_A1E9E`** (moniteurs) |
| Air d’admission | `word_C3BA` | `word_C904` | 15 axes | chaîne 0x30E |
| Gasoil | `word_C3B0` | `word_C900` | 5 axes | chaîne 0x310 |
| Masse d’air par tour | `word_C5A8` | — | 5 axes | **`sub_A5C92`** (hystérésis) |
| Charge / % | `word_C6A2` | — | 17 axes | cartes (abscisse) |
| Débit d’air | `word_C3E6` | — | 2 axes | cartes (axe mg/s ×10) |

### Sorties

| sortie | organe | état de la connaissance |
|---|---|---|
| EGR | électrovanne, commande en **RCO** | seuils = plafonds ; axe `word_C3C2` (0…678) **probable** |
| N75 (suralimentation) | électrovanne, **RCO** | idem — **pas d’unité physique** |
| Injection | injecteurs | **chaîne non établie** (voir boucle G) |
| Post-injection / FAP | injecteurs | **non localisé** |
| Voyant / mode dégradé | combiné, via CAN | `word_CFD6` alimente la mémoire ; le lien vers le voyant est **dans la couche absente** |

---

## 5 quinquies. ★ Les cartes sans axes, et les tables vérifiées à la main

**Constat de l’utilisateur, confirmé par le binaire : il existe des cartes SANS AUCUN AXE.**
Le gabarit `[tagY][nY][axeY][tagX][nX][axeX][grille]` n’est pas universel : certaines grilles sont
stockées **nues**, leurs axes étant définis **ailleurs** (autre structure, ou axes fixes du
calculateur). Le décodeur les rejetait — c’est l’origine des grands trous de la § 6 bis.

### ★ Le mécanisme qui explique « des axes partout dans le code »

**Un handle peut viser l’intérieur d’une structure.** Vérifié sur la toute première courbe :

```
EA 0xE100A : [tag 0xC42E][n = 8][axe 8 mots : 200 … 4000][valeurs 8 mots]   -> 36 octets
EA 0xE101E : = 0xE100A + 4 + 2x8  -> DÉBUT DES VALEURS, l’axe est sauté
```

Le handle `0x1400` pointe sur la structure entière ; le handle `0x1402` pointe **exactement sur
les valeurs**. Un consommateur qui a déjà l’axe dans ses registres lit les valeurs sans relire
l’axe ; un autre peut ne lire que les bornes. **Sur les 1 304 handles, 19 pointent ainsi sur des
valeurs ou des grilles, et non sur un début de structure.**

**⇒ C’est la réponse à ton observation** : ce ne sont pas des axes orphelins, ce sont des
**adresses de sous-parties**. Le même bloc de calibration est découpé en plusieurs handles selon
ce que chaque routine a besoin de lire.

### Les quatre tables vérifiées — toutes confirmées

| table | EA | contenu | ton indication | verdict |
|---|---|---|---|---|
| **Ralenti = f(T LDR)** | `0xE8084` | 1-D, 6 pts : axe **2531, 2631, 2731, 2931, 3231, 3381** (−20, −10, 0, +20, +50, +65 °C) → **1100, 1000, 900, 800, 780, 750 tr/min** | « 1100 à 750 tr/min pour −20 °C (2531) à +50 °C (3231) » | **EXACT au point près** |
| **Préchauffage bougies** | `0xE86F4` | 2-D **10 × 9** : Y = régime (0…1760), X = T LDR (**−30 … +80 °C**). Grille : `9230 8160 4210 1280 0 0 0 0 0` **identique à tous les régimes** | « table (RPM, Temp_ldr), sans doute un temps de préchauffage » | **CONFIRMÉ et précisé** : décroît de **9 230** à −30 °C jusqu’à **0 au-dessus de +10 °C** ⇒ c’est un **temps en millisecondes**, 9,23 s à froid, nul à chaud. Les lignes régime 0 et 1760 sont nulles : hors plage de fonctionnement |
| **Correction de démarrage** | `0xE80A0` | 2-D **8 × 10** : Y = régime (100…1000), X = T LDR (−25 … +100 °C). Grille **1300 … 12500**, décroissante avec la température, maximale à froid (12 500 vers 400-500 tr/min) | « carte de correction pour le démarrage (rôle exact ?) » | **Rôle précisé** : c’est un **enrichissement de démarrage à froid** — il vaut 3 à 10 fois plus à −25 °C qu’à +100 °C. L’**unité reste ouverte** (magnitude seule) |
| **Table 6 × 6 à `0x6882A`** | `0xE882A` | 6 × 6 = 36 mots, **sans en-tête** : `0 640 896 1920 3584 6912` / `0 512 768 1792 3584 7040` / `0 384 640 1536 3456 7040` / `0 128 384 1280 3200 7040` / `0 128 512 1408 3200 7040` / `0 128 384 1408 3328 6912` | « une autre table en 6x6 (rôle ?) » | **Confirmée comme grille nue** : aucun axe propre. Sa voisine immédiate (`0xE8872`) porte **Y = régime 0…5000** et **X = C3E6 0…10000**. Les valeurs croissent en ligne et en colonne, avec un plafond ~7040 ⇒ **table de limitation**, pas une correction. **Rôle exact non établi** |

### ★ La smoke map est retrouvée — et elle valide C3E6

| EA | dim. | Y | X | grille | lecture |
|---|---|---|---|---|---|
| **`0xE8444`** | **16 × 16** | régime 0…5200 | **`C3E6` 3000…11500 = 300…1150 mg** | 0 … 7600 | **la smoke map** : quantité de carburant admissible en fonction du régime et de la **masse d’air mesurée par le débitmètre** |
| `0xE8872` | 6 × 6 | régime 0…5000 | `C3E6` 0…10000 | **0 … 0** | second emplacement de smoke map, **grille entièrement nulle** ⇒ non utilisée dans cette calibration |

**⇒ Ta définition de `C3E6` est donc vérifiée par le binaire lui-même** : c’est bien l’abscisse de la
smoke map. Et l’emplacement vacant à `0xE8872` montre que le calculateur garde une **seconde smoke
map désactivée** — utile à savoir avant de « corriger » quoi que ce soit.

### ★ `C3B0` = température carburant : **exactement deux cartes**, comme tu l’annonçais

Balayage exhaustif de tout le Datensatz : **seules deux cartes 2-D utilisent `0xC3B0`**.

| EA | dim. | Y | X | grille |
|---|---|---|---|---|
| `0xE7F7E` | 8 × 4 | régime 800…4800 | **T carburant 3601…3751** (+87 … +102 °C) | 1500 … 7630 |
| `0xE8000` | 8 × 6 | régime 800…4800 | **T carburant 3051…3751** (+32 … +102 °C) | 1500 … 7600 |

**Deux cartes de limitation dont la seule variable est la température carburant, et elles ne
couvrent que le carburant chaud** (+32 °C à +102 °C). Ta lecture est confirmée.

### Le décompte réel des cartes 2-D

Le balayage à **tout alignement** (et non au seul début de bloc) trouve :

| catégorie | nombre |
|---|---|
| cartes 2-D à en-tête complet | **72** |
| dont **grille entièrement nulle** (emplacement vacant) | 13 |
| cartes **plates sans axes** (§ 6 bis) | 19 |

*(le décodeur d’origine en comptait 66 : il testait la 1-D avant la 2-D et, sur une carte 2-D,
l’axe Y a la forme d’une courbe 1-D valide — il s’arrêtait donc avant de voir la carte.)*

**Liste intégrale des 72 cartes : voir `cartes_2D_toutes_avec_axes.csv`.**

### Et ton hypothèse sur les correcteurs PI / PID

**Elle est cohérente avec ce qu’on observe, et je la retiens comme piste principale :**

- les **364 blocs de 3 mots** (§ 6 bis) sont numériquement compatibles avec des **triplets de
  coefficients** (gain, limite d’intégrale, constante de temps) ;
- les **94 paires de mots** avec des couples (Kp, Ki) ;
- les axes nus, sans carte, correspondent à des **points de rupture d’interpolation** pour des
  gains qui varient avec le régime ou la charge ;
- et cela expliquerait pourquoi la recherche de constantes en dur a échoué partout dans le code
  (constantes de vitesse = 0, immédiats 240/245/250 écartés) : **le calculateur relit ses
  paramètres au lieu de les coder.**

> ⚠ **Statut : hypothèse forte, pas fait établi.** Rien dans le code visible ne nomme encore un
> correcteur. Ce qui est établi, c’est que les triplets et les paires existent en grand nombre, et
> que leur disposition est **régulière** — deux propriétés que des paramètres de régulation
> expliqueraient bien.

---

## 6. Paramètres scalaires et blocs réservés

**Blocs réservés** (`0xFFFE` + zéros, 32 octets) : **7 emplacements libres** dans le Datensatz —
le constructeur a prévu de la place pour des tables supplémentaires selon la variante.

| ID | EA |
|---|---|
| `17C4` | `0xE45BA` |
| `17CE` | `0xE465A` |
| `17D0` | `0xE467A` |
| `17D2` | `0xE469A` |
| `17D4` | `0xE46BA` |
| `17EC` | `0xE483A` |
| `17EE` | `0xE485A` |

**Sentinelles identifiées** :

| sentinelle | position | sens proposé |
|---|---|---|
| `0xFFFE` | **premier mot** d’un bloc | **bloc sans variable** — emplacement non affecté |
| `0xC300` | **fin** de chaque bloc réservé ; aussi `[word_1474+0x08]` et `[word_142A+0x22]` | **« pas de valeur » / case vide** |
| `0xFF00` | avant `0xC300` dans les blocs réservés | second marqueur de fin |

> **Conséquence** : la valeur `0xC300`, qui revenait à plusieurs endroits et que j’avais notée comme
> « anomalie à instruire », est très probablement une **sentinelle d’absence de valeur** et non une
> constante physique. Les champs qui la contiennent doivent être lus comme **vides**, pas comme
> « −15 616 ».

**Paramètres scalaires** (bloc de 2 octets) : 91. Le bloc ne contient qu’une valeur ; le premier mot
**est donc la valeur elle-même**, pas une adresse de variable.

---

## 6 bis. Les tables oubliées — recherche systématique

**Question posée : reste-t-il des tables que l’on aurait manquées ?** Quatre vérifications
indépendantes, reproductibles par `python3 outils/tables_oubliees.py`.

### 1. Couverture : **97,9 %** des octets sont atteints par un handle

Sur la fenêtre `0xE1000-0xEC000` (45 056 octets), **44 088 sont couverts** par une structure
décodée. Il ne reste que **deux trous** :

| trou | taille | contenu | lecture |
|---|---|---|---|
| `0xE1000-0xE100A` | 10 o | `0a 1d 0c 1d 0e 1d 10 1d 12 1d` | **cinq handles en clair** : `0x1D0A, 0x1D0C, 0x1D0E, 0x1D10, 0x1D12`. Petite **table de renvoi** placée juste avant la première structure. Les mêmes octets existent aussi à `0xE0FFA`. |
| `0xEBC42-0xEC000` | 958 o | `9e 0d 53 0d 1b 09` puis remplissage `0xC3` | **fin du Datensatz** : 3 mots décroissants (3486, 3411, 2329) puis remplissage jusqu’à `0xEC000`. |

**⇒ Conclusion nette : il n’existe pas de grande table hors pointeurs.** Le Datensatz est
intégralement adressé. Les « oubliées » ne sont donc pas des octets perdus, mais des **structures
dont on n’a pas décodé la disposition interne** — c’est l’objet des points suivants.

### 2. Typologie des **1 056 blocs sans en-tête 1-D**

C’est le vrai gisement : 1 056 blocs (27 854 octets) n’ont **aucun en-tête** au sens du gabarit
`[variable][n][axe][valeurs]`. Voici ce qu’ils contiennent réellement :

| type interne | blocs | octets | lecture |
|---|---|---|---|

**Trois constats :**

- **364 blocs de 6 octets = 3 mots** : c’est le gabarit le plus fréquent après les courbes. Ce sont
  vraisemblablement des **triplets de paramètres liés** (seuil bas / seuil haut / temporisation),
  cohérent avec les moniteurs décodés à l’étape 43 — **mais ce n’est pas prouvé bloc par bloc**.
- **32 blocs sont des axes autonomes** (`[tag][n][n valeurs]`), dont **6 avec un tag inconnu** — les
  vraies oubliées ici sont ces six tags.
- **468 blocs restent non classés**, mais **24 230 octets seulement** : la médiane est de 2 octets.
  L’essentiel de ce « non classé » est donc une masse de **scalaires isolés**, pas des tables.

### 3. ★ 19 cartes 2-D **sans axes** — de vraies tables passées inaperçues

Le décodeur exigeait le gabarit `[tagY][nY][axeY][tagX][nX][axeX][grille]`. Or **il existe des
cartes stockées à plat, sans aucun axe** — elles étaient donc rejetées. La trame correcte se
retrouve par **minimisation de la discontinuité** entre cellules voisines : sur les cartes déjà
décodées, la méthode retrouve la bonne largeur **17 fois sur 25** (les échecs sont les grilles
8×8, trop petites pour être discriminées).

| EA | taille | mots | trame | lissage | plage | verdict |
|---|---|---|---|---|---|---|
| `0xE9848` | 512 o | 256 | 16 × 16 | 417.1 | 2500 … 13500 | **grille plausible** |
| `0xEB1E2` | 512 o | 256 | 16 × 16 | 78.0 | 427 … 2304 | **grille plausible** |
| `0xEB792` | 512 o | 256 | 16 × 16 | 18.6 | 45 … 510 | **grille plausible** |
| `0xE2B62` | 504 o | 252 | 18 × 14 | 14.0 | 0 … 200 | **grille plausible** |
| `0xE5634` | 384 o | 192 | 16 × 12 | 217.0 | 59861 … 64877 | **grille plausible** |
| `0xE57B4` | 384 o | 192 | 16 × 12 | 130.7 | 61355 … 64575 | **grille plausible** |
| `0xE5DB4` | 384 o | 192 | 16 × 12 | 1598.8 | 0 … 65236 | **suspect (trame douteuse)** |
| `0xE65C4` | 336 o | 168 | 14 × 12 | 54.8 | 1050 … 2200 | **grille plausible** |
| `0xE6714` | 336 o | 168 | 14 × 12 | 60.5 | 990 … 2150 | **grille plausible** |
| `0xE94FE` | 256 o | 128 | 8 × 16 | 61.8 | 0 … 800 | **grille plausible** |
| `0xE9748` | 256 o | 128 | 8 × 16 | 13.2 | 128 … 512 | **grille plausible** |
| `0xE9C70` | 256 o | 128 | 8 × 16 | 258.6 | 6000 … 13500 | **grille plausible** |
| `0xE9D72` | 256 o | 128 | 8 × 16 | 0.0 | 0 … 0 | **uniforme (bloc rempli)** |
| `0xE9F96` | 256 o | 128 | 8 × 16 | 1.1 | 40 … 60 | **grille plausible** |
| `0xEA558` | 256 o | 128 | 8 × 16 | 7.5 | 0 … 171 | **grille plausible** |
| `0xEA658` | 256 o | 128 | 8 × 16 | 0.0 | 1280 … 1280 | **uniforme (bloc rempli)** |
| `0xEA758` | 256 o | 128 | 8 × 16 | 11.8 | 0 … 256 | **grille plausible** |
| `0xEAA60` | 256 o | 128 | 8 × 16 | 91.8 | 800 … 3000 | **grille plausible** |
| `0xEAB60` | 256 o | 128 | 8 × 16 | 0.0 | 0 … 0 | **uniforme (bloc rempli)** |
| `0xEAC60` | 256 o | 128 | 8 × 16 | 0.0 | 0 … 0 | **uniforme (bloc rempli)** |
| `0xEAD60` | 256 o | 128 | 8 × 16 | 74.8 | 0 … 1665 | **grille plausible** |
| `0xEAE60` | 256 o | 128 | 8 × 16 | 34.5 | 0 … 1000 | **grille plausible** |
| `0xE3BE4` | 128 o | 64 | 8 × 8 | 833.7 | 500 … 9500 | **suspect (trame douteuse)** |
| `0xE3C70` | 128 o | 64 | 8 × 8 | 359.1 | 500 … 6000 | **grille plausible** |
| `0xE3DB6` | 128 o | 64 | 8 × 8 | 359.1 | 500 … 6000 | **grille plausible** |

**Vérification visuelle** : `0xE5634` lu en 16×12 donne une surface parfaitement lisse et monotone
(≈ 64 000 en haut à gauche, ≈ 60 000 en bas à droite, soit **−1 300 à −5 500 en complément à deux**) ;
`0xEB792` lu en 16×16 monte de 45 à 510 avec des paliers francs. **Ce sont bien des cartes.**

**Signal structurel fort** : ces blocs sont **contigus et régulièrement espacés** —
`0xE5634, 0xE57B4, 0xE5934, 0xE5AB4, 0xE5C34, 0xE5DB4` sont **à 0x180 d’intervalle** (six cartes de
384 o à la suite), et `0xEA558, 0xEA658, 0xEA758, 0xEAB60, 0xEAC60, 0xEAD60, 0xEAE60` **à 0x100**
(sept cartes de 256 o). Un remplissage régulier de ce type ne se produit pas par hasard : c’est une
**famille de cartes rangée par usage**, exactement comme l’étape 55 l’a montré pour les blocs
adressés par handle.

> ⚠ **Prudence sur quatre d’entre elles** : `0xE9D72`, `0xEA658`, `0xEAB60`, `0xEAC60` sont
> **uniformes** (une seule valeur) — ce sont des **blocs remplis**, pas des cartes exploitables.
> `0xE5DB4` et `0xE3BE4` ont une trame douteuse (lissage > 500) : **non retenues**.

**⇒ Le décompte des cartes du catalogue passe de 66 à 66 + 19 = 85**, sous réserve de validation
par le code consommateur.

*Sorties : `etat_couverture.csv`, `typologie_blocs_sans_entete.csv`, `cartes_plates_sans_axes.csv`,
`duplication_datensatz.csv`.*

---

## 7. Blocs de paramètres identifiés par leur usage dans le code

| handle | EA | taille | champ | rôle établi | preuve |
|---|---|---|---|---|---|
| `word_142A` | `0xE122C` | 10 | `+0` | seuil n°1 du moniteur | l. 153179 |
| | | | `+2` | incrément → borne haute | l. 153180 |
| | | | `+4` | autorisation (`0xFFFF` = inhibé) | l. 153183 |
| | | | `+6` | seuil n°2 (critère de durée) | l. 153314 |
| `word_1474` | `0xE226E` | 34 | `+0x00` | **durée de confirmation** 360 cycles | l. 155411 |
| | | | `+0x02` | 60 cycles | l. 155760 |
| | | | `+0x04` | 60 cycles (partagé par 4 états) | l. 155516 |
| | | | `+0x06` | 325 cycles | l. 156049 |
| | | | `+0x1A` | **250 cycles** (chargé dans `word_D6FA`) | l. 156042 |
| `word_18B2` | `0xE4E2C` | | `+0x12` | **masque de variante, bits 2 à 7** | l. 155300 |
| | | | `+0x14…+0x1A` | 4 valeurs de variante → `word_D1BE/BА/B2`, **`word_C5A8`** | l. 155358 |
| `word_18F2` | `0xE5316` | 58 | `+0x14` | 120 — comparé à `word_C5AE` (moyenne) | l. 162157 |
| | | | `+0x38` | 2 — comparé à `word_C5B8` | l. 162350 |
| `word_1818` | `0xE4962` | 6 | — | **numéros de bits : 2, 1, 0, 8, 15** | l. 153197 |
| `word_18AA` | `0xE4D9C` | 36 | — | borne basse sur `word_C5A8`, axe 1300…11000 | étape 50 |
| `word_18AC` | `0xE4DC0` | 72 | — | borne haute, puis 2ᵉ entrée (axe 500…11000) | étape 50 |

---

## 7 bis. ★★ La bibliothèque d’accès à la calibration — et les correcteurs

**C’est l’avancée majeure : le code visible ne lit jamais la calibration directement. Il appelle
une bibliothèque, et cette bibliothèque est dans la couche absente.** On ne connaît donc pas son
corps — mais **ses sites d’appel, ses arguments et ses effets sont parfaitement lisibles.**

### L’idiome de lecture

```
mov  r4, word_1474      ; r4 <- valeur du pointeur de la table 0xE1400
mov  r5, [r4]           ; lecture dans la structure de calibration
```

Le handle `0x14xx` **est** l’offset de l’entrée de pointeur (`0xE0000 + h`), et la valeur lue est
l’**offset de la structure** dans la même page. Un seul mécanisme, deux additions — d’où la
simplicité du modèle et la régularité observée partout.

### L’API de la couche absente

| routine | appels | rôle établi | signature |
|---|---|---|---|
| **`unk_1D36`** | **168** | **interpolation 1-D** | `(r12 = handle, r13 = x)` → **r4 = y** |
| **`unk_1D50`** | **72** | **interpolation 2-D** | `(r12 = handle, r13 = x, r14 = y)` → **r4** |
| **`unk_1D6C`** | **44** | interpolation 1-D **avec destination mémoire** et **mémorisation de l’axe** | `(r12 = dest, r13 = x, r14 = handle)` → écrit dans `[r12]` |
| **`unk_1D7E`** | **54** | même chose **sans nouvelle variable** : réutilise l’axe déjà chargé | `(r12 = dest, r13 = handle)` → **r4** |
| **`word_1D94`** | **64** | interpolation entre **deux bases fournies par pointeurs** (cœur du calcul) | `(r12, r13 = bases, r14 = handle)` |
| `word_1DA8` | 14 | non identifié | — |
| **`word_1DDA`** | **35** | **pas de régulation** — voir ci-dessous | `(r12 = mode, r13 = état, r14 = cible)` → **r4 = nouvel état**, drapeau en `USR0` |

**338 sites d’appel** au total, **203 courbes distinctes** réellement interpolées.

### ★ Pourquoi des axes apparaissent « partout, sans carte »

L’enchaînement est écrit noir sur blanc dans le code :

```
mov  r12, r0            ; r0 = pointeur de ZONE DE TRAVAIL
mov  r13, word_C91C     ; x = régime
mov  r14, word_1604     ; handle de la 1re courbe
calls 0, unk_1D6C       ; l’axe est chargé et MÉMORISÉ dans [r0]
mov  r12, r0
mov  r13, word_1602     ; handle de la 2e courbe
calls 0, unk_1D7E       ; réutilise l’axe déjà en place
mov  r12, r0
mov  r13, word_1600     ; handle de la 3e courbe
calls 0, unk_1D7E       ; encore le même axe
```

**⇒ Une série de courbes partage un axe chargé une seule fois dans une zone de travail.** C’est
la réponse complète au constat « des axes sans map » : ce ne sont ni des axes orphelins ni des
cartes sans axes — ce sont des **axes mis en cache**, consommés par plusieurs courbes successives.
Et cela **valide** l’existence des 19 grilles nues de la § 6 bis : leurs axes sont dans une zone
de travail, pas à côté de la grille.

### ★★ Les correcteurs : `word_1DDA` est le primitif de régulation

Les **35 sites** d’appel suivent tous le **même patron**, sans exception dans l’échantillon :

```
mov  r12, <mode>            ; #0, #2710h (=10000), ou un registre
mov  r13, word_X            ; r13 = VALEUR PRÉCÉDENTE (l’état persistant)
mov  r14, <cible>           ; la consigne du pas courant
calls 0, word_1DDA
mov  word_X, r4             ; réécriture de l’état
bmov word_FD00.n, USR0      ; USR0 remonte saturation / signe
```

**Un état persistant, une cible, un mode, un indicateur de saturation** : c’est la signature
d’un **pas d’intégration / limiteur de pente / filtre du premier ordre**. Chaque boucle possède
son propre mot d’état.

### ★★★ Une chaîne de régulation complète, décodée (EA `0xAC65E`)

```
mov  r12, word_19D0         ; courbe de calibration
mov  r13, [r0+#4]           ; entrée mesurée — SELECTIONNÉE PAR UN OCTET DE CALIBRATION
calls 0, unk_1D36           ; r4 = CONSIGNE interpolée
mov  MDL, #2710h            ; /10000  ->  échelle 0…100 %
div  r8
mov  r13, word_D836         ; état précédent
mov  r14, r8               ; consigne du pas
calls 0, word_1DDA          ; PAS DE RÉGULATION
mov  word_D836, r4          ; nouvel état
```

Puis, immédiatement après, une **seconde courbe** `word_19C8` est interpolée **contre la même
entrée** et son résultat publié en `word_D2EE`, l’état en `word_D2F0`.

**⇒ C’est un canal de régulation complet : entrée → courbe → mise à l’échelle → pas de régulation
→ sortie.** Et le choix de l’entrée est fait par `[word_141E + 0x23]`, **un octet de calibration** :
c’est-à-dire que **la source de la boucle est elle-même calibrée**.

### ★★ Un filtre à coefficient calibré (EA `0xACD4A`)

```
mov  r12, word_19F6         ; courbe de calibration
mov  r13, word_C91C         ; x = RÉGIME
calls 0, unk_1D36           ; r4 = coefficient K(régime)
mov  r5, word_C940          ; valeur précédente
add  r5, word_D854          ; + entrée
add  r5, r4                 ; + K(régime)
ashr r5, #1                 ; / 2
mov  word_C940, r5          ; stockage
```

**`y[n] = ( y[n−1] + u[n] + K(régime) ) / 2`** : un **filtre récursif du premier ordre dont le
coefficient est une courbe de calibration interpolée sur le régime.** C’est exactement « un
traitement qui lit dans la zone de calibration » — et il est entièrement décodé.

### Bilan de la chasse

| question | réponse |
|---|---|
| le code lit-il la calibration ? | **oui, via 338 sites d’appel** à 4 interpolateurs |
| combien de courbes sont réellement utilisées ? | **203** |
| y a-t-il des correcteurs ? | **oui** : 35 boucles à état persistant via `word_1DDA` |
| un PID complet est-il visible ? | **non** — le **pas** est dans la couche absente ; la **chaîne** qui l’entoure est décodée |
| des valeurs en dur dans le code ? | **quasi aucune** : les gains sont des courbes, l’échelle est `#2710h`, et jusqu’au **choix de l’entrée** est un octet de calibration |

**⇒ Ton hypothèse était la bonne** : le calculateur relit ses paramètres au lieu de les coder.
Ce n’est plus une conjecture de méthode, c’est **observé sur 338 sites**.

### Les grandeurs d’entrée les plus interpolées

| variable | interpolations | lecture |
|---|---|---|
| **`word_C91C`** | **62** | **copie de travail du régime moteur** (120 axes, 0…6000) — variable indépendante dominante |
| `word_C908` | 23 | température LDR (instantané diagnostic) |
| `word_C940` | 13 | copie de `word_C60A` (0…1800) |
| `word_C904` | 12 | air d’admission |
| `word_C5A8` | 4 | masse d’air par tour |
| `word_C68A` | 3 | non identifiée |

---

## 8. EEPROM — tout ce qui est établi

### 8.1 Trois couches

```
applicatif  →  gestionnaire 0x94Axx-0x94Cxx  →  pilote sub_A0002  →  image 0xE5CE
               redondance, rythme, options      page + offset          (RAM)
```

**Confinement prouvé** : les **74 occurrences** de la constante `0xE5CE` sont **toutes** situées entre
les lignes **149820 et 152100**. **Aucune fonction applicative ne calcule jamais une adresse EEPROM.**
⇒ tout champ EEPROM est atteignable par un handle du descripteur `0x0BA6`, donc présent dans
l’inventaire des 1 304 handles.

### 8.2 Le pilote `sub_A0002` (l. 149775)

- `cmd > 0x29` rejeté ; descripteur de 12 octets à `0x0BA6` ; type 1 → `sub_A09E4`, type 4 → `sub_A0B72`
- **handle = `[2 bits page][14 bits offset]`** ; page dans une table de 64 mots à `0x0FE00`
- **adresse = `0xE5CE + offset`** ; codage : `[word_BBE+0xE5CE] & mask == 0` ⇒ `| 0x8000`
- **20 appelants**, en 4 familles (§ 8.5)

### 8.3 Le magasin interne `sub_95E78` (l. 128999-129403)

| table | adresses RAM | pas | taille | nombre |
|---|---|---|---|---|
| **A** | `0xF819`, `0xF821`, `0xF829` | 8 | 8 octets | 3 |
| **B** | `0xF831`, `0xF835`, `0xF839` | 4 | 4 octets | 3 |

- sélection par **`byte_F842`** (0/1/2), table B autorisée par **`byte_F83C & 2`**
- pointeur publié dans **`word_C18A`** ; le **premier octet de l’enregistrement sert de commande** `sub_A0002`
- écriture **temporisée** : seuil **35** unités sur `word_F91C`, avec correction de rebouclage `−1`
- **`byte_C8F5`** = drapeau d’activité du magasin

### 8.4 Les quatre enregistrements de configuration persistante `0xF7ED…0xF815`

| enreg. | tag | valeur | commande | bit de `byte_F80D` |
|---|---|---|---|---|
| n°1 | `0xF7ED` | 1 mot **×3** | `0x0C` | bit 0 |
| n°2 | `0xF7F5` | 1 mot **×3** | `0x0C` | bit 1 |
| n°3 | `0xF7FC` | 1 octet **×3** | `0x0D` | bit 2 |
| n°4 | `0xF800` | 1 octet **×3** (compteur) | — | bit 7 |

- **`byte_F80D`** = masque des éléments **en attente d’écriture** ; **`byte_F80E`** = élément courant ;
  **`word_C186`** = pointeur sur le tampon ; **`word_C124`** = horodatage
- les **20 écritures** de `byte_F80D` sont **toutes entre les lignes 127179 et 128305** : un seul sous-système
- **seul effacement de bits d’option du code visible** : l. 127204-127222, `andb …, #9Fh` sur les **bits 5 et 6**
  de l’enregistrement n°3, **dans les trois copies**, conditionné par la nullité du compteur `0xF800`
- compteur `0xF800` décrémenté par **tranches de 62 500** (accumulateur 32 bits `word_F808/F80A`)

### 8.5 Les 20 appelants de `sub_A0002`, en quatre familles

| famille | sites | contenu persisté |
|---|---|---|
| **F1** configuration à triple redondance | l. 127438 (`0x0B`), 127491 (`0x0C`), 127544 (`0x0D`) | `0xF7F6`, `0xF7FD` — voir § 8.4 |
| **F2** magasin `sub_95E78` | l. 129029-129092, 129904 | les 6 enregistrements |
| **F3** quatre files de report | l. 152332, 152521, 152790, 152979 | `word_C462/464/466/468` → tampon `0xCFA4`, `byte_CF9D` |
| **F4** commande calculée | l. 128443 (`word_C186`), 206384 (`MDH+0x10`) | seuls sites où la commande n’est pas un immédiat |

**La couche absente a un nom** : `nullsub_8`, appelée **exactement 4 fois**, une par slot de F3.

### 8.6 Les 13 groupes de l’image (étape 30)

`word_C5A`, bloc 10 octets (`0xC895`), `word_BFA`, `word_D7A`, `word_D6E`+`word_D70`, `word_CF6`,
`word_C1E`, `word_C4E`, `word_D26`, `word_D1A`, `word_D4A`, `word_CD2`, `word_CDE`, `word_BCA`.

Écriture indirecte via `byte_C238` / `byte_C30D` / `byte_C31D`, recopiés par `sub_A0CCC`.
**Aucun service de diagnostic n’appelle `sub_A0002` directement.**

### 8.7 Validité de l’image : `byte_C2EC`

| bit | sens | preuve |
|---|---|---|
| **0** | **image valide, utilisez-la** | `orb byte_C2EC,1` si **`word_CFAA == 0`** — l. 152021 |
| **1** | **forcer les valeurs par défaut** | `byte_C2EC = 2` en `loc_90618` (l. 111754), quand `word_DE22 ∈ {0x28…0x2B}` |

Cinq sites testent `byte_C2EC & 1` et **sautent l’initialisation par défaut** quand il est posé :
l. **154442** (`word_C5BE/C5C0 = 0x7FFF`, `C5F4 = 0`), **160911** (`C5D2/C5D4/C5D6 = 0xFA`),
**167312** (sept `word_C5xx` à 0), **213355** (`word_C3A6 = 0`), **210888** (`word_FD18.15`).

`word_CFAA` n’est écrit qu’en **149916** (`= 0`) et **149922** : c’est **l’état de l’opération EEPROM**.

### 8.8 Anti-falsification : un historique, pas un checksum

**Sept algorithmes de checksum testés sans succès** (sommes mots/octets/quartets, CRC16 CCITT /
XOTMODEM / IBM / ARC sur 3 plages) : **il n’y a pas de checksum à trouver** dans les 512 Ko.

Ce qui protège réellement :

```
valeur courante word_C5B8 ──► persistée en EEPROM
        │
        ├──► historique 5 niveaux : C5D2, C5D4, C5D6, C5D8, C5DA  (PERSISTÉ)
        │        └──► moyenne word_C5AE = somme / 5   (sub_97DDC)
        │                 └──► comparée à [word_18F2+0x14] = 120
        └──► comparée à [word_18F2+0x38] = 2
             comparée à [word_1474+0x06] = 325  ──► décompte word_D6FE ──► byte_C317
```

**On ne peut pas falsifier la valeur sans falsifier simultanément son historique de 5 valeurs et sa
moyenne — eux-mêmes persistés — ni sans franchir des seuils dont les valeurs sont dans le Datensatz,
donc hors de l’EEPROM.**

### 8.9 Le codage de variante — deux moitiés

**Moitié EEPROM (étape 45)** : quatre enregistrements à tag, à valeur unique en triple copie,
sélectionnés par le masque `byte_F80D`, écrits par la commande `0x0B`.

**Moitié CAN (étape 50)** : `[word_18B2 + 0x12]` porte un **masque de variante, bits 2 à 7** ;
chaque bit est **armé par un drapeau de trame CAN** et sélectionne un groupe de quatre valeurs
`+0x14…+0x1A` du Datensatz.

| bit de `[word_18B2+0x12]` | armé par |
|---|---|
| 2 | inconditionnel |
| 3 | `word_FD38` |
| 4 | `word_FD38+1` |
| 5 | `word_FD7A` |
| 6 | `word_FD7A+1` |
| 7 | `word_FD7C` |

```
Lexia → code le BSI → trame CAN → word_FD38 / FD7A / FD7C
                                    ↓
                    [word_18B2+0x12] : quel bit est autorisé
                                    ↓
                    groupe de valeurs du Datensatz → word_C5A8, word_D1B2/BA/BE
```

> **Limite** : le lien entre ces drapeaux et **le régulateur, la clim, BVM/BVA** n’est **pas** établi.
> La correspondance « bit ↔ option » est dans la **couche absente**. Un Datensatz ne contient que des
> nombres et des axes, **pas des affectations d’options** — la seule voie restante est de comparer
> deux EEPROM de véhicules de configurations connues.

---

## 9. Diagnostic : mémoire des défauts et moniteurs

| objet | adresse | structure |
|---|---|---|
| table des défauts | `0xCAD0` | **96 × 4 octets** : `+0` drapeau, `+2` mot |
| miroir | `0xFD21` | 96 octets |
| codes transmis | `0xCCB2` | **96 mots** — code ET indice de descripteur (`mot+0x1C`) |
| nb de défauts mémorisés | `byte_E466` | 0…7 |
| enregistrements | `0xE467` | **7 × 22 octets** |
| défaut courant | `0xE501` | `0xFF` = aucun |

**Descripteur de défaut** : `mot(0xCCB2) + 0x1C`, **confirmé par trois sites indépendants**
(l. 153103, 230034-230040, 231394). Champ : bits 0-1 = classe, bit 2 = drapeau, bits hauts = niveau.

**Sélecteurs** : `0x8000` compter · `0x9000` effacer tout · `0xFF00` courant · `0x80xx` lire les 154
octets · `0xEFxx` supprimer n° xx · `0xDFxx` lire n° xx · `0xD000` ajouter/mettre à jour.
**Numéro 87 utilisé littéralement** (l. 152158).

**Services** : `0x04` = ajout/mise à jour · `0x14` = compter + effacer · `0x17` = `sub_C1544`.

**Cinq compteurs de défauts par niveau** : `0xC9F3…0xC9F7`, incrémentés une fois par défaut **présent**,
sur une boucle de **96 entrées** (l. 231394), selon les bits hauts de `+0x1C`. Puis, si un compteur est
non nul, le bit correspondant est posé dans **`word_C548`** (bits 0, 1, 2) ou **`word_C54A`**
(bits 8, 15), d’après les numéros lus à `word_1818` = `02 01 00 08 0F`.

**Deux types de moniteurs** : `word_CFD4` bit 0 = **durée**, bit 7 = **valeur**.
Confirmation `sub_A1E9E` : `and CFD4,r12` → inhibitions `byte_CFC2/CFC3` → décompte `byte_CFC4` →
`or word_CFD6, r12`. Inhibitions actives : `byte_C2F5`, `byte_CFDC`, `word_C0BC` ; inhibition globale
par **`word_FD2E`**. **Power latch** : `word_FD0C.15` **gèle l’évaluation** (l. 153175).

**Anti-rebond à hystérésis** (étape 49) : deux courbes 1-D (`word_18AA`, `word_18AC`) sur une même
entrée donnent les **deux bornes d’une fenêtre** ; le résultat est comparé à une référence ; le
changement d’état exige **N cycles consécutifs** (`word_1474+offset`). Sept compteurs `word_D6EE…D6FA`.

---

## 10. Registre des erratas et des hypothèses retirées

*Conservé volontairement : ces pistes ne doivent pas être réintroduites.*

| # | hypothèse retirée | raison |
|---|---|---|
| 38 §1 | ~~« la banque F est une copie de E »~~ → **RÉHABILITÉE (étape 57)** | l’argument de retrait était faux : **14 octets d’écart est exactement la signature d’une copie variante**, pas d’une zone distincte. Comparaison octet par octet : 49 138 octets identiques, 14 différents. **F est bien une copie de E.** |
| 39 §2 | checksum de bloc | **invérifiable depuis le code visible** ; 7 algorithmes échouent |
| 39 §3 | piste par les usages de `unk_7EC8` | **un seul appelant**, corps absent |
| 43 §4 | les 5 entrées = les 5 identifiants EEPROM | le magasin compte **6** enregistrements |
| 46 §4 | format de descripteur partagé (« seuil à +6 ») | `+6` est un **indice**, pas un champ typé |
| 47 §1 | les blocs sont des **structures** | ce sont des **suites de mots indexés** |
| 47 §3 | 250 = Vmax (240 ou 250 ?) | **250 est une durée** de confirmation, en cycles |
| 47 §4 | `word_C5B8` = grandeur physique | c’est **un compteur** |
| 48 §5 | `word_1474` = blocs de **seuils** | ce sont des **durées** (étape 49) |
| 48/49 | « pointeur manquant » sur `word_1952` | le code lit jusqu’à `+0x3C` : les 62 octets sont **utilisés** |
| 49 | `word_18F6` = enregistrement triple | répétition **interrompue** et non monotone |
| **56** | `word_C3D2`, `word_C3BA`, `word_C3B0` = **masse d’air par tour (mg ×10)** | inféré de la **seule plage** 2 200-4 300 ; la chaîne capteur de l’étape 13 prouve que ce sont des **températures**. **ERREUR DE MÉTHODE : une plage ne prouve rien.** |
| **57** | « il n’y a pas de somme de contrôle » | les **champs** sont localisés (`0xE0FF6`, `0xE0FFC`, `0xEBCFC`) ; c’est le **calcul** qui reste inconnu. |
| **57** | « 66 cartes 2-D » = total | **sous-décompte** : 19 cartes stockées **à plat, sans axes**, échappaient au décodeur, et 6 cartes à en-tête masquées par le test 1-D. **Total : 72 + 19 = 91 cartes.** |

---

## 11. Ce qui reste à trouver

| sujet | état | piste |
|---|---|---|
| correspondance bit ↔ option (régulateur, clim, BVM/BVA) | **non résolu** | comparaison de deux EEPROM ; couche absente |
| PIN, VIN, immo | **non localisés** | handler EEPROM ; `byte_F62E`/`sub_95CC8` écartés (cohérence de config) |
| kilométrage | **écrit par l’ECU** (util) | `word_166C` → `EA 0xE406E`, 32 bits `C83A:C83C`, ÷2000 → `word_C654` |
| quantité de `word_C5B8` | compteur persistant, nature inconnue | ni kilométrage (comparé à 2), ni grandeur physique |
| `word_C5BC` | **axe −32768…−29408** | anomalie d’alignement à vérifier, ne pas conclure |
| valeur `0xC300` récurrente | `[word_1474+8]`, `word_142A+0x22`, bloc 2 o à `0xE2290` | **à instruire** |
| 958 enregistrements non décodés | d’un autre type | chercher les gabarits par taille régulière |
| régime depuis les impulsions | `sub_88A6C` (247,5 mm/impulsion) | vitesse par fil, 8 impulsions/tour de roue |
| Vmax (240 / 250 ?) | **250 présent en calibration** (`word_1474+0x18` et `+0x1A`) | unité **non établie** |
| rapport engagé | `sub_9B796` → `word_D3EC` | calculé v/RPM |
| FAP : suie, km, niveau de cérine | non localisés | chercher dans les blocs non décodés |

---

## 12. Annexe A — Correcteurs, filtres et boucles de régulation

*Consigné ici, en fin de document, tout ce qui a été identifié comme **traitement** et non comme
donnée : les correcteurs, les filtres, et les courbes qui les alimentent.*

### A.1 — Les quatre interpolateurs (bibliothèque de la couche absente)

| routine | appels | rôle |
|---|---|---|
| `unk_1D36` | 168 | interpolation **1-D** : `(handle, x)` → `r4` |
| `unk_1D50` | 72 | interpolation **2-D** : `(handle, x, y)` → `r4` |
| `unk_1D6C` | 44 | 1-D **avec destination mémoire** et **mémorisation de l’axe** : `(dest, x, handle)` |
| `unk_1D7E` | 54 | idem **sans nouvelle variable** — réutilise l’axe en cache : `(dest, handle)` → `r4` |

**338 sites d’appel · 203 courbes distinctes réellement interpolées · 62 sur le régime seul.**

### A.2 — Les deux traitements entièrement décodés

**Filtre récursif à coefficient calibré** — EA `0xACD4A` :

```
K = unk_1D36(handle 0x19F6, x = régime)        ; le coefficient EST une courbe
y[n] = ( y[n-1] + u[n] + K ) / 2               ; ashr #1
```

**Canal de régulation complet** — EA `0xAC65E` :

```
consigne = unk_1D36(handle 0x19D0, x = entrée)  ; consigne CALIBRÉE
consigne = consigne / 10000                     ; #2710h  ->  échelle 0…100 %
état = word_1DDA(mode, état précédent, consigne) ; LE PAS DE RÉGULATION
word_D836 = état
puis  unk_1D36(handle 0x19C8, même x) -> word_D2EE  ; seconde grandeur calibrée
```

**Et la source de la boucle est elle-même calibrée** : l’entrée est choisie entre `C616`, `C91C`
et `C93E` par l’octet `[0xE1148 + 0x23]`.

### A.3 — Le primitif de régulation `word_1DDA` : **35 boucles**

Signature constante : `(r12 = mode, r13 = état précédent, r14 = cible) → r4 = nouvel état`.
Un état persistant par boucle, plus un indicateur de saturation remonté en `USR0`.

| fonction | ligne | état persistant | cible |
|---|---|---|---|
| `sub_9928E` | 135096 | `word_CF4A` | `r7` |
| `sub_A1E9E` | 153755 | `word_CFE8` | `r7` |
| `sub_A5C92` | 159708 | `word_D75C` | `[r5+#4]` |
| `sub_A7D96` | 163561 | `word_D7AE` | `r2` |
| `sub_A7D96` | 168958 | `word_C5DC` | `r9` |
| `sub_A7D96` | 168973 | `word_C5DE` | `r9` |
| `sub_A7D96` | 168988 | `word_C5E0` | `r9` |
| `sub_A7D96` | 169028 | `word_D810` | `r9` |
| `sub_A7D96` | 169052 | `word_D814` | `r9` |
| `sub_A7D96` | 169089 | `word_D812` | `r9` |
| `sub_A7D96` | 169114 | `word_D816` | `r9` |
| `sub_A7D96` | 169142 | `word_D81E` | `r9` |
| `sub_A7D96` | 169154 | `word_D81E` | `r9` |
| `sub_A7D96` | 169180 | `word_D81C` | `r9` |
| `sub_A7D96` | 169192 | `word_D81C` | `r9` |
| `sub_A7D96` | 169213 | `word_D81A` | `r9` |
| `sub_A7D96` | 169225 | `word_D81A` | `r9` |
| `sub_A7D96` | 169246 | `word_D818` | `r9` |
| `sub_A7D96` | 169258 | `word_D818` | `r9` |
| `sub_AB3AC` | 169295 | `word_D80C` | `r6` |
| `sub_AB3AC` | 169323 | `word_D80E` | `r6` |
| `sub_AB3AC` | 169341 | `word_D80E` | `r6` |
| `sub_AC65E` | 171910 | `word_D836` | `r8` |
| `sub_ACD4A` | 172207 | `word_D838` | `word_D83A` |
| `sub_AF6E8` | 176987 | `word_C646` | `r8` |
| `sub_AF7B6` | 177115 | `word_D8C4` | `[r4]` |
| `sub_AF7B6` | 177145 | `word_D8C4` | `[r4]` |
| `sub_AFAA0` | 180162 | `word_D904` | `word_D906` |
| `sub_AFAA0` | 181069 | `word_D904` | `word_D906` |
| `sub_B2C9C` | 182581 | `r8` | `[r0+#0Ch]` |
| `sub_B2D36` | 182662 | `r9` | `[r0+#0Ah]` |
| `sub_B2D36` | 183147 | `word_D998` | `[r4+#10h]` |
| `sub_B2D36` | 183213 | `word_D998` | `[r4+#12h]` |
| `sub_B64A8` | 190143 | `r4` | `word_DB2C` |
| `sub_B7FD4` | 195332 | `word_DB38` | `[r0+#2]` |

**Lecture** : `sub_A7D96` porte à lui seul douze boucles indépendantes (`D810`, `D812`, `D814`,
`D816`, `D818`, `D81A`, `D81C`, `D81E`, `C5DC`, `C5DE`, `C5E0`, `D7AE`) — c’est le **cœur de
régulation** du calculateur, et il est aussi l’un des plus gros consommateurs de calibration.

---

## 13. Annexe B — Les switchs de calibration : **253 options**

**Un switch se reconnaît à trois traits simultanés** — il n’y a pas d’ambiguïté :

```
mov   r5, word_141E        ; handle de calibration  ->  structure EA 0xE1148
movb  rl4, [r5+#0Dh]       ; OCTET d’option, offset 13
jmpa  cc_NZ, loc_A4916     ; si NON NUL  ->  SAUTE 864 LIGNES ENTIÈRES
```

**Les paramètres numériques sont des MOTS ; les switchs sont des OCTETS.** C’est le discriminant
qui les sépare sans erreur. Et le saut est presque toujours un **saut long (`jmpa`)**, c’est-à-dire
un **shunt de bloc entier** — pas un ajustement, une décision.

| mesure | valeur |
|---|---|
| switchs conditionnels | **253** |
| fonctions concernées | **41** |
| structures de calibration porteuses d’options | **37** |
| lignes de code shuntées au total | **7232** |
| actifs si l’octet est NUL | 109 |
| actifs si l’octet est NON NUL | 84 |

*(29 sites supplémentaires ont été écartés : le saut qui les suit est inconditionnel, ce ne sont donc pas des switchs.)*

### B.1 — Les structures d’options, par nombre d’options

| handle | EA | options | lignes shuntées | remarque |
|---|---|---|---|---|
| `0x141E` | `0xE1148` | 60 | 3600 | **le bloc d’options maître** — présent dans 7 fonctions différentes |
| `0x1928` | `0xE5FE8` | 37 | 192 | options par paires d’offsets (0/1, 10/11, 16/17…) : un octet par stratégie |
| `0x1972` | `0xE6542` | 23 | 453 | options groupées par paires (22/23, 34/35, 36/37, 38/39, 44/45, 50/51) |
| `0x18B2` | `0xE4E2C` | 14 | 307 | déjà identifié comme **sélecteur de variante** (offsets 18 = 0x12 et 28 = 0x1C) — recoupement indépendant |
| `0x18EE` | `0xE52EE` | 14 | 133 |  |
| `0x1A64` | `0xE7E84` | 9 | 55 |  |
| `0x1E2C` | `0xEBC14` | 9 | 73 |  |
| `0x148A` | `0xE2332` | 7 | 197 |  |
| `0x1904` | `0xE5598` | 7 | 72 |  |
| `0x147A` | `0xE22B0` | 6 | 78 |  |
| `0x1488` | `0xE232A` | 5 | 875 |  |
| `0x1654` | `0xE400A` | 5 | 126 |  |

### B.2 — Les vingt switchs qui shuntent le plus de code

| fonction | structure | offset | valeur ici | polarité | lignes shuntées |
|---|---|---|---|---|---|
| `sub_A1E9E` | `0xE1148` | +13 | `0x00` | actif si NON NUL | **864** |
| `sub_A5C92` | `0xE1148` | +12 | `0x00` | actif si NUL | **787** |
| `sub_AFAA0` | `0xE232A` | +0 | `0x01` | actif si NON NUL | **578** |
| `sub_BF750` | `0xE1148` | +41 | `0x00` | actif si NON NUL | **576** |
| `sub_AFAA0` | `0xE83DA` | +17 | `0x01` | actif si NUL | **387** |
| `sub_972FA` | `0xE1148` | +20 | `0x04` | actif si NON NUL | **363** |
| `sub_AFAA0` | `0xE1148` | +51 | `0x00` | actif si NUL | **151** |
| `sub_A7D96` | `0xE6542` | +39 | `0x04` | actif si NUL | **147** |
| `sub_A7D96` | `0xE6542` | +39 | `0x04` | actif si NUL | **118** |
| `sub_AF932` | `0xE2332` | +0 | `0x01` | actif si NUL | **103** |
| `sub_9BAF0` | `0xE232A` | +0 | `0x01` | actif si NON NUL | **97** |
| `sub_9BAF0` | `0xE232A` | +0 | `0x01` | actif si NON NUL | **97** |
| `sub_9BAF0` | `0xE232A` | +0 | `0x01` | actif si NON NUL | **96** |
| `sub_D4D0A` | `0xE239E` | +12 | `0x05` | cc_UGT | **75** |
| `sub_ACD4A` | `0xE1148` | +36 | `0x01` | actif si NON NUL | **68** |
| `sub_D3C5A` | `0xE1148` | +44 | `0x00` | actif si NON NUL | **64** |
| `sub_D3C5A` | `0xE1148` | +45 | `0x00` | actif si NUL | **61** |
| `sub_A1E9E` | `0xE4E2C` | +18 | `0x1D` | actif si NON NUL | **59** |
| `sub_B35B6` | `0xE1148` | +49 | `0x01` | actif si NON NUL | **59** |
| `sub_D3C5A` | `0xE1148` | +44 | `0x00` | actif si NON NUL | **52** |

**Trois exemples parlants :**

- `sub_A1E9E` lit `[0xE1148 + 13]` ; l’octet vaut **0** et la condition est « actif si NON NUL » :
  **les 864 lignes sont exécutées** dans cette calibration.
- `sub_A5C92` lit `[0xE1148 + 12]` ; l’octet vaut **0** et la condition est « actif si NUL » :
  **les 787 lignes sont shuntées** — une stratégie entière est désactivée.
- `sub_AFAA0` lit `[0xE232A + 0]` ; l’octet vaut **1**, condition « actif si NON NUL » :
  **578 lignes sont actives**. Cette même structure porte **7 options** lues depuis 4 fonctions.

**⇒ C’est exactement le mécanisme que tu décrivais** : un octet de calibration qui autorise ou
interdit une portion entière de fonction, sans rien changer au code. **Modifier cet octet change
la stratégie appliquée**, et les blocs shuntés sont assez gros (jusqu’à 864 lignes) pour contenir
des algorithmes complets, pas des cas particuliers.

### B.3 — ★ Trier : tous les octets ne sont pas des switchs

**Correction importante.** Une lecture d’octet en calibration ne suffit pas à faire un switch.
Sur **122** lectures d’octets examinées :

| classe | nombre | critère |
|---|---|---|
| **SWITCH** | **78** | l’octet est immédiatement testé par un saut conditionnel |
| **DONNÉE** | **44** | l’octet est utilisé par un calcul (`movbz`, `and`, `add`, `mul`) — **c’est une valeur, pas un interrupteur** |

**36 % des lectures d’octets sont des données, pas des switchs.** Exemple net : les octets de
`0xE5FE8` (handle `0x1928`, 37 octets) sont lus puis combinés arithmétiquement — **ce sont des
coefficients, pas des options**. Un outil qui se contenterait de voir « octet de calibration +
saut dans les environs » les classerait à tort comme switchs.

### B.4 — ★★ Le patron réel : `SWITCH` à 2 états, `MODE` à N stratégies

La forme à **deux** états est un vrai interrupteur. Mais la forme la plus fréquente est un
**sélecteur**, et il faut la lire en cascade. Exemple intégral, option `[0xE6542 + 0x16]` :

```
mov  r5, word_1972
movb rl4, [r5+#16h]        ; octet d’option  = 0x01 dans ce firmware
jmpr cc_Z, loc_AA736       ; 0  ->  bclr word_FD0E.3          TOUJOURS INACTIF
cmpb rl4, #1
jmpr cc_Z, loc_AA73A       ; 1  ->  piloté par le drapeau CAN word_FD7C.8
cmpb rl4, #2
jmpr cc_Z, loc_AA746       ; 2  ->  piloté par le SEUIL calibré [0xE6542+0x12]
jmpr cc_UC, loc_AA75C      ; autre -> 4e stratégie
```

**C’est exactement « soit ignoré, soit une autre stratégie »** — et ici les stratégies sont :
**désactivé · par le CAN · par un seuil de calibration · autre**. L’octet ne dit pas oui/non,
il dit **qui décide**.

Les options de `0xE6542` vont d’ailleurs **par paires** d’offsets — (16/17), (22/23), (28/29),
(34/35), (44/45), (50/51) — ce qui suggère **un octet « stratégie » + un octet « état »** par
fonction, et chaque paire ne shunte que **8 lignes** : c’est une **substitution**, pas un bloc.

### B.5 — Ce que contiennent les blocs shuntés

| fonction | structure | +off | valeur | bloc | interpolations | axes appelés |
|---|---|---|---|---|---|---|
| `(code non nomme)` | `0xE1148` | +13 | `0x00` | **864** | 5 | C588 n=8,C5A4 n=4,D1E6(8)xD1F6(6),D1FE n=4,D202(8)xC590(8) |
| `sub_A5C92` | `0xE1148` | +12 | `0x00` | **787** | 5 | régime n=10 |
| `(code non nomme)` | `0xE232A` | +0 | `0x01` | **578** | 9 | — |
| `(code non nomme)` | `0xE83DA` | +17 | `0x01` | **387** | 0 | — |
| `(code non nomme)` | `0xE1148` | +51 | `0x00` | **151** | 0 | — |
| `sub_AF932` | `0xE2332` | +0 | `0x01` | **103** | 0 | — |
| `sub_9BAF0` | `0xE232A` | +0 | `0x01` | **97** | 0 | — |
| `sub_9BAF0` | `0xE232A` | +0 | `0x01` | **97** | 0 | — |
| `sub_9BAF0` | `0xE232A` | +0 | `0x01` | **96** | 0 | — |
| `(code non nomme)` | `0xE1148` | +44 | `0x00` | **64** | 0 | — |
| `(code non nomme)` | `0xE1148` | +45 | `0x00` | **61** | 0 | — |
| `(code non nomme)` | `0xE1148` | +49 | `0x01` | **59** | 0 | — |

**Le plus gros** (`[0xE1148+13]`, 864 lignes) contient **5 interpolations** : courbes sur `C588`,
`C5A4`, `D1FE`, et deux **cartes** — `D1E6 × D1F6` et `D202 × C590`. C’est donc **tout un étage de
calcul**, pas un cas particulier.

### B.6 — Deux réserves de méthode, à conserver

1. **L’attribution des fonctions n’est pas fiable partout.** Le désassembleur laisse des zones de
   code **sans étiquette**. Les plus gros switchs (`864`, `787`, `578`, `387` lignes) sont dans du
   **code non nommé** : les rattacher à `sub_AFAA0` — qui ne fait que **10 lignes** — aurait été
   faux. Le catalogue les marque `(code non nommé)`.
2. **La polarité doit se lire, pas se supposer.** « actif si NUL » prêtait à confusion : il faut
   dire **« le saut est pris si l’octet est NUL »**, donc le bloc est **exécuté** quand l’octet est
   non nul. Une inversion de lecture inverse la conclusion.

### B.7 — ★ L’EGR : ce qui est établi, et ce qui ne l’est pas

**Établi — la famille de cartes et son usage :**

| handle | EA | contenu |
|---|---|---|
| `0x1B3C` | `0xE83DA` | bloc de paramètres de la zone air (octets lus 9 fois dans un même calcul) |
| `0x1B3E` | `0xE83F4` | courbe sur le **régime**, 19 points, 0…5200 → 0…7430 |
| **`0x1B40`** | **`0xE8444`** | **CARTE 16 × 16 : régime 0…5200 × air mesuré 300…1150 mg → 0…7600** |
| `0x1B44` | `0xE86F4` | carte préchauffage (régime × T LDR) |
| `0x1B4C` | `0xE8872` | seconde carte régime × air, **grille nulle** (emplacement vacant) |

**Ces handles sont interpolés à quelques lignes d’une lecture de la masse d’air mesurée**
(`word_C5A8` / `word_C3E6`) — c’est le schéma d’une **limitation par la masse d’air**, dont la
carte `0xE8444` est l’élément central.

**Candidats switchs de cette zone :**

| site | structure + off | valeur | effet |
|---|---|---|---|
| `l.181491` | `0xE83DA + 17` | `0x01` | saute 387 lignes **si NUL** → **bloc exécuté** |
| `l.178313` | `0xE7FF8 + 0` | `0x01` | bloc de 6 lignes |
| `l.167740` & suivants | `0xE6542` paires | 0/1/2 | **sélecteurs de stratégie** (voir B.4) |

**Ce que je dois écarter, et pourquoi.** Le bloc gaté par `[0xE83DA+17]` (387 lignes) contient une
**division avec reste** — `divu` puis lecture de `MDH` comparé à `word_D91E`, sur un compteur
`word_D920` incrémenté — c’est un **processus périodique / base de temps**, pas une fonction
spécifique. **Je ne le retiens donc pas comme switch EGR.**

**Conclusion honnête : la région EGR est identifiée, le switch EGR ne l’est pas encore.**
Ce qui manque est un lien fonctionnel : savoir quel mot RAM porte la **consigne de l’électrovanne EGR**.
Tant que ce mot n’est pas nommé, tout octet de cette zone peut aussi bien commander la
suralimentation, la vanne EGR ou le volet d’admission. **Le prochain pas est donc d’identifier la
sortie, pas l’entrée.**

### B.8 — Le bloc d’options `0xE111E` (42 octets) : qui le lit, ce qu’il fait, la zone touchée

**Résolution de l’adresse.** L’octet `0x6111F` est l’octet `+1` du bloc ; la base du Datensatz est au
fichier `0x60000`, donc `EA = 0x6111E − 0x60000 + 0xE1000 + 0xFF000`… plus simplement :
**fichier `0x6111E` ⇔ EA `0xE111E`**. Le pointeur est l’entrée n° 14 de la table de pointeurs
(fichier `0x61400`, EA `0xE1400`) : `EA 0xE141C = 0x111E` ; c’est le handle **`0x141C`**, symbole RAM
`word_141C`, qui vaut donc `0x111E`.

**Bornes du bloc — preuve arithmétique.** Pointeur suivant `word_141E = 0x1148` (EA `0xE1148`).
`0xE111E + 42 = 0xE1148` : le bloc fait **exactement 42 octets**.
**Correction** : le bloc voisin `0xE1148` ne fait pas 60 octets mais **52** (`0xE1148 → 0xE117C`,
pointeur `word_1420 = 0x117C`). Le « 60 » de l’étape 60 était un décompte de sites, pas une taille.

**Nature : ce n’est pas une carte.** Aucun tag, aucun `n`, aucune valeur d’axe : c’est un **bloc de
paramètres**, au sens de la règle « une map sans en-tête n’a pas d’axes ». 42 octets, presque tous
à `0x00`/`0x01`, sauf `+0x0A = 0x30`, `+0x0E = 0x08`, `+0x16 = 0x0A`, `+0x17 = 0x02`,
`+0x18 = 0x02`, `+0x19 = 0x03`, `+0x1A = 0x02`, `+0x27 = 0x01`, `+0x28 = 0x02`.

**35 octets sur 42 sont lus**, chacun par **un seul type de lecteur** :

| usage | offsets | mécanisme |
|---|---|---|
| **recopie en RAM** (31 octets) | `+1 +2 +3 +4 +6 +8 +9 +0x0A +0x0E +0x0F +0x10 +0x15…+0x1F +0x20…+0x28` | 3 routines copient l’octet dans une variable `byte_C2Bx`/`byte_C2Cx` |
| **test direct** (5 octets) | `+0x0B` (2 sites), `+0x0C`, `+0x0D`, `+0x11` | le saut est immédiatement pris selon la valeur |

**Les 9 lecteurs de `word_141C`** (aucun autre site dans tout le listing) :

| site | fonction réelle | ce qui est fait |
|---|---|---|
| `l.151755` `loc_A11BA` | bloc non nommé (seg014) | recopie **10 octets** → `C2B1 C2B2 C2B0 C2C5 C2C9 C2B3 C2B9 C2BB C2B4 C2BA` |
| `l.199982` `loc_BD7D6` | `sub_BD464` | recopie **20 octets** → `C2BF C2CC C2C7 C2B8 C2C3 C2B7 C2C0 C2D0 C2D1 C2CE C2CF C2CB C2CD C2C8 C2BE C2C6 C2CA C2BD C2C4 C2C1` |
| `l.200395` | bloc non nommé (seg015) | recopie `+0x10` → `C2B6` ; puis **teste `+0x11`** |
| `l.196409` | bloc non nommé (seg015) | teste `+0x0B` **deux fois** |
| `l.196438` | bloc non nommé (seg015) | teste `+0x0C` |
| `l.196446` | bloc non nommé (seg015) | teste `+0x0D` contre `1` |

**Consommation des miroirs : ≈ 341 références** dans le code pour ces 31 octets. L’octet `+0x27`
(→ `byte_C2BA`) est le plus utilisé : **63 références**.

#### Ce que font les octets testés directement

| octet | valeur | effet exact |
|---|---|---|
| `+0x0B` | `0x00` | si **non nul** : `word_DB64 = 0` **et** `word_DB66 = 0` — la consigne est annulée. Si nul : consigne = interpolation de `[word_14A0 + 0x32]`, **ou** constante calibrée `word_C506` si les bits `0x800`/`0x200` de `[word_1468]` le demandent |
| `+0x0C` | `0x00` | si **non nul** : la consigne passe par **`unk_2020`** (régulateur, voir B.9) ; si nul : par **`unk_1FE8`**. **L’octet choisit la structure du régulateur** |
| `+0x0D` | `0x01` | `cmpb #1` → `byte_DB73 = 5`, sinon `4`. C’est un **code d’état** d’une machine à états |
| `+0x10` | `0x01` | recopié dans `byte_C2B6` |
| `+0x11` | `0x00` | **verrou à mémoire** : `C8EB := C2B6` ; si `C2B6 + C2B5 == 1`, alors si `+0x11 == 1` → `C8EB = 1, C2B5 = 0`, sinon → `C8EB = 0, C2B5 = 1` |

#### ★ La zone que ce bloc touche

Aucun lecteur n’est dans le segment d’injection : les recopies sont en **seg014** (CAN/diagnostic) et
**seg015** (supervision). En revanche les miroirs `byte_C2B0…byte_C2D1` sont lus **partout**. Le bloc
commande donc trois étages :

1. **La machine à états de supervision** — `byte_DB73`, **14 états** (`0…0x0D`) sélectionnés par une
   **table de saut à EA `0xE0AE6`** (`movbz r4, byte_DB73 ; shl #1 ; add #0AE6h ; mov r4,[r4] ; jmpi`).
   Les 14 cibles sont `0xAEE0 0xAFB0 0xB03C 0xB0D4 0xB16A 0xB134 0xB1E2 0xB22C 0xB25C 0xB27E
   0xB1A2 0xB08C 0xB2D6 0xB3D8` (offsets dans le segment 015).
2. **La consigne d’air et sa régulation** — `word_DB66` (consigne) / `word_DB64` → `word_D4B0` /
   `word_D4B2`, puis régulateur `unk_2020` ou `unk_1FE8`, puis `unk_1EBC`, avec **saturation
   `0x7FFF`/`0x8000`** et **butées anti-emballement** `[r7]` / `[r7+2]`.
3. **Le diagnostic** — `+0x0E = 0x08`, bit 0 actif : enregistre **deux identifiants** via
   `sub_9CF70` (`9 / 0x349`) et (`0x0D / 0x389`).

#### ★★ Découverte de structure : `0xE0000–0xE1000` n’est pas de la calibration

Les tables de saut de la couche code vivent dans le **début du Datensatz**. Sept bases recensées :
`0xE0966`, `0xE0970`, `0xE098E`, `0xE09C6`, `0xE09DC`, `0xE0A62`, `0xE0AE6`. Le motif est toujours
`movbz rN, rlN ; shl rN, #1 ; add rN, #0XXXh ; mov rN, [rN] ; jmpi cc_UC, [rN]`.
Les entrées sont des **offsets 16 bits de segment** (ex. `0xE0966` → `0x95C6`, `0x95E0`, `0x965A`,
`0x96A4`, `0x96EE`, …). **Conséquence** : la couverture `0xE1000–0xEC000` ne décrit que la
calibration ; la zone `0xE0000–0xE1000` est du **code adressé par table**, à inventorier à part.

#### ★ Nouvelle famille « couche absente » (corps `ds 1`)

| routine | appels | rôle observé |
|---|---|---|
| **`unk_2020`** | **2** (`l.173370`, `l.196462`) | reçoit **6 arguments**, dont deux pointeurs de structure de calibration et un pointeur de sortie ; renvoie la correction. **Cœur du régulateur PI** |
| `unk_1FE8` | **8** | même famille, variante de régulateur (cf. `+0x0C`) |
| `unk_1EBC` | **2** | appelé juste après, sur les mots `DB6A/DB6C/DB6E` — étage de lissage/limitation |
| `word_1DA8` | **14** | pointeur de routine appelé avec `r12` = sortie, `r13 = #2710h` (échelle ×10000) |

---

### B.9 — ★ CONFIRMÉ : l’octet `0xE111E+0x0B` neutralise la boucle d’air/EGR

**Ce que fait exactement l’octet** (valeur `0x00` dans ce firmware), aux **trois** endroits où il est testé :

| site | code | effet |
|---|---|---|
| `l.196410` | `jmpr cc_NZ, loc_BB548` | `word_DB64 = 0` **et** `word_DB66 = 0` — la **consigne est annulée** |
| `l.196439` | `jmpr cc_NZ, loc_BB566` | force `r5 = 0` puis `mov [r0], r5` ⇒ la valeur interpolée stockée dans `word_D492` est **zéro** |
| `loc_BB550` | (branche atteinte) | `word_DB6C = 0` et `word_DB6E = 0` — le **terme accumulé est effacé** |

**Donc oui : l’octet coupe la boucle fermée.** Consigne à zéro + intégrale à zéro = le régulateur ne
peut plus rien produire. Ce n’est pas un « switch EGR » qui débranche une fonction nommée : c’est un
**interrupteur de boucle** qui met toutes les entrées du régulateur à zéro. **La formulation est validée.

#### La boucle, étage par étage

| # | étage | code / donnée |
|---|---|---|
| 1 | **consigne** | carte **8 × 8** `word_1C98` → **EA `0xE9660`**, appelée `l.196401` `unk_1D50(handle, word_C91C, r8)` |
| 2 | **repli consigne** | constante calibrée `word_C506` si les bits `0x800`/`0x200` de `[word_1468]` le demandent (`l.196419`) |
| 3 | **correction neutre** | courbe `word_1C90` → **EA `0xE9626`**, n=2, axe tag `0xC7C6` 1000…3000 — **les deux valeurs sont `0`** |
| 4 | **régulateur PI** | `unk_2020` (2 appels) puis `unk_1EBC`, avec **saturation `0x7FFF`/`0x8000`** et butées `[r7]`/`[r7+2]` |
| 5 | **hystérésis / anti-rebond** | `sub_BAC40` : état `[r13]` 0…`0xFF`, compare `r12`, retourne 0 ou 1 avec drapeaux `DB84`/`DB86` |
| 6 | **moniteur de dérive** | `l.197160` : `r4 = word_DB68 + word_DB66`, comparé à `[word_14A0+0x5C]`, seconde condition `[word_14A0+0x4C] ≥ word_DB52` ⇒ compteur `word_DB5E` **saturé à `0x7FFF`** |

#### ★★ La carte de consigne, décodée octet par octet : `0xE9660`

| champ | valeur | lecture |
|---|---|---|
| tag Y | **`0xC42E`** | **régime moteur** |
| n Y | `8` | axe : `200, 500, 750, 1000, 1500, 2000, 3000, 4000` |
| tag X | **`0xC7B8`** | grandeur **dérivée** (pas un capteur brut : `word_C7B8` est recalculé `l.190859` après un **max-glissant** `word_DBB8`) |
| n X | `8` | axe : `2000, 3000, 5000, 7000, 9000, 10000, 11000, 13000` |
| grille | `8 × 8` | 64 valeurs |

Une consigne bâtie sur une **carte (régime × grandeur 2 000…13 000)** n’est pas une consigne de
carburant (le débit de carburant se calcule, il ne se lit pas sur une carte 8 × 8 de cette forme) :
c’est **une boucle d’air**. C’est le point qui rend l’hypothèse EGR cohérente.

#### Ce qui reste à trancher — le seul doute qui subsiste

**`word_C7B8` : air (×10, donc 200…1300 mg) ou pression (mbar) ?** Les deux donnent la même plage
2000…13000. Tant que ce mot n’est pas nommé, on ne peut pas séparer **EGR** de **suralimentation
(VNT)** — les deux se règlent en boucle fermée sur une carte régime × air/pression.

Le test qui tranche : remonter `word_C7B8` jusqu’à sa source capteur (loi ADC ou `word_C3E6`).
S’il descend du débitmètre ⇒ **c’est l’EGR**.

#### Les sorties de la boucle ne pilotent rien directement

`word_D48E`, `word_D49C`, `word_D4A4`, `word_D49E`, `word_D4A8`, `word_D4AE`, `word_D4B0`, `word_D4B2`
sont **écrits et jamais relus** dans tout le listing : ce sont des **images de mesure** (bloc diagnostic /
CAN), pas des commandes. La grandeur qui sort réellement de la boucle est `word_DB6A` / `word_DB6E`,
consommée **uniquement** par la couche absente (`unk_2020`, `unk_1EBC`).
**Conclusion** : la boucle est neutralisée par `+0x0B`, mais **l’actionneur physique n’est pas encore
nommé** — le prochain pas reste la sortie PWM.

---

### B.10 — Portée mesurée de chaque octet du bloc `0xE111E` : ils n’agissent PAS sur les mêmes fonctions

**Deux octets sont morts.** `+0x00` (la donnée « en `0xE111E` ») n’est **lu par aucun site** —
vérifié quatre fois : aucun `[r4]` sans déplacement, aucun `[r4+#0]`, aucun handle voisin (`word_1418`
n’accède qu’à `+8`, `word_141A` qu’à `+8`), aucune arithmétique de pointeur. `+0x04` (→ `byte_C2BB`)
est écrit et **jamais relu**. **Aucun des deux ne peut donc désactiver quoi que ce soit.**

**Un seul octet coupe la boucle : `+0x0B` = `0xE1129`.** Et il ne fait **rien d’autre** :

| variable touchée | valeur forcée | conséquence |
|---|---|---|
| `word_DB66` | `0` | consigne nulle (les **deux** chemins de calcul, `l.196410` et `l.196439`) |
| `word_DB64` | `0` | terme remis à zéro |
| `word_D492` | `0` | valeur interpolée effacée |
| `word_DB6C`, `word_DB6E` | `0` | terme accumulé effacé |

Les images `word_D4xx` tombent à zéro **par conséquence** (elles recopient `DB66`/`DB68`), pas par action
directe. **`+0x0B` n’a que 2 sites, dans une seule fonction (EA `0xBB51E` et `0xBB558`, seg015) : c’est la
portée la plus étroite de tout le bloc.**

#### Portée mesurée, octet par octet (nombre de lectures et segments atteints)

| octet | miroir | lectures | segments |
|---|---|---|---|
| `+0x0B` | *(test direct)* | **2 sites** | seg015 seul, **1 fonction** |
| `+0x27` | `byte_C2BA` | **61** | s13 = 11, s14 = 37, s15 = 7, s16 = 5, s17 = 1 |
| `+0x0E` | `byte_C2B7` | **29** | s13 = 14, s14 = 1, s15 = 10, s16 = 4 |
| `+0x10` | `byte_C2B6` | **24** | s13 = 5, s14 = 6, s15 = 11, s17 = 2 |
| `+0x03` / `+0x15` | `C2BD` / `C2C0` | 12 / 12 | s14-s15-s16 / s14-s15-s16 |
| `+0x17` / `+0x1A` | `C2B8` / `C2D1` | 8 / 8 | s13-s14-s16 / s16 |
| `+0x0A` | `byte_C2C9` | 7 | s13 = 5, s15 = 2 |
| `+0x16` / `+0x18` / `+0x26` | `C2BF` / `C2B4` / `C2C4` | 6 / 6 / 6 | s14 / s13-s14-s15-s16 / s14-s15-s16 |
| `+0x01` / `+0x02` / `+0x19` | `C2B1` / `C2C5` / `C2D0` | 5 / 5 / 5 | s13-s16 / s14-s16 / s16 |
| `+0x09` | `byte_C2B0` | 3 | s14 = 2, s16 = 1 |
| `+0x06` / `+0x0F` | `C2B9` / `C2B3` | 2 / 2 | s14 / s15 |
| `+0x1B`…`+0x25`, `+0x28` | 11 miroirs | **1 chacun** | s16 uniquement |

**Total : 214 lectures** pour les 31 miroirs. **Conclusion nette : le bloc n’est pas « un switch », et les
octets ne partagent pas la même cible.** `+0x0B` est le seul à toucher la boucle d’air ; les autres
touchent la carte `byte_C2B7` (diagnostic, 4 segments), `byte_C2B6` (4 segments), `byte_C2BA` (5 segments).

**Si une définition de fichiers annonce « EGR off » à `0xE111E`, elle désigne la BASE du bloc. L’octet
réellement lu par le code est `0xE1129` (`+0x0B`).**

---

### B.11 — Zone `0xE1129` → `0xE11DD` (+180 octets) : inventaire

**Douze blocs**, bornés par les pointeurs consécutifs de la table `EA 0xE1400`.

| handle | EA | taille | contenu | symbole lu | lectures |
|---|---|---|---|---|---|
| `0x141C` | `0xE111E` | 42 o | options — `+0x00` mort, **`+0x01` = interrupteur maître**, `+0x0B` = coupe la boucle d’air | `word_141C` | 9 |
| `0x1F8A` | `0xE1127` | 4 o | `30 01 00 00` | **aucun** | 0 |
| `0x232E` | `0xE112B` | 11 o | octets 0/1 | **aucun** | 0 |
| `0x1F0A` | `0xE1136` | 4 o | `02 03 02 01` | **aucun** | 0 |
| `0x23F4` | `0xE113A` | 14 o | octets 0/1 + `0xC3` final | **aucun** | 0 |
| **`0x141E`** (+ alias `0x2148`) | **`0xE1148`** | **52 o** | **bloc d’options : 97 lectures, offsets `+0x01`…`+0x33`** | `word_141E` | **97** |
| `0x1420` | `0xE117C` | 24 o | **12 × `0xFFFF`** | `word_1420` | 2 (pointeur) |
| `0x1E76` | `0xE1194` | 12 o | 6 × `0xFFFF` | **aucun** | 0 |
| `0x1422` | `0xE11A0` | 23 o | zéros | `word_1422` | 2 (pointeur) |
| `0x1FE6` | `0xE11B7` | 11 o | zéros | **aucun** | 0 |
| `0x1FC8` | `0xE11C2` | 2 o | `0x0000` | **aucun** | 0 |
| `0x1424` | `0xE11C4` | 40 o | **table de 20 valeurs 16 bits** | `word_1424` | 4 (pointeur) |

**8 handles sur 12 n’ont aucun symbole dans le code** ; `0x2148` est un **alias exact** de `0x141E`.

#### Les deux offsets dominants de `0xE1148`

| offset | sites | effet |
|---|---|---|
| **`+0x0A`** | **16** (seg015) | **sélecteur d’échelle** : `r8 = 0` si `== 1`, sinon **`r8 = 0x2710` (10 000)**. Valeur `0x30` ⇒ échelle 10 000 partout |
| **`+0x14`** | 6 (4 segments) | **sélecteur à 4 états** (`#2`, `#3`, `#4` → même cible), sinon `r5 = 0x0F − r4` |
| `+0x09` / `+0x06` | 8 / 4 | sélecteurs de type (`#4`, `#2`, `#1`) |
| `+0x0C` | 5 (seg014) | variante : 5 sauts conditionnels |

#### Le diagnostic, sous forme de tables

- `sub_BE2BA` construit une **réponse diagnostic** (`movb rl4, #42h` + identifiant + 4 octets), avec
  découpage en groupes de 32 (`0x00 0x20 0x40 0x60 0x80 0xA0 0xC0 0xE0`).
- Marqueur `0xFF` ⇒ valeur lue dans `0xE117C` (que des `0xFFFF` = « pas de valeur »).
- Marqueur `0xFE` ⇒ valeur lue dans `0xE11A0` (que des zéros). Le marqueur vient de **RAM `0xDC2C + index`**.
- `sub_BEF66` scanne les **20 entrées** de `0xE11C4` après un **test de masque** (`and r4, r5`).
- `loc_CF1F0` (seg016) **recopie ces 20 mots en RAM `0xCC54+4i`** via `sub_CFEFA` (conversion).
  ⇒ `0xE11C4` est une **table de 20 valeurs 16 bits indexées par position**, pas une table d’identifiants.
- Juste après, `loc_CF216` parcourt **96 entrées** depuis `0xCCB2` (`cmp r3, #60h`) = **table de défauts**.

#### Verdict sur les hypothèses FAP

**Aucune donnée FAP dans cette zone** : pas de masse de suie (g), pas de pression différentielle (hPa),
pas de kilométrage. Ce qu’elle contient réellement = **options de variante** + **tables de service du
diagnostic**. La porte d’entrée vers les seuils FAP est la **table de défauts `0xCCB2`** (96 entrées),
dont les enregistrements pointent en général vers les seuils de surveillance.

---

### B.12 — ★ ERRATA de B.11 + seconde passe : 138 lectures dans la zone

#### Deux raisons pour lesquelles `0xECCB2` est vide

1. **`0xCCB2` est une adresse RAM** (`mov r4, #0CCB2h`), pas une EA de ROM : la table de défauts est
   **construite en RAM** au runtime à partir de `0xCC54` (`cmp r8, #0CCA4h`).
2. **La copie `0xE` est tronquée** : les données s’arrêtent à **EA `0xEBFB9`**, puis `0xEC000–0xF0000`
   est constitué de **16 384 octets de `0xC3`**. En revanche **`EA 0xFCCB2` (copie `0xF`) contient
   des données** : `f0 fe 0f 00 21 8f 04 60 50 7e 00 00 41 8f 06 60 0a cc 0f 00 ff ff ff ff`.

**Différence entre les deux copies : 14 147 octets**, dont **14 octets isolés seulement sous `0xEBFFF`**
(`0xE0FF6`, `0xE0FFC`, `0xE434D`, `0xEBCFC`…) et **14 133 octets dans `0xEC000–0xEFFFF`.
⇒ la copie `0xF` possède **≈ 14 Ko de données en plus**. Aucune structure au format 1-D/2-D connu
(18 détections, toutes faux positifs) : ce n’est **pas** de la calibration cartographique.

#### Errata : 8 handles n’existent pas

La table de pointeurs compte **exactement 1305 entrées** = handles **`0x1400` → `0x1E30`**.
Les handles `0x1F8A`, `0x232E`, `0x1F0A`, `0x23F4`, `0x1E76`, `0x1FE6`, `0x1FC8`, `0x2148` cités en B.11
sont **des artefacts** : au-delà de `0x1E30` la table contient autre chose (`0x0010`, `0x02D5`…).

| handle | EA | taille corrigée | lectures |
|---|---|---|---|
| `0x141C` | `0xE111E` | 42 o | 36 |
| `0x141E` | `0xE1148` | 52 o | **102 (39 offsets)** |
| `0x1420` | `0xE117C` | **36 o** (18 × `0xFFFF`) | par `pointeur + PID×2` |
| `0x1422` | `0xE11A0` | **36 o** (18 × `0x0000`) | par `pointeur + PID×2` |
| `0x1424` | `0xE11C4` | 40 o (20 valeurs) | par `pointeur + index` |
| `0x1426` | `0xE11EC` | 32 o | — |

**18 entrées = PID `0x00`…`0x11`** : les trois tables sont indexées par identifiant OBD.

#### Seconde passe : 138 lectures, 89 switch / 49 donnée

| groupe | offsets de `0xE1148` | sites | effet |
|---|---|---|---|
| **masque 32 bits** | **`+0x15 +0x16 +0x17 +0x18`** | 4 | `andb byte_D98E…D991, octet` puis recomposition en `word_D3CE` → **4 octets = un seul filtre 32 bits** |
| **sélecteurs 5 états** | **`+0x04` (8), `+0x09` (9), `+0x14` (8)** | 25 | codes `0…4` ; `+0x04` déclenche aussi le service EEPROM `sub_CE9B4` (`#1B2h`, `word_176E`, `#46FEh`) |
| **échelle** | **`+0x0A`** | **17** | `r8 = 0` si `==1` sinon `0x2710` |
| variante | `+0x0C` (6), `+0x0D`, `+0x1B` | 8 | stratégies seg014 |
| masques ponctuels | `+0x1F +0x20 +0x30` | 3 | `andb` sur registres |
| drapeau de fin | `+0x33` | 7 | seg013 + seg015 |
| seg017 | `+0x1C +0x1D +0x2B +0x2C +0x2D` | 6 | couche CAN/tâches |

**13 offsets jamais lus** : `+0x00 +0x07 +0x0B +0x0E +0x0F +0x10 +0x11 +0x12 +0x13 +0x1A +0x1E +0x27 +0x32`.

---

### B.13 — ★ Accès directs ET indirects à la zone : balayage exhaustif (7 pistes)

**Le segment `seg019` (`EA 0xF0000`+) contient bien du CODE** (labels `loc_FC0EA`, `loc_FC142`…).
La région non dupliquée de 14 Ko n’est donc **pas** de la calibration. Les seules **données** que le
code y lit sont des cellules nommées, atteintes par `extp` : `byte_FBEF9`, `byte_FBEFA`,
`word_FBF38`/`word_FBF3A`, `byte_FEC00`/`byte_FEC01`.

| piste d’accès indirect | méthode | résultat |
|---|---|---|
| immédiats `#111Eh #1129h #1148h #117Ch #11A0h #11C4h` | balayage du listing entier | **0 occurrence** |
| repointage des mots-handles | recherche d’écritures sur `word_141C/141E/1420/1422/1424` | **0 écriture** |
| handle passé à une routine (1541 sites) | fenêtre de 6 lignes avant `calls` | 6 candidats → **6 faux positifs** (le vrai handle est chargé 3-4 lignes après : `word_1994`, `word_19B6`, `word_1DCA`) |
| `sub_CE9B4` (686 appels) | relevé des `r1` | **aucun** de nos handles |
| `extp` / pages | pages utilisées : `0x22 0x24 0x33 0x37 0x3E 0x3F` | **jamais `0x38`–`0x3B`** : le Datensatz n’est jamais ouvert en cross-page |
| **`sub_CE57E` (seg016)** | `mov r3, word_1422 ; add r3, r12 ; mov r3, [r3]` | **indirect réel** : la table est choisie par des **bits en RAM `0xFD21 + code`** (bit 0 → `0xE11A0`, bit 1 → `0xE117C`) ; **voir § B.14 pour le décodage complet (r12 doublé, table RAM `0x0E4E`)** |
| **`l.231375` / `l.231675` (seg016)** | `mov r7, word_1424 ; mov r1, [r7+]` (boucle de 20) et `mov r0, word_1424 ; add r0, r1 ; add r0, r1` | **indirect réel** : la table `0xE11C4` est parcourue par index |

#### ★ Conséquence sur `0xE11C4` : la plupart des valeurs sont des TROUS

```asm
mov  r0, word_1424
add  r0, r1
add  r0, r1           ; r0 = base + 2*index
mov  r2, [r0]
cmp  r2, #11h         ; ★ 17
jmpr cc_UGT, loc_CF51E ; valeur > 17 -> ÉCARTÉE
mov  r0, #0E4Eh       ; table RAM
add  r0, r2
add  r0, r2
movb rl2, [r0+]       ; 2 octets par entrée, sentinelle 0xFF
```

Les seize premières valeurs (`0x0F10`, `0x0F61`, `0x0F80`, `0x0FFA`…) sont **toutes > 17** : elles
sont **écartées** par ce test. Seules les deux entrées `0x0005` et `0x000F` passent le filtre et
deviennent des **index** dans une table courte à `0x0E4E`. Autrement dit, **cette table de 20 mots
n’est pas indexée par position : c’est une liste de valeurs dont 18 sont des marqueurs hors bornes.**

**Conclusion générale** : les **octets d’option** de la zone sont lus **directement** (138 sites) ;
les **trois tables** (`0xE117C`, `0xE11A0`, `0xE11C4`) sont lues **uniquement indirectement**, par
index, avec un sélecteur en **RAM `0xFD21`**. Aucune autre voie d’accès n’existe : sept pistes
vérifiées, toutes négatives sauf celle-là.

*Données : `acces_indirects_zone.csv`.*

---

### B.22 — ★★★★ LE DICTIONNAIRE identifiant → adresse RAM (356 entrées, page `0x90000`)

**C’est le chaînon final.** À `EA 0x91202` une table de **356 entrées** (`0x0164`) :

| EA | contenu |
|---|---|
| `0x91202` | `0164` = **356** = nombre d’entrées |
| `0x91204` – `0x914CA` | **356 identifiants triés croissants**, `0x0004` → `0xE4EE` |
| `0x914CC` – `0x91791` | **356 adresses RAM** parallèles |
| `0x91794` … | un 3e tableau parallèle (`FF1C`, `C6CC`, `C476` …) non décodé |

Accès dans le code : `sub_B7FAC` → `sub_CFEFA` (page `0x24` = `0x90000`) = **recherche dichotomique**
de l’identifiant dans le tableau trié, puis lecture des tableaux parallèles.

#### Vérification par nos ancres déjà établies

| identifiant | adresse RAM | grandeur | statut |
|---|---|---|---|
| `0x0F00` | `0xC3D2` | **température LDR** | ancre établie ✔ |
| `0x0F02` | `0xC3B0` | **température carburant** | ancre établie ✔ |
| `0x0F10` | `0xC42E` | **régime moteur** | ancre établie ✔ |
| `0x0F65` | `0xC3C2` | **RCO EGR** | ancre établie ✔ |
| `0x0F8C` | `0xC6A2` | **charge %** | ancre établie ✔ |
| `0xE4D2` | `0xC5A8` | **masse d’air / tour** | ancre établie ✔ |

**Six ancres indépendantes tombent juste** ⇒ le tableau est bien identifiant → adresse RAM.
Plage couverte : `0xC228` → `0xFF1C`, **334 adresses distinctes** pour 356 identifiants (quelques alias).

#### ★ Le groupe EGR, enfin nommé

| identifiant | RAM |
|---|---|
| **`0x0E80`** | **`0xC4B6`** |
| `0x0E81` | `0xC4E0` |
| `0x0E82` | `0xC4DE` |
| `0x0E87` | `0xC4D4` |
| `0x0E91` | `0xC4DC` |
| `0x0EA2` | `0xC4F6` |
| `0x0EA4` | `0xC4DA` |
| `0x0EA5` | `0xC4D6` |
| `0x0EA7` | `0xC4F4` |
| `0x0EA8` | `0xC4E8` |

⇒ **le bloc EGR vit en RAM `0xC4B6`–`0xC4F6`**.

#### Les records DTC, traduits en adresses RAM

| DTC | identifiants → RAM | lecture |
|---|---|---|
| **P0401/2/3 (EGR)** | `0F10`→`C42E` **régime**, `0F32`→`C3EA`, `0E80`→**`C4B6`**, `0F30`→`C3E8`, `0F80`→`C68A` | le diagnostic EGR compare le **régime** à l’état `C4B6` |
| **P0470 (pression)** | `0F10`→`C42E`, `0F41`→`C60A`, `0F40`→`C612`, `0F42`→`C614`, `0F7F`→`C6E0` | ⚠ rectifié en B.24 : `C60A` = **patmo**, `C612` = pression d’admission, `C614` = limite |
| P0190 / P0191 (rampe) | `0F64`→`C3A8`, `0EA5`→`C4D6`, `2066`→`C376`, `0FFC`→`C3AC` | |

*Données : `identifiants_vers_RAM.csv` (356 lignes), `dictionnaire_identifiants.csv`.*

---

### B.23 — ★★★ `C6A2` = la CHARGE, et le retour aux capteurs par les DTC

#### 1. `C6A2` (identifiant `0x0F8C`) = charge moteur

C’est le **2ᵉ axe** de la famille de cartes « régime (`C42E`) × charge (`C6A2`) » **et** la **mesure** d’une
boucle fermée dont la consigne est `C628`. Ce n’est pas un capteur : c’est une grandeur **calculée,
plafonnée, filtrée**. Aucun DTC ne la surveille ; elle n’apparaît que comme **variable de contexte**
(P1003, P1107, P1429, P1517).

**Preuves :**

1. **Axe de cartes** — 11 cartes : `0xE10BA` (16 pts, 0→7000), `0xE10DE` (8 pts, 500→12000), `0xE13C6`,
   `0xE2AEE`, `0xE5468`, `0xE54F2`, `0xE5602`, `0xE5610`, `0xE609A`, `0xE6102`, `0xE61B2`, `0xE622E`,
   `0xE627A`, `0xE62C6`, `0xE7DAC`, `0xE8E12`, `0xE8EE0`, `0xEAFBA`, `0xEB6CE`.
2. **Structure de carte** — `EA 0xE2ADC` (handle `0x14CE`) :
   `[C42E][0007][02EE 03E8 0514 05DC 07D0 0A28 1388][C6A2][0007][01F4 05DC 1770 1B58 1F40 2328 2710]`
   → régime 750…5000 tr/min, charge 500…10000.
3. **Mesure de boucle** — `sub_D4C1A` (l.241445) : `r13 = C91C = C42E`, `r14 = C94C = C6A2`,
   `unk_2EE2` (2-D), puis `mul r4, word_C7E0` / `divl #2710h` ⇒ résultat en **% de 10000**.
4. **Écart consigne − mesure** — `loc_A3FDA` (l.156386) : `r4 = word_C628 − word_C94C`.
   `C628` = **consigne**, écrite à `loc_B2818` (l.182038). Seuils de bascule en `[cal+#14h..#18h]`.
5. **Producteur borné** — bloc `seg015 0xB71xx–0xB73xx` : `r9` borné ≥ 0 (l.189610), plafonné par
   `[word_142C+#0Eh] + word_C690` (l.189624), `r8 = C6A0 + r9`, machine d’état `C948` ∈ {1,2,3} avec
   compteurs `C0EE`/`C0F0`/`DAF8`, puis `C94C ← r9` → **`C6A2 ← C94C`** (l.189839).
   `word_C690` = **sortie de la carte de limite de fumée** : `unk_1D50(0x1B40 = 0xE8444, C42E, C3E6)`.

⇒ **charge = air admis mesuré, plafonné par la limite de fumée, filtré, maintenu par machine d’état.**
Unité : mêmes décades que les variables d’air ⇒ **mg d’air/tour ×10** (0…12000 ⇔ 0…1200 mg) —
*confiance moyenne* (une plage ne prouve pas une grandeur).

#### 2. Les trois variables d’air, enfin distinctes

| RAM | identifiant | rôle | preuve |
|---|---|---|---|
| `C3E6` = `C3E8` = `C3E2` | **`0x0F30`** | **air admis mesuré** (3 miroirs) | `loc_97324` l.131318-131322 : `[word_15F0+#4]` → `C3E8`, `C3E6`, `C3E2` |
| **`C6A2`** | **`0x0F8C`** | **charge retenue** (axe + boucle) | cf. ci-dessus |
| `C5A8` | `0xE4D2` | masse d’air par tour | DTC P1429 |
| `C3EC` | *(aucun)* | variante d’air, si `byte_C2C9 < 0x30` | l.181913 vs 181922 |

#### 3. Règle de tri : identifiant OU constante dans les records

Les **5 champs** d’un record DTC peuvent porter **un identifiant** (⇒ variable RAM) **ou une constante**.
Sur 93 records : **103 identifiants** seulement sont de vraies variables. Exemples de constantes :
`P0106` → `6463 6968 7270 7574 7776` ; `U0300` → `00C8 0D67 1388 2328` (200, 3431, 5000, 9000) ;
`P0503` → `01F4 F8FF C301`. ⇒ toujours tester la présence dans les 356 du dictionnaire.

#### 4. Tableau maître des identifiants vus dans les records

| identifiant | RAM | nb DTC | grandeur |
|---|---|---|---|
| `0F10` | `C42E` | 53 | **régime** |
| `0F80` | `C68A` | 27 | à nommer |
| `0F7F` (+`0F7C`) | `C6E0` | 18 | à nommer |
| `0F00` | `C3D2` | 16 | **T° LDR** |
| `0F01` | `C3BA` | 14 | à nommer |
| `0F30` | `C3E8` | 13 | **air mg/tour ×10** |
| `0F65` | `C3C2` | 13 | **RCO EGR** |
| `2066` | `C376` | 10 | à nommer |
| `0FFC` | `C3AC` | 9 | à nommer |
| `0F40` | `C612` | 6 | pression échappement/suralim. |
| `0F71`+`0F70` | `C416` | 6+4 | même adresse |
| `0F08`+`000D` | `C562` | 5+1 | même adresse |
| `0F32` | `C3EA` | 5 | 2ᵉ grandeur d’air |
| `0E80` | `C4B6` | 4 | **EGR** |
| `0F60` | `C3C0` | 4 | à nommer |
| `0F8C` | `C6A2` | 4 | **charge** |
| `0FFA` | `C3BE` | 4 | à nommer |
| `E4D1` | `C5B8` | 4 | FAP/turbo |
| `0EA5` / `0F64` | `C4D6` / `C3A8` | 3 / 3 | rampe |
| `0F86` | `C6B4` | 3 | à nommer |
| `E4D3` / `E4D6` / `E4E2` | `C5BC` / `C31E` / `C248` | 3 | FAP, turbo, FAP |
| `0F41` / `0F42` | `C60A` / `C614` | 2 / 1 | **pression échappement** |
| `0FF6` | `C3C6` | 2 | à nommer |
| `0FF8` / `0FF9` | `C7EC` / `C7F0` | 2 | rampe (P1169/70) |
| `0FFB` / `1114` | `C396` / `C39E` | 2 | turbo |
| `E4D4` / `E4D7` / `E4E3` | `C5F4` / `C5A4` / `C228` | 2 | FAP, turbo, FAP |
| `0E82` | `C4DE` | 1 | PAP (P1402) |
| `0E91` | `C4DC` | 1 | **pression clim** (P0530) |
| `0EA2` / `0EA8` | `C4F6` / `C4E8` | 1 | calculateur (P1608) |
| `0F8A` | `C690` | 1 | **sortie limite de fumée** |
| `0FD7` | `C33B` | 1 | FAP (P1435) — octet |
| `0FD8` / `0FF7` | `C6AA` / `C3C8` | 1 | P1003 / P1614 |
| `1E81` | `C4F8` | 1 | P1107 |
| `E4D0` / `E4D2` | `C596` / `C5A8` | 1 | turbo / masse d’air/tour |
| `E4D8`–`E4DB` | `C598` / `C2FA` / `D212` / `C321` | 1 | additif FAP (P1451) |

#### 5. Capteur → DTC → identifiant → RAM

| famille | DTC | identifiants → RAM |
|---|---|---|
| Débitmètre / air | P0100, P0101 | `0F01`→`C3BA`, `0F10`, `0F30`→`C3E8`, `0F32`→`C3EA`, `0F40`→`C612` |
| T° air admission | P0110 | `0F00`→`C3D2`, `0F01`, `0F10`, `0F30`, `0F7F` |
| T° LDR | P0115 | `0F00`→`C3D2`, `0F01`, `0F10`, `0F80`, `2066`→`C376` |
| Pédale / potentiomètres | P0121, P0221 | `0F60`→`C3C0`, `0F71`→`C416`, `0F80`, `0FFA`→`C3BE` |
| T° carburant | P0180 | `0F00`, `0F10`, `0F80`, `0FFC`→`C3AC`, `2066` |
| Pression rampe | P0190/191, P1168 | `0EA5`→`C4D6`, `0F10`, `0F64`→`C3A8`, `0FFC`, `2066` |
| | P1169, P1170 | `0F10`, `0F65`, `0F80`, `0FF8`→`C7EC`, `0FF9`→`C7F0` |
| Injecteurs 1-4 | P0201…P0204 | `0F10`, `0F30`, `0F80`, `0FFC`, `2066` |
| **Préchauffage** | P0381 | `0F00`→`C3D2` **T° LDR**, `0F01`, `0F10` **régime**, `0F65`, `0F7F` |
| **EGR** | P0401…P0403 | `0E80`→**`C4B6`**, `0F10`, `0F30`→**air**, `0F32`, `0F80` |
| Pression d’admission / patmo (⚠ ERRATA B.24) | P0470 | `0F10`, `0F40`→`C612` **mesure**, `0F41`→**`C60A` patmo**, `0F42`→**`C614` limite**, `0F7F` |
| **Pression fluide clim** | P0530 | `0E91`→**`C4DC`**, `0F00`, `0F01`, `0F10`, `0F7F` |
| Batterie / alternateur | P0560/568/571 | `0F08`→`C562`, `0F10`, `0F65`, `0F70`→`C416`, `0F71`, `0F86`, `0F7F` |
| Calculateur / pompe | P0604, P1601/06/08/14 | `0EA2`→`C4F6`, `0EA6`, `0EA8`→`C4E8`, `0FF6`, `0FF7`, `0F65`, `0F7F` |
| Électrovannes EGR/PAP | P1402, P1403, P1404 | `0E80`→`C4B6`, `0E82`→`C4DE`, `0F30`, `0F70`, `0F7F`, `0F80` |
| Turbo / suralim. | P1421, P1425, P1458 | `0FFB`→`C396`, `1114`→`C39E`, `E4D6`→`C31E` |
| | **P1429** | `0F8C`→**`C6A2` charge**, `E4D0`→`C596`, `E4D1`→`C5B8`, `E4D2`→`C5A8` |
| **FAP / additif** | P1435 | `0FD7`→`C33B`, `E4D1`, `E4D3`, `E4E2` |
| | P1442, P1446 | `E4D1`, `E4D3`, `E4D4`→`C5F4`, `E4E2`, `E4E3`→`C228` |
| | P1451 | `0F10`, `E4D8`→`C598`, `E4D9`→`C2FA`, `E4DA`→`D212`, `E4DB`→`C321` |
| Dosage / volet | P1517 / P1521 / P1537 | `0F08`,`0F8C` charge / `0F60`,`0F71`,`0F86` |
| Boîte / CAN / ABS | P0700, U0300/301/303, U1008, C1014 | **littéraux uniquement** |

#### 6. Trois découvertes

1. ~~ΔP FAP nommé par un DTC~~ → **RECTIFIÉ B.24** : P0470 s’appuie sur **`C60A` = patmo**,
   capteur de pression différentielle du filtre travaille dans `C60A`–`C614`.
2. **Préchauffage surveillé en T° LDR × régime** : P0381 = `0F00` + `0F10` — les mêmes axes que la carte
   bougies déjà repérée.
3. **Identifiant ou constante** dans les champs de record (cf. § 3).

*Données : `identifiants_dans_DTC.csv` (103 identifiants), `capteurs_par_DTC.csv`.*

---

### B.24 — ★★★★ `C60A` = PRESSION ATMOSPHÉRIQUE · la carte boost limiter `0xE7828` · ERRATA P0470

#### 1. La carte `EA 0xE7828` = boost limiter = f(Patmo, régime)

`fo 0x67858` (= `EA 0xE7858`) est **la grille** de cette carte (handle `0x1A44`, ptr `0x7828`) :

```
EA 0xE7828 : [C60A][10] 600 700 750 800 850 900 925 950 975 1050
EA 0xE7840 : [C42E][10] 1000 1250 1500 2000 2500 3000 3500 4000 4500 5000
EA 0xE7858 : grille 10 x 10  (fo 0x67858)
```

Consommateur (l.174279) : `r12 = word_1A44`, `r13 = word_C940 (= C60A)`, `r14 = word_C91C (= C42E)`,
`unk_1D50` → `sub_9FF46(consigne, limiteur)` → `C946` → **`C614`** (l.174392).

| Patmo \ régime | 1000 | 1500 | 2000 | 2500 | 3000 | 3500 | 4000 | 5000 |
|---|---|---|---|---|---|---|---|---|
| 600  | 1000 | 1120 | 1325 | 1375 | 1415 (2.36) | 1455 | 1355 | 1159 |
| 700  | 1000 | 1250 | 1520 | 1605 | 1645 (2.35) | 1635 | 1520 | 1359 |
| 800  | 1040 | 1440 | 1745 | 1835 | 1880 (2.35) | 1830 | 1725 | 1570 |
| 900  | 1170 | 1640 | 1960 | 2070 | 2130 (2.37) | 2045 | 1950 | 1780 |
| 950  | 1240 | 1750 | 2070 | 2200 | 2270 (2.39) | 2200 | 2130 | 1840 |
| 1050 | 1330 | 1850 | 2150 | 2370 | 2370 (2.26) | 2300 | 2150 | 1840 |

**Preuve** : à régime fixe, valeur / Patmo = **rapport de compression constant ≈ 2.35-2.39** ⇒ l’axe ne
peut être qu’une **pression d’entrée du compresseur** = pression atmosphérique. Valeurs 1000-2370 =
1.0-2.37 bar **absolus**.

#### 2. `C60A` = pression atmosphérique (hPa) — quatre autres preuves

1. **Repli en calibration** : `word_C60A ← word_C38E` (l.172644-645), et `word_C38E = [word_1418+8]`
   (l.212327) = **constante de calibration** (capteur absent).
2. **Figée dans le contexte de tous les diagnostics** : `mov word_C940, word_C60A` dans chaque routine
   de défaut (l.131371, 133066, 134627, 166288, 170987, 171250).
3. **Filtrage lent** : `C940 = (C940 + D854 + courbe(régime)) / 2` — référence moyenne, lente.
4. **13 courbes et 3 cartes l’ont pour axe** ⇒ famille « altitude ».

#### 3. La chaîne de pression

```
C3B2 -> unk_1E50(word_19FA, C3B2, #0D852h) -> D854
        C612 = D854 + C3B4      (l.172880)   C3B4 = offset capteur
        C60A = repli / filtre   (l.172882, 172645)
C60E = C68A | C6B6 | C6B8       (l.174217, choix par word_141E+0x26)
  unk_1D50(1A4C/1A4A, régime, C60E) -> D348 consigne
  unk_1D50(1A46,      patmo,  C60E) -> D344
  unk_1D50(1A44,      patmo,  régime) -> D34A boost limiter
        sub_9FF46(consigne D34E, limiteur D34A) -> C946 -> C614
```

| RAM | rôle |
|---|---|
| `C60A` | **pression atmosphérique** (hPa) |
| `C612` | **pression d’admission absolue** (mbar, axes 1000-2200) |
| `C614` | **pression maximale autorisée** (boost limiter) |
| `C60E` | variable d’entrée des consignes (sélectionnée) |
| `C3B4` | offset du capteur de pression |
| `C38E` | patmo de repli (constante de calibration) |

#### 4. ⚠ ERRATA sur B.23 — P0470

`P0470` = `0F41`→**`C60A` patmo**, `0F40`→`C612` mesure, `0F42`→`C614` limite.
⇒ **c’est le capteur de pression d’admission et sa cohérence avec la patmo**, PAS le ΔP du FAP.
**Le ΔP FAP reste à identifier** (à chercher dans P1435 / P1442 / P1446).
Les lignes de B.23 concernées ont été rectifiées.

#### 5. La famille « altitude » keyée sur `C60A`

| EA | type | axe | valeurs / rôle |
|---|---|---|---|
| **`0xE7828`** | 2-D | C60A × C42E | **boost limiter absolu** 1000-2370 mbar ★ |
| `0xE71F6` | 2-D | C60A × D004 | 9 × 9 |
| `0xE7920` | 2-D | C60A × C60E | 9 × 9 |
| `0xE3EF4` | 1-D | 743 … 1100 | **11000 … 10000** (×1.10 → ×1.00) ; axe 743-750 pas de 1 = **patmo mémorisée** |
| `0xE69FA` | 1-D | 700 … 1050 | 10000 10000 10000 **7500 5000 0 0 0** = **dérate altitude** |
| `0xE6050` | ambigu | 820 … 1060 | axe 9 pts + 8 valeurs → **non résolu** |
| `0xE3C64` `0xE6038` `0xE6066` `0xE620A` `0xE6ACE` | 1-D | 0 … 1800 | **10000 partout = gain neutre** |
| `0xE39B0` `0xE6A5E` `0xE6B46` `0xE6B86` `0xEBA58` | 1-D | 0 … 1800 | **0 partout** |
| `0xE39C8` | 1-D | 700 … 1000 | 10000 partout |

---

### B.25 — ★★★★ `C68A` = 0x0F80 = la CHARGE DE BASE · `C60E` · la charge est du CARBURANT

#### 1. `C68A` n’a que deux écrivains — et il est produit avec `C6A2`

```
C690 = unk_1D50(handle 0x1B40 = EA 0xE8444, C42E, C3E6)   <- carte LIMITE DE FUMEE
C6B0 = sub_B33DC(C6BA)                              (l.178866)
C6BC = min( C690 - C69C , C6B0 )                    (l.178878-178894)
C68A = C6BC + C69C        (l.189637 + 189836)  <- charge de BASE
C6A2 = r9, borne par [word_142C+#0Eh] + C690  (l.189624 + 189839)  <- charge FINALE
```

| RAM | rôle |
|---|---|
| **`C68A`** | **charge de base** (limite de fumée écrêtée puis ré-offsetée) |
| **`C6A2`** | **charge finale** (indexe les cartes) |
| `C690` | sortie de la carte de fumée `0xE8444` |
| `C6BC` / `C69C` / `C6B0` | limite moins offset / offset / plafond secondaire |

`C68A` sert d’axe d’interpolation : l.190628, 195721, 197906, 197911, 204199.

#### 2. `C60E` = charge retenue, trois variantes (`loc_AE2B6`, l.174194-174217)

| `word_141E+0x26` | source de `C60E` |
|---|---|
| 0 ou 1 | **`C68A`** (0x0F80) |
| 2 | `C6B6 = D9A6 + C69E` (l.183252) |
| 3 | `C6B8 = C6A6 + C69E` (l.182757) |

⇒ `C68A`, `C6B6`, `C6B8`, `C60E` = **quatre formes de la même grandeur : la charge demandée**.

#### 3. La consigne de suralimentation `EA 0xE7A00` (handle `0x1A4A`)

`[C42E][16] 0…5500` × `[C60E][10] 0 800 2000 3200 3600 4000 4500 5000 6000 7000`

| régime \ charge | 0 | 800 | 2000 | 3200 | 3600 | 4000 | 4500 | 5000 | 6000 | 7000 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 800 | 800 | 800 | 800 | 800 | 800 | 800 | 800 | 800 | 800 |
| 1000 | 1030 | 1030 | 1040 | 1090 | 1110 | 1150 | 1175 | 1200 | 1200 | 1200 |
| 1500 | 1050 | 1060 | 1080 | 1204 | 1272 | 1370 | 1490 | 1580 | 1755 | 1800 |
| 2000 | 1070 | 1080 | 1150 | 1354 | 1452 | 1540 | 1660 | 1780 | 1980 | 2100 |
| 2500 | 1090 | 1110 | 1250 | 1462 | 1556 | 1645 | 1765 | 1870 | 2050 | 2200 |
| 3000 | 1110 | 1124 | 1308 | 1570 | 1650 | 1740 | 1835 | 1930 | 2110 | 2200 |
| 4000 | 1110 | 1130 | 1330 | 1624 | 1722 | 1810 | 1900 | 2000 | 2130 | 2150 |
| 5500 | 1110 | 1130 | 1330 | 1508 | 1574 | 1630 | 1680 | 1740 | 1830 | 1830 |

**800 → 2200 mbar absolus** = consigne de pression de suralimentation, cohérente avec la limite `C614`
(≤ 2370 mbar, B.24). Axe 2 = la charge.

Courbes associées : `0xE65A4` (C60E 800→7000 ⇒ **1050 → 1200**, plancher) ; `0xE7936` (C60E 0→7000 ⇒
**−300 … −400**, offset) ; `0xE6D28` (`C6B6` 0→10000 ⇒ 0 partout, neutralisée).

#### 4. ★ La charge est du CARBURANT (mg/tour × 100)

| indice | calcul |
|---|---|
| sortie de la carte de fumée `0xE8444` | 1750 → 7600 ⇒ **17.5 → 76 mg/tour** si ×100 |
| axes de la famille `C6A2` | 500/1500/6000/7000/8000/9000/10000 ⇒ **5/15/60/70/80/90/100 mg** |
| axe de `C6B6` (`0xE6D28`) | 0 → **10000** ⇒ plafond 100 mg du limiteur de débit |
| structure | pression rail/suralimentation = f(régime, **quantité injectée**) — jamais f(air) |

⇒ **`C6A2` et `C68A` = quantités de CARBURANT (mg/tour × 100).** Confiance **élevée**, pas encore
prouvée : manque le point où `C6A2` devient un temps d’injection.

#### 5. ⚠ Révision du décompte « cartes à axe C6A2 » (B.23)

Plusieurs « axes » étaient des **courbes 1-D** dont les valeurs ressemblent à un axe (`0xE609A`, `0xE5610`…).
Nouvelle règle : retenir l’axe seulement si `n1 × n2` mots tiennent entre l’axe et la structure suivante
avec deux suites strictement croissantes.

| statut | EA |
|---|---|
| **carte 2-D établie** — f(régime, charge), offsets −160…0 | **`0xE2ADC`** (7×7) |
| cartes probables | `0xE13C6`, `0xE7DAC` |
| **4 descripteurs d’axes sans grille — POINT OUVERT** | `0xE1082` : C68A(16) · C68A(8) · C6A2(16) · C6A2(8) |
| courbes 1-D sur la charge | `0xE609A` `0xE6102` `0xE61B2` `0xE622E` `0xE627A` `0xE62C6` `0xE8E12` `0xE8EE0` `0xE963A` `0xEAFBA` `0xEB6CE` `0xE6D28` |

---

### B.26 — ★★★★ LA BANQUE D’AXES et les cartes SANS AXES (16×16, 9×9)

#### 1. Banque d’axes `EA 0xE100A`–`0xE10F1` (handles `0x1400`–`0x1412`)

| handle | EA | tag | n | valeurs |
|---|---|---|---|---|
| `0x1400` | `0xE100A` | **C42E** | 8 | 200 400 600 1250 1750 2250 2500 4000 |
| `0x1402` | `0xE101E` | **C42E** | 2 | 650 1200 |
| `0x1404` | `0xE1026` | **C42E** | 16 | 200…5000 |
| `0x1406` | `0xE104A` | **C42E** | 16 | idem 0x1404 |
| `0x1408` | `0xE106E` | **C42E** | 8 | idem 0x1400 |
| `0x140A` | `0xE1082` | **C68A** | 16 | 0 200 400 … 6000 7000 |
| `0x140C` | `0xE10A6` | **C68A** | 8 | 400 2000 2800 4000 4500 6000 8000 11000 |
| `0x140E` | `0xE10BA` | **C6A2** | 16 | identique à 0x140A |
| `0x1410` | `0xE10DE` | **C6A2** | 8 | 500 1000 2000 4000 6000 8000 11000 12000 |
| `0x1412`–`0x141A` | `0xE10F2`–`0xE1112` | — | 1/4/5/6/6 | scalaires |

⇒ `C68A` et `C6A2` ont **les mêmes 16 points de rupture** (0…7000) : deux variables de même nature.

#### 2. Le mécanisme des cartes sans axes

```
unk_2F56(&pos1, variable1, handle_axe1)      ; position dans l’axe (3 mots)
unk_2F56(&pos2, variable2, handle_axe2)
unk_2FAC(&pos1, &pos2, handle_grille)       ; lecture de la GRILLE NUE
```

`sub_D4D0A` (l.241558-241576) : axes `word_14D6`/`word_14D8`, grille `word_14D0` ou `word_14D2`.
`loc_D4848` (l.241049) : `unk_2FAC(0xC9BA, 0xC9C6, word_14C6)`.
**C’est l’explication mécanique de la règle « des maps n’ont pas d’axes ».**

#### 3. Cartes sans axes trouvées

| EA | handle | mots | dimension | contenu |
|---|---|---|---|---|
| **`0xE2816`** | `0x14C6` | **256** | **16 × 16** | **tout à zéro (fonction neutralisée)** |
| `0xE2B62` | `0x14D0` | 252 | ? | tout à zéro |
| `0xE2D5A` | `0x14D2` | 252 | ? | tout à zéro |
| `0xE130E` | `0x1444` | **81** | **9 × 9** | tout à zéro |
| `0xE2078` | `0x1446` | **81** | **9 × 9** | tout à zéro |
| `0xE211A` | `0x1448` | **81** | **9 × 9** | tout à zéro |

Axes de `0xE2816` = `word_1404` (régime 16 pts) × `word_140E` (charge 16 pts).
Variantes `0xE2B62` / `0xE2D5A` sélectionnées par **`byte_C2C1`** (1 → 0x14D0, 3 → 0x14D2).

#### 4. ★ Méthode nouvelle : la table des handles donne la TAILLE des objets

Écart entre deux pointeurs consécutifs = taille exacte de l’objet. Vérifié :

| objet | mots mesurés | structure | accord |
|---|---|---|---|
| `0xE7828` boost limiter | **124** | 2+10+2+10+100 | ✔ |
| `0xE2ADC` f(régime, charge) | **67** | 2+7+2+7+49 | ✔ |

844 handles pointent dans le Datensatz ⇒ plan cadastral complet de la calibration.

#### 5. Ouvert

1. Les **252 mots** de `0xE2B62`/`0xE2D5A` : ni 16×16 ni 14×18 — non tranché.
2. Comment les grilles nues **9×9** sont consommées (`word_1444` passée en `r14` d’un `unk_1D50`).
3. Les 5 objets scalaires `0xE10F2`–`0xE111D`.

---

### B.27 — ★★★★ CORRECTION : les cartes « à zéro » ne le sont pas · `0xE2816` = avance (SOI) 16×16

#### 1. ⚠ Correction d’une affirmation de B.26

« tout à zéro » était **faux** : je n’avais lu que les six premiers mots. Contenus réels :

| EA | mots | non nuls | min | max |
|---|---|---|---|---|
| **`0xE2816`** | 256 (16×16) | **229/256** | **−37** | **1067** |
| `0xE130E` | 81 (9×9) | 64 | 0 | 15437 |
| `0xE2078` | 81 (9×9) | 64 | 0 | 17920 |
| `0xE211A` | 81 (9×9) | 64 | 0 | 13184 |
| `0xE2B62` | 252 | 147 | 0 | **+200** |
| `0xE2D5A` | 252 | 134 | **−175** | 0 |

#### 2. `0xE2816` = f(régime C42E [16], charge C6A2 [16]) — avance à l’injection

Axes prouvés (l.239933-239968) : `unk_2F56(0xC9BA, C42E, word_1404)` et
`unk_2F56(0xC9C6, C6A2, word_140E)`, puis `unk_2FAC(0xC9BA, 0xC9C6, word_14C6)` (l.241049).

| régime \ charge | 0 | 1200 | 2000 | 2800 | 3600 | 4500 | 6000 | 7000 |
|---|---|---|---|---|---|---|---|---|
| 800  | −37 | −35 | 20 | 40 | 80 | 44 | 44 | 44 |
| 1500 | 126 | 29 | 29 | 29 | 79 | 139 | 232 | 272 |
| 2000 | 153 | 52 | 52 | 53 | 107 | 188 | 320 | 362 |
| 2500 | 229 | 93 | 93 | 102 | 166 | 267 | 387 | 427 |
| 3500 | 388 | 275 | 366 | 454 | 571 | 638 | 683 | 683 |
| 4500 | 597 | 809 | 896 | 937 | 972 | 981 | 981 | 981 |
| 5000 | 683 | 881 | 960 | 990 | 1015 | 1043 | 1067 | 1067 |

Croissance dans les deux directions ⇒ **avance**. Plancher négatif à bas régime = correction de ralenti.

**Consommateur** (l.240996-241052) : `r15 = C756 + C73E + C74E + C748 + C766 + C770` (six correctifs),
`D518 = r15`, puis `+ carte 0xE2816`, plafond `word_C754` → `D51A`. **Base + corrections + plafond** =
structure d’un calcul d’avance. Unité non établie (0,02 °CA ⇒ 21,3° max).

#### 3. Vérification de la méthode de dimensionnement (B.26 §4)

Test : taille calculée `2+n1+2+n2+n1·n2` vs écart entre handles consécutifs.
**34 accords**, **3 désaccords** :

| EA | écart | calculé | cause probable |
|---|---|---|---|
| `0xE39C0` | 12 | 6 | handle pointant **à l’intérieur** d’un objet |
| `0xE6952` | 66 | 18 | objet voisin non référencé |
| `0xE6E7E` | 102 | 18 | objet voisin non référencé |

⇒ la méthode donne une **borne** ; confirmer par la structure interne. Des objets **orphelins** existent.

#### 4. `0xE2B62` / `0xE2D5A` : 14 × 18 (dimension résolue)

Axes (`sub_D4D0A`, l.241558-241576) :

| handle | EA | tag | n | valeurs |
|---|---|---|---|---|
| `0x14D6` | `0xE2F6A` | **C7C2** | 14 | 1190 1200 2000 3000 4000 5000 6000 7000 8000 9000 10000 11000 12000 13500 |
| `0x14D8` | `0xE2F8A` | **C78A** | 18 | 0 200 1000 1500 2000 3000 4000 6000 7000 7100…7900 (pas de 100) |

`C7C2` 1190→13500 = **pression rail × 0,1 bar** (119 → 1350 bar, probable).
Les deux grilles = **couple d’offsets opposés** (+0…+200 vs −175…0), variantes par `byte_C2C1`.

#### 5. Les grilles 9×9

Axes 9 points : `0x144A` C42E (0…4500), `0x144C` C6A2 (0…8000), `0x144E` **C63C** (0 1707 3413 5120
6827 8533 10667 12800 15360) ⇒ **pression rail × 0,1 bar** (0 → 1536 bar).

Consommateur (l.177865-177910) : `r7 = <grandeur> − word_C678` (borné ≥ 0) → `unk_1D6C(pos, r7, word_144E)`
→ `word_1D94(0xC83E, pos, word_1446)` → `[r0+#8]` + bit `byte_C335.#8`.

**Hypothèse** : correction de débit/durée en fonction de l’**écart de pression rail** (dérive d’injecteur).
Max 17920 ⇒ 1,79 ms si µs×0,1. Non tranché (manque le coefficient appliqué après `[r0+#8]`).

---

### B.28 — ★★★ `D51A` = identifiant `0x1F4D` · couverture réelle du Datensatz · 4 zones orphelines

#### 1. L’avance est une grandeur EXPORTÉE

`word_D51A` reçoit la valeur de la carte `0xE2816` (l.241052) et porte l’identifiant **`0x1F4D`** dans le
dictionnaire identifiant → RAM (B.22). Elle figure aussi dans le catalogue des 92 grandeurs (`EA 0xEA254`,
position 71). ⇒ **le code ne la relit pas, il la publie.** Identifiant `0x1F4D` = **lisible au diagnostic**.

| identifiant | RAM | note |
|---|---|---|
| `0x1F40` | `C3AE` | — |
| `0x1F41` | `C73C` | voisin de `C73E` |
| `0x1F42` | `D52A` | — |
| **`0x1F4D`** | **`D51A`** | **sortie de la carte d’avance `0xE2816`** |
| `0x1F4E` / `0x1F4F` | `D520` / `D51E` | — |
| `0x1F50` | `C736` | — |
| `0x1F51` / `0x1F52` / `0x1F53` | `D532` / `D54C` / `D570` | — |
| `0x1F55`+`0x1F56` | `C7DA` | même adresse |
| `0x1F58` | `C7CC` | — |
| `0x1F59` | `C73E` | **un des 6 correctifs de l’avance** (l.241003) |
| `0x1F5A` / `0x1F5B` | `D528` / `D544` | — |
| `0x1F5E` / `0x1F5F` | `C7B8` / `C7C6` | — |
| `0x1F63` | `D574` | — |
| **`0x1F64`** | **`C78A`** | **axe 18 points des grilles 14×18** |
| **`0x2109`** | **`C63C`** | **axe 9 points « pression rail » (0 → 15360)** |

⚠ Piège : `sub_CD506` (l.227574) `add r0, #0D51Ah` + `jmpi [r0]` = **base de table de sauts dans le code**,
et non l’adresse RAM `0xD51A`.

#### 2. ⚠ Correction : deux bugs dans mon balayage de la table des handles

| version | erreur | conséquence |
|---|---|---|
| 1 | filtre `ptr < 0x8000` | tous les pointeurs ≥ `0x8000` perdus ⇒ moitié haute du Datensatz (dont la carte de fumée `0xE8444`) invisible |
| 2 | boucle arrêtée à `0x1DFE` | ~25 handles perdus |
| **3 (bonne)** | 1 305 entrées, handles `0x1400`–`0x1E2E` | **1 304 objets** distincts |

| mesure | valeur |
|---|---|
| entrées table `0x61400` | **1 305** |
| objets distincts | **1 304** |
| couverture | `EA 0xE100A` → **`0xEBC38`** |
| avant le 1ᵉʳ handle | `0xE0000`–`0xE1009` = 2 053 mots (**records DTC**, référencés autrement) |
| après le dernier | **448 mots** |

⇒ « 8 157 mots non référencés » (B.27) était un **artefact**. La calibration est référencée à ~99 %.

#### 3. Les 4 zones orphelines (176 mots)

| EA | handle | écart | structure | résidu | contenu |
|---|---|---|---|---|---|
| `0xE39C0` | `0x15EC` | 12 | 6 | 6 | axe 2 pts + valeurs |
| `0xE6952` | `0x199C` | 66 | 18 | **48** | escalier **74 → 120** par paliers |
| `0xE6E7E` | `0x19FC` | 102 | 18 | **84** | `3500 4000 4500 5012` puis **3500 × 80** |
| `0xE868C` | `0x1B42` | 52 | 14 | **38** | `14016 18000 0` + 4 lignes `0,X,X,X,X,X` (X = **9230, 8150, 4210, 1280**) |

`0xE86A8` est **juste avant la carte de préchauffage `0xE86F4`** ⇒ priorité d’instruction.

---

### B.29 — ★★ Carte 6×6 préchauffage · **Kelvin ×10** · errata des zones orphelines

#### 1. ⚠ Les « zones orphelines » de B.28 n’existent pas

Parseur corrigé (2-D testée avant 1-D, acceptée seulement si elle remplit **exactement** l’écart).
`0xE86A8` = grille de la carte `0xE868C` (handle `0x1B42`), taille 52 mots = écart exact.

| résultat sur 1 303 objets | nombre |
|---|---|
| cartes 2-D à en-tête complet | **48** |
| courbes 1-D à en-tête complet | **30** |
| **objets sans en-tête** | **1 079** |
| taille incohérente | 146 |

⇒ le Datensatz est **contigu et entièrement référencé** ; mais **1 079 objets / 1 303 n’ont aucun en-tête**
⇒ « des maps n’ont pas d’axes » est la **règle majoritaire**, pas l’exception.

#### 2. Carte 2-D `0xE868C` (h `0x1B42`) — 6 × 6

```
[0xC3D2][6] [2431 2531 2631 2731 2831 3831]   axe Y = température LDR
[0xC562][6] [0 300 10000 12000 14016 18000]   axe X = C562
[36 valeurs]
```

| T LDR ↓ / C562 → | 0 | 300 | 10 000 | 12 000 | 14 016 | 18 000 |
|---|---|---|---|---|---|---|
| **2431** | 0 | **9230** | 9230 | 9230 | 9230 | 9230 |
| **2531** | 0 | **8150** | 8150 | 8150 | 8150 | 8150 |
| **2631** | 0 | **4210** | 4210 | 4210 | 4210 | 4210 |
| **2731** | 0 | **1280** | 1280 | 1280 | 1280 | 1280 |
| **2831** | 0 | 0 | 0 | 0 | 0 | 0 |
| **3831** | 0 | 0 | 0 | 0 | 0 | 0 |

Première colonne nulle + valeur constante par ligne + effondrement avec la température ⇒ **durée de
préchauffage** (profil attendu à cet endroit du segment).

#### 3. ★★ Clé de décodage : températures en **Kelvin ×10**

`T[°C] = valeur/10 − 273,1`

| valeur | 2431 | 2531 | 2631 | 2731 | 2831 | 3831 |
|---|---|---|---|---|---|---|
| **°C** | **−30** | −20 | −10 | **0** | **+10** | **+110** |

Arguments : (1) plage −30…+110 °C canonique ; (2) l’objet voisin `0xE870C` est un axe 9 pts
`2431…2931` = **−30…+20 °C** (axe de démarrage à froid) ; (3) graduations rondes.
⇒ **clé applicable à tout axe portant `0xC3D2` (T LDR) ou `0xC3B0` (T carburant)**.
⚠ Ce sont des **graduations d’axe**, pas des mesures : l’échelle des grandeurs reste à confirmer.

#### 4. Objets voisins

| EA | handle | structure | taille = écart |
|---|---|---|---|
| `0xE86F4` | `0x1B44` | `[0xC3AE][10][0 50 300 500 600 1000 1150 1250 1750 1760]` | 12 ✓ |
| `0xE870C` | `0x1B46` | `[0xC3D2][9][2431 2531 2631 2731 2831 2931 …]` | axe d’un objet plus grand |

`0xC3AE` porte l’identifiant `0x1F40` ⇒ grandeur mesurable.

#### 5. `C562`

3 écritures / 100 références : `word_C562 ← word_C3FA` (`sub_CF8C8` l.232358), `← 0xFF` (secours,
`sub_CF8A4` l.232352), `← MDL` (l.232870). Employée en **seuil** (`cmp r5, word_C562`) et comme axe X.
⇒ **paramètre/limite recopié**, pas une mesure (candidats : compteur ou seuil d’auto-adaptation).

#### 6. Queue du Datensatz `0xEBC38`–`0xEBFB9` (449 mots) — pas une zone de cartes

| contenu | mots |
|---|---|
| `0xC3C3` remplissage | **152** |
| `0x0000` | **188** |
| `0xFFFF` | **60** |
| autres (42 distincts) | 49 |

Îlot `[0xC3BA][3][2681 2831 2832]` ; résidus ASCII `75vGB075WF2S010384` (`0xEBF04`), `1037353776` (`0xEBFB0`).
⇒ **la calibration s’arrête là.**

---

### B.30 — ★★★ Kelvin ×10 **validée** : 53 axes de température · `C3BA` = 3ᵉ température

#### 1. Test décisif

| contrôle | résultat |
|---|---|
| axes de température détectés (`C3D2`, `C3B0`, `C3BA`) | **53** |
| valeurs tombant sur un **entier de °C** | **283 / 290 = 98 %** |

⇒ **`T[°C] = valeur/10 − 273,1` ACQUISE.** Les 2 % restants sont des faux positifs de détection
(valeurs −19,4 / 143,3 / 133,6).

#### 2. Les 53 axes de température ( °C )

| EA | grandeur | n | points |
|---|---|---|---|
| `0xE2F52` | T_LDR | 5 | 17 40 60 80 100 |
| `0xE3820` | T_LDR | 4 | −30 −10 10 30 |
| `0xE38E0` | C3BA | 6 | −15 0 10 17 37 60 |
| `0xE3918` | T_LDR | 6 | −20 −10 0 15 20 40 |
| `0xE39C0` | C3BA | 2 | −20 60 |
| `0xE3CF0` | T_LDR | 2 | −20 0 |
| `0xE3E50` | C3BA | 4 | −5 17 35 50 |
| `0xE68D0` | T_LDR | 8 | −30 10 17 19 25 50 70 80 |
| `0xE68FC` | T_LDR | 4 | −25 −18 −10 −1 |
| `0xE6946` | T_LDR | 2 | −20 0 |
| `0xE69D6` | C3BA | 8 | −25 −18 −10 0 10 17 30 40 |
| `0xE6A1E` | T_LDR | 6 | −25 −18 20 60 80 100 |
| `0xE6A3A` | C3BA | 8 | −30 −10 0 10 20 30 40 60 |
| `0xE6A6A` | T_LDR | 8 | −25 −18 −10 0 10 30 60 80 |
| `0xE6A8E` | T_carb | 6 | 54 64 74 84 93 120 |
| `0xE6AAA` | C3BA | 8 | −35 −30 −20 −10 0 15 17 20 |
| `0xE6AF2` | T_LDR | 8 | −25 −18 −10 0 10 30 60 70 |
| `0xE6B16` | T_carb | 2 | −20 0 |
| `0xE6B52` | T_LDR | 12 | 0 10 30 40 50 51 80 100 101 102 103 104 |
| `0xE6B92` | T_LDR | 2 | −50 150 |
| `0xE6B9E` | T_LDR | 8 | −25 −18 −10 0 10 30 60 70 |
| `0xE6BC2` | T_LDR | 8 | −25 −18 −10 0 10 30 60 80 |
| `0xE6BE6` | T_carb | 6 | 54 64 74 84 93 120 |
| `0xE6DBC` | T_LDR | 6 | −50 −20 0 50 100 150 |
| `0xE6E7E` | C3BA | 8 | −20 −10 0 10 20 40 60 80 |
| `0xE6F4A` | C3BA | 6 | −50 0 28 40 50 100 |
| `0xE6FDE` | T_LDR | 10 | −25 −20 −15 −10 −5 0 5 10 30 50 |
| `0xE7E18` | T_LDR | 6 | −25 −18 −10 0 15 20 |
| `0xE7F92` | T_carb | 4 | 87 91 93 102 |
| `0xE8014` | T_carb | 6 | 32 54 64 84 93 102 |
| `0xE8084` | T_LDR | 6 | −20 −10 0 20 50 65 |
| `0xE80B4` | T_LDR | 10 | −25 −18 −10 0 10 20 40 60 80 100 |
| `0xE816C` | T_LDR | 6 | −18 −10 0 30 50 90 |
| `0xE8188` | T_LDR | 6 | −30 −25 −10 10 80 100 |
| `0xE81E2` | T_LDR | 8 | −30 −20 −10 0 20 40 60 80 |
| `0xE8386` | T_LDR | 2 | 0 100 |
| `0xE839A` | T_LDR | 2 | 0 100 |
| `0xE868C` | T_LDR | 6 | −30 −20 −10 0 10 110 (carte 6×6, B.29) |
| `0xE870C` | T_LDR | 9 | −30 −20 −10 0 10 20 40 60 80 |
| `0xE881A` | T_LDR | 6 | 111 112 113 116 119 122 |
| `0xE8F88` | C3BA | 2 | −40 0 |
| `0xE91E4` | T_LDR | 9 | −30 −20 0 25 40 60 80 95 110 |
| `0xE9E72` | T_LDR | 8 | −20 0 20 40 60 80 100 120 |
| `0xEAFCA` | T_LDR | 2 | −30 60 |
| `0xEB9DA` | T_LDR | 2 | −30 −20 |
| `0xEBA64` | T_LDR | 2 | −30 10 |
| `0xEBA78` | T_LDR | 2 | 0 140 |
| `0xEBB54` | T_LDR | 5 | −30 0 20 60 100 |

Faux positifs écartés : `0xE7440`, `0xE7CF8`, `0xE7F1E`, `0xE91D8`, `0xEBBDC`.

#### 3. ★ `C3BA` = troisième température

| tag | identifiant | axes | rôle |
|---|---|---|---|
| `0xC3D2` | `0x0F00` | 36 | T liquide de refroidissement |
| `0xC3B0` | `0x0F02` | 5 | T carburant |
| **`0xC3BA`** | **`0x0F01`** | **12** | **troisième température** (même clé de décodage) |

Candidats : T air d’admission, T huile, T EGR. Le groupe DTC de `C3BA` = 14 codes (B.23) ⇒ à trancher par ses DTC.

#### 4. `C562` = paramètre **adapté**, pas une mesure

| site | écriture |
|---|---|
| `sub_CF8C8` l.232358 | `word_C562 ← word_C3FA` |
| `sub_CF8A4` l.232352 | `word_C562 ← 0xFF` (défaut) |
| l.232870 | `word_C562 ← MDL` |
| l.139595 (reset) | `word_C3FA ← [h 0x1654]` = `[0xE400A]` = **0** |
| l.142744 (adaptation) | `word_C3FA ← [h 0x1470 + 6]` = `[0xE2260]` = **8000** |

#### 5. `sub_CE9B4` (l.230432) = gestionnaire d’états par item

`add r3,#21D4h` (table d’états) · `shl r5,#2 ; add r5,#0CAD0h` (4 octets/item) · `[r4+#0FD21h]` (masque) ·
`bmovn r0.1, Z` (drapeau valide) · `extp #3 ; mov [r3], word_E1D2` (compteur). Appelé avec
`r2 = #1FFDh / #1FFEh / #3DEFh` et `r1 = word_1686 / word_185E / word_1862`.

#### 6. Verrou restant : la carte des DPP

`DPP0 = 0x22`, `DPP1 = 0x21`, `DPP2 = 0x24 / 0x48`, `DPP3 = 3` (l.96805-96808, 125397, 233064).
Tant que `DPP × 0x4000 → adresse linéaire` n’est pas établie, **toutes les lectures indirectes** restent ambiguës.

---

### B.31 — ★ Deux chaînes résolues : `C78A` = accumulateur d’avance · `C3AE` = `[0xF884]`

#### 1. `word_C78A ← word_F99E ← r15` = **l’accumulateur d’avance**

```
l.240948 : word_F99E, r15          r15 = C756+C73E+C74E+C748+C766+C770 (six correctifs)
l.241092 : saturations #7FFFh / #8000h
l.241148 : word_C78A ← word_F99E
l.241149 : calls sub_D4D0A           → r4 = sortie de la carte
l.241152 : add r14, r4              → la sortie SE RAJOUTE à l’avance
```

⇒ la carte 14 × 18 (`0xE2B62` / `0xE2D5A`) est une **correction d’avance = f(pression `C7C2`, avance `C78A`)**.

#### 2. `sub_D4D0A` (l.241558) — mécanisme intégral

```
byte_C2C1 = 1 → r15 = word_14D0 (grid 0xE2B62)   |   3 → r15 = word_14D2 (grid 0xE2D5A)
unk_2F56(r1=0xE5B0, r2=C7C2, r3=word_14D6)   → position X
unk_2F56(r1=0xE5B6, r2=r14 (C78A), r3=word_14D8) → position Y
unk_2FAC(0xE5B0, 0xE5B6, r15)                → valeur interpolée
```

`0xE5B0` / `0xE5B6` = positions d’interpolation en RAM (et non des adresses de calibration).

#### 3. `C3AE ← [0xF884]`

`mov r9, #0F884h` · `mov r9, [r9]` · `sub_C4AAE(word_1548, r9)` · `word_C3AE ← r9` (l.214368-214374),
ainsi que `word_D05A` et `word_C374`. `0xF884` n’est pas un symbole nommé : c’est un **pointeur de
structure** (aussi l.213595, 213974, 217875). Chemins de secours : `C3AE = 0` (l.205130).

#### 4. Points ouverts (détail : `ETAPE85_chantiers_et_verrous.md`)

| # | objet | blocage |
|---|---|---|
| 1 | unité de l’avance | loger `0x1F4D` |
| 2 | `C7C2` (14 pts, 1190…13500) | pas d’identifiant ⇒ comparaison au rail |
| 3 | `C3AE` | identifier le bloc `0xF880` |
| 4 | `C562` | paramètre appris (km ? heures ?) |
| 5 | `C63C` = `0x2109` | logger `0x2109` |
| 6 | `C678` | aucune écriture tracée |
| 7 | 1 079 objets sans en-tête | passer par `unk_2F56` + `unk_2FAC` |
| 8 | carte des DPP | taille RAM/EEPROM du μC |
| 9 | `C3BA` | T air / huile / EGR — par ses 14 DTC |

---

### B.32 — ★★★★★ CARTE D’AVANCE EN DEGRÉS · facteur `0,0234375` · errata `C63C` = angle

#### 1. Le facteur (acquis)

**`0,0234375 °CRK` par LSB** = 360° / 15 360 pas. Offset **0** (convention PSA, BTDC).
Plage brute de `0xE2816` : −37 … 1067 ⇒ **−0,87° … +25,01°**.

#### 2. La carte complète ( ° avant PMH )

Axes : régime `C42E` 200 → 5 000 tr/min × charge `C6A2` 0 → 7 000.

| IQ / tr/min | 200 | 400 | 600 | 800 | 1000 | 1250 | 1500 | 1750 | 2000 | 2250 | 2500 | 3000 | 3500 | 4000 | 4500 | 5000 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **0** | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 | 1.0 | 3.0 | 3.0 | 2.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| **200** | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 | 1.0 | 3.0 | 3.0 | 2.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| **400** | -0.9 | -0.9 | -0.9 | -0.8 | -0.8 | 0.0 | 1.0 | 1.0 | 1.0 | 3.0 | 3.0 | 1.0 | 0.2 | 0.0 | 0.0 | 0.0 |
| **800** | -0.9 | -0.9 | -0.9 | -0.9 | -0.8 | 0.0 | 0.5 | 0.8 | 0.9 | 1.7 | 1.9 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| **1200** | 0.6 | 0.6 | 0.3 | 0.0 | 0.0 | 0.2 | 0.3 | 0.5 | 0.8 | 1.4 | 1.9 | 2.4 | 2.8 | 3.0 | 3.0 | 3.0 |
| **1600** | 2.2 | 2.2 | 1.1 | 0.8 | 0.5 | 0.5 | 0.5 | 0.5 | 0.7 | 1.2 | 1.7 | 2.3 | 2.9 | 3.4 | 3.6 | 3.6 |
| **2000** | 3.0 | 3.0 | 1.6 | 1.1 | 0.7 | 0.7 | 0.7 | 0.7 | 0.7 | 1.1 | 1.9 | 2.5 | 3.3 | 4.0 | 5.4 | 6.4 |
| **2400** | 3.3 | 3.3 | 2.0 | 1.1 | 0.9 | 0.9 | 0.9 | 0.9 | 0.9 | 1.3 | 2.0 | 2.9 | 3.8 | 4.6 | 6.7 | 7.6 |
| **2800** | 3.6 | 3.6 | 2.4 | 1.4 | 1.2 | 1.2 | 1.2 | 1.2 | 1.2 | 1.8 | 2.5 | 3.3 | 4.4 | 5.3 | 7.5 | 8.5 |
| **3200** | 4.4 | 4.0 | 2.8 | 1.9 | 1.7 | 1.7 | 1.7 | 1.7 | 1.8 | 2.1 | 3.1 | 4.1 | 5.2 | 6.3 | 8.3 | 9.3 |
| **3600** | 5.4 | 4.8 | 4.0 | 2.3 | 2.2 | 2.2 | 2.2 | 2.3 | 2.4 | 3.0 | 3.9 | 5.0 | 6.3 | 7.4 | 9.1 | 10.0 |
| **4000** | 6.9 | 6.5 | 6.0 | 3.5 | 3.0 | 3.6 | 4.5 | 5.5 | 6.6 | 7.8 | 8.6 | 9.3 | 9.8 | 10.4 | 11.0 | 11.0 |
| **4500** | 9.1 | 8.5 | 7.9 | 6.5 | 6.4 | 7.6 | 8.6 | 9.5 | 10.6 | 12.2 | 13.4 | 14.2 | 15.0 | 15.6 | 16.0 | 16.0 |
| **5000** | 11.6 | 11.2 | 10.8 | 10.7 | 11.7 | 12.7 | 13.7 | 14.6 | 15.6 | 16.7 | 17.9 | 19.3 | 20.7 | 21.0 | 21.0 | 21.0 |
| **6000** | 14.0 | 14.0 | 14.9 | 17.4 | 19.0 | 20.0 | 21.0 | 21.5 | 22.0 | 22.4 | 22.8 | 23.0 | 23.0 | 23.0 | 23.0 | 23.0 |
| **7000** | 16.0 | 16.0 | 17.0 | 19.0 | 20.6 | 21.9 | 22.5 | 22.9 | 23.2 | 23.5 | 23.8 | 24.1 | 24.4 | 24.8 | 25.0 | 25.0 |

**Validations physiques** : max **25,0° BTDC** (canonique 2,2 HDi) · ralenti 0,0/−0,9° ·
croissance monotone en régime ET en charge · plateau 24,4→25,0° à pleine charge 3 500-5 000.

#### 3. ⚠ ERRATA : `C63C` = **ANGLE**, pas pression

| brut | 0 | 1707 | 3413 | 5120 | 6827 | 8533 | 10667 | 12800 | 15360 |
|---|---|---|---|---|---|---|---|---|---|
| **angle** | **0°** | **40°** | **80°** | **120°** | **160°** | **200°** | **250°** | **300°** | **360°** |

Valeurs **parfaitement rondes** en degrés jusqu’à un tour complet (360° = 15 360).
⇒ l’interprétation « pression rail × 0,1 bar (B.27) » est **FAUSSE**.
⇒ les **3 grilles 9 × 9** (`0xE130E`, `0xE2078`, `0xE211A`) sont indexées par l’**angle vilebrequin**.

#### 4. `C7C2` = P_rail × 10 (confirmé)

`1190 … 13500` = **119 … 1350 bar**. La carte 14 × 18 est indexée par **[pression rail, `C78A`]**.

#### 5. `C562` = identifiant **`0x0F08`** (correction de B.31 §4) — hypothèse IQ

| brut | 0 | 300 | 10 000 | 12 000 | 14 016 | 18 000 |
|---|---|---|---|---|---|---|
| **mg/cycle (÷1000)** | **0** | **0,3** | **10** | **12** | **14** | **18** |

Grille de la carte 6 × 6 : IQ = 0 ⇒ durée 0 ; durée constante en IQ ; effondrement avec la température
(9230 à −30 °C → 0 à +10 °C). ⇒ **durée d’injection additionnelle (post-injection) f(T_LDR, IQ)**,
max **9230 µs ≈ 9,2 ms**.

#### 6. `0xF884` ≠ `EA 0xEF880`

| écriture | nature |
|---|---|
| `#0F884h` (l.213595, 214368…) | **adresse RAM `0xF884`** — pointeur de structure, non symbolisé |
| **EA `0xEF880`** | **hors Datensatz** (fin `0xEBFB9`) ⇒ **padding / vide** ✔ |

#### 7. `C3BA`

Température confirmée (même clé Kelvin ×10). Ses **12 occurrences sont toutes des AXES**, aucune grille ⇒
hypothèse **homonyme / doublon de conditionnement**. À trancher par ses 14 DTC.

---

### B.34 — ★★★★★ Le LIMITEUR D’AVANCE MAXIMALE : `0xEA658` plat à **1280 = 30,0°** + 3 correcteurs cachés

#### 1. La chaîne `loc_D2A6E` → `loc_D2AFC` (l.238062-238124)

```
C740 = r15 ;  unk_2FAC(r3 = h 0x1D9A)        → correcteur n°2
C742 = C750 × C976 / 10000                  ← mul + divl #2710h = POURCENTAGE
r15 += C742
unk_2FAC(r3 = h 0x1D9C)                     → correcteur n°3  → C73C
unk_2FAC(r3 = h 0x1D98)                     → **LIMITEUR**  → C754
```

Et dans la chaîne principale : `D518 = Σ correctifs` → `+= carte 0xE2816` → **`min(·, C754)`** → `D51A`.

#### 2. Les 4 cartes du bloc `0x1D96`–`0x1D9C` (128 mots = 16 × 8 chacune)

| handle | EA | non nuls | brute | **degrés (°CRK)** | rôle |
|---|---|---|---|---|---|
| `0x1D96` | `0xEA558` | 30/128 | 0 … 171 | 0 … 4,0° | correcteur n°1 |
| **`0x1D98`** | **`0xEA658`** | **128/128** | **1280 constant** | **30,0° constant** | **★ MAX SOI LIMITER** |
| `0x1D9A` | `0xEA758` | 38/128 | 0 … 256 | 0 … 6,0° | correcteur n°2 (blocs de 85 = 2,0°) |
| `0x1D9C` | `0xEA858` | 75/128 | −72 … 277 | −1,7° … +6,5° | correcteur n°3 (le plus riche) |

**`1280 × 0,0234375 = 30,000°`** ⇒ l’avance totale est **plafonnée à 30,0° avant PMH**.

⚠ **Conséquence pratique** : la carte `0xE2816` culmine à **25,0°** ⇒ **5,0° de marge**. Au-delà de
30,0°, tout gain dans `0xE2816` est **écrasé, sans code défaut** — symptôme « la map ne fait rien ».

`0xEA758` (blocs 85 = 2,0°) :

```
   0    0    0    0    0    0    0    0    0    0    0    0    0    0    0    0
 2,0  2,0    0    0    0    0    0    0  2,0  2,0    0    0    0    0    0    0
 2,0  2,0    0    0    0    0    0    0  2,0  2,0    0    0    0    0    0    0
 2,0  2,0  2,0    0    0    0    0    0  2,0  2,0  2,0    0    0    0    0    0
```

`0xEA858` (170 = 4,0°) :

```
   0    0    0    0    0    0 -0,7 -0,7    0    0    0    0    0    0    0 -1,7
   0    0    0  2,0  1,0  0,4  0,4 -0,7  4,0  4,0  4,0  2,8  2,9  3,3  4,7  4,7
 4,0  4,0  4,0  3,7  3,0  3,0  4,3  4,3  4,0  4,0  4,0  2,8  2,5  2,5  4,1  4,1
 4,0  4,0  4,0  2,6  1,6  1,4  1,4  1,4  4,0  4,0  4,0  2,5  1,0  0,3  0,3  0,3
```

Les correcteurs sont appliqués **en pourcentage** (`× C75x / 10000`).

#### 3. `C562` : IQ ou pédale ?

| lecture | 0 | 300 | 10 000 | 12 000 | 14 016 | 18 000 |
|---|---|---|---|---|---|---|
| **IQ (÷1000)** | 0 | 0,3 | 10 | 12 | 14 | 18 mg |
| **Pédale (×0,01)** | 0 % | 3 % | **100 %** | 120 % | 140 % | 180 % ✗ |

Les deux tiennent au début ; la pédale casse au-delà de 120 %. **Test véhicule : loger `0x0F08`.**

#### 4. `C78A` — facteurs binaires écartés

`7900/128 = 61,7` · `/64 = 123,4` · `/32 = 246,9` ⇒ aucun chiffre rond. `7900 × 0,0234375 = 185°` ⇒ absurde.
⇒ la forme (pas fin près du maximum) désigne un **régime** ou une **butée**. Identifiant **`0x1F64`** : à logger.

---

### B.35 — ⚠ ERRATA de B.34 : **dix** objets **8 × 8** (et non 4 × 16 × 8) · `unk_2FAC` est un STUB

#### 1. Ce qui est VÉRIFIÉ ligne par ligne

Axes (l.237874-237884) :

| handle | EA | tag | n | valeurs |
|---|---|---|---|---|
| `0x1408` | `0xE106E` | **C42E** (régime) | **8** | 200 400 600 1250 1750 2250 2500 4000 |
| `0x1410` | `0xE10DE` | **C6A2** (charge) | **8** | 500 1000 2000 4000 6000 8000 11000 12000 |

⇒ grilles **8 × 8 = 64 mots** indexées (régime, charge).

Dix `unk_2FAC` consécutifs (l.237890-238124) avec `r3 = word_1Dxx` :

| handle | EA | contenu 8×8 | lecture |
|---|---|---|---|
| `0x1D9E` | `0xEA958` | −854 … 85 | fortement négatif à haut régime/charge |
| `0x1DAA` | `0xEAE60` | plat 1000 | butée |
| `0x1DA4` | `0xEAB60` | **tout à 0** | variante désactivée |
| `0x1DA6` | `0xEAC60` | **tout à 0** | variante désactivée |
| `0x1DA8` | `0xEAD60` | 100 → 1665 | limite à gradient |
| `0x1DA2` | `0xEAA60` | 800 → 3000 | limite (lignes plates) |
| `0x1D96` | `0xEA558` | 0 … 85 | correction coin froid/faible charge |
| `0x1D9A` | `0xEA758` | 0 / 85 | masque en escalier |
| `0x1D9C` | `0xEA858` | −72 … 200 | correction riche |
| **`0x1D98`** | **`0xEA658`** | **plat 1280** | **★ plafond** |

#### 2. Preuve d’adressage (test décisif `0xE8444` vs `0xE4444`)

| EA | contenu | verdict |
|---|---|---|
| `0xE8444` | `[0xC3C2][16][0 800 1000 … 5200]` + `[0xC476][16][3000…11500]` + grille | ✅ **structure d’axes cohérente** |
| `0xE4444` | 69, −1, 0, 65, −1… | ❌ déchet |

⇒ **`EA = 0xE0000 + pointeur` re-confirmée par la structure.**

#### 3. ⚠ ERRATA de B.34

| écrit en B.34 | réalité |
|---|---|
| « 4 cartes » | **10 objets** (`0x1D96`–`0x1DAA`) |
| « 128 mots = 16 × 8 » | **64 mots = 8 × 8** |
| tables de `0xEA758`/`0xEA858` sur 4 lignes | **8 lignes** (tables décalées d’un bloc) |
| « `unk_2FAC` = interpolateur » | ⚠ **`unk_2FAC: ds 1`** — jamais désassemblé par IDA ⇒ **inférence**, pas lecture. Idem `unk_2F56`. |

`0xEA758` (h `0x1D9A`), 8 × 8, 0 / 85 :

```
  0   0   0   0   0   0   0   0
  0   0   0   0   0   0   0   0
 85  85   0   0   0   0   0   0
 85  85   0   0   0   0   0   0
 85  85   0   0   0   0   0   0
 85  85   0   0   0   0   0   0
 85  85  85   0   0   0   0   0
 85  85  85   0   0   0   0   0
```

`0xEA858` (h `0x1D9C`), 8 × 8, −72 … 200 :

```
   0    0    0    0    0    0  -30  -30
   0    0    0    0    0    0    0  -72
   0    0    0   85   43   15   15  -28
 170  170  170  119  122  142  200  200
 170  170  170  157  128  126  183  183
 170  170  170  121  107  107  176  176
 170  170  170  111   68   60   60   60
 170  170  170  108   43   13   13   13
```

#### 4. Ce qui reste ACQUIS : plafond **1280**

`C754` = sortie de h `0x1D98`, et `min(r15, C754)` (l.241064) compare **deux grandeurs de même unité**.
Carte d’avance max 25,0° + 15 360 pas/tour ⇒ **1280 = 30,0° avant PMH**, marge **5,0°**.

#### 5. `C562` dans le code

| fait | preuve |
|---|---|
| 100 références / **3 écritures** | `← C3FA` (l.232361), `← 0FFh` (l.232352), `← MDL` (l.232870) |
| **argument de `unk_1FE8`** (10 paramètres empilés) | l.184986 et l.187031 |
| entouré des handles d’axes `0x14BA`/`0x14BE` et des buffers `D9B6 D9C6 D9E0 D9EA D9F6 DA04 DA0A` | idem |
| comparé à des éléments d’axe pour produire un indice | l.177661, l.159936 |
| identifiant `0x0F08` | dictionnaire B.22 |

⇒ **grandeur d’entrée de l’arbitrage des limiteurs** (`unk_1FE8`) — place exacte d’une IQ / souhait conducteur.
Chemin de valeur : `C562 ← C3FA` ← calibration (h `0x1470` +6 = **8000** ; h `0x1654`), saturé 0 / `0x7FFF`.

#### 6. Prochaine cible : `unk_1FE8`

Coordinateur à 10 paramètres (`C562`, axes `0x14BA`/`0x14BE`, buffers `D9B6`…`DA0A`) — appelé depuis tout
le segment 015. Le désassembler nommerait `C562` **par son rôle**.

---

### B.36 — ★★★ La CHAÎNE PÉDALE : 2 voies, 4 seuils volts, moyenne et delta

#### 1. Tâche `0x326` (l.213301-213400)

```
scxt CC2_CC27, #326h          ; tâche pédale
r0 = word_151C ; r9 = #0F844h ; sub_C4AAE ; sub_C46D2   → D04E (voie 1), D052
r0 = word_151C ; r9 = #0F854h ; sub_C4AAE ; sub_C46D2   → D050 (voie 2)
C36C = (r11.2 ? r10 : r12)                             ; aiguillage diagnostic
add r10, r12 ; shr r10, #1                             ; ★ MOYENNE
```

| grandeur | rôle |
|---|---|
| `word_D04E` / `word_D050` | valeurs voie 1 / voie 2 |
| `word_D052` | grandeur annexe voie 1 |
| `word_C36C` | **valeur retenue** (moyenne ou voie choisie) |
| `word_C3A4` | valeur par défaut = `[h 0x151C + 8]` |
| `word_C3A6` | **delta** |

#### 2. `sub_C46D2` (l.213203) = porte de plausibilité + delta

```
r10 = [r0+#2] ; if (r10 < r9) → erreur bit 5 (trop bas)
r10 = [r0+#4] ; if (r9 < r10) → erreur bit 6 (trop haut)
sinon r10 = r9 ; bits d’erreur = 0
sous conditions (régime C91C, C5FE, C5A4, byte_C8F9) :
   word_C3A6 = [r2+#6] − r9   ; DELTA
   byte_C216 = 1              ; drapeau
   bornage du delta entre [r2+#0Ah] et [r2+#8]
addb byte_C9F2, ONES          ; compteur anti-rebond
```

#### 3. Seuils — `0xE31FE` (h `0x1528`) et `0xE31B8` (h `0x151E`)

| offset | valeur | lecture |
|---|---|---|
| `+#0` / `+#2` / `+#4` | 3131 / 3031 / 2831 | 40,0 / 30,0 / 10,0 °C (Kelvin ×10) |
| `+#6` | **102** | référence du delta |
| `+#8` / `+#0Ah` | **9** / **−12** | bornes du delta |
| `+#0Ch` | **100** | seuil d’activation (régime) |

`0xE31B8` : `[4]` puis **20 · 102 · 921 · 1003** ⇒ sur un ADC 0-5 V / 1023 pas :

| brut | tension | rôle |
|---|---|---|
| **20** | **0,10 V** | plancher absolu |
| **102** | **0,50 V** | début de course utile |
| **921** | **4,50 V** | fin de course utile |
| **1003** | **4,90 V** | plafond absolu |

#### 4. Reste à établir

| point | état |
|---|---|
| deux voies lues séparément | ✅ code |
| fenêtres 0,5-4,5 V | ✅ calibration `0xE31B8` |
| moyenne | ✅ `add` + `shr #1` |
| delta + drapeau + bornes | ✅ `C3A6`, `byte_C216`, −12/+9 |
| anti-rebond | ✅ `byte_C9F2` |
| **rapport 2:1 entre voies** | ⏳ probablement **dans la courbe de conversion** (`0x151C`), pas dans un test arithmétique |
| conversion en **0…10 000** | ⏳ identifiant de `C36C` à vérifier |
| **delta éco/sport** | ⏳ `C3A6` lu en l.151547, l.151904, `sub_A0CCC+246` |

#### 5. `C562` n’est PAS dans la chaîne pédale

La chaîne écrit `D04E`, `D050`, `D052`, `C36C`, `C3A4`, `C3A6`, `byte_C216`, `byte_C9F2` — jamais `C562`.
⇒ la piste « IQ » se joue **en aval** de la pédale.

---

### B.37 — ★★ Trame de mesure `word_CF6` · relais pédale `C6DA`/`C952` · axes `0…10000`

#### 1. Le delta `C3A6` part dans la TRAME DE MESURE (l.151536-151552)

```
mov r5, word_CF6
movb [r5+#0E5D0h], rl4      ; slot 0xE5D0 ← byte_C30D
mov r4, #0E5D2h
add r4, word_CF6            ; ← BASE RELOGEABLE
mov [r4], word_C3A6         ; slot 0xE5D2 ← delta pédale
```

⇒ **`word_CF6` = base d’une trame** ; `0xE5D0`, `0xE5D2`, `0xE5D4`… = emplacements numérotés.
Mécanisme d’export vers la lecture de mesure — probablement celui qui publie `D51A` (identifiant `0x1F4D`).
Le delta n’est donc **pas** un mode caché : il est publié (borné −12 / +9).

#### 2. Le relais pédale : `C6DA` / `C952`

| ligne | écriture |
|---|---|
| l.191961 | `word_C952 ← word_C6DA` |
| l.194713 | `word_C952 ← word_C6DA` (tâche `#33Ch`) |
| l.195521 | `word_C6DA ← word_C952` |
| l.195389 | `word_C952 ← word_DB38` (variante) |

Même motif que le régime (`C91C ← C42E`) : **valeur / copie de travail**.

#### 3. Les axes `0…10000` = 0…100 % (pédale)

| EA | tag | n | axe |
|---|---|---|---|
| `0xE8B64` | **C6DA** | 6 | **118 2000 4000 6000 8000 10000** |
| `0xE8BE8` | **C6DA** | 6 | **118 2000 4000 6000 8000 10000** |
| `0xEB6CE` | C6A2 | 2 | 0 · 10000 |
| `0xE6D28` | C6B6 | 8 | 0 1500 3000 4500 6000 7500 9000 10000 |
| `0xE4D5C`… | C5A8 | 8 | 100 2000 3000 4000 5000 6000 7000 11000 |

⇒ `0xE8B64` et `0xE8BE8` = **cartes « souhait conducteur »** (Driver’s Wish), axe pédale `C6DA`.

#### 4. `C36C` n’est pas la pédale publiée

Une seule lecture : `cmp r3, word_C36C` (l.154237) avec `r3 = [h 0x1878] = **25**` ⇒ condition d’activation
(pédale > 25) combinée au régime, `byte_C8F9` et au drapeau de delta `byte_C216` → `word_FD78.10`.

#### 5. `C562` — état

| fait | état |
|---|---|
| absent de la chaîne d’entrée | ✅ (B.36) |
| absent de la boucle `C36C`/`C6DA` | ✅ (ici) |
| `C562 ← C3FA` ; `C3FA ← h 0x1470 +6` = **8000** ; secours `0xFF` | ✅ |
| argument de `unk_1FE8` (10 paramètres) | ✅ (B.35) |
| identifiant `0x0F08` | ✅ |

Question ouverte : la cartographie qui utilise la pédale **et** qui touche `C562` — côté `0xE8xxx` ou ailleurs ?

---

### B.38 — ★★★★★ Les DEUX cartes « souhait conducteur » · sélection par nervosité · **`C562` TRACÉ**

#### 1. `0xE8B50` (h `0x1B66`) et `0xE8BD4` (h `0x1B68`)

```
[C42E][8] [0 600 750 1000 1300 1750 2250 5000]   axe Y = RÉGIME
[C6DA][6] [118 2000 4000 6000 8000 10000]        axe X = PÉDALE (0 → 100 %)
[grille 8 × 6]
```

`0xE8BD4` — variante NORMALE :

| tr/min / pédale | 1,18 % | 20 % | 40 % | 60 % | 80 % | 100 % |
|---|---|---|---|---|---|---|
| 0 | 1060 | 3372 | 5660 | 7260 | 8000 | 8000 |
| 600 | 460 | 2608 | 4928 | 6768 | 8000 | 8000 |
| 750 | 320 | 2400 | 4688 | 6684 | 8000 | 8000 |
| 1000 | 140 | 2132 | 4444 | 6408 | 8000 | 8000 |
| 1300 | 0 | 1844 | 4104 | 6064 | 8000 | 8000 |
| 1750 | 0 | 1520 | 3616 | 5606 | 7660 | 8000 |
| 2250 | 0 | 1260 | 3208 | 5180 | 7180 | 8000 |
| 5000 | 0 | 680 | 1846 | 3656 | 5740 | 8000 |

`0xE8B50` — variante NERVEUSE : **identique sauf la colonne 20 %**

| tr/min | 0 | 600 | 750 | 1000 | 1300 | 1750 | 2250 | 5000 |
|---|---|---|---|---|---|---|---|---|
| **écart (mg/100)** | 0 | 0 | **+50** | **+350** | **+500** | **+450** | **+350** | 0 |

Unité : **valeur / 100 = mg/cycle**, plafond **8000 = 80 mg**.
⇒ la différence est **concentrée sur la colonne 20 % de pédale**, max **+5 mg** ⇒ **c’est la « nervosité ».

#### 2. Le sélecteur `sub_B56F8` (l.186826-186848)

```
r4 = word_C576 ; word_C93E = r4          ; copie de travail
r5 = word_1B6A ; r2 = [r5]               ; EA 0xE8C58, [0] = 539
cmp r2, word_C93E
  C93E ≤ 539 → r12 = word_1B68 ; unk_1D50   ; carte NORMALE
  sinon      → r12 = word_1B66 ; unk_1D50   ; carte NERVEUSE
```

Seuil **539** ; `C93E > 539` ⇒ nerveuse. Les deux appels passent par `unk_1D50` avec (régime, pédale).

#### 3. ★ `C562` tracé : `loc_CFDA0` (l.232852-232870)

```
r7 = word_1470 ; r2 = [r7+#6]   ; = 8000  (EA 0xE2260)
word_C93E = 0 ; word_C576 = 0
word_C578 = 8000 ; word_F908 = 8000 ; byte_F91A = 0
word_F904 |= 8000h
loc_CFDD2:
MDL = word_C578
word_C562 = MDL                ; ★★ C562 = 8000
word_C552 = byte_F91A          ; = 0
```

| variable | rôle | repos |
|---|---|---|
| **`C562`** = `C578` = `F908` | **la quantité** (8000 = **80 mg**) | 8000 |
| **`C576`** = `C93E` | **indice de nervosité / mode** | 0 |
| `C552` = `byte_F91A` | état associé | 0 |

⇒ `C562` **n’est pas un capteur** : c’est la **quantité de référence de l’arbitrage** (80 mg),
avec `C576`/`C93E` comme indice de mode — celui qui choisit entre les deux cartes de souhait conducteur.

#### 4. Régulateur de vitesse

`sub_B56F8` est appelé depuis `seg015:ABE0` ; le site `C562` (l.187031) est dans la même zone que
l’arbitre `unk_1FE8` (B.35). **L’arbitrage se fait donc en QUANTITÉ (mg), pas en % de pédale** —
les deux cartes sortent déjà de l’IQ et `C562` = 80 mg.

#### 5. Cibles

1. L’autre carte de la paire (axe vitesse, valeurs décroissantes).
2. Le producteur de `C576`/`C93E` : écrit l.140049, 171718, 172956, 176887 — c’est là que se décide le mode.

---

### B.39 — ★★★ Le RÉGULATEUR : machine à états, 12 handles, 5 courbes sur `C3AE` · bloc d’IDs `0x0F00`

#### 1. Machine à états `sub_AC65E` (l.171280)

```
C91C = C42E                            ; copie de travail du régime
r2 = [word_1C94 +2] = 150 ; cmp r2, C91C ; cc_SGE → état 0
r2 = [word_1C94 +4] = 300 ; cmp r2, C91C ; cc_SLE → état 0
rl4 = byte_D82A ; cmpb rl4, #4 ; cc_UGT → sortie
r4 = rl4 << 1 ; add r4, #0A10h ; jmpi [r4]   ; ★ TABLE DE SAUTS, 5 états
```

| état | action |
|---|---|
| **0** | `C140 = 0 ; C786 = 0 ; C7DE = 0` ; état → 1 |
| 1…4 | fenêtre `[0x14A2]`, comparaisons consigne/mesure, courbes |

#### 2. Ressources de calibration du régulateur

| handle | EA | contenu | lecture |
|---|---|---|---|
| `0x141E` | `0xE1148` | 0 2048 260 1 1024 512 0 512 1280 1280 | bloc **configuration véhicule** (`C60E` à `+0x26`) |
| `0x14A2` | `0xE2728` | 2000 2000 20 20 0 0 20 0 2 68 | **paramètres du régulateur** |
| `0x17B2` | `0xE4584` | 1000 −1 69 −1 0 1 −1 0 1 −1 | paramètres / pas de réglage |
| `0x1C94` | `0xE964A` | **500 · 150 · 300** · 1000 · 3000 … | **bloc d’état** |
| `0x1DDA` | `0xEB9DA` | `[C3D2][2][2431 2531]` | axe de température (−30 / −20 °C) |

#### 3. Les 5 courbes, toutes sur `C3AE`

| handle | EA | axe |
|---|---|---|
| `0x19C8` | `0xE6C10` | `[C3AE][8]` 1000 1300 1500 1750 2000 2500 3000 4500 |
| `0x19CA` | `0xE6C34` | idem |
| `0x19CC` | `0xE6C58` | idem |
| `0x19D0` | `0xE6CB0` | idem |
| `0x19CE` | `0xE6C7C` | `[C3AE][12]` 1000 1250 1500 1750 2000 2500 2750 3000 … |

`C3AE` porte l’identifiant **`0x1F40`** ; c’est aussi l’axe de `0xE86F4`. Hypothèse : **régime de travail
du régulateur** — non prouvé (`C3AE ← [0xF884]`, RAM non symbolisée).

Primitives employées : `unk_1D36` (1-D) et `unk_20AC` (mise à l’échelle).

#### 4. ★ Bloc d’identifiants `0x0F00`–`0x0F1E` (41 identifiants)

| ID | RAM | note |
|---|---|---|
| `0x0F00` | `C3D2` | T liquide de refroidissement |
| `0x0F01` | `C3BA` | T air d’admission |
| `0x0F02` | `C3B0` | T carburant |
| `0x0F06` | `C6E8` | — |
| **`0x0F08`** | **`C562`** | **quantité de référence (8000 = 80 mg)** |
| `0x0F0A` | `C552` | état associé |
| **`0x0F0B`** | **`C576`** | **indice de mode / nervosité** |
| `0x0F0C` | `C6EA` | — |
| **`0x0F10`** | **`C42E`** | **régime** |
| `0x0F12` | `C428` | — |
| `0x0F13`…`0x0F18` | **`C442` `C444` `C446` `C448` `C44A` `C44C`** | **6 consécutives** |
| `0x0F19`…`0x0F1E` | **`C436` `C438` `C43A` `C43C` `C43E` `C440`** | **6 consécutives** |

⇒ deux séries de 6 = signature de valeurs **par cylindre**. Et `0x0E80`-`0x0EA8` (19 IDs) → `C4B6`…`C502`
= le **bloc EGR**.

---

### B.40 — ★★★ Le CAN en clair : `0x38D` et `0x412` · la vitesse · deux errata

#### 1. Errata 92 — `0x1DDA` n’est pas une courbe de température

`calls 0, word_1DDA` (35 sites) : la valeur de handle `0xB9DA` est un **décalage de code** en
segment 0 (base `0x80000`) ⇒ cible **EA `0x8B9DA`** (fo `0xB9DA`) = du code. **Règle** : donnée ⇒
`EA = 0xE0000 + valeur` ; code (`calls 0,`) ⇒ `EA = 0x80000 + valeur`. Corroboré par `word_1D94`
(`0xA556` → `0x8A556`), `word_1DA8`, `word_1E08`, `word_1DEC`.

#### 2. Errata 88/91 — `C562` = **VITESSE VÉHICULE** (0,01 km/h), pas une quantité

L’axe Y de la carte `0xE868C` est taggé **`C562`** avec les points **0 · 300 · 10000 · 12000 · 14016 ·
18000** = 0 · 3 · 100 · 120 · 140,16 · **180 km/h** ; la sortie (durée en µs : 9230 à −30 °C, 0 à +20 °C)
est le **post-chauffage**, et sa **colonne 0 km/h vaut 0** ⇒ coupé à l’arrêt. Défaut `[word_1470+6] =
8000` = **80,00 km/h** ; `[+0x0E] = 31621` borne haute ; `[+0x10] = 2560` **timeout**.

#### 3. Trames CAN reçues (configurateur `sub_9A8B8`, objets `0xEF00 + 16×slot`)

| slot | ID | long. | armement | destination | décodeur |
|---|---|---|---|---|---|
| 1 / 2 / 3 / 5 / 7 | `0x208` `0x348` `0x488` `0x788` `0x388` | 8 / 5 / 8 / 6 / 5 | toujours | ? | ? |
| 4 | `0x072` puis **`[word_1650]`** | 5 / **8** | `[word_1650] ≠ 0` | ? | **ID programmable** (candidat `0x468`) |
| 8 | `0x7E2` | 6 | `C2B7 & 8` | `0xC82B` | `sub_9C43A` |
| **9** | **`0x349`** | **7** | **`C2B7 & 1`** | `0xC86E` | `sub_9B796` = **rapport de boîte** |
| 10 | `0x50E` | 3 | `C2B7 & 8` | `0xC7E8` | `sub_9C206` |
| **11** | **`0x412`** | **8** | `C2B7 & 8` | **`0xC87D`** | `sub_9C23E` |
| **12** | **`0x38D`** | **5** | ★ **`byte_C2BC == 8`** | **`0xC811`** | `sub_9C56A` |
| 13 | `0x389` | 5 | `C2B7 & 1` | `0xC816` | `sub_9C76A` |
| 14 | `0x34D` | 6 / 5 | `C2B7 & 6 == 6` | `0xC825` | ? |
| 15 | `0x0A8` | 5 | `C2B7 & 8` | ? | ? |

`0x468` **absent** du fichier. Les longueurs recoupent exactement la table de `sub_9D166` (étape 25).

#### 4. Chaîne vitesse

```
0x38D octets 0-1  →  C3FA  (mot 16 bits, 0xFFFF invalide, unk_2196(1024,0), borné 0..0x7FFF)
0x38D octets 2-3  →  C406  (compteur → DIFFÉRENCE avec CF7E = incrément de distance)
0x38D octet 4     →  C3F2  (états ABS/ESP, unk_2184 + filtre unk_1E50)
0x412 C884        →  C3F8  (unk_20AC ×4) ; C87E/C880/C883/C87D → C23D/C23F/C248/C229
```

Sélecteur de source : **`byte_C2BC = [0xE1148 + 5]`** — `1` = impulsions CC1, `8` = CAN, `4` = variante
(dispatching de l’odomètre en l.153570, et des deux tops de `C562` en `sub_CF8C8` / `loc_CFDD2`).
Dans ce dump : **`+5 = 0x01`** ⇒ voie filaire.

Avec les impulsions : `loc_CFB36` mesure `CC1_T0`/`PECC2`, `C56C` = période, `C556 = [word_1470+2] =
17578`, `C566` = vitesse lissée, puis `loc_CFC6C` calcule **|C578 − F90C| / F910** (dérivée) filtrée
par `unk_24BA` et bornée par `[word_1470+0x0C/+0x0D]` ⇒ **`byte_F91A`** (accélération) → `C552`.

#### 5. Les autres blocs demandés

| handle | EA | nature réelle |
|---|---|---|
| `0x141E` | `0xE1148` | **codage véhicule** : 22 octets lus un à un (`+3`,`+5`,`+9`,`+0x0E`,`+0x15`…`+0x28`,`+0x33`), `0xFF` au-delà de `+0x37` |
| `0x14A2` | `0xE2728` | **seuils de surveillance** (`+2`,`+4`,`+6`,`+8`,`+0x0A`=`0`/`68`,`+0x0C`) + **5 identifiants `0x0Fxx`** en `+0x1A`…`+0x22` — **pas** un bloc PI/PID |
| `0x17B2` | `0xE4584` | **descripteurs de moniteurs de défaut** : argument `r1` de `sub_CE9B4` (défaut `0x267F`), paires (seuil, ±1) ; **pas** des appuis `+`/`−` |
| `0x1C94` | `0xE964A` | seuils (`500 150 300 1000 3000`) + courbe `[D4AC][2]` + **carte 8×8 `[C42E][8][200…4000] × [C7B8][8][2000…13000]`**, grille 896…4850 |

`sub_AC65E` = machine à états de la **pression rail** (compare `C91C` et **`word_C7C2`**), et non le
régulateur de vitesse : `150 / 300` = seuil « moteur tourne », **aucune température**.

---

### B.41 — `C562` = VITESSE, prouvée par les axes · le **codage du régulateur** (`byte_C2BD`)

#### 1. Les trois axes taggés `C562` (scan du tag + axe strictement croissant)

| EA | type | n | axe | traduction |
|---|---|---|---|---|
| `0xE4FA4` | courbe 1-D | 8 | `0 5000 6000 7000 8000 9000 11000 20000` | **0 · 50 · 60 · 70 · 80 · 90 · 110 · 200 km/h** |
| `0xE87EE` | courbe 1-D | 6 | `1500 2100 7000 9000 11500 20000` | **15 · 21 · 70 · 90 · 115 · 200 km/h** |
| `0xE869C` | carte | 6 | `0 300 10000 12000 14016 18000` | **0 · 3 · 100 · 120 · 140,16 · 180 km/h** |

Signature : grand saut initial puis **pas de 1000 = 10 km/h**, et **20 000 (200 km/h)** en bout. Les trois
existent en **double** (`0xF4FA4`, `0xF87EE`, `0xF869C`) : deux copies du Datensatz dans les 512 Ko.

#### 2. Autres preuves dans le code

- **`C562 == 0` = arrêt** : `sub_A7C5A` l.163014 et `sub_C0496` l.205739 (`jmpr cc_NZ` sur `word_C562`).
- **transfert sans à-coup** : `loc_A3B12` l.155935/155942/155952/155959 — `word_D6E0 = C562` au réarmement,
  puis `sub_97E16` (limiteur de pente à état) avec `r13 = C562`.
- **seuils OBD de roulage** : `sub_C7398` l.217467/217489 — `[word_16F0] = 1000` (**10 km/h**) et
  `[word_16F0+2] = 9000` (**90 km/h**) → `byte_CA39`.
- **seuil 5 km/h** : `loc_B74E6` l.189946 — `[word_1432+0x2C] = 500`.

**99 lectures de `word_C562` dans 88 blocs** : ~45 dans la forêt de limiteurs `seg015 loc_B45xx-B53xx`,
~8 dans le régulateur, 4 dans les filtres, 5 dans les limitations post-injection/EGR/couple, 2 OBD,
4 dans le sélecteur de source `seg016`.

#### 3. ★ Le codage du régulateur : `byte_C2BD` (= `[word_141C + 3]`)

| `byte_C2BD & 0x70` | sens | consigne par défaut |
|---|---|---|
| **`0x00`** | **régulateur NON codé** (`sub_AF50E` → 0) | — |
| `0x10` / `0x20` / `0x40` | variantes A / B / C | `[word_1A80 + 0 / +2 / +4]` |

`0xE7F76` (handle `0x1A80`) = `30000 30000 30000 30000` puis `[C42E][8][800 1500 1750 2000 2750 3000
4000 4800]`. **30 000 = 300,00 km/h = sentinelle « pas de consigne »** (même valeur dans `word_1B70`).
**Dans ce dump `byte_C2BD = 0x00` ⇒ le régulateur est désactivé par codage.**

#### 4. ERRATA 93 — `0x141C` (`0xE111E`, 42 o) et `0x141E` (`0xE1148`, 52 o) sont deux enregistrements
contigus d’une même table de codage (`0xE1148 = 0xE111E + 0x2A`). Les champs `+3`, `+0x0B`, `+0x0C`,
`+0x0E`, `+0x15`…`+0x28` viennent de **`0x141C`** ; `+0x05` (`byte_C2BC` = origine vitesse) vient bien de
`0x141E` et vaut `0x01`.

⇒ **`byte_C2B7 = [0x141C+0x0E] = 0x08`** : les trames `0x412`/`0x50E`/`0x7E2`/`0x0A8` sont **armées**, mais
`byte_C2B7 & 1 = 0` ⇒ **les trames `0x349` (rapport de boîte) et `0x389` ne sont PAS reçues** dans cette
calibration ; `byte_C240` reste au défaut `[word_1658+8]`.

#### 5. État du régulateur

`byte_D9EE` (actif) · `byte_D9EF` (état 0…3) · `D3EE`…`D3FA` (publication diag) · `word_C6EA` (consigne) ·
`D9FA = C6EA − C562` (écart) · `word_1B70` seuils `0/+30000/0/−29968/+30000/0/+10000/0` · `word_1B7A`
rampe `1 1000 820 220 512 1024 1024 9` · `word_1B6C` (défaut `0x40DF`) · **`unk_1FE8`** rampe à 10
arguments (l.187031 et l.196459) · **`word_C69A` = sortie, 3 écritures et AUCUN lecteur** ·
`[0x141C+0x0B]` = coupe · `[0x141C+0x0C]` = activation du PI `unk_2020`.

---

### B.42 — La BIBLIOTHÈQUE est effacée · conventions d’appel · le rapport engagé · bloc paramètres régulateur

#### 1. ★★★ Segment 0 = `0xC3` : 77 primitives sans corps

`fo 0x00000`–`0x07FFF` = **32 768 octets `0xC3`** ; **108 490 o** de `0xC3` au total en 27 plages.
Vérifié : `fo 0x1D36`, `0x1D50`, `0x1FE8`, `0x20AC`, `0x2160`, `0x2196`, `0x24BA`, `0x2EE2` → que des `C3`.

| primitive | appels | rôle |
|---|---|---|
| `unk_20AC` | 250 | mise à l’échelle multiplicative |
| `unk_1D36` | 168 | interpolation **1-D** |
| `unk_7C2` / `unk_7B4` | 110 / 110 | verrous de section critique |
| `unk_1D50` | 72 | interpolation **2-D** |
| `unk_1D7E` / `unk_1D6C` | 54 / 44 | non identifiés |
| `unk_2160` / `unk_2128` | 27 / 24 | non identifiés |

#### 2. Conventions d’appel acquises

- `unk_1D36(r12 = EA courbe, r13 = X)` — prouvé par `sub_B2A02` (courbe `0xE87EE`, X = `C562`).
- `unk_1D50(r12 = EA carte, r13 = var du **tagY**, r14 = var du **tagX**)` — prouvé par `loc_B28AA`
  (carte `0xE868C` : `r13 = C908`=T° eau, `r14 = C562`=vitesse). **Ordre (Y, X)**.
- `unk_20AC(r12 = a, r13 = b, r14 = 10000)` → **a·b/10000**.
- `unk_1FE8` : 10 arguments (r12/r13 = taux montée/descente, r14/r15 = états, 5 sur la pile dont
  l’entrée = **`C562`** au site régulateur `l.187031` ; au site `l.196459` les taux sont en RAM
  (`0xDBAE`/`0xDBA4`).

#### 3. Le rapport engagé (BVM)

| fait | mesure |
|---|---|
| écrivains de `byte_C240` | 4 : trois défauts `[word_1658+8]` + un nibble CAN `byte_C871>>4` |
| **lecteurs** | **un seul** : `loc_AFBE8` l.177553 |
| divisions touchant `C562` | **0** sur 124 sites |
| sites combinant `C562` et `C91C` | **1** (`sub_B2A02` : un produit, pas un quotient) |

`loc_AFBE8` : `code = byte_C240 & 0x0F` ; si `> 0x0E` → repli ; **table de sauts `0xA2C + 2×code`** ⇒
`word_1B22` (**EA `0xE835A`, 15 octets**) = `48 · 1 · 2 · 3 · 4 · 0 · 0 · 0 · 0 · 11 · 0 · 0 · 0 · 0 · 0`.

⇒ **le rapport n’est pas calculé dans le code visible** : soit reçu (`0x349`, non armée :
`byte_C2B7 & 1 = 0`), soit figé au défaut `[word_1658+8]`, soit calculé dans la bibliothèque effacée.
**Test de banc** : relever `byte_C240` en 3ᵉ puis en 5ᵉ à 50 km/h — s’il change, il est calculé.

#### 4. Protection thermique modulée par la vitesse (`sub_B2A02`)

`0xE880A` = `[C42E][6][1300 1800 2200 2800 3300 4000] × [C3D2][6][3841 3851 3861 3891 3921 3951]`
(températures **111 → 122 °C**), multipliée par `0xE87EE` = `[C562] → [0 10000 10000 20496 20496 0]`
(×2,05 entre 21 et 70 km/h, **0 à 200 km/h**), le tout `/10000`.

#### 5. Bloc de paramètres du régulateur (`0xE8C5A`–`0xE8CD0`)

`0x1B6C` `FFFF·0·41·FFFE` (défaut `0x40DF`) · `0x1B6E` + `0F10·0F08·0F80` · `0x1B70` `0·30000·0·−29968·30000
·0·10000·0` · `0x1B7A`…`0x1B84` table des rampes `1000·820·220·512·1024·1024·9` puis paires `(3840,8)
(4480,8) (2560,8) (0,8)` et `500·500·500·600·600·1152` — **paliers de vitesse mémorisés**.

---

### B.43 — Le régulateur est UNE tâche (jeton `0x35C`) · ±1 km/h · **ni SET ni RESUME**

#### 1. Bornes : l.186853 → 187110 (`scxt CC2_CC27, #35Ch` en l.186919)

```
C93E = C576 ; C91C = C42E ; D9F8 = C6EA
D9FA = C6EA − C562                ; écart consigne − vitesse
r9   = D9F8 ; D9FC = D9F8 − r9    ; limitation de pente par unk_1E50 (descripteur 1B7A)
D9FE = r9 − C562
r8   = unk_1FE8(taux, &DA0A, &D9FE, r9, C562)   ; rampe
C69A = r8   ; C6EA = r9          ; sortie et consigne appliquée
```

#### 2. ★★ Le ±1 km/h : `word_1B70 + 6` = **EA `0xE8C86` = 100** (1,00 km/h)

Comparé à `D9FE` ; au-delà → **moniteur de défaut `0x40DF`** (descripteur `word_1B6C`).
Carte de `0xE8C80` : `+0`=0 · `+2`=30000 · `+4`=0 · **`+6`=100** · `+8`=30000 · `+0x0A`=0 ·
`+0x0C`=10000 (sortie `C69A` en état 1). Les **±2 km/h** ne sont pas en immédiat.

#### 3. Les quatre descripteurs de taux sont **tous nuls**

`0x1B72`/`0x1B74` = `0 0 0 0 2` · `0x1B76`/`0x1B78` = `0 0 0 0 8` ⇒ rampe neutre. Le vrai limiteur
de pente est `0x1B7A` = **`1 · 1000 · 820 · 220 · 512 · 1024 · 1024 · 9`** via `unk_1E50`
(l.187004) : **10 / 8,2 / 2,2 km/h/s**.

#### 4. ★★★ Pas de SET, pas de RESUME

| question | reponse |
|---|---|
| ecrivain de `D9F8` | **un seul** : `D9F8 <- C6EA` (l.186911) |
| ecrivains de `C6EA` | `sub_AF520` (codage) et `C6EA <- r9` (l.187064) |
| memoire de `C562` comme consigne | **aucune** |
| rappel d une consigne anterieure | **aucun** |

=> **ni SET (`C562 -> memoire`) ni RESUME** dans ce build. La consigne ne peut valoir que **30000**
(defaut de codage) ou **10000** (etat 1).

#### 5. ★★★ `C576` et `C93E` sont **structurellement nuls**

`C576 <- C93E` et `C93E <- C576` (ou `0`) sur les 5 sites d ecriture ; **aucun pointeur vers `0xC576`
ni vers `0xC93E`** => boucle fermee a zero. Consequences : les taux nuls sont toujours retenus ; **la
nervosite ne peut pas se declencher** (test `C93E > 539` impossible => toujours la carte `0xE8BD4`) ;
aucune demande exterieure n entre par `C576`.

#### 6. La regle « 3e/4e rapport ≥ 50-60 km/h » est **hors ECU** — 4 preuves

1. `byte_C240` : un seul lecteur, dans le bloc **BVA** (hors circuit si `byte_C2C0 ≠ 1`) ;
2. `byte_C2B7 & 1 = 0` => trame **`0x349` non armee** ;
3. aucune division ne touche `C562` (0 sur 124) ;
4. aucune constante 50/60 km/h dans la tache (seulement **1** et **100** km/h).

=> condition detenue par le **BSI / commodo** (full-mux), ou par la bibliotheque effacee, ou absente
d un build ou `byte_C2BD & 0x70 = 0`.

---

### B.44 — ERRATA de B.43 et **vrai régulateur = tâche `0x340`**

#### 1. Errata

| # | B.43 / ETAPE96 | correction |
|---|---|---|
| E1 | « regulateur = tache `0x35C` » | **incomplet** : `0x35C` = sous-tache de consigne ; le regulateur est la tache **`0x340`** (l.183699-186918, ~3200 lignes) |
| E2 | « regle 3e/4e rapport hors ECU » | **partiellement faux** : l autorisation vitesse mini/maxi et regime mini/maxi est **dans l ECU** (bloc `0xE2788`) ; seul le **rapport** reste introuvable |
| E3 | `C576`/`C93E` nuls | valable ; `C93E` = etat de la demande du regulateur |
| E4 | « ni SET ni RESUME » | **a revoir** : la tache `0x340` a un etat de memorisation `D9CE` et des etats 1/2/3/4 (`byte_D9B0`) |

#### 2. Tache `0x340` : codage et machine d etats

- `byte_C2BD` (EEPROM de codage, `[word_141C+3]`) : **`0x80` ou `0x01`** = actif (`loc_B36EC`),
  `0x00` = variante `loc_B3CEC`, autre = hors service.
- code d etat 4 bits `byte_D9DF` : bit3 `C2D7`, bit2 `C2D6`, bit1 `C2D8`, bit0 = (`C2D5`==0),
  force par `C8EE`/`FD5A.15` -> **table de 16 entrees `0xA7A`** (offsets `fo 0x60A7B`,
  dupliques `0x70A7B` : `3898 39AA 396A 3AB8 3A48 39CA 3A12 3A36 3BFA 3848 3BBC 39B4
  3B06 3CB4 3B68 3CC4`) -> gestionnaires `0xB38xx`-`0xB3Cxx`.
- `byte_D9B3` = **cause de refus** : `0x85` defaut, **`0x86` vitesse mini/maxi**, **`0x87`/`0x88`
  regime maxi/mini**, `0x89` demande insuffisante, `0x8A` incoherence de demande, `0x8E` coupure.

#### 3. ★★ Bloc d autorisation `word_14B0` = EA `0xE2788`

`+00` **2500** (25,00 km/h mini) - `+02` **25000** (250 km/h maxi) - `+04` **1000** (tr/min mini) -
`+06` **4500** (tr/min maxi) - `+08` 2560 (ecart de demande) - `+0A` 768 (demande mini) -
`+0C` 4000 - `+0E` 1000 (offset de memorisation -> `D9E0`).

#### 4. Lois de rampe des etats internes `byte_D9B0`

etat 2 (l.185468) : `D9BC = 2500*C562/10000 + 5000` ; etat 3 (l.185722) : `D9BC = 500*C562/10000
+ 400` ; puis `D9C0 = D9BC/50`. Parametres : `0xE27B6` (`500`, `400`) et `0xE27C2` (`2500`, `5000`).

#### 5. Rapport engage : ce qui est exclu

- division `C91C/C562` : **0 site** (124 divisions, fenetre 18 lignes, sur `C91C`, `C562`, `C42E`,
  `C3FC`, `C578`, `C3FA`) ; multiplication `C562*K` : **0** ; carte 2-D a axe vitesse : **0 sur 66**.
- seules courbes a axe vitesse : `0xE4FA4` (n=8, h `0x18C4`), `0xE87EE`, `0xE869C` (n=6).
- site metier : l.156549 -> `unk_1D36(h 0x18C4, C562)` combine a une correction de charge ->
  `word_D1E6` (correction dependante de la vitesse).
- piste : chercher la **selection de courbes par index** `mov r12, [table + 2*index]`, `index` 0-6.

---

### B.45 — ★★★ Le rapport engage : chaine complete et **cartes 1re/2nde/3e confirmees**

#### 1. Limitation de couple par rapport (`loc_B3116`, l.183021)

```
byte_C330 & 0x0F  -> switch table 0xA62 (12 cas) -> unk_1D36(courbe, C91C) -> D9A2
```

| rapport | cellule | EA courbe | EA valeurs | contenu |
|---|---|---|---|---|
| 1re | `word_1B54` | `0xE8906` | **`0xE8928`** | `6660 6400 6350 6300 6330 6400 6500 6440 6270 6240` (apres 1250 tr/min) |
| 2nde | `word_1B56` | `0xE8946` | **`0xE8968`** | **identique a la 1re** |
| 3e | `word_1B58` | `0xE8986` | **`0xE89A8`** | **`10000` x15 = aucune limitation** |
| 4e | `word_1B64` | `0xE8B10` | `0xE8B32` | identique a la 1re |
| 5e | `word_1B5C` | `0xE89FA` | `0xE8A1C` | `10000 10000` |

Blocs de **0x40 octets** = `[tag 0xC42E][n=15][axe 15][valeurs 15]`, axe = regime 635-4000 tr/min.
`main_torque` = **`0xE841E`** = debut des **valeurs** de la pleine charge `0xE83F4` (n=19).
Sortie : `D9A2` publie en `D3EC`/`D3DA`, **memoire de minimum** `D9A8`, offset/plancher `C622`.

#### 2. Rapport remappe : `byte_D398` = 0-7 (table `0xA4A` indexee par `r9 & 0x0F`)

#### 3. Origine de `byte_C330` (fin de tache `0x34C`, l.178003)
- BVA (`byte_C2C0 == 1`) : `unk_1D7E(#0C83E, word_1B24)` + `unk_1D36` -> trame CAN boite ;
- sinon : **table 15 octets `0xE835A`** (`word_1B22`) = `30 01 02 03 04 00 00 00 00 0B 00 00 00 00 00`
  indexee par `byte_C240 & 0x0F`.

**Dans ce dump : `byte_C240 = [word_1658+8]` = `0x00`** (`word_1658` -> `0xE4022`), et la signature du
bloc n existe qu en **2 copies** (`0xE4022` et `0xF4022`, toutes deux a `0x00`).
=> `r9 = 0x30` => `C330 & 0x0F = 0` => **switch de limitation sur `> 0x0B` => aucune limitation par
rapport appliquee**. Le calcul N/V n est donc pas actif dans ce build (bibliotheque effacee, variante
BVA, ou codage).

#### 4. Le regulateur et le rapport
- rejet `byte_C330 & 0x0F` in {`0x0B`, `0x0C`} -> `byte_D9B3 = 0x92` (point mort / marche arriere) ;
- **aucun `FGR_GangMin`** : pas de test « rapport >= 3 ou 4 » dans la tache `0x340` ;
- masque `[word_14A8]` = **`0xBFFE`** (bit0 = 0, bit1 = 1) : refus frein/embrayage `0x8E` quand le bit
  teste vaut 1 => bit « embrayage » actif dans la calibration, **a verifier sur banc**.

#### 5. ERRATA E5 — etiquetage du bloc `0xE2788`

`2500 / 25000 / 1000 / 4500` sont **exacts comme donnees** et compares a `C562` / `C91C`, mais ce n est
PAS `FGR_vMin` / `FGR_nMin` (doc : 4000-6000 km/h x100 et 1200-1300 tr/min). C est une **fenetre
d autorisation dure**. Ni `4000`, ni `6000`, ni un scalaire `4` de rapport minimum n existent dans la
tache `0x340`.

---

### B.46 — Gangberechnung : la chaine complete du rapport engage

#### 0. ERRATA E6/E7/E8
- E6 : « aucune division ne combine regime et vitesse » est FAUX. La division est en
  l.232301 (sub_CF774). Le balayage l a ratee car le motif etait (div|divu|divl) et non divlu.
- E7 : « le rapport n est pas calcule » est FAUX (confusion non actif / non calcule).
- E8 : C576/C93E ne sont pas nuls : c est le ratio V/N filtre (r5 = 2e registre de retour de
  unk_24BA). Toute l etape 98 section 2.5 est a jeter.

#### 1. Ratio : V x 256 / N (l.232289-232321)

    r0 = C42E (regime) ; si 0 -> ratio 0
    MDL = C578 (vitesse) x 256 ; divlu r0 ; saturation = [word_1470+0Eh] = 2560
    unk_24BA(r2, gain word_185C, etat C56A) -> r5 = ratio filtre -> C93E -> C576

word_1470 -> 0xE225A ; word_185C -> 0xE4B70. 2560 = borne haute de la derniere fenetre de la
table de rapports : coherence croisee.

#### 2. loc_B0000+2 = Gangberechnung, table word_1A9A -> 0xE81A4

Codes (octets +0..+5) : 01, 0x0B (point mort), 02, 03, 04, 05. Quatre mots par rapport :
[borne basse][drapeau a][drapeau b][borne haute] ; bit 0x40 = incertitude (hysteresis, r13 =
rapport precedent). Bandes : 1re <202 ; neutre 234-338 ; 2e 338-559 ; 3e 559-826 ; 4e 826-1116 ;
5e 1116-2560.

Appel l.177478, conditionne par byte_C2C0 == 1 ; sinon branche trame boite
(unk_1D7E(#0C83E, word_1B24)).

#### 3. Escalier Gangstufen en N/V x100 : 0xE80C4 -> 0xE8164

7 enregistrements de 10 mots, escaliers de 6 marches. Les deux derniers sont quasi identiques
(10500 7000 4600 3500 2700 / 10500 7000 4500 3500 2700) = seuil d entree / seuil de sortie
(hysteresis). Cellules : 1A8A->0xE8084, 1A8C->0xE80A0, 1A8E->0xE816C, 1A92->0xE8188,
1A9A->0xE81A4, 1AA0->0xE81E2.

#### 4. Chaine de bout en bout

C42E, C578 -> divlu (l.232301) -> filtre -> C93E/C576 -> loc_B0000+2 (table 0xE81A4) ->
byte_C330 (+ byte_D398 0-7) -> switch 0xA62 (1B54/1B56/1B58/1B64/1B5C) -> D9A2 -> D3EC/D3DA ;
et refus regulateur 0x92 si code 0x0B/0x0C.

Verrou restant : byte_C2C0 == 1 (octet de telecodage) — a chercher dans l EEPROM de codage.

---

### B.47 — Abords de l escalier Gangstufen et bloc FGR reel (facteur 0,01)

#### 1. Autour de l escalier 0xE80E0-0xE8168 : AUCUN scalaire FGR

Enregistrement = 10 mots = [6 seuils N/V x100][1 valeur][3 valeurs identiques] :

    0xE8144 : 12500 10500 7000 4600 3500 2700 2350 1800 1800 1800
    0xE8158 : 12000 10500 7000 4500 3500 2700 2350 1800 1800 1800

Pas de 40/45/50/55/60, pas de 200/210/220/250, pas de 1200/1250/1300, aucun mot = 4.
Echelle : 2700 3500 4600 7000 10500 = 27/35/46/70/105 x100 (meme escalier que la doc).

#### 2. Bloc FGR reel : 0xE275C -> 0xE2798

    0xE275C : 49150 1 1 40 0 200 500 20000 4000 400
    0xE2770 : 0 100 300 1024 512 768 8 10000 896 896 0 8 2500 25000 1000 4500
    0xE2790 : 2560 768 4000 1000 5000 3000 4000

Attributions prouvees par le code :
- 0xE275C = 0xBFFE : masque frein/embrayage ([word_14A8] & 1 / & 2, l.183926).
- 0xE2762 = 40 : TEMPORISATION, pas une vitesse (r4 = word_C0E8 - word_F91C puis cmp 40, l.183421/183465).
- 0xE276A = 20000 (= 200 km/h) : FGR_vMax, cmp avec word_D9CE, l.185490. => FACTEUR 0,01.
- 0xE2770 = 0 : masque des options 0x04 / 0x10 (and #4, and #10h) => desactivees.
- 0xE2788 = 2500 (25 km/h), 0xE278A = 25000, 0xE278C = 1000, 0xE278E = 4500 (refus 0x86/0x87/0x88).
- Aucun mot = 4 dans 0xE2700-0xE2800 : pas de FGR_GangMin dans cette zone.

#### 3. Facteur tranche : 0,01

60 km/h s ecrit 6000 (0x1770), 40 km/h s ecrit 4000 (0x0FA0). Le 200 de 0xE2766 n est pas utilise
par le code, le 20000 de 0xE276A l est. Les vMin/vMax lues par le regulateur sont donc en 0,01 km/h.

#### 5. Vitesse et rapport engagé

| recherche | résultat |
|---|---|
| axes « vitesse » | **2** : `0xE4954` `[C337][2][0 250]` ; `0xE5150` `[C590][8][0 20 30 40 50 60 70 90]` |
| carte exploitant `C590` | `0xE513C` `[D202][8][1000…3000] × [C590]` — grille **constante en vitesse** |
| axe « rapport » 0…6 | **aucun** dans tout le Datensatz |

⇒ soit le rapport est traité **en code** (variable d’état), soit la vitesse est **reconstruite** par
`unk_20AC(x, 1000, 0xC5A)` (l.156803, 157583).










Max 17920 ⇒ 1,79 ms si µs×0,1. Non tranché (manque le coefficient appliqué après `[r0+#8]`).




⇒ **sous-système altitude présent mais quasi neutralisé** dans cette calibration : seuls `0xE7828`
(boost limiter) et `0xE69FA` (dérate) agissent réellement.




---

### B.21 — ★★★ Le VOCABULAIRE des grandeurs : catalogue d’identifiants à `EA 0xEA24C`

#### 1. Le même format, avec un code interne au lieu d’un code DTC

À `EA 0xEA1A8` on trouve un record de **exactement 32 octets, même trame**, mais son premier mot
n’est pas un code DTC :

```
EA 0xEA1A8 : 0603 0000 0000 0000 0000 0000 0000 0000
EA 0xEA1B8 : 0000 0000 0F10 0F00 0F65 0F8C 0F7F 0001
EA 0xEA1C8 : C302 ...
```

⇒ `[+0x00]` = **code interne** (`0603`), `[+0x12]` = 5 identifiants, `[+0x1C]` = classe, `[+0x1D]` = seuil A,
`[+0x1E]` = seuil B, `[+0x1F]` = `0xC3`. **C’est exactement le descripteur lu aux étapes 69-72** via
`0xCCB2 + 2·index` (classe bits 0-1, seuils `+0x1D`/`+0x1E`). **La boucle est fermée :**
les conditions de maintien d’un défaut et les records DTC partagent **une seule trame de 32 octets**,
la seule différence étant la nature du premier mot (code interne vs code DTC).

#### 2. ★ Le catalogue d’identifiants — `EA 0xEA254` → `EA 0xEA30A`

Une liste continue de mots, **le vocabulaire complet des grandeurs** :

```
0F12 0F02 0F61 0F60 0FFA 0FF8 0FF9 0FF6 0FF7 0F63
0FFC 0F00 0F70 0F71 0F6F 1F50 1001 1005 0FD6 0F7F
0F7C 0F40 0F42 DF11 DF12 0F30 0F32 DF13 DF14 0F64
1E80 0F80 DC86 0F8D DC87 0F8C 0F82 0F8B 0F8F 0F96
0F8A 0F83 1F80 1F81 1F82 1F83 1F58 1F55 1F56 0FD7
0F10 1F53 1F63 1F64 1F5E 1F5F 1F78 1F79 1F7A 1F7B
0EA4 0E80 0E87 0EA5 0E81 1F42 1F41 1F4D 1F4E 1F4F
1F51 0F10 0F08 E4DC E4DD 0FFB 1114 E4D0 0F01 E4E1
E4D6 E4D2 E4D8 E4DE E4DF 0F00 E4D5 E4D1
```

**Preuves convergentes :**

- tous les identifiants des records DTC s’y retrouvent (`0F10 0F30 0F32 0F64 0FFC 0EA5 …`) ;
- les 20 valeurs de `word_1424` (`0xE11C4`) en sont un sous-ensemble (`0F61 0FFA 0F80 0F64 0F7F 0F08 0F8A …`) ;
- **`0E80`**, l’identifiant propre à l’EGR, est présent à **`EA 0xEA2D6`**, entouré de `0EA4 0E87 0EA5 0E81` :
  un **groupe de cinq identifiants `0x0Exx`** — le bloc EGR/pression.

#### 3. Remarque sur « 0 données »

La majorité des records DTC ont leurs 8 mots de données à `0000` : la condition se réduit alors au code
lui-même. Comme le record est en **flash**, le comptage ne peut pas s’incrémenter sur place : il se fait
dans le miroir RAM `0xCAD0 + 4·code` (état) et `0xFD21 + code` (bits), cf. § B.14. Les records à mots
non nuls (39 relevés) sont ceux qui portent des conditions supplémentaires.

*Données : `records_DTC_segmentE.csv` ; catalogue d’identifiants à recopier dans `identifiants_grandeurs.csv`.*


---

### B.20 — ★★★ LA TABLE DES CODES DTC « EN CLAIR » (page `0xE0000`, en bas du segment E)

**Consigne de l’utilisateur, vérifiée et consignée :** *« un code écrit en clair, ex P1401 ⇒ 0x1401,
suivi de 8 ou 16 mots (taille variable) qui contiennent des seuils ; ces zones sont placées plutôt en bas
du segment E »* — **c’est exact.**

#### 1. Résolution d’adresse

```
EA = 0xE0000 | (pointeur & 0x3FFF)        ; offset dans la page de 16 Ko en tête du segment E
offset fichier = 0x60000 + (EA - 0xE0000)
```

Les records s’étendent de **`EA 0xE0B10` à `EA 0xE4F52`**, soit **offset fichier `0x60B10`–`0x64F52`** :
bien « en bas » du segment E, et non à `0x60000` exactement.

#### 2. Format du record

| offset | contenu | taille |
|---|---|---|
| `+0x00` | **code DTC en clair** (16 bits, ex. `1169` = P1169) | 2 o |
| `+0x02` … | **mots de données / seuils** (souvent à 0) | 8 mots = 16 o (variante 16 o : 7 mots) |
| `+0x12` … `+0x1B` | **5 identifiants de grandeurs** `0x0Fxx` (`0xE4xx` pour la famille FAP/rampe) | 10 o |
| `+0x1C` | **classe** (0…3) | 1 o |
| `+0x1D` | **seuil A** | 1 o |
| `+0x1E` | **seuil B** (`0xFF` = jamais de guérison) | 1 o |
| `+0x1F` | **sentinelle `0xC3`** — le mot final est donc `0xC3xx` où `xx` = seuil B | 1 o |

**Deux tailles : 32 octets = 16 mots** (73 records) et **16 octets = 8 mots** (20 records) — le « 8 ou 16 mots »
annoncé par l’utilisateur.

#### 3. Les 93 records relevés

| EA | offset fich. | taille | DTC | classe | seuil A | seuil B | identifiants |
|---|---|---|---|---|---|---|---|
| `0xE0B10` | `0x60B10` | 16 o | **P0100** | 2 | 2 | 2 | `` |
| `0xE0DCA` | `0x60DCA` | 32 o | **P0106** | 0 | 121 | 128 | `6463 6968 7270 7574 7776` |
| `0xE1138` | `0x61138` | 16 o | **P0102** | 0 | 1 | 2 | `` |
| `0xE120C` | `0x6120C` | 32 o | **P0170** | 0 | 255 | 0 | `0F10 0F00 0F30 0F80 0F7F` |
| `0xE12E0` | `0x612E0` | 32 o | **P0960** | 0 | 3 | 238 | `251C 2710 C42E 0002 0258` |
| `0xE12F0` | `0x612F0` | 16 o | **P2328** | 0 | 3 | 238 | `` |
| `0xE21CC` | `0x621CC` | 32 o | **P0303** | 3 | 248 | 1 | `2B01 FFFF F8FF FFFF FFFF` |
| `0xE21CE` | `0x621CE` | 16 o | **P0305** | 1 | 3 | 3 | `` |
| `0xE21D2` | `0x621D2` | 32 o | **P0303** | 0 | 1 | 1 | `FFFF FFFF F8FF C301 0000` |
| `0xE21D6` | `0x621D6` | 32 o | **P0503** | 0 | 3 | 1 | `F8FF C301 0000 01F4 C301` |
| `0xE21DC` | `0x621DC` | 16 o | **U0303** | 3 | 248 | 1 | `` |
| `0xE224A` | `0x6224A` | 16 o | **P0105** | 0 | 0 | 1 | `` |
| `0xE2258` | `0x62258` | 32 o | **U0301** | 1 | 1 | 0 | `000A 6FFE 0168 003C 003C` |
| `0xE2290` | `0x62290` | 32 o | **U0300** | 0 | 39 | 0 | `00C8 1388 0D67 2328 2328` |
| `0xE22A0` | `0x622A0` | 16 o | **P2328** | 0 | 39 | 0 | `` |
| `0xE2314` | `0x62314` | 32 o | **U1008** | 1 | 0 | 1 | `09C4 05DC 0101 C303 112B` |
| `0xE231E` | `0x6231E` | 16 o | **P0258** | 1 | 1 | 3 | `` |
| `0xE232C` | `0x6232C` | 32 o | **U0303** | 1 | 0 | 1 | `0000 2710 C301 0032 0028` |
| `0xE2372` | `0x62372` | 32 o | **P1517** | 1 | 0 | 2 | `0F10 0F08 0F65 0F8C 0F7F` |
| `0xE23A2` | `0x623A2` | 16 o | **P0600** | 0 | 0 | 50 | `` |
| `0xE273C` | `0x6273C` | 32 o | **P0568** | 0 | 0 | 2 | `0F10 0F70 0F08 0F65 0F7F` |
| `0xE2798` | `0x62798` | 16 o | **P1388** | 2 | 0 | 1 | `` |
| `0xE2FCA` | `0x62FCA` | 32 o | **P1101** | 2 | 2 | 2 | `0F10 0F41 0F40 0F80 0F01` |
| `0xE304A` | `0x6304A` | 32 o | **P0470** | 0 | 255 | 0 | `0F10 0F41 0F40 0F42 0F7F` |
| `0xE30C6` | `0x630C6` | 32 o | **P1421** | 1 | 0 | 5 | `0FFB E4D6 1114 0F10 E4D7` |
| `0xE313C` | `0x6313C` | 32 o | **P1425** | 1 | 0 | 5 | `0F10 E4D7 E4D6 1114 0FFB` |
| `0xE318C` | `0x6318C` | 32 o | **P0530** | 0 | 2 | 2 | `0F10 0F00 0F01 0E91 0F7F` |
| `0xE31DE` | `0x631DE` | 32 o | **P1429** | 3 | 0 | 4 | `E4D0 0F10 E4D1 0F8C E4D2` |
| `0xE3230` | `0x63230` | 32 o | **P1168** | 0 | 255 | 0 | `0F64 0EA5 0FFC 0F7F 0F10` |
| `0xE3282` | `0x63282` | 32 o | **P0190** | 3 | 0 | 4 | `0F10 0F64 2066 0FFC 0EA5` |
| `0xE347C` | `0x6347C` | 32 o | **P0180** | 1 | 2 | 2 | `0F00 2066 0F10 0F80 0FFC` |
| `0xE3598` | `0x63598` | 32 o | **P0110** | 0 | 2 | 2 | `0F10 0F00 0F01 0F30 0F7F` |
| `0xE35FA` | `0x635FA` | 32 o | **P0604** | 3 | 0 | 255 | `0F60 0FFA 0F10 0FF6 0F7F` |
| `0xE361A` | `0x6361A` | 32 o | **P0221** | 3 | 0 | 255 | `0F60 0FFA 0F10 0F80 0F71` |
| `0xE3664` | `0x63664` | 32 o | **P0121** | 3 | 0 | 255 | `0F60 0FFA 0F10 0F80 0F71` |
| `0xE36AC` | `0x636AC` | 32 o | **P0560** | 2 | 2 | 2 | `0F10 0F01 0F65 0F08 0F7F` |
| `0xE3734` | `0x63734` | 32 o | **P1169** | 3 | 0 | 255 | `0F10 0F65 0FF8 0FF9 0F80` |
| `0xE3754` | `0x63754` | 32 o | **P1170** | 3 | 0 | 255 | `0F65 0F01 0FF8 0FF9 0F80` |
| `0xE3798` | `0x63798` | 32 o | **P1614** | 1 | 0 | 2 | `0FF6 0F65 0FF7 0F10 0F7F` |
| `0xE37DC` | `0x637DC` | 32 o | **P1614** | 2 | 0 | 2 | `0FF6 0F65 0FF7 0F10 0F7F` |
| `0xE37FA` | `0x637FA` | 16 o | **U0302** | 3 | 19 | 170 | `` |
| `0xE3802` | `0x63802` | 32 o | **P0104** | 1 | 0 | 210 | `000C 000A 0045 000C 000A` |
| `0xE3812` | `0x63812` | 16 o | **P1770** | 1 | 0 | 210 | `` |
| `0xE38B8` | `0x638B8` | 32 o | **P0115** | 2 | 0 | 2 | `0F10 0F00 0F01 2066 0F80` |
| `0xE38FA` | `0x638FA` | 32 o | **C1014** | 0 | 9 | 210 | `03E8 0514 05DC 0708 07D0` |
| `0xE3AEC` | `0x63AEC` | 32 o | **P0100** | 3 | 0 | 4 | `0F10 0F32 0F01 0F30 0F40` |
| `0xE3B0C` | `0x63B0C` | 32 o | **P0101** | 3 | 0 | 4 | `0F10 0F32 0F01 0F30 0F40` |
| `0xE3D96` | `0x63D96` | 32 o | **P0403** | 2 | 2 | 2 | `0F10 0F32 0E80 0F30 0F80` |
| `0xE3E42` | `0x63E42` | 16 o | **P0384** | 0 | 3 | 186 | `` |
| `0xE3E9C` | `0x63E9C` | 32 o | **P0401** | 3 | 0 | 4 | `0F10 0F32 0E80 0F30 0F80` |
| `0xE3EBC` | `0x63EBC` | 32 o | **P0402** | 2 | 2 | 2 | `0F10 0F32 0E80 0F30 0F80` |
| `0xE4008` | `0x64008` | 16 o | **U0301** | 3 | 0 | 1 | `` |
| `0xE4012` | `0x64012` | 16 o | **P0707** | 2 | 11 | 15 | `` |
| `0xE401C` | `0x6401C` | 16 o | **P0504** | 3 | 16 | 0 | `` |
| `0xE40B6` | `0x640B6` | 32 o | **P0700** | 0 | 255 | 0 | `0F10 0F00 0F80 2315 0F7F` |
| `0xE415A` | `0x6415A` | 32 o | **P1000** | 2 | 0 | 2 | `0F10 0F65 2308 2309 230A` |
| `0xE417A` | `0x6417A` | 32 o | **P1001** | 1 | 0 | 2 | `0F10 0F65 2308 2309 230A` |
| `0xE422C` | `0x6422C` | 32 o | **P0571** | 0 | 2 | 2 | `0F10 0F86 0F65 0F71 0F70` |
| `0xE425A` | `0x6425A` | 32 o | **P1521** | 0 | 2 | 2 | `0F10 0F86 0F08 0F71 0F80` |
| `0xE42A0` | `0x642A0` | 32 o | **P0148** | 3 | 6 | 40 | `1770 0280 001A D6D8 157C` |
| `0xE434C` | `0x6434C` | 32 o | **P2304** | 0 | 23 | 194 | `07D0 0BB8 0FA0 1388 157C` |
| `0xE45DA` | `0x645DA` | 32 o | **P0201** | 3 | 0 | 4 | `0F10 2066 0F80 0FFC 0F30` |
| `0xE45FA` | `0x645FA` | 32 o | **P0203** | 3 | 0 | 4 | `0F10 2066 0F80 0FFC 0F30` |
| `0xE461A` | `0x6461A` | 32 o | **P0204** | 3 | 0 | 4 | `0F10 2066 0F80 0FFC 0F30` |
| `0xE463A` | `0x6463A` | 32 o | **P0202** | 3 | 0 | 4 | `0F10 2066 0F80 0FFC 0F30` |
| `0xE46DA` | `0x646DA` | 32 o | **P1135** | 1 | 0 | 2 | `0F10 0F00 0FFC 0F7F 0F80` |
| `0xE46FA` | `0x646FA` | 32 o | **P1110** | 0 | 255 | 0 | `0F00 0F10 0F80 0F71 0F8A` |
| `0xE471A` | `0x6471A` | 32 o | **P1402** | 2 | 2 | 2 | `0F10 0E80 0E82 0F80 0F30` |
| `0xE473A` | `0x6473A` | 32 o | **P1109** | 0 | 2 | 2 | `0F00 0F10 0F80 0F7F 0F70` |
| `0xE476A` | `0x6476A` | 16 o | **P0477** | 2 | 255 | 0 | `` |
| `0xE477A` | `0x6477A` | 32 o | **P1451** | 2 | 2 | 2 | `0F10 E4D8 E4D9 E4DA E4DB` |
| `0xE478A` | `0x6478A` | 16 o | **P0417** | 2 | 2 | 2 | `` |
| `0xE479A` | `0x6479A` | 32 o | **P1458** | 2 | 255 | 0 | `0F00 0F01 0F10 0F80 E4D6` |
| `0xE47BA` | `0x647BA` | 32 o | **P1404** | 2 | 2 | 2 | `0F10 0F80 0F65 0F70 0F7F` |
| `0xE47DA` | `0x647DA` | 32 o | **P1608** | 0 | 255 | 0 | `0F10 0F00 0F01 0EA2 0EA8` |
| `0xE47FA` | `0x647FA` | 32 o | **P1108** | 0 | 2 | 2 | `0F00 0F10 0F80 0F7F 0F01` |
| `0xE481A` | `0x6481A` | 32 o | **P1107** | 2 | 2 | 2 | `0F10 0F8C 0F40 0F30 1E81` |
| `0xE487A` | `0x6487A` | 32 o | **P1403** | 0 | 2 | 2 | `0F01 0F00 0F10 0F80 0F7F` |
| `0xE489A` | `0x6489A` | 32 o | **P1404** | 0 | 2 | 2 | `0000 0000 0000 0000 0000` |
| `0xE4980` | `0x64980` | 32 o | **P1606** | 0 | 255 | 0 | `0F00 2066 0F10 0F40 0F08` |
| `0xE49A0` | `0x649A0` | 32 o | **P1606** | 0 | 255 | 0 | `0F00 2066 0F10 0F40 0F08` |
| `0xE49D8` | `0x649D8` | 32 o | **P1601** | 0 | 255 | 0 | `0F10 0F65 0F7F 0EA6 2066` |
| `0xE49F8` | `0x649F8` | 32 o | **P1003** | 1 | 0 | 2 | `0F10 2315 0F8C 0FD8 0F86` |
| `0xE4A24` | `0x64A24` | 32 o | **P0381** | 0 | 255 | 0 | `0F10 0F00 0F65 0F01 0F7F` |
| `0xE4A50` | `0x64A50` | 32 o | **P1300** | 0 | 255 | 0 | `0F00 0F10 0F01 0F65 0F80` |
| `0xE4A70` | `0x64A70` | 32 o | **P0191** | 3 | 0 | 4 | `0F10 0F64 2066 0FFC 0EA5` |
| `0xE4B26` | `0x64B26` | 32 o | **P1537** | 2 | 0 | 255 | `0F60 0FFA 0F10 0F80 0F71` |
| `0xE4C4A` | `0x64C4A` | 32 o | **P1442** | 2 | 0 | 5 | `E4E3 E4D3 E4D1 E4E2 E4D4` |
| `0xE4C6A` | `0x64C6A` | 32 o | **P1446** | 2 | 5 | 5 | `E4E3 E4D3 E4D1 E4E2 E4D4` |
| `0xE4C8A` | `0x64C8A` | 32 o | **P1435** | 2 | 0 | 5 | `E4D3 0FD7 0F10 E4E2 E4D1` |
| `0xE4E2A` | `0x64E2A` | 32 o | **P0384** | 0 | 11 | 0 | `0258 C31D 0023 FFEC FFF6` |
| `0xE4E30` | `0x64E30` | 16 o | **U3830** | 0 | 2 | 29 | `` |
| `0xE4F52` | `0x64F52` | 16 o | **P2710** | 0 | 20 | 20 | `` |

#### 4. Codes directement liés à l’EGR et au FAP

| DTC | EA | identifiants | lecture |
|---|---|---|---|
| **P0401** | `0xE3E9C` | `0F10 0F32 0E80 0F30 0F80` | EGR : débit insuffisant |
| **P0402** | `0xE3EBC` | `0F10 0F32 0E80 0F30 0F80` | EGR : débit excessif |
| **P0403** | `0xE3D96` | `0F10 0F32 0E80 0F30 0F80` | EGR : circuit |
| **P0470** | `0xE304A` | `0F10 0F41 0F40 0F42 0F7F` | capteur de pression d’admission / cohérence patmo (B.24) |
| P0477 | `0xE476A` | (variante 16 o) | sortie commande de pression d’échappement |
| P0190 / P0191 | `0xE3282` / `0xE4A70` | `0F10 0F64 2066 0FFC 0EA5` | pression de rampe |
| P1168 / P1169 / P1170 | `0xE3230` / `0xE3734` / `0xE3754` | `0F64 0EA5 0FFC …` | famille PSA rampe/dose |
| P1401→P1404, P1421/1425/1429, P1435, P1442/1446, P1451/1458 | `0xE30C6`…`0xE4C8A` | `E4D0`…`E4E3` | famille PSA vanne EGR / dose (identifiants `0xE4xx`) |

⇒ Les trois codes **P0401 / P0402 / P0403 partagent exactement les mêmes cinq identifiants**
(`0F10 0F32 0E80 0F30 0F80`) : ce sont les grandeurs du diagnostic EGR. **`0E80` est spécifique à l’EGR**
(absent des autres codes).

#### 5. Constat négatif important

Sur les **1 277 pointeurs** des 96 listes du § B.16, seuls **36 tombent sur un début de record**
(34 avec un décalage nul, 2 de plus dans une fenêtre de ±8 octets). **Les 96 listes ne sont donc PAS
l’index des records DTC** — piste fermée, à ne pas rouvrir.

#### 6. Piste fermées au passage (ne pas rejouer)

- pointeurs des 96 listes = records DTC → **non** (36/1 277) ;
- record à trame fixe terminée par `0xC3` **et** champs `+0x1C…+0x1E` → **oui**, mais seulement 93 records
  détectés automatiquement : le balayage n’est pas exhaustif (des records se confondent avec des courbes) ;
- `0xCF5EC` lu en page `0x3A` → **non** ; la bonne règle est `0xE0000 | (p & 0x3FFF)`.

*Données : `records_DTC_segmentE.csv` (93 records, EA + offset fichier + DTC + classe + seuils + identifiants + mots).*


---

### B.19 — ★★★ Les codes DTC **en clair** : record de 16 mots = `[DTC][8 mots][5 identifiants][classe][seuil A][seuil B][0xC3]`

**LA BONNE RÉSOLUTION D’ADRESSE** (elle débloque tout) : les pointeurs des 96 listes se résolvent par
`EA = 0xE0000 | (pointeur & 0x3FFF)`, c’est-à-dire **en offset dans la page de 16 Ko en tête du segment E**
— et non par page `0x3A` comme je l’avais supposé à l’étape 70.

```
EA 0xE3730 : 0000 0045 1169 0000 0000 0000 0000 0000
EA 0xE3740 : 0000 0000 0000 0F10 0F65 0FF8 0FF9 0F80
EA 0xE3750 : 0003 C3FF 1170 0000 0000 0000 0000 0000
```

| offset | contenu | exemple `P1169` |
|---|---|---|
| `+0x00` | **code DTC en clair** (16 bits) | `1169` = **P1169** |
| `+0x02` … `+0x11` | 8 mots de données (16 o) | `0000` ×8 |
| `+0x12` … `+0x1B` | **5 identifiants de grandeurs** (`0x0Fxx`) | `0F10 0F65 0FF8 0FF9 0F80` |
| `+0x1C` | **classe** (0…3) | `03` |
| `+0x1D` | **seuil A** | `00` |
| `+0x1E` | **seuil B** (`0xFF` = jamais de guérison) | `FF` |
| `+0x1F` | **sentinelle `0xC3`** | `C3` |

⇒ **record de 32 octets = 16 mots**, et le suivant commence immédiatement : `0xE3754` = `1170` (P1170).
Une **variante de 16 octets** existe aussi (28 pointeurs vérifiés).

#### Les 43 records validés (extrait)

| index | EA | DTC | classe | seuil A | seuil B | identifiants |
|---|---|---|---|---|---|---|
| 0 | `0xE2372` | **P1517** | 1 | 0 | 2 | `0F10 0F08 0F65 0F8C 0F7F` |
| 0 | `0xE2FCA` | **P1101** | 2 | 2 | 2 | `0F10 0F41 0F40 0F80 0F01` |
| 4 | `0xE3734` | **P1169** | 3 | 0 | 255 | `0F10 0F65 0FF8 0FF9 0F80` |
| 5 | `0xE3754` | **P1170** | 3 | 0 | 255 | `0F65 0F01 0FF8 0FF9 0F80` |
| 6 | `0xE3282` | **P0190** | 3 | 0 | 4 | `0F10 0F64 2066 0FFC 0EA5` |
| 9 | `0xE36AC` | **P0560** | 2 | 2 | 2 | `0F10 0F01 0F65 0F08 0F7F` |

#### ★ Conséquence : la question ouverte sur `word_1424` est RÉSOLUE

Les identifiants de ces records (`0F10 0F65 0F7F 0F64 0F08`…) sont **exactement l’alphabet de `word_1424`**
(`0xE11C4`). Donc les 20 valeurs de `0xE11C4` sont des **identifiants de grandeurs**, et non des adresses :
`0x0Fxx` = *« identifiant de la mesure n° 0Fxx »*. Le test d’intersection vide de l’étape 70 portait sur les
**pointeurs**, pas sur ces identifiants — d’où le faux négatif.

*Données : `dtc_records_valides.csv` (43 records 32 o validés) et `dtc_records_32o.csv` (1 277 candidats).*


---

### B.18 — ★★ Les CINQ conditions de maintien d’un défaut (algorithme complet)

Le désassemblement de `loc_CF0B6` … `loc_CF14E` (l. 231240-231300) donne l’algorithme exact qui décide
si un enregistrement de défaut **reste** en mémoire ou est **supprimé**. `r3` = enregistrement,
`r0` = `[0xCCB2 + 2·code]` = descripteur du code.

| # | condition | ligne | sinon |
|---|---|---|---|
| 1 | `descr[+0x00]` bit 0 **doit être 0** (validité du code) | 231252 | supprimé |
| 2 | **classe** `descr[+0x1C] & 3` **< 2** ⇒ il faut `enr[+1]` bit 0 **= 1** ; **≥ 2** ⇒ il faut bit 0 **= 0** | 231257-231268 | suprimé |
| 3 | `enr[+7]` : `0` ⇒ supprimé ; `1` ⇒ bit 3 de `enr[+1]` doit être 0 ; `> 1` ⇒ il doit être 1 | 231270-231283 | supprimé |
| 4 | si `enr[+1]` bit 6 posé ⇒ `enr[+6]` doit **égaler** `word_142A + 9` (octet de **variante/codage**) | 231284-231289 | supprimé |
| 5 | `enr[+4] <= descr[+0x1D]` | 231290-231293 | supprimé |
| 6 | `enr[+5] <= descr[+0x1E]` (si `descr[+0x1E]` = 0, on prend **1**) | 231294-231299 | supprimé |

**Corrections aux étapes 69 et 71 :**

- `0xCCB2 + 2·code` n’est **jamais écrit** en marche : les **13 sites** du firmware le **lisent** seulement ;
  il est rempli une fois au démarrage (l. 231171-231180).
- `descr[+0x1C]` n’est **pas** un seuil : c’est un **code de classe 0…3** (bits 0-1) doublé d’un **masque**
  (bits 3-7, `andb #0F8h` l. 231777). Les **seuils** sont `+0x1D` et `+0x1E`.

⇒ **Deux seuils numériques par code de défaut** (`+0x1D`, `+0x1E`) comparent les compteurs `enr[+4]` et
`enr[+5]` ; et **un octet de variante** (`word_142A + 9`) filtre les défauts selon le **codage** du calculateur.


---

### B.17 — ★★ Verrou DPP levé : les 1 277 pointeurs sont des **adresses RAM**, une plage privée par code

#### 1. La configuration de pages du firmware (enfin établie)

```asm
scxt DPP0, #0        ; l. 96805
scxt DPP1, #0        ; l. 96806   <-- DPP1 = 0, PAS 1
scxt DPP2, #2        ; l. 96807
scxt DPP3, #3        ; l. 96808
```

⇒ l’espace 16 bits couvre **EA `0x00000`–`0x0FFFF`** (64 Ko de RAM/périphériques internes).
Les pages flash ne sont ouvertes que **localement**, six fois : `DPP0 = 0x22` (l. 96530, 97450, 98358,
98477, 98515, 111273), `DPP1 = 0x21` (l. 98479), `DPP2 = 0x24` (l. 233064, 233137), `DPP2 = 0x48` (l. 111665).
Le reste du temps, les DPP sont **sauvegardés/restaurés** depuis `word_C1DA` / `word_C1DC`
(`mov word_C1DA, DPP0`, l. 112878 ; `scxt DPP0, word_C1DA`, l. 125397 ; écriture calculée l. 199535).

#### 2. Conséquence : les listes pointent la **RAM**

Aucune des routines qui consomment les 96 listes (`sub_CEC02`, le bloc l. 231157-231530) ne modifie un DPP.
⇒ un pointeur `0xA1A8` vaut **EA `0xA1A8`**, c’est-à-dire une **variable RAM**, pas une adresse flash.
Mon test de l’étape 70 (« le contenu à `fo 0xA1A8` est du code ») comparait donc une adresse RAM à un
offset de fichier : l’hypothèse à réfuter était mal posée, le résultat est maintenant net.

#### 3. Ce que révèle la géométrie des 1 277 pointeurs

| constat | mesure |
|---|---|
| plages **disjointes** | seules **3 paires sur 4 465** se chevauchent ⇒ **chaque code possède sa plage RAM privée** |
| écart entre pointeurs consécutifs | **6 o** (316×), 12 (132×), 4 (92×), 2 (83×), 32 (78×), 10, 8, 36, 28, 24 |
| taille des blocs | des **enregistrements de 6 / 12 / 32 octets** |

| code | plage RAM | nb d’enregistrements |
|---|---|---|
| 0 | `0xA1A8`–`0xBAB0` | **139** |
| 1 | `0x2372`–`0x2736` | 10 |
| 2 | `0x9462`–`0x94C8` | 14 |
| 3 | `0xBAB6`–`0xBB9A` | 11 |
| 7 | `0x4A70`–`0x4A96` | 3 |
| 8 | `0x94CE`–`0xA128` | 49 |

⇒ **chaque code de défaut possède, en RAM, une table privée d’enregistrements de 6 / 12 / 32 octets** ;
la liste du Datensatz en donne l’index. Ces tables sont **construites au démarrage** à partir de la calibration :
c’est là, et non dans la liste, que se trouvent les seuils.

#### 4. Retour sur `word_1424` (`0xE11C4`)

Les valeurs `0x0F10 0x0F61 0x0F80 0x0FFA …` appartiennent au **même espace** : ce sont des **adresses RAM**
de la page `0x0F00`. Donc les « trous » constatés à l’étape 67 ne sont pas des marqueurs : ce sont
**les entrées qui ne sont pas des codes ≤ 17** — seules `0x0005` et `0x000F` en sont. La lecture « tableau mixte »
est la bonne.


---

### B.16 — Réseau code de défaut → listes de pointeurs : 96 listes, 1 277 pointeurs (et 3 hypothèses réfutées)

**Ce qui est acquis.** La table de 96 pointeurs de `EA 0xCF5EC` (page `0x33`) donne 96 structures
**distinctes** dans le Datensatz, `0xE1426`–`0xE1E20`, soit **2 554 octets**, et chacune est une
**liste de pointeurs de 2 octets** (décalages croissants, ce qui est l’auto-validation : une suite
croissante ne peut pas être du code).

| mesure | valeur |
|---|---|
| listes | 96 (95 non vides) |
| pointeurs | **1 277**, tous distincts |
| plage des pointeurs | `0x11EC` – `0xBB9A` |
| longueur des listes | 2 o (43 listes → 1 seul pointeur) … 278 o (`EA 0xE1CF4`, code 0) |
| moyenne | ≈ 13 pointeurs par code de défaut |

⇒ **un code de défaut donné est associé à ≈ 13 grandeurs surveillées.** C’est le réseau
« défaut ↔ mesures » du calculateur.

**Trois hypothèses testées ce jour, trois réfutées** (consignées pour ne pas les rejouer) :

1. « Ces listes contiennent des identifiants `0x0Fxx` comme `word_1424` » → **faux** : intersection
   **vide** (0 des 20 identifiants de `0xE11C4`). L’alphabet `0x0Fxx` et les listes de défauts sont deux mondes.
2. « Les blocs pointés suivent une trame fixe de 32 octets terminée par la sentinelle `0xC3` » → **faux** :
   seulement **16 blocs sur 96** finissent par `0xC3` à `+0x1F` ; les autres valeurs sont majoritairement
   `0x00` (39 blocs).
3. « Les pointeurs sont des adresses linéaires résolubles » → **non tranché** : `0xA1A8` lu à `fo = 0xA1A8`
   donne du code, à `fo = 0xA1A8 + 0x80000` sort du fichier. Il manque **le DPP en vigueur** au point
   d’accès ; `sub_CEC02` n’exécute aucun `scxt DPP`, donc il hérite de son appelant.

*Données : `defauts_96_listes.csv` (96 listes, 1 277 pointeurs) et `defauts_96_descripteurs.csv`.*


---

### B.15 — ★★ Mémoire de défauts : 7 enregistrements de 22 octets, 96 descripteurs, et le bloc EEPROM de 176 octets

#### 1. Géographie

| adresse | taille | rôle | preuve |
|---|---|---|---|
| **`0xE467` – `0xE500`** | **`0x9A` = 154 o = 7 × 22** | enregistrements de défauts | `mov r2, #9Ah` l. 229619 ; `mov r1, #16h ; mulu` l. 229640-229644 |
| `byte_E466` | 1 o | **nombre d’enregistrements courants** (0…7) | l. 229606, 229661, 229896 |
| `byte_E501` | 1 o | **pointeur d’insertion / index du dernier** | l. 229585, 229918, 229938 |
| `byte_E502`, `0xE503 + i` | 1 o | octets annexes du service diag | l. 231679, 231711, 231717 |
| `0xCAD0 + 4·code` | 96 × 4 o | état par code | § B.14 |
| **`0xCCB2 + 2·code`** | **96 × 2 o** | **pointeurs vers les descripteurs** | `mov r1, #0CCB2h` + boucle de `0xC0` = 192 o, l. 231163-231172 |
| `0xCE00` | 96 o | instantané de `0xFD21` | l. 230346 |

#### 2. Champs de l’enregistrement de 22 octets

| offset | rôle | preuve |
|---|---|---|
| `+0` | **code du défaut** | `movb rh2, [r3]` l. 229620 ; `cmpb rl2, rl6` l. 229668 |
| `+1` | **octet d’état** (bit 0 = actif, bit 6, bit 2) | `jnb r0.0` l. 229940 ; `jb r0.6` l. 231296 |
| `+2` | **compteur de conditions** (nombre de bits à 1) | boucle `jnb r0.0 / add r4,#1 / shr r0,#1` l. 229947-229958 |
| `+3` | doit être **non nul** (validité) | l. 229695, 229699 |
| `+4` | **compteur de guérison**, comparé à `[descr+#1Dh]` | l. 231251-231257 |
| `+5` | comparé à `[descr+#1Eh]` (0 → 1) | l. 231258-231266 |
| `+6` | comparé à `[descr+#1Ch]` **et** à `word_142A+9` (bloc Datensatz) | l. 231273-231282 |
| `+7` | seuil `1` / `>1`, aiguillé par le bit 3 | l. 231285-231292 |
| `+8` … `+21` | non exploités à ce stade (14 o) | — |

★ **Les seuils de maintien d’un défaut sont donc dans le Datensatz** : `[0xCCB2 + 2·code]` pointe un bloc
dont les champs `+0x1C`, `+0x1D`, `+0x1E` sont comparés aux octets de l’enregistrement.

#### 3. `sub_CE256` : le service de la mémoire de défauts (commande dans `rh6`)

| commande | effet | preuve |
|---|---|---|
| `0xFF` | rend le **dernier** enregistrement (`byte_E501`) + son pointeur de descripteur | l. 229583-229599 |
| `0x80`–`0x9F` (masque `0xE0` = `0x80`) | **dump complet : `0x9A` = 154 octets** depuis `0xE467` | l. 229603-229621 |
| `0xCF` | **compte** les défauts (bits de `+2` quand `+1`.0, `+4`=0, `+6`≠0) | l. 229624-229650 |
| `0x00`–`0x1F` | **lit l’enregistrement n° `rl6`** (offset `22 × rl6`) + descripteur `0xCCB2+2·code` | l. 229631-229652 |
| `0x20`–`0x7F`, `0xA0`+, `0xE0`+ | **recherche par code** (`0xEF`/`0xDF` = variantes), bits `r6.12…15` | l. 229663-229740 |

#### 4. ★ Deux tables de 96 entrées, une par code de défaut, dans la page `0x33`

| EA | taille | contenu relevé | rôle |
|---|---|---|---|
| **`0xCF5EC`** | 96 × 2 o | `1CF4 1492 1C64 1E0A 15B4 15B6 153E 183E …` — **toutes les valeurs tombent dans la plage des handles `0x1400`–`0x1E30`** | **un bloc de descripteur par code** ; recopié au démarrage à `0xCCB2` (`mov r0, #0B5ECh` + `extp #33h`, `add r2, #0C0h`, l. 231163-231172) |
| **`0xCF6AC`** | 96 × 1 o | `0D 80 FC 00 CC CC F8 7F 00 FC C8 78 1F F8 FC F8 F8 C4 FE …` | **masque par code**, OR-é dans `0xCAD0 + 4·code` à l’init (boucle `r12 = 0xB6AC`, `r13 = 0xCAD1`, `r14 = 0x60`, l. 231221-231232) |

#### 5. ★ Le bloc EEPROM de la mémoire de défauts — **offset `0x2467`, 176 octets**

```asm
loc_CF030:
  r1 = word_C45A ; r0 = word_C46A ; extp r0, #1 ; rl0 = [r1]
  r0 = 22 × rl0 ; MDH = 0xE467 + r0        ; ★ enregistrement pointé par l’EEPROM
  ...
  r0 = word_C46A ; shr r0, #2 ; jmpr cc_NZ, loc_CF072
  mov r0, #0E467h ; mov r2, #0B0h ; calls unk_2A9A   ; ★ EEPROM vierge -> 176 o remis à zéro
loc_CF072:
  mov r1, #2467h      ; ★ offset EEPROM
  mov r0, #0B0h       ; ★ 176 octets = 8 × 22
  mov r2, #3
  mov r3, r1
  calls 9, sub_9FFE2  ; ★ lecture/écriture EEPROM
```

**176 = 8 × 22** : l’image EEPROM réserve **8 enregistrements**, la RAM n’en gère que **7** en marche.


---

### B.14 — ★★ `0xFD21` décodé : 96 octets d’ÉTAT DE DÉFAUT par code, et le mécanisme complet de substitution

**ERRATA étape 67** : j’avais écrit « table de mots `EA 0xE4E4E` » et « `add r3, r12` avec `r12` = index ».
Les deux sont faux : la table est en **RAM `0x0E4E`** (18 couples d’octets) et `sub_CE57E` exécute
`add r12, r12` **avant** : l’index est doublé. Voici la chaîne complète.

#### 1. `0xFD21` = 96 octets d’état, un par code de défaut `0x00`–`0x5F`

| évidence | ligne |
|---|---|
| remise à zéro de 96 octets : `mov r0, #0FD21h` … `mov r2, #5Fh` | 229851-229852 |
| **écrivain unique : `sub_CE9B4`** — `movb rl4, [r4+#0FD21h]`, `andb rl4, rl2`, `orb rl4, rh6`, réécriture | 230438, 230466, 230476 |
| `sub_CE43C` reconstruit les états depuis les enregistrements **RAM `0xE467`** (pas `0x16` = 22 o, `byte_E466` = nombre, fin `0xE501`) et remet `0xFD21 + code` à zéro ; ces enregistrements sont chargés de l’**EEPROM** (bloc de 176 o à l’offset `0x2467`) — voir § B.15 | 229816-229964 |
| copie de travail : `0x0CE00` ← `0xFD21`, 96 octets (`unk_2A9A` = copie avant, débordement exploitée comme `memset`) | 230346-230350 |
| lecture de l’état d’un code dans le service « lire un bloc » : `mov r9, #0FD21h ; add r9, r13` avec `r13 = 16·(code−0x90)`, 7 codes | 206936-206942 |

#### 2. `sub_CE9B4` = le **poseur d’état de défaut** (686 appels)

```asm
movb rl4, [r4+#0FD21h]   ; état courant du code rh2
andb rl4, rl2            ; & masque demandé
orb  rl4, rh6            ; | (~masque)  -> pose ou lève
movb [r5+#1], rh0        ; enregistrement 0xCAD0 + 4·code
```

Deux mémoires mises à jour en parallèle : **`0xFD21 + code`** (bits d’état courants, 1 octet) et
**`0xCAD0 + 4·code`** (enregistrement de 4 octets, `[0]` = état, `[1]` = bits cumulés).

#### 3. `sub_CE57E` décodé en entier — c’est le pont défaut → valeur de mesure

```asm
cmp  r12, #11h            ; i = 0…17   (18 mesures surveillées)
jmpr cc_UGT, locret_CE5DE
add  r12, r12             ; ★ i -> 2i
mov  r3, #0E4Eh            ; ★ RAM 0x0E4E : 18 couples de codes
add  r3, r12
movb rl2, [r3+]           ; c1 = 1er code de défaut de la mesure i
movb rh2, [r3]            ; c2 = 2e code (0xFF = aucun)
cmpb rl2, #60h            ; borne : code < 96
jmpr cc_NC, locret_CE5DE
movb rl3, [r3+#0FD21h]    ; ★ état du code c1
andb rl3, #1              ; bit 0 -> word_1422 (0x0000)
andb rl3, #2              ; bit 1 -> word_1420 (0xFFFF)
```

**Résultat** : la mesure `i` est remplacée par **`0x0000`** si le bit 0 de l’état d’un de ses deux
codes est posé, par **`0xFFFF`** si c’est le bit 1. Les deux tables de 18 mots du Datensatz
(`0xE11A0` = 18 × `0x0000`, `0xE117C` = 18 × `0xFFFF`) sont donc des **valeurs de substitution** —
des drapeaux « mesure disponible / invalide », **pas des lois de calibration**.

#### 4. Le consommateur : réponse diagnostique `0x42`

`sub_BE10C` → `sub_942F2` (l.201240) → `sub_CE57E` ; en-tête `0x42` = réponse du service
`readDataByCommonIdentifier`. Dans `sub_BE2BA` (l.201482-201530) :

```asm
mov  r4, [r8]             ; word_1424[i]
movbz r5, rl6             ; identifiant demandé
cmp  r4, r5
movb rl5, [r4+#0DC2Ch]    ; octet de la table RAM 0xDC2C (8 entrées)
cmp  r4, #0FEh            ; -> pointeur word_1422 + 2·code  (= 0x0000)
cmp  r4, #0FFh            ; -> pointeur word_1420 + 2·code  (= 0xFFFF)
```

#### 5. Ce qui reste ouvert sur `word_1424` (`0xE11C4`, 20 mots)

Valeurs : `0F10 0F61 0F80 0FFA 0F8B 0F30 0F32 0F60 0FFC 0F40 0F42 1F5A 1F51 0F64 0F7F 0005 000F 0F65 0F08 0F8A`.

Elles sont parcourues par `[r7+]` / `[r8+]` (l.201513, l.231375) et **une seule** passe le test
`cmp r2, #11h` d’un des deux consommateurs (`0x0005`, `0x000F`). Deux lectures possibles, non tranchées :
soit des **pointeurs vers la RAM basse `0x0Fxx`/`0x1Fxx`**, soit **deux codages mêlés**. À instruire.


*Données : `zone_0xE1129_v2.csv` (74 EAs lues, avec site, segment, nature).*

*Données : `zone_0xE1129.csv`.*

**Données complètes : `bloc_options_0xE111E.csv`** (35 octets : valeur, site, miroir, nombre de références).

*Données complètes : `switchs_calibration.csv` (282 sites bruts), `switchs_contenu.csv` (122 sites classés avec contenu des blocs), `boucles_regulation.csv` (35 boucles).*

---

## B.48 — Étape 101 : carte d'effacement, blocs A/B et les deux octets de télécodage

**1. Carte d'effacement du dump** (comptage `0xC3` par tranches de 8 Ko).

| fo | EA | % `C3` | verdict |
|---|---|---|---|
| `0x00000-0x07FFF` | `0x80000-0x87FFF` | **100 %** | **BIBLIOTHÈQUE EFFACÉE (32 Ko)** |
| `0x12000-0x13FFF` | `0x92000-0x93FFF` | 99,9 % | effacé (8 Ko) |
| `0x54000-0x5FFFF` | `0xD4000-0xDFFFF` | 37→100 % | 40 Ko effacés |
| `0x6C000-0x6FFFF` | `0xEC000-0xEFFFF` | 100 % | queue du bloc A effacée |
| `0x7C000-0x7FFFF` | `0xFC000-0xFFFFF` | 22,8 % | queue du bloc B présente (16 Ko) |

⇒ Les 32 Ko qui contiennent la **bibliothèque** (`0x1D36`, `0x1FE8`, `0x20AC`, `0x24BA`, `0x2EE2`,
toutes < `0x3000`) sont **effacés**. Le corps des `unk_*` **n'existe pas** dans ce fichier :
c'est une **limite du dump**, pas une piste. Un dump complet est indispensable.

**2. Blocs A (`0xE0000`) et B (`0xF0000`) = même Datensatz.** 14 147 octets différents en 12 plages ;
`0xE0000-0xEBFFF` identique sauf 4 plages : `0xE0FF6` (empreinte/checksum), `0xE434D` (`23`/`03`),
`0xEBCF2` (**checksum 32 bits**), `0xEBF1B`. ⇒ Toute modification est à faire dans **les deux blocs**,
avec **deux checksums** à recalculer. Pas de variante BVA/BVM dans le flash.

**3. `byte_C2C0` : BVM ⇒ Gangberechnung ACTIVE.** `sub_BD464` décode `[codage+2]` : `1`/`2` ⇒
`C2C0 = 1` ; `8h`/`10h` ⇒ `C2C0 = 2`/`4` (+ `C2B7|=1`, `C22C|=1`). Ici **`[0xE111E+2] = 0x01`** ⇒
**`C2C0 = 1`**. Or `loc_AFB34` ne lance la Gangberechnung (ratio `V×256/N`) que si `C2C0 == 1`.
⇒ Le ratio est calculé, le rapport classé (`0xE81A4`), la **limitation 1re/2nde active**
(`0xE8906`/`0xE8946`). La description Bosch était juste ; les étapes 96/97 étaient fausses.

**4. `byte_C2BD` : FGR INHIBÉ par télécodage.** `loc_BD7D6` (l.199997) :
`mov r4, word_141C ; movb rl5, [r4+#3] ; movb byte_C2BD, rl5`. Ici **`[0xE111E+3] = 0x00`** ⇒
`C2BD = 0` ⇒ tâche `0x340` branche `loc_B3CEC` ⇒ `D9B2 = 2`, `D9B3 = 0x8E`.
⇒ Le refus ne vient **ni** de la vitesse mini, **ni** du régime, **ni** du rapport : le régulateur
est **coupé au codage**, et toutes les valeurs FGR (`2500`, `25000`, `1000`, `4500`, `20000`) sont
de la **calibration morte** — d'où l'absence de `40`/`60` km/h et de `FGR_GangMin`.

**Activation** : `0xE111E+3` : `0x00` → `0x01` (ou `0x80`) + recalcul des 2 checksums. Cohérence :
`[0xE111E+0x0E] = 0x08` = `byte_C2B7` (bit 0 = 0 = pas de trame boîte) ⇒ OK avec `C2C0 = 1`.
Réserve : `sub_BD464` a aussi un chemin décodé (`[r0+#7]`, `1` ⇒ `C2BD = 1`) ; vérifier
`byte_C2BD` à la valise avant de flasher.

---

## B.49 — Étape 102 : le bloc FGR lu par le code (seuils, variables, codes de refus)

**Test de la recette hexadécimale** : `A8 61` (25000) n'existe que **3 fois** — `0x94368` (code),
`0xE278A` (bloc A), `0xF278A` (bloc B). La co-occurrence `vMin+vMax+nMin` donne 24 sites = 3 zones
(`0xE4CF0`, `0xE6AB0`, `0xE9370`), **toutes des courbes/grilles**, aucun bloc de scalaires.

**`15 27 40 58 105` = `0xE4D4A`**, dans la courbe **`0xE4D38`** (`word_18A4`) :
`[tag 0xD1B6][n=8][axe 500…11000][15 27 40 58 105 130 185 260]`. Son tag est **actif** :
l.155184-155192 `word_D1B6 → unk_1D36(word_18A4) → word_C594 → word_D1C0 = C596 − C594`
⇒ chaîne de **limitation de couple**. L'échelle 15..105 sert au couple, pas au FGR.

**Table définitive (tâche `0x340`, l.184672-184880)** — `C562` vitesse, `C91C` régime, `C93E` ratio :

| off | EA | valeur | rôle | refus |
|---|---|---|---|---|
| +0 | `0xE2788` | 2500 | **`FGR_vMin`** 25 km/h | `0x86` |
| +2 | `0xE278A` | 25000 | **`FGR_vMax`** 250 km/h | `0x86` |
| +6 | `0xE278E` | 4500 | **`FGR_nMax`** | `0x87` |
| +4 | `0xE278C` | 1000 | **`FGR_nMin`** | `0x88` |
| +A | `0xE2792` | **768** | **`FGR_GangMin` = 3×256** | `0x89` |
| +8 | `0xE2790` | 2560 | `FGR_GangMax` = 10×256 | `0x8A` |
| +C | `0xE2794` | 4000 | **temporisation** (`C112−F91C`) | `0x8B` |
| +14 | `0xE279C` | 4000 | consigne = **40 %** (`D9CE×4000/10000`) | `0x8D` |
| +16/+1A | `0xE279E`/`0xE27A2` | +71 / **−71** | **commodo ±0,71 km/h** vs `C552` | — |
| +10/+12 | `0xE2798`/`0xE279A` | 5000/3000 | rampes consigne ± | `0x8C`/`0x8D` |

⇒ **Vitesse = `0xE2788`/`0xE278A` ; rapport = `0xE2790`/`0xE2792` ; régime = `0xE278C`/`0xE278E`.**
`FGR_GangMin` **existe** mais en échelle **×256** (768 = 3) : d'où l'échec de la recherche d'un mot
`0x0004`. Les `1200/1300` de la recette sont des grilles de cartes. Les seuils 25/250 km/h et
1000/4500 tr/min sont **confirmés par le code** (E11/E12 corrigent l'Étape 100).

---

## B.50 — Étape 103 : bloc consigne `word_14AA` (0xE2762), verrou 40 km/h, pas ±2 km/h

**Bloc `word_14AA → 0xE2762`** : `40 · 0 · 200 · 500 · 20000 · 4000 · 400 · 0 · 100 · 300`
| off | EA | val | rôle | preuve |
|---|---|---|---|---|
| +0 | `0xE2762` | 40 | temporisation bouton | l.185096 |
| **+4** | **`0xE2766`** | **200** | **pas = ±2,00 km/h** | l.185135 (`C562+200`) / l.185275 (`C562−200`) |
| +6 | `0xE2768` | 500 | tolérance 5 km/h (re-synchro) | l.185128 |
| +8 | `0xE276A` | 20000 | **plafond consigne 200 km/h** | l.185157 |
| **+A** | **`0xE276C`** | **4000** | **★★★ plancher consigne 40 km/h** | l.185291, **185301**, 185806, 185856 |
| +C | `0xE276E` | 400 | incrément appui long 4 km/h | l.185028 |
| +E | `0xE2770` | 0 | masque d'options (inactif) | 10 sites |

⇒ **Le verrou des 40 km/h est `0xE276C = 4000`** : clamp de `D9CE` **et** refus d'engagement si
`C562 < 4000` (`D9CC = 0x60`). `FGR_vMin = 2500` (25 km/h) est moins contraignant ⇒ 40 km/h gagne.

**16 bits d'inhibition** (l.184447-184660) : `movb rl4, <flag FD>; and [0xE275C], #bit` ⇒ `D9B2=2`,
`D9B3=0x8E`. Flags : `FD20+1`(#1) `FD23`(#2) `FD28+1`(#10) `FD2A+1`(#20) `FD3E+1`(#80) `FD57`(#400)
`FD3A+1`(#4000). Masque **`0xE275C = 0xBFFE`** ⇒ seuls bits 0 et 14 désarmés.

**Bloc `word_14B2 → 0xE27B6`** (rampes) : `500·400·masque 0xFFFE·45·3·100·108·3…` ;
`D9BC = 500×C562/10000 + 400`, `D9C0 = D9BC/50`, `D9BE = (D9BC/50)×1310` ; `+8 = 3` = pas de 6
dans `sub_B3572`.
**Bloc `word_14AC → 0xE2774`** : `300 · 1024 · 512 · 768 …` ⇒ **4 / 2 / 3 en Q8.8** mais **aucun
renvoi code** : seuils de réserve. Le seuil actif reste `0xE2792 = 768` (= 3).

**Modifications** : `0xE276C` 4000→2500 (25 km/h) · `0xE2766` 200→100 (±1 km/h) · `0xE2792`
768→512 (2e) · `0xE111E+3` 0x00→0x01 (activation). Chacune en **double** (`0xE`/`0xF`) + checksums.
Errata **E13** (`±71` = bande morte, pas le pas) et **E14** (`0xE276C` = plancher de consigne).

---

## B.51 — Étape 104 : chaîne `D1B6 → C594 → D1C0` = limitation par rapport **neutralisée**

**Preuve** : toute la zone `word_D1B0`…`word_D1C4` (l.52392-52402) n'a que des XREF `↓w` —
**aucun lecteur**, et **0 immédiat** `0D1B0h…0D1C0h` dans le fichier. ⇒ le calcul par rapport est
une **trace de contrôle**, pas un limiteur : **limitation de couple par rapport neutralisée
d'origine** (ML5T / DW12TED4).

**Chaîne** (tâche quantité, entrée ≈ `seg014:32A4`) :
`D1B6 = (C586 × 28 / ([18B2+10h]+C596)) × D6D4 / 100` — indice de charge sur l'échelle 500…11000
(la même que les `Gangstufen`) ; `C596 = word_1878[+4] = 0xE4C0A = 120` (plafond de débit).
**Deux courbes jumelles, même tag `0xD1B6`, même axe** : `18A2 → 0xE4D14` = `117 266 367 447 542 585
643 655` et `18A4 → 0xE4D38` = `15 27 40 58 105 130 185 260`.
`D1C0 = C596 − 18A4(D1B6)×18A0(C5BC)/1000` · `D1BC = C596 − 18A2(D1B6)×189E(C5BC)/1000` ·
**`D1B4 = D1C0 − coeff_189C × ([1Eh]−[1Ch])/10000`** ⇒ **soustractions pondérées, PAS un MIN**.
Le `MIN` existe mais sur les candidates classiques (`word_18A8/18AC/18AA`, struct `word_18B2 →
0xE4E2C` = `2000 1500 −2000 −2500 5000 4500 13000 1100`, drapeau `byte_C308`).

**Codage** : `word_141C → 0xE111E` (`+2=01` ⇒ `C2C0=1` BVM ; **`+3=00` ⇒ `C2BD=0` FGR off** ;
`+0E=08`) · `word_141E → 0xE1148` (`+3=08` voie directe ; **`+5=01` ⇒ `byte_C2BC=1`**, l.200025).

**Bilan rapport** : ratio `C576/C93E` actif · classement `byte_C330` actif · autorisation FGR
`0xE2792=768` actif · **limitation couple par rapport INERTE**. Errata **E15**.

---

## B.52 — Étape 105 : Vmax, checksums, queue `0xFC000` (SW en ASCII)

**Vmax — éliminé** : aucune carte 2-D à axe km/h (0/72) ; aucun immédiat `#61A8h`/`#4E20h` en
comparaison (le `A8 61` de EA `0x94368` est dans une table de sauts `14 00 CC 00`) ; les 33
comparaisons `word_C562` hors FGR portent sur des seuils courts.
**Deux blocs nouveaux** : `word_142C → 0xE1236` et `word_1432 → 0xE1264`, lus par le limiteur
`seg015:045C-0x053E`. Seuils `200` (2 km/h), `275` (2,75), `500` (5), `750/870/920` ⇒ logique
**arrêt/rampage**, produisant les **niveaux de limitation `0x10`/`0x20`/`0x30`** sélectionnés par
**`byte_C330 & 70h`** (bits de rapport) et conditionnés par `byte_C2C0 == 1` → sortie
`unk_20F6(word_1AA2, C908, D8CE)`. ★ C'est **là** que vit la limitation dépendante du rapport.
**Candidates Vmax restantes** : courbes à axe octet 0-255 — `0xE7EA6`/`0xE7EBE` (tag `0xD369`),
`0xE7EE2` (`0xD366`), `0xE7F06`/`0xE7F12` (`0xD36A`).

**Checksums** : les seules différences A/B sont `0xE0FF6-9`, `0xE0FFC-F`, `0xE434D`, **`0xEBCFC-FF`**,
`0xEBF1B` + queues. Somme16 LE/BE, somme8, CRC32, Adler testés sur les 3 zones ⇒ **aucune
correspondance** ⇒ algorithme propriétaire (bibliothèque effacée ou bootloader). Ne pas recalculer
à la main. **Errata E16** (`0xEBCFC`, pas `0xEBCF2`).

**Queue `0xFC000`** : `0xEFEF4 = "1037353776"` en **ASCII** ⇒ **bloc B = calibration réelle** (A
effacé). `0xEFF00 = AA 55 … 42 4F 4F 54` = signature + **"BOOT"** + table de pointeurs.
`A5 A5` à `0xFC000`, `0xEC2FB`, `0xEC5FA` = **marqueurs de descripteur** suivis de quads de pointeurs
(`0xE014`, `0xE02E`, `0xE040`, `0xE300`…). **Errata E17** (`A5A5` ≠ remplissage).

---

## B.53 — Étape 106 : tags `D366/D369/D36A` (états normalisés) et superviseur 239/240

**Tags** : `byte_D366`, `byte_D369`, `byte_D36A` = **octets 0…255 en écriture seule** (l.175829,
175864, 176093). `D36A = clamp(unk_1D36(word_1A70, C908), 0, 255)` ; `D369 = D8A2` puis
`C61C = D8A2 × 10000/256` (‰). ⇒ les courbes à axe 0…255 (`0xE7EA6`, `0xE7EBE`, `0xE7EE2`,
`0xE7F06`, `0xE7F12`) sont indexées par un **état normalisé**, **pas** par des km/h → **piste Vmax
éliminée** (errata E18).

**★★ Superviseur `seg014:D232` → `byte_C325`** : bloc `word_19EA → 0xE6E2E` =
`32767 · 200 · 32767 · 23900 · 24000 · 1 · 1 · 460 · 10 · 69 · 565`.
Index `[r0] += C91C × [0xE6E32]/10000` (`0x7FFF` = saturation/bypass) ; **bascule d'hystérésis**
entre `word_19EC → 0xE6E38` et `word_19EE → 0xE6E3A` via `unk_1E50` → `0xD84E`/`0xD850` ;
comparaison **`0xE6E34 = 23900`** (armé) / **`0xE6E36 = 24000`** (coupure) → drapeau
**`word_FD12.10`** → **`byte_C325`** (voisin de `byte_C330` = rapport).
Conditions : `word_C6D8 ≠ 0`, `byte_C2DE = 0`, `word_C64A & 0F0h == 70h`.
⇒ **meilleur candidat Vmax** (239/240 km/h, hystérésis 1 km/h). Patch type ECUSafe : `0xE6E34` →
32000 et `0xE6E36` → 32000 (ou `0x7FFF`), en double (`0xF6E34`/`0xF6E36`) + checksum par l'outil.
Validation en roulant : lire `byte_C325`. Errata **E19**.

---

## B.54 — Étape 107 : navigation `A5A5` — appendix, répertoire `BOOT`, record d'identification

**Trois records `A5 A5`, pas quatre** (le 4e à `0xFFF58` est un faux positif) : `0xFC000`, `0xFC300`,
`0xFC600` — **pas de 0x300 = 768 o**. Structure :
`A5 A5 | u32 p1..p4 | u16 id | u16 n | n×u16 | …code C166 dès +0x40…`
- R1 `0xFC000` : `0xC014 0xC000 0xC040 0xC300` id `0xE601`, payload effacé
- R2 `0xFC300` : `0xE014 0xE02E 0xE040 0xE300` id `0x4702`, **n = 12** → `8 9 10 11 12 13 14 15
  0x0F80 0x0FA0 0x0FC0 0x1000`
- R3 `0xFC600` : `0xE314 0xE31C 0xE320 0xE600` id `0xD380`, puis `8 0 16`
Poignées constants `…014 / …02E / …040 / …300` ⇒ records **indexés par page mémoire** (`0xC0`, `0xE0`,
`0xE3`). Prologue `88 90 88 80 88 70 88 60`, épilogue `DB 00` ⇒ **blocs code+données**.

**Répertoire `BOOT` à `0xFFF00`** : `AA 55 75 14 89 11 30 AA` + `"BOOT"` + 8 pointeurs LE
`0xFC000 · 0xFFFFE · 0xFCC14 · 0xDFF00 · 0xFBF00 · 0xFCC5A · 0xFCC2A · 0xFFF00` (boucle sur lui-même).

**★★ Record d'identification** : **`0xFCC00 = "0281010877"`** (n° **HW**), **`0xFFEF0 = "1037353776"`**
(n° **SW**), libellés `"75vG"` / `"B075WF2S01"`, et **paires de pointeurs**
`(0x600A9241, 0x000FCC00)` / `(0x600A9441, 0x000FFEF0)` à `0xFCC30`/`0xFCC38` qui **lient** la table
d'identification aux deux chaînes. ⇒ ce fichier est la calibration **2.0 HDi (HW 0281010877)** ;
le n° SW est **référencé par pointeur**, pas isolé ; la queue est **effacée dans le bloc A** ⇒ seul B
porte l'identité.
**Conclusion** : `A5A5` = navigation de l'**appendix** (identité + extensions), **pas** du Datensatz
de calibration — celui-ci reste la table de handles `0x61400` (1 305 entrées). Errata **E20/E21**.

---

## B.55 — Étape 108 : cartes driver's wish, sélection par le rapport, entrée de la boucle IQ

**Cartes** (`tagY = 0xC42E` régime × `tagX = 0xC6DA` pédale, 8×6, valeurs 0…8000) :
- `word_1B66 → 0xE8B50` : `1060 3372 5660 7260 8000 8000 / 460 2608 … / 320 2400 4688 … / 140 2132
  4444 … / 0 1844 4104 … / 0 1520 3616 … / 0 1260 3208 … / 0 680 1846 3656 5740 8000`
- `word_1B68 → 0xE8BD4` : **identique sauf la colonne pédale = 2000** aux régimes 750-2250
  (`2400→2350`, `2132→1782`, `1844→1344`, `1520→1070`, `1260→910`)
Axes : Y `0 600 750 1000 1300 1750 2250 5000` · X **`118** 2000 4000 6000 8000 10000` (errata E23).

**★★★ Sélection par le RAPPORT — `sub_B56F8`** : `C93E = C576 × 1` ; seuil `[word_1B6A] = [0xE8C58]
= 539` ; `539 ≤ ratio` → `0xE8B50`, sinon → `0xE8BD4`. La fenêtre `338-559` de `0xE81A4` étant la 3e,
**539 = frontière 2e/3e** ⇒ **1re/2de = carte basse**.
⇒ **C'EST la limitation 1re/2de, et elle est ACTIVE** (errata E22 : la chaîne `D1B6/D1C0` reste une
trace, mais la limitation passe par la carto souhait).

**Production** : `C6A6 = souhait(C91C = régime, C952 = pédale)` (l.195501-195504) ; `C6DA = C952`.
Échelle `8000 = 80 mm³`, contre `C596 = 120` max.
**Suite IQ** : `D2F4 = C6A6 − D834` (ΔIQ cycle) ; bloc `word_19C6 → 0xE6C06` = `650 · 1500 · 0 · 0 ·
tag C42E · 8 · 1000` (seuil demande **1500**) ; et **arbitrage FGR** l.185007-185016 :
`cmp C6A6, C698` → si la pédale dépasse, `D9B6/D9B8` basculent, `byte_D9D0 |= 10h`, **`bset
word_FD18.4`** ⇒ « cartes inversées remplaçant la pédale, sauf dépassement » **confirmé par le code**.

---

## B.56 — Étape 109 : détermination du rapport, maillon par maillon

**1. Formula** : `sub_CF774` (l.232285-232325) : `C91C = C42E` (régime) ;
`MDL = C578 ; shl #8` ; **`divlu r0`** ⇒ **`ratio = (C578 × 256) / N`**, plafonné à `[word_1470+0Eh]`
(`word_1470 → 0xE225A`). `C578` = **vitesse en 0,01 km/h** (seule référence du fichier : cette
lecture → écriture par overlay non désassemblé).
**2. Filtrage** : `unk_24BA(handle 0x185C, valeur_brute, C576_ancien, C56A)` ⇒ **`C576 = C93E`** =
ratio filtré (les deux symboles désignent la même donnée).
**3. Classification** : `word_1A9A → 0xE81A4` = `[01 0B 02 03 04 05][00 00 00 C3][6 fenêtres]`,
mots `234 · 202 · 234 · 256 · 234 · 338 · 453 · 410 · 559 · 720 · 652 · 826 · 1015 · 910 · 1116`.
Chaque fenêtre = 4 bornes `[outer_lo][outer_hi][hyst_lo][hyst_hi]`, testées dans l'ordre ;
hors bande fine ⇒ `code | 0x40` (**hystérésis**).
**Fenêtres** : 1) `202-234` → code `01` (8,5 km/h à 1000 tr/min) · 2) `234-338` (fine 234-256) →
`0B` (11,2) · 3) `338-559` (fine 410-453) → `02` (17,5) · 4) `559-826` (fine 652-720) → `03` (27,0) ·
5) `826-1116` (fine 910-1015) → `04` (38,0) · 6) `≥1116` → `05`.
La cohérence `V = ratio/2,56` km/h à 1000 tr/min valide formule **et** échelle.
**Point ouvert** : le code `0B` en 2e position (la tâche FGR traite `0x0B` comme « rapport
indéterminé », refus `0x92`) ⇒ soit 2e volontairement indéterminée, soit la 1re est hors table
(traitée par `loc_B0000` avec les bornes de l'appelant `r4`, l.178055-178066) et les codes sont
`0B·02·03·04·05` = 2e à 6e. À trancher via le bloc passé en `r4` par `seg014:FB30`.
**4. Stockage** : `byte_C330` écrit **une seule fois** (l.178003) : bits 0-3 = rapport, **bit 6
`0x40`** = incertitude, bits 4-6 `0x70` exploités par le limiteur `seg015:045C`.
⇒ **aucun rapport n'est reçu par CAN : il est entièrement calculé à bord.**

---

## B.57 — Étape 110 : le rapport et le régulateur — le seuil réel « 3e/4e »

**★★★ Le verrou n'est pas un numéro de rapport** : il n'existe **aucun `cmp #3`/`#4`** dans la tâche
FGR. Le test est **`cmp [0xE2792] = 768, word_C93E`** (l.184704-184709) ⇒ si `ratio < 768` :
`byte_D9B3 = 0x89`, refus. Or `C93E` = ratio `V×256/N` de l'Étape 109 ⇒ **condition réelle :
`V/N ≥ 3,00 km/h pour 1000 tr/min`**, constante par rapport engagé.
**Les 6 portes du bloc `word_14B0 → 0xE2788`** (`2500 · 25000 · 1000 · 4500 · 2560 · 768 · 4000 ·
1000`) : `+00 2500` vs `C562` (V min 25,00 km/h, refus `0x86`) · `+02 25000` vs `C562`
(V max **250,00 km/h**, refus `0x86`) · `+06 1000` vs `C91C` (N min, `0x87`) · `+04 4500` vs `C91C`
(N max, `0x88`) · `+0A 768` vs `C93E` (`0x89`) · `+08 2560` vs écart filtré `D9E0` (`0x8A`).
**Second mécanisme** : `byte_C330 & 0x10` = bit d'autorisation générique, testé par `sub_A7C5A`
(l.163019) et `sub_A7D48` (l.163145), **bypassé si `byte_C2C0 == 1`** (codage sans info rapport).
Ce bit `0x10` est produit dans la tâche rapport quand `byte_D8CC == 2` (l.178513-178518), état d'une
machine à hystérésis comparant `[0xE1236+6] = 200 + C6C8` à `D8CA = courbe(0x1A98 → 0xE7FF4, N)`
⇒ « décollage / rapport établi », **pas** un numéro de vitesse.
**Troisième mécanisme** : codes de rapport `0x0B`/`0x0C` ⇒ `D9B3 = 0x92` **et `C698 = 0`** (coupure
du PID, l.184425-184437). Cela **explique** le code `0x0B` de la fenêtre `234-338` (2e) de
`0xE81A4` : la 2e est marquée indéterminée ⇒ **régulation impossible en 2e** même en baissant 768.
**Conséquence** : `768` tombe dans la bande de 4e (`559-826`) ⇒ **4e/5e autorisées, 3e refusée**.
Pour autoriser la 3e : passer **`0xE2792`** `00 03` → `40 01` (320) puis **recalculer les checksums**.

---

## B.58 — Étape 111 : autoriser la 2nde et 20 km/h (patch)

**★ ERRATA E24** : la numérotation des fenêtres de `0xE81A4` de l'Étape 109 était fausse. La 2e
fenêtre `234-338` n'est pas un rapport mais une **bande de transition** (sa bande certaine
`234-256` est collée au bord bas, les autres sont centrées). Lecture corrigée : **1re** `202-234`
(code `01`) · **transition** `234-338` (`0B`, certaine `234-256`) · **2nde** `338-559` (`02`,
certaine `410-453`) · **3e** `559-826` (`03`, certaine `652-720`) · **4e** `826-1116` (`04`,
certaine `910-1015`) · **5e** `≥1116` (`05`). Conséquences : (a) `768` tombe bien dans la bande de
**3e** ⇒ règle « 3e minimum » ; (b) **la 2nde renvoie `0x02`, non refusé** (liste des codes
indéterminés : `6·0·9·0B·0C·0D`) ⇒ **aucune modification de la table des fenêtres n'est nécessaire**
(l'avertissement de B.57 §5 est retiré) ; (c) le seuil `539` de `sub_B56F8` tombe dans la bande de
2nde ⇒ la carte basse couvre 1re + transition + presque toute la 2nde, ce qui **confirme** la
limitation de couple 1re/2de.
**★ Deux verrous seulement** (l.184672-184707) : `[0xE2788] = 2500` vs `C562` (V ≥ 25,00 km/h,
refus `0x86`) et `[0xE2792] = 768` vs `C93E` (ratio, refus `0x89`).
**Patch retenu** : `0xE2788` `2500 → 2000` (20,00 km/h) et `0xE2792` `768 → 380` (sous la bande
certaine de 2nde 410-453, au-dessus du haut de la bande de transition 338). Cohérence : à 20 km/h en
2nde, N = 2000·256/430 ≈ **1190 tr/min** > minimum 1000.
**★ Bloc dupliqué confirmé** : motif de 16 octets présent à `fo 0x62788` (EA `0xE2788`) **et**
`fo 0x72788` (EA `0xF2788`) ⇒ **les deux copies patchées**.
**Livrable** : `outils/patch_2nde_20kmh.py` → **`edc_2nde_20kmh.bin`**, 8 octets modifiés
(`[C4 09]→[D0 07]`, `[00 03]→[7C 01]` × 2). **Checksums propriétaires à recalculer**
(`0xE0FF6-9`, `0xE0FFC-F`, `0xE434D`, `0xEBCFC-FF`, `0xEBF1B`) ⇒ non flashable en l'état.
**À vérifier par log** : bit `0x10` de `C330` (`D8CC == 2`) établi à 20 km/h en 2nde ; sinon les
deux patchs ne suffisent pas. Seuil de dérive `+0x08 = 2560` à surveiller (`0x8A`).
Le plancher `0xE276C = 4000` (40 km/h) est un **maintien de consigne** (`D9CC = 0x50`), pas une
porte d'engagement ⇒ ne pas y toucher.

---

## B.59 — Étape 112 : checksums — anatomie complète, algorithme non cassé

**★★★ Structure réelle** : chaque bloc se termine par **6 octets `[94 C7][u32]`** — **14 occurrences**
(EA `0x8FFFA`, `0x93FFA`, `0xAC2CC`, `0xAC404`, `0xD2998`, `0xDFFFA`, **`0xE0FFA`** = `0xB20532C9`,
**`0xEBCFA`** = `0x5BD935DD`, **`0xF0FFA`** = `0xC0CDD4CD`, **`0xFBCFA`** = `0xAF775C20`, `0xFC2FA`
= `0xD97B6BB1`, `0xFC5FA` = `0x276E5435`, `0xFC8FA` = `0xCC8254A1`, `0xFEBFA` = `0xF0262558`).
Notre patch est protégé par **`0xEBCFC-FF`** (banque A) et **`0xFBCFC-FF`** (banque B).
**★ ERRATA E25 — trois fausses pistes de l'Étape 105 levées** : (a) `0xE0FF6-9` = `3D D3 3D D3` =
**signature `0xD33D` ×2 comparée à une CONSTANTE** dans le code (`sub_BCEBE` l.198817-198827 avec
`extp` page `0x37` → `0xDFFF6/0xDFFF8` ; `loc_90686` l.111788-111792 `subc r0, #0D33Dh`) ⇒ **pas un
checksum, indépendant des données** ; (b) `0xE434D` = **l'unique octet qui diffère entre les deux
banques** (`0x23`/`0x03`) — les blocs `0xE1000-0xEBCF9` et `0xF1000-0xFBCF9` (44 282 o) ne diffèrent
que là ⇒ **octet de variante de codage** ; (c) `0xEBF1B` = **ASCII** (`WGDWPF1`, `075WF2S010384`) =
identifiant logiciel. ⇒ **aucun des trois n'a besoin d'être recalculé.**
**★ Contrainte structurale** : un seul octet modifié dans le bloc fait changer **les deux mots** du
u32 (`0x35DD·0x5BD9` → `0x5C20·0x77AF`) ⇒ **un seul checksum 32 bits sur la zone entière**, pas deux
sous-checksums.
**★★ Différentiel exploité** : banques identiques à 1 octet près ⇒ variation XOR = **`0xF4AE69FD`**,
arithmétique = `0x539E2643`. Un delta aussi grand **exclut toute somme additive ou pondérée**.
**Balayages négatifs** : 48 variantes CRC-16/32 (polys `1021`, `8005`, `3D65`, `8BB7`, `04C11DB7`,
`1EDC6F41` × refin/refout × init × xorout) ; sommes 8/16/32 bits (LE, BE, swappées, repliées,
complémentées, XOR) ; sommes pondérées `Σi·octet` ; 9 combinaisons de bornes de zone (début
`0xE0000`/`0xE1000`/`0xE0E72`, fin `0xEBC47`/`0xEBCF6`/`0xEBCFA`) ; différentiel CRC-32 réfléchi et
non réfléchi, distances 0→48 000 ⇒ **0 match**. **Algorithme propriétaire Bosch**, absent de
`clean.asm` (aucune référence à `0xE0FFC`, `0xEBCFC`, `0xC794`).
**★ Point troublant** : la signature est cherchée à `0xDFFF6/0xDFFF8` mais se trouve à
`0xE0FF6/0xE0FF8` — soit **exactement +0x1000** ⇒ l'adresse runtime de la calibration diffère
peut-être de `0x1000` de l'adresse fichier (à trancher).
**★ Protocole de test sûr** : modifier **un seul octet de remplissage `C3`** (par ex. `0xE0E80`) et
flasher ⇒ si DTC/refus, les trailers sont vérifiés à l'exécution ; si rien, ils ne servent qu'à
l'outil de programmation et **le patch passe tel quel**. Voies alternatives : correcteur de checksum
EDC15C2 existant · retrouver/neutraliser le vérificateur (voie « unpatchable fixable »).
**État** : `edc_2nde_20kmh.bin` **en attente** (données patchées, checksums non recalculés).

---

## B.60 — Étape 113 : la cascade de limitation après le souhait

**Consommateurs de `C6A6` — inventaire définitif (7 sites)** : `195504` production · `171719/171723`
ΔIQ `D2F4 = C6A6 − D834` · `171734`/`171813` comparaisons · `182735`/`182752` entrée de cascade
`D9A6` · `185007` arbitrage FGR (`FD18.4`).
**★★★ Cascade (seg015 l.182725-182880)** : `D9A6 = C6A6` (ou `C6A6 + C69E` si `byte_D9AC == 1`) →
`C6B8 = D9A6` (**sauvegarde du souhait brut**) → **plancher `C680`** → plafond `C67E` → plafond
`C696` → `C6A4 = D9A6` → `D9AA = max(0, C6A4 − C69E)` → `byte_C8F8 = courbe(word_1B5E, C91C, D9AA)`
→ **plancher `C688`** → `C6AE` → plafond `C682` → `C6AA` → plafond `C6C0` (+ `byte_C33D = (C6C0 <
C6AA)`) → **`sub_AF75A`** → **plancher `C686`** → plafond `C684` → **`C6B2` = sortie finale**.
Sémantique des tests vérifiée : `cc_SGT` ⇒ **plancher**, `cc_SLT` ⇒ **plafond**.
**Sources des limiteurs** : `C680` ← **`C698` (demande du régulateur)** l.186652 · `C684`/`C686` ←
tâche couple seg014 (l.177920 / 178001) · `C682`/`C688` ← 4 sites (l.179820-821, 180333/180409,
181239/181315) · `C67E`, `C696`, `C6C0` = **sentinelles jamais réécrites** (`0x7FFF`) ⇒ voies
inactives dans ce dump.
**★★★ Découverte : le régulateur agit par PLANCHER, pas par substitution** —
`C680 = C698` (l.186651-186652) et `cmp C6A6, C698` ⇒ `FD18.4` (l.185007-185016) : la pédale gagne
**automatiquement** dès qu'elle demande plus, par simple jeu du plancher. Le « cartes inversées
remplaçant la pédale, sauf dépassement » est donc un **effet émergent d'une seule affectation**.
**Exploitation de `C6B2`** : `cmp C6B2, C6A4` (l.178423-178427) ⇒ `C6B2 ≠ C6A4` alimente le drapeau
**« limitation active »** (`bset USR0` l.178445 → bit `0x40` de l'état) — **l'indicateur à loguer**.
**Carto 2-D de la cascade** : `word_1B5E → 0xE8A06`, `tagY = 0xC42E` (régime), `n = 10`, axe
`0 · 600 · 750 · 1000 …`, évaluée à `(C91C, D9AA)` ⇒ `byte_C8F8` (seule carte de la cascade).
**Bloc `word_18B2 → 0xE4E2C`** : `2000 · 1500 · −2000 · −2500 · 5000 · 4500 · 13000 · 1100 · 600 ·
−15587 · 35 · −20 · −10 · 3000 · −15616 · −11788 · 8 · 0 · 500 · 1000` ; `+0x0E = 1100` et
`+0x10 = 600` encadrent `C8FE` (l.155117-155160), puis `[r0+8] = valeur + C596 (120)`.
**Reste à faire** : `sub_AF75A` (l.182854, transformation/quantification) · identifier les limiteurs
réels `C682`/`C688` · trouver le lien aval vers la durée d'injection.

---

## B.61 — Étape 114 : `sub_AF75A` = filtre conditionnel, pas une quantification

**Corps complet (20 instructions, l.182853 appelée depuis seg015:2F6A)** : entrée en `r12`, sortie en `r4`.
**Deux portes** : `byte_C2C0 == 4` (l.178614-178617) **ET** `(byte_C227 & 2) != 0`. Si l'une manque :
**passe-plat strict** (`loc_AF790 : mov r4, r9` + `bset word_FD16.13`).
**S'il est actif** : `jnb word_FD16.13` ⇒ `D8C2 = entrée`, `D8C0 = 0`, `bclr FD16.13` (**réinitialisation
= pas de rampe au réengagement**), puis `unk_1E50(word_1A96, entrée, &D8C0)` et **retour de `D8C2`**.
⇒ **filtre à état (lissage) de l'IQ finale**, pas un arrondi d'injection.
**`unk_1E50` = stub de bibliothèque** (`ds 1`, zone absente du dump — même limite que les checksums).
Signature constante sur tous ses appelants : `(handle, X, &dest)` → écrit `[dest]` (état) et
`[dest+2]` (sortie) = **filtre du 1er ordre à constante de temps cartographiée**. Même schéma qu'à
l'Étape 110 (`unk_1E50(word_1A98, C91C, &D8C8)` → `D8C8`/`D8CA`).
**Paramètre** : `word_1A96 → 0xE7FF2`, mot lu = **`0x4000` (16 384)** ; handle voisin `word_1A98 →
0xE7FF4` = `0x0302` (770). Format du descripteur non tranché (les deux handles sont à 2 octets d'écart).
**★ Portes** : `byte_C2C0` = **octet de codage variante** (comparé à `1` en l.163017/163143/178618 et à
`4` ici, lu 10 fois) ; `byte_C227` bit 1 écrit par `seg013:loc_99828` (l.135629) = chaîne CAN/entrées.
**★ Dans ce dump la variante par défaut n'est pas `4`** (bloc `0xE111E` = `00 01 01 00 00 01 00 01 …`,
toutes les autres lectures attendent `1`) ⇒ **`sub_AF75A` très probablement INACTIF** : `D9A6` traverse
la cascade sans filtrage. À confirmer par log (`D8C2` reste à 0).
**⇒ Cascade réelle = 8 clamps purs** : `D9A6 = C6A6 [+C69E si D9AC==1]` → `C6B8` (brut) → plancher
`C680` (=`C698`) → plafonds `C67E`/`C696` (inactifs) → `C6A4` → plancher `C688` → plafond `C682` →
plafond `C6C0` (inactif) → [filtre inactif] → plancher `C686` → plafond `C684` → **`C6B2`**.
**À loguer** : `D9A6`/`C6B2`, `C6B8`, `C6A4`, `C680`, `D8C2`, `byte_C2C0`, `byte_C227`.

---

## B.62 — Étape 115 : les limiteurs réels `C682`/`C688` (et `C684`/`C686`)

**★★ Moule commun** (`l.180255-180333` plafond, `l.180391-180409` plancher ; **dupliqué** en
`l.181164-181239` / `l.181242-181315` pour la 2e variante) : `word_D904` = **accumulateur de
limitation de couple**, initialisé à **`0x7FFF`** (« aucune limitation », l.179732/179841/179868) et
abaissé par chaque limiteur via **`word_1DDA`** (min, l.180159-180163). Si `D904 >= 0x7FFF` ⇒
`C682 = 0x7FFF`, `C688 = 0`, drapeaux `byte_C335` bits `0x20`/`0x10` effacés (limiteurs neutralisés).
Sinon : `r7 = D904 − C67A` (si `byte_C339 == 1`) ou `D904 − C678` (si 0), saturé 0…`0x7FFF` →
**`unk_1D6C(…, r7, word_144E)`** = interpolation 1-D de la courbe **`0xE13DC`** (tag `0xC63C`, n=9,
axe `0 · 1707 · 3413 · 5120 …`) → **`word_1D94(0xC83E, y, word_1448/0x1446)`** = carto 2-D →
**`C682`** (plafond, drapeau `0x20`) et **`C688`** (plancher, drapeau `0x10`).
**★ Même moule dans la tâche couple seg014** (`l.177974-177979`, handles `word_144E` + `word_1448`) ⇒
**les 5 limiteurs actifs ne sont que 3 mécanismes** : `C680` = `C698` (régulateur) · `C682`/`C688` =
conversion couple→IQ (carto 2-D) · `C684`/`C686` = même conversion calculée en seg014.
**★ Non décodable (même limite que les checksums)** : `unk_1D6C` = **stub**, `word_1D94` et
`word_1DDA` = **pointeurs de fonction** (`ds 2`, appelés par `↓P`) — bibliothèque absente.
**★ Les handles `0x1446` / `0x1448` pointent sur du vide** : `0xE2078` et `0xE211A` = **12 octets à
zéro** ⇒ les pointeurs des cartos 2-D sont **remplis à l'initialisation** (sélection de variante),
d'où les deux variantes du bloc.
**Sélecteur de mode `byte_C339`** = `(C68A >= C626)` calculé en `l.189047-189058` (zone
régulateur/décollage), remis à 0 par l'init `l.188959` ⇒ le mode de limitation dépend d'un **état
d'exploitation**, pas du codage.
**Leviers actionnables identifiés** : cartes souhait `0xE8B50`/`0xE8BD4` + seuil `0xE8C58 = 539`
(changement de rapport) · **courbe `0xE13DC`** (plage couple→IQ) · **carto 2-D derrière `0x1448`/
`0x1446`** (couple max — à localiser) · `C698`/`C690` (demande régulateur).
**Prochaine étape** : la **routine d'init qui remplit `0x1446`/`0x1448`** = désigne les cartos de
limitation de couple réellement utilisées.

---

## B.63 — Étape 116 : extraction des cartos couple → IQ

**★ ERRATA E26** : la §4 de B.62 était fausse — les emplacements `0x1446`/`0x1448` ne sont **pas
vides**, leurs 12 premiers octets sont un **en-tête à zéro** et la carto commence derrière.
**★ Méthode corrigée** : table des handles **indexée en OCTETS** —
`EA = 0xE0000 + u16[0x61400 + (handle − 0x1400)]` ⇒ seuls les handles **PAIRS** sont valides (un
handle impair lit un mot désaligné ⇒ valeur fantôme, d'où le faux « slot vide »).
**★★ Format d'une carto de limitation (162 octets exactement, vérifié `0xE211A − 0xE2078 = 0xA2`)** :
`[10 mots d'en-tête = 0][axe 8 points = 16 o][7 lignes × (1 séparateur 0 + 8 valeurs) = 126 o]`.
**★★ Carto n°1 — `handle 0x1446` → EA `0xE2078`** (mode 0, offset `C678`), axe
`1460 · 3100 · 4608 · 6144 · 7808 · 10768 · 14096 · 17920` ;
lignes : `800 1538 2532 3605 4762 8582 12212 15540` / `800 1492 2434 3336 4310 5593 6920 8480` /
`880 1587 2492 3278 4023 5066 6142 8067` / `830 1495 2402 3236 3980 4926 6025 7853` /
`800 1481 2299 3098 3869 4960 6132 7650` / `800 1372 2097 2901 3761 4920 6692 10710` /
`720 1301 2123 2956 3905 5465 7348 11264`.
**★★ Carto n°2 — `handle 0x1448` → EA `0xE211A`** (mode 1, offset `C67A`), axe
`1080 · 2710 · 4200 · 5632 · 7040 · 8960 · 10880 · 13184` ;
lignes : `660 1340 2110 3243 4424 6224 8112 10544` / `700 1409 2273 3173 4040 5265 6578 9087` /
`610 1465 2279 3058 3920 4910 5970 8070` / `690 1401 2157 2903 3699 4720 5784 8103` /
`640 1428 2230 3030 3790 4860 6110 7856` / `750 1372 2260 3060 3850 5000 6692 10710` /
`800 1430 2240 3080 4050 5465 7342 10964`.
**Lecture** : même forme pour les deux (col. 1 quasi constante 610-880, colonnes 7-8 très dispersées ;
lignes 1, 6, 7 les plus permissives) ; **n°1 toujours plus permissive que n°2** (ex. l.1 c.8 : `15540`
vs `10544`) ⇒ cohérent avec mode 0/1 par `byte_C339`.
**Unités (hypothèse, non tranchée)** : axe = **vitesse 0,01 km/h** (14,6 → 179,2) ; valeurs = **couple
0,01 Nm** (6 → 155 Nm) — en 0,01 mm³ la valeur `15540` = 155 mm³ serait impossible (souhait plafonné à
80 mm³). La **conversion couple → IQ est faite dans `word_1D94`** (bibliothèque absente) ⇒ `C682`/
`C688` non recalculables à la main. **Un patch sur ces tables a donc un effet indirect.**
**Annexe** : table des handles `0x1440-0x1470` documentée (`0x1440→0xE12F6`, `0x1442→0xE1E30`,
`0x1444→0xE130E`, `0x1446→0xE2078`, `0x1448→0xE211A`, `0x144A→0xE13B0`, `0x144C→0xE13C6`,
`0x144E→0xE13DC`, `0x1454→0xE21BC`, `0x1470→0xE225A`).
**Reste à faire** : identifier ce que vaut **`0xC83E`** (tampon passé en `r12` à `word_1D94`) pour
lever l'ambiguïté d'unité.

---

## B.64 — Étape 117 : comprendre les cartes de limitation (explication)

**But de ces cartes** : le calculateur raisonne en **deux unités** — les protecteurs (boîte, fumée,
ABS, régulateur) en **couple**, l'injection en **mm³**. Les cartes `0xE2078`/`0xE211A` sont le
**traducteur couple → débit**. Ce ne sont ni des cartes de puissance ni d'agrément.
**★★ Convention d'appel établie** (vérifiée sur ~60 sites de `word_1D94`) : `r12` et `r13` sont des
**POINTEURS**, pas des valeurs. D'où, pour nos cartes : **X = le mot en RAM `0xC83E`** (variable
globale, écrite hors zone désassemblée) et **Y = le résultat de la courbe 9 points `0xE13DC`**
appliquée à `D904 − C67A/C678`. La sortie devient `C682` (plafond) / `C688` (plancher).
**Lecture de la chaîne** : `C6A6` (souhait, mm³) → limiteurs en couple (`D904`) → **carte de
conversion** → `C682`/`C688` → cascade → `C6B2` (mm³ réellement injectés).
**Les deux cartes** : n°1 `0xE2078` (handle `0x1446`, offset `C678`, axe `1460…17920`, sortie
720→15540) · n°2 `0xE211A` (handle `0x1448`, offset `C67A`, axe `1080…13184`, sortie 610→10964).
**La n°1 est ~47 % plus permissive** (l.1 c.8 : `15540` vs `10544`) et les deux **ne servent jamais
ensemble** : `byte_C339` choisit l'une **ou** l'autre ⇒ **deux modes d'exploitation**, pas deux étages.
**Format** : `[10 mots = 0][axe X 8 pts][7 × (1 séparateur 0 + 8 valeurs)]` = 162 o. Les 10 mots à
zéro = **en-tête neutralisé** ⇒ **l'axe des 7 lignes n'est pas dans la donnée**, il est imposé par la
bibliothèque (régimes ? rapports ? températures ?) — non identifiable.
**Unités (hypothèses étiquetées)** : axe X = vitesse `0,01 km/h` (14,6→179,2) ; sortie = `0,01 mm³`
(6→155, mais 155 > maxi 80 ⇒ ne briderait presque jamais) **ou** `0,01 N.m` (6→155 N.m, conversion
faite en bibliothèque). **Non tranché** ⇒ on ne peut pas dire « baisser telle case donne +Y de couple ».
**Déblocage** : ① identifier l'écrivain de **`0xC83E`** (nomme l'axe X) · ② **log** de
`C682`/`D904`/`C6A6`/`C6B8` (si `C682 > C6A6` en permanence, ces cartes ne brident pas ⇒ ne pas y
toucher) · ③ suivre `C68A`/`C626` (nomme les deux modes).

---

## B.65 — Étape 118 : révision critique — format réel des tables

**★★★ ERRATA E27 — l'Étape 116 est RETIRÉE sur le fond.** Les blocs `0xE2078`/`0xE211A` ne sont
**pas** des « cartes couple → IQ » : l'« axe X de 8 points » et l'unité « 0,01 N.m » étaient des
hypothèses de découpage, non prouvées. **Cet ECU travaille uniquement en mm³ d'IQ.**
**★★★ Format canonique établi par la preuve** : une carte = `[tag][n][axe n pts][0 séparateur]
[valeurs n pts]`. Preuve en `0xE83F4` : `50222 (0xC42E)`, `19`, axe
`0 · 50 · 800 · 1000 · 1250 · 1500 · 1750 · 2000 · 2250 · 2500 · 2750 · 3000 · 3500 · 3750 · 4000 ·
4250 · 4500 · 4800 · 5200`, séparateur `0`, puis les valeurs. ⇒ **c'est la carte 19×1 sur axe RPM
valeurs en mm³ attendue**, et `main_torque = 0xE841E` désigne non pas une carte mais le **bloc de
valeurs** de cette courbe (d'où le `0` du séparateur en tête).
**★★ Courbe plein gaz extraite** (0,01 mm³) : régime `0/50/800/1000/1250/1500/1750/2000/2250/2500` →
`3516/3516/4485/5800/6660/7060/7430/7280/7060/6870`, puis `2750/3000/3500/3750/4000/4250/4500` →
`6810/6440/6270/6240/5690/5300/4750`. **Maximum 74,3 mm³ à 1750 tr/min** — forme caractéristique d'un
plein gaz 2.2 HDi.
**Autres courbes de la famille** : `0xE8928` (n=15, axe dès 635 tr/min, valeurs 3516→6500→6240) ·
`0xE8968` (**doublon** de `0xE8928`) · `0xE89A8` (n=12, **`10000` partout**).
**★★ `10000` = 100 mm³ = sentinelle « AUCUNE LIMITATION »** (au-dessus de tout IQ atteignable),
présente partout dans la zone, y compris juste avant les blocs 162 o (`0xE2060`).
**Statut révisé des blocs 162 octets** : ils ne respectent **aucun** critère du format canonique
(pas de tag, pas de `n`, **7 séparateurs** au lieu d'un, valeurs entrecoupées) ⇒ **hypothèse
reformulée : jeu de 7 courbes partageant un axe de 8 points** (format « Kennlinien-Satz » de la
bibliothèque), avec **une seule entrée interpolée** et des lignes sélectionnées par index —
**hypothèse, plus un fait**.
**Prochaines étapes ordonnées** : ① nommer chaque courbe de `0xE83xx-0xE89xx` via son handle et son
site d'appel (« quelle courbe = quel limiteur ») · ② vérifier si le 1er mot (toujours `0`) des blocs
162 o sert d'**index de sélection** aux sites d'appel · ③ alors seulement, savoir quelles cases
toucher et en mm³.

---

## B.66 — Étape 119 : suivre le code après le souhait (nommage par usage)

**★★ ERRATA E28 — alignement des courbes** : la règle est **`valeur[k] ↔ axe[k+1]`** (l'axe compte un
point de plus que le bloc de valeurs : 19 points d'axe, 17 valeurs). Le **74,3 mm³ est à 2000 tr/min**
(et non 1750). Table corrigée : `50→35,2 · 800→35,2 · 1000→44,9 · 1250→58,0 · 1500→66,6 · 1750→70,6 ·
2000→74,3 · 2250→72,8 · 2500→70,6 · 2750→68,7 · 3000→68,1 · 3500→64,4 · 3750→62,7 · 4000→62,4 ·
4250→56,9 · 4500→53,0 · 4800→47,5`.
**★★ ERRATA E29 — le modèle des « handles » était FAUX** : `0x1400-0x1FFF` ne sont pas des
identifiants de cartes mais des **variables POINTEURS en RAM**, initialisées par la table de flash à
`0x61400`. Le code les **déréférence** : `mov r4, word_1BE8` puis `[r4]`, `[r4+#1]` ; `word_148E →
0xE2348` avec `[+0x16]=6000`, `[+0x18]=1200`, `[+0x1A]=1200` comparés à `C3C0`/`C3BE`. ★ Les pointeurs
voisins `0x1BE0…0x1BEC → 0xE8E06…0xE8E12` sont espacés de **2 octets** dans le **même bloc** ⇒ **ce ne
sont pas des cartes**.
**★★★ Inventaire des consommateurs** (CSV `sites_maps_usage.csv`) : **63 sites 2-D** (`word_1D94`, 32
pointeurs) + **44 sites 1-D** (`unk_1D6C`, 21 pointeurs) = **107 sites** ; par fonction : `sub_B64A8`
24 · bloc après `sub_AFAA0` 24 · `sub_A7D96` 23 · `sub_BAC40` 11 · `sub_AB3AC` 10 · `sub_BF750` 7 ·
`sub_97FF8` 3 · `sub_B7788` 3.
**★★★ Limiteur de fumée trouvé** (`sub_B64A8`, l.188584-188592) : `C94C := C6A2` (charge) →
`unk_1D36(word_1BEC, charge)` → `DA4E` → `+ C662` → **`C664` = IQ max par la charge**. En **mm³**, pas
en N.m. Réserve : `C664` écrit **une seule fois, jamais relu** dans la zone désassemblée ⇒ consommateur
en bibliothèque.
**★★★ Suite après le souhait** : `C6AA` → 1-D `word_144C` (0xE13C6) → 2-D `word_1444` (0xE130E) avec
`X = r0+6`, `Y = r0`, `+ C678` → **triplet `D41C`/`D41A`/`D418`** (l.189176-179) → **écarts vs `C640` :
`C63E`/`C63C`/`C63A`** (l.189181-188) → `D41E = D41C − C404` (l.189194).
**★★★ Conversion finale** (`sub_9AE42`/`sub_9B0E0`, l.139990+) : `r12 = C63A` · `r13 = [[word_1660]]` ·
`r14 = [[word_1658]+2]` → `unk_20AC` → **saturation 0…0xFE** → octets **`byte_C821`, `byte_C822`
(avec `C640`), `byte_C820`, `byte_C823`, `byte_C824`, `byte_C81B…C81F`, `byte_C88A`** ; relus l.141404
(`C825`), 141420 (`C827`), 141664 (`C828`), 141908 (`C829`). Signature d'une **grandeur de commande
d'injecteur**, pas d'un couple.
**★ Chaîne complète établie** : `C6A6 → limiteurs → 0xE8A06 → C688/C682 → sub_AF75A → C6AA → 0xE13C6 +
0xE130E → D418/D41A/D41C → C63A/C63C/C63E → unk_20AC → octets C81x/C82x`.
**Reste à lire** : `sub_A7D96` (23 sites) et `sub_BAC40` (11 sites).

---

## B.67 — Étape 120 : commande de pompe, smoke map, limitations par température

**★★★ ERRATA E30 — `0xE8A06` n'est PAS dans la cascade d'IQ.** Preuve l.182807-182815 :
`D9AA` → `D3D4` · `r12 = word_1B5E` (→ EA **0xE8A06**) · `r13 = C91C` (**régime**) · `r14 = D9AA` (**IQ**)
→ `unk_1D50` → **`movb byte_C8F8, rl4`**. Axes dans la donnée : `0xC42E` (0…5002) et **`0xD3D4`**
(0…8000 = 0…80 mm³). ⇒ **`0xE8A06 = f(RPM, IQ) → C8F8`, un OCTET 0…250 = commande de pompe HP**,
calculée **à côté** de la chaîne de quantité. La cascade continue séparément à l.182816 (`D9A6` vs
`C688`/`C682`/`C6C0`). **ERRATA E31** : `D3D4` = simple copie de `D9AA` (l.182808).
**★★★ SMOKE MAP TROUVÉE : `0xE8444`** — `word_1B40 → EA 0xE8444` ; axe1 `0xC42E` **régime** 16 pts
**0…5200**, axe2 **`0xC3E6` = masse d'air** 16 pts **3000…11500** (0,1 mg ⇒ 300…1150 mg), grille
**16×16**, sortie **1500…7600** (15…76 mm³). Appel l.181913 `unk_1D50(word_1B40, C42E, C3E6)` →
`D986` → **`C690`** ; et `C690` est un **PLAFOND de `C698`** (l.185814-185820 : `cmp C698, C690`,
si `>` alors `C698 := C690`). Variante froide : `word_1B46 → 0xE87D6` = f(régime 200…620, C3EC 700…850).
Origine de `C3E6` : bloc `word_15F0 → 0xE3AD0` champ `[+4]` (l.131319). Autres cartes à axe `C3E6` :
`0xE8872` (6×6), `0xE8444`.
**★★★ LIMITATIONS PAR TEMPÉRATURE** (axes Kelvin×10, dictionnaire : `C3D2` = **T° LDR** id `0F00`,
`C3B0` = **T° carburant** id `0F02`) — **T° moteur `C3D2`** : `0xE80A0` (régime 100-1000 × 2481-3731,
1300…12500) · `0xE3908` (1000-2500 × 2531-3131, 0…4200) · `0xE86F4` (0-1760 × 2431-3531, 0…9230) ·
`0xE868C` (`C3D2` × `C562` vitesse, 0…9230) · **`0xE880A` (1300-4000 × 3841-3951 = 111…122 °C, 0…7040
= protection surchauffe)** · `0xE68F4` (`C3C2` × `C3D2`) · `0xEBB46` (`D5B0` × `C3D2`). **T° carburant
`C3B0`** : **`0xE8000`** (800-4800 × 3051-3751 = 32…102 °C, 1500…7600) · **`0xE7F7E`** (800-4800 ×
3601-3751 = 87…102 °C, 1500…7630).
**★★ Deux routines d'interpolation à ne plus confondre** : `unk_1D50(ptr, X, Y)` = **valeurs** (cartes
classiques) · `word_1D94(ptrX, ptrY, ptr)` = **pointeurs** (bibliothèque).
**★ Livrable** : `inventaire_cartes_2D_axes.csv` — **85 cartes 2-D** détectées par signature
`[tagY][nY][axeY][tagX][nX][axeX]` avec variables d'axe et étendues. **Base de travail désormais :
les cartes et leurs axes d'abord, le code ne confirme que le consommateur.**
**Prochaines étapes** : ① nommer `C3E6` (bloc `0xE3AD0` champ `[+4]`) = axe air de la smoke map ·
② repérer les cartes plafonnant `C698` **par température** · ③ la **smoke map `0xE8444` est le vrai
levier** pour 1re/2de (elle plafonne tout), avant les courbes `0xE83xx`.

---

## B.68 — Étape 121 : chaîne complète du souhait aux injecteurs (19 cartes)

**Document de référence** `ETAPE121_chaine_complete_du_souhait_aux_injecteurs.md` : chaque maillon
porte sa ligne de code ; statut **[C]** confirmé / **[S]** usage confirmé.
**Entrées** : `C91C` régime (copie de `C42E`) · `C952 → C6DA` pédale · `C3E6` masse d'air ·
`C908` T° LDR (copie de `C3D2`) · `C900` T° carburant · `C562` vitesse · `C576` code de rapport.
**★★ SOUHAIT** : `sub_B56F8` l.186821-846 — sélecteur `[word_1B6A]` = **`0xE8C58` = seuil 539** vs
`C576` ⇒ `C576 < 539` → **`0xE8BD4`** (l.186835), sinon **`0xE8B50`** (l.186843), tous deux
`f(régime 0…5000 × pédale 118…10000)` → **`C6A6`** (appel l.195503-506).
**★★ SMOKE** : `0xE8444` `f(régime × C3E6 air)` → **`C690`** (l.181914, 181950) ; variante froide
`0xE87D6` (l.181946) ; **`C690` plafonne `C698`** (l.185814) ; `C680 := C698` = plancher du souhait.
**★★ TEMPÉRATURES** : carburant `0xE8000` (32…102 °C) et `0xE7F7E` (87…102 °C) → **`D8C4`**
(l.177109/127/184, 177139/157/173) · moteur `0xE80A0` (l.177378) · `0xE86F4` (l.182069) ·
`0xE868C` T°×vitesse → `D98A` (l.182115) · **`0xE880A` surchauffe 111…122 °C** (l.182258) ·
`0xE3908` (l.131306).
**★★ LIMITEURS 2 MODES** : `0xE13DC` (9 pts) → `0xE2078` (mode 0 → **`C682`**, 6 sites) / `0xE211A`
(mode 1 → **`C688`**, 6 sites).
**★★ ARBITRAGE** : `C6A6` max(`C680`) → `C6B8` → plafonds `C67E`/`C696` → `C6A4` → `D9AA` →
plancher `C688` → `C6AE` → plafond `C682` → `C6AA` → plafond `C6C0` → **`sub_AF75A` → `C6B2`**.
**★★ INJECTEURS** : `0xE8A06` `f(régime × IQ)` → **`byte_C8F8`** (pompe HP, l.182813) ; puis
`0xE13B0` (l.189063/304/327) + `0xE13C6` (l.189069…189522) + `0xE130E` (l.189118/139/160/526) →
`D418`/`D41A`/`D41C` → écarts vs `C640` → **`C63A`/`C63C`/`C63E`** → `unk_20AC` → **`byte_C81B…C829`,
`byte_C88A`** (saturation 0…254, l.139993-140223).
**Total : 19 cartes, chacune adossée à une ligne de code.**
**Reste ouvert** : `C3E6` et `0xC83E` rafraîchis hors zone désassemblée ; découpage interne de
`0xE2078`/`0xE211A` ; paramètres `[word_1660]`/`[word_1658+2]` non nommés.
**Levier pratique** : **`0xE8444` (smoke) + `0xE8BD4` (souhait 1re/2de)** = les deux seules cartes à
toucher pour un gain en bas rapport.

---

## B.69 — Étape 122 : les fonctions de la chaîne (entrées / sorties / rôle)

**Document** `ETAPE122_les_fonctions_de_la_chaine.md`, complément de l'É.121.
**★★ A. Routines de bibliothèque — ABSENTES du dump (`ds`, vides)** ; conventions déduites de 385
sites d'appel : **`unk_1D50(r12=carte, r13=X valeur, r14=Y valeur) → r4`** (72 appels) ·
**`word_1D94(r12=ptrX, r13=ptrY, r14=carte) → r4`** (64) · **`unk_1D6C(r12=dest, r13=X, r14=courbe) →
r4 ET [r12]`** (44) · **`unk_1D36(r12=courbe, r13=X) → r4`** (168) · **`unk_20AC(valeur, référence,
échelle) → r4`** (251, échelle **`0x2710` = 10000** prouvée l.131283 et l.182266) ·
**`word_1DDA(courant, candidat, étiquette) → r4` + drapeau `USR0`** (35) · `unk_1E50(handle, x, état)`
= pas de filtre · `unk_1E34`, `word_1E08`, `word_1DA8`.
**★★★ DÉCOUVERTE : `word_1DDA` = sélection du minimum AVEC étiquette de source** — preuve l.180159-163
`word_1DDA(0x7FFF, D904, D906)` → `mov word_D904, r4` puis `bmovn word_FD16.14, USR0` ⇒
**`D904` = minimum courant, `D906` = ÉTIQUETTE DU LIMITEUR GAGNANT** (la variable qui dit « qui bride »).
**★★ B. Fonctions désassemblées (corps cité)** : `sub_B56F8` (l.186821, `r12`=régime `r13`=pédale →
`r4`=souhait ; bascule sur `C576` vs **539**, effet `C93E := C576`) · `sub_AF75A` (l.177009, filtre 1er
ordre si `byte_C2C0==4` ET `byte_C227&2`, état `D8C0`/`D8C2`, drapeau `FD16.13`) · **`sub_B33DC`
(l.183315, `r12`→`min(r12, C692)`, `0x7FFF` = pas de limite, **cas véhicule à l'arrêt `C562==0` →
`C5AC`**) · `sub_AFA42` (l.177370, instantané `C91C`/`C908` puis carte `0xE80A0`) · `sub_972FA`
(l.131297, idem avec `0xE3908`) · `sub_972CA` (l.131274, `0xE38D8` + `unk_20AC` échelle 10000) ·
`sub_BAC40` (l.195544, **anti-rebond/maintien** : compteur pointé, débordement `0xFF` → `DB84=1`,
`DB86` mémorise, retour booléen) · `sub_A7D96` (l.163166, décodeur `C307`/`C31A`) · `sub_BF750`
(l.203990, test de `FD26+1`/`FD28`) · `sub_AFAA0` (l.177430, réinit `D8F2`/`D8F4` + invalide
`D8F6`/`D8F7`) · `sub_B64A8` (l.188256, 428 l. : rampe, `C914 := C41A`, `C94C := C6A2` →
`unk_1D36(0x1BEC)` → `+C662` → **`C664`**).
**★ CORRECTION** : `sub_97FF8` = `movb [r12],[r12]` — **coquille sans effet** ⇒ les cartes attribuées à
cette « fonction » à l'É.119 le sont par **proximité de label**, pas par appartenance.
**★ Table des 25 pointeurs → EA** de la chaîne (0x1B66→0xE8B50 · 0x1B68→0xE8BD4 · 0x1B6A→0xE8C58
seuil 539 · 0x1B40→0xE8444 smoke · 0x1A84→0xE8000 · 0x1A82→0xE7F7E · 0x1A8C→0xE80A0 · 0x1B44→0xE86F4 ·
0x1B42→0xE868C · 0x1B4A→0xE880A · 0x1B48→0xE87EE · 0x15E2→0xE38D8 · 0x15E4→0xE3908 · 0x1B5E→0xE8A06 ·
0x144A→0xE13B0 · 0x144C→0xE13C6 · 0x1444→0xE130E · 0x1446→0xE2078 · 0x1448→0xE211A · 0x144E→0xE13DC ·
0x1BEE→0xE8E26 · 0x1BEC→0xE8E12 · 0x1BD8/0x1BDA→0xE8DEE/0xE8DF8 · 0x1A96→0xE7FF2).

---

## B.70 — Étape 123 : audit complet (récursif) de tout le dossier

**Niveau 1 — données : 44 contrôles automatiques, 0 échec réel.** Identité (`fo 0x7CC00` = **EA
0xFCC00** HW `0281010877` · SW `0xEBFB0`/`0xFBFB0`/**`0xFFEF0`** · `BOOT 0xFFF08`) · 19 pointeurs
vérifiés · axes des cartes de la chaîne · seuil **539** · max **7430 @ 2000 tr/min** · `0xE89A8` =
10000 · pas de 0xA2 · duplication `0xE2788`≡`0xF2788` · patch **8 octets** exacts. Les 3 « échecs » du
1er passage étaient des **bugs du test** (EA vs offset fichier).
**★★ Validation croisée indépendante** : les 6 premières entrées de la table de pointeurs
(`0xE100A · 0xE101E · 0xE1026 · 0xE104A · 0xE106E · 0xE1082`) **coïncident exactement** avec les 6
premières cartes trouvées par le scan par signature ; **85/85** des cartes détectées sont pointées.
**★★ C1 — mon scan des cartes était incomplet** : il rejetait les axes > 60000 (valeurs **signées**,
ex. 61046 = −4486) ⇒ **85 → 86** cartes (`0xE7D44` ajoutée). CSV `inventaire_cartes_2D_axes_v2.csv`.
**★★ C2 — le catalogue est incohérent avec lui-même** : §5 « table exhaustive 66 cartes » vs §10
errata #57 « total **91** cartes » vs mon scan **86 à axes explicites** ⇒ **§5 périmé**, l'écart 91−86
= **5 cartes à identifier**.
**★★ C3 — les citations de lignes sont le point faible** : sur **195 citations vérifiables**, **38
exactes (19,5 %)** ; décalages de 1 à 5 lignes en général, et jusqu'à **−20** (plafond fumée
`C698 := C690` : annoncé l.185814, réel **l.185833-185838**, dans `loc_B4D1A`). **Règle adoptée :
citer symbole + EA**, la ligne en secours.
**★ C4 — `C690` s'applique en NEUF endroits** (l.185133, 185500, 185835, 186059, 186123, 186335,
186645, 187403, 187510), pas un seul.
**★★★ C5 — auto-correction** : `C3E6` n'est **PAS prouvé** être la masse d'air — je l'avais nommé par
sa **plage** (3000…11500), soit **exactement l'erreur de méthode de l'errata #56** (« une plage ne
prouve rien »). ⇒ **rétrogradé en `?`** : `0xE8444` est confirmée comme **smoke map de structure**,
pas la sémantique de son axe.
**★★★ TROUVAILLE INÉDITE** : `0xE8B50` et `0xE8BD4` (souhait selon le seuil 539) **ne diffèrent qu'en
5 cases sur 48**, toutes en **colonne pédale = 20 %** : régime `750/1000/1300/1750/2250` →
`2400/2132/1844/1520/1260` vs `2350/1782/1344/1070/910` (−2 % à −30 %). **À 40 % de pédale et plus,
les deux cartes sont identiques** ⇒ patcher `0xE8BD4` est **quasi invisible** ; le levier réel est
`0xE8444`. **Nuance à porter sur l'É.121 §9.**
**Verdict** : données **solides**, code solide sur la substance mais fragile sur la localisation,
documentation bonne avec 2 défauts (catalogue §5, bandeaux « PÉRIMÉ » à poser sur Étapes 116/117).

---

## B.71 — Étape 124 : audit FAP / post-injection / régénération

**Demande** : *« Fait un audit complet du filtre à particule, de la post injection et tout ce qui est lié aux régénérations. Reprend tout ce que nous avons vu. »*
Document : `ETAPE124_audit_FAP_post_injection.md`.

**★★★ FONDATION NOUVELLE — l'image est entièrement cartographiée.** Inventaire des 10 706 labels +
détection des runs de `0xC3` ≥ 64 o ⇒ `0x80000`–`0x87FFF` **padding** (32 768 o, 100 %) · `0x88020`–`0xD5414`
**CODE** (316 405 o) · `0xD5415`–`0xDFFFF` **stub 16 o + padding** (44 011 o, 100 %) · `0xE0000`–`0xFBFFF`
**CALIBRATION** (114 688 o) · `0xFC0EA`–`0xFEB22` **CODE queue** (10 809 o) · `0xFEB23`–`0xFFFFF` boot.
⇒ **le code est couvert à 100 % par `clean.asm`** ; aucune zone de code cachée. La duplication `0xF0000`
est confirmée à l'octet (runs identiques à +0x10000 : `0xE0E72`↔`0xF0E72`, `0xEBC48`↔`0xFBC48`), et le
padding de `0xEF880` tombe dans le run `0xEBFBA`–`0xEFFFF` (16 454 o).

**★★★ CONSÉQUENCE** : l'argument « la post-injection est dans la moitié non désassemblée » est **invalide**.
Ce logiciel **n'a pas de post-injection séparée** : la régénération **élargit le temps principal** via
`word_C69E` (+0…60 mm³) et `word_C77C` (+10 mm³) et **borne** par des courbes indexées sur l'EGT.

**Régénération — architecture complète (nouvelle)** : tâche **`0x12C`** (l. 163238, `scxt CC2_CC27, #12Ch`),
gardée par `byte_C2BA` · état **`byte_D7A8` ∈ 0…5** avec table de sauts en **`0xA04`** (`shl #1`/`jmpi`) ·
drapeaux **`byte_D7B8`** (bit 1 = fenêtre charge/régime · bit 2 ⇒ mode 8 · **bit 4 (`orb #4`) = demande de
régénération** · bit 8 = mode · 0x80 = limitation) · **intégrateur de suie `word_D7B0`** (`unk_20AC(x,#1,#0x64)`
puis `add word_D7B0, r4`, saturation `0x7FFF`/`0x8000`, plafond `[word_1904+0x16]`) · **seuil `word_D7B2`** =
courbe EGT sélectionnée par `byte_D7B8 & 2` · déclenchement `D7B0 > D7B2` ⇒ `D7B8 |= 4` · fin de cycle ⇒
`D7B0 := 0`, `D28E := 0`.

**Six courbes FAP, toutes 1-D** (aucune carte 2-D indexée par `C586`/`C584`/`D1B6`/`D5A2` sur 86) :
`0xE5F9C` (`C586`, 250→550 °C, `100,3200`) · `0xE5FC0` (`C586`, 250→600 °C, `100,32767` = régén. interdite) ·
`0xE639A` (`C586`, 8 pts, `7231→5131` décroissant) · `0xE4D14` (`D1B6`, `117…655`) · `0xE4D38` (`D1B6`,
`15…260`) · `0xEBA84` (`D5A2`, **`[10000,10000]` neutralisée**).

**ERRATA E32 (majeur)** — `ETAPE121` présentait `byte_C81B…C829` comme la **commande des injecteurs**.
**Faux** : ces octets ont **1 écriture et 0 lecture** chacun (`C820` l. 140141, `C821` l. 140182, `C822`
l. 140223, `C823` l. 140264, `C824` l. 140302, `C81B` l. 140353) et ne sont consommés qu'**indirectement**
par le publieur de valeurs mesurées **`sub_9CFD0`** : `(2, 0, 0xC820, 0x348)` l. 143249-143253 et
`(7, 0, 0xC81B, 0x388)` l. 143536-143540 ⇒ **canaux de diagnostic `0x348` et `0x388`**. La chaîne de
conversion `0xE13xx → D41x → C63x → unk_20AC → octet` est réelle mais **terminale et passive**.
**E33** : `word_C642 = r6 − C640` = **écart signé** (l. 189543), pas une quantité absolue.
**E34** : `word_C69E` = **11 sites** (5 `add` + 4 `sub` + 1 lecture + 1 écriture l. 187528), pas 6.
**E35** : `word_C586` = **9 lignes**, pas 8. **E36** : `word_D294` = recopie de `D7B2`, **0 lecteur** ⇒ miroir.

**Vérifié conforme** : porte `byte_C2BA` (1 écriture l. 151775 ← `[word_141C+0x27]`, 63 lectures) ·
`byte_C297` co-conditionne le bit 3 de `C820` · `word_D5A2` 1 écriture / 0 lecture · `word_C77C` =
`0xE6B86([0,0])` + `0xE6B92([1000,1000])` = **1000 constant** · `C69E = clamp(BDBC|BDDC selon BDAC&1, 0, 6000)`
(`word_147E`→`0xE22CA` `[+8]=6000`, `[+0Ah]=0` ; `word_1434`→`0xE1294` `[0]=0` ⇒ pas de doublement) ·
`sub_ACD46` = `mov r4,#1` ⇒ branche **inconditionnelle**.

**Confiance** : image 99 % · porte 99 % · machine à états 95 % · courbes 95 % · `C81x` diagnostic 95 % ·
absence de post-injection séparée 85 %.

---

## B.72 — Étape 125 : audit adversarial (« tout est faux jusqu'à preuve »)

**Demande** : *« Analyse tous les documents produits, croise leurs données, vérifie-les à nouveau en supposant qu'à priori tout est faux et que rien n'est démontré (sauf ce que j'ai affirmé), vérifie tout ! »*
Document : `ETAPE125_audit_adversarial.md`. Corpus : 124 docs (22 773 l.), 54 CSV, `clean.asm`, `edc.bin`.

**★★ PIERRE ANGULAIRE — la formule d'adressage est une INFÉRENCE, pas une preuve.** `grep` sur `clean.asm` ⇒
**aucune référence à `0x61400`** : aucune instruction ne lit cette table. La formule correcte, écrite sans
ambiguïté (**errata E41**), est `u16 @ (0x60000 + h)` — **décalage en OCTETS** (≡ `0x61400+(h-0x1400)`), et
`EA = 0xE0000 + entrée`. Une relecture en mots donne 9,3 % de validité au lieu de ~100 %.
Validation : **6/6 courbes FAP** re-dumpées exactement (`0xE5F9C`, `0xE5FC0`, `0xE639A`, `0xE4D14`, `0xE4D38`,
`0xEBA84` avec tags `C586`/`D1B6`/`D5A2`), **298 structures** valides, **385/385** entrées du registre d'appels
re-dérivées (348 non vides, **0 désaccord**). Formule concurrente « base 0x1000 » : 1,5 % ⇒ éliminée.

**★★ CARTES — 86 confirmées, 66 et 91 sont FAUSSES (E37).** Scan neuf indépendant : 89 brutes, dont **3
artefacts** éliminés (`0xE79EE` tag `0x7D2B` hors espace RAM ; `0xE9835` et `0xE9837` **adresses impaires**)
⇒ **86**. Croisement CSV v2 : cartes manquantes **0**, **désaccords de dimension 0**. Le CSV est exact à 100 %.

**★★ 8 CARTES ORPHELINES (E39, inédit).** Sur 86 : **62** ont un site d'appel dans le registre, **16** ont une
variable pointeur référencée sans être au registre, et **8 n'ont AUCUNE référence nominale** : `0xE22F4`
(h.`0x1482`), `0xE230C` (h.`0x1484`), `0xE3B2C` (h.`0x15FC`), `0xE6306` (h.`0x1946`), `0xE7D44` (h.`0x1A54`),
`0xE7DAC` (h.`0x1A56`), `0xEAFB2` (h.`0x1DB8`), `0xEBB46` (h.`0x1E1A`). ⇒ la règle « aucune carte sans site
d'appel » n'est satisfaite que pour **78/86**.

**★★ REGISTRE D'APPELS = artefact le plus fiable (E40).** **385/385** lignes exactes (**décalage 0**), 348/348
EA conformes. La dérive des citations (19,5 % exacts) touche la **prose**, pas les CSV. Défaut mineur : 8 lignes
contiennent un `;` dans un champ (`"#64h ; 'd'"`) ⇒ `split(';')` naïf cassé.

**★★ ERRATA E38 — E32 réécrit : bonne conclusion, mauvaise preuve.** Le corps de `sub_9CFD0` a été lu : args
en `[r0+#12h]`=r12, `[r0+#16h]`=r14, `[r0+#18h]`=r15 ; `r12` = **index de record** (`shl #4` puis `add #0EF00h`
⇒ record 16 o) ; `r15` réduit à `key = ((r15&7)<<13)|((r15>>3)&0FFh)` ⇒ `0x348`→`0x0069`, `0x388`→`0x0071` ;
`r14` = **source** copiée sur `n` octets. Ce n'est **pas** un publieur de diagnostic : c'est une **routine de
mémorisation** et le bloc `C820`/`C81B` en est une **entrée**. Conclusion maintenue (pas une commande
d'injecteur), preuve reformulée, nature exacte **non établie**.

**RE-VÉRIFIÉ CONFORME** : `sub_ACD46` = `mov r4,#1`/`rets` (XREF unique `loc_ACFC6`) · `byte_C2BA` 63 réf. /
**1 écriture** l.151775 · `word_C69E` = 1 label + **11 sites** · `word_C586` = 1 label + **9 sites** ·
`word_C77C` = `0xE6B86[0,0]`+`0xE6B92[1000,1000]` = **1000** · `0xE8A06`→`byte_C8F8` (l.182810-182814,
`mov r12, word_1B5E`/`calls unk_1D50`/`movb byte_C8F8, rl4`) · `0xE8B50` vs `0xE8BD4` = **5 cases/48** toutes
en colonne pédale 2000 (`2400/2132/1844/1520/1260` vs `2350/1782/1344/1070/910`) · seuil `0xE8C58` = **539**.

**NON DÉMONTRÉ (à cesser de présenter comme acquis)** : lien handle→adresse (empirique) · **noms d'axes**
(méthode condamnée en errata 56, seules les plages sont prouvées) · unité **mm³** (vient de l'utilisateur) ·
`unk_20AC`/`0x2710` (bibliothèque `0xC3`) · nature de `sub_9CFD0` · absence de post-injection (85→**80 %**).

**INCIDENT UTILE** : `0281010877` présent **1 fois** à `EA 0xFCC00` (ctx `…B075WF2S…`) ; **`0281010597` ABSENT
du fichier** ⇒ conforte la correction « ce binaire n'est pas un semi-mux » ; `1037353776` **3 fois**
(`0xEBFB0`, `0xFBFB0` = +`0x10000`, `0xFFEF0` à côté de `BOOT`).

**Confiance révisée** : cartes **99 %** · registre **99 %** · courbes FAP **99 %** · `C82x`≠injecteurs **90 %** ·
noms d'axes **55 %** · unité mm³ **60 %**.

---

*Document généré automatiquement — ne pas éditer à la main, modifier `outils/genere_catalogue.py`.*