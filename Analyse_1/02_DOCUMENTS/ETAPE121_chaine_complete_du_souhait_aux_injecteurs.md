# ÉTAPE 121 — LA CHAÎNE COMPLÈTE : du driver's wish aux injecteurs

> ⚠️ **PÉRIMÉ SUR UN POINT — errata E32 (voir `ETAPE124_audit_FAP_post_injection.md` §4)** :
> ce document présente `byte_C81B`…`byte_C829` comme la **commande des injecteurs**. C'est **FAUX**.
> Ces octets ont **1 écriture et 0 lecture** ; ils sont publiés par `sub_9CFD0` sur les **canaux de
> diagnostic `0x348` et `0x388`** (l. 143249-143253 et 143536-143540). La chaîne de conversion est réelle
> mais **terminale et passive**. Voir aussi **E33** (`word_C642` = écart signé, pas une quantité).

**Règle de ce document** : chaque maillon porte **sa ligne de code**. Une carte n'apparaît que si elle
est effectivement appelée dans la séquence. Statut explicite : `[C]` = confirmé par le code,
`[S]` = usage confirmé mais sémantique de la sortie encore ouverte.

---

## 0. Les entrées (grandeurs)

| variable RAM | grandeur | preuve |
|---|---|---|
| `C91C` | **régime** | recopiée de `C42E` : l.181906-907, l.182256-257 |
| `C952` → `C6DA` | **pédale** (0…10000 = 0…100 %) | `mov word_C6DA, r4` juste après, l.195520-521 |
| `C3E6` | **masse d'air** (3000…11500 = 300…1150 mg/coup) | axe de `0xE8444` ; init. l.131319-320 depuis `0xE3AD0[+4]` |
| `C908` | **T° liquide de refroidissement** (copie de `C3D2`) | l.177377-378, l.182067-068 |
| `C900` | **T° carburant** (axe de `0xE8000`/`0xE7F7E`) | Y des cartes, l.177109…177184 |
| `C562` | **vitesse véhicule** (0…18000) | axe de `0xE868C`, l.182115 |
| `C576` | **code de rapport engagé** (Gangberechnung) | sélecteur du souhait, l.186826 |
| `C7C2` | **P rail × 10** | axes de `0xE23B4`, `0xEB3E2` |

---

## 1. LE SOUHAIT — `sub_B56F8` → `C6A6`

```asm
loc_BABD8:                          ; l.195503
    mov  r12, word_C91C      ; X = RÉGIME
    mov  r13, word_C952      ; Y = PÉDALE
    calls 0Bh, sub_B56F8
    mov  word_C6A6, r4       ; ★ SOUHAIT = C6A6
```

et le sélecteur (l.186821-186846) :

```asm
sub_B56F8:
    mov  r4, word_C576
    mov  word_C93E, r4        ; C93E := code de rapport
    mov  r5, word_1B6A        ; → EA 0xE8C58
    mov  r2, [r5]             ; seuil = 539
    cmp  r2, word_C93E
    jmpr cc_SLE, loc_B5722    ; 539 <= rapport  → carte A
    ...                       ; sinon           → carte B
loc_B5722:
    mov  r12, word_1B66       ; → EA 0xE8B50
```

| carte | axe X | axe Y | sortie | rôle | code |
|---|---|---|---|---|---|
| **`0xE8BD4`** `[C]` | `C42E` régime 0…5000 (8) | `C6DA` pédale 118…10000 (6) | → `C6A6` | souhait **quand `C576 < 539`** (1re/2e, marche arrière) | l.186835 |
| **`0xE8B50`** `[C]` | `C42E` régime 0…5000 (8) | `C6DA` pédale 118…10000 (6) | → `C6A6` | souhait **quand `C576 ≥ 539`** | l.186843 |
| `0xE8C58` | — | — | constante **539** | seuil de bascule | `[word_1B6A]` |

★ **C'est ici que se joue la limitation « 1re/2de »**, en tout premier, avant tout limiteur.

---

## 2. LE RÉGULATEUR — `C698`

Le régulateur produit `C698`, immédiatement **plafonné par la fumée** :

```asm
loc_B4D1A:                          ; l.185814
    mov  r4, word_C698
    cmp  r4, word_C690
    jmpa cc_SLE, loc_B53E4
    mov  word_C698, r5          ; C698 := C690
```

Puis il devient le **plancher** du souhait :

```asm
    mov  word_C680, ...         ; C680 := C698      (l.186651-652)
```

```
souhait C6A6  ──┐
                ├─ le plus GRAND gagne ─→ C6B8
régulateur C680 ┘   (pédale prioritaire dès qu'elle demande plus)
```

---

## 3. LES LIMITEURS — quatre familles, toutes confirmées

### 3.1 La smoke map — `0xE8444` → `C690`

```asm
loc_B26D2:                          ; l.181914
    mov  r12, word_1B40      ; → EA 0xE8444
    mov  r13, word_C42E      ; X = RÉGIME
    mov  r14, word_C3E6      ; Y = MASSE D'AIR
    calls 0, unk_1D50
    mov  word_D986, r4
    mov  word_C690, r4       ; ★
```

| carte | axe X | axe Y | sortie | code |
|---|---|---|---|---|
| **`0xE8444`** `[C]` | `C42E` régime 0…5200 (16) | **`C3E6` air 3000…11500 (16)** | **15…76 mm³** → `C690` | l.181914, l.181950 |
| `0xE87D6` `[C]` | `C42E` régime **200…620** (2) | `C3EC` 700…850 (2) | → `C690` | variante démarrage à froid, l.181946 |

### 3.2 La température carburant — `0xE8000` / `0xE7F7E` → `D8C4`

```asm
    mov  r12, word_1A84      ; → EA 0xE8000
    mov  r13, word_C91C      ; X = régime
    mov  r14, word_C900      ; Y = T° CARBURANT
    calls 0, unk_1D50
    mov  word_D8C4, r4       ; ★
```

| carte | axe X | axe Y | sortie | code |
|---|---|---|---|---|
| **`0xE8000`** `[C]` | régime 800…4800 (8) | `C3B0`/`C900` **3051…3751** = 32…102 °C (6) | 15…76 mm³ → `D8C4` | l.177109, 177127, 177184 |
| **`0xE7F7E`** `[C]` | régime 800…4800 (8) | `C3B0` **3601…3751** = 87…102 °C (4) | 15…76 mm³ → `D8C4` | l.177139, 177157, 177173 |

### 3.3 La température moteur — cinq cartes

| carte | axe X | axe Y | sortie | code |
|---|---|---|---|---|
| **`0xE80A0`** `[S]` | régime **100…1000** (8) | `C3D2` 2481…3731 = −25…+100 °C (10) | **12,5…125 mm³** | l.177378 (`sub_AFA42`) |
| **`0xE86F4`** `[C]` | régime 0…1760 (10) | `C908` 2431…3531 (9) | → `[r0]` | l.182069 |
| **`0xE868C`** `[C]` | `C908` 2431…3831 (6) | **`C562` vitesse 0…18000** (6) | → `D98A` | l.182115 |
| **`0xE880A`** `[C]` | régime 1300…4000 (6) | `C908` **3841…3951** = 111…122 °C (6) | → `r9` | l.182258 |
| **`0xE3908`** `[S]` | régime 1000…2500 (6) | `C3D2` 2531…3131 (6) | → retour | l.131306 |

★ **`0xE880A` = protection surchauffe** : son axe température ne couvre que 111…122 °C.

### 3.4 Les limiteurs à deux modes — `0xE2078` / `0xE211A` → `C682` / `C688`

```asm
loc_B15BA:                          ; l.180281
    mov  r12, r0
    mov  r13, r7
    mov  r14, word_144E      ; 9 pts -> 0xE13DC
    calls 0, unk_1D6C
    mov  r12, #0C83Eh        ; X = variable RAM 0xC83E
    mov  r13, r0
    mov  r14, word_1446      ; -> EA 0xE2078
    calls 0, word_1D94
```

| carte | mode | X | Y | sortie | code |
|---|---|---|---|---|---|
| **`0xE13DC`** `[C]` | commun | `D904 − C678/C67A` | — | courbe 9 pts → Y | l.177869, 177899… 189231 |
| **`0xE2078`** `[C]` | `byte_C339 = 0` | `0xC83E` | `r0` | **`C682`** (plafond) | 6 sites : 177873, 177949, 180285, 180362, 181191, 181268 |
| **`0xE211A`** `[C]` | `byte_C339 ≠ 0` | `0xC83E` | `r0` | **`C688`** (plancher) | 6 sites : 177903, 177979, 180316, 180392, 181222, 181298 |

*Note honnête* : le code **utilise** bien ces deux blocs comme tables 2-D (pointeurs passés à
`word_1D94`). Leur découpage interne en 7×8 reste une hypothèse (É.118), **pas** leur usage.

---

## 4. L'ARBITRAGE FINAL — l'enchaînement exact

```asm
loc_B2EB4:                          ; l.182780
    mov  word_C6A4, r4            ; C6A4 := C6B8
    ...
loc_B2EE2:  mov word_D9AA, r4     ; D9AA := C6A4 (ou C6A4 − C69E si byte_D9AC = 1)

loc_B2F18:  cmp D9A6, C688        ; PLANCHER
            mov word_C6AE, r4
loc_B2F2C:  cmp D9A6, C682        ; PLAFOND
loc_B2F46:  cmp D9A6, C6C0        ; PLAFOND final
            mov word_C6AA, r4
```

Puis l'étage de lissage :

| étape | valeur | code |
|---|---|---|
| plancher `C680` (= régulateur) | `C6B8` | l.186651 |
| plafonds `C67E` / `C696` | `C6A4` | l.182781 |
| plancher `C688` | `C6AE` | l.182816-822 |
| plafond `C682` | `C6AA` | l.182829-835 |
| plafond `C6C0` | `C6AA` | l.182843-849 |
| **filtre `sub_AF75A`** | **`C6B2`** | l.182870 (écriture) |

```asm
loc_B2F50:                          ; l.182850
    mov  r4, word_C6C0
    cmp  r4, word_C6AA
    bset ...                        ; témoin « limitation active »
```

---

## 5. CE QUI PART VERS LES INJECTEURS

### 5.1 Branche A — la commande de pompe (parallèle, pas dans la chaîne de quantité)

```asm
loc_B2EEA:                          ; l.182807
    mov  word_D3D4, r4            ; D3D4 := D9AA (demande d'IQ)
    mov  r12, word_1B5E           ; -> EA 0xE8A06
    mov  r13, word_C91C           ; régime
    mov  r14, word_D9AA           ; IQ
    calls 0, unk_1D50
    movb byte_C8F8, rl4           ; ★ OCTET de commande 0…250
```

**`0xE8A06`** `[C]` — `f(régime 0…5002 × IQ 0…8000)` → **`byte_C8F8`** = commande d'électrovanne HP.

### 5.2 Branche B — la conversion finale en grandeur d'injecteur

Trois évaluations en série, chacune **1-D puis 2-D** :

```asm
loc_B6D1C:                          ; l.189152
    mov  r12, r0
    mov  r13, word_C6AA           ; IQ final
    mov  r14, word_144C           ; 1-D -> 0xE13C6
    calls 0, unk_1D6C
    mov  r12, #6
    add  r12, r0
    mov  r13, r0
    mov  r14, word_1444           ; 2-D -> 0xE130E
    calls 0, word_1D94
    mov  [r0+#12h], r4
    add  r4, word_C678            ; + offset
```

| carte | axe X | axe Y | sortie | code |
|---|---|---|---|---|
| **`0xE13B0`** `[C]` | `C42E` régime 0…4500 (9) | `C6A2` charge 0…8000 (9) | préparation | l.189063, 189304, 189327 |
| **`0xE13C6`** `[C]` | `C6A2` charge 0…8000 (9) | **`C63C`** 0…15360 (9) | Y de la carte 2-D | l.189069, 189090, 189113, 189134, 189155, 189522 |
| **`0xE130E`** `[C]` | `C3EE` 0…4500 (16) | `C3EE` (16) | **`D418` / `D41A` / `D41C`** | l.189118, 189139, 189160, 189526 |
| `0xE8E26` (`1BEE`) `[C]` | — | — | `+C67A` → `r8` | l.189073 |

Puis les **écarts à la référence `C640`** :

```asm
loc_B6D5E:                          ; l.189176
    mov  word_D41C, r8
    mov  word_D41A, r6
    mov  word_D418, r4
    sub  r5, word_C640  →  mov word_C63E, r5
    sub  r2, word_C640  →  mov word_C63C, r2
    sub  r3, word_C640  →  mov word_C63A, r3
```

### 5.3 La dernière conversion avant l'injecteur

```asm
    mov  r12, word_C63A        ; l.139993 / l.140183
    mov  r5, word_1660
    mov  r13, [r5]             ; paramètre de calibration
    mov  r2, word_1658
    mov  r14, [r2+#2]          ; second paramètre
    calls 0, unk_20AC          ; ★ conversion
    cmp  r4, #0FEh             ; saturation 0…254
    movb byte_C821, rl4        ; ★ SORTIE OCTET
```

Sorties : **`byte_C88A`, `byte_C820`, `byte_C821`, `byte_C822` (avec `C640`), `byte_C823`, `byte_C824`,
`byte_C81B … byte_C81F`** — puis relues à l.141404 (`C825`), l.141420 (`C827`), l.141664 (`C828`),
l.141908 (`C829`) par l'étage de commande d'injection.

---

## 6. LA CHAÎNE, EN UN SEUL SCHÉMA

```
RÉGIME C91C · PÉDALE C952 · AIR C3E6 · T°LDR C908 · T°GASOIL C900 · VITESSE C562 · RAPPORT C576
   │
   ├─► [select. C576 vs 539]
   │        └─► 0xE8BD4 (1re/2e) │ 0xE8B50  = f(régime, pédale)  ──► C6A6   ← SOUHAIT
   │
   ├─► 0xE8444 = f(régime, air) ─────────────► C690  ← SMOKE  (~15-76 mm³)
   ├─► 0xE8000 / 0xE7F7E = f(régime, T°gasoil) ► D8C4 ← T° CARBURANT
   ├─► 0xE80A0 / 0xE86F4 / 0xE868C / 0xE880A / 0xE3908 = f(…, T°LDR)  ← T° MOTEUR
   ├─► 0xE13DC → 0xE2078 | 0xE211A ───────────► C682 (plafond) / C688 (plancher)
   │
   └─► RÉGULATEUR C698 ──plafonné par C690──► C680 (plancher)
                     │
        C6A6 ──max(C680)──► C6B8 ──plafonds C67E/C696──► C6A4
                                                            │
                                    ┌───────────────────────┤
                                    │                       │
                              D9AA (IQ)                 D9AA copié → D3D4
                                    │                       │
                        plancher C688 / plafond C682        └─► 0xE8A06 = f(régime, IQ)
                        plafond C6C0                              └─► byte_C8F8 (POMPE HP)
                                    │
                                C6AA ──sub_AF75A──► C6B2   ← IQ FINAL
                                    │
                ┌───────────────────┘
                │   1‑D 0xE13C6  +  2‑D 0xE130E   (×3)
                ▼
        D418 / D41A / D41C  ──écarts vs C640──►  C63A / C63C / C63E
                                                      │
                                              unk_20AC  (0 … 254)
                                                      ▼
                                    byte_C81B…C829, byte_C88A
                                                      ▼
                                              INJECTEURS
```

---

## 7. TABLEAU DE VÉRITÉ — toutes les cartes de la séquence

| # | carte | axes | sortie | preuve | statut |
|---|---|---|---|---|---|
| 1 | `0xE8BD4` | régime × pédale | `C6A6` | l.186835 | **[C]** |
| 2 | `0xE8B50` | régime × pédale | `C6A6` | l.186843 | **[C]** |
| 3 | `0xE8444` | régime × **air** | `C690` | l.181914 / 181950 | **[C]** |
| 4 | `0xE87D6` | régime × `C3EC` | `C690` | l.181946 | **[C]** |
| 5 | `0xE8000` | régime × **T° gasoil** | `D8C4` | l.177109/127/184 | **[C]** |
| 6 | `0xE7F7E` | régime × T° gasoil chaude | `D8C4` | l.177139/157/173 | **[C]** |
| 7 | `0xE80A0` | régime × **T° LDR** | retour | l.177378 | **[S]** |
| 8 | `0xE86F4` | régime × T° LDR | `[r0]` | l.182069 | **[C]** |
| 9 | `0xE868C` | T° LDR × **vitesse** | `D98A` | l.182115 | **[C]** |
| 10 | `0xE880A` | régime × T° LDR 111-122 °C | `r9` | l.182258 | **[C]** |
| 11 | `0xE3908` | régime × T° LDR | retour | l.131306 | **[S]** |
| 12 | `0xE13DC` | `D904−offset` (9 pts) | Y | 14 sites | **[C]** |
| 13 | `0xE2078` | `0xC83E` × Y | `C682` | 6 sites | **[C]** usage |
| 14 | `0xE211A` | `0xC83E` × Y | `C688` | 6 sites | **[C]** usage |
| 15 | `0xE8A06` | régime × IQ | `byte_C8F8` | l.182813 | **[C]** |
| 16 | `0xE13B0` | régime × charge | prép. | l.189063/304/327 | **[C]** |
| 17 | `0xE13C6` | charge × `C63C` | Y | l.189069…189522 | **[C]** |
| 18 | `0xE130E` | `C3EE` × `C3EE` | `D418…` | l.189118/139/160/526 | **[C]** |
| 19 | `0xE8E26` | — | `r8` | l.189073 | **[C]** usage |

**Total : 19 cartes, 100 % adossées à une ligne de code.**

---

## 8. Ce qui reste ouvert (dit franchement)

1. **`C3E6`** (axe air de la smoke map) est initialisé à **10000** (l.131320) et **jamais réécrit dans
   la zone désassemblée** ⇒ il est rafraîchi par la **partie basse du code**, hors dump. C'est la
   même limite que pour `0xC83E`.
2. **`0xE2078`/`0xE211A`** : usage 2-D prouvé, découpage interne encore hypothétique.
3. **`D8C4`, `D98A`, `D986`** : produits prouvés, mais leur **consommation** se fait hors zone
   désassemblée pour partie.
4. **Les paramètres `[word_1660]` et `[word_1658+2]`** de `unk_20AC` n'ont pas encore été nommés.

## 9. Le levier pratique

La **smoke map `0xE8444`** plafonne `C698` (le régulateur) **et** alimente `C690`, qui remonte la
chaîne. Avec `0xE8BD4` (souhait 1re/2de), ce sont **les deux seules cartes à toucher** pour un gain en
bas rapport — les courbes `0xE83xx` et les blocs 162 octets n'étant pas les bons leviers.
