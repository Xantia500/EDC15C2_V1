# ÉTAPE 15 — `sub_88084` décodé intégralement, la chaîne `FD04.0`/`FD04.2`, et la mise au point sur les pressions

> **ERRATUM (étape 16)** — Le §3 de ce document est **faux** : je concluais qu'« aucun timer n'est
> configuré » après avoir cherché `T0CON`/`CAPREL`/`CC16`. Les registres existent sous d'autres noms
> (`CC1_T0` = base de temps, 126 lectures ; `CC1_T01CON` ; `CC1_CC8`/`CC15`/`CC13` = captures ;
> `CC2_CC23`…). **Le temps est mesuré dans ce demi-programme**, et une période est même mesurée par
> capture (`CC1_CC13` → `word_D896`). Voir `ETAPE16_...md` §3 et §4.
> Le §1.1 est également incomplet : `sub_88084` est le gestionnaire du **service diagnostic `0x80`**,
> avec session, longueur et codes d'état (Étape 16 §1.1-§1.2).

Suite de `ETAPE14_dP_pression_admission_rapport_et_reverification_temperatures.md`.
Preuves = **numéros de ligne de `clean.asm`** + **adresses en zone de calibration** (`0xE0000–0xEBFFF`).

---

## 0. Ce que cette étape change

| # | Résultat | Statut |
|---|---|---|
| 1 | **`sub_88084` est un gestionnaire de service de diagnostic**, pas une table de mesures. 27 identifiants décodés. | **prouvé** (§1) |
| 2 | **`byte_D20C` n'est PAS le rapport engagé** : c'est un **code d'état à 3 valeurs** issu de deux conditions booléennes **temporisées**. | **erratum** (§2.2) |
| 3 | **`FD04.0`/`FD04.2` pilotent des intégrateurs 32 bits à taux variable**, pas une limite de couple. | **prouvé** (§2.3) |
| 4 | **Aucun timer ni CAPCOM n'est configuré** dans ce demi-programme (`T0CON…T6CON` = 0 occurrence) ⇒ **le sous-système de capture d'impulsions est hors de ce demi-programme**. | **prouvé (négativement)** (§3) |
| 5 | **Mise au point des pressions** : `C38E` = pression **atmosphérique** (prouvé par 2 usages), `D04C` = pression **d'admission/turbo**, et le « 2,5 bar max » se lit dans la carte **`0xE7828` : 1000…2370 mbar**. | **prouvé** (§4) |
| 6 | **Le dP n'est utilisé ni brut ni converti** : aucun des 88 cartographies n'a d'axe sur `D044/D052/D054/D056`. | **prouvé (négativement)** (§5) |

---

## 1. `sub_88084` — décodage complet (l. 96088 → 96409)

### 1.1 Ce que c'est vraiment

Le prologue ne laisse aucune place au doute : **c'est un gestionnaire de requête de diagnostic**
(service type « read data by local identifier »), pas une table de pointeurs de mesure.

```
l.96089  mov [-r0], r9
l.96090  mov r4, #80h          ; ┐
l.96091  mov word_BF00, r4     ; ┘ code de réponse "en cours" n°1
l.96092  movb rl4, byte_F67E
l.96093  cmpb rl4, #3          ; session / mode doit valoir 3
l.96094  jmpa cc_NZ, loc_88340 ; sinon → chemin d'erreur
l.96096  movbz r4, byte_F627
l.96097  cmpi2 r4, #7Eh        ; longueur demandée ≤ 0x7E
l.96098  jmpa cc_SGT, loc_88340
l.96100  mov r4, #90h ; mov word_BF00, r4      ; code de réponse "en cours" n°2
l.96101  calls 8, sub_888D6                    ; préparation
l.96102  calls 8, sub_8E168                    ; préparation
l.96103  movb byte_FB4E, #3                    ; ┐
l.96107  byte_FB4F = byte_FACF | 40h           ; │
l.96110  byte_FB50 = byte_FAD0                 ; │ constitution de la RÉPONSE
l.96113  byte_FB51 = #1                        ; │
l.96115  movb word_FC10, #12h                  ; ┘
l.96117  mov r4, #0A0h ; mov word_BF00, r4     ; "prêt à répondre"
l.96119  movb rl4, byte_FAD0                   ; ← IDENTIFIANT DEMANDÉ
l.96120  cmpb rl4, #1 ; jmpr cc_Z, loc_881DA
         … 25 comparaisons …
```

Puis, pour chaque identifiant, **une seule instruction** : `mov r9, #<adresse>` suivi d'un saut vers
`loc_882AA`. La fonction **renvoie donc en `r9` l'adresse RAM d'un bloc de paramètres**, que
l'appelant (`sub_8A794`, l. 96430) recopie dans la trame de réponse.

### 1.2 Table complète des 27 identifiants (l. 96184 → 96339)

| id (`byte_FAD0`) | adresse RAM renvoyée | id | adresse RAM |
|---|---|---|---|
| `0x01` | `0x09FB2` | `0x20` | `0x0CA06` |
| `0x02` | `0x0D896` | `0x21` | `0x08738` |
| `0x03` | `0x0D594` | `0x22` | `0x08EDA` |
| `0x04` | `0x0C564` | `0x23` | `0x09B2E` |
| `0x05` | `0x0922E` | `0x31` | `0x0CD46` |
| `0x06` | `0x0CA8A` | `0x32` | `0x0A0F2` |
| `0x08` | `0x0D63E` | `0x33` | `0x0BA5A` |
| `0x0B` | `0x08FA8` | `0x34` | `0x0AB82` |
| `0x0C` | `0x0C1FC` | `0xF0` | `0x0AFEC` |
| `0x0D` | `0x0A804` | `0xF4` | `0x09E30` |
| `0x0E` | `0x0C0D0` | `0xF5` | `0x09E1C` |
| `0x0F` | `0x0A47A` | `0xF6` | `0x0C4AC` |
| `0x11` | `0x095AA` | `0xF7` | `0x0B700` |
| `0x13` | `0x0A8EA` | `0xFF` | `0x0934A` |
| `0x15` | `0x09E68` | | |
| `0x16` | `0x0BF64` | | |
| `0x19` | `0x09CC4` | | |
| `0x1C` | `0x0A026` | | |

> **Erratum de l'étape 14 §2.4.** Le tableau que j'y avais donné était **faux** : je l'avais reconstitué
> « à vue » en associant les identifiants et les adresses par leur proximité dans le listing. Le tableau
> ci-dessus est **extrait automatiquement** (parsing des couples `cmpb rl4,#NNh` → `loc_XXXX` →
> `mov r9,#YYYYh`). Exemple de l'erreur : j'avais écrit `0x0F → 0x09FB2` ; en réalité
> `0x0F → 0x0A47A` et `0x09FB2` est l'identifiant **`0x01`**. Les identifiants `0x07`, `0x09`, `0x0A`,
> `0x10`, `0x12`, `0x14`… **n'existent pas** (trous dans la table : ce sont les identifiants non
> supportés par cette version).

### 1.3 Le chemin d'erreur, et ce qu'il révèle

```
l.96340  loc_88340:  movb rl4, #11h
l.96341  mov r5, word_F62A ; movb [r5], rl4      ; écrit 0x11 dans une boîte aux lettres
l.96344  mov r12, #2 ; mov r13, #1
l.96345  calls 8, sub_8F9F0                       ; signale l'échec (2,1)
l.96350  loc_88352:  mov word_BF00, ZEROS ; mov r9, [r0+] ; rets
```
Donc **`0x11` est aussi le code d'échec** (invalidité/refus) et `word_BF00` retombe à 0 en sortie.
`byte_F67E` (mode), `byte_F627` (longueur) et `word_BF00` (état) forment le **contexte de session
diagnostic** : ce service ne répond que dans une session précise.

### 1.4 Nature des 27 blocs — et pourquoi je n'ai pas pu les identifier d'un coup

Chacune des 27 adresses est référencée **exactement une fois** dans tout le fichier : dans son
`mov r9, #…`. Conséquence importante et vérifiée :

> **Ces blocs ne sont jamais adressés en absolu.** Ils sont remplis et relus **par pointeur/indice**.
> C'est la raison pour laquelle tous mes balayages par symbole (`word_xxxx`, `byte_xxxx`) les ont
> manqués — et c'est aussi pourquoi la région RAM **`0x8000–0xBFFF`** (où se trouvent 22 des 27 blocs)
> n'apparaît dans aucun de mes inventaires : elle ne contient **aucun symbole nommé**.

Ce sont donc des **blocs de paramètres de diagnostic** (le « Messwertblock » PSA/Bosch) : un en-tête
puis N valeurs, remplies par une routine générique indexée. Les identifiants bas
(`0x01`…`0x0F`) renvoient les valeurs « de base », les `0x11`…`0x34` des grandeurs individuelles,
les `0xF0`…`0xFF` des blocs spéciaux — motif classique de la mesure PSA.

**Ce qu'il faudrait pour les nommer** : trouver la routine qui **écrit** dans ces blocs (accès
`[rX+#offset]` avec `rX` chargé par un indice). C'est un travail de prochaine étape, mais il est
**borné** : 27 blocs, une routine d'écriture.

---

## 2. `FD04.0` / `FD04.2` — la chaîne complète

### 2.1 Le schéma réel

Les deux bits ne sont **pas calculés** dans cette fonction : ils sont **verrouillés** depuis deux
autres bits, eux-mêmes issus d'une temporisation sur des **conditions booléennes**.

```
                ┌─ r8.0, r8.1, r8.2, r9.10, r9.11, r9.14 = PARAMÈTRES D'ENTRÉE (registres)
                │
l.157371  FD04.14 = ( [18C2+42h] < C5A4 < [18C2+44h] )      ← FENÊTRE DE TEMPÉRATURE D'AIR
l.157384  FD04.1  = r8.0 ? FD04.14 : !r9.10   ;  forcé à 1 si r8.1   ;  mis à 1 si r8.1
l.157390  si FD04.1 && FD04.10 → décrémente byte_D709 (recharge [18C2+3Dh]) sinon FD04.10 = FD04.1
l.157306  bmov word_FD04.0, word_FD04.10                  ← VERROUILLAGE
l.157159  FD04.11 : temporisation sur r9.14 via byte_D708 (recharge [18C2+3Ch])
l.157171  bmov word_FD04.2, word_FD04.11                  ← VERROUILLAGE
l.156206  (init) bclr FD04.0 ; bclr FD04.2 ; byte_D20C = 0
```

### 2.2 Erratum : `byte_D20C` n'est pas le rapport engagé

```
l.156657  r8.3 = (FD04.0 && !FD04.2)        ; sinon 0
l.156670  r8.4 = (FD04.0 &&  FD04.2)
l.156687  r8.5 = (!FD04.0 && FD04.2)
l.156774  byte_D20C = 1 (si r8.3) / 2 (si r8.4) / 3 (si r8.5)
l.156765  FD02.13/.14/.15 = images de r8.3/.4/.5
```

C'est bien un **code à 3 valeurs**, mais ses deux entrées sont :
- une **fenêtre de température d'air** (`[18C2+42h] < C5A4 < [18C2+44h]`) → `FD04.0` ;
- un **bit d'entrée** de la fonction (`r9.14`) → `FD04.2`.

Ce n'est donc **pas** un rapport de boîte calculé par `régime/vitesse`. J'avais conclu trop vite à
l'étape 14 : `byte_D20C` est un **état de fonctionnement** (typiquement une plage de validité
d'EGR/ARF : « air dans la fenêtre thermique » × « condition externe »), pas un rapport.

### 2.3 Ce que `FD04.0`/`FD04.2` pilotent réellement

Deux **intégrateurs 32 bits** (paire `r4:r5` en retour) appelés en segment 9 :

```
l.157326  si FD04.0 :  sub_97E16( [18C2+30h], [18C2+48h], D71C:D71A )
l.157347  sinon     :  sub_97E16( [18C2+30h], [18C2+46h], D71C:D71A )
l.157381  si FD04.2 :  sub_97E16( [18C2+30h], [18C2+4Ch], D720:D71E )
l.157400  sinon     :  sub_97E16( [18C2+30h], [18C2+4Ah], D720:D71E )
```

⇒ les deux bits **sélectionnent le taux d'intégration** (`[18C2+46h]`/`+48h` et `+4Ah`/`+4Ch`) d'un
apprentissage à deux états. Tout est calibré dans **`word_18C2` = `0xE4F56`** :

| champ | usage |
|---|---|
| `+30h` | incrément commun de l'intégrateur |
| `+3Ch`, `+3Dh` | recharges des temporisations `byte_D708` / `byte_D709` |
| `+42h`, `+44h` | **fenêtre de température d'air** (bornes basse/haute) |
| `+46h`, `+48h` | taux de l'intégrateur n° 1 (deux états) |
| `+4Ah`, `+4Ch` | taux de l'intégrateur n° 2 (deux états) |
| `+38h`, `+3Ah`, `+36h` | hystérésis et offset du diagnostic de pression |
| `+3Eh`, `+40h` | fenêtre basse d'un second diagnostic (l. 157186-157205) |

---

## 3. La vitesse : la preuve négative est maintenant définitive

Relevé exhaustif des registres de temps du C167CR dans tout `clean.asm` :

| registre | occurrences |
|---|---|
| `T0CON` `T1CON` `T2CON` `T3CON` `T4CON` `T5CON` `T6CON` | **0 chacune** |
| `CAPREL` | **1** — et c'est un **commentaire** du manuel SFR (l. 63020) |
| `CC16` | **1** — et c'est une **étiquette** `seg016:CC16↑j` (l. 226723), pas le registre |
| `CC1_CC6`, `CC5`, `CC7`, `CC8`, `CC15` | aucune écriture (établi à l'étape 11) |

**Conséquence logique** : sans timer configuré, **ni la vitesse ni le régime ne peuvent être calculés**
ici. Or le régime `C42E` existe et est utilisé partout. Donc :

> **Le sous-système de capture d'impulsions (sonde de boîte + capteur de vilebrequin 60-2) et la base
> de temps sont dans le demi-programme manquant. `C42E` et la vitesse y sont *reçus*, pas *calculés*.**

Cela explique trois choses d'un coup :
1. pourquoi `word_F91C` est une **base de temps entretenue ailleurs** (un seul écrivain ici : le décrément) ;
2. pourquoi `FD04.0`/`FD04.2` viennent de **paramètres d'entrée** `r8`/`r9` (déjà calculés en amont) ;
3. pourquoi aucune variable 0…3000 (0,1 km/h) n'est lue dans les fonctions de couple.

Le rapport `régime/vitesse` que tu décris est donc **certainement** dans la partie manquante, et il y
produit les bits `r9.10`/`r9.11`/`r9.14` qui arrivent ici comme arguments. Ce que je peux affirmer :
**ce n'est pas `byte_D20C`, et ce n'est pas calculé dans les 234 000 lignes désassemblées.**

---

## 4. Mise au point sur les pressions (ta remarque)

Tu as raison de me reprendre : j'ai mélangé deux choses. Voici la séparation propre, avec les preuves.

### 4.1 Les quatre grandeurs de pression

| grandeur | variable | plage | preuve |
|---|---|---|---|
| **pression atmosphérique** | `D03A` → `C38E` → `C60A`/`C940` | **600 … 1200 mbar**, loi 2 points `0xE2FB2`, fenêtre `450…972`, repli **839 mbar** | §4.2 |
| **pression d'admission (« turbo »)** | `D04C` → `C36A` | **667 … 2066,7 mbar**, loi `0xE316E` (51→667, 972→20667), capteur 0,5–4,5 V | §4.3 |
| **pression absolue modélisée** | `C5BA` | `P_atmo + k·ṁ²/P_atmo` | l. 156510-156536 |
| **ratio des deux** | `D202` | `1000·C944/C5BA`, axe de carte **1000…3000** = 1,00…3,00 | l. 156546-156549 |

### 4.2 `C38E` est bien la pression atmosphérique — deux preuves

1. **Elle sert de référence dans l'équation d'orifice** : `C5BA = C8FE + k·ṁ²/C8FE` avec
   `C8FE = C38E` (l. 156507-156534). Une pression de rampe ou de suralimentation n'a aucun sens
   comme référence de densité dans cette formule : c'est **P_atmo**.
2. **Elle est le second axe de la carte de densité de l'air** :

```
l.131771  mov word_D094, [r0+2]        ; D094 = T°air (C904, éventuellement corrigée :
l.131756  D094 = 2731 + (C904 − 2731)·k/10000   ; gain sur la température d'air !)
l.131772  test byte_C2C9.2 → r8 = word_C940           ; = P_atmo
l.131778  test byte_C2C9.3 → r8 = min(C944, C946)     ; ou le min de deux pressions
l.131793  sinon            → r8 = word_C944
l.131795  word_D092 = r8
l.131796  calls unk_1D50( word_15EE, D094, D092 )     ; carte 2-D densité
l.131800  word_C3EC = r4                              ; facteur de correction
```

`word_15EE` = **`0xE39D8`** : c'est **la carte de densité de l'air** (T°air × pression). Y mettre une
pression de rampe serait absurde ; y mettre la pression atmosphérique (ou la pression d'admission)
est exactement l'usage attendu. **`C38E` = P_atmo : confirmé.** C'est ce que j'appelais « capteur
d'ambiance » — et c'est bien un capteur distinct de la pression turbo.

### 4.3 Où se lit le « 2,5 bar max » que tu évoques

Pas dans la loi du capteur, mais dans **la carte de consigne** : **`0xE7828`**
(`word_18D2`… non : `0xE7828` = carte du Datensatz)

```
X = C60A [600 … 1050 mbar]   (pression atmosphérique)
Y = C42E [1000 … 5000 tr/min]
valeurs = 1000 … 2370 mbar
```

**C'est la pression d'admission maximale admissible, corrigée par l'altitude** (à 600 mbar
d'atmosphère — 4000 m — on n'autorise pas la même suralimentation qu'au niveau de la mer).
`2370 mbar` est **exactement** l'ordre de grandeur du « 2,5 bar max » dont tu parles. Deux cartes
voisines confirment la fonction : `0xE71F6` (`C60A × D004 → 0…1000`) et `0xE707A`/`0xE72C4`/`0xE744C`
(régime × `D004 [0…7000]` → 1500…9000).

Donc : **`D04C` ≈ 2 bar pleine échelle au capteur, la consigne monte à 2,37 bar** — les deux chiffres
sont cohérents entre eux et avec ta valeur.

---

## 5. Le dP « brut » : vérifié aussi, et négatif

Ton intuition était la bonne à tester : un dP peut très bien n'être **jamais converti** et servir
d'axe de carte en « points de code ». Balayage des **88 cartographies** du Datensatz :

| variable | apparaît comme axe ? |
|---|---|
| `D044`, `D046` | **non** (0) |
| `D052`, `D054` | **non** (0) |
| `D056`, `D060`, `D062`, `D066` | **non** (0) |
| `D0xx` brutes en général | non — les axes sont des grandeurs **physiques** (`C42E` régime, `C3D2` LDR, `C3E6` mg/s, `C60A` mbar, `D202` ratio, `D1F4` charge…) |

⇒ **ni converti, ni brut.** Le dP ne peut donc, dans ce demi-programme, être :
1. soit **une grandeur purement diagnostique** (fenêtres de validité + compteurs de défaut, ce qui est
   prouvé pour les 4 voies) ;
2. soit **publié dans un des 27 blocs de `sub_88084`** (§1.2) — c'est la seule cachette restante
   accessible ici ;
3. soit **traité dans le demi-programme manquant** (avec la vitesse et la base de temps).

Reste une observation que je n'avais pas faite et qui va dans ton sens : **`C612` et `C614` sont deux
pressions mesurées distinctes**, et le code prend **`min(C944, C946)`** (l. 131781-131789). Si `C612`
et `C614` sont deux prises de pression **amont/aval**, alors **le dP est leur différence — et cette
différence n'est jamais formée**. C'est la piste la plus prometteuse pour expliquer un capteur
présent, câblé, calibré… et jamais exploité comme dP.

---

## 6. Errata de cette étape

| document | affirmation | correction |
|---|---|---|
| **Étape 14 §2.4** | table « identifiant → adresse » de `sub_88084` (`0x0F→9FB2`, `0x19→0D896`…) | **fausse** (reconstituée à vue). Table correcte au §1.2, extraite par parsing |
| **Étape 14 §3.1** | « `byte_D20C` = le rapport engagé 1/2/3, construit sur `FD04.0`/`FD04.2` » | **faux** : `FD04.0`/`FD04.2` viennent d'une fenêtre de température d'air et d'un bit d'entrée, **pas d'un ratio régime/vitesse** (§2.2) |
| **Étape 14 §3.1** | « le rapport sert aux limites de couple par rapport » | **non démontré** : les deux bits sélectionnent des **taux d'intégration** (§2.3) |
| **Étape 14 §2.2** | « `D04C` = la pression d'admission » | **confirmé** (§4.3) — et le « 2,5 bar » se lit dans `0xE7828` |

---

## 7. Les deux actions suivantes, dans l'ordre

1. **Trouver la routine d'écriture des 27 blocs** de `sub_88084` : elle est unique (accès indexé sur
   `0x8000–0xBFFF`). Une fois trouvée, les 27 identifiants se nomment d'un coup — dont, peut-être,
   un « dP » et une « vitesse véhicule ».
2. **Cartographier la région RAM `0x8000–0xBFFF`** : elle n'a **aucun symbole**, ce qui explique
   qu'elle ait échappé à 15 étapes de balayage. C'est 16 Ko de RAM quasi inexplorés, et c'est
   probablement là que vivent les grandeurs publiées au banc.
