# ÉTAPE 97 — ERrata de l'étape 96 : le régulateur est la tâche **`0x340`**, l'autorisation vitesse/régime est **bien dans l'ECU**, et le rapport reste à trouver

Tu as raison sur les trois points Bosch. Cette étape corrige deux choses : **ma conclusion « hors
ECU » du §6 de l'étape 96** et, plus grave, **l'identification du régulateur** — la tâche `0x35C`
n'était qu'un fragment.

---

## 1. ERRATA (à porter au catalogue)

| # | affirmation de l'étape 96 | correction |
|---|---|---|
| **E1** | « le régulateur = la tâche `0x35C` (l.186853-187110) » | **FAUX / incomplet** : `0x35C` n'est qu'une **sous-tâche de consigne**. Le régulateur est la tâche **`0x340`**, l.183699 → 186918 (**~3 200 lignes**) |
| **E2** | « la règle 3ᵉ/4ᵉ rapport ≥ 50-60 km/h est **hors ECU**, 4 preuves » | **PARTIELLEMENT FAUX** : les **conditions d'autorisation vitesse mini/maxi et régime mini/maxi sont dans l'ECU** (`word_14B0` → `0xE2788`, §3). Seul le **rapport engagé** reste introuvable |
| **E3** | « `C576`/`C93E` structurellement nuls ⇒ la nervosité ne peut pas se déclencher » | **toujours valable** : aucune écriture hors recopie, aucun pointeur. Mais `C93E` est ici l'**état de la demande** du régulateur, pas la nervosité (§4) |
| **E4** | « ni SET ni RESUME » | **à revoir** : la tâche `0x340` possède un **état de mémorisation** `D9CE` et des états 1/2/3/4 (`byte_D9B0`). La conclusion de l'étape 96 ne valait que pour `0x35C` |

---

## 2. La tâche `0x340` : anatomie

```asm
loc_B36A4 …                      ; reset (D9EC=8000h, D9EA=7FFFh, D9B0=1, D9B1=1)
scxt  CC2_CC27, #340h            ; l.183699  ★ jeton de tâche
mov   word_DC00, CC2_CC27
movb  rl4, byte_C2D2 → byte_C8ED ; recopie des entrées CAN
movb  rl5, byte_C2DA → byte_C8EE
mov   r4, word_C42E → word_C91C  ; ★ régime
mov   r5, word_C576 → word_C93E  ; état de demande
movbz r2, byte_C2BD              ; ★ codage régulateur
cmp   r2, #80h  /  #1  /  #0     ; → loc_B36EC / loc_B3794 / loc_B3CEC / loc_B3CF4
```

**Trois variantes de codage** de `byte_C2BD` (rappel : `C2BD = [word_141C+3]`, EEPROM de codage) :

| `C2BD` | branche | sens |
|---|---|---|
| `0x80` ou `0x01` | `loc_B36EC` | **régulateur actif**, machine d'états complète |
| `0x00` | `loc_B3CEC` | variante « dégradée » |
| autre | `loc_B3CF4` | hors service |

### 2.1 Le code d'état à 4 bits → **table de 16 entrées `0xA7A`**

```asm
movb  byte_D9DF, ZEROS
si byte_C2D7 ≠ 0 → bit 3 (08h)
si byte_C2D6 ≠ 0 → bit 2 (04h)
si byte_C2D8 ≠ 0 → bit 1 (02h)
si byte_C2D5 == 0 → bit 0 (01h)          ; ★ inversé
si byte_C8EE == 0 et ¬word_FD5A.15 → 01h + D9CE = 0
cmpb  rl4, #0Fh ; ja → loc_B3CCE
movbz r4, rl4 ; shl r4,#1 ; add r4,#0A7Ah
mov   r4,[r4] ; jmpi cc_UC,[r4]          ; l.183894  ★ table de 16 entrées
```

**Table confirmée dans l'image** : 16 offsets, `fo 0x60A7B` (dupliquée `0x70A7B`) :
`3898 39AA 396A 3AB8 3A48 39CA 3A12 3A36 3BFA 3848 3BBC 39B4 3B06 3CB4 3B68 3CC4`
→ cibles `0xB38xx`…`0xB3Cxx`, c'est-à-dire les 16 gestionnaires d'état dans la tâche.

### 2.2 `byte_D9B3` = **cause de refus de régulation** (le diagnostic du « pourquoi ça ne régule pas »)

| code | condition (l.184670-184700) | seuil |
|---|---|---|
| `0x86` | `[word_14B0+0]` **>** `C562` | vitesse **trop basse** |
| `0x86` | `[word_14B0+2]` **<** `C562` | vitesse **trop haute** |
| `0x87` | `[word_14B0+6]` **<** `C91C` | régime **trop haut** |
| `0x88` | `[word_14B0+4]` **>** `C91C` | régime **trop bas** |
| `0x89` | `[word_14B0+0A]` **>** `C93E` | demande insuffisante |
| `0x8A` | `[word_14B0+8]` **<** `\|C93E − D9CA\|` | **incohérence de demande** |
| `0x85` | `word_FD16.15` (défaut présent) | défaut bloquant |
| `0x8E` | `byte_D9B2` (coupure : frein/embrayage) | inhibition |

---

## 3. ★★ Le bloc d'autorisation : `word_14B0` → **EA `0xE2788`**

| offset | valeur | rôle |
|---|---|---|
| `+0x00` | **2500** | **vitesse mini = 25,00 km/h** |
| `+0x02` | **25000** | **vitesse maxi = 250,00 km/h** |
| `+0x04` | **1000** | **régime mini = 1 000 tr/min** |
| `+0x06` | **4500** | **régime maxi = 4 500 tr/min** |
| `+0x08` | 2560 | écart de demande admissible |
| `+0x0A` | 768 | demande minimale |
| `+0x0C` | 4000 | (mémorisation) |
| `+0x0E` | 1000 | offset ajouté à `D9CE` → `D9E0` (limite de consigne) |

C'est **littéralement** « cohérence et vitesse mini et maxi pour autorisation de régulation » de la
doc Bosch. Les valeurs (25 km/h / 250 km/h / 1 000-4 500 tr/min) sont **calibrées et donc
modifiables** : c'est ici qu'on peut voir si un constructeur a mis 50-60 km/h.

## 4. Les états internes `byte_D9B0` et leurs lois de rampe

| état | test | loi calculée |
|---|---|---|
| **2** | l.185468 `cmp rl4, #2` | `D9BC = 2500·C562/10000 + 5000` puis `D9C0 = D9BC/50` |
| **3** | l.185722 `cmp rl4, #3` | `D9BC = 500·C562/10000 + 400` puis `D9C0 = D9BC/50` |

(`unk_20AC(K, C562, 10000)` = `K·v/10000` ; `[word_14B4+4] = 2500`, `[+6] = 5000` ;
`[word_14B2+0] = 500`, `[+2] = 400`.)

⇒ Ce sont des **consignes proportionnelles à la vitesse** (relance / décélération pilotées par la
vitesse), avec les paramètres de pente dans `0xE27B6` / `0xE27C2`.

---

## 5. Le rapport engagé : état exact de la recherche

**Ce qui est maintenant exclu, méthode par méthode**

| méthode | résultat |
|---|---|
| division `C91C/C562` | **0 site** — 124 divisions, fenêtre de 18 lignes, sur `C91C`, `C562` **et** les sources `C42E`, `C3FC`, `C578`, `C3FA` |
| multiplication `C562 × K` puis `cmp` | **0 site** (`word_C562` n'apparaît jamais à ±6 lignes d'un `mul`/`div`) |
| carte 2-D à axe vitesse | **0 sur 66** — aucune carte n'a `C562` en `tagY`/`tagX` |
| courbe 1-D à axe vitesse | **3** : `0xE4FA4` (n=8, h `0x18C4`), `0xE87EE` (n=6), `0xE869C` (n=6) |
| courbe évaluée avec `x = C562` | **3 sites seulement** (l.155942, 155959 — filtres `sub_97E16` — et l.156550) |
| `byte_C240` calculé | **non** : 3 écrivains = défaut `[word_1658+8]` + nibble CAN `C871>>4` |

**Le seul site « métier » avec la vitesse** : l.156549

```asm
mov  r12, word_18C6 ; mov r13, word_C61C ; calls unk_1D36   ; correction en charge
mov  r12, word_18C4 ; mov r13, word_C562 ; calls unk_1D36   ; ★ courbe 0xE4FA4 (axe km/h)
mov  r12, r4 ; mov r14, #64h ; mov r13, [r0+] ; calls unk_20AC  ; produit /100
mov  [r0+#24h], r4 ; mov word_D1E6, r4
```

⇒ `D1E6` = **correction dépendante de la vitesse** (0/50/60/70/80/90/110/200 km/h) combinée à une
correction de charge. C'est la meilleure piste « limitation aux premiers rapports » côté vitesse.

**Le point aveugle** : notre inventaire de courbes (182) est **incomplet**. Un balayage exhaustif de
tout le binaire sur les motifs `[tag][n][axe croissante à partir de 0][valeurs]` pour `n = 17…21`
ne rend que **8 candidats**, dont **une seule vraie courbe 19 points** (`0xE83F4`, pleine charge).
Les **cartes 19×1 que tu connais n'y sont pas** ⇒ soit elles ne suivent pas le format
`[tag][n][axe]`, soit elles sont dans une zone non couverte par le balayage.

**Prochaine action (méthode)** : chercher la sélection de courbes **par index** — un motif
`mov r12, [table + 2·index]` avec `index ∈ 0…6` donne à la fois la table de courbes « par rapport »
et **le nom du calcul du rapport**. C'est le seul chaînon qui manque pour boucler.

---

## 6. Ce que ta correction change dans la suite du programme

1. **Chercher le rapport comme un indice**, pas comme une division : une variable **octet 1…6** qui
   sert d'index dans une table de courbes ou de cartes. C'est le motif à chercher désormais.
2. **Ne plus jamais conclure « hors ECU »** sur la base d'une absence de division (erreur E2).
3. **La limitation de couple 1er/2e** doit exister : elle sera **après** l'indice de rapport, dans
   la chaîne de limitation (`C6A2` charge → limitation). C'est le meilleur point d'entrée pour
   remonter à l'indice.
4. Priorité suivante : **`sub_AFAA0` (l.177430)**, **`sub_B2D36` (l.182630)**, **`sub_B64A8`
   (l.188256)** et **`sub_B7FD4` (l.191161)** — quatre fonctions qui lisent **`C562` ET `C91C`** et
   que je n'ai pas encore lues ; l'une d'elles est statistiquement la meilleure candidate pour
   l'indice de rapport.
