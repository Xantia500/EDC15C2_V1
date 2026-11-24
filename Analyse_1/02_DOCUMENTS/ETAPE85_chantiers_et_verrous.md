# ÉTAPE 85 — Où j'en suis : les cartes trouvées, et les 9 points sur lesquels je bute

> Document de travail, fait pour que tu puisses regarder de ton côté. Chaque point « bloqué » contient
> l'adresse exacte, la preuve disponible, et **ce qui le trancherait**.

---

## A. Les cartes trouvées / confirmées récemment

| # | carte | adresse | structure | ce qui est **prouvé** | ce qui reste |
|---|---|---|---|---|---|
| 1 | **Avance (SOI)** | `0xE2816` | 16 × 16, 229/256 non nuls, **−37 … 1067** | axes **régime `C42E` × charge `C6A2`** par `unk_2F56`/`unk_2FAC` (l.239933-239968, 241049) ; sortie → `D51A` = **identifiant `0x1F4D`** | l'**unité** (°CA) |
| 2 | **Préchauffage** | `0xE868C` | 6 × 6, `0xC3D2` × `C562` | grille : 0, **9230 / 8150 / 4210 / 1280**, effondrement avec la température ; taille 52 = écart exact | ce qu'est `C562` |
| 3 | **Courbe `C3AE`** | `0xE86F4` | `[0xC3AE][10][0 50 300 500 600 1000 1150 1250 1750 1760]` | structure 12 mots = écart exact | nature de `C3AE` |
| 4 | **Couple de cartes 14 × 18** | `0xE2B62` / `0xE2D5A` | 14 × 18 = 252 | `sub_D4D0A` (l.241558) : variantes **`byte_C2C1` = 1 → h `0x14D0`**, **3 → h `0x14D2`** ; axes **`C7C2` (14 pts, 1190…13500) × `C78A` (18 pts, 0…7900)** ; positions d'interpolation en RAM `0xE5B0` / `0xE5B6` | ce que sont `C7C2` et `C78A` |
| 5 | **3 grilles 9 × 9** | `0xE130E` · `0xE2078` · `0xE211A` | 81 mots, 64 non nuls, max 15437 / 17920 / 13184 | consommateurs `word_144A/144C/144E` (l.177865-177910) : `r7 = X − word_C678` → `unk_1D6C(…, word_144E)` → `word_1D94(0xC83E, …)` | l'axe réellement associé à chacune |
| 6 | **53 axes de température** | — | — | **clé Kelvin ×10 validée : 283/290 valeurs entières (98 %)** ⇒ `T°C = v/10 − 273,1` | — |
| 7 | **Consigne de suralimentation** | `0xE7A00` | 16 × 10, 800 → 2200 mbar | (étape 78) | — |
| 8 | **Carte de fumée** | `0xE8444` | — | (étapes 79/80) — base de `C68A` | — |
| 9 | **Limiteur de suralimentation** | `0xE7828` | 10 × 10, max 2370 mbar | (étape 78) | — |

## B. Les 9 points où je bute

### ① Le couple 14 × 18 est indexé par… l'avance elle-même
**Nouveau, trouvé à l'instant** : `word_C78A ← word_F99E` (l.241148), et `word_F99E ← r15` (l.240948)
où `r15 = C756 + C73E + C74E + C748 + C766 + C770` — **l'accumulateur d'avance**.
Puis `calls sub_D4D0A`, et `r14 += r4` : la sortie de la carte **se rajoute** à l'avance.

⇒ la carte 14 × 18 est une **correction d'avance = f(pression `C7C2`, avance `C78A`)**.
**Ce qui trancherait** : logger l'identifiant **`0x1F64`** (= `C78A`) et vérifier qu'il suit bien l'avance.

### ② `C7C2` — l'axe à 14 points, **aucun identifiant**
`1190 1200 2000 3000 4000 5000 6000 7000 8000 9000 10000 11000 12000 13500`
Si ×0,1 bar → **119 → 1350 bar** = plage pile d'un **rail common-rail**. Mais `C7C2` n'est **pas publié**
au diagnostic (absent du dictionnaire des 356 identifiants) ⇒ soit une variable interne, soit un axe
« virtuel ».
**Ce qui trancherait** : une seule chose — comparer `C7C2` à la pression rail mesurée (`C612`/`C614`) sur
une log. S'il colle → c'est le rail ; sinon c'est la pression d'admission ou une consigne.

### ③ `C3AE` = **`[0xF884]`**
`mov r9, #0F884h` / `mov r9, [r9]` / `sub_C4AAE(r0 = word_1548, r9)` / `word_C3AE ← r9` (l.214368-214374).
`0xF884` n'est pas un symbole nommé et sert de **pointeur de structure** (aussi en l.213595, 213974, 217875).
**Ce qui trancherait** : identifier le bloc `0xF880` — c'est probablement un **résultat de mesure brut**
(ADC ou compteur), donc `C3AE` en serait la version corrigée.

### ④ `C562` — l'axe X de la carte de préchauffage
Écrit 3 fois pour 100 lectures : `← C3FA` (`sub_CF8C8`), `← 0xFF` (secours), `← MDL`. Et `C3FA` vaut **0**
au reset (`[0xE400A]`) et **8000** quand l'adaptation l'autorise (`[0xE2260]`).
⇒ un **paramètre appris**, pas une mesure.
**Ce qui trancherait** : `C562` n'a pas d'identifiant non plus. Regarder s'il évolue avec les **kilomètres**
(→ km depuis dernière régénération) ou avec le **temps** (→ heures).

### ⑤ `C63C` — l'axe 9 points, identifiant `0x2109`
`0 1707 3413 5120 6827 8533 10667 12800 15360` → si ÷10 : **0 → 1536 bar**, pas régulier au début.
Écrit à 0 (l.188955) puis `← r2` (l.189185).
**Ce qui trancherait** : logger l'identifiant **`0x2109`**.

### ⑥ `C678` — le seuil soustrait avant les grilles 9 × 9
`sub r7, word_C678` (l.177879, 177955, 180292) : c'est un **écart à une référence**. 13 références, aucune
écriture tracée.
**Ce qui trancherait** : trouver qui écrit `C678` (probablement par un handle, dans le bloc `0xE1129+180`).

### ⑦ Les **1 079 objets sans en-tête** (sur 1 303)
C'est le gros morceau restant : 83 % des objets du Datensatz n'ont **ni tag, ni axe, ni compteur**.
La méthode des écarts est morte (étape 83). Il faut passer par les **consommateurs** :
`unk_2F56` (position) + `unk_2FAC` (grille nue) — c'est le couple qui vient de résoudre le 14 × 18.
**Ce qui trancherait** : rien de ton côté ; c'est du travail systématique sur `clean.asm`.

### ⑧ Le verrou des **DPP**
`DPP0 = 0x22`, `DPP1 = 0x21`, `DPP2 = 0x24 / 0x48`, `DPP3 = 3`. Sans la traduction
`DPP × 0x4000 → adresse linéaire`, **toutes les lectures indirectes** restent ambiguës.
**Ce qui trancherait** : la **carte mémoire** du boîtier (taille de RAM externe, adresse de l'EEPROM).
Si tu as la référence du microcontrôleur (C167 ?) et la taille des mémoires, je boucle ça en une étape.

### ⑨ `C3BA` — la troisième température
Identifiant **`0x0F01`**, **12 axes** la portent, décodée avec la même clé Kelvin ×10.
**Candidats** : T air d'admission (P0110/P0111), T huile (P0196-98), T EGR.
**Ce qui trancherait** : ses **14 DTC** (déjà extraits dans `capteurs_par_DTC.csv`) — si on y trouve
`P0110`, c'est l'air d'admission.

## C. Ce que tu peux vérifier de ton côté, par ordre de rentabilité

| priorité | action | ce que ça débloque |
|---|---|---|
| **1** | logger **`0x1F4D`** (avance) et le comparer à une avance mesurée | l'**unité** de la carte d'avance |
| **2** | logger **`0x1F64`** (= `C78A`) | confirme que le 14 × 18 est indexé par l'avance |
| **3** | logger **`0x2109`** (= `C63C`) | nomme l'axe 9 × 9 |
| **4** | comparer `C7C2` (si tu peux l'atteindre) au rail | tranche ① et ② |
| **5** | me donner **référence du microcontrôleur + taille RAM/EEPROM** | débloque le verrou ⑧, donc tout le reste |
