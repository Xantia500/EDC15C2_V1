# Étape 2 — Synchronisation, gap et phase : la machine d'état `byte_CA39`

*ECU 0 281 010 877 — EDC15C2 / C167CR‑4RM — image `edc.bin`*
*Adresses = EA du listing IDA (offset `.bin` = EA − 0x80000). Variables `0xC***`/`0xD***`/`0xF***` = adresses proches en page 3 (DPP3 = 3) → RAM externe à `0x30000 + adresse`.*

---

## 0. Comment j'ai cherché (pour que tu puisses refaire)

Quatre critères, dans cet ordre :

1. les **lecteurs de `byte_C2E9`** (l'index d'événement produit par la capture `CC6`) ;
2. les **variables d'état** (octets prenant des valeurs discrètes : `byte_CA39`, `byte_CA3A`, `byte_F70A`) ;
3. les **comparaisons 32 bits** (`cmpd1`, `sub`/`subc`) — seul moyen de comparer une période de dent ;
4. les **seuils lus dans des structures** (`mov rX, [rY+#n]` suivi d'un `cmp`).

Résultat : **il n'y a pas de détection « 2 dents manquantes »** au sens « période > 1,5 × période précédente ». Le gap est traité autrement — deux mécanismes distincts, décrits ci‑dessous.

---

## 1. La machine d'état de synchronisation — `sub_C736E` / `sub_C7398` (en `0xC736E`)

C'est le cœur de la synchro. L'état est dans **`byte_CA39`** :

| État | Signification déduite | Transition |
|---|---|---|
| **0** | attente d'activité du signal | → 1 si le temps écoulé depuis `word_C08C` atteint `[word_16F0+6]` (c'est un **timeout**, pas un comptage de dents) |
| **1** | première qualification | → 2 si `[word_16F0+0] ≥ word_C562`, sinon → 4 |
| **4** | qualification alternative | (retour vers 1/2 selon la mesure) |
| **2** | qualification avancée | → **8** si `[word_16F0+2] ≥ word_C562` **et** si l'appel OS `sub_CE9B4(r1 = word_16F2, r2 = 0x377F, r3 = 0x13A)` rend `r0.0 = 1` |
| **8** | **vilebrequin synchronisé** | → 0x20 quand les deux drapeaux `word_FDCC.0` et `word_FDCC.1` sont tous deux à 1 |
| **0x20** | **phase arbre à cames validée** | si le **byte de phase** `byte_CA3A` ≠ `byte_CA38` (mémorisé) → re‑validation par le même appel OS ; si l'appel échoue → **0x10** |
| **0x10** | **défaut de phase** | état « collé » : `loc_C73DC` sort immédiatement (`cmpb rl2,#10h / jmpa cc_Z, loc_C74F2`) |

Les deux extraits qui portent la logique :

```
loc_C73FE:                       ; état courant != 0x20
        jnb     word_FDCC.1, loc_C743E
        jnb     word_FDCC.0, loc_C743E
        movb    rl2, #20h
        movb    byte_CA39, rl2   ; ------> VILEBREQUIN + AAC SYNCHRONISÉS

loc_C74E6:                       ; fin de routine : publication de la phase
        mov     r4, word_16F0
        movb    rl1, [r4+#4]     ; octet de phase fourni par la structure
        movb    byte_CA3A, rl1
loc_C74F2:
        mov     r0, word_C416
        movb    rl1, byte_CA3A
        bmov    r0.9, r1.0       ; ------> bit 9 de word_C416 = PHASE
        mov     word_C416, r0
```

**`word_C416` bit 9 = le drapeau de phase** diffusé à tout le firmware (les tâches d'injection s'en servent pour choisir le cylindre en cours de compression). `byte_CA3A` = la phase courante ; `byte_CA38` = la phase mémorisée lors de la dernière validation.

> Autrement dit : la synchro « vilebrequin seul » (état 8) suffit pour tourner, mais le passage en **injection séquentielle** exige l'état 0x20, donc la **validation par l'arbre à cames**.

---

## 2. Le gap : pas de comptage de dents manquantes, un seuil de plausibilité

Le calcul de vitesse (voir §3) se termine par ceci — `loc_C7D0C`, dans `0xC7D0C` :

```
        mov     r0, MDL              ; valeur calculée (proportionnelle au régime)
        mov     word_C91A, r0        ; valeur BRUTE publiée
        cmp     r0, word_F8E4        ; <=== SEUIL
        jmpr    cc_SGE, loc_C7D34
        mov     r1, word_F8F4        ; en dessous du seuil :
        add     r1, r0
        shr     r1, #1               ;   moyenne (précédent + nouveau) / 2
        mov     word_C91C, r1        ;   -> valeur FILTRÉE
        ...
loc_C7D34:
        mov     word_C91C, r0        ; au dessus du seuil : on prend la valeur telle quelle
```

et les trois seuils sont rechargés au début de la tâche, depuis **une seule structure** (`loc_C7514`) :

```
        mov     r0, word_145A
        mov     r1, [r0+#0] ; mov word_F8E0, r1
        mov     r1, [r0+#2] ; mov word_F8E2, r1
        mov     r1, [r0+#4] ; mov word_F8E4, r1     ; <-- le seuil de plausibilité
```

**Conséquence directe sur le 60‑2 :** une dent manquante (ou les deux) produit une période ≈ 3 × la normale. La valeur calculée à partir de cette période tombe **sous** `word_F8E4` : elle est donc **écartée par filtrage** au lieu d'être utilisée. Le gap est donc **absorbé par un seuil**, pas identifié par un compteur de dents.

C'est une architecture différente de ce que l'on trouve sur d'autres calculateurs, et c'est important pour ta compréhension : **le firmware ne « compte » pas les dents manquantes, il rejette les mesures aberrantes.**

---

## 3. Le calcul de régime — et le « N périodes sommées » (les 4 par tour ?)

Bloc `loc_C7C42` → `loc_C7D40` (dans `0xC7C42`) :

```
        mov     r0, word_1702
        mov     r1, [r0+#2] ; mov MDL, r1      ; constante 32 bits (mot bas)
        mov     r1, [r0+#0] ; mov MDH, r1      ; constante 32 bits (mot haut)
        mov     r1, [r0+#4]                    ; facteur / limite
        ...
loc_C7CAC:
        shl     r2, #11
        shr     r1, #5
        add     r2, r1
        divlu   r2                             ; MDH:MDL / r2  -> quotient 32 bits
        mov     r0, MDL
        shr     r0, #5                         ; mise à l'échelle
```

et surtout, **ce qui est divisé** — la somme des N dernières périodes (`loc_C7C16`) :

```
loc_C7C16:
        movbz   r2, byte_F63E
        jmpr    cc_NZ, loc_C7C22
        mov     r0, word_F640                  ; N = 0 : une seule période
        jmpr    cc_UC, loc_C7C42
loc_C7C22:
        mov     r0, word_F640
        add     r0, word_F642                  ; + 1
        sub     r2, #2
        jmpr    cc_ULE, loc_C7C42
        add     r0, word_F644                  ; + 2
        sub     r2, #2
        jmpr    cc_ULE, loc_C7C42
        add     r0, word_F646                  ; + 3
        sub     r2, #2
        jmpr    cc_ULE, loc_C7C42
        add     r0, word_F648                  ; + 4
```

⟹ **`régime ≈ K32 / (somme de `byte_F63E` périodes d'événement)`**, K32 étant lu dans la structure `word_1702`.

C'est ici que se joue ton « **4 calculs par tour** » : si `byte_F63E` (= 1 + `word_F648`, calculé dans la couche ROM, §4) vaut **4**, alors la mesure de vitesse est faite sur **4 événements = un tour** pour un 4 cylindres — et on a bien **4 mesures par tour**, chacune propagée ensuite dans la grille de 16 slots de l'étape 1.

---

## 4. La couche bas niveau (segment ROM `0x80000`) — `sub_8F4CC`

C'est là que sont gérés les événements et **les compteurs d'événements** :

```
sub_8F4CC:
        movb    rl4, byte_F70A
        cmpb    rl4, #10h                  ; étape de séquence (posée par sub_8E2D4)
        jmpa    cc_NZ, loc_8F7BC
        ...
        mov     r4, word_F646              ; POINTEUR vers un tampon d'événements
        movb    rl3, [r4]
        movbz   r5, rl3
        and     r5, #0C0h                  ; champ de 2 bits  (<< 6)
        ashr    r5, #6
        movb    byte_F635, rl5
        ...
        and     r5, #3Fh                   ; champ de 6 bits
        jmpr    cc_NZ, loc_8F596
        movb    rl4, #1
        movb    word_F632, rl4
        subb    word_F648, ONES            ; décrémente le compteur de périodes
        ...
        movb    rl4, word_F648
        movb    byte_F63E, rl4             ; <-- N pour le calcul de régime (cf. §3)
```

* `word_F646` = **pointeur** vers un tampon d'octets **à champs de bits** (2 bits + 6 bits) : c'est le format compact dans lequel le noyau enregistre les événements de dent/secteur ;
* `word_F648` = compteur qui décroît jusqu'à 0 → **c'est lui qui fabrique `byte_F63E`** ;
* `byte_F70A` = variable d'étape, écrite par un setter unique `sub_8E2D4` (appelée depuis plusieurs endroits, dont `ROM:8FA6C`) ;
* `word_F690` = limite de compteur (`cmp r6, word_F690; jmpa cc_UGT`).

---

## 5. Conclusion de l'étape 2

| Question | Réponse |
|---|---|
| Où est la synchro vilebrequin ? | Machine d'état `byte_CA39` en `0xC736E`/`0xC7398`, état 8 |
| Où est la synchro de phase (AAC) ? | État 0x20 + `byte_CA3A` (phase) / `byte_CA38` (mémorisée), publiée dans `word_C416` bit 9 |
| Où est la détection du gap ? | **Nulle part sous forme de compteur** : c'est un **seuil de plausibilité** (`word_F8E4`, depuis `word_145A+4`) qui fait rejeter les périodes aberrantes |
| Où sont comptées les dents ? | Dans la couche ROM `sub_8F4CC`, via un **tampon à champs de bits** pointé par `word_F646`, et le compteur `word_F648` |
| Combien d'événements par mesure ? | `byte_F63E` (1 à 5 périodes sommées) — **la valeur à relever pour confirmer les 4 par tour** |

---

## 6. Ce qui bloque encore — et c'est toujours la même chose

**Tous** les paramètres qui décideraient de tout sont derrière des **pointeurs de la mémoire basse absente** :

| Pointeur | Ce qu'il fournit |
|---|---|
| `word_145A` | `F8E0`, `F8E2`, `F8E4` = seuils (dont celui du gap) |
| `word_16F0` | `+0`,`+2` seuils d'état, `+4` **octet de phase**, `+6` timeout |
| `word_16F2` | paramètre de l'appel OS de validation `sub_CE9B4` |
| `word_1702` | **constante 32 bits K** du calcul de régime + facteur |
| `word_1708` | `+0Ch` compteur de dents à ignorer, `+10h` valeur de repli |
| `word_170A` | paramètre de l'appel OS (`r2 = 0x2FE`) |
| `word_141E` | `+4` = **N (nombre d'unités par cycle)** — pilote la grille de 16 slots |

C'est maintenant sans ambiguïté : **la couche « mesure » de ton firmware est entièrement dans l'image, mais toute sa paramétrisation (nombre de dents, seuils, phase, constante de régime) est dans la mémoire basse** — celle qui contient aussi l'OS, la table de vecteurs et l'init des chip‑selects.

**Donc le prochain pas n'est plus une analyse, c'est une lecture** : dumper `0x00000`–`0x07FFF` (moitié basse de la flash 1 Mo, ou second circuit). Dès qu'on l'a, je peux :
1. résoudre les 8 pointeurs ci‑dessus et donner **les valeurs réelles** (dents, seuils, K, phase) ;
2. vérifier `byte_F63E` = 4 → « 4 calculs par tour » confirmé ;
3. terminer la chaîne jusqu'aux variables d'injection.

---

*Étapes 1 et 2 terminées. La suite logique : soit tu obtiens la mémoire basse, soit on continue sur la chaîne aval (comment `word_C416` bit 9 et les valeurs filtrées arrivent aux sorties d'injection) — dis‑moi laquelle des deux.*
