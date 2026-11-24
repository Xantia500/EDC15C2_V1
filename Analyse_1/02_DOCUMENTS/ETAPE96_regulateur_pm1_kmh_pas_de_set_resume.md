# ÉTAPE 96 — La tâche du régulateur : le ±1 km/h trouvé, **ni SET ni RESUME**, et pourquoi le « 3ᵉ rapport à 60 km/h » ne peut pas être dans l'ECU

Tu me donnes deux informations de terrain précieuses : l'activation à partir du **3ᵉ/4ᵉ rapport vers
50-60 km/h**, et des pas de **±1 / ±2 km/h**. Voici ce que le code dit, y compris quand il dit
« non ».

---

## 1. Le régulateur = **une seule tâche**, jeton `0x35C`

Toutes les références à `byte_D9EE` / `byte_D9EF` / `word_D9F8` tombent entre **l.186853 et
l.187110** : c'est **un seul bloc**, une tâche du scheduler coopératif.

```asm
sub_B56F8:                    ; l.186826 — sélecteur de souhait (nervosité)
  …
  rets                        ; l.186848
; ---------------------------------------------------------------------------
  jnb  word_FD0C.15, loc_B573C          ; ★ début de la tâche
  …
loc_B573C:
  calls 0Ah, sub_AF50E        ; régulateur codé ?     (§4 de l'étape 94)
  …
loc_B57AC:
  calls 0Ah, sub_AF520        ; consigne par défaut selon le codage
loc_B57CC:
  mov  word_D9F8, r4          ; ★ D9F8 ← C6EA   (mémoire de consigne)
  mov  word_D3FA, r4          ;   publication diag
  rets                        ; ← branche d'INITIALISATION
; ---------------------------------------------------------------------------
  scxt CC2_CC27, #35Ch        ; l.186919  ★ jeton de tâche 0x35C
  …
  calls 0, unk_7C2            ; verrou de sortie
  rets                        ; l.187110
```

## 2. Le schéma complet de la demande (l.186913 → 187110)

```
C93E      = C576                       ; indicateur de demande
C91C      = C42E                       ; régime
D9F8      = C6EA                       ; consigne mémorisée
D9FA      = C6EA − C562                ; ★ écart consigne − vitesse
        ┌── [1B26+2] ≥ D9FA  →  état 2 / 3 (demande de réduction)
        └── [1B26+0] <  D9FA  →  rien
r9        = D9F8                       ; objectif
D9FC      = D9F8 − r9                  ; écart après limitation (unk_1E50, descripteur 1B7A)
        si [1B70+4] < D9FC  →  état 3
loc_B58CE:
D9FE      = r9 − C562                  ; ★ écart objectif − vitesse
DA0A/0A0C = C690 (32 bits)
   taux = (C93E == [1B70+0x0A] = 0) ? ([1B76],[1B72]) : ([1B78],[1B74])
r8        = unk_1FE8(taux, &DA0A, &D9FE, r9, C562)     ; ★ rampe / coordinateur
        si [1B70+6] ≤ D9FE  →  bit USR0  →  moniteur défaut 0x40DF (descripteur 1B6C)
        si D9EF == 1        →  r8 = [1B70+0x0C] = 10000
C69A      = r8                         ; ★ SORTIE
C6EA      = r9                         ; ★ consigne appliquée
D3F0 = D9EF · D3FA = D9F8 · D3F6 = D9F6 · D3F4 = DA06 · D3F2 = D9FE     ; publication diag
```

---

## 3. ★★ LE ±1 km/h : il est là

```asm
; l.187029-187042
mov  r4, word_1B70
mov  r5, [r4+#6]                 ; ★ 0xE8C86  =  100
cmp  r5, word_D9FE               ; écart objectif − vitesse
jmpr cc_SLE, loc_B5944           ; si 100 ≤ D9FE  → USR0 = 1
…
mov  r3, #180h
mov  r2, #40DFh                  ; défaut 0x40DF
mov  r1, word_1B6C               ; descripteur de seuils
calls 0Ch, sub_CE9B4
```

**`[word_1B70 + 6] = 100 = 1,00 km/h`** (EA **`0xE8C86`**) : c'est la **tolérance de cohérence entre
la consigne et la vitesse réelle**, et elle est **calibrée** — donc modifiable au Lexia. Au-delà de
1 km/h d'écart non résorbé, un **défaut `0x40DF`** est instrumenté.

Carte complète de `word_1B70` (EA `0xE8C80`), telle que le code la lit :

| offset | valeur | usage dans le code |
|---|---|---|
| `+0x00` | `0` | borne basse de l'écart `D9FA` |
| `+0x02` | `30000` | borne haute (= 300 km/h, jamais atteinte) |
| `+0x04` | `0` | seuil de décroissance de l'écart `D9FC` |
| **`+0x06`** | **`100`** | **tolérance 1,00 km/h → défaut `0x40DF`** |
| `+0x08` | `30000` | seconde borne haute |
| `+0x0A` | `0` | seuil d'aiguillage des taux, comparé à `C93E` |
| `+0x0C` | `10000` | **valeur de sortie `C69A` en état 1** (= 100 km/h) |

Les **±2 km/h** ne sont pas en immédiat : ils ne peuvent venir que de la calibration (pas trouvés
sous forme de constante `#0C8h`/`#64h` dans la tâche).

---

## 4. Les taux de rampe… sont **tous à zéro**

Les quatre descripteurs de taux sélectionnés par `C93E` :

| handle | EA | 10 octets | mots |
|---|---|---|---|
| `0x1B72` | `0xE8C8E` | `00 00 00 00 00 00 00 00 02 00` | `0 · 0 · 0 · 0 · 2` |
| `0x1B74` | `0xE8C98` | `00 00 00 00 00 00 00 00 02 00` | `0 · 0 · 0 · 0 · 2` |
| `0x1B76` | `0xE8CA2` | `00 00 00 00 00 00 00 00 08 00` | `0 · 0 · 0 · 0 · 8` |
| `0x1B78` | `0xE8CAC` | `00 00 00 00 00 00 00 00 08 00` | `0 · 0 · 0 · 0 · 8` |

⇒ **Les deux paires de taux sont nulles.** La rampe `unk_1FE8` est donc **neutre** : elle recopie
l'objectif. Le vrai limiteur de pente est ailleurs, dans :

| handle | EA | contenu |
|---|---|---|
| `0x1B7A` | `0xE8CB6` | **`1 · 1000 · 820 · 220 · 512 · 1024 · 1024 · 9`** |

utilisé par `unk_1E50(r12 = 1B7A, r13 = D9F8, r14 = &DA00)` (l.187004) — et `1000/820/220` sont
**10 / 8,2 / 2,2 km/h par seconde**, valeurs typiques d'un régulateur de vitesse. **C'est là que se
règle la progressivité de la reprise.**

---

## 5. ★★★ Ni SET, ni RESUME — et c'est démontrable

| question | réponse dans le code |
|---|---|
| qui écrit `word_D9F8` (mémoire de consigne) ? | **uniquement** `D9F8 ← C6EA` (l.186911) |
| qui écrit `word_C6EA` (consigne) ? | `sub_AF520` (défaut de codage) et `C6EA ← r9` (l.187064) |
| où `C562` (vitesse courante) est-elle **mémorisée** comme consigne ? | **nulle part** |
| y a-t-il un rappel d'une consigne précédente ? | **non** — aucune cellule « consigne précédente » |

**Il n'y a donc pas de SET (`C562 → mémoire`) ni de RESUME (`mémoire → consigne`) dans ce build.**
Le régulateur ne sait que **poursuivre** une consigne déjà présente, laquelle vaut **30 000**
(300 km/h, sentinelle) par défaut de codage, ou **10 000** (100 km/h) en état 1.

### 5.1 Et la raison structurelle : `C576` et `C93E` sont **toujours nuls**

```
C576 : écrivains = l.232324, 232403, 232617, 232825, 232861   → tous « C576 = C93E » ou « = 0 »
C93E : écrivains = l.232306, 232324, 232890                   → tous « C93E = C576 » ou « = 0 »
pointeurs `#0C576h` / `#0C93Eh` : AUCUN
```

Les deux cellules forment une **boucle fermée** initialisée à zéro, et **aucun pointeur** ne permet à
la bibliothèque de les écrire.

> **Conséquences, à vérifier au banc mais bien étayées :**
> 1. l'indicateur de demande `C93E` reste **0** ⇒ `[1B70+0x0A] ≥ C93E` est toujours vrai ⇒ **les taux
>    `1B76`/`1B72` (nuls) sont toujours retenus**, et la rampe est neutre ;
> 2. **la « nervosité » (étape 91) ne peut pas se déclencher** : `sub_B56F8` teste `C93E > 539`, ce
>    qui est **impossible** si `C93E` est structurellement nul ⇒ c'est **toujours la carte normale
>    `0xE8BD4`** qui est sélectionnée ;
> 3. **aucune demande extérieure n'entre par `C576`** : ce n'est donc pas le chemin du commodo.

Relever `C576` / `C93E` à la valise pendant un essai trancherait en 2 minutes.

---

## 6. ★ Pourquoi « 3ᵉ rapport ≥ 50-60 km/h » **ne peut pas** être dans cet ECU

Ta règle de terrain est probablement juste — mais elle n'est **pas** implémentable ici :

1. **Pas de rapport** : `byte_C240` n'a **qu'un seul lecteur** (`loc_AFBE8`, l.177553) et ce lecteur
   appartient au bloc **boîte automatique** (il travaille sur `word_C3FC`, `word_1B22`, `byte_C32E`,
   `unk_1D7E`). En BVM ce bloc est **hors circuit** (`byte_C2C0 ≠ 1`).
2. **Pas de trame de rapport** : `byte_C2B7 & 1 = 0` (`0x141C+0x0E = 0x08`) ⇒ la trame **`0x349`**
   n'est **pas armée**.
3. **Pas de calcul de rapport** : 0 division sur 124 sites ne touche `C562` (étape 95).
4. **Pas de seuil 50/60 km/h** dans la tâche : les seules constantes sont **1 km/h** et **100 km/h**.

⇒ La condition « rapport ≥ 3 et vitesse ≥ 50-60 km/h » est **hors du calculateur d'injection** :

- soit dans le **BSI / commodo** (full-mux : c'est lui qui voit la vitesse et le rapport par le CAN
  et qui n'envoie la demande que si les conditions sont réunies — c'est le montage standard PSA) ;
- soit dans la **bibliothèque effacée** (§1 de l'étape 95) ;
- soit simplement **absente de ce build**, puisque `byte_C2BD & 0x70 = 0` : le régulateur **n'est pas
  codé** dans la calibration présente.

**Le test qui tranche** : activer le régulateur au Lexia en télécodant le codage (bits 4-6 de
l'octet `+3` de `0x111E`) puis relire `C6EA` / `C69A` / `C93E`. Si `C93E` reste à 0 alors que le
commodo demande, la demande passe par un **autre chemin** qu'il faudra chercher côté CAN.

---

## 7. Ce qu'on a, ce qui manque

| élément | état |
|---|---|
| tâche du régulateur | **identifiée** — jeton `0x35C`, l.186853-187110 |
| consigne `C6EA` / mémoire `D9F8` | **identifiées** |
| écart `D9FA`, `D9FE`, sortie `C69A` | **identifiés** |
| **±1 km/h** | **trouvé** (`0xE8C86 = 100`) |
| taux de rampe | **trouvés** — `0xE8CB6` (`1 · 1000 · 820 · 220 · …`) |
| **pas de SET / RESUME** | **démontré** (aucun écrivain) |
| entrée de demande `C576`/`C93E` | **boucle à zéro** ⇒ aucun chemin d'entrée |
| condition 3ᵉ rapport / 50-60 km/h | **hors ECU** (4 preuves) |
| **arbitrage avec la pédale** | reste à faire : voir §8 |

## 8. Suite immédiate

1. **`C69A`** : il n'a **aucun lecteur** dans le code visible — mais il est publié en diag. Chercher
   son identifiant (`0x0Fxx`) et voir si une **autre tâche** le lit par pointeur indirect.
2. **Le lien avec la pédale** : comparer `C69A` (demande régulateur, en vitesse) et la sortie des
   cartes de souhait (`C6DA`/`C952`, en mg). L'arbitrage se fait **nécessairement** par une
   conversion ; chercher les deux seules conversions disponibles : `unk_20AC(·, ·, 10000)` (250 sites)
   et les cartes à axe `C562` (les 3 trouvées à l'étape 94).
3. **Le PI `unk_2020`** (l.196447) reste le candidat le plus sérieux pour la **boucle fermée** : il
   est **dans le code visible**, hors bibliothèque. À décortiquer en priorité.
4. **`word_16F0`** (`1000` / `9000` = 10 / 90 km/h, seuils de roulage OBD) : vérifier s'il est aussi
   utilisé pour une **condition d'activation** du régulateur.
