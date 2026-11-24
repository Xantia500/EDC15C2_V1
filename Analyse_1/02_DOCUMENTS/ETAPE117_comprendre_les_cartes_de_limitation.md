# ÉTAPE 117 — Comprendre les cartes de limitation (explication pas à pas)

> ## ⚠️ PÉRIMÉ (audit Étape 123)
>
> La lecture « couple → débit » et l'unité « 0,01 N.m » sont **RETIRÉES** (errata **E27**).
> Restent valables : la convention d'appel `word_1D94(ptrX, ptrY, handle)`, l'exclusivité des deux
> cartes via `byte_C339`, et l'inventaire des 12 sites. Voir `ETAPE118` et `ETAPE123`.


Ce document reprend tout depuis le problème physique, sans jargon, pour expliquer **ce que sont**
les cartes `0xE2078` et `0xE211A`, **à quoi elles servent** et **comment les lire**.

---

## A. Le problème que ces cartes résolvent : deux unités incompatibles

Le calculateur raisonne en permanence dans **deux unités différentes** :

| unité | ce que ça représente | exemple de variable |
|---|---|---|
| **couple** (N.m) | l'effort mécanique demandé à l'arbre | `D904`, `C698` |
| **débit de gasoil** (mm³/coup) | ce qu'on injecte réellement | `C6A6`, `C6B2` |

Tous les **protecteurs** du moteur raisonnent en **couple** :
- la boîte de vitesses (elle ne supporte qu'un couple max),
- le limiteur de fumée (au-delà d'un certain couple à bas régime, ça fume),
- l'ABS/ESP (il demande moins de couple quand une roue patine),
- le régulateur (il demande « plus » ou « moins » de couple).

Mais le système d'injection, lui, ne sait faire qu'une chose : **ouvrir l'injecteur X millisecondes**,
c'est-à-dire injecter **X mm³**.

> **Il faut donc un traducteur couple → mm³. C'est exactement le rôle de nos deux cartes.**

C'est le point clé : **ces cartes ne sont pas des cartes de puissance ni d'agrément.** Ce sont des
**tables de conversion** (« combien de gasoil pour ce couple-là, dans ces conditions-là »).

---

## B. Où elles se situent dans la chaîne complète

```
   PÉDALE + RÉGIME
        │
        ▼
   CARTES SOUHAIT  (0xE8B50 / 0xE8BD4)        ← ce que le conducteur DEMANDE  (en mm³)
        │  (sélection 1re/2nde par ratio 539)
        ▼
      C6A6  ────────────────────────────────┐
        │                                    │
        │   ┌──────────────────────────────┐ │
        │   │  LIMITEURS (en COUPLE)       │ │
        │   │  D904 = min(régulateur,      │ │
        │   │         couple max, ...)     │ │
        │   └──────────────┬───────────────┘ │
        │                  │                 │
        │                  ▼                 │
        │        ★ CARTE DE CONVERSION ★     │
        │        (0xE2078 / 0xE211A)         │
        │                  │                 │
        │                  ▼                 │
        │            C682 (plafond)          │
        │            C688 (plancher)         │
        │                  │                 │
        ▼                  ▼                 ▼
      ┌──────────────────────────────────────────┐
      │  CASCADE : on borne le souhait           │
      │  résultat = min(souhait, ce qu'on peut)  │
      └──────────────────────────────────────────┘
                       │
                       ▼
                     C6B2  = quantité RÉELLEMENT injectée (mm³)
```

Autrement dit : **les cartes transforment « tu as droit à tant de couple » en « tu as droit à tant de
millimètres-cubes ».** C'est la brique qui empêche la mécanique et le nuage de fumée de se plaindre.

---

## C. Comment se lit une carte (rappel de base)

Une carte 2D = une **grille** :

- un **axe des colonnes** (8 points ici : `1460 3100 4608 … 17920`),
- un **axe des lignes** (7 lignes ici),
- dans chaque case, une **valeur**.

Le calculateur ne lit jamais une case exacte : il **interpole** entre les 4 cases voisines.
C'est le rôle de `word_1D94` (routine de bibliothèque).

```
                 colonnes (axe X : 8 points)
               1460  3100  4608  6144  7808  10768 14096 17920
        ligne 1  800  1538  2532  3605  4762  8582 12212 15540
        ligne 2  800  1492  2434  3336  4310  5593  6920  8480
   Y      ...
        ligne 7  720  1301  2123  2956  3905  5465  7348 11264
```

---

## D. Comment le code la lit — précisément

Le motif apparaît **12 fois** dans le firmware, toujours identique (Étape 115), et se lit en 3 étapes :

```asm
; ① on part du couple disponible, moins un offset
180260  r7 = D904 − C67A                  ; D904 = couple max autorisé (accumulateur)
                                          ; C67A (ou C678) = couple de référence à retirer

; ② une courbe 9 points "met en forme" ce couple
180281  unk_1D6C(dest = r0, x = r7, handle = word_144E)   ; → résultat écrit en [r0]

; ③ la carte 2D traduit en débit
180282  r12 = 0xC83E      ; ← POINTEUR vers la valeur X (variable en RAM)
180283  r13 = r0          ; ← POINTEUR vers la valeur Y (résultat de l'étape ②)
180284  r14 = word_1446   ; ← la carte (0xE2078 en mode 0, 0xE211A en mode 1)
180285  word_1D94(...)    ; → renvoie la valeur interpolée  = LE DÉBIT AUTORISÉ

180333  word_C682 = résultat   ; plafond appliqué au souhait
```

⚠ **Convention d'appel importante** (vérifiée sur 60 sites) : `r12` et `r13` sont des
**pointeurs**, pas des valeurs. `r12 = #0C83Eh` signifie « va chercher la valeur X à l'adresse
RAM `0xC83E` ».

**Donc les deux entrées de la carte sont :**

| entrée | origine | état |
|---|---|---|
| **Y** (lignes) | couple disponible `D904 − offset`, passé par la courbe 9 pts `0xE13DC` | ✅ calculé dans le code |
| **X** (colonnes) | la variable stockée à **RAM `0xC83E`** | ⚠️ **écrite hors zone désassemblée** |

---

## E. Les deux cartes, en détail

| | carte n°1 | carte n°2 |
|---|---|---|
| handle | `0x1446` | `0x1448` |
| adresse | `0xE2078` | `0xE211A` |
| taille | 162 octets | 162 octets |
| offset de couple utilisé | **`C678`** | **`C67A`** |
| axe X | `1460 · 3100 · 4608 · 6144 · 7808 · 10768 · 14096 · 17920` | `1080 · 2710 · 4200 · 5632 · 7040 · 8960 · 10880 · 13184` |
| plage de sortie | 720 → **15 540** | 610 → **10 964** |

**Ce qui les distingue :**

1. **Elles sont décalées** : l'axe X de la n°2 commence à 1080 au lieu de 1460, et finit à 13 184
   au lieu de 17 920. La n°2 couvre donc une plage **plus basse et plus courte**.
2. **La n°1 est plus permissive** : à ligne 1 / colonne 8, elle autorise `15540` contre `10544` pour
   la n°2 (soit **+47 %**).
3. **Elles ne sont jamais utilisées ensemble** : `byte_C339` choisit l'une **ou** l'autre
   (`= (C68A >= C626)`, calculé l.189047-189058). On est donc en présence de **deux modes
   d'exploitation**, pas de deux étages.

**Interprétation la plus probable du mode** : `C68A` et `C626` sont comparés dans la zone
**régulateur / décollage**. Les deux cartes correspondent donc très vraisemblablement à
**« avec » et « sans » une contrainte particulière** (embrayage débrayé, rapport engagé, mode
dégradé…). Le nom exact demanderait de suivre `C68A` et `C626`.

---

## F. Ce que signifient les nombres (hypothèses, clairement étiquetées)

| grandeur | lecture proposée | pourquoi |
|---|---|---|
| axe X : `1460 … 17920` | **vitesse 0,01 km/h** → 14,6 à 179,2 km/h | plage réaliste pour un véhicule ; c'est la seule lecture qui « tombe juste » |
| sortie : `610 … 15540` | **débit en 0,01 mm³** → 6 à 155 mm³ | c'est l'unité de toute la cascade ; mais 155 mm³ dépasse le maxi possible (80 mm³) |
| ou bien | **couple en 0,01 N.m** → 6 à 155 N.m | plage réaliste pour un limiteur de couple |

⚠ **Je ne tranche pas**, et c'est important :

- Si la sortie est en **mm³**, ces cartes ne brident quasiment jamais (leurs valeurs dépassent le
  maximum du souhait : elles ne servent qu'en cas extrême).
- Si la sortie est en **N.m**, la conversion en mm³ se fait **dans la bibliothèque** et un
  ajustement direct des cases n'a pas d'effet prévisible.

**Dans les deux cas, on ne peut pas encore dire « baisser telle case de X % donne +Y de couple ».**
C'est la limite honnête de ce chantier à ce stade.

---

## G. Pourquoi 7 lignes, et pourquoi l'en-tête est à zéro

Le format enregistré est :

```
[ 10 mots = 0 ][ axe X : 8 points ][ 7 × ( un 0 + 8 valeurs ) ]
```

- les **8 valeurs** par ligne = une valeur par colonne de l'axe X ✔ (cohérent),
- le **0** devant chaque ligne = un séparateur,
- les **10 mots à zéro** = un en-tête **neutralisé** : normalement il décrirait l'axe des lignes,
  mais il est vide.

⇒ **L'axe des lignes (les 7 lignes) n'est pas décrit dans la donnée** : il est **imposé par la
bibliothèque** (probablement 7 régimes, 7 rapports ou 7 températures). C'est ce qui empêche de
nommer les lignes — et donc de retoucher la carte intelligemment.

---

## H. Ce que l'on peut faire, et ce qu'on ne peut pas

**✅ Directement exploitable (unités et sélection entièrement comprises)**
- les **cartes souhait** `0xE8B50` / `0xE8BD4` (mm³, sélection par ratio `539`) — Étape 108 ;
- le **seuil 539** qui décide 1re/2nde vs le reste — Étape 108 ;
- les **seuils du régulateur** (`0xE2788 = 2500`, `0xE2792 = 768`) — Étapes 110-111.

**⚠️ Identifié mais NON modifiable en confiance**
- ces **deux cartes de conversion couple → débit** : on connaît leur adresse, leur taille, leur
  axe X et toutes leurs valeurs, mais **ni l'axe des lignes, ni l'unité certaine, ni le moteur
  d'interpolation** (bibliothèque absente du dump).

**🔍 Ce qui débloquerait tout (par ordre d'efficacité)**
1. **Identifier ce qui est écrit à `0xC83E`** → nomme l'axe X, donc la physique de la carte.
2. **Un log** de `C682`, `D904`, `C6A6`, `C6B8` sur un roulage : en comparant `C682` à `C6A6` on
   verrait immédiatement si ces cartes brident (si `C682 > C6A6` en permanence, elles ne servent à
   rien et il ne faut **pas** y toucher).
3. Suivre `C68A` et `C626` → nomme les deux modes.
