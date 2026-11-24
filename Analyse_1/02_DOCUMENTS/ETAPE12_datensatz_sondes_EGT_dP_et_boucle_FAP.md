# ÉTAPE 12 — La clé d'adressage du Datensatz, les 21 voies de mesure, les deux EGT, le dP et la boucle FAP

> Toutes les preuves sont des **numéros de ligne de `clean.asm`** ; les adresses de calibration sont en **EA = offset BIN + 0x80000** et ont été relues dans `edc.bin`.
> Artefacts joints : `capteurs_ADC_et_chaines_de_mesure.csv`, `table_pointers_datensatz_0E1400.csv`.

---

## 0. Résumé — six résultats, dont une correction

| # | Résultat | Preuve |
|---|---|---|
| 1 | **L'adressage est résolu** : une adresse 16 bits C166 = `(DPP[n] << 14) OR (a & 0x3FFF)` avec `n = a >> 14`. Le **Datensatz est une banque de 48 KB** chargée dans DPP0/DPP1/DPP2 = `0x38 / 0x39 / 0x3A` ⇒ `0xE0000 / 0xE4000 / 0xE8000` | l.199533 à 199543 |
| 2 | **Le Datensatz existe en deux exemplaires identiques** : `0xE0000–0xEBFFF` et `0xF0000–0xFBFFF` (14 octets de différence = identifiant + CRC). La sélection se fait par `DPP0/1/2 = 0x3C/0x3D/0x3E` | l.111724-111728, l.112892-112896 |
| 3 | **Le Datensatz porte sa propre table de pointeurs à `0xE1400`** (1 304 mots = offsets 16 bits) et **la RAM `0x1400–0x19FF` en est la copie** ⇒ tous les `word_14xx…word_19xx` ont une adresse EA. **666 pointeurs décodés** | §3 + CSV |
| 4 | **Le « tag » est l'adresse RAM de la variable attachée** : chaque table commence par un mot `0xC3xx…0xD0xx` ; c'est prouvé par le code qui écrit le résultat dans exactement cette adresse | l.212783/212844 (`mov word_D04A, r9`) |
| 5 | **`word_18F6` et `word_1952` sont décodés numériquement** : consignes de température de régénération **399 / 300 / 200 °C**, rampe **50** par pas depuis **85 °C**, fenêtre de combustion de suie **300 → 650 °C** | §9, §10 |
| 6 | **Correction de l'étape 11** : `0xD066` n'est **pas** le meilleur candidat dP — sa loi de conversion est **cubique** (typique d'un débitmètre à fil chaud). Le circuit du dP est néanmoins identifié, et il est bien alimenté par cette voie (§8) | §8 |

---

## 1. L'adressage, enfin complet

### 1.1 Le mécanisme C166

Les quatre *Data Page Pointers* découpent l'espace en pages de 16 KB. Une adresse « near » de 16 bits sélectionne le pointeur par ses **deux bits de poids fort** et utilise les **14 bits restants** comme offset :

```
adresse = (DPP[a >> 14] << 14) | (a & 0x3FFF)
```

**Preuve directe** — l'initialisation du calculateur :

```
96439:  mov DPP0, #0        ; page 0x00000  (RAM interne)
96440:  mov DPP1, #0
96442:  mov DPP2, #2        ; page 0x08000
96443:  mov DPP3, #3        ; page 0x0C000  (RAM interne haute / SFR)
```

et les changements de page explicites : `mov DPP0, #22h` (page **0x88000**, l.96530 — c'est là qu'est la chaîne `'TSW V2.31 071099 1217 C2/ESB/G40'`), `#0Ah` (0x28000), `#09h` (0x24000), `#04h` (0x10000), `#3Ch` (0xF0000), `#44h` (0x110000).

Conséquence pratique : **`mov r9, #0F864h` (l.212834, 205062) n'est pas une adresse de calibration** mais `0xF864` avec `DPP3 = 3` ⇒ `0xC000 | 0x3864` = **`0xF864` en RAM interne** — la table des mesures brutes (§5.2).

### 1.2 La banque de calibration et son basculement

```
199532:  mov     r10, #0
199533:  mov     r11, #38h              ; page 0x0E0000
199535:  mov     word_C1DA, r4          ; <- DPP0 sauvegarde en RAM
199536:  mov     DPP0, r4
199539:  mov     DPP1, r5               ; 0x39 -> 0x0E4000
199542:  mov     word_C1DC, r5          ; <- DPP2 sauvegarde en RAM
199543:  mov     DPP2, r5               ; 0x3A -> 0x0E8000
199544:  calls   0Bh, sub_BCEBE         ; vérification / validation du Datensatz
```

Le second jeu de pages est installé **exactement de la même manière** avec `0x3C/0x3D/0x3E` (page `0x0F0000`) :

```
111724:  mov DPP0, #3Ch     ; 0x0F0000
111726:  mov DPP1, #3Dh     ; 0x0F4000
111728:  mov DPP2, #3Eh     ; 0x0F8000
```
(idem l.112892-112896, l.404059 à 405014)

Un troisième jeu `0x44/0x45/0x46` = `0x110000/0x114000/0x118000` (**hors de notre dump**) est installé l.112871-112875 : c'est probablement le Datensatz de l'autre variante de software, dans l'autre moitié de la mémoire.

Et surtout, **chaque accès à la calibration restaure les pointeurs de page** depuis la RAM :

```
125397:  scxt DPP0, word_C1DA
125398:  scxt DPP2, word_C1DC
```
(également l.125427-125428, l.125456-125457)

⇒ C'est **la** réponse à la question de fond posée depuis l'étape 8 : une donnée de calibration est désignée par le couple **(numéro de page DPP stocké dans `word_C1DA`/`word_C1DC`, offset 16 bits)**. L'« identité » de la donnée n'est donc ni dans le code (aucun immédiat de calibration n'existe : `0[EF]xxxxh` → **0 occurrence** dans tout `clean.asm`), ni dans un pointeur absolu : elle est **dans la donnée elle-même**, via son entête.

---

## 2. Anatomie du Datensatz

| Élément | Valeur | Où |
|---|---|---|
| Taille | **0x C000 = 48 KB** | `0xE0000–0xEBFFF` |
| En-tête | `55 55 00 00  02 92 24 00` puis **151 pointeurs far 32 bits** (segment `0x9…0xD` : `0x00099AB8`, `0x000A1048`, `0x000D030A`…) vers du code | `0xE0000` |
| Zone `0xEC000–0xEFFFF` | **vide** (`C3 C3 C3…`) en banque A ; en banque B (`0xFC000`) on trouve le secteur de boot | — |
| Identifiant de variante | `75vGB075WF2S010384` + code `__NWGDWPF1` (banque A) / `__NFGDWPF1` (banque B) | `0xEBF04`, `0xFBF04` |
| Somme de contrôle | `94 C7` + 4 octets : `DD 35 D9 5B` (A) / `20 5C 77 AF` (B) | `0xEBCFA`, `0xFBCFA` |
| Nombre d'octets différents entre les deux copies | **14** | `0xE0FF6-0xE0FFF`, `0xE434D`, `0xEBCFC-0xEBCFF`, `0xEBF1B` |
| Nombre de mots de calibration identiques | 24 576 | comparaison byte à byte 0xE0000↔0xF0000 |

**Conclusion forte** : `0xE0000` et `0xF0000` ne sont **pas deux jeux de données différents** (l'hypothèse « 14 147 octets de différence » de l'étape 9 mesurait en réalité `padding` contre `boot`). Ce sont **deux copies redondantes du même Datensatz** — d'où `byte_E5AC` (bits `0x01/0x10/0x20`, l.112865-112902) qui mémorise **quelle copie est active**, et `sub_BCEBE` (l.198814) qui la valide.

La différence `NWG` / `NFG` (1 caractère) et les deux CRC distincts sont cohérents avec deux programmations successives : l'outil de flash a écrit l'identifiant *après* la copie.

---

## 3. La table de pointeurs du Datensatz — `0xE1400`

En cherchant les runs de mots, on trouve à **`0xE1400`** une table de **1 304 offsets 16 bits** croissants :

```
0E1400: 100A 101E 1026 104A 106E 1082 10A6 10BA 10DE 10F2 10F4 10FC 1106 1112 111E 1148 …
```

Chaque entrée pointe sur un en-tête de table. Vérification sur les trois premiers :

| Entrée | Cible | Contenu |
|---|---|---|
| `0xE1400` = `0x100A` | `0xE100A` | `C42E 0008 00C8 0190 0258 04E2 06D6 08CA` → courbe sur C42E (régime), 8 points |
| `0xE1402` = `0x101E` | `0xE101E` | `C42E 0002 028A 04B0` → 2 points |
| `0xE1442` = `0x1E30` | `0xE1E30` | `C42E 0010 02D5 …` → 16 points |

**Et la RAM `0x1400–0x19FF` contient les mêmes valeurs aux mêmes offsets.** Trois preuves indépendantes :

1. `word_191E` → offset `0x5F9C` → `0xE5F9C` = `C586 0002 146F 2027 0064 0C80` — et le code fait `mov r12, word_191E / mov r13, word_C586 / calls unk_1D36` (l.163860-163862) ⇒ courbe **sur la température gaz**. ✔
2. `word_1922` → `0xE5FC0` = `C586 0002 146F 221B 0064 7FFF` — appelée aussi sur `word_C586` (l.163868). ✔
3. `word_1950` → `0xE639A` = `C586 0008 …`, et **le mot suivant exactement `+0x24` (= 4 + 8×4 octets) est `word_1952` = `0x63BE`** ⇒ `0xE63BE`. Le code enchaîne `unk_1D36(word_1950, C586)` puis les seuils de `word_1952` (l.166434-166485). ✔

**Artefact** : `table_pointers_datensatz_0E1400.csv` — 666 lignes `symbole_RAM;offset;EA_cible;nature;detail;nb_usages`. Répartition : **132 courbes**, **32 cartes 2-D**, **502 blocs de paramètres**.

---

## 4. Le tag = l'adresse RAM de la variable attachée

Le format prouvé à l'étape 11 (`<tag><n><n axe↑><n sorties>`, 4 + 4n octets) prend tout son sens ici : **le premier mot n'est pas un numéro, c'est une adresse RAM**.

Preuve par le code — la chaîne de conversion de la voie EGT n° 2 :

```
212834:  mov     r9, #0F864h        ; table des mesures brutes (RAM interne 0xF864)
212836:  calls   0Ch, sub_C4AAE     ; extraction + contrôle de validité
212838:  mov     r1, word_1506      ; -> 0xE30EC = la courbe de linéarisation
212839:  calls   0Ch, sub_C66EA     ; filtrage + linéarisation
212844:  mov     word_D04A, r9      ; <<< résultat écrit dans word_D04A
```
et l'en-tête de `0xE30EC` (cible de `word_1506`) : `4A D0 10 00 …` = **`0xD04A`**.

⇒ La table **annonce sa destination**. Le mot d'en-tête est à la fois *tag* (identité fonctionnelle) et *adresse cible*. C'est exactement le modèle « l'adresse porte identité + type + tag » : **banque (DPP) + offset (pointeur) + tag (mot d'en-tête)**.

Le même mécanisme sert d'**entrée** pour les courbes : `C42E` (régime), `C586` (température gaz), `C3BA`/`C3D2` (températures), `C60A`, `C7C2`, `D1B6`, `D1F4`… sont les variables **lues** (axes).

---

## 5. Inventaire des 21 chaînes de mesure (entrées analogiques)

### 5.1 Tableau maître (détail complet : `capteurs_ADC_et_chaines_de_mesure.csv`)

| Tâche | Voie | Descripteur | Linéarisation | Tag | n | Axe ADC | Sortie | RAM physique | Copie travail | Famille |
|---|---|---|---|---|---|---|---|---|---|---|
| `0x302` | 0 | `0xE363A` | `0xE35D6` | partagé | — | — | — | `C3D0` | — | bloc partagé (4 voies) |
| `0x304` | 1 | `0xE35B8` | `0xE35D6` | partagé | — | — | — | `D06E` | `C3CE` | bloc partagé |
| `0x306` | 2 | `0xE301E` | **`0xE302A`** | `D044` | 4 | 20 / 102 / 921 / 1003 | 500/500/2500/2500 | **`D044`+`D046`** | `C362` | validité ratiométrique **+ paire redondante** |
| `0x308` | 3 | `0xE349C` | **`0xE34A8`** | `D060` | 4 | 20 / 205 / 972 / 1023 | 133/133/2500/2500 | `D060`+`D062` | `C378` | validité ratiométrique |
| `0x30A` | 4 | `0xE34EA` | **`0xE34F6`** | `D066` | 12 | 192 → 1064 | **55 → 7739** | `D066` (+`D068`/`D06A`) | **`C3B6`+`C37A`** | **loi cubique** (débitmètre) |
| `0x30C` | 5 | `0xE1106` | `0xE2FB2` | `D03A` | 2 | 485 / 970 | 600 / 1200 | `D03A` | `C360` | tout-ou-rien |
| `0x30E` | 6 | `0xE353C` | **`0xE3548`** | `D06C` | 16 | 40 → 962 | 4031 → 2331 | `D06C` | **`C3BA` → `C904`** | **CTN −40…+130 °C** |
| `0x310` | 7 | `0xE3436` | **`0xE3444`** | `D05E` | 10 | 32 → 969 | 3931 → 2331 | `D05E` | **`C3B0` → `C900`** | **CTN −40…+120 °C** |
| `0x312` | 8 | `0xE306A` | **`0xE3076`** | `D048` | 16 | 32 → 1023 | **11731 → 2849** | `D048` | **`C366` → `C394`** | **EGT mesurée : +12…+900 °C** |
| `0x314` | 9 | `0xE1112` | **`0xE30EC`** | `D04A` | 16 | 10 → 991 | **3731 → 11381** | `D04A` | `C368` | **2ᵉ EGT (CTP) : +100…+865 °C** |
| `0x318` | 11 | `0xE3834` | **`0xE3842`** | `D084` | 24 | 42 → 1002 | 4032 → 2331 | `D084` | **`C3D2` → `C908`** | **CTN −40…+130 °C (24 pts)** |
| `0x31A` | 12 | `0xE3774` | `0xE35D6` | partagé | — | — | — | `D080` | `C388` | bloc partagé |
| `0x31C` | 13 | `0xE37B8` | `0xE35D6` | partagé | — | — | — | `D082` | `C38A` | bloc partagé |
| `0x31E` | 14 | `0xE3162` | **`0xE316E`** | `D04C` | 2 | 51 / 972 | 667 / 20667 | `D04C` | `C36A` | plausibilité (paire de seuils) |
| `0x320` | 15 | `0xE37FC` | **`0xE3808`** | `C3AA` | 2 | 57 / 340 | 1000 / 6000 | `C370` | — | grandeur calculée |
| `0x322` | 16 | `0xE2FF4` | **`0xE3000`** | `D03C` | 2 | 0 / 788 | 0 / 700 | `D042`+`D040` | — | voie analogique double |
| `0x326` | 18 | `0xE31AC` | **`0xE31B8`** | `D052` | 4 | 20/102/921/1003 | 0/0/1000/1000 | `D04E`+`D050` | `C36C` | validité 0,5–4,5 V |
| `0x406` | 6 | `0xE3688` | `0xE3694` | `D072` | 2 | 2 / 4 | 0 / 0 | `D072` | `C382` → `C906` | **compteur** (nibble/octet), pas un capteur |
| `0x408` | 8 | `0xE320C` | **`0xE3218`** | `D054` | 2 | 0 / 1023 | 0 / **5000** | `D054` | `C36E` | linéaire 10 bits = 0…100 % |
| `0x602` | 2 | `0xE3250` | **`0xE325C`** | `D056` | 4 | **102 / 922** | 0/0/**15000**/15000 | `D056` | `C3CA` → `C372` | validité 0,5–4,5 V |
| `0x606` | 6 | `0xE342A` | `0xE3436` | `D05A` | 10 | 32 → 969 | 3931 → 2331 | `D05A` | `C374` → `C3AE` | 2ᵉ gamme de la sonde CTN |

### 5.2 La table des mesures brutes en RAM interne — `0xF864`

```
C4AB0:  mov  r2, [r0+#0]      ; descripteur : octet 0
C4AB4:  and  r2, #0Fh         ; bits 3..0 = variante
C4AB6:  cmp  r9, #0F864h
C4ABC:  mov  r3, #7 / #0Fh    ; borne de la famille
C4AD0:  sub  r3, r2
C4AD2:  shl  r3, #1
C4AD4:  add  r9, r3
C4AD6:  mov  r3, [r9]         ; <<< mot de mesure
C4AE0:  mov  r4, r3
C4AE4:  shr  r4, #12          ; bits 15..12 = sélecteur de source
C4B00:  and  r5, #3FFh        ; bits 9..0 = valeur 10 bits
                                         3FFh = INVALIDE
```
et les masques `word_E19E` / `word_E1A0` = bits de canaux en défaut. Le descripteur, lui, donne `[+0] >> 4` = **numéro de voie** comparé à `byte_C21A` (l.212810-212814) et `[+8]` = valeur de remplacement.

C'est le troisième niveau d'identité : **(tâche `0x3xx`, voie `[desc+0]>>4`, variante `[desc+0]&0F`) → mot 10 bits dans `0xF864`**.

---

## 6. Les deux sondes EGT — et l'estimée

### 6.1 Les deux sondes physiques

| Sonde | Chaîne | Table | Plage | Écrit dans | Utilisation |
|---|---|---|---|---|---|
| **EGT 1 (amont filtre)** | `0x312`, voi e8 | **`0xE3076`** | **+12 → +900 °C** (axe 32→1023, sorties 11731→2849, **décroissante**) | `D048` → `C366` → **`C394`** | sélectionnée par défaut (l.153883, 153903) |
| **EGT 2** | `0x314`, voie 9 | **`0xE30EC`** | **+100 → +865 °C** (axe 10→991, 3731→11381, **croissante**) | `D04A` → `C368` | voie 2 / redondance |

**Décroissante ≠ CTN** : la pente du tableau ne donne que le sens du *diviseur*. `D048` et `D04A` sont **toutes deux des CTP** (plage 900 °C impossible pour une CTN), mais montées dans deux diviseurs différents :
- `D04A` : sonde vers la masse, tirage vers +5 V ⇒ U↑ quand T↑ ⇒ table **croissante** ;
- `D048` : sonde vers +5 V, résistance vers la masse ⇒ U↓ quand T↑ ⇒ table **décroissante**.

C'est la raison pour laquelle la « règle CTP = croissante » de l'étape 11 doit être énoncée ainsi : **CTP = loi monotone sur ±900 °C ; CTN = loi monotone sur −40…+130 °C**. Le sens seul ne suffit pas.

### 6.2 La sonde *estimée* (versions sans 2ᵉ sonde)

`word_C586` est **lu 9 fois et écrit 0 fois dans cette moitié** (l.153877, 153964, 153993, 155179, 162605, 163861, 163869, 166435, 167078). Son écriture est donc dans la **moitié basse absente** — c'est le **modèle thermique**.

Sélection à trois voies (l.153877-153890) :

```
153877:  if word_FD30+1 == 0 -> C396 = word_C394      ; mesure EGT1
153882:  if word_FD32   == 0 -> C396 = word_186A[+6]  ; valeur de remplacement calibrée
153878:                 sinon -> C396 = word_C586     ; ESTIMATION
```

⇒ **`word_C396` = la température gaz « retenue »** par le stratégie, avec dégradation automatique mesure → modèle. La bascule est pilotée par les drapeaux de défaut `word_FD30.x` / `word_FD32` (alimentés par les chemins `r3 = #84h`, codes `#10FBh`, l.153848-153860).

Les trois courbes sur `C586` (toutes dans le Datensatz, donc calibrées) :

| EA | n | Axe (K×10) | Sorties | Rôle |
|---|---|---|---|---|
| `0xE5F9C` (`word_191E`) | 2 | 5231 → 8231 (**+250 → +550 °C**) | 100 → 3200 | seuil de bascule |
| `0xE5FC0` (`word_1922`) | 2 | 5231 → 8731 (**+250 → +600 °C**) | 100 → 32767 | saturation |
| `0xE639A` (`word_1950`) | 8 | **3731 → 8531 (+100 → +580 °C)** | **7231 → 5131** (décroissante) | **correction sonde → température filtre** |

`0xE639A` transforme la mesure en une température équivalente **723 °C → 513 °C** : c'est la correction d'emplacement (la sonde est en amont, le filtre est plus froid). Cette courbe est utilisée deux fois : l.163861/163869 (avec `word_191E`/`word_1922`) et l.166434 où son résultat est comparé à `word_C584` :

```
166434:  mov  r12, word_1950
166435:  mov  r13, word_C586
166436:  calls 0, unk_1D36
166437:  mov  r9, r4
166438:  cmp  r9, word_C584
166439:  jmpa cc_SGE, loc_A9B36   ; si EGT corrigée < C584 -> pas de régénération
```

---

## 7. Eau / carburant / air : les trois CTN

| Variable | Chaîne | Table | n | Plage | Points remarquables |
|---|---|---|---|---|---|
| **`C3B0`** (`C900`) | `0x310` voie 7 | **`0xE3444`** | 10 | +120 → −40 °C | axe 32 → 969 |
| **`C3BA`** (`C904`) | `0x30E` voie 6 | **`0xE3548`** | 16 | +130 → −40 °C | pas de 10 °C exact (2331, 2431, …) |
| **`C3D2`** (`C908`) | `0x318` voie 11 | **`0xE3842`** | **24** | **+130 → −40 °C** | pas de 5 °C au-dessus de +80 °C |

Les trois sont recopiées dans le banc de travail :

```
153691:  mov r4, word_C3B0 ; mov word_C900, r4
153693:  mov r5, word_C3BA ; mov word_C904, r5
153697:  mov r4, word_C3D2 ; mov word_C908, r4
```
(et l.131274-131302 dans `sub_972CA`/`sub_972FA`)

### 7.1 Attribution — ce qui est prouvé, ce qui reste à trancher

**Prouvé** (par les axes de calibration qui consomment chaque variable) :

- **`C3D2` = la température la plus utilisée** : **≈30 courbes** ont `C3D2` en axe (dont des cartes 6×6 `C42E`×`C3D2` à `0xE3908`), avec des fenêtres typiques « actif sous +80 °C, neutre au-dessus » (`0xE3F52`, `0xE6A6A`, `0xE6B9E`). C'est la signature d'une **température de liquide de refroidissement** (démarrage à froid, fumées, EGR).
- **`C3BA`** est l'axe Y de deux cartes 2-D `régime × T` :
  `0xE38D8` = `C42E 0002 (1000, 2000)` × `C3BA 0006 (2581 → 2901 = −15 → +17 °C)` (cible de `word_15E2`) et
  `0xE39C0` = `C3BA 0002 (2531, 3331 = −20, +60 °C)` × `C60A 0002 (700, 1000)` (cible de `word_15EC`).
  Les points d'axe **très froids** indiquent une correction de démarrage/carburant.
- **`C3B0`** n'a que **4 courbes**, toutes actives **au-dessus de +60 °C seulement** (`0xE6A8E` et `0xE6BE6` : axe 3271→3931 = +60→+120 °C → sortie 0…21000). Une correction qui n'existe qu'« à chaud » est typique d'une **température d'air d'admission** (limitation de fumées) ou de **carburant** (densité).

**Non tranché** : entre `C3BA` et `C3B0` pour carburant vs air. Les deux attributions restent compatibles avec les preuves ci-dessus. Le test décisif est **le brochage** : les voies sont `AN6` (D06C/`C3BA`), `AN7` (D05E/`C3B0`), `AN11` (D084/`C3D2`). Une mesure au connecteur (ou la doc « rôle des voies ANx » du calculateur) tranche définitivement ; le code seul ne le peut pas, car les trois descripteurs ont **exactement la même structure** (`0xE3436`/`0xE353C`/`0xE3834`, blocs de 0x… identiques en forme).

---

## 8. Le capteur de pression différentielle — et la correction de l'étape 11

### 8.1 `0xD066` n'est pas linéaire : sa loi est cubique

`0xE34F6` (12 points) :

| Code ADC | 192 | 315 | 421 | 532 | 614 | 687 | 745 | 798 | 921 | 1023 | 1043 | 1064 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Sortie | 55 | 185 | 388 | 697 | 1088 | 1629 | 2225 | 2980 | 5477 | 7739 | 7739 | 7739 |

On teste un transmetteur **linéaire** (dP 0,5–4,5 V) : la pente varie de **1,1 à 22 unités par code** — ce n'est pas un capteur de pression linéaire.
On teste une loi de **fil chaud** (masse ≈ (U − U₀)³) avec U₀ ≈ 150 :

| Code | (code−150)³ | Sortie | rapport |
|---|---|---|---|
| 532 | 5,6×10⁷ | 697 | 1,25×10⁻⁵ |
| 687 | 1,5×10⁸ | 1629 | 1,06×10⁻⁵ |
| 798 | 2,7×10⁸ | 2980 | 1,10×10⁻⁵ |
| 921 | 4,6×10⁸ | 5477 | 1,20×10⁻⁵ |
| 1023 | 6,6×10⁸ | 7739 | 1,17×10⁻⁵ |

**Rapport constant à ±10 % sur 3 décades** ⇒ **la voie `0x30A` (`D066`) est un débitmètre massique à fil chaud**, pas un capteur de pression différentielle. C'est la correction à apporter à l'étape 11.

### 8.2 Mais le circuit du dP existe, et il est alimenté par cette voie

```
131394:  mov  r9, word_C3B6          ; <<< valeur de la voie 0x30A
131396:  cmp  r4, #0                 ; r4 = C42E (régime)
131397:  mov  r1, word_C080          ; compteur de distance
131400:  sub  r4, word_F91C          ; distance depuis le dernier point
131405:  cmp  r4, [word_15F0+8]      ; fenêtre de distance
131429:  mov  r13, word_C080 - F91C
131435:  mov  r12, #2710h - [word_15F0+6]
131437:  calls unk_20AC              ; pondération  (a*b/c)
131443:  mov  r13, [word_15F0+6] + r4
131447:  mov  r12, r9 ; mov r14, #2710h
131449:  calls unk_20AC              ; moyenne pondérée par la distance
131459:  mov  word_D090, r9          ; <<< D090 = valeur filtrée « sur km »
131487:  mov  r12, word_15EC         ; carte 2-D C3BA x C60A  -> 0xE39C0
131489:  mov  r13, word_C904         ; (température)
131490:  mov  r14, word_C940
131491:  calls unk_1D50
131492:  mov  r6, r4
131493:  mov  r4, word_15F0 ; mov r13, [r4]   ; 8333
131496:  calls unk_20AC              ; normalisation par le régime
131498:  mov  word_D098, r7          ; <<< D098
131504:  mov  word_D09A, r4          ; <<< D09A = mélange D098 / carte
```

Paramètres du filtre, `word_15F0` → **`0xE3AD0`** : `8333 | 3000 | 10000 | 10000 | 0 | 450 | 300 | 69`.

**Lecture** : `C3B6` (la voie `0x30A`) est moyennée **pondérée par la distance parcourue** (`C080 − word_F91C`, fenêtre `[15F0+8]`) puis normalisée par le régime (`[15F0+0]` = 8333) et mélangée à une carte `température × C60A`. C'est un **apprentissage de référence sur les kilomètres** — la signature d'un estimateur de charge (suie/cendres), pas d'une simple mesure.

Trois valeurs publiées pour le diagnostic (écrites, jamais lues dans cette moitié — « miroirs » comme `D5A2`) : **`D090` (filtré), `D098` (normalisé), `D09A` (mélangé)**.

### 8.3 Où est alors le vrai capteur dP ?

Il est dans les voies à **butée 0,5–4,5 V** (codes 102/921) — `D052`, `D056`, `D060`, `D044` — dont les tables sont des **fenêtres de validité** et non des linéarisations :

| Table | Axe | Sortie | Sens |
|---|---|---|---|
| `0xE31B8` (`D052`) | 20 / **102** / **921** / 1003 | 0 / 0 / 1000 / 1000 | « 1 » entre 0,49 V et 4,50 V |
| `0xE325C` (`D056`) | **102 / 103 / 921 / 922** | 0 / 0 / 15000 / 15000 | idem, avec 150 % d'hystérésis |
| `0xE34A8` (`D060`) | 20 / 205 / 972 / 1023 | 133 / 133 / 2500 / 2500 | fenêtre large |
| `0xE302A` (`D044`) | 20 / 102 / 921 / 1003 | 500 / 500 / 2500 / 2500 | **deux sorties** ⇒ paire redondante `D044`/`D046` |

La **valeur** de ces capteurs transite par `D054` (linéaire `0…1023 → 0…5000` = 0…100 % de pleine échelle, `0xE3218`). **Le dP est donc l'une de ces voies** : `D054`/`D056` (tâches `0x408`/`0x602`) ou `D052`/`D050` (`0x326`). Le choix définitif demande le brochage — mais la **fonction** qui consomme le dP est, elle, entièrement identifiée (§8.2).

---

## 9. `word_18F6` décodé — durées et consignes de régénération

`word_18F6` = **`0x5368`** → bloc **`0xE5368`** (18 accès, tous `mov r4, word_18F6` puis `[r4+#xx]`).

| Offset | Valeur | Interprétation | Preuve |
|---|---|---|---|
| `+00` | **`0x004D`** = `0100 1101` | **masque d'options** (bit 0 testé) | l.163006-163010 `mov r13,[r4] ; mov r4,#1 ; and r4,r13` |
| `+02` | **1200** | durée état 0 → 1 | l.163256 |
| `+04` | **2400** | durée état 1 → 2 | l.163300 |
| `+06` | **300** | durée état 2 → 3 | l.163322 |
| `+08` | **600** | durée état 3 → 4 | l.163344 |
| `+0A` | **3000** | durée état 5 → 3 | l.163497 |
| `+0C` | **4** | fin d'état 4 (retour à 0) | l.163360 |
| **`+0E`** | **3990** | **consigne 399 °C — état 1** | l.163498 |
| **`+10`** | **3000** | **consigne 300 °C — état 3** | l.163506 |
| **`+12`** | **2000** | **consigne 200 °C — état 5** | l.163514 |
| **`+14`** | **50** | **diviseur de rampe** (K×10 par pas) | l.163550-163555 `(consigne − D7AE) / 50` |
| **`+16`** | **850** | **valeur initiale de rampe = 85 °C** | l.163532-163533 `D7AE = D270 = 850` |
| `+18` / `+1A` | 5000 / 5000 | limites hautes | l.163589, 163645 |
| `+1C` / `+1E` | 30 / 150 | compteurs / temporisation | l.163619, 163660 |

Extrait clé — la consigne dépend de **l'état demandé `byte_C31A`** :

```
163487:  movb rl4, byte_C31A
163489:  cmpb rl4, #1  -> loc_A8018 : r7 = [word_18F6+0Eh]   ; 3990 = 399 °C
163491:  cmpb rl4, #3  -> loc_A802A : r7 = [word_18F6+10h]   ; 3000 = 300 °C
163493:  cmpb rl4, #5  -> loc_A803C : r7 = [word_18F6+12h]   ; 2000 = 200 °C
163500:  orb  byte_C335, #40h        ; drapeau « consigne active »
163526:  mov  word_D26C, r7          ; <<< consigne de température
```

⇒ La régénération a **trois paliers thermiques (399 / 300 / 200 °C)**, une **rampe de montée de 50 K** par pas depuis **85 °C**, et une machine à 6 états dont les temporisations valent 1200 / 2400 / 300 / 600 / 3000 / 4 unités. L'unité de temps est celle de l'appel de la tâche `0x12C` : si la tâche est à 10 ms, les durées sont **12 s / 24 s / 3 s / 6 s / 30 s / 40 ms** — cohérent avec un cycle de chauffe de FAP. (À confirmer par la table de cadencement ; c'est la seule inconnue de ce bloc.)

---

## 10. `word_1952` décodé — fenêtre de combustion et jeux de seuils

`word_1952` = **`0x63BE`** → bloc **`0xE63BE`**, situé **immédiatement après** la courbe `0xE639A` (même base + 0x24). Contenu utile :

| Offset | Valeur | Sens (prouvé par le code) | Preuve |
|---|---|---|---|
| `+0A` | 7000 | | |
| `+12` | 10000 | 100 % | |
| `+16` | 9000 | | |
| `+18` | 2931 / `+1A` 2881 | **+20 °C / +15 °C** (temps) | |
| `+1C` | 3731 | **+100 °C** | |
| `+22` | 1000 | | |
| **`+2A`** | **5731** | **borne basse de la fenêtre = 300 °C** | l.166370-166372 `cmp [r4+2Ah], word_C584` |
| **`+2C`** | **9231** | **borne haute de la fenêtre = 650 °C** | l.166381 |
| `+2E` | 0 | gain appliqué à la progression | l.166427 |
| `+30` | 10000 | 100 % | |
| `+32`/`+33` (octets) | **0 / 0** | **jeu B** : `word_D7EE = 0`, `byte_D7EC = 0` | l.166465, 166468 |
| `+36` / `+37` (octets) | **200** / **0** | seuil de comptage (jeu A) | l.166455 |
| **`+38` (octet)** | **110** | **durée max de régénération = 110 s** (jeu A) | l.166458 |
| **`+39` (octet)** | **50** | seuil de comptage (jeu C) | l.166475 |
| **`+3A` (octet)** | **254** | **durée max = 254 s** (jeu C) | l.166478 |
| `+3C` | `0xC300` (mot) | **tag** : renvoi vers une autre variable (`byte_C2FF`/`C300`) | |

**Calcul de la progression de combustion** (l.166370-166432) — c'est le cœur de la boucle :

```
r5 = [1952+2Ah]  (300 °C)
if r5  >  C584:  progression = 0
elif [1952+2Ch] (650 °C) < C584: progression = 10000      ; 100 %
else:            progression = (C584 − 3000) / (6500 − 3000) × 10000
puis             word_D2BE = progression × [1952+2Eh] / 10000
```

⇒ **`C584` = la température de référence de combustion**, et **`word_D2BE` = la rampe 0…100 % de la régénération**. C'est la variable de sortie du contrôleur — celle qui pilote la post-injection.

**Trois jeux de seuils** sélectionnés par l'état des voies de température gaz (l.166450-166485) :

| Condition | Seuil `word_D7EE` | Durée `byte_D7EC` |
|---|---|---|
| `FD30+1 = 0` et `FD32 = 0` (les 2 voies gaz OK) | 0 | 0 |
| `FD30+1 = 0`, `FD32 ≠ 0` (une voie en défaut) | 0 | **110 s** |
| `FD30+1 ≠ 0` et `FD32 ≠ 0` (les 2 en défaut) | **50** | **254 s** |

C'est la stratégie de repli : **plus le diagnostic est dégradé, plus la régénération est longue et plus le seuil de comptage est élevé**.

⚠️ Subtilité d'implémentation à noter : le bloc est adressé **en octets et en mots sans alignement** (`[+37h]` et `[+38h]` sont des octets, alors que `+38h` est aussi un mot `0x326E`). Toute modification de calibration doit respecter **les deux lectures**.

---

## 11. La boucle FAP, maintenant complète de bout en bout

```
                    ┌──────────────── ENTREES ────────────────┐
 EGT 1  D048 ──0xE3076──► C366 ─► C394 ─┐
 EGT 2  D04A ──0xE30EC──► C368          ├─► C396 (l.153877-153890) ─► word_C586
 modèle C586 (moitié basse) ────────────┘        ▲
 voie 4 D066 ──0xE34F6──► C3B6/C37A ─► filtre km (word_15F0=0xE3AD0) ─► D090
                                        └─► normalisation ─► D098 ─► D09A (suie)
 T liquide  C3D2 (0xE3842) ─► C908
 T carb.    C3BA (0xE3548) ─► C904
 T air      C3B0 (0xE3444) ─► C900
 régime    C42E (axis tag) ─► C91C
                    └─────────────────────────────────────────┘
                                     │
            demande : byte_C316 bit 0  ◄── calculée en l.166490-166600
                                     │   (comparaison EGT corrigée 0xE639A ↔ C584)
            inhibiteur : byte_C2FA bit 3 (l.166481-166484)
                                     │
            seuils : word_1952 = 0xE63BE  (fenêtre 300–650 °C, durées 110/254 s)
            rampe  : word_D2BE  ◄── progression 0…100 %
                                     │
            machine à 6 états : byte_D7A8 (0…5), sauts [0x0A04], tempo word_D7AA
            durées : word_18F6 = 0xE5368 (1200/2400/300/600/3000/4)
            consignes : word_D26C = 399 / 300 / 200 °C  (rampe 50 depuis 85 °C)
                                     │
            état demandé : byte_C31A  ← **écrit dans la moitié basse absente**
                                     │
            post-injection : word_D844 = C6BA + C69E ± C77C  (EA 0xACFC6)
                             → unk_1D50(word_147C=0xE22B2, C91C, D844) → word_C4CE
```

Le seul chaînon qui manque encore est donc **matériellement absent du dump** : `byte_C316 → byte_C31A`. Ce n'est pas une lacune d'analyse.

---

## 12. Ce qui reste ouvert, et comment le fermer

| Question ouverte | Pourquoi | Comment la fermer |
|---|---|---|
| Seuil **kilométrique** de régénération | `C080` (compteur de distance) est utilisé dans le filtre dP, mais aucune comparaison `C080 > seuil` n'apparaît dans cette moitié | dump de la moitié `0x00000–0x7FFFF` ; le seuil est très probablement en EEPROM, comme le kilométrage |
| **`C316 → C31A`** | écriture/lecture séparées par la frontière du dump | idem (moitié basse) |
| **Unité de temps** des durées `word_18F6` | dépend de la cadence de la tâche `0x12C` | table de cadencement du scheduler, ou mesure sur banc |
| **Attribution eau / carburant / air** | descripteurs des 3 CTN structurellement identiques | brochage AN6 / AN7 / AN11 du calculateur |
| **Quelle voie est le dP** | 4 voies à butée 0,5–4,5 V indiscernables par le code | brochage + mesure : dP = 0 mbar contact mis |
| `0xE35D6` (bloc partagé par `D06E`, `D070`, `D080`, `D082`) | structure ni courbe ni carte : `0A 00 0A 00 05 00 FF FF …` | à décoder : probablement des paramètres d'adaptation par voie |

---

### Récapitulatif des artefacts produits

| Fichier | Contenu |
|---|---|
| `analyse_edc15c2_4hx/ETAPE12_datensatz_sondes_EGT_dP_et_boucle_FAP.md` | ce document |
| `analyse_edc15c2_4hx/capteurs_ADC_et_chaines_de_mesure.csv` | 21 chaînes : tâche, voie, descripteur, linéarisation, tag, axes, RAM, copies, chemins de défaut |
| `analyse_edc15c2_4hx/table_pointers_datensatz_0E1400.csv` | 666 pointeurs `word_14xx…word_19xx` → EA de calibration, nature (courbe / carte / bloc) |
