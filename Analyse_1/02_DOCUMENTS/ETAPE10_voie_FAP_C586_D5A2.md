# ÉTAPE 10 — Voie FAP/DPF : `C586` (EGT) et `D5A2`, et délimitation par le coding `byte_C2BA`

> ⚠️ **CORRECTIONS DE DÉCOMPTE — errata E34/E35 (voir `ETAPE124_audit_FAP_post_injection.md` §4)** :
> §7 de ce document annonce « `add r4, word_C69E` (6 sites) » ; le recomptage donne **11 sites**
> (5 `add` + 4 `sub` + 1 lecture + 1 écriture l. 187528). « 8 sites `C586` » doit se lire **9 lignes**.
> Le fond de l'analyse (porte `byte_C2BA`, chaîne EGT, miroir `D5A2`) reste **valide et confirmé**.

Suite de l'étape 9. Objectif : suivre `C586` et `D5A2`, vérifier qu'il s'agit bien de **sondes de température**, et **délimiter ce qui relève du FAP/DPF et de sa régénération**.

---

## 0. Réponse en cinq points

1. **`word_C586` = température des gaz d'échappement** utilisée comme **grandeur d'axe** et comme **entrée de courbes de correction**. Elle est traitée dans **8 sites** du code, tous dans `seg014` et tous dans le périmètre FAP.
2. **`word_D5A2` n'est pas une mesure** : c'est une **valeur publiée** (1 seule écriture EA `0xBFAA4`, **aucune lecture** dans l'image) qui sert d'**axe** à une table de correction **neutre** (gain = 1,0) dans la plage **200 → 300 °C**.
3. **La chaîne de mesure est bien une chaîne de capteur résistif** : ADC → **table de conversion non linéaire** pointée en **`0x0F864`** (en mémoire basse, absente de l'image) → `word_C394`. **CTN ou CTP : non tranchable depuis `edc.bin`** (§6) — mais la structure (table tabulée + deux défauts de plage) est celle d'un **thermistor**, pas d'un émetteur linéaire.
4. **La porte du FAP existe et elle est unique** : `byte_C2BA = [word_141C + 0x27h]` (octet de coding), recopié EA `0xBF...`/`0xA11BA`, **63 références** dans le code. Tout ce qui est conditionné par `byte_C2BA` = périmètre FAP. C'est la délimitation demandée.
5. **Post-injection** : j'ai trouvé **un terme additif à la quantité** (`word_C69E`) **+ une correction dépendant de la température** (`word_C77C`) qui s'ajoutent à la quantité principale (`word_D844 = word_C6BA + word_C69E + word_C77C`) — mais **pas** de seconde quantité d'injection indépendante (constat négatif, §8).

---

## 1. Correction de l'étape 9 : le format des courbes 1-D est maintenant décodé

Ce bloc de `0xEBA64` à `0xEBA8E` le montre sans ambiguïté :

```
0xEBA64 : C3D2  2  [2431, 2831]   10000  10000     → gain constant 1,00 (inactif)
0xEBA78 : C3D2  2  [2731, 4131]   10000  10000     → gain constant 1,00 (inactif)
0xEBA84 : D5A2  2  [4731, 5731]   10000  10000     → gain constant 1,00 (inactif)   ← NOTRE TAG
```

**Format d'une courbe (Kennlinie)** :

```
<tag> <n> <n valeurs d'axe croissantes> <n valeurs de sortie>
```
soit `4 + 4n` octets. C'est exactement le format que j'avais supposé à l'étape 9 sans le prouver ; la zone `0xE1000`–`0xE10F0` (que je prenais pour un « catalogue d'axes ») est en fait un **enchaînement de courbes dont la sortie est stockée ailleurs** ou d'axes partagés — point à reprendre.

Application à `C586` dans la zone de calibration :

| Enregistrement | Axe `C586` (K × 10 → °C) | Sorties | Lecture |
|---|---|---|---|
| `0xE5F98` | 5231 → 8231 = **250 → 550 °C** | **100 → 3200** | facteur ×100 : **1,00 → 32,00** |
| `0xE5FBC` | 5231 → 8731 = **250 → 600 °C** | **100 → 32767** | facteur ×100 : **1,00 → 327,67** (butée) |
| `0xE639A` | 3731 → 8531 = **100 → 580 °C**, **8 points** | 8 valeurs | courbe de correction complète |

Ces deux premières courbes sont des **rampes de facteur** qui s'envolent au-delà de 250 °C : typiquement des **facteurs de dosage/dérating liés à la régénération**.


---

## 1 bis. Inventaire complet des courbes 1-D (format maintenant prouvé)

Le format `<tag> <n> <n axe> <n sorties>` appliqué à tout le segment `0xE` donne **104 courbes distinctes** (× 2 avec le miroir `0xF`). Fichier joint : **`courbes_1D_datensatz.csv`**.

### Répartition des axes

| Axe de la courbe | Nb de courbes | Grandeur |
|---|---|---|
| `0xC42E` | **64** | **régime** |
| **`0xC3D2`** | **34** | **température moteur (−50…+150 °C)** |
| `0xC60A` | 18 | charge / régime secondaire |
| **`0xC3BA`** | **12** | **température (−50…+135 °C)** |
| `0xC5A8` | 8 | quantité (100…11000) |
| `0xC77A`, `0xC38E`, `0xC5BC`, `0xD1B6`, `0xC562`, `0xC3B0`, `0xD369`, `0xD36A`, `0xC7C2`, `0xD5AE` | 4 chacun | divers (dont 2 tags **octets** `0xD369`) |
| 14 autres | 2 chacun | dont `0xC586`, `0xD5A2`, `0xD230/232/234`, `0xC5A4`, `0xC588`, `0xC3DA` |

→ **46 des 104 courbes sont indexées par une température** (`C3D2` + `C3BA` + les tags thermiques). C'est la colonne vertébrale des corrections thermiques de l'ECU.

### Exemples de courbes de correction thermique (extraits)

| EA | Axe (converti en °C) | Sorties | Lecture |
|---|---|---|---|
| `0xE2F52` | **+17 → +100 °C** (5 pts) | 13000, 13000, 11000, 8000, 7000 | correction **décroissante** avec la T° (facteur ×1,3 → ×0,7) |
| `0xE3E50` | **−5 → +50 °C** (4 pts) | 12000, **1000, 1000**, 12000 | correction **en fenêtre** : active seulement à froid |
| `0xE68D0` | **−30 → +80 °C** (8 pts) | 18000, 18000, 18000, 40000, 40000, **0, 0, 0** | **coupure** au-delà de +40 °C |
| `0xE69D6` | **−25 → +40 °C** (8 pts) | 10000 ×4, 6000, **0, 0, 0** | **coupure** au-delà de +30 °C — typique **post-chauffage / démarrage à froid** |
| `0xE6A6A` | **−25 → +80 °C** (8 pts) | 15000, 15000, 10000 ×4, 5000, 0 | correction dégressive |
| `0xE5208` | **0 → +20 °C** (5 pts) | 0, 100, 400, 1200, 2000 | rampe croissante à froid |
| `0xE51E4` | **−30 → +60 °C** (8 pts) | 300 ×8 | constante (neutralisée) |

**18 des 104 courbes ont toutes leurs sorties à `10000` (= ×1,0) : tables présentes mais neutralisées.** Ne pas les interpréter comme actives.

---

## 2. `word_C586` — les 8 sites et leurs 4 rôles

| Listing | Rôle | Détail |
|---|---|---|
| `153877` (`loc_A265A`) | **source d'une sélection à 3 voies** | `word_C396` ← `C394` si `word_FD30+1==0` ; ← **`C586`** si `word_FD32==0` ; sinon ← `[word_186A+6]` (valeur de calibration) |
| `153964`-`153993` | **conversion** | `r9 = |C586 − word_C584|`, puis **`r9 += 0x0AAB` (2731)** → passage **°C×10 → K×10 absolu** |
| `155179` | **normalisation → tag `D1B6`** | `unk_20AC(C586, [r0+8], [word_1472+0]×1000)` → ×100/`[r0+20h]` → **`word_D1B6`** (tag du Datensatz 0…11000) → courbe `word_18A4` → **`word_C594`** |
| `162605` | **seuil + temporisation** | `[word_18F2+18h]` vs `C586` → décompte `word_D792` → drapeau **`word_FD0A.10`** |
| `163861` / `163869` | **deux courbes selon un mode** | `unk_1D36(word_191E, C586)` **ou** `unk_1D36(word_1922, C586)` selon `byte_D7B8` bit 0 → **`word_D7B2`** → **`word_D294`** |
| `166435` | **seuil comparé à la référence** | `unk_1D36(word_1950, C586)` puis `cmp r9, word_C584` → remise à zéro de `word_D7EE` / `byte_D7EC` |
| `167078` | **substitution réciproque** | selon `[word_1952+3Ch]==1` : `r9 = word_C584 − [1952+26h]` **ou** `r9 = word_C586 − [1952+26h]` → `word_D2B2` → `unk_20AC(r9, [1952+20h], 1)` |

**Trois enseignements structurels :**

* `word_C584` et `word_C586` sont **interchangeables** dans 4 sites ⇒ ce sont **deux températures de même nature** (deux sondes, ou une mesure + un modèle). `0xC586` est un **tag** du Datensatz, `0xC584` non ⇒ `C586` est la grandeur « officielle », `C584` une référence interne.
* `word_C396`, `word_D294`, `word_D2B2`, `word_D1B6` = **points de sortie** de la chaîne EGT : `C396` n'est **jamais relu dans l'image** (→ consommé par l'autre moitié de la flash / diagnostic) ; `D1B6` est un **tag** du Datensatz (donc réutilisé comme axe ailleurs).
* Le **couple de défauts** autour de la sélection (`10FBh`/`84h` en `153842`, `10FDh`/`82h` et `10FEh`/`80h` en `154...`) = **signal hors plage haut / bas** ⇒ signature d'un capteur résistif (voir §6).

---

## 3. `word_D5A2` — une valeur **publiée**, pas mesurée

```asm
; EA 0xBFAA4 (seg015), la seule écriture :
loc_BFAA4:  mov  word_D5A2, r6          ; r6 = valeur saturée (7FFFh/8000h) + 0AABh
            mov  r12, word_1DFA
            mov  r13, r6
            calls 0, unk_1D36           ; → r9 (courbe 1-D)
            ...  unk_20AC(r8, r9, #2710h) ...
            mov  word_D598, r8
            mov  word_D5A0, r8          ; valeur normalisée publiée
```

* **1 écriture, 0 lecture** dans l'image ⇒ `D5A2` est un **miroir de télédiagnostic** (elle n'alimente aucun calcul de cette moitié).
* Elle est pourtant **enregistrée comme tag** dans la zone de calibration avec un axe **4731 → 5731 = 200 → 300 °C** ⇒ il existe une table indexée par cette température.
* Cette table (`0xEBA84`) a un **gain de 1,00** sur les deux points ⇒ **présente mais neutralisée** sur ce véhicule.

**Conclusion** : `D5A2` = **température gaz d'échappement publiée** (plage de travail 200–300 °C = montée en température normale du FAP), dotée d'une **table de correction neutralisée**. Ce n'est pas une entrée capteur primaire.

---

## 4. La chaîne de mesure : ADC → **table en `0x0F864`** → `word_C394`

EA `0xBFF3A` et suivants (seg015, tâche **`0x312`**) :

```asm
calls 0, unk_7B4                       ; service OS : acquisition ADC
scxt  CC2_CC27, #312h
movb  rl0, byte_C21A / movb byte_C89F, rl0    ; n° de canal ADC
mov   r0, word_14FA / mov r1,[r0] / shr r1,#4
cmp   r2, r1 / jmpr cc_NZ, loc_BFFCC          ; décimation : 1 acquisition sur N
mov   r9, #0F864h                      ; ← TABLE DE CONVERSION (mémoire basse)
mov   r3, #0
calls 0Ch, sub_C4AAE                   ; conversion
mov   r1, word_14FC
calls 0Ch, sub_C66EA                   ; filtrage / linéarisation
mov   word_D048, r9 / mov word_C366, r10
...
mov   r1, word_C394 / mov r0, word_14FA / calls 0Ch, sub_C6720
mov   word_C394, r10                   ; ← TEMPÉRATURE publiée
```

* Le pointeur **`0x0F864`** désigne une **table de conversion dans la moitié basse de la flash** (`0x00000`–`0x7FFFF`), **absente de notre image**.
* Deux voies sont maintenues : **`word_D048`** (brut/filtré) et **`word_C394`** (converti, publié) — `word_D048` est lui aussi un **tag** (axe 32→1023, donc **code ADC**).

---

## 5. CTN ou CTP ? — ce qui est prouvable, ce qui ne l'est pas

### Prouvé (binaire)

1. La conversion passe par une **table tabulée** (`0x0F864`) et non par une droite ⇒ capteur **non linéaire**.
2. Il existe **deux défauts de plage** par voie (`10FDh`/`82h` et `10FEh`/`80h`), plus un défaut de cohérence (`10FBh`/`84h`) ⇒ contrôle « circuit ouvert / court-circuit ».
3. La valeur est convertie en **°C×10** (`+2731` pour repasser en K×10) ⇒ la variable est **signée en pratique** (une température jusqu'à −50 °C doit être représentable).

### Non prouvable depuis `edc.bin`

**Le signe du coefficient** (CTN ↔ CTP) est inscrit dans la **table `0x0F864`**, qui est **hors image**. Aucune instruction de l'image ne permet de le déduire : le code traite la valeur **après** conversion, sans jamais manipuler la résistance.

**Ce que je peux dire honnêtement :** votre hypothèse **CTP** est *plausible* pour une sonde de température de gaz d'échappement (les CTP/PT200 sont utilisés pour les hautes températures, car leur résistance **augmente** avec la température et reste exploitable à 600–900 °C, là où une CTN sature), mais **je ne peux pas la confirmer** avec ce fichier. Les CTN classiques (eau, air, gasoil) plafonnent vers 130–150 °C, d'où l'usage d'un autre type pour l'EGT.

### Test décisif

| Mesure | Attendu si **CTP** | Attendu si **CTN** |
|---|---|---|
| Résistance sonde à 20 °C puis à 400 °C | **augmente** | **diminue** |
| Code ADC correspondant | **augmente** avec T° | diminue |
| Donc dans la table `0x0F864` | croissante | décroissante |

→ Une simple mesure ohm-mètre sur la sonde tranche définitivement, et permet aussi de **lire la table `0x0F864`** à l'envers.

---

## 6. La délimitation demandée : **la porte du FAP est `byte_C2BA`**

```
loc_A11BA : movb byte_C2BA, [word_141C + 27h]      ; ← octet de coding, offset 0x27 du bloc de variante
```
**63 références** dans tout le code. C'est le **drapeau d'activation de la chaîne FAP**. Tout ce qui est précédé/aiguillé par `byte_C2BA` appartient au périmètre FAP/DPF.

### Tâches et sites conditionnés par `byte_C2BA` (échantillon représentatif)

| Zone / listing | Contenu | Statut FAP |
|---|---|---|
| `loc_A27xx`-`loc_A29xx` (153956 → 154300) | traitement **EGT `C586`**, seuils, substitution | **FAP — certain** |
| `154194`, `154214`, `154296` | aiguillages de la même tâche | **FAP — certain** |
| `153642`, `153689`, `153899` | sélection de la source de température | **FAP — certain** |
| `162278`-`162601` | compteurs **`byte_D794`**, `word_D79E` | **FAP (supervision)** |
| `163747`-`163938` | état **`byte_D7B8`**, courbes `191E`/`1922` | **FAP (états de régénération)** |
| `166440`-`166500` | **`word_D7EE`**, **`byte_D7EC`** (drapeaux de demande) | **FAP** |
| `134025`, `134333`, `139634`, `139937`, `140133`, `140629`, `140679`, `142353`, `142408`, `142531` | chaînes de mesure/estimation amont | à vérifier une par une |

### Le bloc de supervision FAP — variables `0xD7xx` (~30 variables)

| Variable | Références | Rôle déduit |
|---|---|---|
| `word_D7AA` | 27 | grandeur principale de supervision (charge/contre-pression ?) |
| `word_D756` | 27 | idem (jumeau) |
| `byte_D7A8` | 23 | état / index |
| `byte_D7BA`, `byte_D7BF`, `byte_D7C4`, `byte_D7C9`, `byte_D7CE` | ~21 chacun | **états et compteurs du cycle de régénération** |
| `byte_D7B8` | 17 | **mode de régénération** (bit 0 → choix de courbe sur `C586`, bit 1 → état, bit 3 → verrou) |
| `byte_D794` | 4 | compteur d'événements (incrémenté/décrémenté) |
| `word_D792` | — | **temporisation** de seuil (`sub #1` → drapeau) |
| `word_D7B2` → `word_D294` | — | sortie de **courbe de correction** indexée par `C586` |
| `word_D7EE`, `byte_D7EC` | 5 | **demande de régénération** (remis à zéro sous condition de température) |

---

## 7. Le point de jonction avec l'injection : `word_C69E` et `word_C77C`

C'est ici que le FAP **doit** toucher les post-injections. Voici ce qui est **prouvé** :

```asm
; sub_B35B6 (régulateur), fin de routine :
loc_B5DDA:  cmp  r9, word_C690
            jmpr cc_SGE, loc_B5DE4
            mov  r6, r9
            ...
loc_B5DE8:  mov  word_C69C, r6          ; plafonné par word_C690
            mov  word_C69E, r9          ; ← TERME ADDITIF BRUT
```

```asm
; seg014, EA 0xACFC6 :
mov  r4, word_C6BA                      ; quantité principale (étape 6)
add  r4, word_C69E                      ; + terme additif
mov  word_D844, r4 / mov word_D304, r4
mov  r5, word_C77C                      ; ← incrément
if C77C > 0 : D844 += C77C (saturation 0xFFFF)
else         : D844 += C77C (saturation 0)
...
mov  r12, word_147C / r13 = word_C91C / r14 = word_D844
calls 0, unk_1D50                       ; CARTE (régime × quantité totale) → word_D846 / word_D302
unk_20F6(word_19E8, word_D846, word_D84A) → word_D848 → word_C4CE
```

Et l'origine de `word_C77C` — **tâche `0x10E`** (EA `0xAC5xx`) :

```asm
word_C940 = word_C60A
word_C908 = word_C3D2                   ; ← TEMPÉRATURE
unk_1D36(word_19BA, word_C940) → r4
unk_1D36(word_19BC, word_C908) → r4
r5 = somme des deux
mov  word_C77C, r5                      ; ← SOMME DE DEUX COURBES, dont une en TEMPÉRATURE
unk_1D36(word_19C0, C908) → word_C97A, word_C760
unk_1D36(word_19BE, C908) → word_C752
```

### Ce que cela établit

| Fait | Preuve |
|---|---|
| Il existe **un terme de quantité additif** (`word_C69E`) qui s'ajoute à la quantité principale | `add r4, word_C69E` (6 sites) + `word_D844 = C6BA + C69E` |
| Ce terme est **modulé par une correction dépendant de la température** (`word_C77C` = somme de 2 courbes 1-D, l'une indexée par `C3D2`) | tâche `0x10E` |
| La **quantité totale** (`D844`) est ensuite l'axe Y d'une **carte (régime × quantité)** | `unk_1D50(word_147C, …)` |
| Le tout est **borné** (`C690` pour `C69C`, saturation pour `D844`) | `sub_B35B6` |

### Ce qui n'est **pas** prouvé (constat négatif honnête)

* **Aucune seconde quantité d'injection indépendante** n'a été trouvée (pas de variable « quantité post » distincte avec sa propre carte et son propre timing). `word_C69E` est un terme **additif** à la quantité principale, pas une injection séparée.
* Le **lien causal FAP → `word_C69E`** n'est pas démontré dans cette moitié de flash : la chaîne `byte_C2BA` (FAP) et la chaîne `word_C69E` (quantité) ne se croisent pas explicitement dans l'image. Elles peuvent se croiser **dans la moitié basse absente**.

C'est le point le plus important à vérifier sur banc : **est-ce que `word_C69E` change d'état quand `byte_D7B8` (mode régénération) bascule ?** Un point d'arrêt simultané sur `loc_B5DE8` (`word_C69E`) et sur `loc_A8354` (`byte_D7B8`) répond en une seule régénération forcée.

---

## 8. Synthèse : périmètre FAP/DPF identifié

| Élément | Statut | Preuve |
|---|---|---|
| **EGT `C586`** | **prouvé** (température gaz d'échappement, axe + courbes) | 8 sites, axes 100–600 °C, courbes `0xE5F98`/`0xE5FC0`/`0xE639A` |
| **`D5A2`** | **prouvé** (valeur publiée, axe 200–300 °C, table neutre) | 1 écriture / 0 lecture, `0xEBA84` |
| **Chaîne de mesure ADC → table `0x0F864`** | **prouvé** (thermistor non linéaire) | EA `0xBFF3A`+ |
| **CTP vs CTN** | **non tranchable** depuis l'image | table en mémoire basse absente |
| **Porte d'activation FAP** | **prouvé** : `byte_C2BA = [word_141C+27h]` | 63 références |
| **Bloc de supervision `0xD7xx`** | **prouvé** (états, compteurs, temporisations) | ~30 variables, 10–27 refs chacune |
| **Terme additif de quantité `C69E` + correction T° `C77C`** | **prouvé** (existence et sommation) | `sub_B35B6`, EA `0xACFC6`, tâche `0x10E` |
| **Post-injection proprement dite** | **non localisée** | aucune quantité indépendante |

---

## 9. Prochaines étapes

1. **Suivre `word_C396`** (sortie de la sélection de température FAP) : elle n'est pas relue dans l'image ⇒ chercher son usage dans la moitié basse, ou via le bloc de diagnostic `0xBD00`/`0xDF00` (étape 6) qui recopie des variables pour le lecteur de défauts.
2. **Décoder les courbes de `C586`** : `word_191E`, `word_1922` (les deux modes de `byte_D7B8`), `word_1950`, `word_18A4` — ce sont les **lois de régénération** (seuil d'entrée, seuil de sortie, dosage).
3. **Vérifier la jonction FAP → quantité** par point d'arrêt (cf. §7).
4. **Chercher les variables de contre-pression FAP** : le 4HX FAP possède un **capteur de pression différentielle** ; il devrait apparaître comme un tag ADC (`0xD0xx`) avec une courbe de conversion → c'est la mesure qui déclenche la régénération. Piste : `word_D048` (brut ADC, tag) et ses courbes.
5. **Exploiter l'inventaire 1-D** (`courbes_1D_datensatz.csv`, 104 courbes) : recouper les 46 courbes thermiques avec les descripteurs utilisés dans le code (`word_191E`, `word_1922`, `word_1950`, `word_18A4`, `word_19BA`-`word_19C0`…) pour nommer chaque loi de correction, et isoler celles qui n'apparaissent que sous `byte_C2BA` (⇒ FAP).
