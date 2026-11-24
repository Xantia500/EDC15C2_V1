# ÉTAPE 82 — ★ La valeur d'avance **est un identifiant exporté** (`0x1F4D`) · vérité sur la couverture · les 4 zones orphelines

> Deux résultats, et une correction de ma propre instrumentation — deux fois de suite, sur le même balayage.
> `D51A`, la sortie de la carte d'avance, porte l'**identifiant `0x1F4D`** : c'est pour cela qu'IDA ne voit
> qu'une écriture. Et le « cadastre » de la calibration est maintenant **complet et chiffré**.

---

## 1. ★ `D51A` = identifiant `0x1F4D`

`word_D51A` reçoit la valeur de la carte `0xE2816` (l.241052). Or dans le dictionnaire identifiant → RAM
(`EA 0x91204` / `0x914CC`, étape 76) :

```
0x1F4D  →  D51A
```

⇒ **la valeur d'avance est une grandeur mesurable et exportée**, pas une variable interne muette.
C'est l'explication du « mystère » de l'étape 81 : le code ne la relit jamais, il la **publie**.

`0x1F4D` figure aussi dans le **catalogue des 92 grandeurs** (`EA 0xEA254`, étape 75, position 71) :
elle est donc déclarée comme grandeur à part entière dans la trame de mesure.

### Le bloc « injection / pression » des identifiants

| identifiant | RAM | ce qu'on en sait |
|---|---|---|
| `0x1F40` | `C3AE` | — |
| `0x1F41` | `C73C` | voisin de `C73E` (un des 6 correctifs d'avance) |
| `0x1F42` | `D52A` | — |
| **`0x1F4D`** | **`D51A`** | **sortie de la carte d'avance `0xE2816`** |
| `0x1F4E` | `D520` | — |
| `0x1F4F` | `D51E` | — |
| `0x1F50` | `C736` | — |
| `0x1F51` | `D532` | — |
| `0x1F52` | `D54C` | — |
| `0x1F53` | `D570` | — |
| `0x1F55`/`0x1F56` | `C7DA` | deux identifiants, même adresse |
| `0x1F58` | `C7CC` | — |
| `0x1F59` | `C73E` | **un des 6 correctifs additives de l'avance** (l.241003) |
| `0x1F5A` | `D528` | — |
| `0x1F5B` | `D544` | — |
| `0x1F5E` | `C7B8` | — |
| `0x1F5F` | `C7C6` | — |
| `0x1F63` | `D574` | — |
| **`0x1F64`** | **`C78A`** | **l'axe à 18 points des grilles 14×18** (`0xE2B62`/`0xE2D5A`) |
| `0x2109` | **`C63C`** | **l'axe à 9 points de « pression rail »** (0 → 15360) |

**Conséquence pratique** : l'avance, la valeur de la carte, les axes `C78A` et `C63C` sont **lisibles au
diagnostic**. On peut donc les journaliser sur le véhicule pour lever l'unité (question restée ouverte
à l'étape 81) — en comparant la valeur live à une mesure externe.

### ⚠ Un piège d'adressage à noter

`sub_CD506` (l.227574) fait `add r0, #0D51Ah` puis `jmpi [r0]` : ici **`0x0D51A` est une base de table de
sauts dans le code**, pas l'adresse RAM `0xD51A`. Ne pas confondre.

## 2. ⚠ Correction : mon balayage de la table des handles était faux — deux bugs

| version | erreur | conséquence |
|---|---|---|
| 1ʳᵉ | filtre `ptr < 0x8000` | **tous les pointeurs ≥ 0x8000 éliminés** ⇒ la moitié haute du Datensatz (dont la carte de fumée `0xE8444`) « disparaissait » |
| 2ᵉ | boucle arrêtée à `0x1DFE` | ~25 handles perdus en fin de table |
| **3ᵉ (bonne)** | 1 305 entrées, handles `0x1400`–`0x1E2E` | **1 304 objets** distincts |

Chiffres définitifs :

| mesure | valeur |
|---|---|
| entrées de la table `0x61400` | **1 305** (handles `0x1400` → `0x1E2E`) |
| objets distincts dans le Datensatz | **1 304** |
| couverture | `EA 0xE100A` → **`0xEBC38`** |
| non couvert avant le 1ᵉʳ handle | `0xE0000`–`0xE1009` = 2 053 mots (**= les records DTC**, référencés autrement) |
| non couvert après le dernier | **448 mots** (`0xEBC38` → `0xEBFB9`) |

⇒ **la phrase « 8 157 mots non référencés » de l'étape 81 était un artefact**, pas une découverte.
La calibration est référencée à **99 %**.

## 3. Les 4 vraies zones orphelines (176 mots au total)

Objets dont la structure interne est plus courte que l'écart jusqu'au handle suivant :

| EA | handle | écart | structure | résidu | contenu du résidu |
|---|---|---|---|---|---|
| `0xE39C0` | `0x15EC` | 12 | 6 | **6** | (2 mots d'axe + valeurs) |
| `0xE6952` | `0x199C` | 66 | 18 | **48** | escalier **74 74 … 79 79 … 93 … 102 … 113 … 120** |
| `0xE6E7E` | `0x19FC` | 102 | 18 | **84** | `3500 4000 4500 5012` puis **3500 répété 80 fois** |
| `0xE868C` | `0x1B42` | 52 | 14 | **38** | `14016 18000 0` puis 4 lignes `0, X, X, X, X, X` avec X = **9230, 8150, 4210, 1280** |

Lecture proposée (hypothèses) :

- `0xE6976` : une **rampe 74 → 120** par paliers — soit une courbe de gain (×0,74 → ×1,20), soit les
  **valeurs** d'une courbe dont l'axe est ailleurs. 48 mots = 6 paliers × 8.
- `0xE6EA2` : une carte **saturée** à 3500 (le préfixe `3500 4000 4500 5012` ressemble à un axe régime
  à 4 points, le corps étant plat).
- `0xE86A8` : une carte à **5 colonnes et 4 lignes** (9230 / 8150 / 4210 / 1280), précédée de deux valeurs
  isolées (`14016`, `18000`). Elle est **juste avant la carte de préchauffage `0xE86F4`** — à instruire en
  priorité, c'est la zone que tu cherchais sur les bougies.

## 4. Où en est le cadastre

| couche | état |
|---|---|
| table des handles | **1 305 entrées, 1 304 objets, 99 % du Datensatz couvert** |
| cartes à en-tête (tag + n + axes) | 66 cartes 2-D + 182 courbes 1-D (comptage historique) |
| banque d'axes | 14 objets identifiés (`EA 0xE100A`–`0xE10F1`) |
| cartes **sans axes** | 16×16 (`0xE2816`) + 3× 9×9 + 2× 14×18 |
| zones orphelines | 4 zones / 176 mots (§ 3) + 448 mots en fin de segment |
| identifiants → RAM | 356 identifiants, dont le bloc injection `0x1F40`–`0x2109` |

## 5. Prochaines cibles

1. **Lire `0x1F4D` en live** et le comparer à une avance mesurée à la lampe → unité tranchée.
2. **`0xE86A8`** (38 mots, avant le préchauffage) : la zone la plus prometteuse restante.
3. Les **448 mots** de `0xEBC38`–`0xEBFB9` en fin de Datensatz.
4. Nommer `C63C` (0x2109) et `C78A` (0x1F64) par leurs consommateurs.

## 6. Consignation

**`CATALOGUE_MAITRE.md` § 13 B.28** — `D51A` = identifiant `0x1F4D`, bloc d'identifiants injection,
piège `#0D51Ah`, couverture recalculée (1 305 / 1 304 / 0xEBC38), les 4 zones orphelines avec leur contenu.
