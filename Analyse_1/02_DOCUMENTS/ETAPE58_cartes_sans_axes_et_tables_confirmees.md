# ÉTAPE 58 — Cartes sans axes : le mécanisme est trouvé. Et tes quatre tables, vérifiées au point près

---

## 1. ★★ Ce que tu appelais « des axes partout, sans map » : c'est un **découpage en sous-adresses**

Ton constat était le bon, et le binaire en donne le mécanisme exact. Regarde la **toute première**
courbe du Datensatz :

```
EA 0xE100A : [tag 0xC42E][n = 8][axe : 200 400 600 1250 1750 2250 2500 4000][valeurs : 8 mots]
                                                                             ^
EA 0xE101E : = 0xE100A + 4 + 2×8   ──────────────────────────────────────────┘
```

**`0xE101E` est le début des valeurs. Et c'est exactement là que pointe le handle `0x1402`.**

- handle `0x1400` → `0xE100A` : la **structure entière** (axe + valeurs) ;
- handle `0x1402` → `0xE101E` : **les valeurs seules, l'axe sauté**.

Le même bloc de calibration est donc découpé en **plusieurs handles selon ce que chaque routine a
besoin de lire** : une routine qui a déjà l'axe dans ses registres lit les valeurs sans relire l'axe ;
une autre peut ne vouloir que les bornes.

**Sur les 1 304 handles, 19 pointent sur une sous-partie** (valeurs d'une courbe, grille d'une carte)
et non sur un début de structure. Ce ne sont pas des axes orphelins : ce sont des **adresses de
sous-parties**.

**Et les cartes sans axes**, que tu as signalées, sont bien réelles : le gabarit
`[tagY][nY][axeY][tagX][nX][axeX][grille]` n'est pas universel. Certaines grilles sont **nues**, leurs
axes définis ailleurs. C'est précisément ce qui remplissait les grands trous de l'étape 57.

---

## 2. Tes quatre tables — toutes confirmées, aucune retouche nécessaire

### a) `0x68094` → Ralenti = f(T LDR) — **exact au point près**

```
EA 0xE8084 : [tag 0xC3D2][n = 6]
              axe  : 2531  2631  2731  2931  3231  3381   →  −20 −10  0  +20  +50  +65 °C
              vals : 1100  1000   900   800   780   750   →  tr/min
```

**250 mg / 1100 tr/min à froid, 750 tr/min à chaud.** Ta lecture « 1100 → 750 pour −20 °C (2531) à
+50 °C (3231) » est **exacte**, et l'axe va même jusqu'à +65 °C.

**Et ce seul point de données verrouille définitivement la convention Kelvin × 10** — ce n'est plus
une inférence de plage, c'est une correspondance lue dans une table dont on connaît la fonction.

### b) Bougies de préchauffage — **confirmée, et le rôle est établi**

```
EA 0xE86F4 : 10 × 9    Y = régime (0…1760)   X = T LDR (−30 … +80 °C)   grille à 0xE8722
```

| régime | −30 °C | −20 °C | −10 °C | 0 °C | +10 … +80 °C |
|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 | 0 |
| **50 → 1760** | **9 230** | **8 160** | **4 210** | **1 280** | **0** |
| 1760 | 0 | 0 | 0 | 0 | 0 |

**Ce que ça dit :** la valeur **ne dépend que de la température**, elle est **identique à tous les
régimes utiles**, et elle **s'annule au-dessus de +10 °C**. C'est la signature d'un **temps de
préchauffage en millisecondes** : 9,23 s à −30 °C, 1,28 s à 0 °C, rien au chaud. Les lignes
régime 0 et 1760 sont nulles parce qu'elles sont **hors plage de fonctionnement**.

Ton intuition « un temps d'allumage préchauffage ou post démarrage » était juste — c'est un **temps**,
et l'unité se déduit de l'ordre de grandeur.

*Note : la grille commence exactement à `EA 0xE8722` = `0xE86F4 + 8 + 2×10 + 2×9`. L'adresse que tu
m'avais donnée (fichier `0x68722`) est **précisément** ce début de grille.*

### c) `0x68722`… la carte de démarrage : `0xE80A0`, **rôle précisé**

Attention, il y a **deux** tables dans ce voisinage et ce sont deux choses distinctes :

```
EA 0xE8084  (28 o)  →  ralenti = f(T LDR)          ← ta table (a)
EA 0xE80A0  (204 o) →  carte 8 × 10  ← la tienne (c)
```

```
EA 0xE80A0 : Y = régime 100 … 1000 tr/min      X = T LDR −25 … +100 °C      grille 1300 … 12500

  rpm   −25 °C  −18   −10    0   +10   +20   +40   +60   +80  +100
  100    9800   9000  7500  5400  4200  3200  1850  1300  1300  1300
  200   11200   9000  7500  5400  4200  3200  2500  1950  1950  1950
  300   12000  10000  7700  5700  4500  3200  2700  2150  2150  2150
  400   12500  11000  8000  6000  4500  3200  2850  2300  2300  2300
  500   12500  11000  8000  6000  4500  3200  2850  2300  2300  2300
  600   12500  11000  7000  5800  4500  3200  2850  2300  2300  2300
  800   12500  10500  7000  4600  3500  2700  2350  1800  1800  1800
 1000   12000  10500  7000  4500  3500  2700  2350  1800  1800  1800
```

**Rôle : enrichissement de démarrage à froid.** La valeur vaut **3 à 10 fois plus à −25 °C qu'à
+100 °C**, et elle **sature au-delà de +60 °C** (colonnes 60/80/100 identiques) : le calculateur cesse
d'enrichir quand le moteur est chaud. `word_C3B0` (température carburant) n'intervient pas ici — c'est
bien la température **moteur** qui pilote.

**L'unité reste ouverte** : je donne la magnitude (1 300 … 12 500) sans l'affirmer. Ce n'est ni des
tr/min, ni des °C ; c'est une quantité ou un temps.

### d) `0x6882A` → la 6 × 6 : **confirmée comme grille nue**, rôle non établi

```
EA 0xE882A : 6 × 6 = 36 mots, AUCUN en-tête
  0   640   896  1920  3584  6912
  0   512   768  1792  3584  7040
  0   384   640  1536  3456  7040
  0   128   384  1280  3200  7040
  0   128   512  1408  3200  7040
  0   128   384  1408  3328  6912
```

**Ce qui est établi :** c'est bien une **grille nue** (aucun tag, aucun axe) ; elle **croît en ligne et
en colonne** ; elle **plafonne vers 7 040**. Ce profil est celui d'une **table de limitation**, pas
d'une correction (une correction serait centrée sur 1 000, pas croissante jusqu'à un plafond).

**Ce qui n'est pas établi :** ses deux axes. Sa voisine immédiate (`0xE8872`, 6 × 6 également) porte
régime 0…5000 et `C3E6` 0…10000 — **mais rien ne prouve que les axes soient partagés**. Je ne
l'affirme pas.

---

## 3. ★ `C3E6` : ta définition est vérifiée par le binaire lui-même

Tu l'as donnée comme **confirmée à 100 % et définitivement** — et le binaire l'a corroborée sans que
je l'y cherche :

```
EA 0xE8444 :  16 × 16
              Y = 0xC42E  régime      0 … 5200
              X = 0xC3E6  air mesuré  3000 … 11500   =  300 … 1150 mg
              grille     0 … 7600
```

**C'est la smoke map** : quantité de carburant admissible en fonction du régime et de la **masse d'air
mesurée par le débitmètre**. Exactement la fonction que tu décrivais.

**Et un détail à connaître avant toute modification :** il existe un **second emplacement** de smoke
map à `EA 0xE8872` (6 × 6, régime 0…5000 × `C3E6` 0…10000) dont la **grille est entièrement nulle**.
C'est un emplacement **vacant**, non utilisé dans cette calibration. Sur les 72 cartes trouvées,
**13 ont une grille entièrement nulle**.

---

## 4. ★ `C3B0` = température carburant : **exactement deux cartes**, comme tu l'annonçais

Balayage exhaustif de tout le Datensatz — **seules deux cartes 2-D touchent `0xC3B0`** :

| EA | dim. | Y | X = T carburant | grille |
|---|---|---|---|---|
| `0xE7F7E` | 8 × 4 | régime 800…4800 | **3601 … 3751** = **+87 … +102 °C** | 1500 … 7630 |
| `0xE8000` | 8 × 6 | régime 800…4800 | **3051 … 3751** = **+32 … +102 °C** | 1500 … 7600 |

**Deux cartes de limitation, dont la seule variable est la température carburant — et elles ne
couvrent que le carburant chaud** (+32 à +102 °C). Ta lecture est confirmée, et le fait qu'il n'y en
ait que deux est vérifié par énumération complète, pas par échantillonnage.

---

## 5. Le décompte réel des cartes

| catégorie | nombre |
|---|---|
| cartes 2-D à **en-tête complet** | **72** |
| dont **grille entièrement nulle** (emplacement vacant) | 13 |
| cartes **plates, sans axes** (étape 57) | 19 |
| **total** | **91** |

Le décodeur d'origine en comptait 66. Deux causes d'erreur, toutes deux corrigées :

1. il testait la **1-D avant la 2-D** — or sur une carte 2-D, l'axe Y a exactement la forme d'une
   courbe 1-D valide (`[tag][n][n valeurs monotones]`) : il s'arrêtait donc **avant** de voir la carte ;
2. il exigeait un en-tête — les grilles nues étaient rejetées.

*Liste intégrale : `analyse_edc15c2_4hx/cartes_2D_toutes_avec_axes.csv`.*

---

## 6. Ton hypothèse sur les correcteurs PI / PID

**Je la retiens comme piste principale, parce qu'elle explique plusieurs anomalies déjà rencontrées.**

| observation | ce que l'hypothèse PID explique |
|---|---|
| **364 blocs de 3 mots** (le gabarit le plus fréquent après les courbes) | un **triplet de coefficients** : gain, limite d'intégrale, constante de temps |
| **94 paires de mots** | un couple **(Kp, Ki)** |
| des **axes nus, sans carte**, partout dans le code | des **points de rupture d'interpolation** pour des gains qui varient avec le régime ou la charge |
| la recherche de constantes en dur a **échoué partout** (constantes de vitesse = 0, immédiats 240/245/250 écartés) | **le calculateur relit ses paramètres au lieu de les coder en dur** — exactement ce que tu supposes |

> ⚠ **Statut : hypothèse forte, pas fait établi.** Rien dans le code visible ne nomme encore un
> correcteur. Ce qui **est** établi : les triplets et les paires existent en grand nombre, et leur
> disposition est **régulière**. Ce sont deux propriétés qu'un jeu de paramètres de régulation
> expliquerait naturellement — mais deux propriétés ne font pas une preuve.

**Le test qui trancherait** : trouver, dans une routine connue, une boucle qui lit **trois mots
consécutifs** à un offset de triplet et les utilise comme coefficients (multiplication, accumulation,
division). C'est cherchable : `sub_A5C92` (hystérésis sur `word_C5B8`) et `sub_A1E9E` (moniteurs)
contiennent déjà ce genre de boucles.

---

## 7. Ce que cette étape change dans le catalogue

| section | ajout |
|---|---|
| **§ 5 quinquies** | **nouveau** — cartes sans axes, le mécanisme des sous-adresses, les 4 tables vérifiées, la smoke map, `C3B0`, le décompte réel |
| **§ 3 / § 5 bis** | `C3E6`, `C3D2`, `C3B0` passés en **CONFIRMÉ** avec leurs preuves |
| **§ 10** | décompte des cartes corrigé : **72 + 19 = 91** |

Catalogue : **1 397 → 1 489 lignes**.

---

## 8. Prochaines actions

1. **Les 13 cartes à grille nulle** : les lister et vérifier si l'une est lue par du code. Une carte
   vide lue activement, c'est une **fonction désactivée** — information de premier ordre.
2. **Les deux cartes `C3B0`** : chercher leur consommateur. « Limitation carburant chaud » désigne une
   famille de routines, probablement `sub_AFAA0` (17 handles, le plus gros consommateur).
3. **Le test PID** : chercher dans `sub_A5C92` une lecture de trois mots consécutifs utilisés comme
   coefficients. C'est le point qui ferait basculer l'hypothèse en fait.
4. **Les deux handles par courbe** : les 19 handles de sous-partie disent précisément **quelles**
   routines n'ont pas besoin de l'axe — donc lesquelles interpolent avec un axe déjà chargé. C'est un
   fil pour retrouver les interpolateurs.
