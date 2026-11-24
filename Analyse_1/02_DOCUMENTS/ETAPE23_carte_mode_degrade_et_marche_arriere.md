# ÉTAPE 23 — La carte de mode dégradé et la marche arrière : trouvées, placées, et bornées

Tes deux indications se vérifient **toutes les deux**. Voici les preuves, puis la distinction stricte
entre ce qui est **lu** et ce qui est **inféré**.

---

## 1. La marche arrière — `word_1B64` → `EA 0xE8B10`

Table de sauts `0xE0A62`, codes **11 et 12** → bloc de `0x3168` → `word_1B64`. Contenu : 15 points,
635…4000 rpm, valeurs **identiques, terme à terme, à la courbe de 1ʳᵉ**
(`3516, 3516, 3516, 4485, 5800, 6660, 6400, 6350, 6300, 6330, 6400, 6500, 6440, 6270, 6240`).

⇒ Une seconde courbe de protection égale à celle de la 1ʳᵉ, sur des codes de rapport élevés :
**c'est bien la marche arrière**, protégée comme le premier rapport. (Lu.)

## 2. Le mode dégradé — `word_1B5A` → `EA 0xE89C6`

`tag 0xC42E`, **n = 12** :

| rpm | 0 | 300 | 1200 | 1600 | 2000 | 2400 | 3200 | 3600 | 4050 | 4200 | 4500 | 5000 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mm³ | 0 | **38,0** | **38,0** | **38,0** | 36,0 | 34,0 | 30,0 | 20,0 | 20,0 | **0** | 0 | 0 |

**38 mm³ au maximum, coupure à 4200 tr/min** — exactement l'ordre de grandeur que tu annonçais
(« 30 à 40 mm³ »). Le profil (plateau bas, décroissance, extinction au-delà de 4050) est celui d'une
**limitation de secours** : couple plafonné et régime borné. (Lu.)

## 3. Où elle est consommée — `loc_B31F4` (l. 183105)

```asm
loc_B31F4:
  mov   r12, word_1B5A        ; la carte mode dégradé
  mov   r13, word_C91C        ; régime
  calls 0, unk_1D36           ; interpolation
  mov   word_D9A4, r4         ; ← limite de secours
  mov   word_D3D2, r4         ; ← valeur publiée
  movb  rl4, byte_C33C
  jmpr  cc_Z, loc_B32A4       ; si aucune anomalie → on saute l'arbitrage
```

Deux points importants :

- la carte est **toujours évaluée** (l'appel précède le test), donc `word_D9A4` existe en permanence ;
- mais la **suite** (mise à l'échelle, rampe, comparaison) n'est exécutée **que si `byte_C33C` ≠ 0**.

## 4. L'arbitrage — `loc_B3242` (l. 183133-183160)

```asm
loc_B3242:
  mov  r4, word_D9A4
  cmp  r4, word_D9A8
  jmpr cc_SGE, loc_B3252      ; si D9A4 >= D9A8 → on prend D9A8
  mov  r12, word_D9A4         ; sinon la plus petite des deux
loc_B3252:  mov r12, word_D9A8
loc_B3256:
  mov  r13, word_D998         ; valeur courante
  mov  r4, word_1430
  mov  r14, [r4+10h]          ; paramètre de calibration
  calls 0, word_1DDA          ; (r12 = cible, r13 = courant, r14 = paramètre)
  mov  word_D998, r4
  jb   USR0, loc_B3274
  cmp  r4, word_D9A4
  jmpr cc_SGE, loc_B3298      ; résultat >= limite de secours → OK
loc_B3274:                    ; sinon → anomalie
  movb rl4, #1
  movb byte_D992, rl4
  movb byte_C338, ZEROS
```

Donc : **`min(word_D9A4, word_D9A8)` sert de cible**, la valeur est **ramenée progressivement** par
`word_1DDA`, et un **défaut est signalé** si le résultat reste sous la limite de secours.

## 5. D'où vient `byte_C33C` — c'est le symptôme d'anomalie

L'écrivain unique (l. 182515-182518) :

```asm
movb rl4, byte_D98E
orb  rl4, byte_D98F
orb  rl4, byte_D990
orb  rl4, byte_D991
movb byte_C33C, rl4          ; ← OU logique de QUATRE drapeaux
```

et trois lignes plus haut, les mêmes drapeaux sont publiés en deux mots de diagnostic :
`word_D3CE = (<<8) | byte_D98E` et `word_D3D0 = byte_D991<<8 | byte_D990`.

Et le lecteur (l. 181028) montre l'effet :

```asm
movb rl4, byte_C33C
jmpr cc_Z, loc_B1D96         ; pas d'anomalie → rien
mov  r4, #400h
or   word_D90C, r4           ; bit 10
or   word_D90E, r4           ; bit 10
movb byte_C232, ZEROS
bclr r9.0
bset word_FD16.14
```

⇒ **`byte_C33C` = « au moins une anomalie parmi quatre »**, et son apparition positionne des drapeaux
d'état (bit 10 de `D90C`/`D90E`). L'arbitrage de secours ne s'exécute donc **que sur défaut**, ce qui
est exactement la logique attendue d'un mode dégradé. *(Construction du OU et effet : lus. Sémantique
« défaut » : inférée du contexte — voir §6.)*

---

## 6. Prudence : ce qui est **lu**, ce qui est **inféré**

| affirmation | statut |
|---|---|
| `word_1B5A` → `0xE89C6`, 12 pts, 38 mm³, coupure 4200 tr/min | **lu** (handle + octets) |
| `word_1B64` → `0xE8B10` identique à la 1ʳᵉ | **lu** |
| table de sauts `0xE0A62`, codes 1/2/3 → 1ʳᵉ/2ᵉ/3ᵉ, 11/12 → marche arrière | **lu** |
| `byte_C33C` = OU de `D98E/D98F/D990/D991` | **lu** |
| l'arbitrage `min(D9A4, D9A8)` + comparaison à `D9A4` | **lu** |
| **`word_1DDA` est une rampe / limitation de taux** | **inféré** — son corps est dans la bibliothèque absente (étape 22) |
| **`D98E…D991` sont des défauts moteur** | **inféré** — on ne sait pas *quels* défauts les lèvent |
| **bit 10 de `D90C`/`D90E` = mode dégradé actif** | **inféré** — l'usage ultérieur de ces mots n'est pas vérifié |
| `word_D9A4` = plafond de secours | **inféré** — les valeurs (38 mm³) et le profil le suggèrent, le rôle exact dépend de `word_1DDA` |

**Et un avertissement de méthode** : en manipulant ces handles, `word_1B60`, `word_1B62`, `word_1B66`,
`word_1B68` produisent des décodages absurdes (`n = 6000`, « 509 mm³ »). Ce ne sont **pas** des
courbes mais des **blocs** d'une autre forme, que mon analyseur ne sait pas lire. **Toute valeur issue
de ces handles doit être écartée** tant que le format des blocs n'est pas établi. C'est la même limite
que celle signalée à l'étape 21 (1013 handles non classés).

## 7. La chaîne complète, mise à jour

```
                    ┌─ word_1B3E  main torque limiter (19 pts, max 74,3 mm³)   ─┐
régime (C42E→C91C) ─┼─ word_1B40  smoke map (16×16, régime × air)              ─┤
                    ├─ word_1B54/56/58/64/5C  par rapport (1ʳᵉ, 2ᵉ, 3ᵉ, R, défaut) ─┤→ word_D9A2
                    └─ word_1B5A  mode dégradé (38 mm³, coupure 4200)          ─┘→ word_D9A4
                                                                                  │
                       byte_C33C (anomalie) ?  ── non ──► on ne fait rien        │
                                │ oui                                             │
                                ▼                                                 │
                    min(D9A4, D9A8) ─► word_1DDA (lissage) ─► word_D998 ◄────────┘
                                │
                                └─ si D998 < D9A4 ─► byte_D992 = 1 (défaut)
```

## 8. Suite

1. **`sub_9B796`** : le calcul de `byte_C240` (le rapport 0…14) — c'est là que doit se trouver la
   vitesse. Toujours prioritaire.
2. **Les quatre drapeaux `D98E/D98F/D990/D991`** : qui les lève ? C'est la porte d'entrée du mode
   dégradé, et leur étude dira quels défauts réduisent la quantité à 38 mm³.
3. Table de sauts `#0A2Ch` en `EA 0xE0A2C` (sélecteur de `byte_C240`).
