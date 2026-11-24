# ÉTAPE 118 — Révision critique : le format réel des tables, et ce que j'ai eu tort d'affirmer

Ta critique était fondée. Ce document **corrige** l'Étape 116 et établit le format canonique
par la preuve.

---

## 1. ★ ERRATA E27 — ce que je retire

**J'ai présenté les deux blocs `0xE2078` / `0xE211A` comme des « cartes couple → IQ avec un axe X de
8 points ». C'était une hypothèse de découpage, pas un fait.** Deux affirmations tombent :

| affirmation (Étape 116) | statut |
|---|---|
| « axe X = 8 points `1460…17920` » | ❌ **non prouvé** — aucun tag, aucun `n` |
| « ce sont des cartes de conversion couple → débit » | ❌ **sur-interprétation** |
| « 7 lignes × 8 colonnes » | ⚠️ découpage arithmétique exact (162 o) mais **syntaxe non conforme** au format du dump |
| « les valeurs sont du couple en 0,01 N.m » | ❌ **hypothèse abandonnée** |

**Et tu as raison sur le fond** : cet ECU travaille en **mm³ d'IQ**, point. Une grandeur de « couple »
n'y a pas sa place comme entrée de carte.

---

## 2. ★★★ Le format canonique, démontré

Une carte de calibration de ce dump se lit ainsi :

```
[ tag variable d'axe ] [ n ] [ axe : n points ] [ 0 séparateur ] [ valeurs : n points ]
```

**Preuve** — zone `0xE83EC` :

```
0xE83F4 : 50222 (=0xC42E)  19           ← tag RÉGIME, 19 points
0xE83F8 : 0  50  800  1000  1250  1500  1750  2000  2250  2500  2750  3000
0xE8414 : 3500 3750 4000 4250 4500 4800 5200    ← axe complet (19 valeurs)
0xE841E : 0                                     ← séparateur
0xE8420 : 3516 3516 4485 5800 6660 7060 7430 7280 7060 6870 6810 6440 6270 6240 5690 5300 4750
```

⇒ **voilà ta carte 19×1 sur axe RPM, valeurs en mm³.** ✔

**Et c'est exactement ce que `main_torque = 0xE841E` désigne** : non pas une carte, mais le
**bloc de valeurs** de cette courbe (d'où le `0` du séparateur en tête).

## 3. ★★★ La courbe de couple plein gaz, en clair

Axe = **régime (tr/min)**, valeurs = **IQ en 0,01 mm³** (3516 = 35,16 mm³ ; 7430 = 74,30 mm³) :

| régime | 0 | 50 | 800 | 1000 | 1250 | 1500 | 1750 | 2000 | 2250 | 2500 |
|---|---|---|---|---|---|---|---|---|---|---|
| **IQ** | 35,2 | 35,2 | 44,9 | 58,0 | 66,6 | 70,6 | **74,3** | 72,8 | 70,6 | 68,7 |

| régime | 2750 | 3000 | 3500 | 3750 | 4000 | 4250 | 4500 | 4800 | 5200 |
|---|---|---|---|---|---|---|---|---|---|
| **IQ** | 68,1 | 64,4 | 62,7 | 62,4 | 56,9 | 53,0 | 47,5 | — | — |

**Le maximum est à 1750 tr/min : 74,3 mm³.** C'est la courbe de plein gaz d'un 2.2 HDi — la forme est
parfaitement caractéristique (montée, plateau 1750-2500, décroissance).

## 4. Les autres courbes de la même famille

| adresse | `n` | axe (tr/min) | valeurs (0,01 mm³) | lecture |
|---|---|---|---|---|
| `0xE83F4` | 19 | `0 · 50 · 800 · 1000 · 1250 … 5200` | 3516 → **7430** → 4750 | plein gaz |
| `0xE8928` | 15 | `635 · 680 · 800· 1000 · 1250 …` | 3516 · 3516 · 3516 · 4485 · 5800 · 6660 · 6400 · 6350 · 6300 · 6330 · 6400 · 6500 · 6440 · 6270 · 6240 | courbe décalée (départ 635 tr/min) |
| `0xE8968` | 15 | idem | **identique** à `0xE8928` | doublon |
| `0xE89A8` | 12 | `0 · 300 · 1200 · 1600 · 2000 · 2400 · 3200 · 3600 · 4050 …` | **10000 partout** = **100 mm³** | **sentinelle « pas de limitation »** |

★ **`10000` = 100 mm³ est le code « aucune limitation »** dans cet ECU (au-dessus de tout IQ
atteignable). On le retrouve partout dans cette zone, y compris juste avant nos blocs
(`0xE2060` : `10000 10000 …`).

## 5. Ce que deviennent alors mes « cartes 7×8 »

Replacés dans le format canonique, les blocs `0xE2078` / `0xE211A` sont **anormaux** :

| critère du format | `0xE2078` / `0xE211A` |
|---|---|
| tag de variable (`0xC42E`, `0xC562`…) | ❌ **absent** (10 mots à zéro) |
| champ `n` | ❌ absent |
| séparateur `0` unique | ❌ il y en a **7** (un par ligne) |
| valeurs contiguës | ❌ entrecoupées |

**Hypothèse la plus vraisemblable, reformulée** : ce ne sont **pas des cartes 2-D à deux axes
interpolés**, mais des **jeux de 7 courbes partageant un même axe de 8 points** (format
« Kennlinien-Satz » propre à la bibliothèque). Autrement dit :

> **il y a bien une table, mais une seule entrée est interpolée (X) ; les 7 lignes sont des courbes
> discrètes, sélectionnées par un index, pas interpolées.**

C'est cohérent avec l'absence d'axe de lignes. **Mais cela reste une hypothèse** — je ne la présente
plus comme un fait.

## 6. Ce que la correction t'apporte concrètement

| avant (Étape 116) | maintenant |
|---|---|
| « cartes couple → IQ, unité 0,01 N.m » | ❌ retiré |
| « limitation par RPM en mm³ » | ✅ **confirmé et chiffré** |
| « 7×8 cartes 2-D » | ⚠️ **jeu de 7 courbes sur axe partagé** (hypothèse) |
| — | ✅ **format canonique `[tag][n][axe][0][valeurs]` établi par la preuve** |
| — | ✅ **`10000` = sentinelle « pas de limitation » (100 mm³)** |

Et surtout : la **vraie** chaîne de limitation que tu décrivais existe bien, et elle est en **mm³** :

```
souhait (mm³) ─→ arbitrage régulateur ─→ limiteurs ─→ correction ─→ C6B2 (mm³)
                                          ↑
                                   courbes sur axe RPM, valeurs en mm³
                                   (0xE83F4, 0xE8928, 0xE89A8 …)
                                   10000 = aucune limitation
```

## 7. Ce qu'il reste à faire, dans le bon ordre

1. **Nommer chaque courbe** de la zone `0xE83xx-0xE89xx` : pour chacune, remonter le **handle** qui la
   désigne et le **site d'appel** qui l'utilise → on obtient « quelle courbe = quel limiteur »
   (plein gaz, fumée, 1re/2de, etc.).
2. **Trancher le statut des blocs 162 octets** : chercher si leur 1er mot (toujours `0`) est utilisé
   comme **index de sélection** dans les sites d'appel — c'est vérifiable.
3. Une fois (1) et (2) faits, on saura **exactement** quelles cases toucher pour un objectif donné,
   et en mm³.

> Bilan honnête : l'Étape 116 a produit un découpage arithmétiquement exact mais **sémantiquement
> faux**. Ta lecture — limitation par régime, en mm³ — est celle que le binaire confirme.
