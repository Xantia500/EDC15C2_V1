# ÉTAPE 13 — Les trois températures, le cadre d'acquisition des voies analogiques, le débitmètre à deux éléments, la vraie distance, et l'état exact du capteur de pression différentielle

> **ERRATUM (étape 14)** — Le §4 de ce document est **inexact** : `word_F91C` n'est pas une distance
> mais une **base de temps** (un seul écrivain, `sub word_F91C, ONES`, l. 233544-233559 ; ~250 lecteurs
> en différence). Les « fenêtres de distance » de `word_15F0` sont des **durées**. Voir
> `ETAPE14_...md` §3.2 et §5. Le reste du document (cadre d'acquisition, descripteurs, températures,
> débitmètre) est conservé et a été renforcé à l'étape 14.

Suite de `ETAPE12_datensatz_sondes_EGT_dP_et_boucle_FAP.md`.
Toutes les preuves sont des **numéros de ligne de `clean.asm`** et des **adresses en zone de calibration**
(`0xE0000–0xEBFFF`, banque Datensatz chargée par DPP0/1/2 = `0x38/0x39/0x3A`).
Rappel d'identité : **EA = offset dans `edc.bin` + 0x80000**.

---

## 0. Résumé exécutif

| # | Résultat | Statut |
|---|---|---|
| 1 | **Anatomie complète du cadre d'acquisition d'une voie** : lecture 10 bits → cadrage/diagnostic → substitution → octet d'état. 3 sous-programmes identifiés et lus. | **prouvé** (§1) |
| 2 | **Sémantique du descripteur de voie** : `+00` voie/groupe, `+02` borne **haute**, `+04` borne **basse**, `+06` stratégie+filtrage, `+08` **valeur de remplacement**, `+0C` **tag de la loi**, `+0E` **nb de points**. | **prouvé** (§1.3) — *corrige l'étape 12* |
| 3 | **Les trois températures** : air = `D06C`, liquide de refroidissement = `D084`, carburant = `D05E`. | air **prouvé**, LDR **très probable**, carburant **probable** (§2) |
| 4 | **Débitmètre = voie 0x308/0x30A, deux éléments ADC (`0x0F844` / `0x0F854`) moyennés**, contrôle croisé, remplacement 1000. | **prouvé** (§3) |
| 5 | **La distance parcourue existe** : `word_F91C`, **décrémenté** par la tâche `0x412`, avec instantané `C080` ⇒ `d = C080 − F91C` (différence **modulo**, ce qui est cohérent pour un compteur qui reboucle). | **prouvé** (§4) |
| 6 | **Nouveau : la pression atmosphérique** = `D03A` / `C38E` / `C60A` / `C940`, loi 2 points `0xE2FB2`. | **prouvé** (§5) — *lève l'ambiguïté de l'étape 12 sur C60A* |
| 7 | **dP : aucune conversion en mbar dans le demi-programme disponible.** Les 4 voies « 0,5–4,5 V » ne sont calibrées qu'en **fenêtres de plausibilité**. | **prouvé (négativement)** + protocole (§6) |

---

## 1. Le cadre d'acquisition d'une voie analogique — anatomie

C'est la découverte structurelle de cette étape : **toutes** les voies analogiques passent par le **même
gabarit de code**, et ce gabarit est entièrement contenu dans la zone `212 300–216 400` (seg016).
Chaque voie possède **6 pointeurs de calibration** distincts (des `word_14xx`, donc des entrées de la
table `0xE1400` → cf. `table_pointers_datensatz_0E1400.csv`).

### 1.1 Les six pointeurs d'une voie (exemple : la voie 0x310 / `D05E`)

| rôle | symbole RAM | contenu |
|---|---|---|
| descripteur de la voie | `word_1418` (ou `word_1556`…) | voie, bornes, stratégie, remplacement, tag, nb points |
| loi de linéarisation | `word_14DA` (ou `word_1558`…) | l'enregistrement `<tag><n><axe><sortie>` |
| descripteur de diagnostic n° 1 | `word_141E` | contient un **mode** en `+09` / `+14h` (comparé à 2 ou 4) |
| descripteur de remplacement | `word_14F0` | son `+08` = la valeur de remplacement de la voie |
| compteur de défaut A | `word_14DC` / `word_155A` | code défaut `0xA4`…`0x96` |
| compteur de défaut B | `word_14DE` / `word_155C` | code défaut `0xA6`…`0x92` |

### 1.2 Les trois sous-programmes

**a) `sub_C4AAE` — lecture du résultat de conversion (10 bits)** (corps : l. 213641)
Appel type : `sub_C4AAE(descripteur, 0F844h, 0)` ; le 2ᵉ argument est la **base des registres de résultat ADC**
(`0x0F844`, `0x0F854`, `0x0F864`… = ADDAT). Retour dans `r9` : le code brut.
(`0x3FF` = invalide, bits 15..12 = n° de voie, comme établi à l'étape 9.)

**b) `sub_C66EA` — cadrage sur bornes + diagnostic + filtrage optionnel** (corps : **l. 216195-216231**)

```
r10 = [desc+02]          ; borne HAUTE
if (r10 < r9)  → bits 5 et 7 de r11     ; sur-gamme
r10 = [desc+04]          ; borne BASSE
if (r9 < r10)  → bits 6 et 7 de r11     ; sous-gamme
else r10 = r9            ; valeur acceptée
r3 = [desc+06] & 1 ; si ≠ 0 → unk_2EBA(r9) → valeur filtrée
retour : r10 = valeur retenue, r11 = mot d'état
```

⇒ **`+02` ≥ valeur ≥ `+04`** : la fenêtre de plausibilité est **`[+04 ; +02]`** (bas ; haut), et le mot `r11`
est le **mot d'état de diagnostic** de la voie.
Vérification numérique sur 3 voies : `D06C` fenêtre `[39 ; 992]` pour un axe `40…962` ✔ ;
`D052` `[20 ; 972]` pour un axe `20…1003` ✔ ; `D03A` `[450 ; 972]` pour un axe `485…970` ✔.

**c) `sub_C6720` — substitution et rampe de rétablissement** (corps : **l. 216233-216290**)
`[desc+06] & 7` = stratégie (0 = transparence) ; selon les bits du mot d'état `r11` il renvoie :
- soit `[desc+08]` = **la valeur de remplacement** (**l. 216265** : `mov r10, [r0+#8]`),
- soit le résultat d'une rampe (`unk_233A`, `[desc+0A]` = paramètre).

**d) L'invalidation franche** — quand la voie est jugée hors service, un cadre court la court-circuite :
**l. 212323-212329** : `D03A = 0`, puis `r1 = [word_1418 + #8]`, `C38E ← r1`, `C360 ← r1`
(**l. 212425-212428** pour la paire `D044/D046` avec `word_14F0`).
⇒ le repli est **la valeur de remplacement du descripteur**, recopiée à la fois dans la variable
« physique » (`D0xx`) et dans la copie de travail (`C3xx`).

**e) Le mot d'état** : `byte_E000` / `byte_E006` = **octet d'état de la voie** (bits de sur/sous-gamme,
défaut, valeur substituée), construit par empilement des bits de `r11` puis écrit en fin de cadre
(ex. **l. 214686-214690** : `byte_E006 = rl7`).

### 1.3 Sémantique du descripteur — table vérifiée

Dix descripteurs lus en **little-endian** (la table `0xE1400` est en little-endian, comme le veut le C167) :

| voie | descripteur EA | `+00` | `+02` haut | `+04` bas | `+06` strat. | `+08` remplacement | `+0C` tag | `+0E` n | `+10` | `+12` |
|---|---|---|---|---|---|---|---|---|---|---|
| `D06C` air | `0xE353C` | 0x0049 | 992 | 39 | 0x0005 | **3231** (+50,1 °C) | `D06C` | 16 | 40 | 61 |
| `D05E` carburant | (voir §2) | 0x001A | 966 | 10 | 0x0005 | **3471** (+74,1 °C) | `D05E` | 10 | 32 | 32 |
| `D084` LDR | `0xE3834` | 0x0038 | 1013 | 20 | 0x0005 | **2631** (−10,0 °C) | `D084` | 24 | 42 | 42 |
| `D048` EGT mesurée | `0xE306A` | 0x001B | 982 | 41 | 0x0005 | **3691** (96,0 °C) | `D048` | 16 | 32 | 76 |
| `D04A` EGT 2ᵉ | `0xE1112` | 0x004F | 1005 | 41 | 0x0005 | **6231** (623,1 °C) | `D04A` | 16 | — | — |
| `D060` élément A | `0xE349C` | 0x0002 | 972 | 20 | 0x0205 | **1000** | `D060` | 4 | 20 | 205 |
| `D066` élément A (2ᵉ vue) | `0xE34EA` | 0x0004 | 6500 | 56 | 0x0003 | **1000** | `D066` | 12 | 192 | 315 |
| `D056` | `0xE3250` | 0x0006 | 972 | 51 | 0x0203 | **15000** (150 %) | `D056` | 4 | 102 | 103 |
| `D054` | `0xE320C` | 0x000C | 1064 | 0 | 0x0003 | **100** | `D054` | 2 | 0 | 1023 |
| `D052` | `0xE31AC` | 0x0005 | 972 | 20 | 0x0105 | **120** | `D052` | 4 | 20 | 102 |

**Corrections apportées à l'étape 12 :**
- `+08` n'est **pas** un code défaut : c'est la **valeur de remplacement**, en unités physiques
  (3471 = 74,1 °C ; 6231 = 623,1 °C pour la seconde EGT : c'est **exactement** le « +14 = 6231 » que
  l'étape 12 avait lu comme un seuil !).
- `+02`/`+04` ne sont ni « couple » ni « voie » : ce sont les **bornes haute/basse**.
- les **codes défaut** sont ailleurs : `0xA0`…`0xAC`, passés en `r3` à `sub_CE9B4`
  (ex. `0x96` **l. 214604**, `0x94` **l. 214616**, `0x92` **l. 214624**, `0xAC` **l. 214797**).
- la table `0xE1400` est en **little-endian** (relire les dumps de l'étape 12 en conséquence ; les tags
  et les nombres, eux, ne changent pas).

---

## 2. Les trois températures — attribution

### 2.1 La chaîne complète d'une CTN

```
brut 10 bits (sub_C4AAE)
   └─> cadrage [desc+04 ; desc+02] + diagnostic      (sub_C66EA)
        └─> loi de linéarisation  <tag><n><axe><sortie>   (courbe 0xExxxx)
             └─> variable physique D0xx  +  copie de travail C3xx  →  C9xx (banc de travail)
                  └─> variable d'état byte_E00x
```

Toutes les CTN du 4HX ont la **même forme de loi** : `brut 32…40 → sortie 4032…3931` puis
`brut 960…1002 → sortie 2331` : **c'est bien l'axe `−40 … +130 °C` en K×10**
(`2731` = 0 °C, `3531` = 80 °C : la règle de l'étape 11 tient).

### 2.2 Verdict

| grandeur | tag | descripteur | loi (EA) | axe brut | sortie (K×10) | remplacement | copie de travail | conviction |
|---|---|---|---|---|---|---|---|---|
| **air d'admission** | `D06C` | `0xE353C` | `0xE3548` | 40…962 | 4031 (−40 °C) → 2331 (+130 °C) | **3231 = +50,1 °C** | `C3BA` → `C904` → **`D094`** | **prouvé** |
| **liquide de refroidissement** | `D084` | `0xE3834` | `0xE3842` | 42…1002 | 4032 → 2331 | 2631 = −10,0 °C | `C3D2` → `C908` | **très probable** |
| **gasoil** | `D05E` | `0xE3436`+`0xE3444` | `0xE3444` | 32…969 | 3931 → 2331 | 3471 = +74,1 °C | `C3B0` → `C900` | **probable** |
| (2ᵉ gamme CTN, même sonde) | `D05A` | `0xE342A` | `0xE3436` | 32…969 | 3931 → 2331 | — | `C374` → `C3AE` | prouvé (double gamme) |

**Pourquoi l'air = `D06C` (prouvé, et non pas une déduction de vraisemblance) :**
la copie de travail `C3BA` alimente `C904` (l. 126 4xx, banc de travail), et `D094` est **calculé à partir de
`C904`** puis utilisé comme **axe de température d'air** de la carte de densité `word_15EE`
(`0xE39D8`, deux jeux d'axes `2731…4051` puis `D092`), avec `D092` = la pression (§5).
Une variable qui sert d'axe de température dans la correction de densité de l'air **est** la température d'air.

**Pourquoi la LDR = `D084` (très probable) :**
1. c'est la **loi la plus fine** du lot : **24 points** (`0xE3842`) contre 10 et 16 ;
2. c'est la seule CTN recopiée dans **31 courbes** du Datensatz (courbes dont `C3D2`/`C908` est l'axe) —
   la LDR est la grandeur thermique la plus utilisée d'un calculateur diesel (démarrage, post-injection,
   EGR, ventilateur, corrections de débit) ;
3. son remplacement (**−10 °C**) est le repli « froid » classique d'une LDR en défaut.

**Pourquoi le carburant = `D05E` (probable) :**
1. ses courbes ne sont sollicitées qu'**au-dessus de +60 °C** (étape 12, §sondes) — signature d'une
   correction de **densité de gasoil** (elle ne sert à rien à froid) ;
2. son remplacement **+74,1 °C** = un carburant « tiède » de retour de pompe.

**Test de discrimination** (si l'on veut trancher sur véhicule, sans démontage) :
débrancher **une** sonde et relever le code défaut. Les codes sont câblés par voie dans le cadre
de diagnostic : `0x94`/`0x92` (paire débitmètre), `0xA0`/`0xA2` (`D044/D046`), `0xA4`/`0xA6` (`D03A`),
`0xA8`/`0xAC` (`D066`), `0x96` (débitmètre, redondance). Les trois CTN se distinguent par leur
**fenêtre** (`[39;992]`, `[20;1013]`, `[10;966]`) : c'est le seul discriminant logiciel qui reste,
et il faut la table des codes défaut N° de voie → P-code (hors de ce dump).

### 2.3 Les deux sondes d'échappement — confirmé, y compris le cas « une seule sonde »

| | tag | loi | axe brut | sortie | remplacement |
|---|---|---|---|---|---|
| EGT **mesurée** | `D048` | `0xE3076` (16 pts) | 32…1023 | 11731 (+900 °C) → 2849 (+12 °C), **décroissante** | 3691 (96 °C) |
| EGT **n° 2** | `D04A` | `0xE30EC` (16 pts) | 10…991 | 3731 (+100 °C) → 11381 (+865 °C) | **6231 (623,1 °C)** |
| EGT **estimée** (version 1 sonde) | `word_C586` | 3 courbes `0xE5F9C`, `0xE5FC0`, `0xE639A` | — | modèle | — |

Le **remplacement 6231 = 623,1 °C** de la seconde sonde est la preuve logicielle du cas « une seule sonde » :
quand la voie `D04A` est déclarée absente ou en défaut, la variable est **substituée par une valeur
plausible de fonctionnement** (623 °C), exactement comme l'exige la variante « seconde sonde estimée ».
La version à estimation par logiciel utilise en plus `word_C586` (3 courbes de modèle) : les deux cas
coexistent donc **dans le même programme**, sélectionnés par la configuration (bit de variante) et non
par une version de fichier différente.

---

## 3. Le débitmètre : deux éléments ADC, deux tags, un contrôle croisé

Voies concernées : **tâches `0x308`** (`word_1556`, `word_1558`) et **`0x30A`** (`word_1562`, `word_1564`).

### 3.1 Cadre `0x308` — l. 214560-214700

```
l.214560  scxt CC2_CC27, #308h
l.214564  r0 = word_1556                          ; descripteur
l.214565  r9 = 0F844h ; calls sub_C4AAE           ; élément A  (registre ADC 0x0F844)
l.214568  r1 = word_1558 ; calls sub_C66EA        ; cadrage + diagnostic
l.214570  word_D060 = r9                          ; ← brut élément A
l.214573  r12 = r10                               ; valeur A retenue
l.214575  r9 = 0F854h ; calls sub_C4AAE           ; élément B  (registre ADC 0x0F854)
l.214580  word_D062 = r9                          ; ← brut élément B
l.214588  word_C378 = r12  (ou r10 selon r11.2)   ; valeur B retenue
l.214591  r10 = (r10 + r12) >> 1                  ; MOYENNE des deux éléments
l.214594  r9  = (r9 + r6) >> 1                    ; idem sur les bruts
l.214597  r11 = r11 | r6                          ; fusion des mots d'état
l.214599  r3 = [word_1556+06] ; bits 8, 9         ; deux voies de diagnostic
          → sub_CE9B4(0x96, word_155E, 13FBh)     ; compteur de défaut commun
          → sub_CE9B4(0x94, word_155A, 13FDh)     ; défaut élément A
          → sub_CE9B4(0x92, word_155C, 13FEh)     ; défaut élément B
l.214686  sub_C6720(word_1556, C902)              ; valeur physique finale
l.214687  byte_E006 = rl7                         ; octet d'état de la voie
l.214691  word_C3B2 = word_C902                   ; ← la variable de travail
```

Détail qui vaut preuve : **le contrôle croisé** (l. 214611+ et 214700+) compare l'état de la voie au
compteur de défaut de l'**autre** élément (`byte_CE9B`, `byte_CE9C`, comparés à `ONES`) : si l'un des deux
éléments est en défaut, l'autre est **invalidé lui aussi**. C'est le comportement d'un **capteur redondant
dont on ne sait pas lequel a tort** — exactement la façon dont on traite deux pistes d'un même capteur.

### 3.2 Cadre `0x30A` — l. 214745-214870

Le même couple de registres (`0x0F844`, `0x0F854`) est relu, filtré (`unk_2EBA`, conditionné par
`[desc+06] & 1`), puis :

```
l.214768  r11 = (r11 + r12) >> 1
l.214770  word_C3B6 = r11  ;  word_C37A = r11     ; ← moyenne (domaine brut)
l.214775  r12 = (r12 + r10) >> 1
l.214777  word_D066 = r12  ;  word_C3CC = r12     ; ← moyenne (domaine brut)
l.214779  word_C91C = word_C42E                   ; instantané du régime
l.214842  r3 = word_1436 ; fenêtre de régime [0]/[2]
          si C91C dans la fenêtre :
l.214868     si [word_1562+04] > C3B6 → C37A = [word_1562+04]   ; bornage bas
```

⇒ **`D060`/`D066` sont deux tags de la même mesure** (les deux vues d'un même capteur double),
`C3B2`/`C902` = la valeur physique (loi `0xE34A8`, `D060`, 4 points `20…1023 → 133…2500`),
`C3B6`/`C37A` = la moyenne brute bornée (loi `0xE34F6`, `D066`, 12 points `192…1064 → 55…7739`,
**loi cubique** : `sortie/(code−150)³ ≈ 1,1–1,25·10⁻⁵`), remplacement **1000** (l. 214726-214737 :
`C3B6 = C37A = [word_1562+8] = 0x3E8`).

Les deux échelles (`133…2500` et `3000…11500`) sont les deux unités du même débit d'air :
**mg/coup** pour l'une, **mg/s** pour l'autre (`word_C3E6`, 16 points `0xE8468`, confirmé mg/s).

**Correction de l'étape 12 :** l'affirmation « `word_C3B6` = dP » était fausse ; `C3B6` est une
**deuxième vue du débitmètre**. En revanche l'affirmation « `C3B6` n'est pas le dP » est **confirmée par
le code** et non plus seulement par élimination.

---

## 4. La distance parcourue — `word_F91C`

### 4.1 Ce que fait le code

| ligne | instruction | lecture |
|---|---|---|
| 233 544 | `word_F91C ← ONES` (initialisation de la tâche) | le compteur est **chargé à −1** |
| 233 555-233 561 | `sub word_F91C, ONES` puis rechargement quand il atteint 0 | c'est un **compteur modulo**, décrémenté d'une unité par appel de la tâche `0x412` |
| 131 451-131 453 | `word_C080 ← word_F91C` | **instantané** pris quand le véhicule est déclaré arrêté |
| 126 465-126 470 | `word_C11E ← word_F91C` puis différence signée avec garde `≥ 2` | seconde prise d'instantané, sur un autre événement |
| 131 5xx | `d = SOU word_C080, word_F91C` ; comparaison à la fenêtre `[word_15F0+8]` | **distance parcourue depuis le dernier instantané** |

### 4.2 Ce que cela veut dire

`word_F91C` **n'est pas** un kilométrage absolu (c'est le point où l'étape 12 avait raison de corriger) :
c'est un **compteur d'unités de distance** qui **décroît** et **reboucle**. Son usage est toujours
**différentiel** :

```
distance depuis le dernier instantané  =  word_C080  −  word_F91C      (arithmétique modulo 16 bits)
```

avec un **seuil minimal de 2 unités** (l. 126 586-126 596) : en dessous, la mesure est jugée non
significative et la tâche ne fait rien. C'est le comportement exact d'un **apprentissage lissé par la
distance parcourue** :

> à chaque cycle, on compare la valeur courante à la valeur apprise ; la **vitesse d'apprentissage est
> proportionnelle à la distance parcourue** depuis la dernière mise à jour, et le résultat n'est publié
> qu'après un nombre minimal d'unités de distance.

C'est ce que fait `unk_20AC(a, b, c) = a·b/c` avec `0x2710` = 10 000 (= 100,00 %) en dénominateur :
`nouvelle_valeur = ancienne + (mesure − ancienne) × distance / 100 %`. On retrouve ce schéma dans
`word_15F0` (`0xE3AD0`) : `8333` (= 83,33 %), `3000`, `10000`, `10000`, `0`, `450`, `300`, `69`.

### 4.3 Ce qui reste introuvable, et pourquoi

Le **kilométrage absolu** (compteur de régénération FAP, échéance d'entretien) et l'**intervalle de
régénération en km** ne sont **pas** dans ce demi-programme : ce sont des valeurs **EEPROM externes**,
lues par l'interface de diagnostic (la même qui écrit `C9xx` — le banc de travail de l'étape 12).
C'est cohérent avec le fait que `word_1952` (`0xE63BE`), le superviseur FAP, pilote la régénération par
**compteur d'événements** (`byte_D7DE` décrémenté, seuil `200` en `+36h`, `254 s` en `+3Ah`) et par
**intégrateur de charge** (`word_D2BA = [word_1952+1Ah]`, seuil `[word_1952+30h] = 10000 = 100 %`,
**l. 166523-166560**), pas par un seuil kilométrique.

---

## 5. Nouveau : la pression atmosphérique (`D03A`, `C38E`, `C60A`, `C940`)

L'étape 12 laissait `C60A` comme « axe de pression, à trancher ». C'est fait.

| élément | valeur | preuve |
|---|---|---|
| voie | tâche `0x30C`, `word_1418` → descripteur **`0xE1106`** | l. 212326, 212364, 212375 |
| loi | **`0xE2FB2`** : `D03A 0002 01E5 03CA 0258 04B0` = **2 points, 485 → 600, 970 → 1200** | dump `0xE2FB2` |
| fenêtre de plausibilité | `[+04 ; +02] = [450 ; 972]` | descripteur `0xE1106` |
| **valeur de remplacement** | **`+08 = 0x0347 = 839`** (mbar : altitude moyenne) | descripteur `0xE1106`, appliquée l. 212327-212329 |
| variable physique | `word_D03A` | l. 212325 (mise à zéro) |
| copie de travail | **`word_C38E` → `word_C60A`** (l. 172 644-172 646 : `C60A ← C38E`, `C3B4 = 0`) | l. 172 644 |
| sauvegarde de banc | `C940 ← C60A` (l. 172 879-172 882) | étape 12 |
| usages | **axe de pression** des cartes `word_15EA` (`0xE39A8` : `700/850` puis `700/750`), `word_15EE` (`0xE39D8`), et bornes `700…1050` / `800…1500` / `0…1800` mbar | étape 12 + §2.2 |

**Conclusion :** `D03A` / `C38E` / `C60A` / `C940` = **la pression d'environnement (mbar)**,
mesurée sur une voie analogique à loi 2 points **600–1200 mbar** (fenêtre de validité `450…972` codes),
avec repli **839 mbar**. Elle sert d'**axe de correction d'altitude** (`700…1050 mbar` = de 3000 m
d'altitude au niveau de la mer) dans les cartes de débit et de suralimentation.

C'est aussi `D092` (§2.2) : la sélection `byte_C2C9` bits 2/3 (l. 131 773-131 801) choisit entre
`C940` (= pression d'environnement) et `min(C944, C946)` (les deux vues d'une pression de suralimentation)
comme entrée « pression » de la carte de densité de l'air.

---

## 6. Le capteur de pression différentielle — état exact

### 6.1 Ce qui est prouvé

1. **Aucune voie analogique disponible n'est calibrée en mbar de pression différentielle.**
   Les quatre voies « à butée 0,5–4,5 V » (`D052`, `D054`, `D056`, `D060`) ont des lois qui produisent
   des **indicateurs de validité**, pas des pressions :

   | tag | loi | axe brut | sorties | lecture |
   |---|---|---|---|---|
   | `D052` | `0xE31B8` | 20 / 102 / 921 / 1003 | **0 / 0 / 1000 / 1000** | 0 hors 0,5–4,5 V, 100 % dedans ⇒ **drapeau** |
   | `D056` | `0xE325C` | 102 / 922 | 0 → 15000 | **0 puis 150,00 %** ⇒ drapeau + échelle |
   | `D054` | `0xE3218` | 0 … 1023 | 0 → 5000 | **conversion brute → mV** (0…5000 mV), remplacement 100 = 100 mV |
   | `D044`+`D046` | `0xE302A` | 20 / 1003 | 500 / 2500 | paire redondante (5,00 % / 25,00 %) |

2. **Aucun de ces tags n'a de lecteur** dans le demi-programme disponible (étape 12 : les copies
   `C36C`, `C36E`, `C378` sont écrites, jamais lues ; seules les variables d'état `D0xx` sont
   consultées, et uniquement comme conditions de plausibilité).

3. **La charge de suie du FAP n'est pas calculée à partir d'un dP** dans ce code : elle vient
   de l'intégrateur `word_D2BA` alimenté par la progression de combustion
   `(word_C584 − 3000)/3500 × 10 000 → word_D2BE` (l. 166 370-166 432) et de la rampe `word_D26C`
   (`[word_18F6+18h/+1Ah] = 5000`), avec un seuil de demande à **100 %** (`[word_1952+30h] = 10000`,
   **l. 166 523-166 560**) — donc un modèle **débit d'air × température**, pas pression différentielle.

### 6.2 Les trois hypothèses qui restent, et comment les trancher

| hypothèse | argument pour | argument contre |
|---|---|---|
| **H1 — le dP est traité dans le demi-programme manquant** (zone non désassemblée / secteur `0xEC000`+) | les 4 voies sont correctement câblées et calibrées en validité : quelqu'un les consomme | la table `0xE1400` et les descripteurs sont dans la banque **présente** : une exploitation devrait laisser des traces |
| **H2 — le dP n'est utilisé que pour le diagnostic OBD** (surveillance du filtre, P2002) | c'est exactement le rôle des fenêtres `D052`/`D056` : validité + cohérence, sans mise à l'échelle physique | sur un FAP, le dP sert normalement aussi au calcul de charge |
| **H3 — le dP est acquis par le calculateur additif FAP** et rapatrié par une liaison série/CAN | expliquerait l'absence totale de conversion mbar | aucune trame de ce type identifiée à ce stade |

**Protocole de discrimination (3 mesures, sans démontage) :**
1. **contact mis, moteur arrêté** : un dP lit **0 mbar** ⇒ **0,5 V** ⇒ code ≈ **102**.
   La voie qui affiche un code proche de 102 au repos est candidate (les quatre lois ci-dessus ont
   justement **102** comme point bas — c'est le signe qu'elles ont été calibrées sur un capteur
   dont le zéro est à 0,5 V).
2. **ralenti** : 5 à 20 mbar ⇒ 0,52 à 0,60 V ⇒ code 108–125.
3. **pleine charge** : 100 à 300 mbar ⇒ 0,9 à 1,7 V ⇒ code 185–350.
   La seule voie qui **suit le débit** dans ces proportions est le dP.

---

## 7. Mise à jour de l'inventaire des voies

Le fichier `capteurs_ADC_et_chaines_de_mesure.csv` est complété de trois colonnes :
`valeur_remplacement`, `fenetre_plausibilite`, `verdict_etape13`.
Les corrections de fond :

| voie | ancien verdict (étape 12) | verdict étape 13 |
|---|---|---|
| `0x30C` / `D03A` | « commutateur, tout-ou-rien » | **pression d'environnement 600–1200 mbar** (§5) |
| `0x308` / `D060` + `0x30A` / `D066` | deux voies différentes | **un seul capteur à deux éléments**, deux tags (133…2500 mg/coup ; 55…7739 mg/s) |
| `0x310` / `D05E` | « CTN −40…+120 » | **gasoil** (probable), remplacement +74,1 °C |
| `0x30E` / `D06C` | « CTN −40…+130 » | **air d'admission** (prouvé), remplacement +50,1 °C, axe de `D094` |
| `0x318` / `D084` | « CTN −40…+130, la plus fine » | **liquide de refroidissement** (très probable), remplacement −10 °C |
| `0x314` / `D04A` | « seconde EGT » | seconde EGT **avec repli 623,1 °C** = preuve du cas « une seule sonde » (§2.3) |

---

## 8. Ce qui reste ouvert

1. **La table « débit d'air × dP → seuil » demandée** : le second axe n'existe pas sous forme de dP ;
   les cartes de charge identifiées ont pour axes **(débit d'air `word_C3E6`) × (régime `C42E`)**
   (`0xE101E`, `0xE1026`, `0xE104C`, `0xE10A6`) et **(débit d'air) × (température d'air `C904`/`D094`)**
   (`word_15EE` `0xE39D8`, `word_15EA` `0xE39A8`). La carte à deux axes d'air existe donc bien,
   mais son second axe est **thermique ou régime**, pas **pressionnel** — ce qui est cohérent avec
   l'absence de dP exploité (§6).
2. **`word_18F6` (`0xE5368`) et `word_1952` (`0xE63BE`)** : champs déjà relevés (399/300/200 °C,
   rampe 50, init 850 ; 5731/9231 = 300/650 °C, 110 s, 254 s, 200) — il reste à identifier
   **qui** écrit `word_C584` (l'axe de la progression de combustion) : c'est la dernière pièce
   du modèle de charge.
3. **Le secteur `0xEC000–0xEFFFF`** (divergent de `0xFC000`, 14 octets) n'est pas encore désassemblé :
   c'est le candidat n° 1 pour l'hypothèse **H1** du dP.
4. Codes défaut N° de voie → P-code : nécessite la table externe (hors `edc.bin`).

---

### Fichiers produits / mis à jour à cette étape
- `ETAPE13_trois_temperatures_MAF_distance_et_dP.md` (ce document)
- `capteurs_ADC_et_chaines_de_mesure.csv` — 3 colonnes ajoutées, 6 verdicts corrigés
