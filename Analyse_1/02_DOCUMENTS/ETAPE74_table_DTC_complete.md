# ÉTAPE 74 — La table des codes DTC « en clair » : 93 records, et l'EGR y est en toutes lettres

> Ta description était juste sur les trois points : **code en clair** (`0x1169` = P1169), **8 ou 16 mots**,
> **en bas du segment E**. Voici la table complète, et ce qu'elle dit de l'EGR et du FAP.

---

## 1. Où c'est exactement

```
EA = 0xE0000 | (pointeur & 0x3FFF)
offset fichier = 0x60000 + (EA - 0xE0000)
```

Les records occupent **`EA 0xE0B10` → `EA 0xE4F52`**, soit **offset fichier `0x60B10` → `0x64F52`**.
C'est bien « en bas » du segment E, pas à `0x60000` exactement — ta nuance était la bonne.

## 2. Format du record

| offset | contenu | taille |
|---|---|---|
| `+0x00` | **code DTC en clair** (`1169` = P1169) | 2 o |
| `+0x02` … | **mots de données / seuils** (souvent à 0) | 8 mots (16 o) — variante 16 o : 7 mots |
| `+0x12` … `+0x1B` | **5 identifiants de grandeurs** (`0x0Fxx`, `0xE4xx`) | 10 o |
| `+0x1C` | **classe** (0…3) | 1 o |
| `+0x1D` | **seuil A** | 1 o |
| `+0x1E` | **seuil B** (`0xFF` = jamais de guérison) | 1 o |
| `+0x1F` | **sentinelle `0xC3`** → le mot final est `0xC3xx`, `xx` = seuil B | 1 o |

**Deux tailles : 32 octets = 16 mots** (73 records) et **16 octets = 8 mots** (20 records).

## 3. Ce que contient la table

93 records, dont les codes forment une liste parfaitement cohérente avec ton calculateur :

`P0100 P0101 P0102 P0104 P0105 P0106 P0110 P0115 P0121 P0148 P0170 P0180 P0190 P0191
P0201 P0202 P0203 P0204 P0221 P0303 P0381 P0384 P0401 P0402 P0403 P0417 P0470 P0477
P0503 P0504 P0530 P0560 P0568 P0571 P0600 P0604 P0700 P0707 P0960 P1000 P1001 P1003
P1101 P1107 P1108 P1109 P1110 P1135 P1168 P1169 P1170 P1300 P1402 P1403 P1404 P1421
P1425 P1429 P1435 P1442 P1446 P1451 P1458 P1517 P1521 P1537 P1601 P1606 P1608 P1614
P1770 P2304 …`

## 4. ★ L'EGR, en toutes lettres

| DTC | EA | offset fichier | identifiants | lecture |
|---|---|---|---|---|
| **P0401** | `0xE3E9C` | `0x63E9C` | `0F10 0F32 0E80 0F30 0F80` | EGR : **débit insuffisant** |
| **P0402** | `0xE3EBC` | `0x63EBC` | `0F10 0F32 0E80 0F30 0F80` | EGR : **débit excessif** |
| **P0403** | `0xE3D96` | `0x63D96` | `0F10 0F32 0E80 0F30 0F80` | EGR : **circuit** |
| **P0470** | `0xE304A` | `0x6304A` | `0F10 0F41 0F40 0F42 0F7F` | capteur de pression d'échappement (**FAP**) |
| P0190 / P0191 | `0xE3282` / `0xE4A70` | | `0F10 0F64 2066 0FFC 0EA5` | pression de rampe |
| P1168 / P1169 / P1170 | `0xE3230` / `0xE3734` / `0xE3754` | | `0F64 0EA5 0FFC …` | famille PSA rampe/dose |

**Les trois codes EGR partagent exactement les cinq mêmes identifiants** : `0F10 0F32 0E80 0F30 0F80`.
Et **`0E80` n'apparaît que là** — c'est l'identifiant de la grandeur propre à l'EGR. C'est un point
d'entrée concret pour toi : `0E80` est la variable à suivre quand tu touches à l'EGR.

La famille PSA vanne/dose (`P1401`→`P1404`, `P1421/1425/1429`, `P1435`, `P1442/1446`, `P1451/1458`)
utilise, elle, des identifiants **`0xE4xx`** — un autre groupe de grandeurs, distinct.

## 5. Constat négatif — et je le consigne pour ne pas y revenir

Sur les **1 277 pointeurs** des 96 listes (étape 70), seuls **36 tombent sur un début de record**.
⇒ **Les 96 listes ne sont pas l'index des records DTC.** Piste fermée.

## 6. Ce que je n'ai pas encore

- **Le balayage n'est pas exhaustif** : 93 records détectés, mais beaucoup se confondent avec des courbes
  (les mots de données ressemblent parfois à des codes valides). Un relevé manuel de la page serait plus sûr.
- **Les 8 mots de données `+0x02…+0x11`** : 39 records en ont des non nuls. Certains sont manifestement des
  **drapeaux binaires** (`0001 0000 0101 0101 0100 0202` pour P0100), d'autres des valeurs
  (`0001 0798 1117 01F4 0C02 00F8` pour P0105). À décoder.
- **Comment le firmware retrouve un record** à partir d'un code : la question reste ouverte.

## 7. Consignation

**Tout est dans le document maître, § 13 B.20**, avec la table des 93 records (EA, offset fichier, taille,
DTC, classe, seuil A, seuil B, identifiants) générée directement depuis le CSV.
Catalogue : 2 548 → **2 712 lignes**.

- `records_DTC_segmentE.csv` — 93 records complets.

## 8. Prochain pas

1. **Relever la page `0xE0B00`–`0xE5000` à la main** (16 Ko) pour ne rater aucun record : balayage par la
   sentinelle `0xC3` puis validation du code + des 5 identifiants.
2. **Décoder `0E80`** (grandeur EGR) et `0E91`/`0EA5`/`0E80`/`0E82` : ce sont les grandeurs qui relient les
   codes EGR/FAP aux mesures.
3. **Les drapeaux binaires** des 8 mots de données.
