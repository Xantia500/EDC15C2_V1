# Étape 5 — Le mot d'état `word_C632`, la seconde mesure, et l'origine de l'autocontrôle

*ECU 0 281 010 877 — EDC15C2 / C167CR-4RM — image `edc.bin`*
*EA = adresse du listing IDA (offset `.bin` = EA − 0x80000). **[constat]** = visible dans le binaire ; **[hypothèse]** = interprétation.*

---

## 1. `word_C632` — le mot d'état qui garde le régulateur, et la boucle se referme

**[constat]** `word_C632` est écrit **une seule fois** (ligne 178765, dans `sub_AFAA0`) et lu **11 fois** — **toutes** dans `sub_B35B6` (EA `0xB35B6`).

### 1.1 Ce que chaque bit déclenche

| Bit | Effet observé dans `sub_B35B6` |
|---|---|
| `0400h` | **autorise la voie de régulation P/I** : sans lui, toute la branche de calcul `unk_1F18` → `word_1DA8` → `unk_20AC` est court-circuitée |
| `0800h` | **gèle l'intégrateur** : `word_DA14` n'est plus décrémenté, et `word_DA1C = 0800h` (recopié) |
| `1000h` | **régime hors fenêtre** → force `word_DA26 = 1000h` et court-circuite la régulation |
| `2000h` | **phase non valide** → force `word_DA30 = word_1B7E` (valeur de repli) |

Rappel de l'étape 3 §4.1 : le bit `1000h` est précisément celui que `sub_AFAA0` pose quand `word_C91C` sort de `[word_1432+12h, +14h]`, et le bit `2000h` celui qu'il pose quand `byte_C2DE` (la phase) vaut 0. **La chaîne est donc cohérente de bout en bout** : la mesure de régime et la phase pilotent l'état, qui pilote le régulateur.

### 1.2 Le régulateur (EA `0xB5AC6` → `0xB5DE8`)

**[constat]** écart, puis deux voies :

```
loc_B5C08:
        mov  r4, word_C6C8
        sub  r4, word_C91C        ; écart = CONSIGNE - RÉGIME MESURÉ
        mov  [r0], r4
        mov  r5, word_C632
        and  r5, #400h            ; régulation autorisée ?
        jmpr cc_Z, loc_B5C8C      ; sinon -> tout à zéro
```

Voie P/D (si `0400h`) :
```
        calls 0, unk_1F18         ; lecture de courbe (r12,r13 = structure, r14 = régime)
        calls 0, word_1DA8        ; évaluation -> r4
        r7 = word_1432[1Eh] + r4  ; offset de calibration, saturé 7FFF/8000
        calls 0, unk_20AC         ; pondération avec word_1432[20h]
        -> word_DA1E
```

Voie I (intégrateur) :
```
loc_B5B9C:
        r5 = -word_DA1E
        word_DA14 = word_DA14 + r5          ; intégration
        saturation 7FFF / 8000
loc_B5CDA:
        borne haute = word_1432[16h]        ; anti-emballement
loc_B5CFC:
        borne basse = word_C690
        word_DA14 = max(word_DA14, word_C690)
        word_C658 = word_DA14               ; <- terme I publié
```

### 1.3 La sortie — et c'est là que la boucle se referme

```
loc_B5D10:
        r9 = word_C65A + word_DA14          ; (terme correcteur) + (terme intégral)
        saturation [0, word_1432[16h]]
        r9 = r9 - word_DA1E                 ; re-saturation
        word_D404 = r9                      ; <-- COMMANDE
        ...
        word_C69C = r6
        word_C69E = r9                      ; <-- COMMANDE (forme finale)
```

**[constat]** `word_C69E` n'est pas un état interne : il est **ajouté à la quantité d'injection de base** en deux endroits :

```
loc_975D0 (EA 0x975D0):
        mov r4, word_C6BA
        add r4, word_C69E                   ; quantité de base + correction
        cmp r4, [word_1438+0Ah]
        ...
loc_ACFC6 (EA 0xACFC6):
        mov r4, word_C6BA
        add r4, word_C69E
        mov word_D844, r4                   ; -> quantité d'injection finale
        mov word_D304, r4
```

et `word_C6BA` est elle-même limitée puis convertie :

```
loc_B33C2 (EA 0xB33C2):
        word_C6BA = word_D9A6               ; quantité de base après limitation
loc_B0780 (EA 0xB0780):
        calls 0Bh, sub_B33DC                ; conversion quantité -> durée
        mov word_C6B0, r4
```

> ⚠️ **CORRIGÉ À L'ÉTAPE 6 (§0.2.c)** : `sub_B33DC` n'est pas une conversion quantité→durée mais un **limiteur** (`min(r12, word_C692)`, avec valeur de substitution `word_C5AC` moteur arrêté). `word_C6B0` n'est donc **pas une durée** : c'est la quantité écrêtée. Voir `ETAPE6_verification_et_blocs.md`.
>
> ~~**`word_C6B0` = la durée d'injection**, et c'est elle qui borne l'intégrateur~~ (`loc_B5BB0` : `[word_DA28] − word_C6B0` comparé à `word_DA14`).

### 1.4 Réponse

**La boucle complète est établie :**

```
word_C91C (régime mesuré)  ─┐
                            ├─► écart = word_C6C8 (consigne) − word_C91C
word_C632 (état)  ──────────┤
   bit 400h : régulation    │        régulateur  sub_B35B6 (EA 0xB35B6)
   bit 800h : intégrateur   │            ↓
   bit 1000h: hors fenêtre  │        word_C69E / word_C69C   (correction)
   bit 2000h: phase invalide┘            ↓
                              quantité = word_C6BA + word_C69E  -> word_D844 / word_D304
                                        ↓
                              sub_B33DC : quantité -> DURÉE  -> word_C6B0
                                        ↓
                              [ouverture d'injecteur : hors image]
```

**[constat]** accessoirement, `sub_BDB22` (appelée juste après) matérialise un **bloc de mesure pour le diagnostic** : à partir du descripteur `word_BD00` (bit `0100h` = autorisation, octet bas = nombre d'entrées, puis une liste de pointeurs à `0xBD02…`), elle recopie jusqu'à **28 octets** dans **`0xDF00 + k`** (`byte[0xDF00+k] = byte[*ptr]`). C'est ce que lit le testeur par la ligne K.

---

## 2. `word_1674` — la source 32 bits de la seconde mesure

**[constat]** `word_1674` (adresse `0x1674`, donc **pointeur de la mémoire basse**) est lu **3 fois**, et **toujours selon le même motif** :

```
mov r4, word_1674
mov r13, [r4]        ; mot bas
mov r14, [r4+#2]     ; mot haut      => valeur 32 bits
calls 0, unk_XXXX    ; service OS
```

| Site | Service | Sortie | Saturation |
|---|---|---|---|
| `sub_9B2B2` (EA `0x9B2B2`, ligne 140316) | `unk_2172` — `r12` = **adresse de destination** | **`word_C562`** | `[0, 0xFFFE]` |
| `sub_9C56A` (ligne 142752) | `unk_2196` | `word_C3FA` | `[0, 0x7FFF]` |
| `sub_9C76A` (ligne 142971) | `unk_2196` | `word_C3FA` | `[0, 0x7FFF]` |

Le motif complet (ligne 142971) montre aussi le **repli** et le **drapeau de validité** :

```
loc_9C86C:
        mov  r12, r0
        mov  r4, word_1674
        mov  r13, [r4] ; mov r14, [r4+#2]
        calls 0, unk_2196
        ...
        mov  word_C3FA, r4         ; valeur convertie, bornée à 7FFF
        movb rl4, #1
        orb  byte_C23E, rl4        ; drapeau « mesure valide »
```
et le chemin d'échec, en amont :
```
loc_9C666:
        jnb  USR0, loc_9C680
        mov  r4, word_1470
        mov  r5, [r4+#6]           ; <-- VALEUR DE REPLI de calibration
        mov  word_C3FA, r5
        andb byte_C23E, #0FEh      ; drapeau « mesure invalide »
```

### Réponse

> **`word_1674` est un pointeur de la mémoire basse vers une valeur 32 bits.** Cette valeur unique alimente **deux conversions différentes** par deux services OS, avec deux saturations différentes :
> * `unk_2172` → **`word_C562`** (le « régime système », saturé `0xFFFE`) — c'est celui que lit la machine d'état de synchro (`word_16F0[0]/[2]`) et les huit seuils de `word_1432` ;
> * `unk_2196` → **`word_C3FA`** (grandeur 15 bits saturée `0x7FFF`) — avec repli sur `word_1470[6]` et drapeau de validité dans `byte_C23E` bit 0.
>
> **[hypothèse]** une valeur 32 bits convertie deux fois avec deux échelles différentes est typiquement **un temps** : une durée → une vitesse (`C562`, échelle large) et une durée → une grandeur normalisée (`C3FA`, 15 bits). Le candidat le plus probable est la **période de la mesure OS**, dont `C562 = K/période` redonne le régime système.

---

## 3. L'origine de l'autocontrôle : deux vecteurs d'interruption

### 3.1 Où sont les appelants

**[constat]** `sub_94428` et `sub_94446` ne sont appelés que depuis **deux emplacements**, EA `0x9403E` et EA `0x9408E` — soit **0x50 octets d'écart**, dans la zone `0x94000` qui commence par `word_94000: dw 0AAAAh` : **la table de vecteurs d'interruption de ce calculateur**.

Les deux stubs sont identiques, au sous-programme appelé près :

```
        bset   IEN
        scxt   MDC, #0
        scxt   DPP0, word_C1DA        ; restauration du contexte de page
        scxt   DPP2, word_C1DC
        push   MDL
        push   MDH
        scxt   CP, #0F6E6h            ; pile locale
        nop
        mov    r4, word_C1B0
        sub    r4, #126h
        mov    r5, CP
        mov    [r5], r4               ; ajustement de l'adresse de retour (OS)
        mov    r1, word_C1F6
        push   r1
        mov    r4, #13h
        mov    word_C1F6, r4          ; niveau / identifiant de tâche = 13h
        calls  9, sub_94428           ; (ou sub_94446)
        pop    r1
        mov    word_C1F6, r1
        ...
        atomic #2
        bclr   IEN
        reti
```

**Après le second stub** vient un troisième gestionnaire qui lit `GPT12E_T4` et `word_F7AA` — donc l'ordre des vecteurs est `… / CAPCOM2 / CAPCOM2 / T4 …`.

### 3.2 L'articulation des deux

| Routine | Rôle |
|---|---|
| `sub_94428` | (`IRQ-1`) `PECC1 = 0328h`, `word_FCE6 = 0F7B6h`, `byte_F7EB = 1`, `bclr IE` — **réarme le transfert PEC et coupe l'interruption** |
| `sub_94446` | (`IRQ-2`) l'automate : lit `word_F7E6`, avance `byte_F7E5`, compile le motif `byte_F602`, réarme `PECC1 = nb_mots \| 400h` et relance `T8R` |

> **Le mécanisme est donc entièrement piloté par interruption** : le compteur du canal PEC1 s'épuise → l'interruption associée est levée → `sub_94446` fabrique la trame suivante → `sub_94428` réarme. C'est un **générateur de séquence autonome**, pas un calcul de tâche de fond.

### 3.3 Un point d'ombre à noter honnêtement

**[constat]** les valeurs écrites dans `PECC1` sont `0328h` et `nb_mots \| 0400h`. Dans la description générique du PEC (UM §5.2, p. 5‑12), le registre `PECCx` se limite à `COUNT` (bits 7…0), `BWT` (bit 13) et `INC` (bits 15…14) ; les **bits 8 à 12 sont déclarés réservés**. Or le firmware y met `1` (bits 9 et 10).

**[hypothèse]** les canaux PEC associés à CAPCOM utilisent un **format de contrôle différent** de celui des canaux standards, non documenté dans les pages que j'ai pu extraire du manuel. C'est cohérent avec le fait que `sub_94428` et `sub_94446` ne manipulent que `CC`/`T8`, jamais un périphérique série. **À vérifier au chapitre « CAPCOM » du manuel** (la figure du `PECCx` en mode capture/compare). Ce n'est pas bloquant : le comportement observable (compteur + relance) est établi.

---

## 4. Synthèse — la chaîne complète, de la dent au débit

```
 P2.6 ──capture CC6──► CC1_CC6 ──PEC5──► 0F8DEh
                                            │
         bibliothèque de mesure (0x8xxxx) : sub_8F4CC / sub_8F7C0 / sub_8FA1A
         · delta de capture, tampon à champs de bits, sub_8FF62 (courbes)
         · écrit l'enregistrement de mesure 0xF622 (12 octets)
                                            │
         instantanés atomiques : 0xF63E (vitesse) · 0xF64E (normalisation) · 0xF65A (valeur 32 bits)
                                            │
   ┌────────────────────────────────────────┴──────────────────────────────────┐
   │ fenêtre K/période (word_1708[2],[4])   → rejet du gap                     │
   │ timeout K×période (word_1708[0Eh])     → DTC 2FEh                         │
   │ K32 / Σ (word_1702)                    → word_C91A → word_C91C (régime)   │
   └────────────────────────────────────────┬──────────────────────────────────┘
                                            │
         automatismes de synchro (byte_CA39) : état 8 = vilebrequin
         état 20h + byte_CA3A (phase AAC) → word_C416 bit 9 → byte_C2DE
                                            │
         sub_AFAA0 : construit le MOT D'ÉTAT  ──►  word_C632
         (régime hors fenêtre = bit 1000h, phase invalide = bit 2000h)
                                            │
         sub_B35B6 : écart word_C6C8 − word_C91C → régulateur P/I
                     ──► word_C69E / word_C69C
                                            │
         quantité = word_C6BA + word_C69E ──► word_D844 / word_D304
                                            │
         sub_B33DC : quantité → DURÉE ──► word_C6B0
                                            │
         ┌──────────────────────────────────┴─────────────────────────────────┐
         │   [ÉTAGE DE SORTIE — ABSENT DE CETTE MOITIÉ DE FLASH]              │
         │   format attendu : paire double-registre CCx (mode 101b = bascule) │
         │                    / CCz (mode 100b), chargée par PEC              │
         └────────────────────────────────────────────────────────────────────┘
```

---

## 5. Trois nouvelles pistes ouvertes (toutes dans l'image)

1. **`word_BD00` → `0xDF00` : le bloc de mesure du diagnostic.** `sub_BDB22` publie jusqu'à 28 octets sélectionnés par une liste de pointeurs. C'est **exactement** ce que lit un testeur K‑line : la correspondance entre les 28 entrées et les grandeurs physiques peut être reconstituée en remontant les pointeurs écrits dans `0xBD02…`.
2. **`word_147E`, `word_1438`, `word_1434`** — trois autres structures de calibration croisées dans cette étape (`[word_147E+0/2/8/0Ah]` = bornes de quantité, `[word_1438+0Ah/10h/12h]` = bornes de débit, `word_1434` = masques de bits d'autorisation). Le même travail qu'à l'étape 4 sur `word_1432` est faisable.
3. **`word_C690`, `word_C6C8`** : `word_C690` sert de borne basse de l'intégrateur *et* de plancher de la commande ; `word_C6C8` est la **consigne de régime**. Savoir qui écrit `word_C6C8` donnerait le régulateur de ralenti complet.

---

*Livrables cumulés : `ENQUETE_capteur_regime_60-2.md`, `ETAPE1…ETAPE5`, `taches_jeton_CC27.csv`, `outils/ctx.py`.*
