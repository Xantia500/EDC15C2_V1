# ÉTAPE 22 — La table des handles, expliquée. Et ce que l'audit a déterré

## PARTIE 1 — La table des handles : rôle et fonctionnement

### 1.1 L'idée en une phrase

**C'est un annuaire.** Le programme ne connaît aucune adresse de calibration ; il ne connaît que des
**noms** (`word_1B54`, `word_1B3E`…). L'annuaire traduit ces noms en adresses. Autrement dit : les
cartes sont désignées **par un numéro de ligne dans un tableau**, pas par leur position en mémoire.

### 1.2 Ce qu'elle est physiquement (mesuré)

| | valeur |
|---|---|
| emplacement | flash, **linéaire `0xE1400`** (offset fichier `0x61400`) |
| taille | **1304 mots de 16 bits** = 2608 octets (`word_1400 … word_1E2E`) |
| contenu | des **offsets 16 bits** dans la page de calibration, de `0x100A` à `0xBC38` |
| conversion | **adresse linéaire de la carte = `0xE0000 + valeur`** |
| unicité | les 1304 valeurs sont **toutes distinctes** (vérifié) |
| écriture par le code | **aucune** — `word_1400`/`word_1402` ne sont jamais écrits (0 occurrence) |

Deux conséquences immédiates, et une précision qui corrige une idée fausse répandue dans nos notes :

- ce n'est **pas** une table recopiée en RAM : rien ne l'écrit, donc on lit directement la flash ;
- les symboles `word_14xx` / `word_1Bxx` ne sont donc **pas des variables RAM** : ce sont des
  **offsets dans la page de calibration**. Pour qu'ils désignent la flash, il faut que le
  `DPP0` (pointeur de page) vaille `0x0E` à ce moment-là. Vérifié : `DPP0` est réaffecté en cours de
  route (`mov DPP0, #0Ah` l. 96631, `#9` l. 96634, `#4` l. 96644, et surtout **dynamiquement** :
  `mov DPP0, r12` l. 97327, 97409, 97863, 97870). Le boot ne fixe `0/0/2/3` qu'au démarrage
  (l. 96439-96443) — c'est un état initial, pas une constante.

**La preuve la plus nette que la page vaut bien `0x0E`** : l'instruction `add r4, #0A62h`
(l. 183031) lit un mot à l'adresse d'offset `0x0A62` ; or c'est à **`0xE0A62`** que se trouve, en
flash, la table de sauts dont les 12 entrées sont *exactement* les adresses des 12 blocs du
sélecteur de rapport. Une coïncidence de 12 mots est exclue : `0x0A62` + page `0x0E` = `0xE0A62`. ✓

### 1.3 Comment le code s'en sert — un exemple complet

Voici le chemin entier pour la courbe de 1ʳᵉ, tel qu'il est écrit dans le programme :

```
mov   r12, word_1B54        ; 1. je nomme la carte  -> r12 = 0x1B54
mov   r13, word_C91C        ; 2. j'abscisse        -> r13 = régime
calls 0, unk_1D36           ; 3. "interpole-moi cette carte en ce point"
mov   word_D9A2, r4         ; 4. résultat          -> 64,0 mm³ par exemple
```

Ce que fait l'étape 3 (par contrat, car son corps n'est pas dans notre dump — voir partie 2) :
`r12` → lire le mot à l'offset `0x1B54` dans la page → `0x8906` → adresse `0xE8906` → là, lire
`[tag = 0xC42E][n = 15][axe 15 mots][valeurs 15 mots]` → interpoler en `r13` → rendre dans `r4`.

Donc la chaîne est : **nom → pointeur → enregistrement → valeur**. La table ne contient *que* des
pointeurs : ni données, ni code, ni cache.

### 1.4 À quoi ça sert — les quatre raisons, dans l'ordre d'importance

1. **Indépendance code / calibration.** Le même programme tourne avec n'importe quelle calibration :
   changer une carte ne demande aucune modification du code, il suffit que le pointeur de la ligne
   correspondante la désigne. C'est ce qui permet à Bosch/PSA de livrer des dizaines de variantes
   avec un seul logiciel.
2. **Deux banques de calibration (E et F).** La table existe en deux exemplaires — vérifié :
   les 2608 octets à `0x61400` et à `0x71400` sont **identiques au bit près (0 différence)**.
   Basculer de banque = changer la page de base ; toutes les cartes suivent, sans toucher au code.
3. **Renumérotation / déplacement par l'outil.** Un outil de calibration peut déplacer une carte,
   la redimensionner, en ajouter une : il réécrit le pointeur, et le code la trouve.
4. **Copies de travail.** C'est le même principe qui alimente les variables de travail
   (`word_C3BA → word_C904`, etc.) : l'interface et la stratégie n'échangent pas des adresses mais
   des symboles.

### 1.5 Comment *nous* devons l'utiliser (la leçon de l'étape 20)

- **Pour trouver qui utilise une carte** : chercher le **nom du handle**, jamais l'adresse.
  `grep word_1B54` → `seg015:3132` → le bloc de sélection. C'est comme ça que la chaîne du limiteur
  par rapport a été trouvée, après deux étapes d'échec par recherche d'adresse.
- **Pour lire une carte** : handle → `valeur` → `0xE0000 + valeur` → décoder
  `[tag][n][axe][valeurs]`.

### 1.6 Table de correspondance des cartes qui nous concernent (vérifiée)

| handle | pointeur | adresse linéaire | carte |
|---|---|---|---|
| `word_1B3E` | `0x83F4` | `0xE83F4` | main torque limiter (19 pts) |
| `word_1B40` | `0x8444` | `0xE8444` | smoke map 16×16 (régime × air) |
| `word_1B54` | `0x8906` | `0xE8906` | courbe **1ʳᵉ** |
| `word_1B56` | `0x8946` | `0xE8946` | courbe **2ᵉ** |
| `word_1B58` | `0x8986` | `0xE8986` | courbe **3ᵉ** (100 mm³) |
| `word_1B5C` | `0x89FA` | `0xE89FA` | courbe 2 pts (100 mm³) |
| `word_1B5E` | `0x8A06` | `0xE8A06` | carte (régime × `D3D4`) |
| `word_1B64` | `0x8B10` | `0xE8B10` | copie de la 1ʳᵉ = **marche arrière** |

---

## PARTIE 2 — Ce que l'audit a déterré : **1288 appels vers une zone absente du dump**

C'est le résultat le plus important de cette vérification, et il change la façon dont nous devons
parler de tout ce qui suit.

### 2.1 Le fait

L'instruction d'appel a été décodée sur les octets réels. Exemple, l'appel à l'interpolateur 1-D :

```
F2 FC E6 15   mov   r12, word_15E6
F2 FD 1C C9   mov   r13, word_C91C
DA 00 36 1D   calls 0, 0x1D36        ← segment 0, offset 0x1D36
```

`DA 00 36 1D` = `CALLS seg=0x00, caddr=0x1D36`. Sur le C166, le segment d'appel est chargé dans le
`CSP`, donc l'adresse visée est **linéaire `0x1D36`** — c'est-à-dire, dans notre fichier,
**l'offset `0x01D36`**.

Or : **la zone fichier `0x00000–0x07FFF` (32 Ko) est à 100 % du remplissage `0xC3`** — vérifié
octet par octet : **0 octet non-`0xC3` sur 32 768**. Et `0xC3` est un opcode illégal.

### 2.2 L'ampleur

Sur l'ensemble du programme, il y a **1288 appels `calls 0, …`**, c'est-à-dire des appels dans cette
zone. Les cibles principales :

| cible | appels | rôle identifié par les sites d'appel |
|---|---|---|
| `unk_20AC` | **250** | mise à l'échelle / division (r12=valeur, r13, r14=échelle `0x2710`) |
| `unk_1D36` | **168** | **interpolation 1-D** (r12=handle, r13=X) |
| `unk_7C2` | 110 | non identifié |
| `unk_7B4` | 110 | non identifié |
| `unk_1D50` | **72** | **interpolation 2-D** (r12=handle, r13=X, r14=Y) |
| `word_1D94` | 64 | non identifié |
| `unk_1D7E` | 54 | non identifié |
| `unk_1D6C` | **44** | interpolation 1-D avec destination (r12=dest, r13=X, r14=handle) |
| `word_1DDA` | 35 | non identifié |
| `unk_2160`, `unk_2128`, `unk_2A9A`… | 27, 24, 20… | non identifiés |

### 2.3 Les deux explications possibles — et pourquoi ça ne change pas nos conclusions

1. **La zone `0x0000–0x7FFF` n'est pas dans le dump.** Le fichier fait 512 Ko et couvre
   `0x80000–0xFFFFF` ; la bibliothèque bas niveau résiderait en dessous, dans un autre composant
   (ROM masquée, secteur non lisible par l'outil de lecture). C'est le plus probable : 32 Ko
   d'effacement **pile** là où tombent 1288 appels ne peut pas être un hasard.
2. **Elle est chargée à l'exécution** (recopie en RAM avant usage). Possible aussi, mais alors la
   source de la recopie devrait être quelque part dans la flash — or on ne trouve aucun bloc
   ressemblant à ces routines.

**Conséquences, à assumer franchement :**

- nous n'avons **jamais lu le corps** des interpolateurs, du routine de mise à l'échelle, ni de
  `unk_7B4`/`unk_7C2`. Tout ce que nous en disons (`r12` = handle, `r13` = X, résultat dans `r4`,
  `0x2710` = 100 %) vient de l'**observation des sites d'appel** — cohérente sur des centaines
  d'occurrences, mais ce n'est pas une lecture du code ;
- en particulier, **le détail de l'interpolation** (linéaire ? lissage ? gestion des bornes ?) et
  **l'unité exacte de sortie** reposent sur cette convention. C'est solide statistiquement, mais ce
  n'est pas prouvé ;
- si tu peux obtenir un dump complet (par exemple en lecture directe de la flash sur banc, ou un
  fichier couvrant `0x00000–0x7FFFF`), **c'est la pièce qui manque** et elle vaudrait plus que
  toutes les analyses restantes.

### 2.4 Ce que ça ne remet pas en cause

Les faits établis sur la **donnée** et sur les **enchaînements** restent valables, car ils ne
dépendent pas des corps de routines :

- contenu et structure des cartes (vérifiés par les tailles : `0xE8444 + 0x248 = 0xE868C`) ;
- table des handles (1304 entrées, pointeurs distincts, banc F identique) ;
- sélecteur de rapport et sa table de sauts (`0xE0A62`, 12 entrées lues) ;
- enchaînement `byte_C240 → byte_C330 → handle → word_D9A2 → word_D3EC`.

## PARTIE 3 — Suite immédiate

1. `sub_9B796` : le calcul de `byte_C240` (le rapport 0…14). **Toujours la cible n° 1.**
2. Table de sauts `#0A2Ch` → à lire en **`0xE0A2C`** (même mécanisme que `0xE0A62`, maintenant qu'il
   est compris).
3. Inventaire complet des 1304 handles, par descripteurs.
