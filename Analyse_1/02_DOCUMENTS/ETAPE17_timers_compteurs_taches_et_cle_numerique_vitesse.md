# ÉTAPE 17 — `T0`/`T7` en mode compteur, la table des tâches, le verdict sur `F91C`, et la clé numérique pour la vitesse

Suite de `ETAPE16_service_080_blocs_et_timers.md`.
Preuves = **numéros de ligne de `clean.asm`**. Ce qui n'est pas vérifié est marqué **non établi**.

---

## 1. `CC1_T01CON` décodé : deux compteurs d'impulsions

`CC1_T01CON` est écrite trois fois dans tout le programme, toujours avec la **même valeur** :

| ligne | instruction | contexte |
|---|---|---|
| 96944 | `bfldh CC1_T01CON, #40h, #41h` | init des canaux CAPCOM1 |
| 106956 | **`mov CC1_T01CON, #4141h`** | chunk de `sub_8874E` (`loc_8E060`) |
| 217565 | `bfldl CC1_T01CON, #4Fh, #41h` | autre init |

Valeur **`0x4141`** = `0100 0001 0100 0001`. Selon la disposition du registre T01CON
(octet bas = T0/T1, octet haut = T7/T8 ; bit 6 = `T0M`, bit 2 = `T1M`, bit 0 = `T1R`,
idem en bits 14/10/8 pour T7/T8) :

| bit | nom | valeur | conséquence |
|---|---|---|---|
| 6 | `T0M` | **1** | **T0 fonctionne en MODE COMPTEUR** (compte les impulsions sur son entrée) |
| 0 | `T1R` | 1 | T1 est rechargé |
| 14 | `T7M` | **1** | **T7 aussi en mode compteur** |
| 8 | `T8R` | 1 | T8 rechargé |

> Réserve de méthode : je n'ai pas pu ouvrir le PDF du C167 dans cet environnement (aucune
> bibliothèque PDF disponible), donc la **disposition des bits** ci-dessus vient du manuel et n'a pas
> été revérifiée page à page ici. En revanche la **conséquence est confirmée par l'usage** :
> `word_FC04 = CC1_T0` est photographié **126 fois** et sert toujours à calculer un **écart**
> (`T0 − FC04`). Un écart n'a de sens que si la source avance à **cadence garantie**. Donc :
> **T0 est alimenté par un signal à fréquence fixe sur son entrée** — soit une horloge de la carte,
> soit un capteur périodique. **C'est exactement ce qu'il reste à déterminer** (§4).

**Correction de l'étape 16 §3** : j'y écrivais que `CC1_T0` était « la base de temps libre ».
C'est **exact en usage** (c'est bien elle qui donne le temps) mais **inexact en nature** : c'est un
**compteur d'impulsions**, pas un timer interne. La nuance est décisive pour la vitesse.

---

## 2. `sub_9CF70` décodé : la table des tâches

```asm
l.143770  sub_9CF70:                     ; (r12 = slot, r13 = n° de tâche, r14, r15)
l.143776    r7 = (r15 << 4) | 0FF00h     ; champ "paramètre" (nibble bits 7..4)
l.143780    si r14 == 1 : r7 |= 8        ; drapeau
l.143790    r8 = (r13 << 13) & 0E0FFh | (r13 >> 3) & 0FFh   ; n° de tâche éclaté
l.143799    r9 = 0EF00h + (r12 << 4)     ; ← DESCRIPTEUR en RAM, 16 octets par slot
l.143806    [r9+6] = r7
l.143808    [r9+2] = r8
l.143810    [r9+4] = 0
l.143812    [r9+0] = 5595h               ; ← MAGIC d'entrée valide
```

**Table complète des 17 enregistrements** (extraite automatiquement) :

| ligne | slot | tâche | r14 | r15 | condition |
|---|---|---|---|---|---|
| 139216 | `#6` | `0x108` | 1 | 8 | toujours |
| 139252 | `#1` | `0x208` | 1 | 8 | toujours |
| 139257 | `#4` | `0x072` | 1 | 5 | toujours |
| 139262 | `#3` | `0x488` | 1 | 8 | toujours |
| 139267 | `#5` | `0x788` | 1 | 6 | toujours |
| 139272 | `#7` | `0x388` | 1 | 5 | toujours |
| 139277 | `#2` | `0x348` | 1 | 5 | toujours |
| 139285 | `#4` | *(variable)* | 1 | 8 | variante |
| 139295 | `#9` | `0x349` | 0 | 7 | `byte_C2B7` bit 0 |
| 139300 | `#0D` | `0x389` | 0 | 5 | `byte_C2B7` bit 0 |
| 139311 | `#0A` | `0x50E` | 0 | 3 | `byte_C2B7` bit 3 |
| **139316** | **`#0B`** | **`0x412`** | **0** | **8** | **`byte_C2B7` bit 3** |
| 139321 | `#8` | `0x7E2` | 0 | 6 | `byte_C2B7` bit 3 |
| 139326 | `#0F` | `0x0A8` | 0 | 5 | `byte_C2B7` bit 3 |
| 139341 | `#0E` | `0x34D` | 0 | 6 | `byte_C2B7` bits 0-2 = 6 |
| 139350 | `#0E` | `0x34D` | 0 | 5 | variante |
| 139363 | `#0C` | `0x38D` | 0 | 5 | variante |

Deux observations **certaines** :
- le **même numéro de tâche** (`0x34D`) est enregistré avec `r15 = 6` **ou** `5` selon la variante
  ⇒ `r15` **dépend de la variante** : c'est bien un **paramètre de cadence/phase**, pas une constante
  d'identification ;
- la tâche **`0x412` n'existe que si `byte_C2B7` bit 3 = 1** ⇒ c'est une tâche **de variante**.

> **Ce qui n'est PAS établi** : l'unité de `r15` (période en ms ? phase dans une trame ? le champ est
> un nibble, valeurs observées 3 à 8). Le planificateur qui consomme ces descripteurs est dans la
> moitié manquante. **Je ne conclus donc pas « tâche 0x412 toutes les 8 ms »** — ce serait une
> hypothèse, pas une preuve.

---

## 3. `word_F91C` : verdict argumenté (et je clos le débat)

Code complet de la tâche `0x412` (l. 233549-233562) :

```asm
scxt CC2_CC27, #412h
r0 = word_F91C
r0 = r0 - 1
si r0 == 0 → r0 = ONESh        ; ← le 0 est SAUTÉ : 0x0001 → 0xFFFF
word_F91C = r0
```
et l'initialisation (l. 233544) : `word_F91C = ONES` quand `word_FD0C.15 = 0`.

**Ce qui est prouvé :**
- `F91C` est un **compte à rebours de 65535 unités** (le zéro est sauté, donc la période est
  exactement 65535) ;
- il **décroît de 1 par exécution** de la tâche `0x412`, **sans aucun lien avec une impulsion** : ni
  la capture, ni un compteur matériel n'est lu dans cette tâche (6 instructions).

**Conséquences :**
- l'hypothèse « **distance parcourue** » (étape 13) est **écartée** : un compteur de distance doit
  *accumuler* les impulsions ; ici il n'y a qu'un décrément d'unité, identique à chaque appel ;
- l'hypothèse « **base de temps** » (étape 14) est **la seule cohérente avec le code**, l'unité
  restant dépendante de `r15 = 8` de la tâche `0x412` (§2) ⇒ **résolution non établie**, mais la
  nature est tranchée.

**Ordre de grandeur plausible** (à titre indicatif, **pas** une preuve) : si 1 unité valait 8 ms,
la fenêtre `8333` de `word_15F0` (`0xE3AD0`) donnerait **66,7 s** et `10000` donnerait **80 s** —
des durées de temporisation tout à fait usuelles. Si 1 unité valait 1 ms : 8,3 s et 10 s, également
usuel. **Les deux passent**, donc les fenêtres ne tranchent pas.

---

## 4. `CC1_CC13` : la mesure, son arithmétique exacte, et la clé numérique

### 4.1 Le mécanisme (l. 174807-174886)

```asm
l.174807  r4 = CC1_M3 ; and r4,#20h ; cmp r4,#20h      ; le canal est-il en mode 2 ?
l.174810  sinon : r4 = CC1_M3 ; and r4,#0FF0Fh ; or r4,#10h ; CC1_M3 = r4   ; → mode 1
l.174819  si IR : bclr IR ; si byte_D8A0 == 0 :
l.174822     word_D894 = CC1_CC13 ; byte_D8A0 = 1      ; ← ARME la mesure
l.174828  sinon (byte_D8A0 ≠ 0) :
l.174828     r4 = CC1_CC13 − word_D894                 ; ← PÉRIODE en unités T0
l.174831     word_D896 = r4
l.174832     fenêtre : 0x26AC ≤ r4 ≤ 0x2774            ; 9900 … 10100
l.174841     si hors fenêtre : nouvel essai sur r4 >> 1 (demi-période)
l.174859     si validé : word_D362 = D896 ; word_D894 = CC1_CC13
l.174866     r5 = D896 / 20
l.174870     r2 = r5 ; shl 2 ; add r5 ; shl 2 ; sub r5  ; → r2 = 19 × r5
l.174880     word_D898 = r2                            ; ← 0,95 × D896
l.174881     CC1_M3 = (M3 & 0FF0Fh) | 20h              ; retour au mode 2
```

Le canal est celui dont le nibble de mode est en **bits 4-7 de `M3`** = **CC13** (M3 couvre
CC12-CC15 : CC12 = bits 3-0, CC13 = bits 7-4).

**Résultat arithmétique exact, vérifiable** : `word_D898 = 19 × (D896 div 20)`, soit
**95 % de la période mesurée** (à la troncature près) — un **seuil à −5 %**, donc une tolérance
de fréquence de **+5,3 %**. C'est la signature d'un **contrôle de période avec bande de tolérance**,
pas d'un calcul de grandeur physique.

### 4.2 Ce que je ne peux pas affirmer

Le nibble de mode vaut **1 puis 2**. Selon le codage CAPCOM1 classique, 1 et 2 sont des modes
**compare** ; selon le codage CAPCOM2, 1 et 2 sont des **captures front montant / front descendant**.
La lecture d'une valeur différenciée après chaque bascule impose la **capture** : c'est donc le second
codage qui s'applique ici. **Mais je ne l'ai pas vérifié sur le manuel** (PDF non exploitable ici) :
je le signale comme **point à confirmer**, plutôt que de le présenter comme acquis.

### 4.3 La clé numérique — avec tes chiffres

Tes données (8 impulsions/tour, 4040 impulsions/km) sont **cohérentes entre elles** :

```
f = 4040 × v / 3600  =  1,1222 × v[km/h]
   v = 50  →  56,1 Hz     ✓ (ton 56 Hz)
   v = 210 → 235,7 Hz     ✓ (ton 235 Hz)
1 impulsion = 1 000 000 / 4040 = 247,5 mm
```

Donc **si** une période de capteur de vitesse était mesurée en unités T0, la valeur attendue serait
`T = F_T0 / f`. Table de conversion, qui permet de **reconnaître la grandeur** en lisant une seule
valeur sur véhicule :

| vitesse | f (Hz) | T si F_T0 = 250 kHz | 500 kHz | **1 MHz** |
|---|---|---|---|---|
| 20 km/h | 22,4 | 11 140 | 22 321 | 44 643 |
| **45 km/h** | 50,5 | 4 950 | **9 900** | 19 800 |
| **50 km/h** | 56,1 | 4 456 | 8 911 | 17 822 |
| **89 km/h** | 99,9 | 2 503 | 5 006 | **10 000** |
| 130 km/h | 145,9 | 1 713 | 3 428 | 6 855 |
| 210 km/h | 235,7 | 1 061 | 2 121 | 4 243 |

**Lecture** : la fenêtre de validité observée (`9900 … 10100`) correspond à
- **89,1 … 90,9 km/h** si T0 compte à 1 MHz,
- **44,6 … 45,5 km/h** s'il compte à 500 kHz,
- **22,3 … 22,7 km/h** à 250 kHz.

Une fenêtre de **±1 % autour d'une valeur ronde** ressemble beaucoup plus à la vérification d'un
**signal à fréquence fixe** qu'à une mesure de vitesse. C'est pourquoi je **ne conclus toujours pas**
que `D896` est une vitesse — mais la table ci-dessus donne le **critère de reconnaissance** :
il suffit de lire l'identifiant de diagnostic **`0x02`** sur un véhicule roulant.

---

## 5. Ce que tu peux faire pour trancher (test concret, sans démontage)

L'identifiant `0x02` du service `0x80` renvoie **`word_D896`** (étape 16 §2.1), et l'identifiant
`0x0E` renvoie **`word_C0D0`** (instantané de `F91C`). Si tu as un outil capable de lire les
**paramètres locaux** PSA (pas seulement les P-codes) :

1. **moteur tournant au ralenti**, relève `0x02`. Puis à 50 km/h stabilisés, puis à 90 km/h.
2. Confronte aux colonnes du §4.3 :
   - si `0x02` **varie avec la vitesse** → c'est le capteur de vitesse, et la colonne qui colle donne
     la fréquence de T0 (donc la nature de son entrée) ;
   - si `0x02` **ne change pas** (≈ 10 000 constant) → c'est un signal fixe (synchronisation/PWM), et
     la vitesse est ailleurs ;
   - si `0x02` vaut ≈ 17 800 à 50 km/h → **vitesse capteur, T0 à 1 MHz** : la vitesse est alors
     disponible, et le rapport engagé se calcule en divisant `C42E` (régime) par elle.
3. Relève aussi `0x0E` deux fois à 30 s d'intervalle, moteur au ralenti : la **différence** donne
   directement la cadence de la tâche `0x412` en unités par seconde ⇒ **l'unité de `F91C`**.
   *(65535 / différence × 30 s = la période de rebouclage ; si la différence vaut 3750 en 30 s,
    l'unité est 8 ms.)*

C'est le genre de mesure qui vaut dix lectures de listing — et elle est faisable au banc.

---

## 6. Prochaines actions côté désassemblage

1. **Source de `T0IN`** : chercher la configuration des ports/fonctions alternatives (`P1`, `P2`,
   `DP1`/`DP2`, `ODP`, `PECC`) au voisinage des init de `loc_8E060` et `sub_88384` — cela dira si
   l'entrée de T0 est une horloge de carte ou une broche capteur.
2. **Le planificateur** qui consomme les descripteurs `0xEF00 + slot×16` (magic `0x5595`) : son code
   donne l'unité de `r15`, donc la cadence de la tâche `0x412`, donc l'unité de `F91C`.
3. **Le rapport engagé** : chercher une division entre `C42E` (régime) et la variable de vitesse une
   fois celle-ci identifiée ; les cartes de couple par rapport sont probablement les cartes à axe
   `C42E` × `D004 [0…7000]` (`0xE707A`, `0xE72C4`, `0xE744C`).
