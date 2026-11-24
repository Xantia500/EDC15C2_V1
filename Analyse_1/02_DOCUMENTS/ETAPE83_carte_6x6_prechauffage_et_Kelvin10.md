# ÉTAPE 83 — La carte 6×6 de la zone préchauffage · ★ les axes de température sont en Kelvin ×10 · le cadastre ne referme pas (et c'est l'information)

> Trois choses : une carte de plus, **la clé de décodage des températures**, et une **erreur de ma part**
> à corriger (les « zones orphelines » de l'étape 82 n'existent pas).

---

## 1. L'« orphelin » `0xE86A8` n'existe pas : c'est la grille d'une carte 6×6

Mon parseur de l'étape 82 concluait « structure 14, résidu 38 ». En le corrigeant (tester la forme 2-D
**avant** la 1-D, et n'accepter la 2-D que si elle remplit *exactement* l'écart), l'objet se résout :

**`0xE868C` (handle `0x1B42`) — carte 2-D 6 × 6, taille 52 mots = écart exact jusqu'à `0xE86F4`.**

```
[0xC3D2][6] [2431 2531 2631 2731 2831 3831]      ← axe Y = température LDR
[0xC562][6] [0 300 10000 12000 14016 18000]      ← axe X = C562
[36 valeurs]
```

| T LDR ↓ / C562 → | 0 | 300 | 10 000 | 12 000 | 14 016 | 18 000 |
|---|---|---|---|---|---|---|
| **2431** | 0 | **9230** | 9230 | 9230 | 9230 | 9230 |
| **2531** | 0 | **8150** | 8150 | 8150 | 8150 | 8150 |
| **2631** | 0 | **4210** | 4210 | 4210 | 4210 | 4210 |
| **2731** | 0 | **1280** | 1280 | 1280 | 1280 | 1280 |
| **2831** | 0 | 0 | 0 | 0 | 0 | 0 |
| **3831** | 0 | 0 | 0 | 0 | 0 | 0 |

Signature très nette : **première colonne nulle**, puis **valeur constante par ligne**, qui **s'effondre quand
la température monte** (9230 à froid → 0 au chaud). C'est un **temps / une durée coupée par la température** —
exactement le profil d'un **préchauffage**. Et c'est bien le voisinage attendu : le handle suivant
`0x1B44` pointe `0xE86F4`.

## 2. ★★ Les axes de température sont en **Kelvin ×10**

Les valeurs d'axe ci-dessus se lisent avec `T[°C] = valeur/10 − 273,1` :

| valeur | 2431 | 2531 | 2631 | 2731 | 2831 | 3831 |
|---|---|---|---|---|---|---|
| **°C** | **−30** | −20 | −10 | **0** | **+10** | **+110** |

Trois arguments convergent :

1. L'axe **−30 → +110 °C** est la plage canonique d'une carte thermique moteur.
2. L'objet voisin **`0xE870C`** est un axe 9 points `2431 2531 2631 2731 2831 2931 …` = **−30 … +20 °C** :
   l'axe de démarrage à froid par excellence.
3. Les valeurs intermédiaires tombent pile sur des graduations rondes (−20, −10, 0, +10), ce qu'aucune autre
   hypothèse (ADC, 0,1 °C, offset 40) ne reproduit.

⇒ **Clé de décodage applicable à tout axe portant `0xC3D2` (T LDR) ou `0xC3B0` (T carburant).**
**Réserve** : les valeurs d'axe sont des **graduations**, pas des mesures — l'échelle des *grandeurs* reste à
confirmer (voir la consigne « une plage ne prouve jamais une grandeur »).

## 3. Les objets voisins, structures confirmées par l'écart exact

| EA | handle | structure | taille | écart | ✓ |
|---|---|---|---|---|---|
| `0xE86F4` | `0x1B44` | `[0xC3AE][10][0 50 300 500 600 1000 1150 1250 1750 1760]` | 12 | 12 | ✓ |
| `0xE870C` | `0x1B46` | `[0xC3D2][9][2431 2531 2631 2731 2831 2931 …]` | 11 | 101 | axe d'un objet plus grand |

`0xC3AE` porte l'identifiant `0x1F40` (étape 82) : c'est une grandeur **mesurable**, donc `0xE86F4` est une
courbe de correction sur une grandeur publiée.

## 4. Ce que `C562` est — partiellement établi

- **3 écritures** seulement pour **100 références** dans `clean.asm` :
  - `sub_CF8C8` (l.232358) : `word_C562 ← word_C3FA` (recopie d'un paramètre)
  - `sub_CF8A4` (l.232352) : `word_C562 ← 0xFF` (**valeur de secours**)
  - l.232870 : `word_C562 ← MDL` (résultat de multiplication)
- Employée **en seuil** : `cmp r5, word_C562` (l.159936, 176821, 177661, 178542…) et comparée à
  `[r4+#6]`/`[r4+#18h]`, c'est-à-dire aux **éléments d'un axe**.
- Axe X de la carte 6×6 ci-dessus : `0, 300, 10 000, 12 000, 14 016, 18 000`.

⇒ `C562` est un **paramètre/limite recopié**, pas une mesure. Un **compteur** (km, heures) ou un **seuil
d'auto-adaptation** sont les deux candidats ; `0xFF` comme valeur de secours plaide pour un petit compteur.
Non tranché.

## 5. ⚠ ERRATA de l'étape 82 — et ce que le non-recouvrement nous apprend

En rejouant le classement sur **1 303 objets** :

| résultat | nombre |
|---|---|
| cartes 2-D (en-tête complet, taille = écart) | **48** |
| courbes 1-D (idem) | **30** |
| **objets sans en-tête** (pas de tag `0xC0xx`–`0xC7xx` en tête) | **1 079** |
| taille incohérente | 146 |

⇒ **Les 4 « zones orphelines » de l'étape 82 étaient un artefact de mon parseur.** Il n'y a pas de
calibration cachée entre les handles : le Datensatz est **contigu et entièrement référencé**.

Et le chiffre qui compte : **1 079 objets sur 1 303 n'ont aucun en-tête**. C'est la **confirmation directe de
ta remarque** : « des maps n'ont pas d'axes » — ce n'est pas une exception, c'est la **règle majoritaire**.

## 6. La queue du Datensatz (`0xEBC38` → `0xEBFB9`, 449 mots) n'est pas une zone de cartes

| contenu | mots |
|---|---|
| `0xC3C3` (remplissage) | **152** |
| `0x0000` | **188** |
| `0xFFFF` | **60** |
| autres (42 valeurs distinctes) | 49 |

Valeurs remarquables : un îlot `[0xC3BA][3][2681 2831 2832]` (= −5 / 0 / +0,1 °C en Kelvin ×10), une zone
`0xFFFF` percée de `0x0014`, et deux **résidus ASCII** : `75vGB075WF2S010384` (EA `0xEBF04`) et
`1037353776` (EA `0xEBFB0`). ⇒ **la calibration s'arrête réellement là** ; rien à exploiter.

## 7. Prochaines cibles

1. **`C3FA` → `C562`** : remonter à la source de `C3FA` pour nommer `C562` (et donc la carte 6×6).
2. **Appliquer Kelvin ×10** à tous les axes `C3D2`/`C3B0` déjà transcrits dans le catalogue — beaucoup de
   valeurs « obscures » vont devenir lisibles.
3. **La carte `0xE86F4`** (`C3AE`, 10 points : 0 → 1760) : identifier `C3AE` par son identifiant `0x1F40`.
4. Les 1 079 objets sans en-tête : il faut une **autre méthode** que les en-têtes — passer par les
   **consommateurs** (`unk_2FAC` et `word_1D94`) pour retrouver axe et grille de chaque grille nue.

## 8. Consignation

**`CATALOGUE_MAITRE.md` § 13 B.29** — carte 6×6 `0xE868C`, **clé Kelvin ×10**, `0xE86F4`, `C562`,
errata des zones orphelines, statistique du cadastre (48 / 30 / 1 079), inventaire de la queue.
