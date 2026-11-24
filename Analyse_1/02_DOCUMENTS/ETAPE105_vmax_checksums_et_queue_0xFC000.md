# ÉTAPE 105 — Trois chantiers : Vmax (résultat mitigé), checksums (négatif documenté), et la queue `0xFC000` (décisive)

---

## 1. Chantier Vmax — ce que la recherche donne, et ce qu'elle exclut

### Ce qui est éliminé

- **Aucune carte 2-D à axe vitesse** : les 72 enregistrements de `cartes_2D_toutes_avec_axes.csv`
  ont tous des axes dans les plages 200-5000 / 0-10000 ; **aucune** n'a d'axe 180-300 km/h.
  ⇒ la Vmax **n'est pas** une carto 2-D indexée par la vitesse.
- **Aucun immédiat `#61A8h` (25000) / `#4E20h` (20000) en comparaison** : le `A8 61` relevé à
  EA `0x94368` appartient à une **table de sauts** (`14 00 CC 00` = motif d'entrée), pas à un `cmp`.
- Les **33 comparaisons** avec `word_C562` (vitesse) recensées : en dehors de la tâche FGR, elles
  portent toutes sur des seuils **courts** (voir ci-dessous), pas sur une Vmax.

### Deux blocs nouveaux, et ce qu'ils sont vraiment

`word_142C → 0xE1236` et `word_1432 → 0xE1264`, lus par le limiteur `seg015:045C-0x053E` :

| handle | EA | valeurs |
|---|---|---|
| `word_142C` | `0xE1236` | 200 · 60 · 147 · 200 · 250 · −1200 · 1200 · 200 · 25 · 2 · 50 · 0xD100 · −1536 · 24 · 1750 · 50 · 6000 · 50 · 1750 · 10000 |
| `word_1432` | `0xE1264` | 750 · 920 · 870 · 920 · 0xFFFF · 16 · 8 · **275** · 0 · 400 · 1750 · 13000 · 0 · 0 · 1200 · 50 · 50 · **500** · 200 · 200 |

```asm
178540  mov  r4, word_142C
178541  mov  r5, [r4]           ; 200  = 2 km/h
178542  cmp  r5, word_C562
178543  jmpr cc_SGE, loc_B047E  ; si V <= 2 km/h -> drapeau 0x80
...
178575  movb rl4, byte_C330
178576  andb rl4, #70h           ; ★ bits de RAPPORT
178577  jmpr cc_NZ, loc_B04D2
178578  mov  r4, word_1432
178579  mov  r5, [r4+#22h]       ; 500 = 5 km/h
178580  cmp  r5, word_C562       ; cc_SLE
178584  mov  r8, #30h            ; ★ niveau de limitation 0x30
...
178604  mov  r8, #10h            ; ★ niveau 0x10
178613  mov  r4, word_1432
178614  mov  r5, [r4+#0Eh]       ; 275 = 2,75 km/h
178615  cmp  r5, word_C562
178617  movb rl4, byte_C2C0
178618  cmpb rl4, #1             ; ★ présence de la Gangberechnung
178620  movb rl5, word_FD40
178622  movb rl3, byte_FD57
178624  movb rl2, word_FD58
```

⇒ **Ce n'est pas la Vmax** : tous les seuils sont **bas** (200 = 2 km/h, 275 = 2,75 km/h,
500 = 5 km/h, 750/870/920 = 7,5/8,7/9,2 km/h). C'est la logique **arrêt / rampage / décollage**,
qui produit trois **niveaux de limitation `0x10` / `0x20` / `0x30`** sélectionnés par les **bits de
rapport `byte_C330 & 70h`** et conditionnés par **`byte_C2C0 == 1`**.

★ C'est donc bien là que vit la **limitation dépendante du rapport** que tu décrivais (1re/2de) —
pas dans la chaîne `D1B6` (Étape 104, inerte). Le résultat part dans
`unk_20F6(word_1AA2, word_C908, word_D8CE)` (l.178561-178565).

### Piste Vmax restante (identifiée, non tranchée)

Cinq courbes 1-D à **axe 0…255** (axe « octet », donc **vitesse en km/h sur un octet**) :

| EA | tag | axe | valeurs |
|---|---|---|---|
| `0xE7EA6` | `0xD369` | 0 64 128 192 255 | 0 2500 5000 7500 9961 |
| `0xE7EBE` | `0xD369` | 0 51 77 102 108 133 136 255 | 0 0 0 0 0 0 3000 8000 |
| `0xE7EE2` | `0xD366` | 0 104 157 171 181 203 204 224 | 0 0 0 0 0 0 136 136 |
| `0xE7F06` | `0xD36A` | 193 204 | 136 255 |
| `0xE7F12` | `0xD36A` | 181 204 | 0 255 |

Si `0xD369` / `0xD36A` sont des variables de **vitesse octet**, ces cinq courbes sont les candidates
Vmax. À vérifier : écrire un `0` à la dernière valeur de `0xE7EBE` couperait le débit à 255 km/h.

---

## 2. Chantier checksums — négatif, mais cadré

### Les octets qui diffèrent vraiment entre les deux copies (correction de l'Étape 101)

| EA | bloc A | bloc B |
|---|---|---|
| `0xE0FF6-9` | `3D D3 3D D3` | `C3 C3 00 00` |
| `0xE0FFC-F` | `C9 32 05 B2` | `D4 CD C0 17` |
| `0xE434D` | `23` | `03` |
| **`0xEBCFC-FF`** | **`DD 35 D9 5B`** | **`20 5C 77 AF`** |
| `0xEBF1B` | `57` | `46` |
| `0xEC000`+ | `C3…` (effacé) | contenu réel |

⇒ les cibles de checksum sont **`0xE0FF6`, `0xE0FFC`, `0xEBCFC`** (et non `0xEBCF2` comme écrit
en Étape 101 — **errata E16**).

### Algorithmes testés, tous négatifs

| cas | somme16 LE | somme16 BE | somme8 | CRC32 | Adler |
|---|---|---|---|---|---|
| `0xEBCFC` (A) cible `5BD935DD` | `0x0F2BC2D5` | `0x2259DE78` | `0x0031544D` | `0xA65A852E` | `0x2532572D` |
| `0xEBCFC` (B) cible `AF775C20` | `0x0F2AC0E4` | `0x225AEC75` | `0x00315459` | `0xFA939B37` | `0xAB4B5739` |

Aucune correspondance, ni pour `0xE0FF6` / `0xE0FFC`. Contrôle de cohérence : la zone
`0xE0000-0xE0FF5` étant identique en A et B, sa somme est bien identique (`0x021DD191`) — le
protocole est donc bon.

⇒ **Le checksum est un algorithme propriétaire**, très probablement dans la bibliothèque effacée
(`0x80000-0x87FFF`) ou dans le bootloader. Conséquence pratique : **ne recalcule pas à la main** ;
laisse WinOLS / ECUSafe régénérer, ou limite-toi à des valeurs dont tu peux vérifier la couverture.

---

## 3. ★★ Chantier queue `0xFC000` — et la preuve que le bloc B est le bon

### L'identifiant logiciel est écrit en clair

```
EA EFEF0 | 31 30 33 37 33 35 33 37 37 36   =  " 1 0 3 7 3 5 3 7 7 6 "
```

⇒ **`1037353776`** — le numéro SW que tu m'avais donné — est stocké en **ASCII** à `0xEFEF4`,
**uniquement dans la copie B**. La copie A a cette zone **effacée (`C3`)**.

**Conclusion définitive** : la copie **B (`0xF0000`) est la calibration réelle** ; la copie A est
tronquée. Toute modification doit être écrite en B, et répliquée en A **si** l'outil de flash
utilise A — sinon A reste effacée.

### Descripteur « BOOT »

```
EA EFF00 | AA 55 75 14 89 11 30 AA 42 4F 4F 54 00 00 00 00
                            ↑     ↑  B  O  O  T
```

`AA 55` = signature, `42 4F 4F 54` = **"BOOT"**, suivi d'une table de pointeurs
(`00 C0 0F 00`, `FE FF 0F 00`, `14 CC 0F 00`, `00 FF 0D 00`, `00 BF 0F 00`, `5A CC 0F 00`…)
⇒ **bloc de descripteurs bootloader / zones mémoire**, exactement la structure prédite en Étape 101.

### Marqueurs `A5 A5`

`A5 A5` apparaît à `0xFC000`, `0xEC2FB`, `0xEC5FA`… chaque fois suivi d'un **quad de pointeurs** :

```
EA EC2FB | 94 C7 B1 6B 7B D9 | A5 A5 | 14 E0 00 00 | 2E E0 00 00 | 40 E0 00 00 | 00 E3 00 00
EA FC000 | A5 A5 | 14 C0 00 00 | 00 C0 00 00 | 40 C0 00 00 | 00 C3 00 00
```

`A5 A5` = **début de sous-bloc descripteur**, suivi d'une liste d'adresses de sous-structures.
C'est la carte de navigation du Datensatz — elle explique pourquoi les handles `0x14xx` pointent
« en désordre ».

---

## 4. Bilan et suite

| chantier | état |
|---|---|
| limitation par rapport (niveaux `0x10/0x20/0x30`) | **trouvée**, dépend de `byte_C330 & 70h` |
| Vmax | **pas une carto à axe vitesse** ; 5 courbes candidates à axe octet 0-255 |
| checksums | **algorithme propriétaire** ; ne pas recalculer à la main |
| queue `0xFC000` | **SW en ASCII + descripteur BOOT** ⇒ bloc B = référence |

## 5. Errata
- **E16** : la zone de checksum est **`0xEBCFC`**, pas `0xEBCF2` (Étape 101). Les plages exactes
  sont `0xE0FF6-9`, `0xE0FFC-F`, `0xE434D`, `0xEBCFC-FF`, `0xEBF1B`.
- **E17** : `0xA5A5` à `0xFC000` n'est pas un « remplissage » : c'est un **marqueur de descripteur**.
