# ÉTAPE 7 — `word_C3E6` : dans quelles cartographies passe-t-elle, et où sont-elles physiquement ?

Suite de l'étape 6. Question posée : **« j'ai quand même un doute sur l'injection — regarde si tu as `C3E6` dedans et dis-moi dans quelles maps elle passe, éventuellement les adresses dans les zones de calibration 0x6/70000+ (les deux derniers segments). »**

Réponse courte en fin de §1. Tout ce qui suit est vérifiable dans `edc.bin` ; les hypothèses sont explicitement marquées **HYPOTHÈSE**.

Rappel de mapping : **EA = offset BIN + 0x80000**. Les deux « derniers segments » de la question sont donc EA `0xE0000`–`0xEFFFF` (BIN `0x60000`) et EA `0xF0000`–`0xFFFFF` (BIN `0x70000`).

---

## 1. Réponse directe

| Question | Réponse | Base |
|---|---|---|
| `C3E6` est-elle « dedans » ? | **Oui.** 3 sites d'appel de `unk_1D50` la passent en **`r14`** (2ᵉ axe) : `clean.asm` lignes **181913**, **181949** (dans `loc_B26D2` / `loc_B2706`) et **182174** (dans `sub_B293A`). | code, segment 015 |
| Dans combien de cartes ? | **2 cartographies distinctes** ont `0xC3E6` comme **axe Y** (+ leurs copies dans le 2ᵉ segment). Une **3ᵉ carte** utilise l'axe alternatif `0xC3EC`. | Datensatz, segments 0xE/0xF |
| Adresses | `0xE8444` (16×16, grille `0xE848C`–`0xE868B`), `0xE8872` (6×6, grille `0xE8892`–`0xE88D9`), alternative `0xE87D6` (2×2, grille `0xE87E6`–`0xE87ED`). Copies identiques en `0xF8444`, `0xF8872`, `0xF87D6`. | §5 |
| Est-ce une quantité / durée d'injection ? | **Non.** C'est un **axe** (grandeur d'entrée). Elle n'est ni produite ni consommée par le calcul de quantité (étape 6). | code |

**Correction de formulation par rapport à l'étape 6** : `word_C3E6` n'est pas « une grandeur d'entrée du calcul d'injection » mais l'**index de l'axe Y de deux Kennfelder** qui délivrent la **borne basse** (`word_C690`) et un **plafond** (`word_C626`) de la commande. Formulation exacte : c'est une **grandeur de charge/remplissage** (voir §7) servant de **coordonnée de cartographie**.

---

## 2. Ce qui manquait, et comment ça a été résolu

L'étape 6 s'était arrêtée sur un mur : les descripteurs de cartes utilisés par le code (`word_1B40`, `word_1B46`, `word_1B4C`…) sont des **mots de la mémoire basse `0x00000`–`0x7FFF`** qui n'existe pas dans notre image. On ne peut donc **pas** remonter du code vers l'adresse physique des tables par le code seul.

Solution employée : **prendre le problème par l'autre bout**, c'est-à-dire décoder directement les **deux segments de calibration** (`0xE0000`, `0xF0000`) pour y retrouver les tables, puis faire la jointure avec le code via les **grandeurs d'axe**.

Résultat : le format est décodé ; **44 cartographies distinctes** et **339 axes** sont localisés, chacun présent **en deux exemplaires** (segments `0xE` et `0xF`) — soit 88 entrées et 678 axes dans les deux fichiers joints (`axes_datensatz.csv`, `cartographies_datensatz.csv`). Toute carte du segment `0xE` a bien sa jumelle à `+0x10000` (vérifié : aucune manquante).

---

## 3. Format d'un bloc cartographie dans le Datensatz (décodé et vérifié)

```
 <tag_X : 16 bits>  <nX : 16 bits>  <nX valeurs 16 bits croissantes>     ← axe des X
 <tag_Y : 16 bits>  <nY : 16 bits>  <nY valeurs 16 bits croissantes>     ← axe des Y
 <nX × nY valeurs 16 bits>                                             ← la grille
```

* 3 champs, aucun séparateur, aucun padding ; tout est en **mots de 16 bits little-endian**.
* Le **tag** est un mot de la zone `0xC000`–`0xDFFF` — voir §4 pour sa signification.

### Preuves du décodage

1. **Statistique sur le tag le plus fréquent.** Le mot `0xC42E` apparaît **208 fois** dans `0xE0000`–`0xEFFFF`. Les **208 fois**, il est suivi (a) d'un compteur `n` entre 2 et 32, puis (b) de `n` valeurs **strictement croissantes**. 208/208 sur un mot de données brut est impossible par hasard.
2. **Fermeture des chaînes.** En supposant `grille = nX × nY` mots, la fin de la grille doit retomber pile sur l'en-tête du bloc suivant. Sur 172 chaînes candidates testées, **88 retombent exactement** sur un en-tête valide (les 84 autres sont des faux positifs internes, écartés).
3. **Contre-épreuve (faux positif).** Le mot `0x141E` apparaît 2 fois dans le Datensatz, mais **au milieu** d'un axe (dans la suite `0xE23DC`), pas en tête : il est écarté. Le filtre n'accepte donc pas n'importe quoi.

### Exemple commenté — la carte à axe `C3E6`, EA `0xE8444` (BIN `0x68444`)

```
0xE8444 : 2E C4        tag_X = 0xC42E            (grandeur « régime »)
0xE8446 : 10 00        nX    = 16
0xE8448 : 00 00 20 03 E8 03 E2 04 DC 05 D6 06 D0 07 CA 08 C4 09 B8 0B AC 0D A0 0F 94 11 8E 12 88 13 50 14
                       X = 0, 800, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 3000, 3500, 4000, 4500, 4750, 5000, 5200
0xE8468 : E6 C3        tag_Y = 0xC3E6            ← NOTRE MOT
0xE846A : 10 00        nY    = 16
0xE846C : B8 0B A0 0F 94 11 88 13 7C 15 70 17 64 19 58 1B 4C 1D 40 1F 34 21 28 23 1C 25 10 27 04 29 EC 2C
                       Y = 3000, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500, 10000, 10500, 11500
0xE848C : grille 16 × 16 = 256 mots = 512 octets, jusqu'à 0xE868B
```

---

## 4. Signification du tag — établie, pas supposée

**Le tag est l'adresse RAM de la grandeur qui indexe l'axe.** Trois vérifications croisées code ↔ Datensatz :

| Tag | Vérification côté code |
|---|---|
| `0xC42E` | `mov r4, word_C42E / mov word_C91C, r4` (listing `131277`, `132002`, `131388`, … — **59 occurrences**) : `word_C91C` est le **régime** ; `r13` = `word_C91C` dans **37 des 72** appels à `unk_1D50`. Tag `0xC42E` = 208 axes → l'axe X « régime » de la quasi-totalité des cartes. |
| `0xC6A2` | `mov r5, word_C6A2 / mov word_C94C, r5` (listing `132004`–`132005`, `147315`–`147316`, `153960`–`153961`, … — **9 occurrences**) : `word_C94C` est une **copie** de `word_C6A2` qui sert de `r14` dans **12** appels. Tag `0xC6A2` = 40 axes → cohérent. |
| `0xC3E6`, `0xC3EC`, `0xC3BA`, `0xC3D2`, `0xC562` | tous présents dans le catalogue des tags **et** passés en `r14`/`r13` dans le code (ex. `sub_972FA` : `unk_1D50(word_15E4, word_C42E, word_C3D2)` ; `loc_B28E4` : `r14 = word_C562`). |

Conséquence pratique : on peut **apparier un site d'appel du code avec une table du Datensatz** par le tag, même sans connaître les descripteurs `0x1Bxx`.

---

## 5. Les cartographies qui utilisent `C3E6` — adresses physiques

| En-tête EA | En-tête BIN | Axe X (tag, n) | X min → max | Axe Y (tag, n) | Y min → max | Grille EA | Taille | Valeurs |
|---|---|---|---|---|---|---|---|---|
| `0xE8444` | `0x68444` | `0xC42E` (16) | 0 → 5200 | `0xC3E6` (16) | 3000 → 11500 | `0xE848C`–`0xE868B` | 16×16 = 512 o | 0..7600 |
| `0xE87D6` | `0x687D6` | `0xC42E` (2) | 200 → 620 | `0xC3EC` (2) | 700 → 850 | `0xE87E6`–`0xE87ED` | 2×2 = 8 o | 8000..8000 |
| `0xE8872` | `0x68872` | `0xC42E` (6) | 0 → 5000 | `0xC3E6` (6) | 0 → 10000 | `0xE8892`–`0xE88D9` | 6×6 = 72 o | 0..0 |
| `0xF8444` | `0x78444` | `0xC42E` (16) | 0 → 5200 | `0xC3E6` (16) | 3000 → 11500 | `0xF848C`–`0xF868B` | 16×16 = 512 o | 0..7600 |
| `0xF87D6` | `0x787D6` | `0xC42E` (2) | 200 → 620 | `0xC3EC` (2) | 700 → 850 | `0xF87E6`–`0xF87ED` | 2×2 = 8 o | 8000..8000 |
| `0xF8872` | `0x78872` | `0xC42E` (6) | 0 → 5000 | `0xC3E6` (6) | 0 → 10000 | `0xF8892`–`0xF88D9` | 6×6 = 72 o | 0..0 |

Les trois cartes existent **en deux exemplaires**, aux mêmes adresses relatives dans les deux segments (`0xE` et `0xF`), et sont **identiques octet pour octet** entre les deux exemplaires (vérifié : 0/256, 0/36 et 0/4 valeurs différentes). Elles n'appartiennent donc **pas** à la partie qui varie d'un segment à l'autre (§6).

### Grille principale — `0xE8444`, 16×16, EA `0xE848C` (lignes = 16 mots)

```
 Y=3000  r 0 : 2482 2816 3070 3610 4064 4064 4064 4064 4064 4064 4064 4064 4064 4064 4064 4064
 Y=4000  r 1 : 2482 2816 3070 3610 4064 4064 4064 4064 4064 4064 4064 4064 4064 4064 4064 4064
 Y=4500  r 2 : 2432 2800 3072 3500 4000 4800 4800 4800 4800 4800 4800 4800 4800 4800 4800 4800
 Y=5000  r 3 : 2320 2766 3050 3456 3830 4300 5000 5800 5800 5800 5800 5800 5800 5800 5800 5800
 Y=5500  r 4 : 2288 2760 3050 3440 3822 4250 4638 5100 5770 6500 7200 7200 7200 7200 7200 7200
 Y=6000  r 5 : 2240 2744 3050 3434 3812 4250 4622 5072 5550 6044 6600 7050 7450 7600 7600 7600
 Y=6500  r 6 : 2226 2738 3050 3428 3812 4200 4622 5044 5500 5970 6490 7000 7550 7600 7600 7600
 Y=7000  r 7 : 2150 2650 2950 3300 3700 4100 4500 4900 5350 5820 6350 6900 7390 7500 7500 7500
 Y=7500  r 8 : 2100 2550 2850 3200 3550 3950 4350 4750 5200 5600 6150 6680 7130 7500 7500 7500
 Y=8000  r 9 : 2050 2500 2700 3000 3300 3600 3900 4250 4580 4980 5400 5900 6390 6890 7000 7000
 Y=8500  r10 : 2050 2500 2700 2950 3150 3400 3700 3950 4200 4550 4900 5400 5940 6500 6500 6500
 Y=9000  r11 : 2000 2400 2600 2850 3050 3250 3500 3750 4000 4250 4600 5070 5650 6350 6400 6400
 Y=9500  r12 : 1750 2150 2350 2600 2800 3050 3300 3550 3790 4100 4470 5000 5384 5594 5600 5600
 Y=10000 r13 : 1850 2250 2450 2650 2800 3000 3200 3400 3600 3920 4200 4350 4570 4750 4900 4900
 Y=10500 r14 :    0  150  300  500  750 1000 1250 1500 1800 2100 2350 2500 2500 2500 2500 2500
 Y=11500 r15 :    0  150  300  500  750 1000 1250 1500 1800 2100 2350 2500 2500 2500 2500 2500
              X=0  800 1000 1250 1500 1750 2000 2250 2500 3000 3500 4000 4500 4750 5000 5200
```

Lecture : surfaces **saturées** (4064, puis 4800, 5800… 7600) en haut de grille ; les deux dernières lignes (Y = 10500 et 11500) **s'effondrent** à 0→2500. Les lignes r0=r1 et r14=r15 sont identiques deux à deux : la table est **plate sur les bords** de l'axe Y (comportement normal d'une grille interpolée qui déborde de son axe).

### Grille alternative `0xE8872` (6×6) : **entièrement nulle**

```
0xE8892 : 36 mots à 0   → carte désactivée / non calibrée
```

### Grille alternative `0xE87D6` (2×2, axe `C3EC`) : **constante 8000**

```
0xE87E6 : 8000 8000 8000 8000
```

**Interprétation prudente** : sur cette variante, la fonction n'est pas réglée par une vraie cartographie mais par une constante (8000) ou par zéro. Ces deux tables sont donc soit des **emplacements réservés**, soit les tables d'une variante moteur non utilisée sur ce véhicule.

---

## 6. Les deux segments `0xE0000` et `0xF0000` : deux jeux de calibration

Question annexe tranchée au passage : **les deux segments ne sont pas une simple redondance.**

* `0xE0000`–`0xEFFFF` et `0xF0000`–`0xFFFFF` partagent le même **en-tête** (`55 55 00 00 02 92 24 00 48 10 0A 00 …`) et la **même arborescence** de cartes (mêmes adresses relatives).
* **14 147 octets diffèrent**, répartis en 12 plages :

| Plage (EA) | Taille | Remarque |
|---|---|---|
| `0xE0FF6`–`0xE0FFF` | 10 o | valeurs de données juste avant le 1ᵉʳ bloc de cartes |
| `0xE434D`, `0xEBCFC`–`0xEBCFF`, `0xEBF1B` | 1–4 o | ponctuels |
| `0xEC000`–`0xEC01B`, `0xEC040`–`0xEC241`, `0xEC2FA`–`0xEC8E1`, `0xECC00`–`0xECCC9` | ~2,2 ko | zone de données |
| **`0xED000`–`0xEEB43`** et **`0xEEBFA`–`0xEFECF`** | **~11,8 ko** | **cœur de la variante** |
| `0xEFEF0`–`0xEFF59` | 106 o | fin de bloc |

→ Le bloc **`0xEC000`–`0xEFFxx`** est la **partie variable** ; `0xE0000`–`0xEBFFF` est **commun**. C'est la signature de **deux Datensatz de variantes** dans la même flash (typique EDC15 : un jeu « de base » et un jeu « variante/coding »).

**Conséquence pratique pour tout patch de calibration : modifier les deux copies** (`BIN 0x6xxxx` **et** `BIN 0x7xxxx`), sinon on ne modifie qu'une variante sur deux.

---

## 7. `word_C3E6` — ce qui est prouvé, ce qui reste hypothèse

### Prouvé (binaire)

1. **C'est une grandeur d'axe**, jamais une quantité ni une durée : elle est *passée* à `unk_1D50` en `r14`, elle n'est produite par aucun calcul de débit.
2. Ses **écrivains** :
   * `loc_97324` (EA `0x97324`) : `word_C3E6 = word_C3E8 = word_C3E2 = [word_15F0+4]` — c'est une **valeur de remplacement**, suivie d'un **test de plausibilité** :
     ```
     movb rl4, [word_141E+14h] ; cmpb rl4,#4 ; jmpr cc_NZ, loc_97354
     movb rl4, byte_C2C9       ; cmpb rl4,#11h ; jmpa cc_NC, locret_973AC   ; si >= 0x11 : pas de défaut
     loc_97354: ... calls 0Ch, sub_CE9B4   ; r2=#187Fh, r3=#0B2h, r1=word_15F6
     ```
     → si `[word_141E+14h] == 4` **et** `byte_C2C9 < 0x11` : **DTC `187Fh`** (code de défaut, classe `0B2h`) et retour immédiat. Donc `C3E6` est une grandeur **surveillée, avec stratégie de substitution**.
   * `loc_977B0` : `word_C3E6 = word_C90C`.
3. Elle appartient à un **bloc de 7 mots consécutifs** `0xC3E2`, `0xC3E4`, `0xC3E6`, `0xC3E8`, `0xC3EA`, `0xC3EC`, `0xC3EE` — une **famille de grandeurs de même nature**, dont 3 membres (`C3E6`, `C3E8`, `C3EC`) sont utilisés comme **tags d'axe** dans le Datensatz.
4. **Étendue de l'axe** : 16 points de **3000 à 11500** (carte `0xE8444`) et 6 points de **0 à 10000** (carte `0xE8872`).

### HYPOTHÈSE (à confirmer, ne pas publier comme fait)

`word_C3E6` = **masse d'air par cycle** (ou grandeur de remplissage équivalente), en **mg/hub × 10** :

* l'axe démarre à **3000** = 300 mg/hub — ordre de grandeur du ralenti d'un 1,9 l TDI ;
* il plafonne à **11500** = 1150 mg/hub — ordre de grandeur de la pleine charge (avec réserve de suralimentation) ;
* une grille « limite » indexée par (régime × air) qui sature puis s'effondre est le profil classique d'un **limiteur de couple/fumée**.

Autre lecture possible : **débit d'air massique en mg/s** (3,0 → 11,5 g/s). Les deux hypothèses sont compatibles avec les valeurs ; **seule une mesure sur banc tranche**.

À noter pour la cohérence : les tags voisins `0xC3D2` (72 axes, valeurs 2481→3731) et `0xC3BA` (3271→3931) ont des étendues typiques d'une **pression** en mbar (2,5–3,9 bar absolus, soit 1,5–2,9 bar de suralimentation). Le bloc `0xC3xx` est donc un **cluster « air / pression »** — ce qui renforce l'hypothèse ci-dessus sans la démontrer.

---

## 8. Ce que devient le résultat des cartes à axe `C3E6`

### Site 1 — `loc_B26D2`, aiguillage de variante (listing 181907-181924)

```asm
loc_B26D2:  movb rl4, byte_C2C9
            cmpb rl4, #30h '0'
            jmpr cc_C, loc_B26F2          ; variante B (byte_C2C9 < 30h)
            mov  r12, word_1B40
            mov  r13, word_C42E           ; X = régime
            mov  r14, word_C3E6           ; Y = C3E6
            calls 0, unk_1D50
            mov  word_D986, r4            ; résultat
loc_B26F2:  mov  r12, word_1B46
            mov  r13, word_C42E
            mov  r14, word_C3EC           ; Y = C3EC (autre carte)
            calls 0, unk_1D50
            mov  word_D986, r4
loc_B2706:  mov r4, word_D986
            mov word_C690, r4             ; → borne BASSE de l'intégrateur (étape 5)
```

### Site 2 — `loc_B2706` (listing 181926-181960) : même carte, X = copie du régime

```asm
mov r4, word_C42E / mov word_C91C, r4
...
mov r12, word_1B40 / mov r13, word_C91C / mov r14, word_C3E6
calls 0, unk_1D50
mov word_C626, r6                     ; 2ᵉ sortie
```
puis, juste après (`loc_B276C`) :
```asm
mov r4, word_1430 / mov r5, [r4+#6]
cmp r5, word_C91C                     ; seuil de régime
jmpr cc_SGE, loc_B279A
mov r5, [r4] / add r5, word_D986      ; C690 + offset
cmp r6, r5 / ...                      ; plafonnement de C626 par C690 + [word_1430+0]
```

### Site 3 — `sub_B293A` (listing 182139-182200 ; appelée depuis `seg015:27A6`)

```asm
mov r4, word_C3D2 / mov word_C908, r4
mov r5, word_C3BA / mov word_C904, r5
mov r2, word_C42E / mov word_C91C, r2
mov r12, word_1B4C / mov r13, r2 / mov r14, word_C3E6
calls 0, unk_1D50
mov r8, r4
mov r4, word_1B50 / movb rl5,[r4] / cmpb rl5,#1
jmpr cc_NZ, loc_B2988
   mov r12, word_1B4E / mov r13, word_C904 / calls 0, unk_1D36   ; courbe 1-D
```

**Conclusion aval** : les cartes à axe `C3E6` produisent des **bornes** (basse → `word_C690`, haute → `word_C626`, et `r8` dans `sub_B293A`), consommées par le régulateur de l'étape 5. Ce sont des **limiteurs indexés par le régime et par `C3E6`** — pas le calcul de la quantité d'injection (qui reste `word_C6A6` ← `unk_1D50(word_1B66/1B68, word_C91C, word_C952)`, étape 6).

**Point ouvert signalé honnêtement** : le Datensatz ne contient que **2** cartes à axe `0xC3E6`, alors que le code a **3** sites d'appel (`struct 0x1B40` ×2, `struct 0x1B4C` ×1). Donc soit deux descripteurs pointent la même table (lecture avec/sans une seconde sortie), soit une des tables n'est pas dans cette zone. Non tranchable sans les descripteurs `0x1Bxx`.

---

## 9. Catalogue complet — 44 cartographies (× 2 segments) et 339 axes (× 2)

Deux fichiers joints :

* **`cartographies_datensatz.csv`** (88 lignes = 44 cartes × 2 segments) : `EA_entete ; tag_X ; nb_X ; X_min ; X_max ; tag_Y ; nb_Y ; Y_min ; Y_max ; EA_grille ; EA_fin ; octets ; val_min ; val_max`
* **`axes_datensatz.csv`** (678 lignes = 339 axes × 2 segments) : `EA ; EA_bin ; tag ; nb_points ; min ; max ; valeurs`

Répartition par tag d'axe Y, sur les 88 entrées (donc **moitié moins** en cartes distinctes) ; les tags X sont majoritairement `0xC42E` = régime (62 des 88 entrées, soit 31 cartes par segment) :

| Tag Y | Nb de cartes |
|---|---|
| `0xC6A2` | 18 |
| `0xC42E` | 10 |
| `0xC3D2` | 10 |
| `0xD004` | 8 |
| `0xC60A` | 4 |
| `0xC60E` | 4 |
| `0xC3E6` | 4 |
| `0xD006` | 2 |
| `0xC78A` | 2 |
| `0xC3A8` | 2 |
| `0xC3BA` | 2 |
| `0xD1F4` | 2 |
| `0xC590` | 2 |
| `0xC7C6` | 2 |
| `0xC6B6` | 2 |
| `0xC3B0` | 2 |
| `0xC562` | 2 |
| `0xC3EC` | 2 |
| `0xD3D4` | 2 |
| `0xC6DA` | 2 |
| `0xC7B8` | 2 |
| `0xC7C2` | 2 |

**Attention à l'interprétation** : sur les 88 entrées, **14 sont entièrement nulles** et **34 ont une valeur constante** — soit, en cartes distinctes, **7 nulles et 17 constantes** sur 44 : près de la moitié du catalogue est non renseigné ou figé. Un catalogue « brut » surestime donc largement le nombre de fonctions réellement calibrées. Les tables à axe `C3E6` (§5) sont dans ce cas pour deux d'entre elles (la 6×6 nulle et la 2×2 constante).

Annexe — les 88 cartes :

| En-tête EA | En-tête BIN | tag X | nX | tag Y | nY | Grille EA | Valeurs |
|---|---|---|---|---|---|---|---|
| `0xE100A` | `0x6100A` | `0xC42E` | 8 | `0xC42E` | 2 | `0xE1026` | 16–50222 |
| `0xE22F4` | `0x622F4` | `0xC42E` | 2 | `0xD006` | 2 | `0xE2304` | 0–4992 |
| `0xE2A2E` | `0x62A2E` | `0xC7C2` | 8 | `0xC78A` | 7 | `0xE2A54` | 0–350 |
| `0xE32AC` | `0x632AC` | `0xC42E` | 6 | `0xC3A8` | 12 | `0xE32D8` | 15000–15000 |
| `0xE38D8` | `0x638D8` | `0xC42E` | 2 | `0xC3BA` | 6 | `0xE38F0` | 10000–20500 |
| `0xE3908` | `0x63908` | `0xC42E` | 6 | `0xC3D2` | 6 | `0xE3928` | 0–4200 |
| `0xE39A8` | `0x639A8` | `0xC612` | 2 | `0xC60A` | 2 | `0xE39B8` | 0–0 |
| `0xE39C0` | `0x639C0` | `0xC3BA` | 2 | `0xC60A` | 2 | `0xE39D0` | 10000–10000 |
| `0xE5094` | `0x65094` | `0xC42E` | 8 | `0xD1F4` | 8 | `0xE50BC` | 0–0 |
| `0xE513C` | `0x6513C` | `0xD202` | 8 | `0xC590` | 8 | `0xE5164` | 1005–1459 |
| `0xE5450` | `0x65450` | `0xC42E` | 10 | `0xC6A2` | 5 | `0xE5476` | 0–0 |
| `0xE54DA` | `0x654DA` | `0xC42E` | 10 | `0xC6A2` | 5 | `0xE5500` | 0–0 |
| `0xE608A` | `0x6608A` | `0xC42E` | 6 | `0xC6A2` | 6 | `0xE60AA` | 10000–10000 |
| `0xE61A2` | `0x661A2` | `0xC42E` | 6 | `0xC6A2` | 6 | `0xE61C2` | 10000–10000 |
| `0xE6222` | `0x66222` | `0xC42E` | 4 | `0xC6A2` | 6 | `0xE623E` | 10000–10000 |
| `0xE626E` | `0x6626E` | `0xC42E` | 4 | `0xC6A2` | 6 | `0xE628A` | 10000–10000 |
| `0xE62BA` | `0x662BA` | `0xC42E` | 4 | `0xC6A2` | 6 | `0xE62D6` | 10000–10000 |
| `0xE68F4` | `0x668F4` | `0xC3C2` | 2 | `0xC3D2` | 4 | `0xE6908` | 0–1500 |
| `0xE6952` | `0x66952` | `0xC3C2` | 8 | `0xC7C6` | 6 | `0xE6976` | 74–120 |
| `0xE6D14` | `0x66D14` | `0xC42E` | 8 | `0xC6B6` | 8 | `0xE6D3C` | 0–0 |
| `0xE6E7E` | `0x66E7E` | `0xC3BA` | 8 | `0xC42E` | 10 | `0xE6EAA` | 3500–3500 |
| `0xE707A` | `0x6707A` | `0xC42E` | 16 | `0xD004` | 10 | `0xE70B6` | 2000–8000 |
| `0xE71F6` | `0x671F6` | `0xC60A` | 9 | `0xD004` | 9 | `0xE7222` | 0–1000 |
| `0xE72C4` | `0x672C4` | `0xC42E` | 16 | `0xD004` | 10 | `0xE7300` | 2650–8000 |
| `0xE744C` | `0x6744C` | `0xC42E` | 16 | `0xD004` | 10 | `0xE7488` | 1500–9000 |
| `0xE7828` | `0x67828` | `0xC60A` | 10 | `0xC42E` | 10 | `0xE7858` | 1000–2370 |
| `0xE7A00` | `0x67A00` | `0xC42E` | 16 | `0xC60E` | 10 | `0xE7A3C` | 800–2200 |
| `0xE7B7C` | `0x67B7C` | `0xC42E` | 16 | `0xC60E` | 10 | `0xE7BB8` | 800–2200 |
| `0xE7D44` | `0x67D44` | `0xD356` | 6 | `0xC42E` | 6 | `0xE7D64` | 0–50 |
| `0xE7DAC` | `0x67DAC` | `0xC6A2` | 6 | `0xC42E` | 6 | `0xE7DCC` | 4830–5520 |
| `0xE8000` | `0x68000` | `0xC42E` | 8 | `0xC3B0` | 6 | `0xE8024` | 1500–7600 |
| `0xE80A0` | `0x680A0` | `0xC42E` | 8 | `0xC3D2` | 10 | `0xE80CC` | 1300–12500 |
| `0xE8444` | `0x68444` | `0xC42E` | 16 | `0xC3E6` | 16 | `0xE848C` | 0–7600 |
| `0xE868C` | `0x6868C` | `0xC3D2` | 6 | `0xC562` | 6 | `0xE86AC` | 0–9230 |
| `0xE86F4` | `0x686F4` | `0xC42E` | 10 | `0xC3D2` | 9 | `0xE8722` | 0–9230 |
| `0xE87D6` | `0x687D6` | `0xC42E` | 2 | `0xC3EC` | 2 | `0xE87E6` | 8000–8000 |
| `0xE880A` | `0x6880A` | `0xC42E` | 6 | `0xC3D2` | 6 | `0xE882A` | 0–7040 |
| `0xE8872` | `0x68872` | `0xC42E` | 6 | `0xC3E6` | 6 | `0xE8892` | 0–0 |
| `0xE8A06` | `0x68A06` | `0xC42E` | 10 | `0xD3D4` | 10 | `0xE8A36` | 0–250 |
| `0xE8B50` | `0x68B50` | `0xC42E` | 8 | `0xC6DA` | 6 | `0xE8B74` | 0–8000 |
| `0xE8ECC` | `0x68ECC` | `0xC42E` | 8 | `0xC6A2` | 8 | `0xE8EF4` | 0–75 |
| `0xE9660` | `0x69660` | `0xC42E` | 8 | `0xC7B8` | 8 | `0xE9688` | 896–4850 |
| `0xEAFB2` | `0x6AFB2` | `0xC42E` | 2 | `0xC6A2` | 2 | `0xEAFC2` | 0–0 |
| `0xEB6CE` | `0x6B6CE` | `0xC6A2` | 2 | `0xC7C2` | 4 | `0xEB6E2` | 10000–10000 |
| `0xF100A` | `0x7100A` | `0xC42E` | 8 | `0xC42E` | 2 | `0xF1026` | 16–50222 |
| `0xF22F4` | `0x722F4` | `0xC42E` | 2 | `0xD006` | 2 | `0xF2304` | 0–4992 |
| `0xF2A2E` | `0x72A2E` | `0xC7C2` | 8 | `0xC78A` | 7 | `0xF2A54` | 0–350 |
| `0xF32AC` | `0x732AC` | `0xC42E` | 6 | `0xC3A8` | 12 | `0xF32D8` | 15000–15000 |
| `0xF38D8` | `0x738D8` | `0xC42E` | 2 | `0xC3BA` | 6 | `0xF38F0` | 10000–20500 |
| `0xF3908` | `0x73908` | `0xC42E` | 6 | `0xC3D2` | 6 | `0xF3928` | 0–4200 |
| `0xF39A8` | `0x739A8` | `0xC612` | 2 | `0xC60A` | 2 | `0xF39B8` | 0–0 |
| `0xF39C0` | `0x739C0` | `0xC3BA` | 2 | `0xC60A` | 2 | `0xF39D0` | 10000–10000 |
| `0xF5094` | `0x75094` | `0xC42E` | 8 | `0xD1F4` | 8 | `0xF50BC` | 0–0 |
| `0xF513C` | `0x7513C` | `0xD202` | 8 | `0xC590` | 8 | `0xF5164` | 1005–1459 |
| `0xF5450` | `0x75450` | `0xC42E` | 10 | `0xC6A2` | 5 | `0xF5476` | 0–0 |
| `0xF54DA` | `0x754DA` | `0xC42E` | 10 | `0xC6A2` | 5 | `0xF5500` | 0–0 |
| `0xF608A` | `0x7608A` | `0xC42E` | 6 | `0xC6A2` | 6 | `0xF60AA` | 10000–10000 |
| `0xF61A2` | `0x761A2` | `0xC42E` | 6 | `0xC6A2` | 6 | `0xF61C2` | 10000–10000 |
| `0xF6222` | `0x76222` | `0xC42E` | 4 | `0xC6A2` | 6 | `0xF623E` | 10000–10000 |
| `0xF626E` | `0x7626E` | `0xC42E` | 4 | `0xC6A2` | 6 | `0xF628A` | 10000–10000 |
| `0xF62BA` | `0x762BA` | `0xC42E` | 4 | `0xC6A2` | 6 | `0xF62D6` | 10000–10000 |
| `0xF68F4` | `0x768F4` | `0xC3C2` | 2 | `0xC3D2` | 4 | `0xF6908` | 0–1500 |
| `0xF6952` | `0x76952` | `0xC3C2` | 8 | `0xC7C6` | 6 | `0xF6976` | 74–120 |
| `0xF6D14` | `0x76D14` | `0xC42E` | 8 | `0xC6B6` | 8 | `0xF6D3C` | 0–0 |
| `0xF6E7E` | `0x76E7E` | `0xC3BA` | 8 | `0xC42E` | 10 | `0xF6EAA` | 3500–3500 |
| `0xF707A` | `0x7707A` | `0xC42E` | 16 | `0xD004` | 10 | `0xF70B6` | 2000–8000 |
| `0xF71F6` | `0x771F6` | `0xC60A` | 9 | `0xD004` | 9 | `0xF7222` | 0–1000 |
| `0xF72C4` | `0x772C4` | `0xC42E` | 16 | `0xD004` | 10 | `0xF7300` | 2650–8000 |
| `0xF744C` | `0x7744C` | `0xC42E` | 16 | `0xD004` | 10 | `0xF7488` | 1500–9000 |
| `0xF7828` | `0x77828` | `0xC60A` | 10 | `0xC42E` | 10 | `0xF7858` | 1000–2370 |
| `0xF7A00` | `0x77A00` | `0xC42E` | 16 | `0xC60E` | 10 | `0xF7A3C` | 800–2200 |
| `0xF7B7C` | `0x77B7C` | `0xC42E` | 16 | `0xC60E` | 10 | `0xF7BB8` | 800–2200 |
| `0xF7D44` | `0x77D44` | `0xD356` | 6 | `0xC42E` | 6 | `0xF7D64` | 0–50 |
| `0xF7DAC` | `0x77DAC` | `0xC6A2` | 6 | `0xC42E` | 6 | `0xF7DCC` | 4830–5520 |
| `0xF8000` | `0x78000` | `0xC42E` | 8 | `0xC3B0` | 6 | `0xF8024` | 1500–7600 |
| `0xF80A0` | `0x780A0` | `0xC42E` | 8 | `0xC3D2` | 10 | `0xF80CC` | 1300–12500 |
| `0xF8444` | `0x78444` | `0xC42E` | 16 | `0xC3E6` | 16 | `0xF848C` | 0–7600 |
| `0xF868C` | `0x7868C` | `0xC3D2` | 6 | `0xC562` | 6 | `0xF86AC` | 0–9230 |
| `0xF86F4` | `0x786F4` | `0xC42E` | 10 | `0xC3D2` | 9 | `0xF8722` | 0–9230 |
| `0xF87D6` | `0x787D6` | `0xC42E` | 2 | `0xC3EC` | 2 | `0xF87E6` | 8000–8000 |
| `0xF880A` | `0x7880A` | `0xC42E` | 6 | `0xC3D2` | 6 | `0xF882A` | 0–7040 |
| `0xF8872` | `0x78872` | `0xC42E` | 6 | `0xC3E6` | 6 | `0xF8892` | 0–0 |
| `0xF8A06` | `0x78A06` | `0xC42E` | 10 | `0xD3D4` | 10 | `0xF8A36` | 0–250 |
| `0xF8B50` | `0x78B50` | `0xC42E` | 8 | `0xC6DA` | 6 | `0xF8B74` | 0–8000 |
| `0xF8ECC` | `0x78ECC` | `0xC42E` | 8 | `0xC6A2` | 8 | `0xF8EF4` | 0–75 |
| `0xF9660` | `0x79660` | `0xC42E` | 8 | `0xC7B8` | 8 | `0xF9688` | 896–4850 |
| `0xFAFB2` | `0x7AFB2` | `0xC42E` | 2 | `0xC6A2` | 2 | `0xFAFC2` | 0–0 |
| `0xFB6CE` | `0x7B6CE` | `0xC6A2` | 2 | `0xC7C2` | 4 | `0xFB6E2` | 10000–10000 |

---

## 10. Points ouverts et suite proposée

1. **Identité physique de `C3E6`** : la seule façon de trancher est un point d'arrêt sur `loc_B26D2+0Eh` (lecture de `r14` = valeur de `C3E6`) **et** sur `loc_97324` (valeur de `[word_15F0+4]`, la valeur de remplacement). À comparer avec le débitmètre mesuré.
2. **`byte_C2C9`** : **un seul écrivain** dans toute l'image — EA `0xA11BA` (`movb byte_C2C9, [word_141C+0Ah]`), dans la routine de recopie du bloc de **coding/variante** (`[word_141C+1,+2,+4,+6,+8,+9,+0A,+0F,+18,+27]` → `byte_C2B1, C2C5, C2BB, C2B9, C2B2, C2B0, C2C9, C2B3, C2B4, C2BA`). C'est **le** sélecteur qui fait basculer `C3E6` ↔ `C3EC`.
3. **Descripteurs `0x141C`, `0x141E`, `0x1430`, `0x1432`, `0x1438`, `0x147E`, `0x15E2`, `0x15E4`, `0x15F0`, `0x1722`** : table de pointeurs de la mémoire basse, jamais écrite dans l'image. On peut au moins **cartographier les offsets utilisés** de chacun (déjà fait pour `0x1432`, `0x1434`, `0x1438`, `0x147E`, `0x1708`) et en déduire la structure de l'interface OS ↔ application.
4. **`unk_1D36`** (168 appels) : service de **courbe 1-D** (2 arguments) — à documenter en miroir de `unk_1D50`.
5. **Les 151 dwords de l'en-tête `0xE0008`/`0xF0008`** pointent tous dans `0x90000`–`0xDFFFF` (applicatif), pas dans la calibration : leur rôle (table de points d'entrée ? descripteurs ?) reste non tranché. À reprendre si on veut relier les descripteurs de l'application aux blocs de calibration.
