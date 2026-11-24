# ÉTAPE 94 — `C562` = la vitesse, confirmé par cinq voies · et le régulateur : le **codage**

Tu voulais la confirmation, et « la retrouver partout ». Voilà trois axes de plus, deux tests
d'arrêt, un transfert sans à-coup, et — en prime — **le codage du régulateur trouvé dans le
fichier**.

---

## 1. ★★★ `C562` = vitesse : la preuve par les **axes**

J'ai scanné les 512 Ko à la recherche du **tag `0xC562`** suivi d'un nombre de points et d'un axe
**strictement croissant** (un vrai axe, pas une coïncidence de code). Résultat : **trois** enregistrements,
tous des axes de vitesse.

| EA | type | n | axe | traduction |
|---|---|---|---|---|
| `0xE4FA4` | courbe 1-D | 8 | `0 · 5000 · 6000 · 7000 · 8000 · 9000 · 11000 · 20000` | **0 · 50 · 60 · 70 · 80 · 90 · 110 · 200 km/h** |
| `0xE87EE` | courbe 1-D | 6 | `1500 · 2100 · 7000 · 9000 · 11500 · 20000` | **15 · 21 · 70 · 90 · 115 · 200 km/h** |
| `0xE869C` | carte (avec `C3D2`) | 6 | `0 · 300 · 10000 · 12000 · 14016 · 18000` | **0 · 3 · 100 · 120 · 140,16 · 180 km/h** |

**La signature est dans la forme de l'axe**, pas seulement dans les nombres : un grand saut initial
(`0 → 5000`, `1500 → 2100`) puis des **pas réguliers de 1000 (= 10 km/h)**, et **20 000 en bout
(200 km/h)**. Un axe de quantité est **lisse et progressif** ; celui-ci a des paliers de vitesse.

Et `0xE4FA4` a ses **valeurs identiques à son axe** (`0 5000 6000 … 20000`) : c'est une **courbe de
conversion linéaire** posée là pour être re-graduée par le calibrateur, comportement classique d'un
axe vitesse.

### 1.1 ★ La calibration existe en **double** dans le fichier

| exemplaire | miroir | écart |
|---|---|---|
| `0xE4FA4` | `0xF4FA4` | +0x10000 |
| `0xE869C` | `0xF869C` | +0x10000 |
| `0xE87EE` | `0xF87EE` | +0x10000 |

Les trois cartes sont **dupliquées à l'identique** : il y a **deux copies du Datensatz** dans les
512 Ko. C'est cohérent avec le CSV `duplication_datensatz.csv` déjà produit. À retenir pour tous les
dumps futurs : **vérifier laquelle des deux copies est lue** (`word_15xx` pointe l'une des deux).

---

## 2. ★★★ `C562` = vitesse : la preuve par le **code**

### 2.1 Deux tests d'« arrêt » explicites

```asm
; sub_A7C5A, l.163014
  mov  r4, word_C562
  jmpr cc_NZ, loc_A7D38        ; ★ si la vitesse N'EST PAS nulle → on saute tout le bloc
  movb rl4, byte_C2C0
  cmpb rl4, #1
  …
```

```asm
; sub_C0496, l.205739
  mov  r5, word_C562
  jmpr cc_NZ, loc_C04D0        ; idem : test de nullité → « véhicule à l'arrêt »
  cmp  r4, #0                  ; (r4 = C42E = régime)
```

Un test **« == 0 »** sur une grandeur, à deux endroits, pour distinguer **arrêt / roulage** : c'est
la façon dont on teste une vitesse, jamais une quantité injectée.

### 2.2 Un **transfert sans à-coup** (bumpless transfer) sur `C562`

```asm
; loc_A3B12, l.155935
  jnb  word_FD02.8, loc_A3B4C
  bclr word_FD02.8
  mov  r3, word_C562
  mov  word_D6E0, r3           ; ★ l'état du limiteur est RÉ-ARMÉ à la vitesse courante
  mov  word_D6DE, ZEROS

loc_A3B4C:
  mov  r4, word_189C
  mov  r12, [r4+#0Eh]
  mov  r13, word_C562          ; ★ entrée du limiteur de pente
  mov  r14, word_D6E0
  mov  r15, word_D6DE
  calls 9, sub_97E16
```

`sub_97E16` = **limiteur de pente à état** (référence + intégrale), et `word_FD02.8` / `.11` sont les
**événements de ré-armement**. On filtre donc la vitesse avant de l'utiliser — comportement
caractéristique d'une mesure bruitée (§8.5 de l'étape 93).

### 2.3 Les seuils de « roulage » (OBD)

```asm
; sub_C7398, l.217467
  r2 = [word_16F0]      → 1000   (= 10 km/h)
  cmp r2, word_C562 ; cc_SGE → byte_CA39 = 2   sinon = 4
; l.217489
  r2 = [word_16F0+2]    → 9000   (= 90 km/h)
  cmp r2, word_C562 ; cc_SGE → byte_CA39 = 8
```

**10 km/h et 90 km/h** : ce sont les seuils réglementaires de détection de roulage pour les
moniteurs OBD. Impossible avec une quantité.

### 2.4 Un seuil de 5 km/h dans un bloc de calibration

```asm
; loc_B74E6, l.189946
  mov r4, word_1432        ; EA 0xE1264
  mov r5, [r4+#2Ch]        ; → 500 = 5,00 km/h
  cmp r5, word_C562
```

### 2.5 Bilan des six voies

| voie | statut |
|---|---|
| 3 axes taggés `C562` (50→200 km/h, 15→200, 0→180) | **lu** |
| test `C562 == 0` = arrêt (2 sites) | **lu** |
| transfert sans à-coup sur `C562` | **lu** |
| seuils OBD 10 / 90 km/h | **lu** |
| seuil 5 km/h (`0xE1264+0x2C` = 500) | **lu** |
| défaut `8000` = 80,00 km/h, borne `31621`, timeout `2560` | **lu** ; unité **inférée** (mais corroborée par les axes) |

**Verdict : `C562` est la vitesse véhicule, exprimée en 0,01 km/h. Ce n'est pas un IQ.**
(l'errata 88/91 de l'étape 93 est donc confirmé et renforcé.)

---

## 3. « On doit la retrouver partout » — où, exactement

**99 lectures de `word_C562` réparties dans 88 blocs de code.** Répartition :

| zone | blocs | ce qu'on y fait |
|---|---|---|
| `seg015` `loc_B45xx`–`loc_B53xx` (l.1851xx–18647x) | **~45** | la **forêt de limiteurs** : `C562` comparée à `[word_14AA]` (`40 / 200 / 500 / 20000 / 4000 / 400`), à `[word_14B4]`, à `[word_1430]`, avec saturation `±0x7FFF` — un **gradient** `C562 − D9CE` (`unk_1DA8`) puis des clamps |
| `seg015` `loc_B57xx`–`loc_B59xx` | ~8 | **le régulateur** : `C6EA − C562` = écart, rampe `unk_1FE8` (§5) |
| `seg014` `loc_A3Bxx` | ~4 | filtrage / transfert sans à-coup (§2.2) |
| `seg015` `loc_B74E6`, `loc_B764C` | 2 | seuils de calibration (`0xE1264+0x2C` = 5 km/h) |
| `seg015` `loc_B89B2`, `loc_B8D42`, `loc_B8E9C`, `loc_BA852`, `loc_BC06E` | 5 | limitations par la vitesse (post-injection / EGR / couple) |
| `seg017` `sub_C7398` | 2 | **statut de roulage OBD** (10 / 90 km/h) |
| `seg016` `sub_CF8A4/C8C8/CFA80/CFDD2` | 4 | **le sélecteur de source et les deux tops** (§8.4 de l'étape 93) |
| `seg014` `sub_A7C5A`, `seg020` `sub_C0496` | 2 | tests d'arrêt |

**C'est cohérent avec une vitesse** : en ECU diesel, la vitesse est lue partout (coupure du
post-chauffage, EGR, couple, régulateur, moniteurs OBD), alors qu'un débit de référence serait lu
presque uniquement par la chaîne d'injection.

---

## 4. ★★★ Le régulateur : **le codage trouvé** (`byte_C2BD`)

### 4.1 La découverte

```asm
sub_AF50E:                          ; l.176670  → « régulateur présent ? »
  movbz r4, byte_C2BD
  and   r4, #70h                    ; ★ bits 4-5-6
  jmpr  cc_Z, loc_AF51C
  mov   r4, #1
  rets
loc_AF51C:
  mov   r4, #0
  rets

sub_AF520:                          ; l.176692  → « quelle consigne par défaut ? »
  movb rl4, byte_C2BD
  andb rl4, #70h
  jmpr cc_NZ, loc_AF52E
  mov  r4, #0
  rets
loc_AF52E:
  movbz r4, byte_C2BD
  and   r4, #40h
  jmpr  cc_Z, loc_AF546
  mov   r4, word_1A80
  mov   r5, [r4+#4]                 ; ★ variante 0x40
  mov   word_C6EA, r5
  jmpr  cc_UC, loc_AF566
loc_AF546:
  and   r4, #20h
  jmpr  cc_Z, loc_AF55E
  mov   r4, word_1A80
  mov   r5, [r4+#2]                 ; ★ variante 0x20
  mov   word_C6EA, r5
  jmpr  cc_UC, loc_AF566
loc_AF55E:
  mov   r4, word_1A80
  mov   word_C6EA, [r4]             ; ★ variante 0x10
loc_AF566:
  mov   r4, #1
  rets
```

| `byte_C2BD & 0x70` | signification | consigne par défaut |
|---|---|---|
| **`0x00`** | **régulateur NON codé** | — (les deux routines renvoient 0) |
| `0x10` | variante A | `[word_1A80 + 0]` |
| `0x20` | variante B | `[word_1A80 + 2]` |
| `0x40` | variante C | `[word_1A80 + 4]` |

Les deux appelants sont **dans le bloc régulateur** : `loc_B573C` (l.186861) appelle `sub_AF50E` et
`loc_B57AC` (l.186886) appelle `sub_AF520`. C'est l'**initialisation** du régulateur.

### 4.2 Le bloc des consignes : `0xE7F76` (handle `0x1A80`)

```
+0x00  30000  30000  30000  30000          ; ★ TROIS consignes par défaut (+0, +2, +4) + une de plus (+6)
+0x08  [C42E][8][800 1500 1750 2000 2750 3000 4000 4800]   ; courbe sur le RÉGIME
```

**30 000 = 300,00 km/h** : ce n'est pas une consigne réaliste, c'est une **sentinelle « pas de
consigne »** — et on la retrouve à l'identique dans `word_1B70` (`[0, +30000, 0, −29968, +30000, 0,
+10000, 0]`), ce qui confirme le rôle de borne.

### 4.3 ★ Et voilà pourquoi ton régulateur « ne fait rien » dans ce dump

```
byte_C2BD = [word_141C + 3] = 0x00   ⇒  bits 0x70 = 0  ⇒  RÉGULATEUR NON CODÉ
```

Attention : **ce n'est pas le même octet** que celui de la vitesse. Voir l'errata ci-dessous.

---

## 5. ★ ERRATA de l'étape 93 — deux blocs de codage **contigus**, pas un seul

L'étape 93 attribuait à `0xE1148` (handle `0x141E`) des champs qui viennent en réalité de
**`0x141C`** :

| handle | EA | taille | contient |
|---|---|---|---|
| `0x141C` | **`0xE111E`** | **42 octets** | `+0x03` → `byte_C2BD` (**codage régulateur**), `+0x0B` → coupe la boucle, `+0x0C` → active le PI `unk_2020`, `+0x0E` → `byte_C2B7` (**masque trames CAN**), `+0x15`…`+0x28` → `C2C0 C2BF C2B8 C2CC C2C7 C2C3 C2D0 C2D1 C2CE C2CF C2CB C2CD C2C8 C2BE C2C6 C2CA C2C4 C2C1` |
| `0x141E` | **`0xE1148`** | **52 octets** | `+0x05` → `byte_C2BC` (**origine vitesse/distance**), `+0x09`, `+0x33`, et les champs `+0x14/+0x19/+0x1B/+0x21…+0x26/+0x2A/+0x2E/+0x2F…+0x33` |

Et la géométrie le confirme : **`0xE1148 = 0xE111E + 0x2A`** — les deux enregistrements sont
**accolés** dans une même **table de codage** (comme les autres entrées `0x1F8A`, `0x232E`, `0x1F0A`
relevées dans `zone_0xE1129.csv`).

**La valeur de `+0x05` sur `0x141E` est bien `0x01`** (origine vitesse = impulsions) : cette
conclusion de l'étape 93 est **maintenue**.

### 5.1 ★★ Conséquence importante : **`byte_C2B7 = 0x08`**

`byte_C2B7 = [0x141C + 0x0E] = 0x08`, et les bits de ce masque sont :

| bit | trame | état dans ce dump |
|---|---|---|
| `& 0x01` | **`0x349` (rapport de boîte) et `0x389`** | **NON armées** |
| `& 0x08` | `0x412`, `0x50E`, `0x7E2`, `0x0A8` (bloc ESP/roues) | **armées** |
| `& 0x06` | `0x34D` (si `== 6`) | non |

⇒ **Dans cette calibration, le rapport de boîte n'est PAS reçu** : tout le décodeur `sub_9B796`
(étape 25) et `byte_C240` restent alimentés par le **défaut** `[word_1658+8]`. C'est un point à
vérifier sur ton véhicule : si ton 4HX communique bien le rapport, `C2B7 & 1` doit être à 1 **dans
l'EEPROM de codage** (le flash, lui, dit 0).

---

## 6. L'état du régulateur : ce qu'on sait déjà, et ce qui reste

| élément | rôle | preuve |
|---|---|---|
| `byte_D9EE` | **régulateur actif** (0/1/2) | `loc_B573C`, `loc_B58B8` |
| `byte_D9EF` | **état interne 0…3** | `loc_B57BC` → `loc_B58A0` |
| `D3EE`…`D3FA` | **publication diagnostic** de l'état | `loc_B5788`, `loc_B597E` |
| `word_C6EA` | **consigne de vitesse** | `sub_AF520` §4 |
| `word_C562` | **vitesse mesurée** | §1-2 |
| `D9FA = C6EA − C562` | **écart consigne/mesure** | l.186927 |
| `word_1B70` | seuils : `0 · +30000 · 0 · −29968 · +30000 · 0 · +10000 · 0` | l.186929-187010 |
| `word_1B7A` | rampe : `1 · 1000 · 820 · 220 · 512 · 1024 · 1024 · 9` | l.187068 |
| `word_1B6C` | descripteur de **défaut `0x40DF`** | l.187047, 186875 |
| **`unk_1FE8`** | **rampe à 10 arguments** — 2 sites : `l.187031` (régulateur) et `l.196459` | 2 sites |
| `word_C69A` | **sortie du régulateur** — 3 écritures, **AUCUN lecteur** ⇒ publication diag | grep |
| `byte_DB78` | aiguillage d'un second limiteur (`sub_B7DAA`) | `loc_BB4D2` |
| `[0x141C + 0x0B]` | **coupe** : si non nul → `DB64 = DB66 = 0` | l.196410, 196439, 195558 |
| `[0x141C + 0x0C]` | **activation du PI `unk_2020`** | l.196447 |

---

## 7. Ce que je propose pour la suite (dans cet ordre)

1. **Décoder `unk_1FE8`** par ses deux sites d'appel : `l.187031` (régulateur) et `l.196459` (bloc
   `DB64/DB66/DB6A/DB68`). Les mêmes 4 pointeurs + 5 arguments sur la pile ⇒ on peut nommer chaque
   argument par différence. **C'est la clé de « la reprise de la demande conducteur ».**
2. **Le PI `unk_2020`** (l.196447) : relever ses gains et sa sortie. Ce n'est **pas** `0xE2728`.
3. **`C6EA` vs les cartes de souhait** : `C6EA` est une consigne de **vitesse** ; la demande du
   régulateur doit être convertie en **quantité**. Chercher où `C562`/`C6EA` alimentent une carte
   `mg` — ou bien où `C69A`/`C698`/`C690` sont produits à partir d'une vitesse (c'est la
   « carte inversée » que tu décris).
4. **`word_1B70` / `word_1B7A` / `word_1B6C`** : dumper les trois blocs (handles `0x1B6C`, `0x1B70`,
   `0x1B7A` — `0x1B7A` déjà lu : `1 1000 820 220 512 1024 1024 9`).
5. **Interrupteur de frein / d'embrayage** : aucun port n'est symbolisé ; la seule piste propre est
   `[word_1468]` (`and #800h`, `and #200h` en `loc_BB4E0`) — un mot de **bits d'état véhicule** dont
   `0x800` et `0x200` sont testés juste avant le calcul de la consigne. **À creuser en priorité.**
