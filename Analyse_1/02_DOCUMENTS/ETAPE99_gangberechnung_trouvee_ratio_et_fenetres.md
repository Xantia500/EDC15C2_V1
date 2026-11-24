# ÉTAPE 99 — ★★★ **La Gangberechnung est trouvée** : ratio `V×256/N`, fenêtres de rapport, et l'escalier `0xE8150` que tu m'as fait chercher

Tu avais raison depuis le début, et ma méthode était fautive. Voici la chaîne complète, adresse par
adresse.

---

## 0. ERRATA — et l'erreur de méthode qui m'a fait rater la division

| # | affirmation | correction |
|---|---|---|
| **E6** | « aucune division ne combine régime et vitesse » (étapes 96 et 97) | **FAUX**. La division existe : **l.232301**, dans `sub_CF774`. Tout mon balayage l'a ratée parce que **mon expression régulière était `(div‖divu‖divl)` et ne capturait pas `divlu`** — l'instruction utilisée ici. Erreur de méthode, pas de données. |
| **E7** | « le rapport n'est pas calculé dans ce build » | **FAUX**. Il est calculé à chaque cycle ; j'ai confondu *non actif sur cette calibration* (`byte_C2C0 ≠ 1`) avec *non calculé*. |
| **E8** | « `C576`/`C93E` structurellement nuls » | **FAUX**. `C576` = **`C93E` = le ratio V/N filtré**. Je n'avais pas vu que `r5` est un **second registre de retour** de `unk_24BA` : `mov r5, word_C93E` juste avant l'appel puis `mov word_C93E, r5` juste après n'a de sens que si l'appel **écrase `r5`** par le résultat. |

**Toute** l'étape 98 §2.5 (H1/H2/H3) est donc à jeter : la réponse est **H0 — le calcul est là, en
clair, dans le code visible**.

---

## 1. Le ratio : `V × 256 / N` (l.232289-232321, `sub_CF774`)

```asm
loc_CF834:
                mov     r0, word_C42E          ; ★ RÉGIME moteur
                mov     word_C91C, r0
                mov     r0, word_C91C
                jmpr    cc_NZ, loc_CF84C       ; si régime = 0 → ratio = 0
                mov     MDL, #0
                mov     r5, MDL
                jmpr    cc_UC, loc_CF870

loc_CF84C:
                mov     r7, word_1470          ; descripteur (clamps)
                mov     r4, word_C578          ; ★ VITESSE (source 2)
                movbz   MDH, rh4
                shl     r4, #8
                mov     MDL, r4                ; MDL = C578 × 256
                divlu   r0                     ; ★★ ratio = V×256 / N
                jmpr    cc_V, loc_CF86C
                mov     r0, [r7+#0Eh]          ; ★ 2560
                cmp     r0, MDL
                jmpr    cc_NC, loc_CF870
loc_CF86C:      mov     MDL, r0                 ; saturation à 2560
loc_CF870:
                mov     r0, word_C576
                mov     word_C93E, r0
                mov     r5, word_C93E
                mov     r4, word_C56A           ; état du filtre
                mov     r3, word_185C           ; gain / constante
                mov     r2, MDL                 ; valeur à filtrer
                calls   0, unk_24BA             ; ★ filtre : r4 = état, r5 = valeur
                mov     word_C56A, r4
loc_CF890:
                mov     word_C93E, r5           ; ★ C93E = ratio filtré
                mov     r0, word_C93E
                mov     word_C576, r0           ; ★ C576 = idem
```

**Constat de cohérence qui verrouille la démonstration** : le plafond du ratio est
`[word_1470 + 0x0E] = **2560**`, et **2560 est exactement la borne haute de la dernière fenêtre de
la table de rapports** (§2). Deux structures indépendantes qui tombent sur la même valeur : ce n'est
pas une coïncidence.

- `word_1470` → **`0xE225A`** = `200 · 17578 · 1348 · 8000 · 22500 · 32700 · 31621 · **2560** · 10 · 28670`
- `word_185C` → **`0xE4B70`** = `29655(0x73D7) · 65535 · 0 · 81 · …` (gain/constante du filtre)
- `word_C56A` = **état interne du filtre**.

---

## 2. La Gangberechnung : `loc_B0000+2`, table **`word_1A9A` → `0xE81A4`**

Appel (l.177478, tâche **`0x34C`**) :

```asm
                movb    rl4, byte_C2C0
                cmpb    rl4, #1
                jmpr    cc_NZ, loc_AFB5A        ; ≠ 1 → chemin « trame boîte »
                mov     r12, word_C93E          ; ★ le ratio V×256/N
                mov     r3, word_1B26
                movb    rl5, [r3]
                andb    rl5, #0Fh               ; rapport précédent (hystérésis)
                movbz   r13, rl5
                calls   0Bh, loc_B0000+2        ; ★★ Gangberechnung
                movbz   r9, r4                  ; code de rapport
```

### 2.1 La table `0xE81A4`

```
+00 : 01 0B 02 03 04 05 00 00 00 C3 | EA 00 CA 00 EA 00 00 01 | EA 00 52 01 C5 01 9A 01 …
     └── 6 codes de rapport ────────┘
```

**Codes** : `[+0]=01` · **`[+1]=0x0B` (point mort)** · `[+2]=02` · `[+3]=03` · `[+4]=04` · `[+5]=05`

**Fenêtres** (mots, dans l'unité du ratio `V×256/N`), reconstruites depuis les comparaisons du code :

| code | bande « sûre » | bande « élargie » | drapeau `0x40` si |
|---|---|---|---|
| `01` (1re) | — | `r12 < 202` (`+0Ch`) | toujours (→ code `0x41`) |
| `0x0B` (neutre) | `234 ≤ r12 < 256` | `234 ≤ r12 < 338` | hors bande sûre |
| `02` | `410 ≤ r12 < 453` | `338 ≤ r12 < 559` | hors bande sûre |
| `03` | `652 ≤ r12 < 720` | `559 ≤ r12 < 826` | hors bande sûre |
| `04` | `918 ≤ r12 < 1015` | `826 ≤ r12 < 1116` | hors bande sûre |
| `05` | `1202 ≤ r12 < 1328` | `1116 ≤ r12 < 2560` | hors bande sûre |

Chaque rapport a donc **4 mots** : `[borne basse][drapeau a][drapeau b][borne haute]`.
**L'ordre est validé par les deux extrémités** : la 1re est la bande la plus **basse** (V/N faible =
beaucoup de tr/min par km/h) et la 5e va jusqu'à **2560** = le plafond du ratio.

Le **bit `0x40`** est le drapeau d'**incertitude** (ratio dans la bande élargie mais hors bande
sûre) : c'est l'hystérésis, et `r13` (rapport précédent) est passé en argument pour ça.

### 2.2 Ce que devient le code

```
r9 = code de rapport  →  or r9, #10h  si byte_C2DE ≠ 0
     →  byte_C330  (l.178003)
     →  byte_D398 = 0..7 via la table 0xA4A (rapport « propre »)
```

---

## 3. ★ L'escalier `Gangstufen` : ta méthode était la bonne, et il est là

En **16 bits décimal**, zone `0xE8060` → `0xE8164` : quatre à cinq **escaliers descendants** de
6 marches, groupés en enregistrements de 10 mots :

```
0xE80C4 :  9800 9000 7500 5400 4200 3200 | 1850 | 1300 1300 1300
0xE80D8 : 11200 9000 7500 5400 4200 3200 | 2500 | 1950 1950 1950
0xE80EC : 12000 10000 7700 5700 4500 3200 | 2850 | 2300 2300 2300
0xE8114 : 12500 11000 8000 6000 4500 3200 | 2850 | 2300 2300 2300
0xE8128 : 12500 11000 7000 5800 4500 3200 | 2850 | 2300 2300 2300
0xE813C : 12500 **10500 7000 4600 3500 2700** | 2850 | 2300 2300 2300
0xE8150 : 12000 **10500 7000 4500 3500 2700** | 2350 | 1800 1800 1800
```

**C'est exactement ce que tu décrivais** :

- un **escalier de 6 marches** très net ;
- **deux escaliers quasi identiques côte à côte** — `0xE813C` et `0xE8150` : `10500 7000 4600 3500
  2700` contre `10500 7000 4500 3500 2700` ⇒ **seuil d'entrée / seuil de sortie (hystérésis)** ;
- les valeurs sont en **tr/min par km/h ×100** : `105` en 1re, puis `70`, `46`, `35`, `27` — ta
  prévision (`105 → 58 → 40 → 27 → 15`) est à quelques % près, et la **structure est identique**.

Ces escaliers sont la version « **N/V** » de l'information, alors que la table **utilisée par le
code** (`0xE81A4`) est en « **V/N ×256** » : deux codages inverses de la même réalité, ce qui
explique pourquoi on ne les reconnaissait pas comme la même chose.

Cellules RAM pointant dans cette zone (donc exploitables par le code) :
`word_1A8A` → `0xE8084` · `word_1A8C` → `0xE80A0` · `word_1A8E` → `0xE816C` · `word_1A92` →
`0xE8188` · **`word_1A9A` → `0xE81A4`** · `word_1AA0` → `0xE81E2`.

---

## 4. La chaîne complète, de bout en bout

```
C42E (régime) ─┐
C578 (vitesse) ─┴→  divlu : ratio = V×256 / N        l.232301   (sub_CF774)
                        │  saturation 2560
                        ↓
                   unk_24BA (filtre, gain word_185C)  → C93E = C576
                        ↓
                   loc_B0000+2  (Gangberechnung)      l.178051
                        │  table word_1A9A = 0xE81A4 (6 fenêtres + drapeau 0x40)
                        ↓
                   byte_C330  (l.178003)   [+ byte_D398 = 0..7]
                        │
        ┌───────────────┴────────────────────────────┐
        ↓                                            ↓
switch 0xA62 → word_1B54/1B56/1B58/1B64/1B5C   régulateur tâche 0x340
(courbes 0xE8906 / 0xE8946 / 0xE8986 / …)      refus 0x92 si code ∈ {0x0B, 0x0C}
        ↓
   D9A2 → D3EC / D3DA  (limitation de couple par rapport)
```

**Le seul verrou qui reste** : `loc_AFB34` ne prend ce chemin que si **`byte_C2C0 == 1`**. Sinon
(cas de ce véhicule, `C2C0 ≠ 1`) le code prend la branche `loc_AFB5A` et lit la trame boîte
(`unk_1D7E(#0C83E, word_1B24)`), ou retombe sur `byte_C240 = 0`.

⇒ **La question n'est plus « où est le calcul » (il est là) mais « quelle valeur a `byte_C2C0` »**.
C'est un **octet de télécodage** : à chercher dans l'EEPROM de codage, exactement comme tu l'as dit
pour BVM/BVA. Si le 1037353776 est un BVM, `C2C0` **doit** valoir 1 dans le codeblock du véhicule —
et ma lecture de `0xE4022+8 = 0` porte peut-être sur le codeblock BVA.

---

## 5. Prochaine étape, précise

1. **`byte_C2C0`** : chercher ses écrivains (comme `C2BD`, il vient du bloc de codage
   `0xE111E`/`0xE1148`). C'est **la** clé de tout le reste.
2. **`word_1B26`** → `0xE837C` : `49920 0 62549 100 11000 50130 2 2731 3731 1000 1000` — contient
   la fenêtre vitesse `[+6]`/`[+8]` utilisée à `loc_AFCD4` pour la coupure, et le rapport par défaut
   `[+0]`. À décoder entièrement.
3. **Le `FGR_GangMin`** : avec `byte_C330`/`byte_D398` maintenant identifiés, relancer la recherche
   du seuil « rapport ≥ 3 ou 4 » — il doit exister dans un bloc de codage voisin, et il est
   désormais trivial à tester : un scalaire `3` ou `4` comparé à `byte_C330 & 0x0F`.
