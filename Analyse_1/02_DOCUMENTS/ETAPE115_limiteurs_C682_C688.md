# ÉTAPE 115 — Les limiteurs réels `C682` / `C688` (et `C684` / `C686`)

Suite des Étapes 113-114. Les cinq limiteurs actifs de la cascade sortent **tous du même moule**.

---

## 1. Le moule commun : accumulateur `D904` → courbe 1-D → carto 2-D

```asm
180255  mov  r4, word_D904
180256  cmp  r4, #7FFFh
180257  jmpr cc_SGE, loc_B1626       ; ★ aucun limiteur n'a agi
        ; --- sinon, choix de l'offset selon le MODE ---
180258  movb rl4, byte_C339
180259  jmpr cc_Z, loc_B15DA
        ; mode 1
180260  r7 = D904 − word_C67A        ; saturé 0…0x7FFF (V/N gérés l.180262-180275)
180280  unk_1D6C(r12 = r0, r13 = r7, r14 = word_144E)      ; ★ interpolation 1-D
180284  word_1D94(r12 = 0xC83Eh, r13 = r0, r14 = word_1446) ; ★ carto 2-D  (variante 1)
180286  [r0+#8] = r4
        ; mode 0  (loc_B15DA)
180292  r7 = D904 − word_C678        ; saturé 0…0x7FFF
180311  unk_1D6C(r12 = r0, r13 = r7, r14 = word_144E)
180315  word_1D94(0xC83E, r0, word_1448)                    ; ★ carto 2-D  (variante 0)
180317  [r0+#8] = r4

loc_B161C:
180320  orb  byte_C335, #20h         ; ★ drapeau « plafond actif »
180332  mov  r4, [r0+#8]
180333  mov  word_C682, r4           ; ★★★ PLAFOND DE LA CASCADE
        ; ... puis le second étage ---
180393  [r0+#0Ah] = r4
180396  orb  byte_C335, #10h         ; ★ drapeau « plancher actif »
180408  mov  r4, [r0+#0Ah]
180409  mov  word_C688, r4           ; ★★★ PLANCHER DE LA CASCADE
180410  jmpa cc_UC, loc_B201C

loc_B1626:                            ; D904 = 0x7FFF  ⇒ aucun limiteur
180326  mov  r4, #7FFFh
180327  [r0+#8] = r4
180328  andb byte_C335, #0DFh        ; drapeau 0x20 effacé
        ...
180402  mov  r4, #0
180403  [r0+#0Ah] = r4
180404  andb byte_C335, #0EFh        ; drapeau 0x10 effacé
```

**Le même bloc est dupliqué** à `l.181164-181239` (plafond) et `l.181242-181315`
(plancher) — c'est la **seconde variante** de la fonction (deux modes d'exploitation).

## 2. Ce que c'est

`word_D904` est **l'accumulateur de limitation de couple** :
- initialisé à **`0x7FFF`** (« aucune limitation ») aux l.179732, 179841, 179868 ;
- abaissé par chaque limiteur via `word_1DDA` (fonction **min** de la bibliothèque) :
  ```asm
  180159  mov  r12, #7FFFh
  180160  mov  r13, word_D904
  180161  mov  r14, word_D906
  180162  calls 0, word_1DDA
  180163  mov  word_D904, r4        ; D904 = min(0x7FFF, D904, D906)
  ```

Puis `C682` / `C688` sont les **bornes d'IQ** issues de la conversion
« demande de couple → quantité d'injection » :

$$\text{C682} = \text{carto2D}_{0x1448}\big(\text{courbe}_{0x144E}(D904 - C_{678/67A})\big)$$

- **`byte_C339` = sélecteur de mode**, qui choisit l'offset `C67A` (mode 1) ou `C678` (mode 0).
- `word_144E → 0xE13DC` : courbe 1-D, **tag `0xC63C`**, `n = 9`, axe `0 · 1707 · 3413 · 5120 · …`
- `word_1446` / `word_1448` : handles de la **carto 2-D**, sélectionnés par le mode.

## 3. ★ Le même moule produit `C684` / `C686` dans la tâche couple

`l.177868-177978` (seg014, tâche de limitation de couple) :
```asm
177974  mov  r14, word_144E
177975  calls 0, unk_1D6C
177976  mov  r12, #0C83Eh
177977  mov  r13, r0
177978  mov  r14, word_1448
177979  calls 0, word_1D94
```
⇒ **Les 5 limiteurs actifs (`C680`, `C682`, `C684`, `C686`, `C688`) ne sont que 3 mécanismes :**
1. `C680` = **`C698`**, la demande du régulateur (Étape 113) ;
2. `C682`/`C688` = **conversion couple → IQ**, carto 2-D (`0x1448`/`0x1446`) ;
3. `C684`/`C686` = **même conversion**, calculée dans la tâche couple seg014.

## 4. Ce qui n'est pas décodable ici (même limite que les checksums)

| élément | nature | conséquence |
|---|---|---|
| `unk_1D6C` | **stub bibliothèque** (`ds 1`) | interpolation 1-D, sémantique certaine, code absent |
| `word_1D94` | **pointeur de fonction** (`ds 2`, appelé par `↓P`) | interpolation 2-D, code absent |
| `word_1DDA` | pointeur de fonction | min/max, code absent |

★ **Et les handles `0x1446` / `0x1448` pointent sur du vide dans ce dump** :
`0x1446 → 0xE2078` et `0x1448 → 0xE211A` contiennent **`00 00` sur 12 octets**.
⇒ **les pointeurs des cartos 2-D sont remplis à l'initialisation** (sélection de variante par
codage), pas définis statiquement. C'est cohérent avec l'existence de **deux variantes** du bloc.

## 5. Le sélecteur de mode `byte_C339`

```asm
189047  mov  r4, word_C68A
189048  cmp  r4, word_C626
189049  jmpr cc_SLT, loc_B6C32
189050  movb rl4, #1
189055  loc_B6C32: movb rl4, #0
189058  movb byte_C339, rl4        ; ★ C339 = (C68A >= C626)
```
Calculé dans la zone **régulateur / décollage** (seg015 `0xB6C00`), et remis à `0` par l'init
(l.188959). ⇒ le mode de limitation change selon un **état d'exploitation**, pas selon un codage.

## 6. Bilan : la cascade finalement décodée

```
C6A6  (souhait, cartes 0xE8B50 / 0xE8BD4, sélection par ratio 539)
  ↓ + C69E si D9AC == 1
  ↓ plancher C680 = C698                ← RÉGULATEUR (impose un minimum)
  ↓ plafond  C682                       ← couple → IQ, carto 2-D 0x1448/0x1446
  ↓ plancher C688                       ← même carto, second étage
  ↓ plafond  C684 / plancher C686       ← même conversion, tâche couple seg014
C6B2  (IQ finale)  →  cmp C6B2 / C6A4  → drapeau « limitation active » (bit 0x40)
```

Plus aucune inconnue de structure : tout ce qui reste est **de la bibliothèque**
(interpolations + filtres), dont la présence est **prouvée par les sites d'appel** et les
stuctures de données, mais dont le code n'est pas dans le dump.

## 7. Ce qui devient actionnable

| objectif | levier | où |
|---|---|---|
| autoriser/brider le couple par rapport | **cartes souhait** `0xE8B50` / `0xE8BD4` | Étape 108 |
| changer le seuil de rapport de ces cartes | **`0xE8C58` = 539** | Étape 108 |
| atténuer la limitation couple (couple max) | **carto 2-D derrière `0x1448` / `0x1446`** | à localiser (pointeur d'init) |
| changer la plage de conversion couple → IQ | **courbe `0xE13DC`** (tag `0xC63C`, 9 pts) | décodée |
| agir sur la demande du régulateur | `C698` / `C690` (saturation) | Étape 110/113 |

**Prochaine étape naturelle** : retrouver la **routine d'init qui remplit `0x1446`/`0x1448`**
— c'est elle qui désigne les cartos de limitation de couple réellement utilisées, et donc le
véritable levier « couple max ».
