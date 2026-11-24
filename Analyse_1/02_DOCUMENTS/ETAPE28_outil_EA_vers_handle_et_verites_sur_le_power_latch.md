# ÉTAPE 28 — Un outil décisif, un erratum, et la vérité sur le power latch

Trois résultats négatifs **utiles**, un outil qui change la méthode, et une conclusion forte sur
l'EEPROM. Les questions régulateur / Vmax restent ouvertes : je dis précisément pourquoi et
comment les prendre autrement.

---

## 1. Outil nouveau — remonter d'une adresse de calibration à son handle

`outils/ea2handle.py` : pour une `EA` donnée, cherche dans la table des 1 304 handles celui dont la
valeur = `EA − 0xE0000`, puis il suffit de `grep` le nom du handle pour trouver **tous les sites
d'appel**.

Validation sur quatre cas **déjà établis indépendamment** :

| EA | handle retrouvé | identité connue | verdict |
|---|---|---|---|
| `0xE8444` | `word_1B40` | smoke map 16×16 | ✔ |
| `0xE89C6` | `word_1B5A` | carte mode dégradé (38 mm³) | ✔ |
| `0xE8B10` | `word_1B64` | marche arrière | ✔ |
| `0xE4954` | `word_1814` | courbe à tag vitesse | ✔ (mais voir §2) |

**4/4.** Désormais, toute adresse de calibration peut être reliée à son consommateur : c'est ce qui
manquait pour traiter méthodiquement les cartes une par une.

## 2. Erratum — `byte_C337` n'est pas la vitesse

Deux arguments indépendants, tous deux techniques :

1. **La courbe à tag `0xC337` (`EA 0xE4954`, axe 0…250) a pour handle `word_1814` — et `word_1814`
   n'apparaît nulle part dans le désassemblage.** Elle n'est donc jamais appelée.
2. **`byte_C337` n'a que 5 occurrences** dans tout le programme (deux écritures effectives,
   l. 182717 et 183306 ; deux lectures, l. 139695 et 139852 ; et un passage par `byte_C8F8`).
   Une grandeur aussi centrale qu'une vitesse véhicule serait consommée par des dizaines de
   fonctions (limiteur, régulateur, EGR, FAP, rapport).

⇒ **Je retire le candidat `C337` de l'étape 27.** C'était une piste, ce n'était pas une réponse.

## 3. Le power latch est **hors du dump** — et voici la preuve

J'ai cherché qui écrit le drapeau qui conditionne tout le programme.

| test | résultat |
|---|---|
| occurrences de `word_FD0C` | **160** |
| `jnb/jb word_FD0C.15` (test global d'extinction) | **oui**, dans toutes les tâches (l. 127428, 129681, 131312, 132966, 148370, 151643, 153174, 153488, 154420, 156265, 160932…) |
| **écrivains** de `word_FD0C` (`mov`/`or`/`and`/`add`/`sub`/`xor`) | **AUCUN** |
| `bset`/`bclr` sur `word_FD0C.x` | **AUCUN** |

Un mot lu 160 fois et écrit zéro fois : son écrivain **n'est pas dans le code fourni**.
Il est donc dans la **bibliothèque bas niveau absente** (`0x0000-0x7FFF`, 100 % de `0xC3`, étape 22).

**Conséquence directe pour ta liste** (km, freeze frames, DTC, immo/déverrouillage, suie, cérine) :
ces fonctions passent très probablement par la **même couche non fournie**. On ne les lira pas
ligne à ligne. **Mais on peut en dresser la carte autrement** — c'est l'objet du §5.

## 4. Régulateur et Vmax — ce que le balayage donne, et pourquoi il échoue

| hypothèse testée | résultat |
|---|---|
| immédiats 240 / 245 / 250 dans le code | **aucun** — les `#0F0h` trouvés sont des **masques de quartet** (`and r12, #0F0h`) |
| couples seuil / hystérésis avec seuil 220-260 dans la calibration | `0xE0B18` = **257/256** ; `0xE40DC` = **257/255** |
| couples 145-215 (candidat régulateur) | `0xEB908` = **165/163** ; `0xEB91E` = **150/148** |

**Pourquoi je rejette les deux plus beaux** : `0xEB908` et `0xEB91E` sont **à l'intérieur de
grilles** — on lit autour : `147, 152, 157, 157, 166, 173…` et `…148, 152, 153, 165, 165, 163, 156`.
Le « 150 puis 148 » est une **rencontre fortuite** dans une suite de valeurs, pas un seuil.
C'est exactement le piège que tu m'as demandé d'éviter.

Et `0xE40DC` / `0xE0B18` n'ont **aucun handle** ni référence directe (0 occurrence de `0E40DCh`,
`0E0B18h`), donc je ne les attribue pas.

**Note méthodologique importante** : la zone `0xE0A00-0xE0C00` est une **zone de tables indexées par
offset** — c'est là que vivait la table de sauts `0xE0A62`, atteinte par `add r4, #0A62h`. Une
recherche de référence littérale y échoue **par construction**. C'est une leçon de l'étape 21 qu'il
faut réappliquer : **ne pas conclure « inutilisé » après un grep littéral dans cette zone.**

⇒ **Méthode à changer pour le Vmax et le régulateur** : ne pas chercher le seuil, chercher le
**coupeur** — l'endroit où la quantité est annulée. Pour le Vmax, c'est une comparaison sur la
vitesse qui force la quantité à zéro ; pour le régulateur, c'est une machine d'état qui lit les
contacteurs frein/embrayage.

## 5. Ce qu'on peut faire malgré la bibliothèque absente

L'idée : les **variables** sont lisibles (elles sont lues et écrites par le code présent) et les
**contrats d'appel** sont lisibles (arguments passés dans `r12/r13/r14` et sur la pile). Donc :

| objectif | méthode |
|---|---|
| carte de l'EEPROM (contenu) | inventorier les `calls 0, …` dont un argument est une **adresse RAM** et l'autre une **longueur** — c'est la signature d'une sauvegarde de bloc |
| compteur kilométrique | chercher son **consommateur** : il est lu (affiché/publié) donc présent ; remonter à son incrément |
| suie / cérine FAP | ce sont des **variables lues** (pour le calcul des régénérations) : on peut les identifier par leur valeur et leur usage |
| DTC / freeze frames | la table des codes défaut doit être dans la zone de calibration (séquence de mots) — à chercher par structure, pas par nom |

## 6. Une trouvaille au passage — un bloc de paramètres RCO

En examinant `0xE40D4` :

```
00 C3 | 03 03 | 0A 00 | 01 02 01 01 FF 00 01 00 |
32 00 | 14 00 | 55 00 | 32 00 | 14 00 | 55 00 | FF FF | 00 00 | 55 00 | FF FF | 00 00 | 55 00 | FF FF
```

`tag = 0xC300`, puis `10`, puis un motif **50 / 20 / 85** (= 0,50 / 0,20 / 0,85) **répété**, séparé par
`0xFFFF` et `0x0000`. Des **rapports cycliques** (0,50 / 0,20 / 0,85) répétés par variante : cela
ressemble à un **bloc de paramètres de commande RCO** — cohérent avec ta règle « EGR et N75 sont
commandés en RCO, pas en unité physique ». À décoder proprement à la prochaine étape.

## 7. Prochaines actions, par ordre de rendement

1. **`word_1B5E`** : la carte 2-D qui produit `byte_C8F8` → tranchera couple / vitesse.
2. **Le bloc RCO `0xE40D4`** (tag `0xC300`) : identification des trois rapports cycliques.
3. **Inventaire des `calls 0, …` avec (adresse, longueur)** → carte de l'EEPROM sans le code.
4. **Le coupeur du Vmax** : chercher la remise à zéro de la quantité, pas un seuil.
