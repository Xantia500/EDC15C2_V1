# ÉTAPE 8 — « L'adresse EST le type » : modèle d'adressage des variables, et convergence sur `C3E6`

Suite de l'étape 7. Question : **« quand on écrit `word_C3E6`, est-ce que tout n'est pas lié — l'axe et le type de donnée avec l'adresse ? Peux-tu déterminer à quoi ça correspond ? »**

**Réponse : oui, les trois sont liés, et c'est démontrable.** J'ai trouvé le mécanisme complet : il existe **deux bancs de RAM jumeaux** et l'adresse d'une grandeur est *à la fois* son identité physique, son type et son nom dans le Datensatz. C'est ce qui explique les « doublons » que nous voyions (`C3E6` ici, `C90C` là) : **c'est la même grandeur, vue dans deux bancs**.

Puis, sur cette base, la convergence sur la nature de `C3E6` (§5).

---

## 1. Les trois couches d'adressage

| Couche | Zone | Rôle | Preuve |
|---|---|---|---|
| **A — Interface** | `0xC2xx` (octets), `0xC3xx`–`0xC8xx` (mots) | variables **partagées** entre l'OS et l'application. **Ce sont ces adresses qui servent de tags dans le Datensatz.** | 14 des tags du Datensatz sont recopiés tels quels en couche B (§2) |
| **B — Copies de travail** | `0xC9xx` | **instantané par tâche**, pris au début de chaque tâche (juste après `scxt CC2_CC27, #<jeton>`) | 120 paires `word_C9xx ← word_C3xx/C4xx/C6xx/C7xx` recensées |
| **C — Descripteurs de calibration** | `0x14xx`–`0x17xx` | pointeurs vers les blocs du Datensatz (`word_141C`, `141E`, `1430`, `1432`, `1438`, `147E`, `15E2`, `15E4`, `15F0`, `1708`, `1722`…) | vivent en mémoire basse, absente de l'image |

### Le banc B est un instantané, pas un doublon

Toutes les routines de calcul commencent par le même rituel :

```asm
scxt  CC2_CC27, #36Eh        ; jeton de tâche
mov   word_DC00, CC2_CC27
mov   r4, word_C3E8          ; ← COUCHE A
mov   word_C90C, r4          ; → COUCHE B  (instantané)
mov   r5, word_C42E
mov   word_C91C, r5          ; régime : 120 occurrences de cette paire !
```

C'est ce qui garantit que toutes les cartes d'une même tâche sont lues avec **des valeurs cohérentes entre elles**.

### Conséquence directe sur `C3E6`

| Banc A (interface, = tag du Datensatz) | Banc B (copie de travail) | Occurrences de la copie |
|---|---|---|
| `word_C3B0` | `word_C900` | 5 |
| `word_C3B2` | `word_C902` | 3 |
| `word_C3BA` | `word_C904` | 18 |
| `word_C3C2` | `word_C906` | 30 |
| `word_C3D2` | `word_C908` | 31 |
| `word_C3D6` | `word_C90A` | 1 |
| **`word_C3E6` / `word_C3E8`** | **`word_C90C`** | 4 |
| `word_C3EA` | `word_C90E` | 1 |
| `word_C42E` (régime) | `word_C91C` | **120** |
| `word_C60A` | `word_C940` | 11 |
| `word_C60E` / `C68A` / `C6B6` | `word_C942` | 5 |
| `word_C612` | `word_C944` | 5 |
| `word_C6A2` | `word_C94C` | 26 |
| `word_C6DA` | `word_C952` | 2 |
| `word_C7C6` | `word_C990` | 5 |

→ **`word_C3E6` ≡ `word_C3E8` ≡ `word_C90C` : une seule grandeur, trois adresses.** C'est pour cela que le site n°1 de lecture de carte utilise `word_C3E6` alors que les sites 2 et 3 utilisent la version élaborée `word_C90C` : les deux sont numériquement identiques dans le cycle, l'un est la valeur d'interface, l'autre l'instantané de tâche.

Fichier joint : **`interface_vers_banc_travail.csv`** (120 paires, avec pour chaque source le nombre d'axes du Datensatz et l'étendue).

---

## 2. Le type est effectivement porté par l'adresse

Sur les **339 axes** du segment `0xE`, il y a **98 tags distincts**. Deux seulement sont **impairs** :

| Tag | Étendue | Lecture |
|---|---|---|
| `0xC337` | 0 → 250 | variable **octet** (0…255) |
| `0xD369` | 0 → 255 | variable **octet** (0…255) |

Les **96 autres sont pairs** → variables **mot de 16 bits**, ce qui est cohérent avec le fait que **toutes les grilles et tous les axes du Datensatz sont en mots de 16 bits** (§3 de l'étape 7).

Et l'**étendue** de l'axe donne l'échelle physique employée par la variable :

| Étendue typique | Tags | Interprétation |
|---|---|---|
| 0 → 255 / 0 → 250 | `0xD369`, `0xD36A`, `0xC337` | grandeur 8 bits brute |
| 0 → 1023 | `0xD048`, `0xD04A`, `0xD07C`, `0xD07E` | **canal ADC 10 bits** |
| 0 → 90 / 0 → 180 | `0xC590`, `0xD17C` | pourcentage |
| 0 → 5000 / 0 → 6000 / 0 → 7000 / 0 → 14000 | `0xC42E`, `0xC6A2`, `0xC7C2`, `0xD012` | **régime** (et ses variantes d'échelle ×1, ×2 …) |
| **2231 → 4231** | `0xC3D2`, `0xC3BA`, `0xC5A4`, `0xC5FE`, `0xD3CC`, `0xD230-0xD234` | **pression absolue en mbar** (1,73 → 3,73 bar, soit 0,73 → 2,73 bar de suralimentation) |
| **118 → 10000** | `0xC6DA` | **consigne de quantité** (1,18 → 100,00) |
| **3000 → 11500** | **`0xC3E6`** | **voir §5** |

Corollaire méthodologique : le nom du symbole (`word_C3E6`) ne dit rien de l'unité ; **c'est le couple (adresse, étendue) qui la donne**. Les 98 tags sont la nomenclature réelle de l'ECU.

---

## 3. Voisinage fonctionnel de nos cartes dans le Datensatz

Les cartes à axe `C3E6` ne sont pas isolées : elles appartiennent à un **bloc continu `0xE8000`–`0xE88xx`** entièrement consacré à la voie d'air :

| En-tête | Axe X | Axe Y | Grille | Valeurs |
|---|---|---|---|---|
| `0xE8000` | régime 800→4800 (8) | **pression `0xC3B0` 3051→3751** (6) | `0xE8024` | 1500→7600 |
| `0xE80A0` | régime 100→1000 (8) | **pression `0xC3D2` 2481→3731** (10) | `0xE80CC` | 1300→12500 |
| **`0xE8444`** | **régime 0→5200 (16)** | **`0xC3E6` 3000→11500 (16)** | `0xE848C` | 0→7600 |
| `0xE868C` | **pression `0xC3D2` 2431→3831** (6) | `0xC562` 0→18000 (6) | `0xE86AC` | 0→9230 |
| `0xE86F4` | régime 0→1760 (10) | pression `0xC3D2` 2431→3531 (9) | `0xE8722` | 0→9230 |
| `0xE87D6` | régime 200→620 (2) | `0xC3EC` 700→850 (2) | `0xE87E6` | 8000 |
| `0xE880A` | régime 1300→4000 (6) | pression `0xC3D2` 3841→3951 (6) | `0xE882A` | 0→7040 |
| **`0xE8872`** | régime 0→5000 (6) | **`0xC3E6` 0→10000 (6)** | `0xE8892` | 0 (désactivée) |

Trois axes seulement dans ce bloc : **régime**, **pression d'admission** (`C3D2`, `C3B0`) et **`C3E6`**. `C3E6` est donc la **troisième grandeur de la voie d'air** — après le régime et la pression de suralimentation.

---

## 4. Ce que le code fait de `C3E6` — chaîne complète

### Production (tâche `0x36A`, segment 013)

```asm
loc_974F8:
  mov  word_D096, r9
  mov  r12, r0 / calls 0, word_1DA8        ; service indirect (pointeur d'interface)
  mov  word_C3E0, r4
  mov  r12, word_15EC / r13 = word_C904 / r14 = word_C940
  calls 0, unk_1D50                        ; → r6   (carte pression × C60A)
  mov  r12, r9
  mov  r4, word_15F0 / mov r13, [r4] / mov r14, word_C91C
  calls 0, unk_20AC                        ; → r7   = (r9 × RÉGIME) / [word_15F0+0]
  mov  word_D098, r7
  mov  r12, r7 / r13 = r6 / r14 = #2710h
  calls 0, unk_20AC                        ; → word_D09A = 10000 × r7 / r6
```

`unk_20AC(x, y, z)` = **(x × z) / y** (forme déduite de 4 usages concordants ; `#2710h` = 10000 sert de normalisation).

**Point capital** : la valeur est un **produit par le régime** (`word_C91C`), normalisé par une constante de calibration `[word_15F0+0]`. Une grandeur **proportionnelle au régime** est un **débit** (quantité par unité de temps), **pas** une masse par cycle.

Publication, plus loin dans la même tâche (listing 131727-131740) :

```asm
loc_977A4: calls 9, sub_9787E ; cmp r4, #0 ; jmpr cc_Z, loc_977B0
           mov r7, word_C3E2                 ; sinon → valeur de REMPLACEMENT
loc_977B0: mov word_C90C, r7                 ; banc B (instantané)
           mov word_C3E6, r4                 ; banc A
           mov word_C3E8, r5                 ; banc A (2ᵉ slot)
```

### Surveillance

| Contrôle | Lieu | Seuil | Réaction |
|---|---|---|---|
| Valeur de substitution | `loc_97324` | `C3E6 = C3E8 = C3E2 = [word_15F0+4]` | **DTC `187Fh`** (classe `0B2h`) si `[word_141E+14h]==4` et `byte_C2C9 < 11h` |
| Plausibilité haute | lignes 171660-171700 (tâche `0x36E`) | `C90C` doit être **≤ courbe `word_19CE`(régime)** | **DTC `267Fh`** (classe `0EEh`) |
| Exploitation | lignes 204400-204440 (tâche `0x38A`) | `unk_1D36(courbe word_1DE8, C90C)` → `word_D598` → ×`[word_149C+0Ch]`/1000 → `word_C79C` (si régime ≠ 0) | courbe de conversion 1-D |
| Axe de cartes | sites §5 de l'étape 7 | 2 cartes | bornes `word_C690`, `word_C626` |

Le contrôle « **mesuré ≤ courbe(régime)** » est la signature d'un **contrôle de plausible d'un débitmètre** : le débit d'air ne peut pas dépasser le débit maximal admissible à ce régime.

---

## 5. Convergence : `C3E6` = **grandeur de la voie d'AIR — masse/débit d'air mesuré**

### Le faisceau d'indices

| # | Indice | Sens |
|---|---|---|
| 1 | axe **Y** de 2 cartes dont l'axe X est le régime | 2ᵉ grandeur d'une loi moteur |
| 2 | voisinage immédiat des cartes à axe **pression d'admission** (`C3D2` 2,48→3,73 bar, `C3B0`, `C3C2`) | même famille physique : **air** |
| 3 | gratuit dans le bloc `0xC3xx`, à côté de `C3B0/C3BA/C3C2/C3D2` (pressions) | grandeur « air » |
| 4 | étendue **3000 → 11500**, unique dans cette famille | grandeur de débit, pas de pression |
| 5 | valeur **proportionnelle au régime** (§4) | **débit** (masse/temps), pas masse/cycle |
| 6 | bornée par **courbe(régime)**, DTC `267Fh` | contrôle de plausible débitmètre |
| 7 | substitution + DTC `187Fh` | signal « mesuré », pas consigne calculée |
| 8 | > en air ⇒ sortie de carte **plus faible** (§5 de l'étape 7 : à régime donné, la grille décroît quand `C3E6` croît) | loi du type **EGR/AGR** : plus d'air frais ⇒ moins de recyclage |

### Convergence retenue

> **`word_C3E6` = débit (ou masse) d'air mesuré, de la voie d'admission/débitmètre.**
> **Unité la plus probable : mg/s, soit 3,0 → 11,5 g/s.**
> Cohérence : ralenti d'un 1,9 l TDI ≈ 15 kg/h ≈ **4,2 g/s** (dans l'axe) ; charge partielle 2000 tr/min ≈ **11,5 g/s** (haut de l'axe) ; pleine charge au-delà ⇒ **écrêtage** par le dernier point. En kg/h l'axe donnerait 30→115 kg/h, incohérent avec un ralenti à 15 kg/h.
> Conséquence : la carte `0xE8444` (régime × débit d'air, sortie 2482→7600) est une **loi de commande de la boucle d'air** (EGR/AGR, ou pilotage de la vanne de suralimentation N75) ; les 2482→7600 sont très probablement un **rapport cyclique en 0,01 %** (24,8→76 %) ou une valeur d'actionneur normalisée.

### Ce qui n'est PAS encore prouvé (à ne pas présenter comme fait)

1. **L'unité exacte** (mg/s vs kg/h×10 vs une échelle interne). Elle est fixée par la déclaration de la variable dans l'OS, absente de l'image.
2. **Le nom de la carte** (EGR vs N75) : il dépend du consommateur final de `word_C690`.
3. **La réserve d'usage** : l'étiquette « borne basse de l'intégrateur » donnée à `word_C690` à l'étape 5 reste une **interprétation** ; le nouveau contexte (boucle d'air) invite à la revérifier — si `word_C690` pilote un actionneur à rapport cyclique, c'est une consigne d'actionneur, pas une borne d'intégrateur.

### Test décisif (une seule session sur banc)

| Point d'arrêt | À lire | Ce que ça tranche |
|---|---|---|
| `loc_974F8` + 4 (après `unk_20AC`) | `r7` **et** le débitmètre physique au même instant | unité et identité (débit vs masse/cycle) |
| `loc_97324` | `[word_15F0+0]`, `[word_15F0+4]` | constante de conversion + valeur de remplacement |
| `loc_B26D2+0Eh` | `r14` (valeur d'axe) vs `r13` (régime) | confirme la coordonnée (régime, air) |
| consommateur de `word_C690` (étape 5, `0xB5AC6`–`0xB5DE8`) | destination finale | EGR vs N75 |

---

## 6. Conséquences pour la suite

1. **La nomenclature des 98 tags est accessible** : adresse (identité) + type (parité) + étendue (unité) + usage (consommateurs). C'est la clé pour **nommer les 44 cartographies** au lieu de les décrire par leurs adresses.
2. **Toutes les cartes se lisent avec les valeurs du banc B** (`0xC9xx`) : pour un point d'arrêt sur une lecture de carte, c'est `word_C90C`, `word_C91C`, `word_C94C`… qu'il faut regarder, pas `word_C3E6`.
3. **Prochaines étapes proposées**, dans l'ordre :
   * **(a)** table complète des 98 tags : `tag ; type ; étendue ; slot banc B ; nb d'axes ; nb de cartes ; consommateurs` ;
   * **(b)** trancher EGR vs N75 en suivant `word_C690` jusqu'à l'actionneur ;
   * **(c)** revisiter l'étape 5 (régulateur) avec le banc B, puisque `C91C` y est le régime et non une « quantité ».
