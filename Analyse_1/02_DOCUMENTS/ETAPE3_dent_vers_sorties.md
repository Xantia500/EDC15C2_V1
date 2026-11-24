# Étape 3 — De la dent à la sortie : entrées, statut, phase et étage CAPCOM

*ECU 0 281 010 877 — EDC15C2 / C167CR-4RM — image `edc.bin`*
*EA = adresse du listing IDA (offset `.bin` = EA − 0x80000). Toute affirmation est marquée **[constat]** (visible dans le binaire) ou **[hypothèse]**.*

---

## 0. Erratum important sur l'étape 2

À l'étape 2 j'ai écrit : « **le gap n'est pas détecté, il est rejeté par un seuil** ». C'est **incomplet**. En creusant la tâche de mesure j'ai trouvé le mécanisme réel, et il est bien plus élégant :

**Il y a trois niveaux de protection, et le gap est traité au niveau 1 — événement par événement.** Le seuil de l'étape 2 (`word_F8E4`) n'est que le troisième filet.

| Niveau | Où | Ce qui est comparé | Ce que ça fait du gap |
|---|---|---|---|
| **1. fenêtre par événement** | `loc_C7AD0` (EA `0xC7AD0`) | `K / période` vs `[word_1708+2]` et `[word_1708+4]` | la période **anormale est rejetée** : elle ne met pas à jour la référence 32 bits |
| **2. timeout de cycle** | `loc_C7B4A` (EA `0xC7B4A`) | `word_C08E − word_F91C` vs `word_F8F8` = `word_F900 × word_1708[0Eh] / 10000` (min. 2) | si aucun événement dans **K × la dernière période** → perte de signal + **DTC** |
| **3. seuil de vitesse** | `loc_C7D0C` (EA `0xC7D0C`) | vitesse vs `word_F8E4` | en dessous → moyenne au lieu de publication |

Le niveau 2 est le vrai détecteur de « dents manquantes » : le seuil est **proportionnel à la dernière période connue**, avec un facteur de configuration `word_1708[0Eh]` (format ×10000, donc 30000 ⇒ 3,0×). Le gap produit une période ≈ 3× → **franchissement du timeout** si le facteur est < 3, ou **rejet par la fenêtre** si le facteur est plus grand. Les deux branches existent, c'est la calibration qui choisit. **[constat pour la structure, hypothèse pour la valeur]**

---

## 1. Le vocabulaire matériel : les modes CAPCOM (source : UM V3.2 ch. 15)

Le firmware écrit dans `CC1_M0..M3` (= `CCM0..CCM3`, SFR `FF52h`…`FF58h`). Chaque nibble = un canal : **CCMODx = bits 2..0**, **ACCx = bit 3**.

| Valeur du nibble | Signification (UM tab. ch. 15) |
|---|---|
| `0` | aucune fonction (état de reset) |
| `1` (`CCMOD=001`) | **capture, front montant** |
| `3` (`CCMOD=011`) | **capture, les deux fronts** |
| `4` (`CCMOD=100`) | **compare mode 0** : interruption seule, broche non touchée |
| `5` (`CCMOD=101`) | **compare mode 1** : la broche **bascule** à chaque comparaison |
| `6` (`CCMOD=110`) | compare mode 2 : une interruption par période de timer |
| `7` (`CCMOD=111`) | compare mode 3 : broche mise à 1, remise à 0 au débordement du timer |
| `+8` (`ACC=1`) | même mode, alloué à **T1** au lieu de T0 |

**Et surtout — le mode double-registre** (UM §15, « Double-register Compare Mode ») :
> si un registre de banque 1 (`CC0…CC7`) est en **compare mode 1** et son homologue de banque 2 (`CC8…CC15`) en **compare mode 0**, les **deux** valeurs de comparaison pilotent **la même broche** `CCxIO`, qui bascule à chaque match.

C'est **le** mécanisme qui permet une impulsion d'injection sans aucune intervention du CPU : `CC0 = valeur d'ouverture`, `CC8 = valeur de fermeture`, la broche P2.0 fait le reste. Aucune interruption, aucun jitter logiciel.

---

## 2. Occupation réelle de CAPCOM1 dans cette image  **[constat]**

Toutes les écritures de `CC1_M0..M3` de l'image, avec leur EA :

| EA | Instruction | Effet |
|---|---|---|
| `0x8874E+` | `bfldl CC1_M0,#0Fh,#4` puis `mov CC1_M0,#4444h` | **CC0…CC3 → compare mode 0** (T0) |
| `0x8D474+` | `mov CC1_M1,#444Ch` | CC4 → compare mode 0 + **ACC=1 (T1)** ; CC5/6/7 → compare mode 0 |
| `0xCF9A2+` | `bfldl CC1_M1,#0F0h,#10h` | **CC5 → capture front montant** |
| `0xD2EAA+` | `bfldh CC1_M1,#0F0h,#10h` et `bfldh CC1_M3,#0Fh,#1` | **CC6 → capture front montant** (vilebrequin) et **CC15 → capture front montant** |
| `0xC7398+` | `bfldh CC1_M1,#0Fh,#1` | **CC7 → capture front montant** |
| `0xD4D0A+` | `bfldl CC1_M2,#0Fh,#3` | **CC8 → capture, les deux fronts** |
| `0xCFF94+` | `bfldl CC1_M2,#0F0h,#50h` | **CC9 → compare mode 1 (bascule de broche)** |

**Conclusion n°1 — les entrées :**

* **CC6 / P2.6** = vilebrequin (capture front montant, confirmé par `bclr DP2.6` = broche en entrée et par PEC5 qui recopie `CC1_CC6`).
* **CC13 / P2.13** = arbre à cames (`word_D894 = CC1_CC13` dans `sub_AE144`).
* **CC5, CC7, CC8, CC15** = quatre **autres entrées de capture**, dont on ne connaît pas encore l'affectation physique (P2.5, P2.7, P2.8, P2.15). `CC8` capturant **les deux fronts** est typique d'une entrée de **fréquence** (débitmètre, signal vitesse véhicule, ou signal « information 15 »).

**Conclusion n°2 — les sorties :**

* `CC0…CC3` sont en **compare mode 0** = « timer logiciel » : leur seule fonction est de **programmer une échéance**. C'est confirmé par `sub_88A6C` qui réarme `CC1_CC0 = CC1_T0 + 0xC8` (200 ticks = **garde-temps**).
* **`CC9` est le seul canal en compare avec action sur broche** (`mode 5`, bascule) → P2.9.
* **Aucune écriture de `CC8`, `CC15`, `CC5`, `CC7` n'existe dans l'image** en dehors des sauvegardes/restaurations de l'ISR `sub_8874E`. Or `CC8` est en **capture** ici — donc la paire double-registre `CC0/CC8` n'est **pas** utilisée dans cet état de configuration.

> **Conséquence majeure :** l'ouverture/fermeture des injecteurs n'est **pas** programmée par du code présent dans cette moitié de l'image. Soit elle est faite par **PEC** (transfert matériel qui n'apparaît pas comme une écriture), soit elle est dans la moitié basse. C'est cohérent avec le fait que **`SRCPx`/`DSTPx` ne sont écrits nulle part** dans l'image (voir §6).

---

## 3. Interface bas niveau des PEC : des **descripteurs** en RAM  **[constat]**

Le firmware ne touche jamais `SRCPx`/`DSTPx`. Il écrit à la place des **descripteurs** que la couche OS (absente) doit convertir :

| Descripteur | Source | Destination | Écrit par |
|---|---|---|---|
| `word_FCF4` / `word_FCF6` | `0FE8Ch` = **CC6** | `0F8DEh` | `sub_C7398` (`loc_C756A`), avec `PECC5 = 7Fh` |
| `word_FCE4` / `word_FCE6` | `0F7B6h` (table) | `0FE6Eh` = **CC23** | `sub_94446` |
| `word_FCF0/FCF2`, `FCF8/FCFA` | `0CD94h`/`0CD8Ch` | `0FEB0h`/`0FEB2h` = **ASC0** | `sub_D02D6` (K-line) |

**[constat]** aucun lecteur de ces mots dans l'image → le programme qui les traduit en `SRCP/DSTP` est **hors image**.
**[constat]** l'U‑M précise (p. 5‑12) que les canaux PEC déplacent des données **dans le segment 0 uniquement** : les adresses PEC sont des offsets 16 bits. `0F8DEh` = IRAM `0x0F8DE` (la carte mémoire du C167CR donne IRAM = `00F600h…00FDFFh`, SFR = `00FE00h…00FFFFh`).
**[hypothèse]** il y a donc une **conversion d'adresse** par l'OS entre « adresse proche » (`word_F8DE` lu avec `DPP3 = 3` → `0x3F8DE`, RAM externe) et l'offset PEC (`0x0F8DE`, IRAM). Le `word_F8DE` écrit par le PEC et celui lu par le firmware ne peuvent être le même octet que si cette conversion existe. À vérifier dès qu'on aura la moitié basse.

---

## 4. `word_C416` : le mot d'état des 16 entrées… et la phase  **[constat]**

Toutes les 500 ms environ, une tâche balaie **22 codes défaut** (`0A08h` à `0A32h`, pas de 2) — un par entrée/config — via deux routines jumelles :

```
mov r4, word_16BE   ; pointeur de configuration du défaut
mov r5, #0A08h      ; emplacement mémoire de défaut
calls 0Ch, sub_C6B26    ; -> ENREGISTRE l'état du défaut
...
mov r4, word_16CC
mov r5, #0A26h
calls 0Ch, sub_C6B44    ; -> RELIT l'état du défaut
```

Les bits d'entrée sont lus sur des broches réelles :
`P12`, `P13`, `P7.1`, `P2.3`, `word_DE16` (bits 8…14), `word_FFD4` (bits 0…4) — **[constat]**.

### 4.1 Carte des bits de `word_C416`

`sub_C700E` puis `sub_C71D6` complètent le mot ; l'unpacking en drapeaux individuels se fait en `0xC70A0` :

| Bit | Drapeau | Origine |
|---|---|---|
| 0 | `byte_C2DB` | entrée |
| 1 | `byte_C2E3` | entrée |
| 2 | `byte_C2E1` | entrée |
| 5, 7, 8 | `byte_C2D7`, `byte_C2D5`, `byte_C2D6` | décodage 2 bits de `byte_C23D` (voir `sub_C700E`) |
| **9** | **`byte_C2DE`** | **PHASE arbre à cames** (posée par `sub_C7398`, `loc_C74F2`) |
| 6 | `byte_C2D3` | entrée |
| 11 | `byte_C2DD` | ← `byte_C243` |
| 13 | `byte_C8ED` | ← `byte_C229` (si `byte_C2B4 == 2`) |
| 15 | `byte_C8EE` | ← défaut de la boucle `sub_C6B44` |

`word_C418` porte 6 autres bits (0…5) ; seuls 3, 4, 5 sont publiés (`byte_C2D9`, `byte_C2DF`, `byte_C2E0`).

### 4.2 Les deux verrous de gel d'entrée

```
mov  r1, word_C416
mov  r0, r1
cpl  r0
or   word_C412, r0      ; C412 = "cette entrée a déjà été vue à 0"
or   word_C414, r1      ; C414 = "cette entrée a déjà été vue à 1"
```

**[constat]** Ce sont des accumulateurs d'activité : un bit de `C412` et de `C414` tous les deux à 1 = l'entrée a bougé ; un seul à 1 en permanence = **entrée figée**. C'est la détection de câble coupé / contact collé, classique EDC15, et c'est la source des défauts « signal implausible ».

---

## 5. La tâche de mesure — le cœur, niveau ROM  **[constat]**

Tout se passe dans `sub_C7398` (EA `0xC7398`, ~2,5 Ko), qui est **une seule tâche** contenant :

### 5.1 Bloc d'état du niveau ROM : `0xF622…0xF62C`

Écrit par les routines ROM `sub_8F4CC`, `sub_8F7C0`, `sub_8FAFE` :

| Adresse | Contenu |
|---|---|
| `byte_F622` | drapeau d'état |
| **`byte_F624`** | **code d'état** — valeurs observées : `00`, `14`, `1E`, `28`, `32`, `3C`, `46` (échelle d'étapes, même famille que `word_BF00` = `40/45/4A/50/60`) |
| `byte_F625`, `byte_F626` | mémorisations (`byte_F626 = byte_F63F`, `byte_F639`) |
| `word_F628`, `word_F62A`, `word_F62C` | **pointeurs calculés** dans un tableau d'octets à `0xF70D`/`0xF70E`, indexés par `byte_F63E` et `word_F642` |

Exemple (`0x8F71C`) :
```
mov  r4, #0F70Dh
movbz r5, byte_F63E
add  r4, r5
mov  word_F628, r4        ; pointeur = 0xF70D + index
```

**[constat]** `byte_F624` contient des paliers réguliers de 10 (`14h`=20, `1Eh`=30, `28h`=40, `32h`=50, `3Ch`=60, `46h`=70) : c'est une **échelle de progression** de l'étape de mesure, pas un code erreur.

### 5.2 Recopie atomique et tableau des périodes

En `0xC7A3A` la tâche prend un **instantané atomique** de 6 mots, sous protection d'interruption :

```
push PSW
atomic #4
or   PSW, #0F000h
and  PSW, word_C1A8
nop
mov  r0, #0F622h
mov  r1, #0F63Eh
mov  [r1+], [r0]     ; 6 transferts de mots
...
pop  PSW
```

**[constat]** l'instantané va de `0xF622` vers `0xF63E` (6 mots) et il est **atomique** — donc `word_F63E…word_F648` est la **copie cohérente** utilisée par le reste de la tâche pendant que le niveau ROM continue d'écrire la zone brute.
**[RÉSOLU à l'étape 4, §« Piste 1 » — il y a trois copies de travail, pas deux]** les 6 mots de destination (`F63E…F648`) sont ensuite utilisés **à la fois** comme *champ nombre d'événements* (`byte_F63E`), *drapeau* (`byte_F63F`), *index* (`word_F642`) et comme **tableau de périodes indexé** (`[r3+0F63Eh]`, `r3 = 2,4,…`). Les deux lectures ne sont pas superposables sans que le niveau ROM écrive la même zone à deux titres. **À trancher dans IDA** par les xrefs de `0xF640`–`0xF648` (voir §8, piste 1).

### 5.3 Fenêtre de plausibilité par événement — `loc_C7AD0`  **[constat]**

```
        mov  r1, word_1708          ; structure de config vilebrequin
        mov  r0, [r1+#0]  ; cmp r0, word_F8F6      ; borne
        ...
        mov  r0, [r1+#6]                            ; période max
        movbz r2, byte_F63E
        mov  r2, [r2+#0F640h]                       ; dernière période
        cmp  r2, r0  ; jmpa cc_UGT, loc_C7BCC       ; > max -> défaut

loc_C7AD0:                                  ; boucle sur les N événements
        mov  r0, word_F900                  ; référence 32 bits (mot bas)
        mov  r0, word_F900 / ror #8 ...
        mov  MDH, r0 ; movb rh0, word_F902  ; -> MDH:MDL = période de référence
        mov  r0, [r3+#0F63Eh]               ; période du i-ème événement
        divlu r0                            ; MDL = K / période_i
        mov  r0, [r1+#4]  ; cmp r0, MDL ; jmpr cc_NC, loc_C7B1E    ; > maxi
        mov  r0, [r1+#2]  ; cmp r0, MDL ; jmpr cc_ULE, loc_C7B1E   ; < mini
        ; ---- dans la fenêtre : l'événement devient la nouvelle référence
        mov  r0, [r3+#0F63Eh]
        mov  word_F900, r0
        movbz r0, byte_F63F ; mov word_F902, r0
        subb byte_F8F2, ONES               ; décrémente le compteur de cycle
loc_C7B1E:                                  ; hors fenêtre : rejeté
        movb rl0, [r1+#14h] ; movb byte_F8F2, rl0   ; recharge le compteur
```

**[constat]** deux limites, **par événement**, sur la vitesse instantanée `K/période` : `[word_1708+2]` (mini) et `[word_1708+4]` (maxi).
**[constat]** `word_F900`/`word_F902` = période de référence **32 bits** (indispensable à bas régime : une période de dent dépasse 65 535 ticks).
**[constat]** `byte_F8F2`, rechargé depuis `[word_1708+14h]`, est le **compteur d'événements du cycle** ; à 0 on passe au contrôle de niveau 2.

### 5.4 Timeout de cycle et DTC — `loc_C7B4A`  **[constat]**

```
loc_C7B4A:
        cmpb ZEROS, byte_F8F2
        jmpr cc_NC, loc_C7BAE          ; compteur non nul -> rien
        jnb  word_FD1C.9, loc_C7B84
        mov  r0, word_C08E             ; horodatage courant
        sub  r0, word_F91C             ; - horodatage du dernier événement
        subc r0, #0
        cmp  r0, word_F8F8             ; vs seuil de timeout
        jmpr cc_C, loc_C7C04           ; pas encore -> on attend
        movb byte_F8F2, ZEROS
        bset r0.2
        bmov r0.0, unk_FD22.8
        mov  r3, #18h
        mov  r1, word_170A
        mov  r2, #2FEh                 ; <-- code défaut
        calls 0Ch, sub_CE9B4           ; ENTRÉE EN MÉMOIRE DE DÉFAUT
        bmov unk_FD22.8, r0.0

loc_C7B84:                              ; calcul du seuil
        mov  r0, word_F900             ; période de référence
        mov  r1, [r1+#0Eh]             ; facteur de config (x10000)
        mulu r0, r1
        mov  r0, #2710h                ; 10000
        divlu r0
        cmp  MDL, #2
        jmpr cc_NC, loc_C7B9E
        mov  MDL, #2                   ; plancher = 2
loc_C7B9E:
        mov  word_F8F8, MDL            ; seuil de timeout
        mov  r0, word_F91C
        mov  word_C08E, r0
        bset word_FD1C.9
```

**C'est la réponse complète à « où est le gap » :**

* seuil = **`période de référence × word_1708[0Eh] / 10000`**, plancher 2 ticks ;
* si aucun événement n'arrive dans ce délai → `word_FD1C.9` est mis, un **défaut `2FEh`** est enregistré via `sub_CE9B4(r1 = word_170A, r2 = 2FEh, r3 = 18h)` et le drapeau `unk_FD22.8` est positionné ;
* `word_1708` = **la structure de configuration vilebrequin** complète :

| Offset | Rôle |
|---|---|
| `+0` | borne de période (contrôle d'entrée) |
| `+2` | **limite basse** de `K/période` |
| `+4` | **limite haute** de `K/période` |
| `+6` | période maximale acceptée |
| `+0Ch` | limite de compteur (dents à ignorer) |
| `+0Eh` | **facteur du timeout de gap** (×10000) |
| `+14h` | nombre d'événements par cycle |

**[constat]** `sub_CE9B4` est l'**API mémoire de défauts** : `r1` = structure de configuration/limites, `r2` = code défaut (ici `2FEh`; ailleurs `377Fh`), `r3` = sous-fonction. Son retour `r0.0` est mémorisé dans un bit d'état (`unk_FD22.8`).
*(Correction de l'étape 2, où je l'avais décrit comme un accès Datensatz.)*

---

## 6. Boucle complète, et où elle casse

```
  P2.6 ──capture CC6──► CC1_CC6 ──PEC5──► 0F8DEh
                                              │
                     niveau ROM  sub_8F4CC / sub_8F7C0 (0x8xxxx)
                     · comptage / tampon à champs de bits (word_F646)
                     · code d'état byte_F624, tableau 0xF70D
                     · écrit 0xF622…0xF62C
                                              │
                     instantané atomique 0xF622 ──► 0xF63E (tâche sub_C7398)
                                              │
        ┌─────────────────────────────────────┴─────────────────────────────┐
        │ fenêtre K/période  → rejet du gap        (word_1708[2],[4])       │
        │ timeout K×période  → DTC 2FEh            (word_1708[0Eh])         │
        │ somme de N périodes → divlu K32/(Σ)      (word_F640…F648, word_1702)│
        │ seuil word_F8E4    → moyenne/publi       → word_C91A / word_C91C  │
        └─────────────────────────────────────┬─────────────────────────────┘
                                              │   (word_C42E, word_C3D2 = sources)
                     bloc d'interface OS  C91C (régime) / C904 (charge)
                                              │
                     cartographies (word_1432, word_1B3C, word_1AA2, …)
                                              │
                     machine d'état byte_CA39 : état 8 = synchro vilebrequin
                                              │
                     état 20h + byte_CA3A (phase AAC) ──► word_C416 bit 9
                                              │
                     XX ← [ÉTAGE DE SORTIE NON PRÉSENT DANS L'IMAGE]
```

**Deux trous, tous les deux au même endroit :**

1. **l'étage de sortie** — aucune écriture de valeur de comparaison d'injection dans cette moitié de flash (§2) ;
2. **les constantes** — `word_1702` (K du régime), `word_1708` (tout le gap), `word_170A` (DTC), `word_16F0` (phase/timeouts), `word_145A` (seuils), `word_1432` (fenêtres régime/charge), `word_141E` (N), `word_1B3C` (angles) sont **toutes** des pointeurs de la mémoire basse.

---

## 7. Une découverte utile en passant : le jeton de tâche et la carte des 125 tâches

Chaque corps de tâche commence par **[constat]** :

```
calls 0, unk_7B4            ; service OS (prologue / watchdog / ordonnanceur)
scxt  CC2_CC27, #610h       ; <- jeton de tâche
mov   word_DC00, CC2_CC27   ; publié dans word_DC00
```

**125 jetons distincts** ont été extraits → `analyse_edc15c2_4hx/taches_jeton_CC27.csv` (ligne, jeton, EA et nom du sous-programme). C'est une **carte de l'ordonnancement** utilisable directement sous IDA : on peut nommer les 125 tâches par leur numéro et retrouver la structure temporelle du calculateur.

Les groupes observés :

| Plage | Interprétation |
|---|---|
| `0x102`…`0x134` | tâches « rapides » (angles, injection) |
| `0x336`…`0x39x` | tâches de calcul (cartographies) |
| `0x402`…`0x410` | tâches moyennes |
| `0x600`…`0x61E` | tâches lentes / diagnostic ; **`0x610`** = agrégateur par cylindre (grille `0xD926`), **`0x608`** = période de slot 32 bits (`0xD5C0`) |

---

## 8. Prochaines pistes, par ordre de rendement

**(1) Trancher l'ambiguïté `0xF622` ↔ `0xF63E`.** Sous IDA : `xrefs` de `0xF640` et des deux constantes `0F622h`/`0F63Eh`. Si personne n'écrit `0xF640..0xF648` hors de la copie, alors le tableau des périodes est **bien** `0xF640` et la zone `0xF622` est sa source brute — et l'interprétation de `byte_F624` comme code d'état doit être revue (deux variables homonymes).

**(2) `sub_94446` (EA `0x94446`) — générateur T8 + PEC1.** Il construit une table à `0xF7B6`, y met une valeur tous les `0x1A0` (416) ticks avec un marqueur `0x2134`, configure `PECC1 = nb_mots | 400h` et démarre `T8R`. Le motif vient de **`byte_F602` (8 bits)**, parcouru bit par bit. Deux lectures possibles, à départager :
 * **[hypothèse A]** **autotest** du couple CAPCOM2/PEC (les canaux `CC16…CC31` sont en mode 0 = *non configurés*, ce qui rend un usage en sortie physique peu probable) ;
 * **[hypothèse B]** générateur d'impulsions 8 voies sur P8 (`CC16IO…CC23IO` = P8.0…P8.7).
 Le fait que `CC2_M4…M7` ne soient **jamais** écrits dans l'image pousse fortement vers A.

**(3) Suivre `word_1432`.** C'est la structure de fenêtres utilisée par `sub_AFAA0` (`+0Eh`, `+12h`, `+14h`, `+22h` comparés à `word_C562` et `word_C91C`). `word_1432` n'a **aucun écrivain** dans l'image → pointeur de la mémoire basse. Mais les **lecteurs** permettent de reconstituer la logique des fenêtres régime/charge, qui est le squelette de la commutation de cartographies.

**(4) `word_C562` : aucun écrivain dans l'image, lu partout comme seuil de régime.** C'est probablement le **régime « système »** publié par la couche absente, distinct du régime mesuré `C91C`/`C42E`. Confirmer par une recherche d'écriture indirecte (`mov [r4], rX` avec `r4 = 0xC562`) — `mov r12, #0C562h` existe en `sub_9B0E0` (ligne 140315), c'est la piste.

---

## 9. Ce qu'on peut déjà affirmer sur la question de départ

| Question | Réponse | Statut |
|---|---|---|
| Où entre le capteur de régime ? | `P2.6` → capture `CC6` → PEC5 → `0F8DEh` | **constat** |
| Combien de mesures par tour ? | somme de `byte_F63E` périodes, `byte_F63E` rechargé depuis `word_1708[14h]` | **constat** (valeur = mémoire basse) |
| Comment le gap est-il traité ? | fenêtre `K/période` par événement + timeout `K × dernière période` + DTC `2FEh` | **constat** |
| Où est la segmentation par cylindre ? | grille 16 mots `0xD926`, indexée par `byte_C2E9` (étape 1) | **constat** |
| Où est la phase ? | `byte_CA3A`/`byte_CA38` → `word_C416` bit 9 → `byte_C2DE` | **constat** |
| Où sont écrites les sorties d'injection ? | **pas dans cette moitié d'image** | **constat négatif** |
