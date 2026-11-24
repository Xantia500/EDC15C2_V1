# ÉTAPE 75 — Le vocabulaire des grandeurs : 92 identifiants catalogués, et la trame commune enfin établie

> Tu as raison : **tous les DTC y sont**, beaucoup avec **8 mots de données à zéro** (la condition se réduit
> au code lui-même), et le comptage se fait **sur le DTC directement** — le record étant en flash, il est
> incrémenté dans son miroir RAM. Et en suivant ta piste, j'ai trouvé **le catalogue des identifiants**.

---

## 1. Le point qui ferme la boucle : une seule trame de 32 octets

À **`EA 0xEA1A8`**, exactement le même format que les records DTC — mais le premier mot n'est pas un code DTC :

```
EA 0xEA1A8 : 0603 0000 0000 0000 0000 0000 0000 0000
EA 0xEA1B8 : 0000 0000 0F10 0F00 0F65 0F8C 0F7F 0001
EA 0xEA1C8 : C302 ...
```

| offset | contenu |
|---|---|
| `+0x00` | **code interne** (`0603`) — là où un record DTC porte son code DTC |
| `+0x12` | 5 identifiants |
| `+0x1C` | classe (bits 0-1) |
| `+0x1D` | seuil A |
| `+0x1E` | seuil B |
| `+0x1F` | sentinelle `0xC3` |

**C'est exactement le descripteur lu aux étapes 69-72** via `0xCCB2 + 2·index`. Donc :
**les conditions de maintien d'un défaut et les records DTC partagent la même trame de 32 octets.**
La seule différence est la nature du premier mot — code interne d'un côté, code DTC de l'autre.

C'était le chaînon manquant entre « la table des DTC » et « les seuils de maintien ». Il n'y a pas deux
mondes : c'est **un seul format**, utilisé deux fois.

## 2. ★ Le catalogue des identifiants — `EA 0xEA254` → `EA 0xEA30A`

Une liste **continue de 92 mots** : le vocabulaire complet des grandeurs.

```
0F12 0F02 0F61 0F60 0FFA 0FF8 0FF9 0FF6 0FF7 0F63 0FFC 0F00 0F70 0F71 0F6F 1F50 1001 1005 0FD6
0F7F 0F7C 0F40 0F42 DF11 DF12 0F30 0F32 DF13 DF14 0F64 1E80 0F80 DC86 0F8D DC87 0F8C 0F82 0F8B
0F8F 0F96 0F8A 0F83 1F80 1F81 1F82 1F83 1F58 1F55 1F56 0FD7 0F10 1F53 1F63 1F64 1F5E 1F5F 1F78
1F79 1F7A 1F7B 0EA4 0E80 0E87 0EA5 0E81 1F42 1F41 1F4D 1F4E 1F4F 1F51 0F10 0F08 E4DC E4DD 0FFB
1114 E4D0 0F01 E4E1 E4D6 E4D2 E4D8 E4DE E4DF 0F00 E4D5 E4D1
```

**Trois preuves convergentes :**

1. Tous les identifiants des records DTC s'y retrouvent (`0F10 0F30 0F32 0F64 0FFC 0EA5 …`).
2. Les 20 valeurs de `word_1424` (`0xE11C4`) en sont un **sous-ensemble** (`0F61 0FFA 0F80 0F64 0F7F 0F08 0F8A …`).
3. ★ **`0E80`**, l'identifiant propre à l'EGR, est là : **`EA 0xEA2D6`**, entouré de `0EA4 0E87 0EA5 0E81` —
   un **groupe de cinq identifiants `0x0Exx`**, le bloc EGR / pression.

**Livrable : `identifiants_grandeurs.csv`** (92 lignes : position, EA, identifiant, octet haut, octet bas).

## 3. Sur « 0 données » et l'incrémentation directe

La grande majorité des records ont leurs 8 mots de données à `0000` : la condition se réduit au code.
Comme le record est en **flash**, l'incrémentation ne peut pas se faire sur place — elle se fait dans le
miroir RAM : **`0xCAD0 + 4·code`** (état) et **`0xFD21 + code`** (bits). Les **39 records à mots non nuls**
sont ceux qui portent des conditions supplémentaires.

## 4. Bilan de la chaîne, maintenant complète

```
catalogue d'identifiants   EA 0xEA254 (92 mots)      ← LE VOCABULAIRE
        │
        ▼
records (trame 32 o)  ├─ codes DTC     EA 0xE0B10-0xE4F52   (93 relevés)
                      └─ codes internes EA 0xEA1A8+           (descripteurs 0xCCB2)
        │
        ├─ 5 identifiants par record = les grandeurs surveillées
        ├─ classe + seuil A + seuil B = les conditions de maintien
        ▼
état RAM  0xFD21 + code  /  0xCAD0 + 4·code
        ▼
réponse diagnostic  0x0000 / 0xFFFF  (tables 0xE11A0 / 0xE117C)
```

## 5. Consignation

- **`CATALOGUE_MAITRE.md` § 13 B.21** (2 712 → **2 766 lignes**) : trame commune, catalogue des 92 identifiants.
- `identifiants_grandeurs.csv`, `records_DTC_segmentE.csv`.

## 6. Prochain pas — le dernier chaînon

**Nommer les identifiants.** Le catalogue donne le vocabulaire ; il reste à savoir **ce que désigne
`0E80`, `0EA5`, `0F30`, `0F32`, `0F80`**. Méthode : chercher dans le code les routines qui lisent une valeur
*par identifiant* — c'est-à-dire les services de diagnostic qui prennent un identifiant en argument
(`sub_B7FAC`, `sub_BDE66`, `sub_BDD60`, repérés dans `sub_BE2BA`) et voir **quelle RAM** elles lisent.
Le bloc `0x0Exx` étant contigu, nommer un seul des cinq donnerait les autres par proximité.
