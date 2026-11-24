# ÉTAPE 66 — `0xECCB2` : pourquoi c'est vide, et **la vraie** seconde passe sur la zone

> Deux choses à assumer dans cette étape :
> **1)** mon `0xCCB2` n'était pas `0xECCB2` — et il y a une deuxième raison, plus intéressante, pour
> laquelle `0xECCB2` est vide ;
> **2)** mon inventaire de la zone était **pollué par 8 handles qui n'existent pas**. La seconde passe
> donne **138 lectures** au lieu de 20, et **39 offsets** pour `0xE1148` au lieu de 11.

---

## 1. Pourquoi `0xECCB2` ne contient rien — deux raisons distinctes

### Raison 1 : `0xCCB2` est une adresse **RAM**, pas une EA de ROM

L'instruction est `mov r4, #0CCB2h`. C'est un **pointeur de travail 16 bits** dans l'espace
variables/EEPROM, pas une adresse de calibration. La table de défauts est **construite en RAM au
runtime** — il n'y a rien à lire dans le binaire à cet endroit. J'aurais dû écrire « RAM `0xCCB2` ».

**Preuve du contexte :** deux lignes plus haut, `mov r8, #0CC54h` puis `mov [r8], r4` et
`cmp r8, #0CCA4h` → on **écrit** les 20 dwords convertis dans la plage `0xCC54…0xCCA4`. C'est une zone
de travail, pas une source.

### Raison 2 — celle qui compte : **la copie `0xE` est tronquée**

| constat | valeur |
|---|---|
| dernier octet de données de la copie `0xE` | **EA `0xEBFB9`** |
| puis `EA 0xEC000 → 0xF0000` | **16 384 octets de `0xC3`** (filler, un seul octet distinct) |
| `EA 0xECCB2` (copie `0xE`) | `C3 C3 C3 C3…` — **effectivement vide** |

**Mais la copie de référence est `0xF`**, et là :

```
EA 0xFCCB2 : f0 fe 0f 00 21 8f 04 60 50 7e 00 00 41 8f 06 60 0a cc 0f 00 ff ff ff ff
```

### Le calcul des deux copies, fait une fois pour toutes

| plage | différence `0xE` vs `0xF` |
|---|---|
| `0xE0000–0xEBFFF` | **14 octets isolés** (dont `0xE0FF6`, `0xE0FFC`, `0xE434D`, `0xEBCFC`) |
| `0xEC000–0xEFFFF` | **14 133 octets différents** |
| **total** | **14 147 octets** |

⇒ **Les deux copies sont identiques jusqu'à `0xEBFB9`** (à 14 marqueurs près) et **divergent
entièrement au-delà** : la copie `0xF` contient **≈ 14 Ko de données que la copie `0xE` n'a pas**.
C'est une région **jamais analysée** dans nos 66 étapes.

**Ce que cette région n'est pas** : j'ai testé les formats connus (1-D `[tag][n][axe][valeurs]`,
2-D `[tagY][nY]…`) sur les 8 192 positions paires → **18 détections, toutes des faux positifs**
(axes « 15..2 », valeurs « 0..65535 », tags `0xCC00`/`0xC000`). Donc **pas de calibration
cartographique** là-dedans ; on y trouve 4 857 octets `0xFF` (zone effacée) mêlés à des suites de mots
(`0x000F`, `0x8F21`, `0x6004`, `0xCC0A`…). **À investiguer comme un objet séparé.**

**Conséquence pratique** : toutes nos valeurs de calibration restent valides (copies identiques
jusqu'à `0xEBFB9`), mais tout ce qui est au-delà de `0xEC000` doit être lu dans la copie **`0xF`**.

---

## 2. Mon erreur d'inventaire : **8 handles fantômes**

La table de pointeurs (`fichier 0x61400`) contient **exactement 1305 entrées**, soit les handles
**`0x1400` → `0x1E30`**. J'avais énuméré jusqu'à `0x2400` : au-delà de `0x1E30` ce ne sont **plus des
pointeurs**, mais une autre table (valeurs `0x0010`, `0x02D5`, `0x02E4`, `0x0320`, `0x044C`…).

**Les 8 « handles » que j'ai annoncés à l'étape 65 n'existent pas** :
`0x1F8A`, `0x232E`, `0x1F0A`, `0x23F4`, `0x1E76`, `0x1FE6`, `0x1FC8`, `0x2148`.

### Inventaire corrigé de la zone

| handle | EA | taille réelle | contenu | lectures |
|---|---|---|---|---|
| `0x141C` | `0xE111E` | **42 o** | options (35 octets lus, 36 lectures) | 36 |
| `0x141E` | `0xE1148` | **52 o** | **options — 39 offsets lus, 102 lectures** | **102** |
| `0x1420` | `0xE117C` | **36 o** (pas 24) | **18 × `0xFFFF`** | par index |
| `0x1422` | `0xE11A0` | **36 o** (pas 23) | **18 × `0x0000`** | par index |
| `0x1424` | `0xE11C4` | 40 o | **20 valeurs 16 bits** | par index |
| `0x1426` | `0xE11EC` | 32 o | (juste après la fenêtre +180) | — |

Les trois derniers ne sont **jamais** lus par déplacement : ils le sont **par `pointeur + PID×2`**.
C'est pour ça que ma première passe les voyait comme « non lus » — et 18 entrées = **les PID `0x00` à
`0x11`**, ce qui est cohérent avec un usage OBD.

---

## 3. ★ La vraie seconde passe : **138 lectures** dans la zone

Méthode : pour chaque handle réel, on suit le registre chargé **jusqu'à 130 lignes** et on relève
**tous** les `[rX+#NN]` tant qu'il n'est pas rechargé — puis on convertit en EA absolue.

| mesure | valeur |
|---|---|
| sites de lecture | **138** |
| EAs distinctes lues | **74** |
| dont dans `0xE1129 → 0xE11E1` | **66 octets sur 185** (36 %) |
| nature | **89 SWITCH / 49 DONNÉE** |
| `word_141C` | 35 offsets, 36 lectures |
| `word_141E` | **39 offsets, 102 lectures** |

### Les 39 offsets de `0xE1148` — regroupés par fonction

| groupe | offsets | sites | ce que fait le code |
|---|---|---|---|
| **masque 32 bits** | **`+0x15 +0x16 +0x17 +0x18`** | 1 chacun | ★ `andb byte_D98E/D98F/D990/D991, octet` puis recomposition en `word_D3CE` → **4 octets de calibration = masque 32 bits** appliqué à un mot de configuration |
| **sélecteurs à 5 états** | **`+0x04`** (8), **`+0x09`** (9), **`+0x14`** (8) | 25 | `cmpb` successifs sur `#1 #2 #3 #4` → **codes 0…4** ; `+0x04` déclenche en plus le service EEPROM `sub_CE9B4` (`#1B2h`, `word_176E`, `#46FEh`) |
| **échelle** | **`+0x0A`** | **17** | `r8 = 0` si `==1`, sinon `0x2710` (10 000) |
| **variante** | `+0x0C` (6), `+0x0D`, `+0x1B` | 8 | sauts de stratégie, tous en seg014 |
| **masques ponctuels** | `+0x1F`, `+0x20`, `+0x30` | 3 | `andb rl7/rl6/rl4, octet` |
| **drapeaux de bloc** | `+0x33` (=51, dernier octet) | 7 | seg013 + seg015 |
| **seg017 (tâches/CAN)** | `+0x1C +0x1D +0x2B +0x2C +0x2D` | 6 | options de la couche communication |
| **divers** | `+0x01 +0x02 +0x03 +0x05 +0x06 +0x08 +0x19 +0x21…+0x26 +0x28…+0x2A +0x2E +0x2F +0x31` | 32 | drapeaux et sélecteurs |

**13 offsets jamais lus** : `+0x00 +0x07 +0x0B +0x0E +0x0F +0x10 +0x11 +0x12 +0x13 +0x1A +0x1E +0x27 +0x32`.

### Le motif le plus instructif : les 4 octets-masque `+0x15…+0x18`

```asm
loc_B2C3C:
                mov     r4, word_141E
                movb    rl5, [r4+#15h]
                andb    byte_D98E, rl5      ; masque octet bas
                movb    rl5, [r4+#16h]
                andb    byte_D98F, rl5
                movb    rl5, [r4+#17h]
                andb    byte_D990, rl5
                movb    rl5, [r4+#18h]
                andb    byte_D991, rl5      ; masque octet haut
                movbz   r5, byte_D98F
                shl     r5, #8
                movbz   r2, byte_D98E
                or      r5, r2
                mov     word_D3CE, r5       ; ★ mot 16 bits recomposé
```

Ce n'est **pas** quatre interrupteurs : c'est **un filtre de 32 bits**. Chaque octet de calibration
autorise ou interdit un groupe de bits d'un mot de configuration (les 4 octets `D98E…D991` sont
assemblés en mots : `D3CE` d'abord, puis le suivant). **Quatre octets = une seule fonction.**

---

## 4. Ce que ça change dans le catalogue

- `0xE1148` passe de « 11 offsets » à **39** : c'est le **panneau d'options principal du calculateur**,
  102 lectures, présent dans **les cinq segments**.
- `0xE117C` / `0xE11A0` font **36 octets chacun (18 mots)**, pas 24 / 23.
- Les 8 handles fantômes sont **retirés** du catalogue.
- La zone `0xEC000 → 0xF0000` de la copie `0xF` est ajoutée comme **objet ouvert** (« 14 Ko de données,
  aucun format connu »).

---

## 5. Consignation

- **`CATALOGUE_MAITRE.md` § 13 B.12** : errata de B.11 (handles fantômes, tailles), la table des
  39 offsets, la différence des deux copies.
- **`zone_0xE1129_v2.csv`** : les 74 EAs lues avec site, segment, nature et handle source.
- Catalogue : 2 142 → **2 192 lignes**.

## 6. Prochain pas, dans l'ordre

1. **La région `0xEC000–0xF0000` de la copie `0xF`** (≈ 14 Ko) : pas de format cartographique, mais
   14 Ko de données uniques. C'est le plus gros gisement non exploré du firmware.
2. **Les 4 octets-masque `+0x15…+0x18`** : remonter `byte_D98E…D991` jusqu'à ce qu'ils filtrent —
   c'est peut-être **l'option de variante la plus structurante** du bloc.
3. **Les 3 sélecteurs à 5 états** (`+0x04`, `+0x09`, `+0x14`) : 25 sites à décoder ensemble.
