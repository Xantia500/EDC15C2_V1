# ÉTAPE 73 — ★★★ Les codes DTC **en clair** : `[DTC][8 mots][5 identifiants][classe][seuil A][seuil B][0xC3]`

> **Tu avais raison, et c'est ta phrase qui a débloqué la situation.** « Un code écrit en clair, ex P1401
> ⇒ 0x1401 suivi de 8 ou 16 mots, taille variable » — c'est exactement la structure. Et « en début de
> segment E » aussi. Mon erreur était la résolution d'adresse : je cherchais page `0x3A`, il fallait lire
> **un offset dans la page de 16 Ko en tête du segment E**.

---

## 1. La résolution d'adresse correcte

```
EA = 0xE0000 | (pointeur & 0x3FFF)
```

C'est-à-dire : le pointeur est un **offset dans la page `0xE0000`–`0xE3FFF`**, celle qui commence au début du
segment E. Avec cette règle, tout s'aligne d'un coup.

## 2. La structure, sur l'exemple `P1169` / `P1170`

```
EA 0xE3730 : 0000 0045 1169 0000 0000 0000 0000 0000
EA 0xE3740 : 0000 0000 0000 0F10 0F65 0FF8 0FF9 0F80
EA 0xE3750 : 0003 C3FF 1170 0000 0000 0000 0000 0000
```

| offset | contenu | exemple `P1169` |
|---|---|---|
| `+0x00` | **code DTC en clair** (16 bits) | `1169` = **P1169** |
| `+0x02` … `+0x11` | 8 mots de données (16 octets) | `0000` ×8 |
| `+0x12` … `+0x1B` | **5 identifiants de grandeurs** `0x0Fxx` | `0F10 0F65 0FF8 0FF9 0F80` |
| `+0x1C` | **classe** (0…3) | `03` |
| `+0x1D` | **seuil A** | `00` |
| `+0x1E` | **seuil B** — `0xFF` = jamais de guérison | `FF` |
| `+0x1F` | **sentinelle `0xC3`** | `C3` |

**Record = 32 octets = 16 mots**, et le suivant commence immédiatement après : `0xE3754` = `1170` (P1170).
Une **variante de 16 octets** existe aussi (28 pointeurs vérifiés) — c'est le « 8 ou 16 mots » que tu décrivais.

**Détail élégant :** le dernier mot du record est `0xC3xx`, où `xx` **est** le seuil B. La sentinelle et la
dernière valeur sont dans le même mot.

## 3. Les records validés

43 records sur 1 277 candidats passent le test d'alignement (octet `+0x1F` = `0xC3`) **et** donnent un code
DTC plausible. Extrait :

| index | EA | DTC | classe | seuil A | seuil B | identifiants |
|---|---|---|---|---|---|---|
| 0 | `0xE2372` | **P1517** | 1 | 0 | 2 | `0F10 0F08 0F65 0F8C 0F7F` |
| 0 | `0xE2FCA` | **P1101** | 2 | 2 | 2 | `0F10 0F41 0F40 0F80 0F01` |
| 4 | `0xE3734` | **P1169** | 3 | 0 | 255 | `0F10 0F65 0FF8 0FF9 0F80` |
| 5 | `0xE3754` | **P1170** | 3 | 0 | 255 | `0F65 0F01 0FF8 0FF9 0F80` |
| 6 | `0xE3282` | **P0190** | 3 | 0 | 4 | `0F10 0F64 2066 0FFC 0EA5` |
| 9 | `0xE36AC` | **P0560** | 2 | 2 | 2 | `0F10 0F01 0F65 0F08 0F7F` |

Ces codes sont **cohérents avec ton calculateur** : P0190 (capteur de pression de rampe), P0560 (tension
système), P1169/P1170/P1101/P1517 (famille PSA : pression de rampe / dose / EGR), P0190…

**Livrable : `dtc_records_valides.csv`** — et `dtc_records_32o.csv` (les 1 277 candidats).

## 4. ★ Bonus : la dernière question ouverte tombe

Les identifiants de ces records sont `0F10 0F65 0F7F 0F64 0F08`… c'est **exactement l'alphabet de
`word_1424`** (`0xE11C4` : `0F10 0F61 0F80 0FFA 0F8B 0F30 0F32 0F60 0FFC 0F40 0F42 … 0F64 0F7F 0005 000F 0F65 0F08 0F8A`).

⇒ **`0x0Fxx` = identifiant de grandeur mesurée**, et `word_1424` est une **liste de 20 identifiants de
grandeurs**. Ce ne sont ni des adresses RAM, ni des indices.

Mon test « intersection vide » de l'étape 70 était **faux** : je comparais ces identifiants à des
**pointeurs** (0xA1A8…), pas à des identifiants. Corrigé.

## 5. Ce qui reste à faire, précisément

1. **Pourquoi seulement 43 records sur 1 277 s'alignent.** Trois causes possibles : variante 16 octets,
   pointeurs tombant au milieu d'un record, ou records d'un troisième type. **C'est le seul point qui
   limite l'extraction** — la structure, elle, est certaine.
2. **Les 8 mots `+0x02…+0x11`** : ils étaient tous à `0000` sur les exemples ; chercher ceux qui ne le sont pas
   donnera les seuils propres au code.
3. **Les identifiants `0x0Fxx`** : il faut maintenant les résoudre un par un (c'est là que se trouve la
   correspondance « défaut → grandeur mesurée »).

## 6. Consignation

- **`CATALOGUE_MAITRE.md` § 13 B.19** (2 500 → **2 548 lignes**).
- `dtc_records_valides.csv`, `dtc_records_32o.csv`.

## 7. Un mot sur la méthode

Ce bloc a été trouvé parce que **tu m'as donné la structure** (« code en clair + 8 ou 16 mots + variable,
en début de segment E »). Mes trois étapes précédentes cherchaient un mécanisme de pointeurs indirects ;
ta description a fourni le **format**, et le format a donné l'adresse. C'est la bonne façon de travailler
sur ce fichier : le format d'abord, l'adresse ensuite.
