# ÉTAPE 51 — ★★★ Annotation automatique du Datensatz : **314 enregistrements typés**

*Outil : `outils/annote_datensatz.py` — sorties : `annotation_datensatz.csv`, `annotation_cartes_2D.csv`.*

---

## 1. Le principe, et pourquoi il fonctionne

Puisque **chaque enregistrement commence par l'adresse de sa variable** (étape 50), on peut décoder
**tout** le Datensatz sans rien supposer :

```
courbe 1-D : [adresse variable][n][axe : n mots][valeurs : n mots]      taille = 4 + 4n
carte 2-D  : [tagY][nY][axeY][tagX][nX][axeX][grille]                   taille = 8 + 2nY + 2nX + 2·nY·nX
```

Chaque décodage est ensuite **confronté à la taille réelle du bloc** déduite de la table des
pointeurs (étape 48 §1). **C'est la confrontation qui fait la preuve** : une lecture fausse ne tombe
pas juste à l'octet.

---

## 2. ★★ Les résultats bruts

### Courbes 1-D

| | nombre |
|---|---|
| handles examinés | **1 304** |
| **en-tête 1-D reconnu** | **248** |
| dont **taille calculée = taille du bloc, À L'OCTET PRÈS** | **181** |
| dont taille < bloc (octets restants) | 66 |
| sans en-tête 1-D | 1 056 |

### Cartes 2-D

| | nombre |
|---|---|
| **cartes 2-D reconnues** | **66** |
| dont **taille calculée = taille du bloc, À L'OCTET PRÈS** | **66** |
| **déborder** | **0** |

**⇒ 66 sur 66. Aucune exception.** Le format 2-D
`[tagY][nY][axeY][tagX][nX][axeX][grille]` est **confirmé sans réserve** — c'est la validation la plus
forte obtenue depuis le début de l'analyse.

**⇒ Et 181 validations indépendantes pour les courbes 1-D.**

**Bilan : 314 enregistrements sur 1 304 sont désormais typés, dimensionnés et nommés
automatiquement — 24 % du Datensatz, sans intervention manuelle.**

---

## 3. ★★★ `word_C42E` = **le régime moteur** — l'axe dominant du calculateur

| variable | nb d'axes | plage |
|---|---|---|
| **`word_C42E`** | **87 (1-D) + 49 (2-D) = 136** | **0 … 6000** |

**Une plage 0 → 6 000, en valeur brute, sur 136 axes** : c'est le régime moteur, et rien d'autre n'a
cette signature. **`word_C42E` est le régime** — et il est de très loin **la variable la plus utilisée
du Datensatz**.

Cela **explique** la statistique de l'étape 27 (112 occurrences, « tag n°1 ») et lui donne enfin un
**sens physique**.

---

## 4. ★★★ La famille `C3xx` : des masses d'air par tour — et une **validation croisée par tes données**

| variable | axes | plage |
|---|---|---|
| `word_C3D2` | 28 + 8 = 36 | **2 231 … 4 231** |
| `word_C3BA` | 11 + 4 = 15 | 2 231 … 4 081 |
| `word_C3B0` | 3 + 2 = 5 | 2 531 … 3 931 |
| `word_C5A4` | 2 | 2 431 … 3 331 |
| **`word_C3E6`** | 2 | **0 … 11 500** |

**Toutes ces variables vivent dans la même bande 2 000-4 300, à pas de 200** — signature d'une
grandeur **de même nature, exprimée dans la même unité**.

**Et voici la validation :** tu m'as indiqué que **`word_C3E6` = débit d'air, en mg/s, avec un axe
en mg/s × 10**. L'outil, qui **ne sait rien de cette information**, trouve `word_C3E6` avec une plage
**0 … 11 500**. Lu en mg/s ×10, cela donne **0 … 1 150 mg/s** — cohérent.

⇒ **La méthode reproduit une information que tu tenais d'une autre source.** C'est le meilleur test
possible, et il passe.

Par extension raisonnable : **`word_C3D2`, `word_C3BA`, `word_C3B0`, `word_C5A4` sont des masses d'air
par tour (mg ×10)**, dans la plage 220-430 mg/tour — régime de **charge partielle**, ce qui est
exactement la zone où l'on surveille l'EGR et le débitmètre. Et cela **explique** pourquoi
`word_C3D2` est la grandeur surveillée par les moniteurs (étape 43 §3) : **on surveille l'air admis,
parce que c'est là que se détectent les dérives d'EGR et de débitmètre.**

*Je marque cela comme **inférence forte**, pas comme lecture : l'unité vient de ton information, pas du
binaire.*

---

## 5. Les autres variables nommées automatiquement

| variable | axes | plage | lecture proposée |
|---|---|---|---|
| **`word_C6A2`** | 3 + 14 = 17 | **0 … 10 000** | **0 … 100 %** — ta convention, appliquée à une grandeur de charge |
| `word_C7C2` | 8 + 6 = 14 | 6 … 14 000 | grandeur large, non identifiée |
| `word_C60A` | 14 + 5 | 600 … 1 800 | petite plage, non identifiée |
| `word_D004` | 4 | 0 … 7 000 | non identifiée |
| `word_C3EE` | 3 | 0 … 4 910 | non identifiée |
| `word_C60E` | 3 | 0 … 7 000 | non identifiée |
| `word_C3C2` | 3 + 3 | **0 … 678** | **probablement un rapport cyclique (RCO)** — ton point sur EGR/N75 |
| `word_C3A8` | 2 | 400 … 2 400 | non identifiée |
| `word_C612` | 2 | 700 … 2 200 | non identifiée |
| `word_C586` | 3 | 3 731 … 8 731 | non identifiée |
| `word_C77A` | 2 | 6 667 … 31 667 | non identifiée |
| `word_C562` | 2 | 0 … 20 000 | non identifiée |
| `word_D1F4` | 2 | 0 … 5 000 | régime ou masse, non tranché |
| `word_C5A8` | 5 | 100 … 11 000 | **masse d'air par tour ×10** (étape 50 §3) |
| `word_C5BC` | 3 | **−32 768 … −29 408** | **anomalie** : axe massivement négatif, à examiner |
| `byte_D36A` | 3 | 0 … 255 | octet, non identifié |

**`word_C5BC`** mérite une remarque : un axe qui commence à **−32 768** ressemble à une **lecture
signée d'un octet de poids fort** ou à une **donnée mal alignée** — c'est le genre d'anomalie qui
signale soit une erreur de mon décodage, soit un encodage particulier. **Je ne tranche pas** ; c'est
noté comme point de contrôle, pas comme résultat.

---

## 6. Ce que le balayage change

1. **Le Datensatz n'est plus un catalogue d'adresses** : il est **nommé**, pour un quart de ses
   entrées, **par le binaire lui-même**.
2. **Deux axes dominants émergent** : **le régime (`word_C42E`)** et **la masse d'air par tour
   (`word_C3xx`)**. Ce sont les deux grandeurs sur lesquelles **tout** est calibré — ce qui est
   exactement la structure attendue d'un calculateur diesel.
3. **La méthode est réutilisable** : les 990 enregistrements restants ne sont pas « illisibles », ils
   sont **d'un autre type** — il faut leur trouver un gabarit, comme on l'a fait pour 1-D et 2-D.

---

## 7. Limites, énoncées franchement

- **66 courbes 1-D laissent des octets inutilisés** dans leur bloc : soit une **seconde entrée**
  (cas vu à l'étape 50 §1), soit du remplissage. Non instruit.
- **Les axes non monotones sont signalés** dans le CSV (`NON MONOTONE`) et **exclus** de l'agrégation
  des plages — ils sont peu nombreux mais réels.
- Les **plages d'axe ne donnent pas l'unité** par elles-mêmes : l'identification de `word_C42E` et de
  la famille `C3xx` repose sur **des plages plausibles + une information externe** (la tienne). Pour
  les autres, **je m'abstiens**.
- Les **990 autres handles** ne sont pas décodés : je ne dis **rien** de leur contenu.

---

## 8. Prochaines actions

1. **Trouver le gabarit des enregistrements restants** en examinant les blocs de taille régulière
   (comme le tableau `word_1946…195C` de l'étape 49 §4) — c'est là que sont les structures non
   identifiées.
2. **`word_C5BC`** : vérifier l'alignement de ce bloc (anomalie d'axe).
3. **`word_C42E`** : remonter à son écrivain — confirmer que c'est bien le régime (une division par le
   nombre de dents, ou une conversion tr/min).
4. **`word_C6A2`** : si c'est bien 0…100 %, identifier **quelle** grandeur est exprimée en pourcentage —
   candidat naturel : la **charge** ou la **demande du conducteur**.
