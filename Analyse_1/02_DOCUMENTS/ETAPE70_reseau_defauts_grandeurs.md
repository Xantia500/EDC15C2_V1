# ÉTAPE 70 — Le réseau « code de défaut → grandeurs surveillées » : 96 listes, 1 277 pointeurs

> J'ai suivi la piste : `0xCF5EC` → 96 structures → leurs pointeurs. Le réseau est **cartographié**.
> Trois hypothèses ont été testées et **trois sont réfutées** — je les consigne pour qu'on ne les rejoue pas.
> Et il reste **un verrou technique précis** que je décris à la fin, avec la façon de le lever.

---

## 1. Ce qui est acquis : le réseau existe et il est lisible

La table de 96 pointeurs de **`EA 0xCF5EC`** (page `0x33`, `mov r0, #0B5ECh` l. 231163) donne **96 structures
distinctes** dans le Datensatz, de `0xE1426` à `0xE1E20`, soit **2 554 octets**. Chacune est une **liste de
pointeurs de 2 octets** en ordre croissant.

**L'auto-validation :** une suite strictement croissante de mots ne peut pas être du code. C'est le critère
qui permet de dire « ce sont des listes de pointeurs » sans connaître leur sémantique.

| mesure | valeur |
|---|---|
| listes | **96** (95 non vides) |
| pointeurs au total | **1 277**, tous distincts |
| plage des pointeurs | `0x11EC` – `0xBB9A` |
| longueur des listes | de **2 o** (43 listes = 1 seul pointeur) à **278 o** (`EA 0xE1CF4`, code 0) |
| moyenne | **≈ 13 pointeurs par code de défaut** |

Exemples :

| code | EA de la liste | longueur | premiers pointeurs |
|---|---|---|---|
| 0 | `0xE1CF4` | 278 o | `A1A8 A1C8 A1D0 A1DC A1E8 A1F4 …` |
| 1 | `0xE1492` | 20 o | `2372 2392 239E 23B4 2684 2690 …` |
| 2 | `0xE1C64` | 28 o | `9462 9482 9488 948E 9490 9498 …` |
| 3 | `0xE1E0A` | 22 o | `BAB6 BAD6 BAD8 BADA BAF6 BB12 …` |
| 5 | `0xE15B6` | 10 o | `3754 3774 3780 378C 3792` |

⇒ **Un code de défaut donné est associé à ≈ 13 grandeurs.** C'est le réseau « défaut ↔ mesures » du
calculateur — et c'est exactement le genre de table qu'on cherche quand on veut savoir **quelles mesures
participent à la détection d'un défaut FAP ou EGR**.

**Livrable : `defauts_96_listes.csv`** — une ligne par code : valeur de la table, EA de la liste, longueur,
nombre de pointeurs, et la liste complète en hexadécimal.

## 2. Les trois hypothèses réfutées

### a) « Ces listes contiennent des identifiants `0x0Fxx` comme `word_1424` » → **FAUX**

Intersection entre les 20 identifiants de `0xE11C4` (`0F10 0F61 0F80 0FFA …`) et les 1 277 pointeurs :
**0**. L'alphabet `0x0Fxx` de `word_1424` et les listes de défauts sont **deux mondes séparés**.
La question ouverte de l'étape 68 sur `word_1424` reste donc **entière** — mais au moins cette piste-là est
éliminée.

### b) « Les blocs pointés suivent une trame fixe de 32 octets finie par la sentinelle `0xC3` » → **FAUX**

J'avais remarqué `… 01 00 02 C3` en fin du premier bloc (code 0) et j'en avais déduit une trame
`[tag][16 o][5 mots][+1C][+1D][+1E][0xC3]`. Test sur les 96 : **16 seulement** finissent par `0xC3` à `+0x1F`,
**39 finissent par `0x00`**. La trame fixe n'existe pas.

### c) « Les pointeurs sont des adresses linéaires » → **NON TRANCHÉ** (voir § 3)

## 3. Le verrou, précisément

`mov r0, [0xCCB2 + 2·code]` place dans `r0` une valeur comme `0xA1A8`. Pour lire `[r0+#1Ch]` il faut savoir
**quel DPP est actif** à cet instant :

| convention | adresse obtenue | résultat |
|---|---|---|
| `fo = pointeur` | `0xA1A8` | contenu = **du code** (`DA 08 16 8C F6 28 …`) |
| `fo = pointeur + 0x80000` | hors fichier | inaccessible (pointeur > `0x80000` − 32) |
| `EA = (0x3A<<14) | 0x21A8` | `0xEA1A8` | contenu plausible (`03 06 00 00 … 0F10 0F00 …`) mais la trame ne tient pas |

**Et le point bloquant est localisé** : `sub_CEC02` (qui contient les lectures `[r0+#1Ch]`, `[r0+#1Dh]`,
`[r0+#1Eh]` aux l. 231251, 231257, 231265) **n'exécute aucun `scxt DPP`** ⇒ il hérite du DPP de son appelant.
Il faut donc remonter la chaîne `sub_CEC02` ← `seg016:F362` (appel depuis le **milieu** d'une fonction, donc
pas de convention) pour trouver le `scxt DPPx` qui fixe la page.

**Comparaison utile :** deux routines voisines, elles, fixent explicitement leur page :
`sub_CFF64` et `sub_CEC02`-voisin font `scxt DPP2, #24h` (l. **233064**, **233137**) ⇒ page `0x90000`.
C'est la preuve que **ce firmware résout bien ses données par DPP**, et que la page change d'une routine à
l'autre. C'est pourquoi je ne veux pas deviner.

## 4. Ce que je ne prétends pas

- Je **ne prétends pas** avoir lu les seuils de maintien par défaut. Les octets `+0x1C`/`+0x1D`/`+0x1E`
  existent et sont bien comparés aux octets `+6`/`+4`/`+5` de l'enregistrement de défaut (preuve :
  l. 231251-231292), mais **je ne peux pas encore dire quelles valeurs du fichier y correspondent**.
- La longueur des listes est calculée par « pointeur suivant − ce pointeur » : c'est une **borne supérieure**
  (des listes peuvent se chevaucher).

## 5. Consignation

- **`CATALOGUE_MAITRE.md` § 13 B.16** (2 383 → **2 417 lignes**).
- `defauts_96_listes.csv` (96 listes, 1 277 pointeurs) et `defauts_96_descripteurs.csv`.

## 6. Prochain pas — un seul, court et décisif

**Trouver le `scxt DPPx` de la chaîne d'appel de `sub_CEC02`.** Trois commandes suffisent : localiser le
début de la fonction contenant `seg016:F362`, lire ses 10 premières lignes, et repartir du `scxt DPP` trouvé.
Une fois la page connue, les 1 277 pointeurs se résolvent **d'un coup**, et les seuils `+0x1C`/`+0x1D`/`+0x1E`
des 96 codes tombent avec eux.

Je le fais maintenant si tu veux — c'est la dernière marche avant les seuils.
