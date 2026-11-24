# ÉTAPE 16 — `sub_88084` : service, table et blocs. Les timers existent (erratum majeur). Première mesure de période par capture.

Suite de `ETAPE15_sub88084_decodee_rapport_et_pressions.md`.
Preuves = **numéros de ligne de `clean.asm`**. Tout ce qui n'est pas vérifié est explicitement marqué **non tranché**.

---

## 0. Résumé — dont trois erratas

| # | Résultat | Statut |
|---|---|---|
| 1 | `sub_88084` = gestionnaire du **service de diagnostic `0x80`**, appelé par `sub_8A794` qui aiguille sur `byte_F626` (services `0x80/0x81/0x82/0x83/0x10/0x20/0x3E`). | **prouvé** (§1.1) |
| 2 | Les **27 identifiants** renvoient des adresses ; **8 sont maintenant identifiés**, dont 3 nommés. | **prouvé** (§2) |
| 3 | **Id `0x20` = `byte_CA06` = l'octet d'état diagnostic de la voie `0x310`** (capteur gasoil). | **prouvé** (§2.1) |
| 4 | **Id `0x02` = `word_D896` = une PÉRIODE mesurée par capture `CC1_CC13`** — première mesure de temps du dossier. | **prouvé** (§4) |
| 5 | **Id `0x0E` = `word_C0D0` = instantané de `word_F91C`** (même mécanisme que `C080`). | **prouvé** (§2.2) |
| 6 | **ERRATUM MAJEUR** : les timers/GPT **existent** dans ce demi-programme. Ils s'appellent `CC1_T0`, `CC1_T01CON`, `CC1_CC8`, `CC2_CC23`… Mes greps de l'étape 15 (`T0CON`, `CAPREL`, `CC16`) cherchaient les **mauvais noms**. | **erratum** (§3) |
| 7 | **ERRATUM** : `sub_88084` n'est **pas** un simple « identifiant → adresse » : c'est un service complet avec session, longueur, codes d'état et chemin d'erreur. | **erratum** (§1.2) |
| 8 | **`word_F91C` : statut ROUVERT** (ni distance, ni base de temps prouvés). | **non tranché** (§5) |

---

## 1. `sub_88084` — le service, en entier (l. 96088-96409)

### 1.1 Qui l'appelle, et pour quel service

```
l.100408  sub_8A794:  movb rl4, byte_F70A
l.100410              cmpb rl4, #10h            ; pré-condition : 0x10
l.100412              movb rl5, word_F624
l.100413              jmpr cc_NZ, locret         ; pré-condition : word_F624 = 0
l.100414              movb rl3, byte_F626        ; ← NUMÉRO DE SERVICE
l.100416              cmpb rl3, #81h → sub_8FD96
l.100418              cmpb rl3, #82h → sub_8FF0E
l.100420              cmpb rl3, #83h → sub_8F2A2
l.100422              cmpb rl3, #10h → sub_8FDE4
l.100424              cmpb rl3, #20h → sub_8FF18
l.100426              cmpb rl3, #3Eh → loc_8A7F2
l.100428              cmpb rl3, #80h → loc_8A7F8  →  calls sub_88084
```

⇒ **`sub_88084` traite le service `0x80`.** C'est donc un service de lecture de paramètre
locaux — et non un annuaire de mesures interne.

### 1.2 Le protocole complet (erratum de l'étape 15 §1.1)

| ligne | instruction | rôle |
|---|---|---|
| 96090-96091 | `word_BF00 = 0x80` | état de réponse n° 1 |
| 96092-96094 | `byte_F67E` doit valoir **3** | session/mode |
| 96096-96098 | `byte_F627 ≤ 0x7E` | longueur demandée |
| 96100 | `word_BF00 = 0x90` | état de réponse n° 2 |
| 96101-96102 | `sub_888D6`, `sub_8E168` | préparation de la trame |
| 96103-96115 | `byte_FB4E = 3`, `FB4F = byte_FACF\|40h`, `FB50 = byte_FAD0`, `FB51 = 1`, `word_FC10 = 0x12` | **construction de la réponse** |
| 96117 | `word_BF00 = 0x0A0` | état « prêt » |
| 96119-96120 | `byte_FAD0` = **identifiant demandé** | aiguillage |
| 96184-96339 | 27 × `mov r9, #adresse` | **la table** |
| 96340-96347 | `0x11` dans `[word_F62A]`, `sub_8F9F0(2,1)` | **chemin d'erreur** |
| 96350 | `word_BF00 = 0` puis `mov r9,[r0+]` | restitution du contexte |

Ce que j'affirmais à l'étape 15 (« un simple table de pointeurs ») est donc **incomplet** : les
pré-conditions, les codes d'état et le compteur de réponse (`byte_FB4E`) font partie du service.

---

## 2. Les 27 blocs : ce qui est identifié

### 2.1 Tableau de statut complet

| id | adresse | statut | preuve / contenu |
|---|---|---|---|
| `0x01` | `0x09FB2` | non identifié | zone RAM non modélisée |
| **`0x02`** | `0x0D896` | **IDENTIFIÉ : période mesurée** | `word_D896`, 9 références, §4 — `CC1_CC13 − word_D894` |
| `0x03` | `0x0D594` | **identifié : valeur de pointe** | `word_D594` ; l. 204473-204490 : `D594 = DD16` où `DD16` est borné par `[word_1DDE+0]` (prise de maximum) |
| `0x04` | `0x0C564` | partiel | **juste après `word_C562`** (déclaré `ds 2` en `0xC562`) ⇒ mot non nommé suivant |
| `0x05` | `0x0922E` | non identifié | zone non modélisée |
| `0x06` | `0x0CA8A` | **identifié : élément de la structure `0xCA68`** | `word_CA8A` ; initialisé à 0 avec `CA88` dans la tâche de configuration des timers (l. 221447-221449) ; `r14 = #0CA68h` l. 221464 |
| `0x08` | `0x0D63E` | non identifié | 0x3C octets après `word_D602` |
| `0x0B` | `0x08FA8` | non identifié | zone non modélisée |
| `0x0C` | `0x0C1FC` | non identifié | 6 octets après `word_C1F6` |
| `0x0D` | `0x0A804` | non identifié | zone non modélisée |
| **`0x0E`** | `0x0C0D0` | **IDENTIFIÉ : instantané de `F91C`** | `word_C0D0` ; §2.2 |
| `0x0F` | `0x0A47A` | non identifié | zone non modélisée |
| `0x11` | `0x095AA` | non identifié | zone non modélisée |
| `0x13` | `0x0A8EA` | non identifié | zone non modélisée |
| `0x15` | `0x09E68` | non identifié | zone non modélisée |
| `0x16` | `0x0BF64` | partiel | à 22 octets de `word_BF4E` (le tampon de réponse) |
| `0x19` | `0x09CC4` | non identifié | zone non modélisée |
| `0x1C` | `0x0A026` | non identifié | zone non modélisée |
| **`0x20`** | `0x0CA06` | **IDENTIFIÉ : octet d'état voie 0x310** | `byte_CA06` ; §2.3 |
| `0x21` | `0x08738` | non identifié | zone non modélisée |
| `0x22` | `0x08EDA` | non identifié | zone non modélisée |
| `0x23` | `0x09B2E` | non identifié | zone non modélisée |
| `0x31` | `0x0CD46` | non identifié | 150 octets après `word_CCB0` |
| `0x32` | `0x0A0F2` | non identifié | zone non modélisée |
| `0x33` | `0x0BA5A` | non identifié | zone non modélisée |
| `0x34` | `0x0AB82` | non identifié | zone non modélisée |
| `0xF0` | `0x0AFEC` | non identifié | zone non modélisée |
| `0xF4` | `0x09E30` | non identifié | à 20 octets de `0x09E1C` (id `0xF5`) |
| `0xF5` | `0x09E1C` | non identifié | zone non modélisée |
| `0xF6` | `0x0C4AC` | **identifié : paramètre d'appel** | `word_C4AC` ; l. 224415 : `mov r0, word_C4AC` puis `calls sub_CDBAC` |
| `0xF7` | `0x0B700` | non identifié | zone non modélisée |
| `0xFF` | `0x0934A` | non identifié | zone non modélisée |

**Bilan honnête : 8 sur 27.** Les 19 autres tombent dans une région RAM **sans symbole** (§3).

### 2.2 `word_C0D0` (id `0x0E`) = instantané de `F91C`

```
l.170750  jnb word_FD0C.11 …
l.170754  movb byte_D828, #1                 ; drapeau d'événement
l.170755  mov r4, word_F91C
l.170757  mov word_C0D0, r4                  ; ← INSTANTANÉ
…
l.170768  mov r4, word_C0D0                  ; puis, sur un autre événement :
l.170770  cmp r4, word_F91C
l.170772  sub r4, word_F91C
l.170775  sub r4, #1                         ; écart depuis l'instantané (moins 1)
…         et, en fin de séquence (l. 170897 / 170903 / 170909) :
          word_C0D0 = word_F91C  ou  word_C0D0 = 0
```

⇒ `word_C0D0` **n'est pas une mesure** : c'est la **photo de `F91C` au dernier événement**
(exactement le mécanisme de `C080` vu à l'étape 13). Ce que publie l'identifiant `0x0E` est donc un
**compteur d'écart depuis un événement**, pas une grandeur physique.

### 2.3 `byte_CA06` (id `0x20`) = octet d'état de la voie `0x310`

```
l.214410  scxt CC2_CC27, #310h            ; cadre de la voie 0x310 (CTN gasoil, D05E)
l.214420  movbz r11, byte_CA06            ; ← relu comme état précédent
l.214421-214424  r11.4 |= FD2E.8 ; r11.4 |= FD2E.9
l.214428  sub_C4AAE(0F864h)               ; lecture brute
l.214430  sub_C66EA                       ; cadrage + diagnostic
l.214431  mov word_D05E, r9
l.214436-214446  sub_CE9B4 ×2 (codes 0x78, 0x76)
l.214454  mov r7, r11
l.214455  movb byte_CA06, rl7             ; ← RÉÉCRIT avec le mot d'état
l.214456  movbz r0, byte_CA07 ; mode 0..4 → 4 branches
```

⇒ **`0xCA04` / `0xCA06` / `0xCA07` = un petit bloc value / status / mode**, et `byte_CA06` est
l'**image de l'octet d'état diagnostic** (`byte_E000`/`byte_E006` du cadre). C'est la **première
identification certaine d'un bloc de diagnostic** : elle montre que le service `0x80` publie bien des
**variables internes de régulation**, pas des copies retraitées. C'est un point important pour la
suite de la chasse au dP.

---

## 3. ERRATUM MAJEUR — les timers sont bien là

Mon « relevé exhaustif » de l'étape 15 §3 était **faux** : je cherchais `T0CON`, `T1CON`, `CAPREL`,
`CC16`… Les noms réels viennent d'un autre fichier d'inclusion :

| registre réel | occurrences | rôle |
|---|---|---|
| **`CC1_T0`** | **126** | **base de temps libre** (GPT1 timer 0) — photographiée dans `word_FC04` (`mov word_FC04, CC1_T0`, ex. l. 97007, 98180, 98671, 98757…) |
| `CC1_T01CON` | 10 | configuration des timers 0 et 1 |
| `CC1_T0REL`, `CC1_T1REL` | 2 / 5 | recharges |
| `CC1_T1`, `CC2_T7` | 4 / 4 | timers 1 et 7 |
| `CC2_T78CON`, `CC2_T7REL` | — / 6 | configuration / recharge de T7 |
| **`CC1_CC0`, `CC1_CC8`, `CC1_CC15`** | 3 / 5 / 5 | **canaux CAPCOM1 (capture/compare)** |
| **`CC1_CC13`** | **lu l. 174828** | **canal de capture exploité pour une mesure de période (§4)** |
| `CC2_CC23` | 2 | canal CAPCOM2 |
| `CC2_CC16IC`, `CC2_CC23IC`, `CC2_CC24IC`, `CC2_CC31IC` | 1 chacun | registres d'interruption CAPCOM2, écrits par `sub_8874E` |
| `CC1_CC0IC`, `CC1_CC8IC`, `CC1_CC15IC` | — | idem CAPCOM1 |

Et `sub_8874E` (l. 96795) est le **prologue commun d'interruption** :
```
push CC1_CC0IC ; push CC1_M0 ; push CC1_T01CON
scxt DPP0..#0 / DPP1..#0 / DPP2..#2 / DPP3..#3
bfldl CC1_M0, #0Fh, #4 ; bfldl CC1_T01CON, #4Fh, #41h ; bfldl CC2_T78CON, #4Fh, #41h
sauvegarde CC1_CC8, CC1_CC15, CC1_M2, CC1_M3, CC1_CC8IC, CC1_CC15IC
calls 8, sub_88A6C            ; ← répartiteur
restitution de tous les registres
r14 = r4 & 3 ; word_BF0C = r14 ; si r14 ≥ 3 → chemin de trap (loc_88810)
```

**Conséquence de fond** : le temps est mesuré ici, par `CC1_T0` et par des **captures**
(`CC1_CC13` au moins). Donc **la vitesse peut parfaitement être calculée dans ce demi-programme** ;
ma « preuve négative définitive » de l'étape 15 tombe.

---

## 4. Première mesure de temps du dossier : `CC1_CC13` → `word_D896`

```
l.174828  loc_AE6E0:
l.174828    mov r4, CC1_CC13          ; ← valeur de capture à l'instant du front
l.174829    sub r4, word_D894         ; − capture précédente  = PÉRIODE (en ticks de timer)
l.174831    mov word_D896, r4         ; ← D896 = période mesurée  (= identifiant diag 0x02)
l.174832    cmp r4, #2774h            ; 10100
l.174833    jmpr cc_SGE, loc_AE6FE
l.174834    cmp r4, #26ACh            ; 9900
l.174835    jmpr cc_SLE, loc_AE6FE
l.174837    movb byte_D8A0, #2        ; ← hors fenêtre : code 2
loc_AE6FE:
l.174841    r4 = word_D896 >> 1       ; ← nouvel essai sur la DEMI-période
l.174845    cmp r4, #2774h … cmp r4, #26ACh
l.174851    word_D896 = D896>>1 ; byte_D8A0 = 2
loc_AE726:
l.174857    si byte_D8A0 == 2 :
l.174859       word_D362 = word_D896          ; ← valeur validée exportée
l.174862       word_D894 = CC1_CC13           ; ← mémorisation de la capture
l.174864       MDL = D896 ; div r2 (#14h = 20) → r5 = MDL
```

Ce qui est **prouvé** :
1. une **période** est mesurée par différence de deux captures `CC1_CC13` ;
2. elle est **validée dans une fenêtre de 9900 à 10100 ticks** (soit **±1 % autour de 10 000**) ;
3. un **repli sur la demi-période** existe (détection de front alterné) ;
4. la valeur validée est copiée en `word_D362` puis **divisée par 20**.

Ce que je **ne** conclus pas : que ce soit la vitesse. Une fenêtre de ±1 % est beaucoup trop étroite
pour un signal de vitesse (qui varie de 0 à 200 km/h). Elle convient en revanche à un **signal à
fréquence fixe** — synchronisation, PWM de consigne, ou horloge d'un capteur. **Il faut identifier la
source de `CC1_CC13` avant d'affirmer quoi que ce soit** ; c'est précisément ce que je propose de faire
ensuite (§6, action 1).

---

## 5. `word_F91C` : statut **rouvert** (ni distance, ni base de temps)

Je dois être précis, car j'ai déjà corrigé deux fois :

| étape | affirmation | état |
|---|---|---|
| 13 | `F91C` = **distance parcourue** | **non démontré** |
| 14 | `F91C` = **base de temps** (un seul écrivain, décrément) | **trop affirmatif** |
| 16 | — | **non tranché** |

Les deux faits solides :
- `F91C` possède **un seul écrivain** (`233544-233559` : chargement à `ONES`, puis `sub word_F91C, ONES`
  avec rebouclage) et **~250 lecteurs, tous en différence** ;
- la **base de temps réelle** est `CC1_T0` → `word_FC04` (126 photographies). Il y a donc **déjà** une
  horloge : que `F91C` en soit une seconde serait redondant, ce qui **affaiblit** l'hypothèse de l'étape 14
  sans la réfuter.

Le point décisif, et il est vérifiable : **à quelle cadence tourne la tâche `0x412`** qui décrémente
`F91C` ? Si elle est déclenchée par un **événement angulaire** (N impulsions de vilebrequin), `F91C`
compte des **incréments de distance/angle** et l'étape 13 avait raison. Si elle est déclenchée par un
**timer**, c'est une horloge. **Je ne l'ai pas encore établi** → je le laisse ouvert plutôt que de
trancher à tort. C'est l'action 2 du §6.

---

## 6. Actions suivantes, par ordre de valeur

1. **Identifier la source de `CC1_CC13`** : chercher où `CC1_Mx`/`CC1_T01CON` configurent le mode
   *capture* du canal 13 (front montant/descendant, source de pin). Le mode est écrit dans les
   `bfldl CC1_M2/CC1_M3` — donc **`CC1_M2`/`CC1_M3` portent l'affectation des canaux 8-15**.
   Cela donnera la broche, donc le capteur (vilebrequin ? boîte ? autre).
2. **Cadence de la tâche `0x412`** (qui décrémente `F91C`) : lire son point d'appel et le compteur
   de tâche associé.
3. **Les 19 blocs restants** : ils sont dans `0x8000-0xBDAB`, sans symbole. La seule voie est de
   trouver la **routine d'écriture indexée** ; indice nouveau et précieux : `0xCA68` est la base
   d'une **structure** qui contient `CA8A` (id `0x06`), et `0xCA04/CA06/CA07` celle de l'id `0x20`.
   Chercher les accès `#0CA68h` / `#0CA04h` élargit la piste sans toucher à la zone non modélisée.
4. **Le dP** : l'identification de `byte_CA06` (§2.3) prouve que ce service publie des **variables
   internes** — donc si un dP est publié, c'est **une variable de régulation**, pas une copie
   d'affichage. Les candidats restants sont parmi les 19 blocs non identifiés, dont 22 sont dans la
   région non modélisée.
