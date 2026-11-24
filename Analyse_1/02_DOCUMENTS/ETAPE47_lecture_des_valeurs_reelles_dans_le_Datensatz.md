# ÉTAPE 47 — ★ Lecture des **valeurs réelles** : ce que contiennent les blocs de calibration

*Méthode : `handle (word_xxxx) → index → valeur de la table 0xE1400 → EA → offset fichier = 0x60000 + valeur`.*

---

## 0. Le chaînage, vérifié

La table des pointeurs est à l'adresse `0xE1400` (**offset fichier `0x61400`**), une valeur 16 bits par
handle. Les valeurs sont des **décalages dans le Datensatz**, dont la base logique est `0xE0000`
(**offset fichier `0x60000`**).

| handle | index | valeur | EA logique | offset fichier | contenu |
|---|---|---|---|---|---|
| `word_142A` | 42 (0x2A) | `0x122C` | `0xE122C` | `0x6122C` | bloc de moniteur |
| `word_1474` | 116 (0x74) | `0x226E` | `0xE226E` | `0x6226E` | bloc « 250 » |
| `word_1818` | 1048 (0x418) | `0x4962` | `0xE4962` | `0x64962` | **numéros de bits** |
| `word_18F2` | 1266 (0x4F2) | `0x5316` | `0xE5316` | `0x65316` | seuils 120 / 2 |
| `word_18F6` | 1270 (0x4F6) | `0x5368` | `0xE5368` | `0x65368` | (question ouverte) |
| `word_1952` | 1362 (0x552) | `0x63BE` | `0xE63BE` | `0x663BE` | (question ouverte) |

**Les six handles se résolvent proprement** — la méthode est donc fiable.

---

## 1. ★ ERratum important : ce ne sont **pas des structures**, ce sont des **suites de mots**

J'ai écrit aux étapes 42, 43 et 46 que `word_142A` / `word_1474` / `word_18F2` pointaient vers des
**structures** avec des champs typés. **La lecture du contenu montre que c'est faux.**

Le bloc à `0xE122C` est une **simple suite de nombres 16 bits consécutifs** :

```
+0x00 0x0D67   +0x02 0x00DC   +0x04 0x0064   +0x06 0x0064
+0x08 0x2828   +0x0A 0x00C8   +0x0C 0x003C   +0x0E 0x0093
+0x10 0x00C8   +0x12 0x00FA   +0x14 0xFB50   +0x16 0x04B0
```

Le code lit `[r4]`, `[r4+#2]`, `[r4+#4]`, `[r4+#6]` : ce sont **le 1er, 2e, 3e et 4e nombre** de la
suite, pas des champs d'une structure.

**Correction retenue** : le modèle correct est **« handle → bloc de paramètres indexé par un
décalage d'octets »**. Cela reste `handle + offset`, mais **`offset` est un simple indice**, et il n'y
a **aucun typage** — ce qui est cohérent avec la nature du Datensatz (une suite de nombres, étape 1).

Cela **affaiblit** le « format de descripteur partagé » que j'annonçais à l'étape 46 §4 : deux blocs
portant un seuil à `+6` n'est pas nécessairement un en-tête commun, c'est peut-être une coïncidence
d'indices. **Je retire l'hypothèse du format partagé.**

---

## 2. ★★ `word_1818` résolu : les cinq bits sont **2, 1, 0, 8, 15**

Contenu à `0xE4962` : `02 01 00 08 0F C3 FF FF ...`

La boucle de l'étape 43 §4 lit `[word_1818 + n]` pour `n = 0…4` :

| n | octet lu | bit posé | mot |
|---|---|---|---|
| 0 | **0x02** | bit **2** | `word_C548` |
| 1 | **0x01** | bit **1** | `word_C548` |
| 2 | **0x00** | bit **0** | `word_C548` |
| 3 | **0x08** | bit **8** | `word_C54A` |
| 4 | **0x0F** | bit **15** | `word_C54A` |

⇒ **`word_C548` = bits 0, 1, 2 ; `word_C54A` = bits 8, 15.** (Le `0xC3` qui suit n'est plus lu : la
boucle s'arrête à 5.)

**C'est un résultat concret, vérifiable et non ambigu.** La question « que sont ces 5 entrées ? » se
réduit maintenant à : **que sont les 5 drapeaux de `0xC9F3` ?** — et leurs emplacements dans les deux
mots de sortie sont désormais fixés.

*Observation* : les bits **0, 1, 2** sont contigus, puis viennent **8** et **15**. Une répartition
0/1/2 + 8/15 est cohérente avec **3 états + 2 drapeaux indépendants**.

---

## 3. ★★ La valeur **250** est bien dans la calibration de **ce** calculateur

`word_1474` (EA `0xE226E`) contient :

```
+0x00 0x0168 (360)      +0x02 0x003C (60)       +0x04 0x003C (60)
+0x06 0x0145 (325)      +0x08 0xC300            +0x0A 0x07D0 (2000)
+0x0C 0x0708 (1800)     +0x0E 0x05DC (1500)     +0x10 0x0000
+0x12 0x05DC (1500)     +0x14 0x1388 (5000)     +0x16 0x1388 (5000)
+0x18 0x00FA (250)      +0x1A 0x00FA (250)
```

Et le code lit `[word_1474 + 0x1A]` → **`word_D6FA = 250`** (l. 156040-156043).

**⇒ La constante 250 n'est pas seulement un littéral de code (étape 46 §2) : c'est une valeur de
calibration inscrite dans le Datensatz de ce calculateur, à deux emplacements voisins (`+0x18` et
`+0x1A`).**

**Sur la question « Vmax 240 ou 250 ? »** : le doute sur la **présence** de 250 est levé — elle est là,
en calibration, et le code la charge dans une variable de travail. **L'unité reste non établie** (km/h
plausible, mais 250 pourrait être un autre plafond). Je retiens donc : **250 est une valeur calibrée
de ce calculateur, à confronter à la mesure**.

*Note* : les valeurs voisines **2000, 1800, 1500, 1500, 5000, 5000** se lisent naturellement comme des
**régimes (tr/min)**. Si le bloc est homogène, un plafond de régime à 5000 tr/min voisine un plafond à
250 — mais **ce n'est pas une preuve d'unité** pour autant.

---

## 4. ★★ `word_C5B8` est une **petite** grandeur — le kilométrage est exclu, définitivement

`word_18F2` (EA `0xE5316`) :

```
+0x00 0x0000    +0x02 0x001E (30)     +0x04 0xC380    +0x06 0x0ADD (2781)
+0x10 0x0000    +0x12 0x0017 (23)     +0x14 0x0078 (120)    +0x16 0x012A (298)
+0x38 0x0002 (2)
```

Les deux comparaisons du code (l. 162150 et 162350) deviennent :

```asm
         cmp  [word_18F2+0x14] (=120), word_C5AE      ; la MOYENNE des 5
         cmp  [word_18F2+0x38] (=2),   word_C5B8      ; la valeur courante
```

⇒ **`word_C5B8` et sa moyenne sont comparés à 2 et à 120.** Ce sont donc des **grandeurs petites**,
de l'ordre de quelques unités à quelques dizaines.

**Conséquence : `word_C5B8` n'est PAS un kilométrage.** L'hypothèse, laissée ouverte à l'étape 46 §5,
est **écartée** : un kilométrage ne se compare pas à 2.

**Ce qui reste compatible** avec : défaut initialisé à **250**, seuils **120** et **2**, historique à
5 niveaux persisté, machine d'état `byte_C30D` bornée entre 2 et 7 :
- un **niveau** (additif, suie, service) exprimé en % ou en unités ;
- un **compteur d'événements** ;
- une **température**.

**Je ne tranche pas** — mais la fourchette est maintenant **fermée**, et c'est un progrès net.

---

## 5. Une paire symétrique dans le bloc de moniteur

Toujours à `0xE122C`, aux offsets `+0x14` et `+0x16` :

```
+0x14  50 FB  → 0xFB50 = −1 200  (signé)
+0x16  B0 04  → 0x04B0 = +1 200  (signé)
```

**Une paire exactement symétrique ±1 200.** Si l'unité est `×10`, cela donne **±120,0** — et 120 est
précisément la borne que tu avais citée pour tes axes de température (**−40…+120 °C**). Si l'unité est
`×100`, cela donne **±12,00**.

Suivent `+0x18 = 0x0019 (25)`, `+0x1A = 0x0002 (2)`, `+0x1C = 0x0032 (50)` — **25 et 50**, valeurs
typiques de seuils thermiques (25 °C, 50 °C).

**Je signale la cohérence sans conclure** : une paire symétrique est la signature d'une **plage
d'encadrement**, et le voisinage immédiat de 25 et 50 va dans le sens d'une grandeur thermique.

---

## 6. Bilan

| question | état |
|---|---|
| `word_1818` → bits des 5 entrées | **2, 1, 0, 8, 15** ✔ (fermé) |
| nature des blocs de calibration | **suites de mots indexés**, pas des structures ✔ (erratum) |
| format de descripteur partagé | **hypothèse retirée** (étape 46 §4) |
| présence de 250 en calibration | **confirmée** ✔ |
| unité de 250 (Vmax ?) | non établie |
| `word_C5B8` = kilométrage | **écarté** ✔ |
| `word_C5B8` = ? | petite grandeur, fourchette fermée |
| PIN / VIN / immo | hors d'atteinte |

---

## 7. Prochaines actions

1. **`0xC9F3` (les 5 drapeaux)** : qui les écrit ? Avec les bits 0/1/2/8/15 connus, la nature des 5
   entrées devient accessible.
2. **`word_18F6`** (EA `0xE5368`) : contient `55 FE` = **−427** répété **trois fois** puis `D3 FE` =
   **−301**. Une valeur **répétée trois fois** est la signature d'un de nos enregistrements triples.
   **À vérifier en priorité** — c'est peut-être la même valeur écrite en 3 exemplaires.
3. **`word_1952`** (EA `0xE63BE`) : contient `F7 FF` (−9), `E8 03` (1000), `48 F4` (−3000),
   `0A 00` (10) — un mélange qui ressemble à un **bloc hétérogène**, donc à une frontière de blocs.
   Utile pour **valider le découpage** du Datensatz.
4. Confronter `[word_1474+0x18]` et `[+0x1A]` : **deux 250 voisins** — l'explication la plus simple
   est *valeur + borne*, mais **à vérifier**, pas à supposer.
