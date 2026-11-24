# ÉTAPE 18 — Les cartes de couple par rapport : décodées, et ce qu'elles disent vraiment

Point de départ : tes quatre adresses `0x6841E`, `0x68928`, `0x68968`, `0x689A8`.
**Convention** : ce sont des **offsets fichier** ; dans notre référentiel (`EA = offset + 0x80000`) cela
donne **EA `0xE841E`, `0xE8928`, `0xE8968`, `0xE89A8`**.
Ce sont, dans chaque cas, **exactement la première valeur** du tableau — ton repérage est juste.

Fichiers joints : `cartes_couple_rapport_decoded.csv` (332 lignes, toutes les valeurs décodées).

---

## 1. Le format d'enregistrement, prouvé

```
1-D :  [tag:mot] [n:mot] [axe: n×mot] [valeurs: n×mot]              → 4 + 4n octets
2-D :  [tagY:mot] [nY:mot] [axeY: nY×mot] [tagX:mot] [nX:mot] [axeX: nX×mot] [grille: nY·nX mots]
```

Les enregistrements sont **contigus** : chaque bloc commence juste après le précédent.
**Preuve de la variante 2-D par recoupement indépendant** : la grille de la carte de `0xE8444`
(16×16 mots) occupe `0xE848C … 0xE868B`, et **`0x868C` est précisément l'entrée suivante du
répertoire** du Datensatz (§4). La taille prédite par le format tombe pile sur l'entrée suivante.

---

## 2. La courbe « main torque limiter » — `EA 0xE841E` (en-tête `0xE83F4`)

`tag = 0xC42E` (régime), **n = 19**, axe = `0 50 800 1000 1250 1500 1750 2000 2250 2500 2750 3000 3500 3750 4000 4250 4500 4800 5200` rpm.

| rpm | 0 | 50-800 | 1000 | 1250 | 1500 | 1750 | **2000** | 2250 | 2500 | 2750 | 3000 | 3500 | 3750 | 4000 | 4250 | 4500 | 4800 | 5200 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mm³ | 0 | 35,2 | 44,9 | 58,0 | 66,6 | 70,6 | **74,3** | 72,8 | 70,6 | 68,7 | 68,1 | 64,4 | 62,7 | 62,4 | 56,9 | 53,0 | 47,5 | 0 |

**Contrôle physique de l'unité (mm³ × 100)** : à 2000 rpm, 74,3 mm³ par injection, 4 cylindres
4 temps ⇒ 2000/30 = 66,7 injections/s ⇒ 4955 mm³/s × 0,84 g/cm³ = **4,16 g/s = 15,0 kg/h**.
Puissance à 314 Nm / 1900 rpm = 62,5 kW ; à 215 g/kWh cela ferait 13,4 kg/h.
**Même ordre de grandeur ⇒ ton « mm³ × 100 » est confirmé**, et la bosse à 2000 rpm est bien le
couple maxi du 4HX.

## 3. Les trois courbes par rapport — `EA 0xE8928 / 0xE8968 / 0xE89A8`

Toutes les trois : `tag = 0xC42E`, **n = 15**.

| | axe rpm | valeurs (mm³) |
|---|---|---|
| **0xE8928** (en-tête 0xE8906) | 635 680 800 1000 1250 1500 1750 2000 2250 2500 2750 3000 3500 3750 4000 | 35,2 35,2 35,2 44,9 58,0 66,6 **64,0** 63,5 63,0 63,3 64,0 65,0 64,4 62,7 62,4 |
| **0xE8968** (en-tête 0xE8946) | **identique** | **identique, valeur pour valeur** |
| **0xE89A8** (en-tête 0xE8986) | 635 680 800 1000 1200 1400 1600 1800 2000 2400 2800 3200 3600 3800 4000 | **10 000 partout = 100,00 mm³ = aucune limitation** |

Trois constats que tu dois avoir en tête :

1. **Les deux premières courbes sont identiques octet pour octet.** Une duplication n'a de sens que
   si l'une des deux n'est jamais lue, ou si deux rapports partagent le même plafond. Il faut donc
   **au moins un autre élément** pour distinguer 1ʳᵉ et 2ᵉ : la courbe seule ne le dit pas.
2. **La troisième est un « pas de limite »** (100 mm³), avec un axe **plus fin à bas régime**
   (pas de 200 au lieu de 250) — c'est la signature d'un rapport où le régime monte vite, donc
   **plutôt la 1ʳᵉ**. Cela contredit l'ordre des adresses : les données ne sont donc pas rangées
   dans l'ordre 1-2-3.
3. Sous 1500 rpm les trois courbes **recopient la courbe principale** (35,2 / 44,9 / 58,0 / 66,6).
   Le plafond par rapport n'agit que **au-dessus de 1750 rpm**, où il écrête de 74,3 à 65 mm³.

## 4. Ce que j'ai trouvé en remontant — et un résultat négatif qu'il faut accepter

### 4.1 L'architecture réelle du Datensatz, mesurée

| élément | valeur mesurée |
|---|---|
| table des handles | `EA 0xE1400`, **666 mots u16**, index `i ↔ word_(0x1400+2i)` |
| conversion | **`EA = 0xE0000 + ptr`** (ptr = offset 16 bits dans la banque) |
| plage réellement utilisée | ptr **`0x100A … 0x60F2`** ⇒ **EA `0xE100A … 0xE60F2`** (20 Ko) |
| handles pointant au-delà de `0xE60F2` | **0 sur 666** |
| handles pointant dans `0xE83xx–0xE8Axx` | **0** |
| répertoire des enregistrements | `EA 0xE1B16`, **212 entrées** u16, `831C … 9F96`, EA = `0xE0000 + ptr` |
| tes 3 courbes dans le répertoire | **entrées 31, 32, 33** |
| limiteur + carte 2-D | **entrées 20, 21, 22** |

### 4.2 Le résultat négatif

Recherche exhaustive, sur les deux formes possibles :

- pointeur **32 bits** vers `0xE83F4/0xE841E/0xE8444/0xE8906/…` : **aucune occurrence** ;
- pointeur **16 bits** : uniquement **`0x61B54` et `0x71B54`**, c'est-à-dire le répertoire `0xE1B16`
  et sa copie dans la banque F ;
- **immédiats du code** : `#83F4h`, `#841Eh`, `#8906h`, `#8946h`, `#8986h`, `#848Ch` → **0 occurrence**
  (contrôle : le même grep trouve 307 fois `#2710h`, il fonctionne) ;
- aucun handle `word_14xx` ne mène dans `0xE8xxx` ;
- la zone est **octet pour octet identique** à `0x78400` (copie F) ⇒ elle fait bien partie du
  Datensatz, mais c'est une partie **que le code n'adresse pas**.

**Conclusion, sans détour** : dans **ce** binaire, les courbes de couple par rapport (et le limiteur
principal) sont **présentes dans la calibration mais pas consommées par le logiciel**. Le seul lien
qui les cite est un **répertoire** (outil/flash), pas un accès d'exécution.
Donc **remonter depuis ces courbes ne peut pas donner le rapport engagé ici** : le maillon manque.

Ton raisonnement reste **juste sur le principe** (un limiteur par rapport exige un numéro de rapport
comme *sélecteur*), mais il faut en tirer la bonne conséquence : soit ces cartes appartiennent à
**une autre variante** conservée dans le fichier, soit le limiteur par rapport de *cette* variante
est calculé autrement. Dans les deux cas, **la vitesse ne se trouve pas par cette porte** — et je
préfère te le dire net plutôt que de construire une chaîne plausible mais fausse.

## 5. Ce que la carte 2-D apprend quand même — et un erratum d'échelle

`EA 0xE8444` : `tagY = 0xC42E`, **nY = 16**, axe rpm `0..5200` ; `tagX = 0xC3E6`, **nX = 16**,
axe `3000…11500` ; grille `16×16` à `EA 0xE848C`, **min 0, max 7600 (76,00 mm³)**.
C'est une **carte de pleine charge / fumées** : la quantité max en fonction du régime **et du débit
d'air**. Son maximum (76 mm³ à 2000 rpm) encadre le limiteur principal (74,3) : les deux sont cohérents.

Extraits de la grille (mm³) :

| rpm \ air | 3000 | 5000 | 7000 | 8000 | 9000 | 10000 | 11500 |
|---|---|---|---|---|---|---|---|
| 1000 | 24,3 | 35,0 | 48,0 | 48,0 | 48,0 | 48,0 | 48,0 |
| 1500 | 22,9 | 34,4 | 46,4 | 57,7 | 72,0 | 72,0 | 72,0 |
| 2000 | 22,3 | 34,3 | 46,2 | 55,0 | 70,0 | 75,5 | 76,0 |
| 3000 | 20,5 | 30,0 | 39,0 | 45,8 | 59,0 | 68,9 | 70,0 |
| 4500 | 17,5 | 26,0 | 33,0 | 37,9 | 50,0 | 55,9 | 56,0 |
| 5000 | 0 | 5,0 | 12,5 | 18,0 | 25,0 | 25,0 | 25,0 |

**L'échelle de l'axe d'air est fausse dans notre modèle actuel.** Trois arguments numériques :

1. `word_C3E6` est un mot de **16 bits** : au plus **65 535 mg/s = 65,5 g/s**. Or un 2.2 HDi à
   4000 tr/min et 2 bar absolus avale **≈ 145-160 g/s** (2,2 L × 4000/2 /60 = 0,073 m³/s, ρ ≈ 2,1 kg/m³).
   Un mot de 16 bits **ne peut pas** exprimer le plein régime en mg/s stricts.
2. Cette carte le confirme : à 2000 rpm / 76 mm³ on a 4,16 g/s de gazole ; avec l'axe à 10 000 lu
   strictement en mg/s (10 g/s), λ = 10/(4,16 × 14,5) = **0,17** — physiquement impossible.
3. En lisant l'axe en **10 mg/s** (0,01 g/s), la plage devient **30 … 115 g/s = 108 … 414 kg/h**,
   et λ = 100/(4,16 × 14,5) = **1,66** — valeur de pleine charge réaliste.

⇒ **Erratum d'échelle à vérifier** : la grandeur « débit d'air » est bien celle que tu as identifiée,
mais l'axe de cette carte est en **10 mg/s**, pas en mg/s. Cela vaut pour **toutes** les cartes dont
l'axe X porte le tag `0xC3E6`, donc aussi pour la carte **(débit d'air × dP) → seuil** demandée
précédemment : il faut relire cet axe avec le facteur 10 avant d'interpréter les seuils.

## 6. Prochaines actions (par ordre de rendement)

1. **Balayer la zone réellement consommée `EA 0xE100A–0xE60F2`** à la recherche d'axes de type
   vitesse (0…250/0…300, ou 0…25,5 m/s) — c'est là que vivent les cartes que le code lit, donc
   c'est la seule zone où la vitesse peut apparaître comme axe. C'est un tri mécanique, sans
   hypothèse, et je peux le lancer tout de suite.
2. **Vérifier l'existence d'un sélecteur de rapport** : chercher, dans la chaîne de limitation déjà
   connue (`C3E6`, `C60A` consigne max, `min` des deux pressions), un octet comparé à 1/2/3.
   S'il est absent, la variante n'a pas de limiteur par rapport et la question du rapport engagé
   ne concerne que le calculateur de *couple*, pas celui d'injection.
3. Garder en réserve la voie diagnostic de l'étape 17 (IDs `0x02` et `0x0E`), qui reste la seule
   mesure de terrain capable de trancher sur `D896`/`F91C`.
