# ÉTAPE 57 — Tables oubliées : recherche systématique, et **le Datensatz existe en deux exemplaires**

> **Ta mise en garde était juste, et elle a corrigé une erreur réelle du catalogue.** Voir § 1.

---

## 1. ⚠ D'abord la correction : **une plage ne prouve rien**

Tu avais raison : 2 200 … 4 300 n'est pas une signature de température. C'est aussi bien :

- une température en K × 10 → **−50 … +150 °C** ;
- une masse d'air par tour en mg × 10 → **220 … 430 mg** ;
- un régime partiel → **2 200 … 4 300 tr/min**.

Or le catalogue (et moi, à l'étape 56) avais nommé `word_C3D2`, `word_C3BA`, `word_C3B0`
« température » **sur la foi de leur plage**. Le générateur contenait même **deux annotations
contradictoires** pour ces trois variables : `UNIT` disait « masse d'air par tour (mg × 10) »,
`AXES` disait « température ». Les deux ne pouvaient pas être vrais.

**Ce qui tranche, ce n'est pas la plage, c'est la chaîne.** L'étape 13 a établi :

```
voie 11 → courbe 0xE3842 → word_D084 → word_C3D2 → word_C908 → moniteur
voie 6  → courbe 0xE3548 → word_D06C → word_C3BA → word_C904 → word_D094
voie 7  → courbe 0xE3444 → word_D05E → word_C3B0 → word_C900
```

**Conclusion conservée** : ce sont bien des températures — mais **parce que la chaîne capteur est
identifiée**, pas parce que la plage y ressemble. `UNIT` a été corrigé, et l'erreur est inscrite au
registre des erratas sous le n° 56, avec sa leçon de méthode.

**Règle adoptée dans tout le catalogue :** un axe n'est nommé que si **la chaîne qui le produit** est
identifiée. La plage ne sert qu'à **vérifier la vraisemblance** — jamais à conclure. Et quand seule la
plage est disponible, le nom reste « grandeur non identifiée ».

C'est pour cette raison que `word_C5A4` et `word_C586` restent marqués **« échelle non tranchée »** :
on a la plage, pas la chaîne.

---

## 2. ★★ Le Datensatz est stocké en **DEUX exemplaires complets**

Comparaison octet par octet de `0xE0000-0xEBFFF` et `0xF0000-0xFBFFF` :

> **49 138 octets identiques, 14 différents, répartis en 5 endroits.**

Ce ne sont donc pas deux zones distinctes : **c'est la même calibration, écrite deux fois.**

| exemplaire E | exemplaire F | taille | E | F | lecture |
|---|---|---|---|---|---|
| `0xE0FF6` | `0xF0FF6` | 4 o | `3d d3 3d d3` | `c3 c3 00 00` | champ de contrôle n°1 — **renseigné** en E, **remplissage** en F |
| `0xE0FFC` | `0xF0FFC` | 4 o | `c9 32 05 b2` | `d4 cd c0 17` | champ de contrôle n°2 |
| `0xE434D` | `0xF434D` | 1 o | `23` | `03` | un octet de calibration diffère |
| `0xEBCFC` | `0xFBCFC` | 4 o | `dd 35 d9 5b` | `20 5c 77 af` | champ de contrôle de **queue** |
| `0xEBF1B` | `0xFBF1B` | 1 o | `57` « **W** » | `46` « **F** » | dans la chaîne `__N**x**GDWPF1` |

### Trois lectures

**1. `0xE0FF6` et `0xE0FFC` sont deux champs de contrôle en tête du Datensatz.** En E ce sont des
valeurs concrètes (`0xD33D` **deux fois**, puis `0xB20532C9`) ; en F, les deux mots valent `0xC3C3` et
`0x0000`, c'est-à-dire **le remplissage**. **⇒ E est l'exemplaire actif ; F est un miroir dont les
champs de contrôle n'ont jamais été remplis.**

**2. `0xEBCFC` est un troisième champ de contrôle, en queue** — et **il diffère d'un exemplaire à
l'autre**, donc il **dépend des données**. C'est le comportement d'une somme de contrôle.
⚠ **Progrès de localisation, pas de résolution** : 15 algorithmes testés (sommes 16/32 bits, CRC-16
CCITT, XMODEM, IBM, CRC-32, complément) sur 6 plages candidates — **aucun ne tombe juste**. On sait
maintenant **où** sont les sommes de contrôle ; on ne sait toujours pas **comment** elles sont
calculées. L'erratum « pas de checksum » est donc nuancé : les **champs** existent.

**3. `0xEBF1B` : « W » contre « F »** dans `__NWGDWPF1` / `__NFGDWPF1`.
**Hypothèse, non prouvée : `F` = FAP, `W` = sans filtre.** Ce serait l'identifiant de variante — et
c'est cohérent avec un véhicule FAP dont le calculateur embarque **aussi** la calibration sans filtre.
Je ne l'affirme pas : un octet isolé dans une chaîne de 9 caractères ne suffit pas.

### ★ Une hypothèse antérieure est **réhabilitée**

L'erratum **38 §1** disait : « la banque F est une copie de E — retirée, car 14 octets d'écart
réels ». **L'argument était mauvais** : 14 octets d'écart est précisément la **signature d'une copie
variante**, pas la preuve de deux zones indépendantes. La comparaison exhaustive tranche : **F est
bien une copie de E.** L'entrée est rétablie dans le registre.

### Et ce que cela ne change pas

**La table de pointeurs `0xE1400` est identique dans les deux exemplaires**, et ses valeurs sont des
**offsets relatifs** (0x100A … 0xBC38). **Le même handle désigne donc la même structure des deux
côtés.** Toutes les adresses du catalogue sont données dans l'exemplaire **E** ; ajouter `0x10000`
donne l'exemplaire F.

---

## 3. ★★ Les tables oubliées : **97,9 % de couverture, et pourtant 19 cartes manquaient**

### 3.1 Couverture — il n'y a **pas** de grande table orpheline

Sur `0xE1000-0xEC000` (45 056 octets), **44 088 sont atteints par un handle**. Deux trous seulement :

| trou | taille | contenu | lecture |
|---|---|---|---|
| `0xE1000-0xE100A` | 10 o | `0a 1d 0c 1d 0e 1d 10 1d 12 1d` | **cinq handles en clair** (0x1D0A…0x1D12) — petite **table de renvoi**, juste avant la première structure. Les mêmes octets existent aussi à `0xE0FFA`. |
| `0xEBC42-0xEC000` | 958 o | `9e 0d 53 0d 1b 09` puis `C3` | **fin du Datensatz** : 3 mots décroissants (3486, 3411, 2329) puis remplissage. |

**⇒ Le Datensatz est intégralement adressé.** Les oubliées ne sont donc pas des octets perdus : ce
sont des **structures dont la disposition interne n'a jamais été décodée**.

### 3.2 Typologie des **1 056 blocs sans en-tête 1-D** (27 854 octets)

| type interne | blocs | octets | lecture |
|---|---|---|---|
| **non classé** | 468 | 24 230 | aucune disposition reconnue — **médiane 2 octets** : surtout des scalaires isolés |
| **triplet (3 mots)** | 364 | 2 184 | seuil bas / seuil haut / temporisation — **hypothèse**, cohérente avec les moniteurs |
| **paire de mots** | 94 | 376 | couple min/max ou (valeur, temporisation) |
| **scalaire 1 mot** | 91 | 182 | une valeur seule |
| **axe (tag connu)** | 26 | 668 | axe autonome `[tag][n][n valeurs]` |
| **axe (tag inconnu)** | 6 | 132 | **les vraies oubliées ici : six tags non identifiés** |
| **liste nue** | 4 | 56 | `[n][n valeurs]` sans tag |
| **suite croissante** | 3 | 26 | fragment d'axe probable |

**Le « non classé » fait peur par son nombre (468) mais pèse peu (24 Ko) et il est fait de miettes**
— 2 octets de médiane. Les vraies tables sont ailleurs.

### 3.3 ★ 19 cartes 2-D **sans axes** — le décompte des cartes était faux

Le décodeur exigeait `[tagY][nY][axeY][tagX][nX][axeX][grille]`. Or **certaines cartes sont stockées
à plat, sans aucun axe** : elles étaient donc **rejetées** — et comptées comme « blocs sans en-tête ».

La trame correcte s'obtient en **minimisant la discontinuité entre cellules voisines**. Validation
sur les cartes déjà décodées : la méthode retrouve la bonne largeur **17 fois sur 25** (les échecs
sont les grilles 8×8, trop petites pour être discriminées).

| EA | taille | mots | trame | plage | verdict |
|---|---|---|---|---|---|
| `0xE9848` | 512 o | 256 | 16 × 16 | 2 500 … 13 500 | **grille plausible** |
| `0xEB1E2` | 512 o | 256 | 16 × 16 | 427 … 2 304 | **grille plausible** |
| `0xEB792` | 512 o | 256 | 16 × 16 | 45 … 510 | **grille plausible** |
| `0xE2B62` | 504 o | 252 | 18 × 14 | 0 … 200 | **grille plausible** |
| `0xE5634` | 384 o | 192 | 16 × 12 | 59 861 … 64 877 | **grille plausible** |
| `0xE57B4` | 384 o | 192 | 16 × 12 | 61 355 … 64 575 | **grille plausible** |
| `0xE5DB4` | 384 o | 192 | 16 × 12 | — | ⚠ trame douteuse, **non retenue** |
| `0xE65C4` | 336 o | 168 | 14 × 12 | 1 050 … 2 200 | **grille plausible** |
| `0xE6714` | 336 o | 168 | 14 × 12 | 990 … 2 150 | **grille plausible** |
| `0xE94FE` | 256 o | 128 | 8 × 16 | 0 … 800 | **grille plausible** |
| `0xE9748` | 256 o | 128 | 8 × 16 | 128 … 512 | **grille plausible** |
| `0xE9C70` | 256 o | 128 | 8 × 16 | 6 000 … 13 500 | **grille plausible** |
| `0xE9D72` | 256 o | 128 | 8 × 16 | 0 | ⚠ **uniforme** (bloc rempli) |
| `0xE9F96` | 256 o | 128 | 8 × 16 | 40 … 60 | **grille plausible** |
| `0xEA558` | 256 o | 128 | 8 × 16 | 0 … 171 | **grille plausible** |
| `0xEA658` | 256 o | 128 | 8 × 16 | 1 280 | ⚠ **uniforme** (bloc rempli) |
| `0xEA758` | 256 o | 128 | 8 × 16 | 0 … 256 | **grille plausible** |
| `0xEAA60` | 256 o | 128 | 8 × 16 | 800 … 3 000 | **grille plausible** |
| `0xEAB60` | 256 o | 128 | 8 × 16 | 0 | ⚠ **uniforme** (bloc rempli) |
| `0xEAC60` | 256 o | 128 | 8 × 16 | 0 | ⚠ **uniforme** (bloc rempli) |
| `0xEAD60` | 256 o | 128 | 8 × 16 | 0 … 1 665 | **grille plausible** |
| `0xEAE60` | 256 o | 128 | 8 × 16 | 0 … 1 000 | **grille plausible** |
| `0xE3BE4` | 128 o | 64 | 8 × 8 | — | ⚠ trame douteuse, **non retenue** |
| `0xE3C70` | 128 o | 64 | 8 × 8 | 500 … 6 000 | **grille plausible** |
| `0xE3DB6` | 128 o | 64 | 8 × 8 | 500 … 6 000 | **grille plausible** |

**19 grilles retenues, 4 blocs uniformes écartés, 2 trames douteuses écartées.**

### Pourquoi ce sont vraiment des cartes — deux preuves

**Preuve visuelle.** `0xE5634` lu en 16×12 est une surface parfaitement lisse : ≈ 64 000 en haut à
gauche, ≈ 60 000 en bas à droite, décroissance régulière — soit **−1 300 à −5 500 en complément à
deux**. Une séquence aléatoire ne produit pas ça. `0xEB792` lu en 16×16 monte de 45 à 510 avec des
paliers francs, comme une cartographie de limitation.

**Preuve structurelle.** Ces blocs sont **contigus et régulièrement espacés** :

```
0xE5634  0xE57B4  0xE5934  0xE5AB4  0xE5C34  0xE5DB4     ← 6 cartes de 384 o, pas de 0x180
0xEA558  0xEA658  0xEA758  0xEAB60  0xEAC60  0xEAD60  0xEAE60   ← 7 cartes de 256 o, pas de 0x100
```

Un remplissage aussi régulier ne se produit pas par hasard : c'est une **famille de cartes rangée par
usage** — exactement ce que l'étape 55 avait montré pour les blocs adressés par handle.

**⇒ Le décompte des cartes passe de 66 à 85** (66 + 19), sous réserve d'identification du
consommateur.

---

## 4. Ce que cette étape change dans le catalogue

| section | ajout |
|---|---|
| **§ 2 ter** | **nouveau** — le Datensatz en deux exemplaires, les 14 octets, et ce que cela implique |
| **§ 5 bis** | encart de **prudence** : une plage ne prouve rien ; règle « nommer par la chaîne, pas par la plage » |
| **§ 6 bis** | **nouveau** — tables oubliées : couverture, typologie des 1 056, 19 cartes plates |
| **§ 10** | erratum **56** (méthode), **57** (champs de checksum localisés), **57** (85 cartes et non 66), **38 §1 réhabilitée** |

Le catalogue : **1 241 → 1 397 lignes**. Tout est régénérable par :

```
python3 outils/tables_oubliees.py        # les 4 vérifications
python3 outils/genere_catalogue.py       # le document
```

---

## 5. Prochaines actions — dans l'ordre de rendement

1. **`sub_AFAA0`, `sub_A1E9E`, `sub_B7FD4`…** : identifier les consommateurs des familles de
   `0xE5634` et `0xEA558` nommerait **19 cartes d'un coup**, par la même méthode qui a marché à
   l'étape 55.
2. **Les six tags d'axe inconnus** : peu de blocs, mais un tag identifié re-nomme toutes les cartes
   qui l'utilisent en abscisse.
3. **L'octet `0xE434D`** : un seul octet sépare les deux variantes — le lire dans le code dirait
   **laquelle est active**.
4. **Les 364 triplets** : tester l'hypothèse « seuil bas / seuil haut / temporisation » sur ceux dont
   le consommateur est déjà connu (`sub_A1E9E`).
