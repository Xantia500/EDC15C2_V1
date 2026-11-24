# ÉTAPE 100 — Réponse à ta question : **il n'y a rien autour de l'escalier**, et voici pourquoi

Tu me demandes les valeurs autour de `15 27 40 58 105`. Réponse honnête : **dans ce fichier,
l'escalier est isolé**. Le bloc FGR est **1 400 octets plus haut**, et il est en **facteur 0,01**.
Voici les dumps bruts, avec adresses, comme demandé.

---

## 1. Les abords de l'escalier — `0xE80E0` → `0xE8168`, 16 bits LoHi décimal

```
0xE80E0 :  11200   9000   7500   5400   4200   3200   2500   1950   1950   1950
0xE80F4 :  12000  10000   7700   5700   4500   3200   2700   2150   2150   2150
0xE8108 :  12500  11000   8000   6000   4500   3200   2850   2300   2300   2300
0xE811C :  12500  11000   8000   6000   4500   3200   2850   2300   2300   2300
0xE8130 :  12500  11000   7000   5800   4500   3200   2850   2300   2300   2300
0xE8144 :  12500  10500   7000   4600   3500   2700   2350   1800   1800   1800
0xE8158 :  12000  10500   7000   4500   3500   2700   2350   1800   1800   1800
```

**Même zone en 8 bits décimal** (0xE80E0 → 0xE8158) :

```
0xE80E0 : 192  43  40  35  76  29  24  21 104  16 128  12 196   9 158   7 158   7 158   7
0xE80F4 : 224  46  16  39  20  30  68  22 148  17 128  12 140  10 102   8 102   8 102   8
0xE8108 : 212  48 248  42  64  31 112  23 148  17 128  12  34  11 252   8 252   8 252   8
0xE8130 : 212  48 248  42  88  27 168  22 148  17 128  12  34  11 252   8 252   8 252   8
0xE8144 : 212  48   4  41  88  27 248  17 172  13 140  10  46   9   8   7   8   7   8   7
```

**Lecture** : un enregistrement = **10 mots (20 octets)** = `[6 seuils N/V][1 valeur][3 valeurs
identiques]`. Aucun `40`, `45`, `50`, `55`, `60`, `200`, `210`, `220`, `250`, `1200`, `1250`, `1300`
— et **aucun `4`** (les octets « 4 » qu'on voit en 8 bits, comme `248 42` ou `0 4`, sont les octets
**hauts** de `12500 = 0x30D4` et `1024 = 0x0400`). ⇒ **Ton repère « chercher vMin/vMax/nMin/4 dans
les 200-400 octets autour de l'escalier » ne s'applique pas ici.**

### Et l'échelle

Ton escalier s'écrit `15 27 40 58 105` ; le nôtre s'écrit `2700 3500 4600 7000 10500`. **C'est le
même escalier, à l'échelle ×100** (et il a 6 marches : `12500 / 10500 / 7000 / 4600 / 3500 / 2700`).
Les deux derniers enregistrements sont presque identiques (`…4600…` vs `…4500…`) : **seuil d'entrée
et seuil de sortie** — exactement ce que tu décrivais.

---

## 2. Le bloc FGR réel : `0xE275C` → `0xE2798`

(≈ **0x5A0 = 1 440 octets avant** l'escalier, pas 200-400.)

```
0xE2754 :   3941   3967      0  49922  49150      1      1     40      0    200
0xE2768 :    500  20000   4000    400      0    100    300   1024    512    768
0xE277C :      8  10000    896    896      0      8   2500  25000   1000   4500
0xE2790 :   2560    768   4000   1000   5000   3000   4000
```

En 8 bits décimal, la même zone :

```
0xE2758 :   0   0   2 195 254 191   1   0   1   0  40   0   0   0 200   0
0xE2768 : 244   1  32  78 160  15 144   1   0   0 100   0  44   1   0   4
0xE2778 :   0   2   0   3   8   0  16  39 128   3 128   3   0   0   8   0
0xE2788 : 196   9 168  97 232   3 148  17   0  10   0   3 160  15 232   3
```

### Le décodage, offset par offset, avec la preuve de code

| EA | mot | ce que le code en fait | verdict |
|---|---|---|---|
| `0xE275C` | **49150** = `0xBFFE` | `[word_14A8] & 1` (frein), `& 2` (embrayage) — l.183926 | **masque** de conditions |
| `0xE2762` | **40** | `r4 = (`**`word_C0E8 − word_F91C`**`)` puis `cmp r4, [word_14AA]` — l.183421 et **l.183465** | **temporisation** (horodatage écoulé), **PAS une vitesse** |
| `0xE2766` | **200** | jamais lu aux sites que j'ai relevés | non attribué |
| `0xE2768` | 500 | non lu | non attribué |
| **`0xE276A`** | **20000** | `mov r2, [word_14AA+#8]` ; `cmp r2, word_D9CE` (consigne mémorisée) — **l.185490** | **`FGR_vMax` = 200,00 km/h** ✔ |
| `0xE276C` | **4000** | non lu aux sites relevés | numériquement = 40,00 km/h |
| `0xE276E` | 400 | non lu | non attribué |
| `0xE2770` | **0** | `[word_14AA+#0Eh]` : `and #4` et `and #10h` — l.183926 / l.183952 / l.183991 / l.184022 | **masque à 0 ⇒ les deux options `0x04` et `0x10` sont désactivées** |
| `0xE2772` | **100** | `cmp r4, [word_14AA+#10h]` — l.183753 | temporisation |
| `0xE2788` | **2500** | `[word_14B0+0]`, `cmp … , word_C562` → refus `0x86` — l.184674 | **vitesse mini = 25,00 km/h** |
| `0xE278A` | **25000** | `[word_14B0+2]` → refus `0x86` | vitesse maxi = **250 km/h** |
| `0xE278E` | **4500** | `[word_14B0+6]` → refus `0x87` | **régime maxi = 4 500 tr/min** |
| `0xE278C` | **1000** | `[word_14B0+4]` → refus `0x88` | **régime mini = 1 000 tr/min** |

### ⚠ Aucun `0004` — donc **pas de `FGR_GangMin` ici**

Balayage complet de `0xE2700` → `0xE2800` : **aucun mot égal à 4**. Ce n'est pas un oubli de
lecture, c'est un résultat : dans ce fichier, il n'y a **pas** de scalaire « rapport minimum 4 »
dans la zone FGR.

---

## 3. Facteur 1 ou 0,5 ou 0,01 ? — tranché par le code, pas par la valeur max

Ta méthode (regarder `vMax` : `210/220` → facteur 1 ; `420/440` → facteur 0,5) suppose que la seule
`vMax` du bloc soit celle du régulateur. Or ici il y a **plusieurs** candidats dans le même
enregistrement — `200` (`0xE2766`), `20000` (`0xE276A`) — et **le code désigne le gagnant** :

```asm
; l.185490
mov r5, word_14AA
mov r2, [r5+#8]          ; = 20000
cmp r2, word_D9CE        ; consigne mémorisée
jmpr cc_SLE, loc_B49EC   ; 20000 ≤ consigne → refuse
```

Le régulateur compare **`20000`** à la consigne ⇒ **facteur 0,01**. `200` n'est pas utilisé ici.
Conclusion : **sur ce fichier, 60 km/h s'écrit `6000` (0x1770) et 40 km/h s'écrit `4000` (0x0FA0)**,
jamais `60` ni `40`. (Et `40` à `0xE2762` est une temporisation — piège classique en 2D : les
nombres ronds ne sont pas toujours des vitesses.)

---

## 4. Ce que ça implique pour ton objectif (3ᵉ à 40 km/h)

Pour **ce** fichier, les leviers réels sont :

| objectif | adresse | valeur actuelle | à mettre |
|---|---|---|---|
| vitesse mini d'autorisation | `0xE2788` | **2500** (25 km/h) | déjà **sous** 40 ⇒ **ce n'est pas ce qui bloque** |
| vitesse max | `0xE276A` | 20000 (200 km/h) | ne pas toucher |
| régime mini | `0xE278C` | 1000 | déjà sous 1 200 ⇒ ne bloque pas |
| hystérésis basse | — | **absente** de ce bloc | — |
| rapport minimum | — | **absent** de ce bloc | — |

⇒ **Le « 40 km/h / 3ᵉ » que tu cherches n'est pas dans le bloc FGR de ce codeblock.** Trois
explications, dans l'ordre de vraisemblance :

1. **il est dans l'autre codeblock** (celui du véhicule) — c'est exactement l'avertissement de ta
   doc : modifier le mauvais bloc ne change rien ;
2. il est **en amont**, dans le commodo/BSI (full-mux) : le calculateur ne reçoit qu'une demande ;
3. il n'existe pas dans cette calibration parce que **le régulateur n'est pas télécodé**
   (`byte_C2BD & 0x70 = 0`), donc les valeurs FGR sont des **valeurs mortes** laissées par le
   Datensatz.

**Le test qui tranche, en une lecture** : comparer `0xE2788`, `0xE2762` et `0xE276A` entre le bloc à
`0x6xxxx` et celui à `0x7xxxx` du fichier. Si les deux sont identiques, il faut chercher ailleurs
(EEPROM de codage). Si l'un diffère, c'est **le** bloc du véhicule, et je te donne alors les octets
exacts à modifier.
