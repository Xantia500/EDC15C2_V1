# ÉTAPE 108 — Les deux cartes *driver's wish*, leur sélection par le **rapport**, et l'entrée de la boucle IQ

> **Correction préalable** : `0281010877` = **2.2 HDi full-mux 3 broches** ; `0281010597` =
> semi-mux intermédiaire 2.2 HDi 4HX. Un 2.0 HDi peut tourner sur ces calculateurs avec le software
> adapté. Le dump étudié est donc bien un **2.2 HDi full-mux**.

---

## 1. Les deux cartes, en clair

Axes **identiques** : `tagY = 0xC42E` (**régime**) × `tagX = 0xC6DA` (**pédale**), 8 × 6.

| | axe Y (régime) | axe X (pédale) |
|---|---|---|
| valeurs | 0 · 600 · 750 · 1000 · 1300 · 1750 · 2250 · 5000 | **118** · 2000 · 4000 · 6000 · 8000 · 10000 |

★ La pédale est bien codée **0-10000** (0-100 %), mais l'axe commence à **118 = 1,18 %** — la
position de repos n'est pas 0.

### Carte `word_1B66` → `0xE8B50`

```
y=   0 : 1060 3372 5660 7260 8000 8000
y= 600 :  460 2608 4928 6768 8000 8000
y= 750 :  320 2400 4688 6684 8000 8000
y=1000 :  140 2132 4444 6408 8000 8000
y=1300 :    0 1844 4104 6064 8000 8000
y=1750 :    0 1520 3616 5606 7660 8000
y=2250 :    0 1260 3208 5180 7180 8000
y=5000 :    0  680 1846 3656 5740 8000
```

### Carte `word_1B68` → `0xE8BD4`

```
y=   0 : 1060 3372 5660 7260 8000 8000      ← identique
y= 600 :  460 2608 4928 6768 8000 8000      ← identique
y= 750 :  320 2350 4688 6684 8000 8000      ← 2400 -> 2350
y=1000 :  140 1782 4444 6408 8000 8000      ← 2132 -> 1782
y=1300 :    0 1344 4104 6064 8000 8000      ← 1844 -> 1344
y=1750 :    0 1070 3616 5606 7660 8000      ← 1520 -> 1070
y=2250 :    0  910 3208 5180 7180 8000      ← 1260 ->  910
y=5000 :    0  680 1846 3656 5740 8000      ← identique
```

**Les deux cartes ne diffèrent que sur une seule colonne** : `pédale = 2000` (20 %), et uniquement
aux régimes 750-2250 tr/min. Partout ailleurs elles sont **strictement égales**. Ce n'est donc pas
une carto « éco/sport » globale : c'est un **correctif local de basse charge**.

---

## 2. ★★★ Qui choisit la carte : le **RAPPORT**

```asm
sub_B56F8:                          ; CODE XREF: seg015:ABE0↓P
mov  r4, word_C576
mov  word_C93E, r4                  ; ★ C93E = C576 (le rapport, recopié tel quel)
mov  r5, word_1B6A
mov  r2, [r5]                       ; ★ [0xE8C58] = 539
cmp  r2, word_C93E
jmpr cc_SLE, loc_B5722              ; si 539 <= rapport
mov  r12, word_1B68                 ;   -> carte 0xE8BD4 (valeurs basses)
calls 0, unk_1D50
loc_B5722:
mov  r12, word_1B66                 ; ─► carte 0xE8B50 (valeurs hautes)
calls 0, unk_1D50
```

### Le seuil `539`, lu sur l'échelle des `Gangstufen`

Les fenêtres de `0xE81A4` (Étape 99) sont `<202 / 234-338 / 338-559 / 559-826 / 826-1116 / 1116-2560`.
**`539` tombe dans la fenêtre `338-559`, c'est-à-dire la 3e.**

⇒ **rapport < 539 (1re et 2de) → carte `0xE8BD4` (moins de débit)**
⇒ **rapport ≥ 539 (3e et au-delà) → carte `0xE8B50` (débit normal)**

### ⚠⚠ Voilà la « limitation de couple en 1re/2de »

Elle n'est **pas** dans la chaîne `word_D1B6 → D1C0` (Étape 104, inerte) : elle est dans la
**sélection de la carte driver's wish par le rapport**, et elle est **ACTIVE** — le sélecteur lit
`word_C576` en direct, sans aucun drapeau de neutralisation.

**Errata E22** : la limitation par rapport **existe et fonctionne** ; c'est seulement son
implémentation « limiteur de débit » (`D1B0-D1C4`) qui est une trace. La vraie limitation passe par
la carto souhait.

---

## 3. Ce qui est produit : `word_C6A6` = IQ souhaitée

```asm
loc_BABD8:                          ; l.195500
mov  r12, word_C91C                 ; ★ Y = régime (copie de C42E)
mov  r13, word_C952                 ; ★ X = pédale filtrée
calls 0Bh, sub_B56F8
mov  word_C6A6, r4                  ; ★★★ C6A6 = IQ SOUHAITÉE
...
mov  r4, word_C952
mov  word_C6DA, r4                  ; ★ C6DA = la pédale (l'axe de la carte)
mov  r4, word_DB38
mov  word_C6D8, r4
```

Échelle : `8000` ⇒ **80,00** (0,01 mm³/coup). Le maximum physique du Datensatz est `C596 = 120`
(120 mm³, bloc `word_1878[+4] = 0xE4C0A`), donc la carte souhait **plafonne à 2/3 du débit max**.

---

## 4. La suite de la chaîne IQ — trois consommateurs identifiés

### (a) `seg014:ACAA4` — gradient cycle à cycle et détection de demande

```asm
171717  mov  r4, word_C576
171718  mov  word_C93E, r4          ; le rapport recopié ici aussi
171719  mov  r5, word_C6A6
171720  sub  r5, word_D834
171722  mov  word_D2F4, r5          ; ★ ΔIQ = C6A6 - IQ(cycle précédent)
171724  mov  word_D834, r2          ; mémoire du cycle
171732  mov  r1, word_19C6          ; ★ bloc 0xE6C06
171733  mov  r2, [r1+#2]            ;   = 1500
171734  cmp  r2, word_C6A6
171736  mov  r8, #1                 ;   drapeau « forte demande »
171737  movb rl6, #2
171742  cmp  [r0+#8], [+4]          ;   ΔIQ vs seuil
171745  mov  r7, #1
```

`word_19C6 → 0xE6C06` : `650 · 1500 · 0 · 0 · 0 · tag 0xC42E · 8 · 1000`
⇒ seuil d'IQ **1500** (15 mm³) pour la détection de demande, seuil de gradient **0** (désactivé).

### (b) `seg015:B447C` — **le régulateur remplacé par la pédale, sauf dépassement**

```asm
185007  mov  r4, word_C6A6          ; IQ demandée par la PÉDALE
185008  cmp  r4, word_C698          ; IQ demandée par le RÉGULATEUR
185009  jmpr cc_SLE, loc_B447C
185010  mov  r4, word_D9E2
185011  mov  r5, word_D9E4
185012  mov  word_D9B6, r4          ; ★ bascule de consigne
185014  movb rl4, #10h
185015  orb  byte_D9D0, rl4
185016  bset word_FD18.4            ; ★★ drapeau « pédale prioritaire »
```

★★ **C'est exactement le comportement que tu décrivais** : le régulateur impose sa consigne
(`word_C698`, issue du PID `unk_1F98(word_14C0, D9E6, C562, D9CE)` à l.185821), mais **si la pédale
demande plus, il lâche** (`FD18.4`) — « cartes inversées remplaçant la pédale, sauf dépassement ».

Bornes du régulateur : `D9E6 = +word_C690`, `D9E8 = −word_C690` (l.185814-185818), puis
`C698` clampé entre 0 et `word_C690` (l.185829-185838).

### (c) `seg014:CAAC` / `CABC` — les autres lecteurs

`C6A6` est encore lu à l.171734 (seuil), 182735/182752 (zone FGR) et 185007. La valeur finale
injectée n'est pas `C6A6` directement : elle passe par l'arbitre de débit de l'Étape 104
(`word_18B2`, `byte_C308`, `C596`) — **prochaine étape logique**.

---

## 5. Schéma de la boucle, désormais continu

```
pédale brute ──► C952 (filtre) ──► C6DA
régime C42E ──► C91C
                  │
                  ▼
        sub_B56F8  ← seuil 0xE8C58 = 539 comparé au RAPPORT C576
           │  ratio < 539 (1re/2de) → 0xE8BD4
           │  ratio ≥ 539 (3e+)     → 0xE8B50
           ▼
        C6A6 = IQ souhaitée  (0…8000 = 0…80 mm³)
           │
           ├─► D2F4 = ΔIQ  ──► seuils 0xE6C06 (1500 / 0) ──► drapeaux de demande
           │
           ├─► arbitrage FGR : C698 vs C6A6 ──► FD18.4 si la pédale dépasse
           │
           ▼
        arbitre de débit (word_18B2, byte_C308, C596 = 120) ──► IQ finale
```

## 6. Errata
- **E22** : la limitation par rapport **est active** — via la sélection de la carte souhait
  (`0xE8C58 = 539` sur `word_C576`). L'Étape 104 avait conclu « neutralisée » sur la seule chaîne
  `D1B6/D1C0`, qui n'est effectivement qu'une trace : les deux constats coexistent.
- **E23** : `tagY` des cartes souhait = `C42E` (régime) et `tagX = C6DA` (pédale) ; l'axe pédale
  démarre à **118**, pas à 0.
