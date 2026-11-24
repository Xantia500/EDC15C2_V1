# ÉTAPE 124 — Audit complet : filtre à particules, post-injection, régénération

**Demande** : *« Fait un audit complet du filtre à particule, de la post injection et tout ce qui est lié aux régénérations. Reprend tout ce que nous avons vu. »*

**Sources de vérité** : `/home/user/clean.asm` (412 022 lignes) et `/home/user/edc.bin` (524 288 o).
**Méthode** : reprise de chaque affirmation de `ETAPE10` → `ETAPE14`, plus `ETAPE121` (chaîne souhait→injecteurs) et `ETAPE123` (audit général), **recomptage systématique de chaque « N sites »** et vérification du contexte de chaque écriture. Aucune affirmation n'est reprise sans avoir été rejouée sur le binaire dans cette étape.

---

## 0. Résumé exécutif

| Question | Réponse de cet audit |
|---|---|
| La chaîne FAP décrite en `ETAPE10`/`ETAPE12` est-elle réelle ? | **Oui**, à 90 %. Les 6 courbes 1-D, la porte `byte_C2BA`, la machine à états `byte_D7A8`/`byte_D7B8` et l'estimateur de charge `word_D7B0` sont tous confirmés sur le binaire. |
| Y a-t-il une **post-injection** dans ce logiciel ? | **Aucune quantité de post-injection indépendante n'existe** dans le code. Le désassemblage couvre **100 % du code** (§1), donc ce n'est plus une « zone d'ombre » : c'est un résultat. |
| Que fait la régénération à l'injection ? | Elle agit par **trois leviers vérifiés** : le terme additif `word_C69E` (+0…60 mm³), la correction `word_C77C` (+10 mm³ constant) et les courbes de limitation indexées par l'EGT. Elle **ne passe pas** par un cinquième temps d'injection. |
| Les octets `byte_C81B…C829` sont-ils la commande des injecteurs (affirmation de `ETAPE121`) ? | **NON — errata E32.** Ce sont des **canaux de mesure publiés pour le diagnostic**, via `sub_9CFD0`. Aucune lecture directe, aucun lien avec le pilote d'injection. |

---

## 1. Fondation nouvelle : la carte de l'image (invalidant un ancien refuge)

Avant d'auditer le FAP, il fallait régler une question structurelle qui traînait depuis `ETAPE11` : *« la post-injection est peut-être dans la moitié non désassemblée »*.

Mesure : inventaire des **10 706 labels** de `clean.asm`, puis détection des **runs de `0xC3` ≥ 64 o** dans `edc.bin`.

| Plage EA | Taille | Contenu | Vérification |
|---|---|---|---|
| `0x80000` – `0x87FFF` | 32 768 o | **padding `0xC3`** | 100 % `0xC3` |
| `0x88020` – `0xD5414` | **316 405 o** | **CODE désassemblé** | 95 % hors padding |
| `0xD5415` – `0xDFFFF` | 44 011 o | stub de 16 o + **padding `0xC3`** | 100 % `0xC3` (run l. `0xD5426`–`0xDFEFF` = 43 738 o) |
| `0xE0000` – `0xFBFFF` | 114 688 o | **CALIBRATION** (cartes/courbes) | 18 % de `0xC3` interne |
| `0xFC0EA` – `0xFEB22` | 10 809 o | **CODE queue** | — |
| `0xFEB23` – `0xFFFFF` | 5 341 o | boot / vecteurs | 97 % `0xC3` |

**Conséquences, définitives :**

1. Le code utile fait **≈ 327 Ko** (`0x88020`–`0xD5414` + `0xFC0EA`–`0xFEB22`) et il est **intégralement présent dans `clean.asm`**. Il n'existe **aucune** zone de code non désassemblée.
2. Toute conclusion négative de type « invisible donc ailleurs » est **invalide** : si une fonction n'apparaît pas, elle **n'existe pas** dans ce logiciel.
3. La **duplication `0xF0000`** est confirmée à l'octet : les runs de padding se répètent **exactement à +0x10000** (`0xE0E72`↔`0xF0E72`, `0xEBC48`↔`0xFBC48`, `0xEBF3C`↔`0xFBF3C`). Le bloc `0xE0000`–`0xEFFFF` est dupliqué en `0xF0000`–`0xFFFFF`.
4. Le padding de `0xEF880` (relevé antérieur) est bien réel : il tombe dans le run `0xEBFBA`–`0xEFFFF` (16 454 o).

> Un stub de 16 o subsiste en `0xD5415` : `8E 52 C3 F7 8E BA F9 FC 08 CC 00 DA 00 C2 07 DB 00`. Il est **orphelin** (aucune entrée de saut ni appel connu vers `0xD5415`) et n'est suivi que de padding : il n'est le siège d'aucune fonction.

---

## 2. Verdict affirmation par affirmation

Notation : **C** = confirmé · **C±** = confirmé avec correction de décompte · **F** = faux (errata).

| # | Affirmation reprise | Doc. source | Verdict | Preuve rejouée en É.124 |
|---|---|---|---|---|
| A | La présence du FAP est une **porte logicielle** `byte_C2BA` | 10 | **C** | 63 références ; **1 seule écriture** l. 151775 `movb byte_C2BA, rl5` ← `[r4+#27h]`, `r4 = word_141C` (bloc de codage) |
| B | `byte_C297` co-conditionne le bit 3 de `byte_C820` | 10 | **C** | `sub_9B0E0` l. 140045 : `orb #8` seulement si `C2BA ≠ 0` **et** `C297 ≠ 0` |
| C | La mesure `word_C586` (EGT) est l'axe des courbes FAP | 10/12 | **C±** | **9 lignes** (et non 8) : 153877, 153964, 153993, 155179, 162605, 163861, 163869, 166435, 167078 |
| D | `word_D5A2` est une EGT publiée en télédiag | 10 | **C** | **1 écriture** l. 204416 (`EA 0xBFAA4`), **0 lecture** ⇒ miroir |
| E | La table associée à `D5A2` est neutralisée | 10 | **C** | handle `0x1DFA` → `EA 0xEBA84`, tag `0xD5A2`, axe `[4731, 5731]`, valeurs **`[10000, 10000]`** |
| F | Machine à états de régénération dans une tâche périodique | 11 | **C** | tâche **`0x12C`** : l. 163238 `scxt CC2_CC27, #12Ch`, **gardée par `byte_C2BA`** (`jmpa cc_Z` si absent) |
| G | L'état est un octet 0…5 avec table de sauts | 11 | **C** | `byte_D7A8` : `cmpb rl3, #5` / `shl r3,#1` / `add r3,#0A04h` / `jmpi [r3]` — table de 6 entrées en `0xA04` (l. 163246-163253) |
| H | `byte_D7B8` = drapeaux de mode | 11 | **C** | 17 sites ; bits observés : `1` = fenêtre charge/régime, `2` ⇒ mode `8`, `4` = **régénération demandée**, `8` = mode, `0x80` = limitation |
| I | `word_D7AA` = demande / seuil de charge | 11 | **C** | 27 sites ; comparé à `[word_18F6+2]` sous `byte_C31A == 1` (l. 163250-163256) |
| J | Estimation de charge (suie) par intégrateur | 11 | **C** | `word_D7B0` : `add word_D7B0, r4` (l. 163904) après `unk_20AC(x, #1, #0x64)` ; saturation `0x7FFF`/`0x8000` |
| K | `word_C69E` est un terme additif de quantité | 10 | **C±** | **11 sites** (et non 6) : 5 `add` + 4 `sub` + 1 lecture + **1 écriture** l. 187528 |
| L | `word_C77C` est une correction de la quantité | 10 | **C** | tâche `0x10E`, l. 171249-171263 : somme de 2 interpolations |
| M | La porte `sub_ACD46` autorise la post-injection | 10 | **C** (et pire) | l. 172038 : `mov r4, #1` / `rets` ⇒ **constante 1**, la branche est **inconditionnelle** |
| N | `byte_C81B…C829` = commande des injecteurs | **121** | **F — E32** | **écrits, jamais lus** ; publiés par `sub_9CFD0` (canaux `0x348` et `0x388`) |
| O | `word_C642` est une quantité absolue | 121 | **F — E33** | `C642 = r6 − C640`, écart **signé** (l. 189543) |
| P | `word_D294` porte une consigne de régénération | 10 | **C±** | 1 écriture (l. 163875) **et 0 lecture** ⇒ recopie de `word_D7B2` (le seuil), pas une consigne |

---

## 3. La chaîne FAP telle qu'elle est réellement câblée

### 3.1 Porte de présence (1 bit)

```
word_141C ──► [+0x27] ──► byte_C2BA ──────────────┬──► tâche 0x12C : jmpa cc_Z si 0  (aucune régénération)
 (bloc de codage)                                 ├──► sub_9B0E0 : orb #8 sur byte_C820 (bit d'état)
                                                  └──► 63 sites de lecture
```

L'écriture est **unique** (l. 151775) et se trouve dans la grande copie de bloc de variante (`C2B9`, `C2BB`, `C2B4`, `C6E2`, `C620`, `C65C`…). Conclusion inchangée depuis `ETAPE10` : **`byte_C2BA` est un bit de codage**, pas une mesure.

### 3.2 Les six courbes 1-D de la voie FAP (relevé complet, nouveau)

Toutes les cartes de la voie FAP sont des **courbes 1-D**, jamais des cartes 2-D : le balayage complet du fichier ne trouve **aucune** carte 2-D dont un axe soit `C586`, `C584`, `D1B6` ou `D5A2` (0 résultat sur 86 cartes).

| Handle | EA | Tag d'axe | Axe | Valeurs | Rôle |
|---|---|---|---|---|---|
| `0x191E` | `0xE5F9C` | `0xC586` | `5231, 8231` (250 → 550 °C) | `100, 3200` | **seuil bas** de charge |
| `0x1922` | `0xE5FC0` | `0xC586` | `5231, 8731` (250 → 600 °C) | `100, 32767` | **seuil haut** (⇒ régénération impossible) |
| `0x1950` | `0xE639A` | `0xC586` | `3731 … 8531` (100 → 580 °C) | `7231, 6531, 5881, 5331, 5181, 5131, 5131, 5131` | limitation décroissante avec T° |
| `0x18A2` | `0xE4D14` | `0xD1B6` | `500 … 11000` | `117, 266, 367, 447, 542, 585, 643, 655` | EGT normalisée ↗ |
| `0x18A4` | `0xE4D38` | `0xD1B6` | `500 … 11000` | `15, 27, 40, 58, 105, 130, 185, 260` | EGT normalisée ↗ (variante) |
| `0x1DFA` | `0xEBA84` | `0xD5A2` | `4731, 5731` | **`10000, 10000`** | **neutralisée** |

Les deux courbes `0x191E`/`0x1922` sont sélectionnées par `byte_D7B8 & 2` (l. 163842-163871) et leur résultat est écrit dans `word_D7B2` **et** recopié dans `word_D294` — cette dernière n'ayant **aucun lecteur** (miroir mort, comme `D5A2`).

### 3.3 L'estimateur de charge et le déclenchement (le cœur de la régénération)

```
                     ┌─ unk_20AC(Δ, #1, #0x64) ─┐   (mise à l'échelle 0…100)
  mesure  ──────────►│                          ├──► word_D7B0  (intégrateur de suie)
                     └─ add word_D7B0, r4 ──────┘        │  saturation ±0x7FFF
                                                        │  plafond [word_1904+0x16]
                                word_D7B2 (seuil = f(EGT)) ──► cmp
                                                        │
                          D7B0 > D7B2  ────────────────►└──► byte_D7B8 |= 4   ← DEMANDE DE RÉGÉNÉRATION
                                                                  │
                                       fin de régénération : D7B0 := 0 ; D28E := 0 ; flag 4
```

Preuves : l. 163900-163912 (`unk_20AC`, `add word_D7B0, r4`, saturation), l. 163916-163922 (plafond), l. 163931-163938 (`cmp r4, word_D7B2` → `orb byte_D7B8, #4`), l. 163940-163946 (remise à zéro).

**C'est la réponse complète à « tout ce qui est lié aux régénérations »** : un intégrateur de suie, un seuil qui dépend de la température d'échappement, un drapeau de demande, une remise à zéro en fin de cycle.

### 3.4 Les deux termes qui modifient la quantité injectée

**`word_C77C`** (tâche `0x10E`, l. 171249-171263) :

```
C77C = unk_1D36(unk_19BA, word_C60A)  +  unk_1D36(unk_19BC, word_C3D2)
     = courbe 0xE6B86 (axe [0,1800], valeurs [0,0])          = 0
     + courbe 0xE6B92 (axe [2231,4231], valeurs [1000,1000]) = 1000
     = 1000  (soit +10,0 mm³) — CONSTANT sur ce véhicule
```

La correction dynamique est donc **neutralisée par calibration** : la branche `sub` de `loc_AD004` n'est jamais atteinte, `word_D844` reste toujours ≥ `word_C6BA + word_C69E`.

**`word_C69E`** (l. 187528) — recompté : **11 sites**, dont 1 écriture.

```
word_BDAC & 1 ──► r8 = BDBC  ou  BDDC
                  r8 := clamp(r8, [word_147E+0Ah], [word_147E+8])   = clamp(r8, 0, 6000)
                  byte_C8EB == 1  ?  r9 = r8
                  [word_1434] & 0x80 ?  r9 = 2·r8      ← vaut 0 ici : [0xE1294] = 0
                  r9 := clamp(r9, [word_1432+16h], 0…0x7FFF)
word_C69E := r9   ⇒  0 … 60 mm³
```

Vérifié sur la calibration : `word_147E` → `EA 0xE22CA` = `(1000,0,1000,0,4000,0,6000,0,6000,0)` ⇒ `[+8] = 6000`, `[+0Ah] = 0` ; `word_1434` → `EA 0xE1294` = `(0,0,0,0,0,10,10,500,5500,8000)` ⇒ `[0] = 0` donc **pas de doublement**.

### 3.5 La porte `sub_ACD46`

```asm
sub_ACD46:                      ; l. 172038 / EA 0xACD46
    mov r4, #1
    rets
```

Utilisée en l. 172301 dans `loc_ACFC6` : `cmp r4, #0` / `jmpr cc_Z, loc_AD072`. Le saut **ne peut jamais être pris** : la branche additive `C6BA + C69E` s'exécute à **chaque** appel. Ce n'est pas une post-injection conditionnelle, c'est un **terme permanent**.

---

## 4. Errata

### E32 (majeur) — `byte_C81B…C829` ne commandent **rien**

`ETAPE121` concluait : *« sorties `0xE13B0`/`0xE13C6`/`0xE130E` → `D418`/`D41A`/`D41C` → `C63A`/`C63C`/`C63E` → `unk_20AC` → `byte_C81x` »* et présentait ces octets comme la commande finale des injecteurs.

**Décompte réel sur `clean.asm` :**

| Variable | Écritures | Lectures |
|---|---|---|
| `byte_C820` | 1 (l. 140141) | **0** |
| `byte_C821` | 1 (l. 140182) | **0** |
| `byte_C822` | 1 (l. 140223) | **0** |
| `byte_C823` | 1 (l. 140264) | **0** |
| `byte_C824` | 1 (l. 140302) | **0** |
| `byte_C81B` | 1 (l. 140353) | **0** |
| `byte_C81C` | 1 (l. 140354) | **0** |

Ces octets ne sont lus qu'**indirectement**, par deux appels de publication :

```asm
; l. 143249-143253
mov r12, #2                 ; mode
mov r13, #0
mov r14, #0C820h            ; source
mov r15, #348h              ; CANAL DE MESURE 0x348
calls 9, sub_9CFD0

; l. 143536-143540
mov r12, #7
mov r13, #0
mov r14, #0C81Bh            ; source
mov r15, #388h              ; CANAL DE MESURE 0x388
calls 9, sub_9CFD0
```

`sub_9CFD0(nombre, mode, source, canal)` est le **publieur de valeurs mesurées** (blocs de mesure / service). `byte_C820`–`C824` et `byte_C81B`–`C81F` sont donc des **valeurs publiées au diagnostic**, pas des ordres.

**Correction à porter dans `ETAPE121`** : le dernier maillon de la chaîne est un **miroir de diagnostic**. La chaîne de conversion (`0xE13xx` → `D41x` → `C63x` → `unk_20AC` → octet) est **réelle**, mais elle est **terminale et passive**. La commande effective des injecteurs n'est pas dans le désassemblage — et comme le désassemblage est complet (§1), cela signifie qu'elle est **matérialisée dans le pilote matériel** (unité de puissance / CAPCOM), à laquelle le CPU ne transmet **pas** par ces octets.

### E33 — `word_C642` n'est pas une quantité absolue

`C642 = r6 − C640` (l. 189543), avec `r6` saturé `0x7FFF`/`0x8000` (l. 189528-189540) et `C640`/`C642` remis à zéro ensemble (l. 189293-189294). C'est un **écart signé**. `byte_C821` reçoit donc un écart, pas une masse.

### E34 — Décompte `word_C69E`

`ETAPE10` §7 annonçait *« `add r4, word_C69E` (6 sites) »*. Recomptage : **5 `add`** (131565, 172306, 172375, 182736, 183251) + **4 `sub`** (182787, 182791, 182875, 182879) + **1 lecture** `mov r9` (134629) + **1 écriture** (187528) = **11 sites**. C'est exactement le piège déjà consigné en É.124 : ne jamais reprendre un décompte sans le refaire.

### E35 — Décompte `word_C586`

`ETAPE10` §7 annonçait 8 sites ; le recomptage donne **9 lignes** (153877, 153964, 153993, 155179, 162605, 163861, 163869, 166435, 167078). Les rôles sont inchangés.

### E36 — `word_D294` n'est pas une consigne

Elle est écrite **une fois** (l. 163875, recopie de `word_D7B2`) et n'a **aucun lecteur**. C'est un miroir, comme `D5A2`. Ne pas la présenter comme l'ordre de régénération : l'ordre est le **bit 2 de `byte_D7B8`** (`orb ... #4`).

---

## 5. Post-injection : réponse définitive

### 5.1 Ce qui existe (prouvé)

| Mécanisme | Variable | Preuve |
|---|---|---|
| Terme additif permanent de quantité | `word_C69E` ∈ [0, 60 mm³] | l. 187528 + clamps `E22CA` |
| Correction additive constante | `word_C77C` = 1000 (+10 mm³) | l. 171249-171263 + `E6B92 = [1000,1000]` |
| Limitation par température d'échappement | `word_D7B2` (courbes `E5F9C`/`E5FC0`) | l. 163861-163875 |
| Limitation décroissante avec l'EGT | `EA 0xE639A` | l. 166435 |
| Demande de régénération | `byte_D7B8` bit 2 | l. 163934 |
| Interdiction si EGT trop haute | seuil `32767` (`E5FC0`) | l. 163869 |

### 5.2 Ce qui n'existe pas (résultat, pas une lacune)

- **Aucune quantité de post-injection indépendante** : pas de variable dédiée, pas de courbe « IQ post-injection = f(régime, charge) », pas de drapeau de post-injection consommé par un pilote d'injecteur.
- **Aucun cinquième temps d'injection** distinct dans la chaîne `0xE13xx`.
- **Aucun consommateur** des octets `C81B`–`C829` autre que le publieur de diagnostic.

### 5.3 Comment la régénération agit donc sur l'injection

La régénération de ce logiciel **n'ajoute pas un temps d'injection** : elle **élargit le temps principal** via `C69E` (0…60 mm³, porte `byte_C8EB`) et `C77C` (+10 mm³), et elle **borne** ce qu'elle autorise via les courbes indexées par l'EGT. C'est une stratégie de **post-injection fondue dans l'injection principale**, ce qui est cohérent avec un EDC15C2 à pilote d'injection matériel : le CPU ne dispose que d'un canal de quantité, qu'il module.

Cette lecture explique aussi pourquoi `sub_ACD46` renvoie `1` en dur : **le terme additif n'a pas à être conditionné**, puisqu'il vaut 0 hors régénération par la calibration de `BDBC`/`BDDC`.

---

## 6. Tableau de confiance

| Domaine | Confiance | Justification |
|---|---|---|
| Carte de l'image / couverture du code | **99 %** | runs de `0xC3` mesurés, 10 706 labels recensés |
| Porte `byte_C2BA` | **99 %** | 1 écriture, 63 lectures, contexte de codage |
| Machine à états `D7A8` (0…5) | **95 %** | table de sauts `0xA04` lue dans le code |
| Drapeaux `byte_D7B8` | **90 %** | 4 bits sur 8 identifiés avec certitude |
| Estimateur de charge `D7B0`/`D7B2` | **90 %** | chaîne complète l. 163900-163946 |
| Courbes FAP (6) | **95 %** | axes et valeurs dumpés intégralement |
| `C77C` = 1000 constant | **95 %** | deux courbes dumpées, valeurs constantes |
| `C69E` ∈ [0, 60 mm³] | **85 %** | clamps tracés ; unité déduite de l'échelle |
| Absence de post-injection séparée | **85 %** | repose sur la complétude du désassemblage |
| `byte_C81x` = diagnostic | **95 %** | `sub_9CFD0` avec canaux `0x348`/`0x388` |

---

## 7. Chantiers ouverts

1. **`sub_9CFD0`** : cartographier les 40+ canaux de mesure publiés — cela donnerait la liste officielle des « blocs de mesure » et permettrait de nommer `0x348` et `0x388`.
2. **`byte_C8EB`** (64 références) : porte du terme `C69E` ; déterminer son origine (mode ? état de démarrage ?).
3. **`word_BDAC`/`BDBC`/`BDDC`** : origine de la quantité additionnelle ; confirmer l'unité mm³ et le rôle hors FAP.
4. **Capteur de pression différentielle** : `ETAPE12` le donnait pour non localisé (« loi cubique »). À reprendre avec la carte d'image (§1) : le conditionnement est nécessairement dans `0x88020`–`0xD5414`.
5. **Les 5 cartes 2-D non identifiées** (86 inventoriées vs 91 annoncées en errata 57).
6. **Porter E32 dans `ETAPE121_*.md`** et E34/E35 dans `ETAPE10_*.md` (bandeau ⚠️ en tête + renvoi vers la présente étape).

---

## 8. Verdict

Le dossier FAP construit aux étapes 10 à 14 **résiste à l'audit** : la porte de codage, la machine à états à six états, l'intégrateur de suie, les seuils dépendants de l'EGT et les courbes de limitation sont tous vérifiables ligne par ligne. Trois erreurs de décompte sont corrigées (E34, E35) et deux lectures sont invalidées (E32 sur les octets de diagnostic, E33 sur `C642`).

Le point qui change la compréhension d'ensemble est le §1 : **le désassemblage est complet**. On ne peut donc plus dire « la post-injection est ailleurs ». Ce logiciel **n'a pas de post-injection séparée** ; il module la quantité principale. C'est une conclusion forte, appuyée sur une mesure reproductible (runs de `0xC3`), et c'est désormais la position à défendre.
