# ÉTAPE 67 — Qui lit `0xE1129` → `0xE11DD` : balayage des accès **directs et indirects**

## ⚠ ERRATA (voir ÉTAPE 68)

Deux points de ce document sont corrigés par l'étape 68 :

1. § 2f — j'avais annoncé une « table de mots `EA 0xE4E4E` ». **Faux** : c'est une table en **RAM `0x0E4E`**,
   et `sub_CE57E` exécute `add r12, r12` **avant** de l'indexer : l'index est **doublé**.
2. § 3 — « les valeurs de `0xE11C4` sont des trous » reste vrai pour **ce site précis** (`cmp r2,#11h`),
   mais la table RAM `0x0E4E` est décodée : **18 couples de codes de défaut**. Voir `ETAPE68`.

---

> Tu avais raison deux fois : le haut du dernier segment de 32 Ko est du **code** (seg019), et il
> fallait chercher des **adresses indirectes**. Voici les sept pistes que j'ai balayées — et la seule
> qui donne un accès indirect réel.

---

## 1. Confirmation : `seg019` = code, et les seules données qui y vivent

Le listing porte des labels `loc_FC0EA`, `loc_FC10A`, `loc_FC142`… `loc_FFFFF` ⇒ **`EA 0xF0000+` est du
code**. Mon « 14 Ko de données » de l'étape 66 était faux dans son vocabulaire : c'est **du code non
dupliqué**, donc pas de la calibration. Ton critère est le bon.

**Mais** le code **lit** quelques cellules nommées, uniquement via `extp` (donc de la donnée au milieu
du code) :

| cellule | EA | accès | usage |
|---|---|---|---|
| `byte_FBEF9` | `0xFBEF9` | `extp #3Eh, #1` | comparée à `0xF0` et `0xFF` → **drapeau d'état** |
| `byte_FBEFA` | `0xFBEFA` | `extp #3Eh, #1` | recopiée dans un buffer (`l.404127`, `l.404472`, `l.404990`) |
| `word_FBF38` / `word_FBF3A` | `0xFBF38` | `extp #3Eh, #2` | paire de mots (`l.405974`) |
| `byte_FEC00` / `byte_FEC01` | `0xFEC00` | `extp #3Fh, #1` | paire d'octets (`l.406144`) |

**Rappel de la règle vérifiée** : `extp #pag` + adresse 16 bits ⇒ `EA = pag × 0x4000 + adresse`, contrôlé
sur cinq sites (`#3Eh` + `FBEF9` → `0xFBEF9`, `#37h` + `DFFF6` → `0xDFFF6`, `#33h` + `B6AC` → `0xCB6AC`…).

---

## 2. Les sept pistes d'accès indirect — résultats

### a) Immédiats des adresses de la zone → **zéro**

Recherche de `#111Eh`, `#1129h`, `#1148h`, `#117Ch`, `#11A0h`, `#11C4h` dans les **412 022 lignes** :
**0 occurrence**. Aucune instruction ne charge directement une adresse de la zone.

### b) Repointage des mots-handles → **zéro**

`word_141C`, `word_141E`, `word_1420`, `word_1422`, `word_1424` : **aucune écriture**. Les pointeurs ne
bougent jamais après l'init ⇒ pas de redirection dynamique possible.

### c) Handle passé à une routine générique → **6 candidats, 6 faux positifs**

J'ai extrait les **1 541 sites** du firmware où un handle est chargé puis une routine appelée dans les
6 lignes suivantes. Six concernent nos handles — **aucun ne les passe réellement** :

```asm
mov  r4, word_141E
movb rl5, [r4+#19h]      ; ← l'octet d'option est LU ici
jmpr cc_NZ, loc_ABB58
mov  r12, word_1994      ; ← le handle réellement passé à l'interpolateur
mov  r13, word_C906
calls 0, unk_1D50
```

Idem `word_19B6` (`l.171009`), `word_1DCA` (`l.240427`). Mon détecteur était trop large : **la zone
n'est jamais passée en handle à un interpolateur**.

### d) `sub_CE9B4` (686 appels, service EEPROM/valeurs par défaut) → **aucun de nos handles en `r1`**

Les handles réellement passés sont `word_14A4` (13×), `word_1C10`, `word_1B1E`… **La zone ne sert pas
de source de valeurs par défaut EEPROM.**

### e) `extp` / pages → **le Datensatz n'est jamais ouvert en cross-page**

Pages utilisées dans tout le firmware : **`0x22`, `0x24`, `0x33`, `0x37`, `0x3E`, `0x3F`**
(= `0x88000`, `0x90000`, `0xCC000`, `0xDC000`, `0xF8000`, `0xFC000`).
**Les pages `0x38` à `0x3B` — soit `0xE0000` à `0xEFFFF` — n'apparaissent jamais.**

### f) ★ `sub_CE57E` (seg016) → **accès indirect RÉEL sur `0xE11A0` et `0xE117C`**

```asm
loc_CE5B0:
                mov     r3, word_1422      ; table des zéros   (0xE11A0)
                add     r3, r12            ; ★ index
                mov     r3, [r3]
                mov     [r13], r3
...
loc_CE5D4:
                mov     r3, word_1420      ; table des 0xFFFF  (0xE117C)
                add     r3, r12            ; ★ index
                mov     r3, [r3]
                mov     [r13], r3
```

**Le sélecteur est un tableau de bits en RAM `0xFD21 + index`** : `andb rl3, #1` → table des zéros,
`andb rl3, #2` → table des `0xFFFF`. **Voilà l'adresse indirecte que tu cherchais** : ce n'est pas
l'adresse de la donnée qui est indirecte, c'est **la table** qui est choisie à l'exécution par un bit.

### g) ★ `l.231375` / `l.231675` (seg016) → **accès indirect RÉEL sur `0xE11C4`**

```asm
mov  r7, word_1424
loc_CF200:
  mov  r1, [r7+]           ; parcours des 20 mots
  calls 0Ch, sub_CFEFA
```
```asm
mov  r0, word_1424
add  r0, r1
add  r0, r1                ; base + 2 × index
mov  r2, [r0]
```

---

## 3. ★ Ce que révèle le dernier site : les valeurs de `0xE11C4` sont des **trous**

```asm
mov  r2, [r0]              ; valeur de la table
cmp  r2, #11h              ; ★ 17
jmpr cc_UGT, loc_CF51E     ; > 17  ->  ÉCARTÉE
mov  r0, #0E4Eh            ; table courte en RAM
add  r0, r2
add  r0, r2
movb rl2, [r0+]            ; 2 octets par entrée, sentinelle 0xFF
cmpb rl2, #0FFh
```

**Seize des vingt valeurs (`0x0F10`, `0x0F61`, `0x0F80`, `0x0FFA`, `0x0F8B`…) sont > 17 : elles sont
rejetées par ce test.** Seules `0x0005` et `0x000F` passent et servent d'**index** dans une table courte
à `0x0E4E`.

⇒ **Correction de l'étape 65** : `0xE11C4` n'est **pas** « 20 valeurs indexées par position ». C'est une
**liste de valeurs dont 18 sont des marqueurs hors bornes** (des trous). Le seul usage réel identifié
mobilise **deux** entrées.

---

## 4. Réponse synthétique à ta question

| question | réponse établie |
|---|---|
| Qui lit les **octets d'option** de la zone ? | **138 sites directs** (89 switch / 49 donnée), segments s13→s17. Rien d'autre. |
| Y a-t-il des **accès indirects aux octets d'option** ? | **Non.** 5 pistes négatives (immédiats, repointage, handle passé, `sub_CE9B4`, `extp`). |
| Y a-t-il des **accès indirects aux tables** ? | **Oui, trois** : `sub_CE57E` (index + bit de sélection en RAM `0xFD21`), `l.231375` (parcours `[r7+]`), `l.231675` (base + 2×index). |
| Le code du haut du dernier segment lit-il la zone ? | **Non** : ses seules données sont `0xFBEF9-FBEFA`, `0xFBF38`, `0xFEC00-01`. |

**Autrement dit : la zone est lue à 100 % par les segments `s13`→`s17` (code moteur, CAN et diagnostic),
et le seul mécanisme « tordu » est le sélecteur de table en RAM `0xFD21`.**

---

## 5. Consignation

- **`CATALOGUE_MAITRE.md` § 13 B.13** : les sept pistes, le mécanisme `sub_CE57E`, la correction sur `0xE11C4`.
- **`acces_indirects_zone.csv`** : une ligne par piste, avec la méthode et le verdict.
- Catalogue : 2 192 → **2 238 lignes**.

## 6. Prochain pas

1. **`0xFD21` — le tableau de bits sélecteur** : qui l'écrit ? C'est lui qui décide, pour chaque index,
   si la valeur vient de la table des zéros ou de celle des `0xFFFF`. **C'est la clé du diagnostic.**
2. **La table courte à `0x0E4E`** (2 octets/entrée, sentinelle `0xFF`) : à décoder.
3. **`byte_FBEF9` / `byte_FBEFA`** : deux drapeaux vivants dans le code non dupliqué — à identifier
   (validité d'apprentissage / variante ?).
