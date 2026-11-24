# ÉTAPE 53 — Le Datensatz est fait de **paquets**, et une hypothèse réfutée

---

## 1. Méthode : la récurrence des tailles

Sur les 1 304 handles, **1 049 ne sont pas des courbes ni des cartes**. Plutôt que de les prendre un par
un, j'ai regardé **la distribution des tailles de bloc** — un format régulier se trahit par une taille
qui revient.

| taille | nombre de blocs | | taille | nombre de blocs |
|---|---|---|---|---|
| 1 mot | 91 | | 11 mots | 5 |
| 2 mots | 94 | | 12 mots | 35 |
| **3 mots** | **364** | | 13 mots | 2 |
| 4 mots | 53 | | 14 mots | 37 |
| 5 mots | 65 | | 15 mots | 4 |
| 6 mots | 136 | | **16 mots** | **119** |
| 7 mots | 10 | | 17 mots | 6 |
| 8 mots | 16 | | 18 mots | 48 |
| 9 mots | 17 | | 19 mots | 1 |
| 10 mots | 24 | | 20 mots | 1 |

**Répartition finale des 1 304 handles :**

```
182 courbes 1-D + 66 cartes 2-D + 31 blocs d'axe + 7 blocs réservés
+ 91 paramètres scalaires + 927 non classés = 1 304
```

---

## 2. ★★ Constat 1 — le Datensatz est **dominé par des paquets de paramètres**

**Le type le plus fréquent est le bloc de 3 mots : 364 exemplaires**, suivi de 136 blocs de 6 mots et
124 de 16 mots. Ce ne sont **ni des courbes ni des cartes**.

`word_142A` en est l'exemple type, et il est déjà décodé : **bloc de 5 mots** (`3431, 220, 100, 100,
10280`), dont le code lit `[+0], [+2], [+4], [+6]` — c'est-à-dire **le 1er, 2e, 3e et 4e mot**.

**⇒ La structure dominante du Datensatz n'est pas la courbe, c'est le PAQUET de paramètres de taille
fixe, lu à offsets fixes par un sous-programme.** Un handle = un paquet. Cela achève de dissoudre
l'idée de « structure typée » (erratum de l'étape 47 §1) : **il n'y a pas de champs nommés, il y a des
positions.**

**Conséquence pratique** : pour décoder ces 927 blocs, **la bonne question n'est pas « quel est le
format ? » mais « quel sous-programme lit ce handle, et à quels offsets ? »** — comme on l'a fait pour
`word_142A`, `word_1474`, `word_18F2`. C'est faisable, mais c'est **du travail par usage**, pas une
découverte de format.

---

## 3. ★ Constat 2 — un marqueur récurrent à position fixe dans les blocs de 32 octets

Sur **119 blocs de 32 octets**, le mot d'offset **`+0x12`** vaut :

| valeur | nombre |
|---|---|
| **`0x0F10`** | **56** |
| `0x0000` | 10 |
| **`0x0F00`** | **8** |
| **`0x0F60`** | **4** |

**68 blocs sur 119 portent une valeur de la bande `0x0Fxx` à la même position.** Ce n'est pas un
hasard de contenu : **c'est un marqueur de format**.

**Je ne conclus pas sur son sens.** Trois lectures possibles, aucune retenue :
- un **type de bloc** (mais alors pourquoi pas universel : 56 sur 119 seulement) ;
- une **borne ou un pas** commun à une famille de blocs ;
- un **drapeau de version** propre à une génération de calibration.

**Noté comme point de contrôle.** Ne pas le présenter comme un type tant que la contre-épreuve
(présence obligatoire) n'est pas faite.

---

## 4. ★★★ Constat 3 — l'hypothèse des « axes partagés » est **TESTÉE et RÉFUTÉE**

**31 blocs** ont exactement la forme `[adresse variable][n][n valeurs]` — soit `4 + 2n` octets, ce qui
les distingue des courbes (`4 + 4n`). Le premier est parlant :

```
word_1400, EA 0xE100A :  var = word_C42E, n = 8
                        valeurs = 200, 400, 600, 1250, 1750, 2250, 2500, 4000
```

C'est **une échelle de régime à huit points**. L'idée naturelle : une **bibliothèque d'axes**, définis
une fois et réutilisés par les cartes.

**Le test :** j'ai calculé les **109 axes distincts** réellement utilisés par les 66 cartes, et cherché
les 31 blocs dedans.

> **Résultat : 2 réutilisations sur 31.**

**⇒ L'hypothèse est réfutée.** Ce ne sont pas des axes partagés : les cartes portent leurs axes
**en propre**, et on l'a vérifié 66 fois sur 66 (tailles exactes, étape 51).

**Mais le test laisse une observation qui, elle, tient :** les handles **`1400`, `1402`, `1404`, `1406`,
`1408` sont cinq blocs CONSÉCUTIFS décrivant tous `word_C42E`** — avec 8, 2, 16, 16 et 8 points.

```
1400  0xE100A   word_C42E   8 points   200 … 4000
1402  0xE101E   word_C42E   2 points   650 … 1200
1404  0xE1026   word_C42E  16 points   200 … 5000
1406  0xE104A   word_C42E  16 points   200 … 5000
1408  0xE106E   word_C42E   8 points   200 … 4000
```

**Cinq échelles de régime distinctes et voisines, regroupées.** C'est la signature d'une **famille
d'axes** — et donc, très probablement, **d'une famille de cartes qui les consomment** : un calculateur
diesel utilise typiquement plusieurs grilles de régime (conduite, démarrage, régénération FAP…).
Cet usage-là est dans la **couche absente**, mais **l'organisation du Datensatz le reflète**.

---

## 5. Le catalogue est à jour

`analyse_edc15c2_4hx/CATALOGUE_MAITRE.md` (**762 lignes**) contient désormais
une section **§ 2 bis** avec :

- la **répartition par gabarit** recalculée à chaque exécution ;
- la **distribution des tailles de blocs** ;
- le **constat du marqueur `0x0F10`** ;
- le **compte rendu du test réfuté** sur les axes partagés.

**Les trois constats de cette étape sont inscrits dans le document, y compris l'hypothèse réfutée** —
c'est précisément ce que le registre du § 10 doit conserver.

---

## 6. Ce que cette étape change dans la stratégie

**Une conclusion de méthode, et elle est importante :** chercher des **formats** ne paie plus. Il reste
927 blocs dont on connaît **la taille** mais pas **le sens**, et aucun gabarit supplémentaire ne les
décodera — parce que **ce sont des paquets de nombres sans en-tête**.

**La seule voie restante est l'usage** : pour chaque handle, **trouver le sous-programme qui le lit et
relever les offsets**. La méthode a déjà donné `word_142A` (4 champs), `word_1474` (5 durées),
`word_18F2` (2 comparaisons), `word_18AA`/`18AC` (deux bornes).

**⇒ C'est un travail systématique et mécanisable** : parcourir les 927 handles, chercher `mov rX,
word_YYYY` dans le code, et remonter les offsets. **Prochaine étape : automatiser ce balayage.**

---

## 7. Prochaines actions

1. **★ Automatiser le « décodage par usage »** : pour chaque handle non classé, extraire du listing
   **tous les couples `(handle, offset)`** lus, et produire un tableau. C'est la suite logique et elle
   est mécanique.
2. **Contre-épreuve du marqueur `0x0F10`** : vérifier s'il est **obligatoire** dans une famille
   identifiée par ailleurs (par exemple les blocs contenant une durée de confirmation).
3. **La famille `1400…1408`** : chercher quels handles de cartes ont des étiquettes voisines — les
   familles de cartes sont peut-être contiguës en mémoire comme les axes.
4. **Ne pas relancer de recherche de gabarit** : le constat 1 dit pourquoi elle est épuisée.
