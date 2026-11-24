# ÉTAPE 106 — Les tags `0xD366` / `0xD369` / `0xD36A`, et la découverte d'un superviseur **239/240** avec hystérésis

---

## 1. Les tags sont des **octets normalisés 0…255**, pas des km/h

`grep` exhaustif dans `clean.asm` — les trois symboles existent bien, en **`byte_`**, avec **un seul
XREF chacun, en écriture** :

| symbole | XREF | lecteurs |
|---|---|---|
| `byte_D366` | `seg014:EEBA↓w` (l.175864) | **0** |
| `byte_D369` | `seg014:F094↓w` (l.176093) | **0** |
| `byte_D36A` | `seg014:EE6C↓w` (l.175829) | **0** |

### Ce qu'ils contiennent, prouvé par le code

```asm
; l.175806-175829  →  byte_D36A
mov  r12, word_1A70
mov  r13, r4              ; r4 = word_C908 (= word_C3D2)
calls 0, unk_1D36         ; interpolation de la courbe 1A70
mov  [r0], r4
cmp  r4, #0FFh
jmpr cc_SLT, loc_AEE58
movb byte_D8A4, ONES      ; >= 255  ->  255
...
movb byte_D8A4, ZEROS     ; <= 0    ->  0
...
movb byte_D36A, rl4       ; ★ recopie de D8A4
```

```asm
; l.176092-176098  →  byte_D369, et la preuve de l'échelle
movb rl4, byte_D8A2
movb byte_D369, rl4
movbz r12, byte_D8A2
mov  r13, #2710h          ; 10000
mov  r14, #100h           ; 256
calls 0, unk_20AC         ; ★ D8A2 x 10000 / 256  =  pour-mille
mov  word_C61C, r4
```

⇒ `D366` / `D369` / `D36A` sont des **états normalisés 0…255** (clampés, puis convertis en ‰ par
`×10000/256`). Ce sont des **copies de contrôle**, jamais relues.

### ⇒ La piste Vmax « courbes à axe 0…255 » est **éliminée**

Les cinq courbes `0xE7EA6` / `0xE7EBE` / `0xE7EE2` / `0xE7F06` / `0xE7F12` (tags `0xD369`, `0xD366`,
`0xD36A`) ne sont **pas** indexées par la vitesse en km/h, mais par une **grandeur normalisée 0…255**.
Ex. `0xE7EA6` (axe 0 64 128 192 255 → 0 2500 5000 7500 9961) = une **rampe de débit** en fonction
d'un état normalisé. **Ce n'est pas la Vmax.**

---

## 2. ★★★ Le superviseur `seg014:D232` → `byte_C325`, avec hystérésis 239/240

En cherchant les seuils ≥ 15000, un couple est apparu : **`23900` / `24000`** à `0xE6E34` / `0xE6E36`.

### Le bloc `word_19EA → 0xE6E2E`

| off | EA | valeur | remarque |
|---|---|---|---|
| +0 | `0xE6E2E` | **32767** | `0x7FFF` = **bypass** |
| +2 | `0xE6E30` | 200 | |
| +4 | `0xE6E32` | **32767** | `0x7FFF` = **bypass** |
| **+6** | **`0xE6E34`** | **23900** | **seuil armé** |
| **+8** | **`0xE6E36`** | **24000** | **seuil de coupure** |
| +A | `0xE6E38` | 1 | début descripteur `word_19EC` |
| +C | `0xE6E3A` | 1 | début descripteur `word_19EE` |
| +E/+10/+12/+14 | `0xE6E3C…` | 460 · 10 · 69 · 565 | corps des deux cartos |

`word_19EC → 0xE6E38` et `word_19EE → 0xE6E3A` sont **deux descripteurs décalés de 2 octets** :
deux variantes d'une même carto, utilisées en **bascule** — c'est la structure classique
**« seuil + hystérésis »**.

### Le code

```asm
; l.172524-172531 — construction de l'index
mov  r12, word_C91C          ; ★ RÉGIME (copie de word_C42E)
mov  r13, #2710h             ; 10000
mov  r14, [r4+#4]            ; ★ 0x7FFF  ->  saturation / bypass
calls 0, unk_20AC
mov  r5, [r0]
add  r5, r4
mov  [r0], r5
```

```asm
; l.172559-172566 — bascule d'hystérésis sur deux cartos
mov  r4, [r0]
cmp  r4, word_D850           ; valeur précédente = mémoire d'hystérésis
jmpa cc_SGE, loc_AD2B4
mov  r12, word_19EC          ; carto « basse »
calls 0, unk_1E50            ; -> 0xD84E / 0xD850
...
loc_AD2B4:
mov  r12, word_19EE          ; carto « haute »
calls 0, unk_1E50
```

```asm
; l.172578-172610 — décision
mov  r4, word_D850
mov  word_D308, r4
jnb  word_FD12.10, loc_AD2E8
mov  r5, word_19EA
mov  r2, [r5+#6]             ; ★ 23900
cmp  r2, word_D850
jmpr cc_SGT, loc_AD2E0       ; 23900 > D850  ->  drapeau remis à 0
...
loc_AD2E8:
mov  r5, [r4+#8]             ; ★ 24000
cmp  r5, word_D850
jmpr cc_SGT, loc_AD2FA
...
bmov word_FD12.10, USR0      ; ★★ le drapeau
```

```asm
; l.172630-172636 — sortie de la fonction
movb rl4, byte_C8F6          ; = FD12.10 -> 0/1
movb byte_C325, rl4           ; ★★★ sortie : byte_C325
```

**Conditions d'activation** : `word_C6D8 ≠ 0` (l.172545), `byte_C2DE = 0` (l.172549),
`word_C64A & 0F0h == 70h` (l.172551-172557).

### Interprétation (hypothèse forte, à confirmer en roulant)

Le couple **23900 / 24000** avec **hystérésis de 1 unité** est la signature d'un **superviseur de
vitesse maximale** : coupure à **240,00 km/h**, réarmement à **239,00 km/h** — et le drapeau qui en
sort est **`byte_C325`**, voisin immédiat de **`byte_C330`** (le rapport !). C'est le meilleur
candidat Vmax trouvé à ce jour, et il est **beaucoup plus crédible** que les courbes à axe octet.

⚠ Réserve : l'index `[r0]` est construit à partir du **régime** (`C91C × 0x7FFF / 10000`) alors que
`0x7FFF` sature la multiplication. Si `0xE6E30` valait autre chose que `0x7FFF`, l'index serait une
vraie image charge/régime. **Test de validation** : en roulant, lire `byte_C325` — s'il passe à 1
vers 240 km/h, c'est la Vmax ; s'il bascule à un régime précis, c'est un limiteur de régime.

### Si c'est bien la Vmax — le patch type « ECUSafe »

| EA | actuel | cible | effet |
|---|---|---|---|
| **`0xE6E34`** | 23900 | 32000 ou 0x7FFF | réarmement repoussé |
| **`0xE6E36`** | 24000 | **32000** (320 km/h) ou `0x7FFF` | **coupure repoussée** |
| `0xE6E2E`/`0xE6E32` | 0x7FFF | déjà bypass | rien à faire |

⚠ En **double** (`0xE6E34` → `0xF6E34`) et avec recalcul de checksum par l'outil (Étape 105 : algorithme
propriétaire).

---

## 3. Ce que ça change dans la cartographie

| élément | rôle établi |
|---|---|
| `byte_C330` | rapport (0-6, bit `0x40`) |
| **`byte_C325`** | **sortie du superviseur 239/240 (nouveau)** |
| `byte_D366/D369/D36A` | états normalisés 0…255, traces |
| courbes `0xE7EA6…0xE7F12` | rampes sur entrée normalisée (**pas** des km/h) |
| `0xE6E34`/`0xE6E36` | seuils 239/240 avec hystérésis |

## 4. Errata
- **E18** : les courbes à axe 0…255 (Étape 105, « candidates Vmax ») sont indexées par des états
  **normalisés 0…255**, pas par la vitesse. Piste abandonnée.
- **E19** : `A5 A5` n'est pas un marqueur unique : il ouvre des sous-blocs **descripteurs**, dont
  `word_19EC`/`word_19EE` (cartos jumelles d'hystérésis) sont un exemple concret.
