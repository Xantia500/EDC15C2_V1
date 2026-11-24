# ÉTAPE 76 — ★★★★ Le dictionnaire identifiant → adresse RAM : 356 entrées, et six ancres qui tombent juste

> C'est le chaînon final, et il est **vérifié**. On peut maintenant traduire n'importe quel identifiant
> (`0E80`, `0F32`, `0F41`…) en **une adresse RAM précise**. Et **six ancres établies indépendamment**
> tombent exactement au bon endroit.

---

## 1. La table

| EA | contenu |
|---|---|
| `0x91202` | `0164` = **356** = nombre d'entrées |
| `0x91204` – `0x914CA` | **356 identifiants triés croissants**, `0x0004` → `0xE4EE` |
| `0x914CC` – `0x91791` | **356 adresses RAM** parallèles |
| `0x91794` … | un 3ᵉ tableau parallèle (`FF1C`, `C6CC`, `C476`…) non décodé |

Accès dans le code : **`sub_B7FAC` → `sub_CFEFA`** (page `0x24` = `0x90000`) = **recherche dichotomique**
de l'identifiant dans le tableau trié, puis lecture des tableaux parallèles.

**Livrables :** `identifiants_vers_RAM.csv` (356 lignes) et `dictionnaire_identifiants.csv`.

## 2. Vérification — six ancres indépendantes

| identifiant | adresse RAM | grandeur | statut |
|---|---|---|---|
| `0x0F00` | `0xC3D2` | **température LDR** | établie ✔ |
| `0x0F02` | `0xC3B0` | **température carburant** | établie ✔ |
| `0x0F10` | `0xC42E` | **régime moteur** | établie ✔ |
| `0x0F65` | `0xC3C2` | **RCO EGR** | établie ✔ |
| `0x0F8C` | `0xC6A2` | **charge %** | établie ✔ |
| `0xE4D2` | `0xC5A8` | **masse d'air / tour** | établie ✔ |

Six grandeurs que nous avions identifiées par des chemins totalement différents atterrissent sur les bons
identifiants. **Le tableau est bien « identifiant → adresse RAM ».** Plage : `0xC228` → `0xFF1C`,
334 adresses distinctes pour 356 identifiants (quelques alias — `0x000C` et `0x0F10` pointent tous deux `0xC42E`).

## 3. ★ Le groupe EGR, enfin nommé

| identifiant | RAM |
|---|---|
| **`0x0E80`** | **`0xC4B6`** |
| `0x0E81` | `0xC4E0` |
| `0x0E82` | `0xC4DE` |
| `0x0E87` | `0xC4D4` |
| `0x0E91` | `0xC4DC` |
| `0x0EA2` | `0xC4F6` |
| `0x0EA4` | `0xC4DA` |
| `0x0EA5` | `0xC4D6` |
| `0x0EA7` | `0xC4F4` |
| `0x0EA8` | `0xC4E8` |

⇒ **le bloc EGR vit en RAM `0xC4B6` – `0xC4F6`**, dix variables contiguës.

## 4. Les records DTC, traduits en adresses RAM

| DTC | identifiants → RAM | lecture |
|---|---|---|
| **P0401 / P0402 / P0403 (EGR)** | `0F10`→`C42E` **régime**, `0F32`→`C3EA`, **`0E80`→`C4B6`**, `0F30`→`C3E8`, `0F80`→`C68A` | le diagnostic EGR confronte le **régime** à l'état `C4B6` |
| **P0470 (pression d'échappement)** | `0F10`→`C42E`, `0F41`→`C60A`, `0F40`→`C612`, `0F42`→`C614`, `0F7F`→`C6E0` | trois adresses voisines `C60A`–`C614` = pression d'échappement |
| P0190 / P0191 (rampe) | `0F64`→`C3A8`, `0EA5`→`C4D6`, `2066`→`C376`, `0FFC`→`C3AC` | |

**Deux conséquences directes pour ton travail :**

- Pour l'**EGR**, la grandeur propre au diagnostic (`0E80`) est **`0xC4B6`**, et tout son contexte est en
  `0xC4B6`–`0xC4F6`. C'est une zone de dix octets à surveiller, pas une carte perdue dans le Datensatz.
- Pour le **FAP**, le capteur de pression d'échappement (P0470) travaille sur **`0xC60A`–`0xC614`**.

## 5. Où en est la cartographie

```
dictionnaire identifiant→RAM  EA 0x91204 (356)      ← dernière pièce
        ↓
records 32 o (DTC + internes) → 5 identifiants
        ↓
dictionnaire → 5 adresses RAM par défaut
        ↓
état 0xFD21 / 0xCAD0+4·code  →  réponse diag 0x0000/0xFFFF (+ tables 0xE11A0/0xE117C)
```

## 6. Ce qui reste

1. **Le 3ᵉ tableau parallèle** (`0x91794`) : il contient `FF1C`, `C6CC`, `C476`… et semble mêler une valeur
   constante et des adresses. Probablement le **format / l'unité / la validité** de chaque grandeur.
2. **Nommer les dix variables `0xC4xx`** : leur contiguïté et leur usage EGR sont acquis, leur sens individuel
   ne l'est pas. `0xC4B6` est la première à instruire.
3. **Les alias** (`0x000C` et `0x0F10` → `0xC42E`) : dire pourquoi deux identifiants désignent la même variable.

## 7. Consignation

**`CATALOGUE_MAITRE.md` § 13 B.22** — dictionnaire complet, vérification par six ancres, groupe EGR nommé,
records DTC traduits en adresses RAM. Catalogue : 2 766 → **2 824 lignes**.
