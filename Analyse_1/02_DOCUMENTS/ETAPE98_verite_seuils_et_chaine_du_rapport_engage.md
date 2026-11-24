# ÉTAPE 98 — Vérité sur les seuils 25/250 km/h et 1000/4500 tr/min · **la chaîne du rapport engagé est trouvée** (et tes adresses sont exactes)

Réponse directe à ta question, puis la découverte qui change tout.

---

## 1. Sur les seuils : ce dont je suis sûr, et ce dont je ne le suis pas

**Ce dont je suis sûr (relu ligne par ligne, l.184670-184700).** Le code fait littéralement :

```asm
mov r4, word_14B0 ; mov r5, [r4]    ; +0
cmp r5, word_C562                    ; C562 = vitesse, 0,01 km/h (étape 94)
jmpr cc_SLE, loc_B40E6               ; si [0] ≤ v → passe
movb rl4, #86h ; movb byte_D9B3, rl4 ; sinon → code 0x86
```

Idem `[+2]` (maxi), `[+4]` (régime mini), `[+6]` (régime maxi). Les valeurs lues à
**`0xE2788`** sont bien **`2500 · 25000 · 1000 · 4500`**. Là, aucun doute : c'est de la donnée, pas
une interprétation.

**Ce dont je ne suis PAS sûr — et tu as raison de me pousser.** Que ce bloc soit *le* `FGR_vMin` /
`FGR_nMin` de la doc Bosch. Trois raisons de douter :

1. **25,00 km/h** est très bas pour un `FGR_vMin` (doc : 4000-6000 = 40-60 km/h) ;
2. **1 000 tr/min** est très bas pour un `FGR_nMin` (doc : 1200-1300) ;
3. et surtout : dans **toute** la tâche `0x340`, il n'y a **ni `4000`, ni `6000`, ni un scalaire `4`
   de rapport minimum** — la seule utilisation du rapport y est un **rejet** (§3.3).

⇒ Ce bloc est une **fenêtre d'autorisation dure** (le véhicule doit rouler et le moteur tourner),
pas le `FGR_vMin` « commercial ». **Conclusion honnête : mes 25/250/1000/4500 sont exacts comme
données et comme comparaisons, mais mal étiquetés si on les présente comme `FGR_vMin`/`FGR_nMin`.**
Je corrige l'étiquette dans le catalogue (errata E5).

---

## 2. ★★★ La chaîne du rapport engagé : elle existe, et elle est indexée

### 2.1 La limitation de couple par rapport

```asm
loc_B3116:                               ; l.183021
movb  rl4, byte_C330
andb  rl4, #0Fh                          ; ★ nibble bas = CODE DE RAPPORT
subb  rl4, #1
cmpb  rl4, #0Bh
jmpr  cc_UGT, loc_B318C                  ; > 11 → aucune limitation (D9A2 = D9A8)
movbz r4, rl4 ; shl r4,#1
add   r4, #0A62h                         ; ★ table de 12 entrées
mov   r4,[r4] ; jmpi cc_UC,[r4]
```

| cas (`C330&0x0F`) | cellule | EA | courbe |
|---|---|---|---|
| 1 | `word_1B54` | **0xE8906** | **1re** |
| 2 | `word_1B56` | **0xE8946** | **2nde** |
| 3 | `word_1B58` | **0xE8986** | **3e** |
| 4 | `word_1B64` | — | 4e |
| 5 | `word_1B5C` | 0xE89FA | 5e |
| autre | — | — | `D9A2 = D9A8` (repli) |

Chaque courbe est évaluée **sur `C91C` (régime)** : `unk_1D36(word_1B5x, word_C91C)`.
Résultat → `word_D9A2`, publié en `D3EC` **et** `D3DA`, avec **mémoire de minimum** :

```asm
mov r5, word_D9A8 ; cmp r5, word_D9A2
jmpr cc_SLT, loc_B31F4
mov r2, word_D9A2 ; mov word_D9A8, r2     ; D9A8 = min glissant
```

puis offset de calibration `C622` (ajouté, ou plancher si `[word_141E+2Ah] == 1`).

### 2.2 Tes adresses : exactes, et voici la structure

Les blocs font **0x40 octets** = `[tag C42E][n=15][axe 15 mots][valeurs 15 mots]` :

| bloc | tag/n | axe (tr/min) | **valeurs** | contenu |
|---|---|---|---|---|
| **`0xE8906`** | C42E / 15 | 635 680 800 1000 1250 1500 1750 2000 2250 2500 2750 3000 3500 3750 4000 | **`0xE8928`** ✔ 1re | `3516 3516 3516 4485 5800 6660 6400 6350 6300 6330 6400 6500 6440 6270 6240` |
| **`0xE8946`** | C42E / 15 | idem | **`0xE8968`** ✔ 2nde | **identique à la 1re** |
| **`0xE8986`** | C42E / 15 | 635 680 800 1000 1200 1400 1600 1800 2000 2400 2800 3200 3600 3800 4000 | **`0xE89A8`** ✔ 3e | **`10000` × 15 = aucune limitation** |
| `0xE89C6` | C42E / 12 | 0 300 1200 1600 2000 2400 3200 3600 4050 4200 4500 5000 | — | `0 3800 3800 3800 3600 3400 3000 2000 2000 0 0 0` |
| `0xE89FA` | C42E / 2 | 635 680 | — | `10000 10000` |

Et le repère que tu donnes, **`main_torque` = `0xE841E`**, est exactement **la zone des valeurs**
de la courbe de pleine charge `0xE83F4` (tag C42E, n=19, axe 0…5200) dont les **valeurs**
commencent à `0xE83F4 + 4 + 2×19 = 0xE841E`. ✔

**Comparaison parlante** : pleine charge = `6660 7060 7430 7280…` ; 1re/2nde = `6660 6400 6350 6300
6330 6400 6500 6440 6270 6240` ⇒ **la limitation ne mord qu'au-dessus de ~1 250 tr/min**, et 3e est
**libre**. C'est bien « une limite en 1 et 2 » comme tu le dis.

### 2.3 Le rapport remappé

Après `r9`, une **seconde table `0xA4A`** (indexée par `r9 & 0x0F`, 0…0x0B) écrit
**`byte_D398` = 0…7** : c'est le rapport « propre ». Elle ne sert qu'à ça dans tout le binaire
(9 écrivains, tous dans ce switch, **aucun lecteur** hors publication).

### 2.4 D'où vient `byte_C330` — et pourquoi ça ne marche pas ici

```asm
; tâche 0x34C (l.177481), fin de tâche :
loc_AFFCA:
mov  word_C686, r6
mov  r4, r9
movb byte_C330, rl4        ; ★ l.178003
```

- **BVA** (`byte_C2C0 == 1`) : `r9 = unk_1D7E(#0C83E, word_1B24)` puis
  `unk_1D36(#0C83E…)` ⇒ le rapport vient de la **trame CAN boîte** (buffer `0xC83E`).
- **sinon** : `r9 = ` **table de 15 octets `0xE835A`** (`word_1B22`) indexée par
  `byte_C240 & 0x0F` :
  `30 01 02 03 04 00 00 00 00 0B 00 00 00 00 00`
  = `{0→0x30, 1→1, 2→2, 3→3, 4→4, 9→0x0B}`.

Et `byte_C240` = `[word_1658 + 8]`, avec **`word_1658` → `0xE4022`**, octets
`32 00 | AB 42 | 00 00 | 10 AB | **00** C3 | 2C 01 | …` ⇒ **`byte_C240 = 0x00`**.

⇒ **`r9 = 0x30` ⇒ `byte_C330 & 0x0F = 0` ⇒ le switch de limitation tombe sur `> 0x0B` ⇒ aucune
limitation par rapport n'est appliquée dans cette calibration.** Le régulateur, lui, ne refuse pas
(il ne rejette que `0x0B` et `0x0C`).

### 2.5 ★ Ce que ça veut dire, sans détour

La **Gangberechnung telle que tu la décris existe bien comme architecture** — j'ai trouvé son
*consommateur aval* (limitation par rapport), son *code de rapport* (`byte_C330`, `byte_D398`), son
*rejet au régulateur* et sa *table de correspondance*. Mais **le calcul N/V lui-même n'apparaît pas**
dans ce build : il est remplacé par une lecture de trame boîte ou par un défaut figé à 0.

Trois explications possibles, à départager :

| hypothèse | indice pour | indice contre |
|---|---|---|
| **H1** la Gangberechnung est dans la **bibliothèque effacée** (`0xC3`) et appelée par `unk_*` | cohérent avec les 108 490 o de `C3` | aucun pointeur identifié vers un ratio |
| **H2** elle est en **BVA uniquement** ici (trame `0xC83E`, `word_1B24`) | le chemin BVA est complet | BVM = ce véhicule |
| **H3** ce code est **désactivé par le codage** (`C2B7&1=0`, `C240=0`) | tout concorde | reste à prouver qu'un autre codeblock l'active |

**Test décisif, sans banc** : relire `0xE4022 + 8` dans les **autres codeblocks** du dump
(décalage `+0x10000`). Si un bloc contient une valeur ≠ 0, c'est **le codeblock BVM avec calcul de
rapport**, et `word_1B22`/`word_1B24` donnent la table de correspondance exacte.

---

## 3. Où en est le régulateur avec tout ça

### 3.1 Les codes de refus (`byte_D9B3`) — liste complète relevée

| code | cause | seuil / condition |
|---|---|---|
| `0x83` | `word_D9DC & 0x10` | inhibition externe |
| `0x84` | `byte_D9B1 == 6` | état interne |
| `0x85` | `word_FD16.15` | défaut présent |
| `0x86` | **vitesse** hors `[14B0+0]` / `[14B0+2]` | **2500 / 25000** (2 500 / 25 000 en 0,01 km/h) |
| `0x87` | **régime** > `[14B0+6]` | **4 500** |
| `0x88` | **régime** < `[14B0+4]` | **1 000** |
| `0x89` | demande < `[14B0+0A]` | 768 |
| `0x8A` | `\|C93E − D9CA\|` > `[14B0+8]` | 2 560 (incohérence de demande) |
| `0x8E` | `[word_14A8] & 1` (frein) ou `& 2` (embrayage) | `byte_D9B2 = 2` |
| `0x8F` | `byte_D9B4 == 1` | état interne |
| **`0x92`** | **`byte_C330 & 0x0F` ∈ {`0x0B`, `0x0C`}** | **point mort / marche arrière** ⇒ le rapport EST utilisé par le régulateur |

### 3.2 Le masque frein/embrayage

`word_14A8` → **`0xE275C`**, mot `+0` = **`0xBFFE`** (`1011 1111 1111 1110`) : bit 0 = 0, bit 1 = 1.
Le code refuse dès que le bit testé est **à 1** ⇒ à ce jour le bit « embrayage » (`& 2`) est **actif**
dans la calibration : **à vérifier sur banc**, c'est peut-être le fameux « régulateur qui ne
s'enclenche jamais ».

### 3.3 Ce que le régulateur ne fait PAS avec le rapport

Aucun `FGR_GangMin` : il ne teste pas « rapport ≥ 3 ou 4 », il teste **seulement** « pas au point
mort, pas en marche arrière ». Si ta voiture exige la 3e, cette condition est **en amont**
(commodo/BSI) ou dans un codeblock différent.

---

## 4. Plan immédiat

1. **Comparer les codeblocks** : lire `0xE4022+8`, `0xE835A`, `0xE836A`, `0xE2788` dans les copies
   `+0x10000` du dump (et dans tout autre bloc présent). Réponse nette sur H3.
2. **`word_1B24` → `0xE836A`** = `9387 9387 9387 9387 9387 9387 19200 19200 19200 49920 0 62464` :
   descripteur passé à `unk_1D7E` avec le buffer CAN `0xC83E` → c'est le **décodeur de rapport BVA**,
   à comprendre ; il donnera la forme attendue des tables de ratio N/V.
3. **`word_1B64`** (le « 4e » du switch, différent des autres) : le dumper, c'est peut-être le
   `FGR_GangMin` déguisé ou la courbe 4e.
4. **Compléter l'inventaire** des blocs `[tag][n][axe][valeurs]` de 0x40 octets sur toute la zone
   `0xE88xx-0xE8Axx` : c'est là que se trouvent les 5-6 courbes de rapport, et peut-être les seuils
   `N/V` manquants.
