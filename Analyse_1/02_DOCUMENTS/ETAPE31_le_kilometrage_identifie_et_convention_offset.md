# ÉTAPE 31 — Le kilométrage est identifié · convention d'offset fixée · journal de vérification

Tu demandais la méticulosité : cette étape commence par **fixer la convention** que tu as raison
d'exiger, puis donne un **résultat ferme** (le compteur kilométrique), puis le **journal des erreurs**
que j'ai commises et corrigées.

---

## 1. Convention — « position dans l'image » = offset depuis l'**octet 0 de l'EEPROM**

L'image en RAM commence à **`0xE5CE`**, et **`0xE5CE` = l'octet 0 de l'EEPROM**. Tous les accès du
code sont de la forme `[0xE5CE + offset]`, donc **l'offset *est* l'adresse EEPROM** (0 → 1024).

**Preuve de la base** (et non une supposition) : l'écriture du checksum utilise une base décalée de 2 :

```asm
mov  r4, word_D6E
add  r4, word_D70
mov  r2, #0E5CCh        ; l.151534  ← 0xE5CE − 2
add  r2, r4
mov  [r2], r4           ; checksum à l'offset (D6E + D70 − 2)
```

Le checksum se pose sur **les deux derniers octets du bloc** `[word_D6E … word_D6E+word_D70−2]`, ce
qui n'est cohérent **que si les offsets sont comptés depuis `0xE5CE`**. La relecture
(`mov word_C838, [r4]`, l. 151839) utilise la même base. **Convention confirmée.**

## 2. Résultat ferme — le compteur kilométrique

### 2.1 La chaîne complète

| étape | ligne | ce que fait le code |
|---|---|---|
| 1 | 142793-142797 | `unk_2196(r12=&local, r13=[word_166C], r14=[word_166C+2])` → **échantillon courant** d'une grandeur 32 bits |
| 2 | 142799-142804 | comparaison à `word_CF7E` (échantillon précédent) ; gestion du rebouclage avec `word_CF6A` |
| 3 | 142808-142811 | **`word_C406` = courant − précédent** = **delta** |
| 4 | 142814 | `word_CF7E` = courant (mémoire pour le tour suivant) |
| 5 | 153592-153601 | `add r10, r4 / addc r11, r5` → **le delta est ajouté au total 32 bits `C83A:C83C`** |
| 6 | 153573-153590 | accumulations intermédiaires ; **`word_C838`** = accumulateur 16 bits, **modulo `0x55D5`** |
| 7 | 151504-151509 | le total et l'accumulateur sont **écrits dans l'image EEPROM** (groupe `word_D7A`) |
| 8 | 153504-153527 | **conversion en km** : division par **`0x7D0` = 2000** → **`word_C654`** |

### 2.2 L'unité : 0,5 m

`2000` unités par kilomètre ⇒ **1 unité = 0,5 m**. Le total est donc stocké en demi-mètres sur
32 bits (portée ≈ 1,07 million de km — cohérent pour un compteur de vie).

### 2.3 La preuve d'usage — c'est bien une distance

`word_C654` est consommée par une **vingtaine** de sites, toujours selon le même motif
(l. 154745-154762, 162096-162112, 167634…, 168536…) :

```asm
loc_A3026:
  mov  r4, word_E176
  and  r4, #1
  jmpr cc_NZ, loc_A303C
  mov  r4, word_C654
  mov  word_E178, r4        ; ← mémorise le kilométrage à cet instant
  or   word_E176, #1        ; ← verrou (one-shot)
loc_A303C:
  mov  r12, word_CFF6       ; handle d'une carte
  mov  r13, word_C654
  sub  r13, word_E178       ; ← DISTANCE PARCOURUE depuis le point mémorisé
  and  r13, #0FFFFh
  → interpolation
```

**Un compteur monotone, sauvegardé en EEPROM, divisé par 2000, et utilisé en différence « depuis un
événement » avec verrou one-shot : c'est le kilométrage**, et les cartes indexées là-dessus sont les
**cartes d'intervalle depuis événement** (régénération FAP, vieillissement, dérive EGR).

Quatre indices indépendants convergent : (a) ÷2000, (b) accumulation de deltas, (c) sauvegarde
EEPROM, (d) usage en différence avec mémorisation. **Je le tiens pour établi.**

### 2.4 Ce qui reste inexpliqué

Le **module `0x55D5` = 21973** de l'accumulateur 16 bits `word_C838` n'a pas d'explication
arithmétique simple (21973 × 0,5 m = 10,99 km ; en impulsions, 5,44 km). Je **ne l'invente pas** : à
élucider (probablement une valeur de *dithering* pour éviter une résonance du report).

## 3. Tableau corrigé du groupe `word_D7A` — avec la colonne d'offset 0…1024

| offset EEPROM (0→1024) | variable d'offset | position relative | contenu | variable vive |
|---|---|---|---|---|
| **= valeur de `word_D7A`** (RAM `0x0D7A`) | `word_D7A` | **+0** | accumulateur 16 bits, modulo `0x55D5` | `word_C838` |
| **= `word_D7A` + 2** | `word_D7A` | **+2** | total 32 bits, mot bas | `word_C83A` |
| **= `word_D7A` + 4** | `word_D7A` | **+4** | total 32 bits, mot haut | `word_C83C` |

La colonne de gauche se remplit en lisant **un seul mot** : `word_D7A` à l'adresse RAM `0x0D7A`.

## 4. Journal de vérification — mes erreurs, et ce qui les a corrigées

| # | erreur | comment elle a été détectée | correction |
|---|---|---|---|
| 1 | `0xE5CE` pris pour une adresse de calibration (`0xE25CE`) | désaccord interne : le contenu n'était pas un bloc de codage | recalcul par DPP (`page 3`) |
| 2 | puis `0xEE5CE` | même désaccord | `mov DPP3, #3` (l. 96443) ⇒ linéaire **`0xE5CE`** = RAM interne |
| 3 | « 6 octets = compteur de kilométrage » (étape 30) | `C83A` et `C83C` toujours manipulés **par paire** (`add/addc`, `divlu`) | **compteur 32 bits** + **accumulateur 16 bits** distinct |
| 4 | « offset inconnu donc colonne vide » (étape 30) | tu as raison : la convention manquait | convention fixée au §1, avec preuve |

**Ce qui a *résisté* à la vérification** (et peut donc servir de base) : les tags = adresses RAM
(3 identifications concordantes), `0xC337` écarté (5 occurrences + courbe non référencée),
`word_FD0C` sans écrivain, les 15 octets du bloc de codage, le checksum par somme négative.

## 5. Ce que ce résultat ouvre

Les cartes indexées par `word_C654` sont indexées par une **distance depuis un événement**. Il y a
donc, dans la calibration, des cartes dont l'axe est une **différence de kilométrage** — or ces cartes
ont un **tag** (une adresse RAM). En cherchant les tags qui pointent vers une variable de type
« distance depuis », on peut **retrouver la famille des cartes FAP / vieillissement**.

Piste concrète : `0xC5BC` (axe `32768…36128`, décalé) et `0xC562` / `0xC6B6` (axes `0…20000`,
`0…10000`) — deux d'entre eux pourraient être ces variables de distance.

## 6. Prochaines actions

1. **`word_E178`, `word_E18C`** (les mémorisations de km) : énumérer tous les couples
   « verrou + mémorisation » → **liste des événements datés en km** (régénérations, défauts).
2. **`unk_2196`** : comprendre le contrat (échantillon 32 bits) — c'est lui qui donne l'unité de base.
3. **Les cartes indexées par la distance** : décoder `word_CFF6` et ses voisins.
