# ÉTAPE 110 — Le rapport et le régulateur : où se trouve vraiment la condition « 3e ou 4e »

**Résultat central : il n'existe AUCUN test `cmp #3` / `cmp #4` dans la tâche régulateur.**
La condition est un **seuil de ratio**, un seul mot de calibration : `[0xE2792] = 768`.

---

## 1. Le verrou : un seuil sur le ratio (l.184704-184709)

```asm
184704  mov  r4, word_14B0        ; bloc 0xE2788
184705  mov  r5, [r4+#0Ah]        ; ★ r5 = 768
184706  cmp  r5, word_C93E        ; ★★ comparé au RATIO (V×256/N filtré)
184707  jmpr cc_SLE, loc_B413E    ; si 768 <= ratio -> on continue
184708  movb rl4, #89h
184709  movb byte_D9B3, rl4       ; ★★★ sinon : refus, motif 0x89
```

`word_C93E` est exactement la valeur de l'Étape 109 (`C576` filtré). Donc :

> **Le régulateur exige `ratio ≥ 768`, c'est-à-dire `V/N ≥ 3,00 km/h pour 1000 tr/min`.**

Comme `V/N` est **constant par rapport engagé**, ce test **EST** la condition de rapport —
mais exprimée en dynamique, pas en numéro de vitesse.

## 2. Les six portes du régulateur, dans le même bloc `0xE2788`

`word_14B0 → 0xE2788` : `2500 · 25000 · 1000 · 4500 · 2560 · 768 · 4000 · 1000`

| seuil | valeur | comparé à | signification | refus |
|---|---|---|---|---|
| `+0x00` | **2500** | `C562` | **vitesse min 25,00 km/h** | `0x86` |
| `+0x02` | **25000** | `C562` | **vitesse max 250,00 km/h** | `0x86` |
| `+0x06` | **1000** | `C91C` | **régime min 1000 tr/min** | `0x87` |
| `+0x04` | **4500** | `C91C` | **régime max 4500 tr/min** | `0x88` |
| `+0x0A` | **768** | `C93E` | ★ **rapport min** | `0x89` |
| `+0x08` | **2560** | `D9E0` (écart filtré) | dérive vitesse/rampe | `0x8A` |

*(bonus : `0xE278A = 25000` est bien une limite de vitesse **250 km/h** — c'est le plafond du
régulateur, ce qui explique pourquoi l'Étape 105 ne trouvait pas de Vmax « véhicule ».)*

## 3. Le rapport intervient aussi comme **bit d'autorisation** — `C330 & 0x10`

Deux fonctions d'autorisation testent le **bit 4 de `byte_C330`** :

```asm
; sub_A7C5A (l.163016)
163016  movb rl4, byte_C2C0
163017  cmpb rl4, #1
163018  jmpr cc_Z, loc_A7CA8     ; ★ codage « sans info rapport » -> BYPASS
163019  movb rl2, byte_C330
163020  andb rl2, #10h
163021  jmpr cc_Z, loc_A7D38     ; bit 0x10 absent -> refus

; sub_A7D48 (l.163142) — même logique, sortie inverse
163145  movb rl5, byte_C330
163146  andb rl5, #10h
163147  jmpr cc_NZ, loc_A7D92    ; bit 0x10 présent -> autorisé (retourne 1)
```

**Origine du bit `0x10`** : il est fabriqué dans la tâche rapport (seg015), conditionné par
l'état `byte_D8CC == 2` :

```asm
178513  movb rl4, byte_D8CC
178514  cmpb rl4, #2
178515  jmpr cc_NZ, loc_B0452
178516  movb rl3, [r0]
178517  orb  rl3, #10h           ; ★ bit d'autorisation
178518  movb [r0], rl3
```

`D8CC` est une **machine à 2 états avec hystérésis** (l.178398-178418) comparant
`[0xE1236 + 6] (= 200) + word_C6C8` à `word_D8CA = courbe(handle 0x1A98 → 0xE7FF4, régime C91C)`.
`C6C8` étant une valeur de type **régime** (comparée à `C91C` l.187308), cet état représente le
**décollage / rapport établi**, pas un numéro de vitesse.

## 4. Deuxième veto : les codes de rapport « indéterminé »

```asm
184425  movbz r4, byte_C330
184426  and   r4, #0Fh
184427  cmp   r4, #0Bh
184428  jmpr  cc_Z, loc_B3E6C
184431  cmp   r4, #0Ch
184432  jmpr  cc_NZ, loc_B3E78
184434  loc_B3E6C:
184435  movb  rl4, #92h
184436  movb  byte_D9B3, rl4      ; ★ refus 0x92
184437  mov   word_C698, ZEROS    ; ★ et PID remis à zéro
```

⇒ si le rapport devient indéterminé (`0x0B`/`0x0C`), la régulation ne se contente pas de refuser :
elle **coupe** (consigne PID `C698 = 0`).

## 5. Le code `0x0B` de la table des fenêtres — explication probable

Rappel Étape 109 : les 6 fenêtres `0xE81A4` portent les codes `01 · 0B · 02 · 03 · 04 · 05`.
Maintenant qu'on sait que `0x0B` est un **code de refus** côté régulateur, la lecture devient
cohérente : la fenêtre `234-338` (2e) est **volontairement marquée « rapport indéterminé »**.
⇒ **on ne peut pas réguler en 2e, même en baissant le seuil 768.** Pour autoriser la 2e il faudrait
aussi changer ce code — ce qui est un autre chantier.

---

## 6. Conséquence pratique : autoriser la 3e

| rapport | bande de ratio (Étape 109) | `768` actuel | seuil à mettre pour l'autoriser |
|---|---|---|---|
| 3e | **338 → 559** | refusé | **≤ 338**, p. ex. `320` (`0x0140`) |
| 2e | 234 → 338 | refusé | ≤ 234 — **mais code `0x0B` bloque encore** |
| 4e | 559 → 826 | accepté | — |

- Octet à modifier : **`0xE2792`** (word, LoHi) : `00 03` → p. ex. `40 01` (320).
- Vérifier **aussi** la copie éventuelle du bloc et **recalculer les checksums** (Étape 105).
- Effet secondaire à surveiller : le critère est dynamique, donc en 3e à très bas régime le ratio
  peut descendre sous le seuil et faire **couper** la régulation (0x89) — c'est normal et sans
  danger, mais cela crée des cycles si le seuil est trop haut.

## 7. Réponse synthétique à « 3 ou 4 ? »

- **Ce n'est pas « 3 ou 4 »** : c'est **« ratio ≥ 768 »**, un seuil unique, sans borne haute.
- Sur l'échelle des fenêtres, `768` tombe **dans la bande de 4e** (`559-826`) ⇒ en pratique :
  **4e et 5e autorisées, 3e refusée**. D'où le blocage en ville ressenti.
- La contrainte passe par **deux** mécanismes distincts et complémentaires :
  **`0xE2792 = 768`** (seuil de ratio, refus `0x89`) et **bit `0x10` de `C330`**
  (autorisation générique, bypassée si codage `C2C0 == 1`).
