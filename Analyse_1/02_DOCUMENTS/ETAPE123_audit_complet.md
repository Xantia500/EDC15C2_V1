# ÉTAPE 123 — AUDIT COMPLET : re-vérification de tout le travail depuis le premier prompt

Audit mené sur trois niveaux indépendants : **données brutes** (`edc.bin`), **code** (`clean.asm`),
**documents** (122 étapes + catalogue). Chaque niveau est re-testé **sans faire confiance aux étapes
précédentes**.

---

## 1. Niveau 1 — Les données : 44 contrôles automatiques

Script de vérification rejoué contre `edc.bin` : **44 PASS / 0 FAIL réel**.

| famille | contrôles | résultat |
|---|---|---|
| identité et format | taille 524 288 o · HW `0281010877` · SW `1037353776` · `BOOT` | ✅ |
| table des pointeurs | 19 pointeurs vérifiés (0x1B66, 0x1B68, 0x1B6A, 0x1B40, 0x1B5E, 0x1446, 0x1448, …) | ✅ 19/19 |
| cartes : axes | `0xE8B50`/`0xE8BD4` (0xC42E × 0xC6DA) · `0xE8444` (0xC42E × 0xC3E6, 16×16) · `0xE8A06` (0xC42E × 0xD3D4, axe 0…8000) · `0xE83F4` (0xC42E, n=19) | ✅ |
| valeurs | seuil `0xE8C58` = **539** · max `0xE83F4` = **7430 à 2000 tr/min** · `0xE89A8` = **10000 partout** | ✅ |
| structure | pas de 162 o (`0x1446`→`0x1448` = 0xA2) · duplication `0xE2788`≡`0xF2788` · `0xE2078`≡`0xF2078` | ✅ |
| fichier patch | `edc_2nde_20kmh.bin` = **8 octets**, `2500→2000` et `768→380` aux 4 offsets | ✅ |

**Trois « échecs » du premier passage étaient des bugs de mon test**, pas des erreurs de fond :

| test | cause | réalité |
|---|---|---|
| « HW absent de 0xFCC00 » | j'ai lu l'**offset fichier** au lieu de l'**EA** | `fo 0x7CC00` = **EA 0xFCC00** ✔ |
| « entrée handle 0x1400 ≠ 0 » | le catalogue dit « handle 1400 = **entrée n°0** », pas « valeur = 0 » | 1re entrée = `0x100A` ✔ |
| 4 contrôles de patch | mon `o+0xA` re-testait le même offset | patch correct ✔ |

**La règle d'adressage est confirmée sur 5 objets** : `HW 0x7CC00→0xFCC00` · `SW 0x6BFB0→0xEBFB0` ·
`0x7BFB0→0xFBFB0` · `0x7FEF0→0xFFEF0` · `BOOT 0x7FF08→0xFFF08`.

### ★ Validation croisée indépendante

Deux méthodes **sans lien** convergent :

| méthode | résultat |
|---|---|
| table de pointeurs (`0x61400`), entrées 0-5 | `0xE100A · 0xE101E · 0xE1026 · 0xE104A · 0xE106E · 0xE1082` |
| mon scan par signature `[tagY][nY][axeY][tagX][nX][axeX]` | **exactement les mêmes 6 adresses** |

Et **85/85** des cartes détectées sont pointées par un handle ⇒ le scan n'invente pas de cartes.

---

## 2. Niveau 2 — Les corrections que l'audit impose

### ★★ C1. Mon scan des cartes était **incomplet** (bug de borne)

Mon test rejetait tout axe dont la valeur dépassait `60000`. Or certaines valeurs sont **signées**
(`61046` = −4486). Correction appliquée : **85 → 86 cartes** (ajout de `0xE7D44`, la seule que le
catalogue avait et que je n'avais pas).

### ★★ C2. Le catalogue est **incohérent avec lui-même** sur le nombre de cartes

| endroit | chiffre |
|---|---|
| § 5, titre « table exhaustive » | **66 cartes** |
| § 10, errata #57 | « sous-décompte… **total 91 cartes** » |
| mon scan corrigé | **86 cartes à axes explicites** |

⇒ **§ 5 est périmé et doit être remplacé** ; l'écart 91 − 86 = **5 cartes** (à plat sans axes, ou à
en-tête masqué) reste à identifier nommément. **La mention « exhaustive » de § 5 est fausse.**

### ★★ C3. Les citations de lignes sont le point faible du dossier

Audit automatique : **195 citations vérifiables**, dont **38 exactes au sens strict (19,5 %)** ;
la grande majorité est **décalée de 1 à 5 lignes**, quelques-unes beaucoup plus.

| citation | annoncé | réel | écart |
|---|---|---|---|
| plafond fumée `C698 := C690` | l.185814 | **l.185833-185838** | **−20 lignes** |
| souhait `r12 = C91C` | l.195503 | l.195501 | −2 |
| `byte_C8F8` | l.182815 | l.182814 | +1 |
| `r12 = C640` | l.140223 | l.140224 | −1 |
| `C680 := C698` | l.186651 | l.186652 | −1 |
| `unk_1D6C` (limiteurs) | l.180262 | l.180281 | −19 |

**Recommandation** : citer désormais **symbole + adresse EA** (`mov word_C698, r5` dans `loc_B4D1A`,
EA `0xB5838`) et ne donner le n° de ligne qu'en secours — un désassemblage régénéré décale tout.

### ★ C4. `C690` n'est pas un plafond unique mais **neuf**

`cmp …, word_C690` apparaît à **l.185133, 185500, 185835, 186059, 186123, 186335, 186645, 187403,
187510** ⇒ la fumée est appliquée **en 9 points** de la chaîne. J'avais écrit « un site » : sous-estimé.

### ★★★ C5. Correction de ma part : **`C3E6` n'est PAS prouvé être la masse d'air**

Dans l'Étape 120 j'ai nommé `C3E6` « masse d'air » **à partir de la seule plage** 3000…11500. C'est
**exactement l'erreur de méthode** que le projet a déjà consignée :

> **Errata #56 du catalogue** : « `word_C3D2`, `word_C3BA`, `word_C3B0` = masse d'air (mg×10) » —
> *« inféré de la seule plage… **ERREUR DE MÉTHODE : une plage ne prouve rien.** »*

⇒ `C3E6` est **rétrogradé au niveau `?`** (grandeur inconnue). Ce qui reste vrai : c'est l'axe Y de
`0xE8444`, il vaut **10000 à l'initialisation** (l.131320) et il **n'est jamais réécrit dans la zone
désassemblée**. **La smoke map est donc confirmée comme structure, pas comme sémantique d'axe.**

Pour mémoire, les trois variables que l'errata #56 a correctement reclassées en **températures** sont
`C3D2` (LDR), `C3BA` (air d'admission), `C3B0` (carburant) — mes Étapes 120-122 les utilisent bien
comme températures. ✔

---

## 3. Niveau 3 — Ce que le croisement a révélé (inédit)

### ★★★ Les deux cartes de souhait ne diffèrent qu'en **5 cases**

Comparaison intégrale `0xE8B50` (rapport ≥ 539) vs `0xE8BD4` (rapport < 539) : 8 × 6 = 48 cases,
**5 différences, toutes en colonne 1**.

Axes : régime `0 · 600 · 750 · 1000 · 1300 · 1750 · 2250 · 5000` — pédale `118 · 2000 · 4000 · 6000 ·
8000 · 10000`.

La colonne 1 = **pédale 20 %**. Les 5 cases réduites :

| régime | 750 | 1000 | 1300 | 1750 | 2250 |
|---|---|---|---|---|---|
| carte A (mm³) | 24,00 | 21,32 | 18,44 | 15,20 | 12,60 |
| carte B (mm³) | 23,50 | 17,82 | 13,44 | 10,70 | 9,10 |
| écart | −2,1 % | −16,4 % | **−27,1 %** | **−29,6 %** | −27,8 % |

**Conséquences à assumer** :

1. La « limitation 1re/2de » codée par la bascule `539` **n'agit qu'à 20 % de pédale**, entre 750 et
   2250 tr/min. À 40 % de pédale et plus, **les deux cartes sont identiques**.
2. Donc **patcher `0xE8BD4` serait quasi invisible** : mon conseil de l'Étape 121 (« le levier pour la
   1re/2de ») est **trop optimiste** — il faut le nuancer.
3. En revanche la **smoke map `0xE8444`** (plafonnement en 9 points, plage 15…76 mm³) reste un levier
   réel, lui.

---

## 4. Tableau de confiance — état consolidé du dossier

| affirmation | niveau | preuve | statut après audit |
|---|---|---|---|
| identité HW/SW, adressage, duplication E/F | **lu** | 5 objets concordants | ✅ confirmé |
| table des pointeurs = variables RAM 0x1400-0x1FFF | **lu** | 19/19 + déréférencement `[r4]` | ✅ confirmé |
| souhait = `0xE8B50`/`0xE8BD4` selon `C576` vs **539** | **lu** | l.186826-846 + `[0x1B6A]` = 539 | ✅ confirmé |
| smoke map = `0xE8444` (régime × `C3E6`) → `C690` | **lu** | `1B40`→`0xE8444`, l.181914 | ✅ confirmé (structure) |
| … mais `C3E6` = masse d'air | **?** | plage seule | ❌ **rétrogradé** |
| `C690` plafonne la quantité | **lu** | 9 sites `cmp …C690` | ✅ confirmé, portée élargie |
| commande de pompe `0xE8A06` = f(régime, IQ) → `byte_C8F8` | **lu** | l.182807-814 | ✅ confirmé |
| triplet `D418`/`D41A`/`D41C` → écarts `C63A/C63C/C63E` | **lu** | l.189176-188 | ✅ confirmé |
| conversion finale `unk_20AC` → octets `C81B…C829` | **lu** | l.139993, 140223 | ✅ confirmé |
| courbe plein gaz `0xE83F4` : 74,3 mm³ **à 2000 tr/min** | **lu** | règle `valeur[k] ↔ axe[k+1]` | ✅ confirmé |
| `0xE2078`/`0xE211A` utilisés comme tables 2-D | **lu** | 12 sites `word_1D94` | ✅ confirmé (usage) |
| découpage interne 7×8 de ces blocs | **?** | arithmétique seule, format non conforme | ⚠️ hypothèse |
| « cartes couple → IQ » | **retiré** | E27 | ❌ abandonné |
| checksums | **abandonné** | E.112 | ❌ gelé |

---

## 5. Cohérence documentaire

| constat | action |
|---|---|
| Erratas **E27 à E31** présents dans les Étapes 118-122 | ✅ rien à faire |
| `CATALOGUE §5` annonce 66 cartes, `§10` annonce 91 | ⚠️ **à corriger** (§5 périmé) |
| Étapes 116-117 (interprétation « couple → IQ ») restent lisibles telles quelles | ⚠️ elles portent l'errata en tête, mais il faudrait un bandeau « PÉRIMÉ » |
| Étapes 108-115 fondées sur les citations de lignes approximatives | ⚠️ **substance OK, précision à reprendre** |
| Les 122 documents n'ont pas de table des matières unique | ⚠️ à produire |

---

## 6. Ce qui reste ouvert, par ordre de coût/bénéfice

| # | question | pourquoi c'est bloquant | coût |
|---|---|---|---|
| 1 | **`C3E6`** et **`0xC83E`** : qui les écrit ? | nomment l'axe air et l'axe du limiteur | élevé — **hors zone désassemblée** |
| 2 | `[word_1660]` et `[word_1658+2]` : paramètres de `unk_20AC` | dernière inconnue de la chaîne injecteur | faible — les blocs sont pointés |
| 3 | les **5 cartes** (91 − 86) sans axes explicites | complétude de l'inventaire | moyen |
| 4 | découpage réel des **blocs 162 o** | saurait si `0xE2078` est une grille | moyen |
| 5 | reprise des **citations de lignes** des Étapes 108-115 | traçabilité | faible mais fastidieux |

---

## 7. Plan de remise à niveau

1. **Corriger `CATALOGUE §5`** : remplacer « 66 cartes » par « 86 à axes explicites + 5 à identifier
   (total 91) », avec renvoi au CSV `inventaire_cartes_2D_axes_v2.csv`.
2. **Publier la table de correspondance ligne → symbole → EA** pour les 40 affirmations structurantes
   (fin des citations fragiles).
3. **Bandeau « PÉRIMÉ »** en tête des Étapes 116 et 117.
4. **Nuancer l'Étape 121 §9** : `0xE8BD4` n'agit qu'à 20 % de pédale ⇒ le levier réel est `0xE8444`.
5. Attaquer les points 2 et 3 ci-dessus (coût faible).

---

## 8. Verdict global

| niveau | état |
|---|---|
| **données** | **solide** : 44/44 contrôles, 2 méthodes indépendantes convergent, patch exact |
| **code** | **solide sur la substance**, **fragile sur la localisation** (19,5 % de citations exactes) |
| **documents** | **bon** : 5 erratas bien tracés ; 2 défauts (catalogue §5, bandeaux manquants) |
| **discipline de méthode** | **une récidive détectée et corrigée** : nommer une grandeur par sa plage (`C3E6`) |

**Conclusion** : la chaîne du souhait aux injecteurs, la smoke map, les températures, la commande de
pompe et le patch sont **tenus par des preuves**. Ce qui ne l'est pas est désormais **explicitement
étiqueté `?`**. Le défaut principal du dossier n'est pas une erreur de fond mais **la précision des
références** — corrigeable sans nouvelle analyse.
