# ÉTAPE 14 — Le dP : ce qui se passe réellement. La pression d'admission, le rapport engagé, et la re-vérification des trois températures

> **ERRATUM (étape 15)** — Deux points de ce document sont **inexacts** :
> (1) le tableau « identifiant → adresse » du §2.4 était reconstitué à vue et **faux** ;
> (2) le §3.1 faisait de `byte_D20C` le **rapport engagé**, alors que `FD04.0`/`FD04.2` viennent
> d'une **fenêtre de température d'air** et d'un **bit d'entrée**, et sélectionnent des **taux
> d'intégration** — pas un ratio régime/vitesse. Voir `ETAPE15_...md` §1.2, §2.2, §2.3 et §6.
> Le reste (§1, §4, §5) est confirmé.

Suite de `ETAPE13_trois_temperatures_MAF_distance_et_dP.md`.
Preuves = **numéros de ligne de `clean.asm`** + **adresses en zone de calibration** (`0xE0000–0xEBFFF`).

---

## 0. Résultat en huit lignes

| # | Résultat | Statut |
|---|---|---|
| 1 | **La fonction maîtresse du chemin d'air est localisée et lue** : seg014 `0xA3E00–0xA4A00`, calibrée par le bloc **`word_18C2` = `0xE4F56`**. | prouvé (§1) |
| 2 | **La chute de pression est MODÉLISÉE, pas mesurée** : `C5BA = P_amb + k·(débit)²/P_amb` = inversion de l'équation d'orifice (l. 156510-156536). | **prouvé** (§2.1) |
| 3 | **La pression d'admission, elle, EST mesurée** : `D04C` = **667 … 2066,7 mbar** (capteur 2,5 bar absolu, 0,5–4,5 V), loi `0xE316E`. Le ratio `D202 = 1000·C944/C5BA` a pour axe **1000…3000 = 1,00…3,00** — cohérent. | **prouvé** (§2.2) |
| 4 | **Le dP n'existe nulle part sous forme de mbar** : les 4 voies 0,5–4,5 V ne produisent que des drapeaux, et **aucune n'a de lecteur direct** (`D044…D082` : 0 occurrence en lecture). | **prouvé (négativement)** (§2.3) |
| 5 | **Nouveau : l'interface de mesure diagnostique** = `sub_88084`, table **identifiant → adresse RAM** (`#0D896`, `#0D594`, `#0D63E`, `#0C564`…). C'est par là que passent les grandeurs que le logiciel n'exploite pas en interne. | **prouvé** (§2.4) |
| 6 | **Le rapport engagé existe** : `byte_D20C` ∈ {1,2,3}, construit par les bits `r8.3/.4/.5` (l. 156657-156700, écriture l. 156774-156786). | **prouvé** (§3.1) |
| 7 | **La vitesse instantanée n'est pas dans ce demi-programme** ; **`word_F91C` est une base de temps, pas une distance** → **erratum de l'étape 13**. | prouvé / erratum (§3.2, §4) |
| 8 | **Les trois températures re-vérifiées par un critère neuf (les axes des cartes)** : air **prouvé 3×**, **LDR prouvée** (axe `3841…3951` = **+111…+122 °C**), carburant **probable** (axe `−10…+102 °C`). | §4 |

---

## 1. La fonction maîtresse du chemin d'air

Elle est appelée par la tâche de fond et se reconnaît à son **bloc d'état passé dans `r0`** (accès
`[r0+18h] … [r0+74h]`) et à son **bloc de calibration `word_18C2` = `0xE4F56`** (73 usages).

**Initialisation** (l. 156140-156262) — c'est une mine : elle donne la liste des champs de `0xE4F56`.

| ligne | effet | lecture |
|---|---|---|
| 156141-156147 | `byte_D704 ← [18C2+7]`, `byte_D707 ← [18C2+8]`, `byte_D705 ← [18C2+25h]`, `byte_D706 ← [18C2+26h]` | temporisations / limites de compteurs |
| 156206-156208 | `FD04.0 = 0`, `FD04.2 = 0`, **`byte_D20C = 0`** | remise à zéro de la détection de rapport |
| 156214-156228 | `D724 = D74A = [18C2+4Ch]`, `D728 = D74C = [18C2+46h]` | deux valeurs d'initialisation (paires redondantes) |
| 156236-156240 | `byte_D708 ← [18C2+3Ch]`, `byte_D709 ← [18C2+3Dh]` | compteurs d'apprentissage |
| 156245-156252 | `byte_D70A ← [18C2+9]`, `byte_D70B ← [18C2+0Ah]`, `byte_D70C ← [18C2+1Fh]`, `byte_D70D ← [18C2+24h]`, `byte_D70E ← [18C2+1Eh]` | hystérésis, délais, seuils |
| 156245 | **`C588 ← C5A4`** | `C588` = température d'air figée en début de cycle |

Les seuils de plausibilité de la pression sont aussi dans ce bloc : `[18C2+38h]`, `[18C2+3Ah]`
(hystérésis, l. 156405-156445) et `[18C2+36h]` (offset, l. 156425).

### 1.1 La chaîne arithmétique du cycle (l. 156480-156560)

```
l.156480  calls sub_A5C92                    ; ← calcule word_C3E0
l.156483  D756 = min(C3E0, 7FFFh)
l.156505  word_D1F4 = D756                   ; ①  D1F4 = C3E0 = CHARGE D'AIR
l.156507  C8FE = word_C38E                   ;    P_amb (800-1200 mbar, étape 13 §5)
l.156512  r4 = unk_20AC(D756, D756, 2710h)   ;    = D756² / 10000
l.156517  r4 = unk_20AC(C588, r4, C8FE)      ;    = T_air · (charge²/10000) / P_amb
l.156520  word_D20A = r4                     ; ②  charge corrigée densité
l.156524  r4 = unk_20AC(r4, [word_18E6], 3E8h)   ; = (…)/1000
l.156530  r4 = unk_20AC(r4, 0Ah, 64h)        ;    ×10/100
l.156534  r4 = r4 + C8FE ; word_C5BA = r4    ; ③  C5BA = P_amb + k·(charge²)/P_amb
l.156541  C944 = word_C612
l.156546  r4 = unk_20AC(C944, 3E8h, [r0+4Ch]) ; = C944 × 1000 / C5BA
l.156549  word_D202 = r4                      ; ④  D202 = RATIO de pression (×1000)
l.156553  r4 = unk_1D36(word_18C6, C61C)      ;    courbe 0xE4FC8, axe 0..7000
l.156558  r4 = unk_1D36(word_18C4, C562)      ;    courbe 0xE4FA4, axe 0..20000
l.156563  r4 = unk_20AC(r4, r12, 64h)         ;    produit /100
l.156566  word_D1E6 = r4                      ; ⑤  correction produit
```

**Lecture physique.** `C5BA = P_amb + k·ṁ²/P_amb` est **l'inversion de la loi d'orifice**
`ṁ = S·√(2ρΔP)`, avec `ρ ∝ P_amb/T`. Autrement dit : le calculateur **reconstruit la pression amont
à partir du débit d'air et de la pression d'ambiance** — la chute de pression est **calculée**, et
`C5BA` est la pression absolue qui en résulte. `D202 = 1000·C944/C5BA` est le **ratio** de cette
pression à la pression mesurée `C944` (= `C612`) ; son axe de carte va de `1000` à `3000`,
c'est-à-dire **1,00 à 3,00**, ce qui est exactement l'ordre de grandeur d'un ratio de suralimentation.

### 1.2 Les cartes associées (toutes en zone de calibration)

| pointeur | EA | tag | axe X | axe Y | valeurs |
|---|---|---|---|---|---|
| `word_18C0` | **`0xE4F42`** | `C5A4` | courbe, axe `2431…3331` = **−30…+60 °C** | — | correction T°air |
| `word_18D4` | **`0xE51E4`** | `C5A4` | courbe 8 pts `2431, 2631, 2731, 2831, 2931, 3031, 3131, 3331` | — | **axe T°air par pas de 10 °C** |
| `word_18C6` | **`0xE4FC8`** | `C61C` | courbe 8 pts `0, 1000, 2000, 3000, 4000, 5000, 6000, 7000` | — | **axe régime 0…7000 tr/min** |
| `word_18C4` | **`0xE4FA4`** | `C562` | courbe 8 pts `0, 5000, 6000, 7000, 8000, 9000, 11000, 20000` | — | débit / charge 0…20000 |
| `word_18C8` | **`0xE4FEC`** | `D1E6` | carte 8 pts `0…20000` | `D1F6` | — |
| `word_18D2` | **`0xE513C`** | `D202` | carte 8 pts **`1000…3000`** | `C590` (`0…90`) | 1005…1459 |
| `word_18E8` | **`0xE52C4`** | — | seuil `[+8]` comparé à `D202` (l. 156590-156600) | | |
| `word_18E6` | **`0xE52C2`** | — | constante de la chaîne ③ | | |
| — | **`0xE5094`** | `D1F4` | carte `C42E` (régime) × **`D1F4` 100…3500** | | 0…0 |

---

## 2. Le dP : la réponse

### 2.1 Il n'y a pas de mesure de dP, il y a un modèle

L'équation du §1.1 est **la** réponse à la question « que fait le logiciel de la pression
différentielle ? » : il ne la lit pas, **il la reconstruit**. La différence de pression n'est pas une
entrée, c'est le **résultat** de `ṁ²/P_amb`. Cette architecture (débitmètre + capteur d'ambiance, sans
capteur de dP) est cohérente avec :

- la carte de charge `0xE5094` : axe **charge `D1F4`**, pas dP ;
- la carte de ratio `0xE513C` : axe **ratio `D202`**, pas dP ;
- et la boucle FAP de l'étape 12, alimentée par **le débit d'air**, pas par une pression.

### 2.2 Ce qui est réellement mesuré : la pression d'admission

| élément | valeur | preuve |
|---|---|---|
| tag | **`D04C`** | table `0xE1400` → `word_151C`… |
| loi | **`0xE316E`** : `D04C 0002 0033 03CC 029B 50BB` = 2 points, `51 → 667`, `972 → 20667` | dump `0xE316E` |
| lecture | **667 … 2066,7 mbar** si l'unité est le **dixième de mbar** → capteur **2,5 bar absolu, 0,5–4,5 V** | déduction dimensionnelle |
| cohérence | l'axe du ratio `D202` est `1000…3000` = `P_int/P_amb` pour `P_amb ≈ 1000 mbar` ⇒ 1,0 à 3,0 bar absolus | **accord parfait** |
| recoupement | `[word_18E8+8]` compare `D202` à un seuil (l. 156590-156600) = surveillance de surpression | code |

C'est cette voie (et non `D044/D052/D054/D056`) qui porte la pression. **Correction de l'étape 12** :
les quatre voies « à butée 102/921 » ne sont **pas** des mesures de pression calibrables ; `D04C` l'est.

### 2.3 Les quatre voies 0,5–4,5 V : aucun lecteur

Relevé exhaustif des lectures (`mov rX, word_D0xx`) pour **toutes** les variables de mesure analogique :

```
D044 : 0   D046 : 0   D052 : 0   D054 : 0   D056 : 0   D060 : 0
D062 : 0   D066 : 0   D06A : 0   D06E : 0   D070 : 0   D080 : 0
D082 : 0   D072 : 0   D03C : 0   D040 : 0   D042 : 0
```

Zéro lecture **directe**. Elles sont lues par **pointeur** (voir §2.4) ou pas du tout.
Combiné au fait qu'aucune loi de ces voies ne produit une grandeur physique (§Étape 13 §6.1),
la conclusion est nette :

> **Sur ce logiciel, la pression différentielle n'est convertie en mbar nulle part.
> Elle n'entre dans aucun calcul de charge, de suie ou de régénération.**

### 2.4 Où elles vont quand même : `sub_88084`, la table de mesure diagnostique

**l. 96140-96260** : une table de sauts qui prend un **identifiant** dans `rl4` et renvoie en `r9`
l'**adresse RAM du bloc de mesure** :

| identifiant (`rl4`) | adresse renvoyée |
|---|---|
| `0x0F` | `9FB2h` |
| `0x11` | `95AAh` |
| `0x13` | `0A8EAh` |
| `0x15` | `9E68h` |
| `0x16` | `0BF64h` |
| `0x19`, `0x1C`, `0x20`…`0x23` | `0D896h`, `0D594h`, `0C564h`, `0CA8Ah`, `0D63Eh`, `8FA8h`… |
| `0x31`…`0x34` | `0C1FCh`, `0A804h`, `0C0D0h`, `0A47Ah` |
| `0xF0`, `0xF4`…`0xF7`, `0xFF` | … |
| défaut | `922Eh` |

**C'est l'interface de mesure du banc de diagnostic PSA** : un identifiant de point de mesure → une
adresse. Les grandeurs « orphelines » du §2.3 y sont exposées, et c'est par cette table que le
capteur de dP (s'il est câblé) est **lisible au banc** sans être utilisé par la régulation.

**Prochaine étape précise** : décoder les 24 identifiants ci-dessus (liste complète à extraire de
`sub_88084`) et, pour chacun, remonter le bloc de mesure `0D5xx–0D8xx` jusqu'à la variable `D0xx`
d'origine. C'est la seule voie qui peut encore révéler un dP exploité.

### 2.5 Verdict et test de terrain

| hypothèse | statut après cette étape |
|---|---|
| **H1** : le dP alimente la charge de suie | **réfutée** : la charge est le modèle `D2BA`/`D2BE` de l'étape 12 |
| **H2** : le dP est mesuré et utilisé pour le **diagnostic** (fenêtres + compteurs de défaut) | **confirmée** : 4 voies cadrées, 4 codes défaut (`0xA0`, `0xA2`, `0x20A`, `0x208`), 0 lecteur interne |
| **H3** : le dP vient de l'ECU additif FAP / du BSI | **non tranchée** — c'est la table `sub_88084` qui dira si une voie dP est publiée |

**Test décisif** (déjà décrit, mais désormais propre) : au contact, la voie `D04C` doit lire
**≈ 1000 mbar** (pression atmosphérique). Si une **autre** voie affiche ≈ 0 mbar au repos et monte
avec la charge, c'est le dP — et il n'est **pas** converti, donc il ne peut s'agir que de `D052`,
`D054`, `D056` ou `D044/D046`.

---

## 3. Vitesse, rapport engagé, compteurs

### 3.1 Le rapport engagé — prouvé

```
l.156208   bclr word_FD04.0 ; bclr word_FD04.2 ; movb byte_D20C, ZEROS   ; init
l.156657   r8.3 = (FD04.0 && !FD04.2) ? 1 : 0
l.156670   r8.4 = (FD04.0 &&  FD04.2) ? 1 : 0
l.156687   r8.5 = (!FD04.0 && FD04.2) ? 1 : 0
l.156771   movb [r0+4Eh], #1 ; byte_D20C = 1     ; si r8.3
l.156779   movb [r0+4Eh], #2 ; byte_D20C = 2     ; si r8.4
l.156785   movb [r0+4Eh], #3 ; byte_D20C = 3     ; si r8.5
l.156765   bmov word_FD02.13, r8.3
l.156766   bmov word_FD02.14, r8.4
l.156767   bmov word_FD02.15, r8.5
```

⇒ **`byte_D20C` = 1, 2 ou 3 = le rapport engagé**, et `word_FD02.13/.14/.15` en sont les images
pour les blocs voisins. C'est exactement la variable qui sert aux **limites de couple par rapport**
(1, 2, 3) : sa valeur est aussi rangée dans `[r0+4Eh]` du bloc d'état, donc lisible par tout le reste
du programme.

Le **calcul** de `FD04.0`/`FD04.2` (donc la détection elle-même, par comparaison du rapport
`régime / vitesse`) n'apparaît pas dans la fenêtre examinée : ils sont seulement **testés** ici.
Deux possibilités : soit les écrivains sont atteints indirectement, soit la détection est dans le
demi-programme manquant — c'est le **prochain point à trancher**.

### 3.2 La vitesse instantanée — pas trouvée, et pourquoi

Faits négatifs **prouvés** :

1. **aucune capture CAPCOM** n'est écrite dans ce demi-programme (établi à l'étape 11 : `CC1_CC6`,
   `CC5`, `CC7`, `CC8`, `CC15` sans écriture) ⇒ **le comptage des impulsions de boîte n'est pas ici** ;
2. **`word_F91C` n'est pas une distance** : un seul écrivain (`233544-233559`), un
   `sub word_F91C, ONES` avec rebouclage, et ~250 lecteurs **tous** en différence
   (`sub rX, word_F91C`). Un compteur **décrémenté à cadence fixe** est une **base de temps**, pas
   un intégrateur d'impulsions de roue. **→ erratum de l'étape 13 (§4).**
3. aucune variable de la forme 0…3000 (0,1 km/h) n'est lue dans les fonctions de couple.

Pistes restantes, par ordre de probabilité :

| piste | indice |
|---|---|
| **`C590`** | calculée l. 156795-156803 : `C5A4 × D756 / C5BA × 1000/3162`, et **axe `0…90`** dans la carte `0xE513C` → la plage 0-90 est celle d'une vitesse en km/h |
| **`D356`** | axe `60036…61046` dans la carte `0xE7D44` (avec le régime `1000…2200`) → ressemble à un **compteur d'impulsions** proche du bouclage 16 bits, pas à une grandeur physique |
| **moitié manquante** | la capture d'impulsions, la réception CAN et les compteurs km y sont probablement |

### 3.3 Les compteurs kilométriques

Rien dans ce demi-programme. Et c'est **cohérent** avec l'étape 12-13 : la régénération est décidée
par **compteur d'événements** (`byte_D7DE`, seuil 200 en `[word_1952+36h]`), **intégrateur de charge**
(`D2BA`, seuil 100 % en `[word_1952+30h]`) et **temporisations** (110 s, 254 s), pas par un seuil
kilométrique. Les km (total, partiels, intervalle de régénération) sont **des données de la ligne de
diagnostic / du combiné**, lues par l'interface `sub_88084` — pas des variables de régulation.

---

## 4. Re-vérification des trois températures — critère neuf : les axes des cartes

**La méthode.** Un tag de courbe/carte n'est pas seulement un pointeur : **les bornes de l'axe disent
le domaine physique admissible de la grandeur**. Un axe qui monte à **+122 °C** ne peut pas être du
gasoil ; un axe qui s'arrête à **+60 °C** ne peut pas être du liquide de refroidissement.

### 4.1 Tableau des axes, par tag candidat

| tag | axes rencontrés dans les cartes | interprétation |
|---|---|---|
| **`C3BA`/`C904`** (voie 0x30E) | `2581…3331` (−15…+60), `2531…3531` (−20…+80), `2531…3331` (−20…+60) | **air d'admission** : jamais > +80 °C |
| **`C3D2`/`C908`** (voie 0x318) | `2481…3731` (−25…+100), `2431…3831` (−30…+110), **`3841…3951` (+111…+122)**, `2531…3131`, `2481…2721` | **liquide de refroidissement** : seule grandeur qui atteint +122 °C |
| **`C3B0`/`C900`** (voie 0x310) | `3051…3751` (**−10…+102**) | **gasoil** : plage étroite, jamais > +102 °C |

### 4.2 Le point qui tranche (LDR)

Carte **`0xE880A`** : `X = C42E [1300…4000 tr/min] (n=6)`, `Y = C3D2 [3841…3951] (n=6)`, valeurs `0…7040`.

Un axe de **+111,0 à +122,0 °C** couplé au régime, avec des sorties jusqu'à 7040 : c'est la
**protection thermique haute** (dérating / coupure). Aucun carburant ne monte à 122 °C dans une
cartographie ; aucun air d'admission non plus. ⇒ **`C3D2` / `C908` / `D084` = liquide de
refroidissement : prouvé** (et non plus « très probable »).

### 4.3 Air d'admission : troisième preuve indépendante

Dans la fonction du §1, la température d'air utilisée est `C5A4`, et :

- **l. 153724-153727** : `C5A4 ← C904` (= copie de `C3BA` = voie `0x30E` / `D06C`) — sauf variante
  ou défaut, où `C5A4 ← [word_186A]` (`0xE4B8E`, l. 153700-153710) ;
- **`0xE4F42`** (`word_18C0`) : courbe **tag `C5A4`**, axe `2431…3331` = **−30…+60 °C** ;
- **`0xE51E4`** (`word_18D4`) : courbe **tag `C5A4`**, axe `2431, 2631, 2731, 2831, 2931, 3031, 3131, 3331`
  = **−30 °C à +60 °C par pas de 10 °C** — l'axe canonique d'une correction de température d'air.

⇒ **`D06C` = air d'admission : prouvé trois fois** (chaîne `C3BA→C904`, tag `C5A4`, et deux axes
−30…+60 °C).

### 4.4 Gasoil : reste « probable »

Axe `3051…3751` = **−10,0 … +102,0 °C** (carte `0xE8000`, `X = C42E [800…4800]`, valeurs `1500…7600`),
plus les courbes sollicitées au-delà de +60 °C et le remplacement **+74,1 °C** (descripteur, `+08`).
Rien ne le **réfute** ; rien ne le **prouve** comme pour les deux autres. Ce qui le prouverait :
un `cmp` explicite contre un seuil de type « carburant chaud » (`≥ 3431` = +70 °C) **ou** un lien
arithmétique avec la densité du gasoil (`ρ = f(T)` multipliant la quantité injectée). C'est le
prochain test ciblé que je propose.

---

## 5. Errata

| étape | affirmation | correction |
|---|---|---|
| **13 §4** | « `word_F91C` = la distance parcourue, `d = C080 − F91C` » | **faux** : un seul écrivain (décrément, l. 233544-233559), ~250 lecteurs en différence ⇒ **base de temps**. Les « fenêtres de distance » de `word_15F0` (`0xE3AD0`) sont des **durées** |
| **12 §8** | « les 4 voies à butée 102/921 = le vrai dP » | **faux** : aucune n'est convertie en mbar ; la pression mesurée est **`D04C`** (§2.2) |
| **12** | « `C60A` = axe de pression à trancher » | confirmé : `C60A`/`C940` = **pression d'ambiance** (`D03A`), axe `600…1050` mbar dans `0xE7828` |

---

## 6. Ce qui reste, par ordre d'utilité

1. **Décoder `sub_88084`** (24 identifiants → adresses) : seule chance de trouver un dP exploité.
2. **Trouver les écrivains de `FD04.0`/`FD04.2`** : c'est la détection de rapport, donc le calcul
   `régime/vitesse`, donc **la vitesse**.
3. **Vérifier `C590`** (l. 156795-156803) : la division par `3162` est suspecte — si c'est
   `impulsions/km × 60`, on tient la vitesse et le compteur.
4. **Trancher le gasoil** : chercher une multiplication de la quantité injectée par une courbe de
   densité indexée `C900`.
5. **Secteur `0xEC000`** : toujours le candidat pour la moitié manquante.
