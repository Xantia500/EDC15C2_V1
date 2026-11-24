# ÉTAPE 48 — Les quatre actions : deux résultats fermes, deux hypothèses réfutées

---

## 1. ★★ Outil général nouveau : **les blocs du Datensatz sont délimités par la table des pointeurs**

Les valeurs de la table `0xE1400` sont des débuts de bloc. Le bloc d'un handle s'étend donc de sa
valeur à **la valeur suivante dans l'ordre croissant**. Résultat immédiat :

| handle | bloc | **taille** | ce que le code lit | cohérence |
|---|---|---|---|---|
| `word_142A` | `0xE122C..0xE1236` | **10 o** = 5 mots | `+0,+2,+4,+6` = mots 1…4 | ✔ |
| `word_1474` | `0xE226E..0xE2290` | **34 o** = 17 mots | `+0x1A` = mot 13 | ✔ |
| `word_1818` | `0xE4962..0xE4968` | **6 o** | **5 octets lus** | ✔ (1 o de marge) |
| `word_18F2` | `0xE5316..0xE5350` | **58 o** = 29 mots | `+0x38` = mot **28** = **le dernier** | ✔✔ |
| `word_18F6` | `0xE5368..0xE5388` | 32 o = 16 mots | — | |
| `word_1952` | `0xE63BE..0xE63FC` | 62 o = 31 mots | — | |

**Trois vérifications indépendantes passent** : `word_18F2` lit `+0x38` = l'**ultime mot** de son bloc
(exactement 56 < 58) ; `word_1818` n'utilise que 5 des 6 octets ; `word_142A` tient en 5 mots et le
code en lit 4.

⇒ **Le découpage du Datensatz est désormais calculable**, plus seulement supposé. Et
**`word_1818` = 6 octets pour 5 entrées** confirme définitivement l'étape 47 §2.

---

## 2. ★★★ Action 1 — `0xC9F3` décodé : ce sont **5 compteurs de défauts par niveau**

### Le code (l. 231387-231410)

```asm
                mov     r3, #0
loc_CF216:
                cmp     r3, #60h ; '`'        ; ← 96 ENTREES ( = 0xCAD0 : 96 × 4 o )
                jmpr    cc_NC, loc_CF242
                mov     r0, [r4+]              ; ← parcours de la table
                jb      r0.0, loc_CF23E        ; ← bit 0 = defaut PRESENT, sinon on saute
                movb    rh2, [r0+#1Ch]         ; ← octet de classe du descripteur (ETAPE 42)
                movb    rl2, #0
                mov     r6, #0C9F3h            ; ← les 5 compteurs
loc_CF22C:
                shl     r2, #1                 ; ← decalage : le bit sort dans le CARRY
                jmpr    cc_NC, loc_CF236       ; ← premier bit NUL : on ARRETE
                movb    rl0, [r6]
                addb    rl0, #1                ; ← INCREMENTE
                movb    [r6], rl0
loc_CF236:
                add     r6, #1
                cmp     r6, #0C9F8h            ; ← 5 octets : 0xC9F3..0xC9F7
                jmpr    cc_C, loc_CF22C
loc_CF23E:
                add     r3, #1
                jmpr    cc_UC, loc_CF216
```

**Décodage :**

1. **boucle sur 96 entrées** — exactement la taille de la mémoire de défauts (`0xCAD0` = 96 × 4 o) ;
2. on ne traite que les entrées dont le **bit 0 est posé** — c'est-à-dire les défauts **présents** ;
3. on lit **`[entrée + 0x1C]`** — **le même octet de classe que l'étape 42**, troisième site indépendant ;
4. l'octet est placé dans `r2` **partie haute**, puis décalé à gauche : **chaque `1` rencontré
   incrémente `0xC9F3 + n`**, et **le premier `0` arrête** ;
5. `n` va de 0 à 4 (borne `0xC9F8`).

**⇒ `0xC9F3…0xC9F7` = le nombre de défauts présents à chacun des 5 niveaux**, le niveau étant lu dans
les bits hauts de l'octet `+0x1C` du descripteur.

### ★★ La boucle est bouclée : c'est exactement l'entrée de l'étape 43 §4

| étape | maillon |
|---|---|
| l. 231394 | `0xC9F3 + n` incrémenté pour chaque défaut présent de niveau n |
| l. 153197 | `if ([0xC9F3 + n] > 0)` → poser le bit `[word_1818 + n]` |
| `word_1818` | contient **02 01 00 08 0F** (étape 47 §2) |
| résultat | **`word_C548` bits 0,1,2 · `word_C54A` bits 8,15** |

**⇒ `word_C548` / `word_C54A` = « au moins un défaut actif au niveau n », pour les 5 niveaux.**
C'est un **résumé d'état de diagnostic**, pas une donnée aléatoire. La chaîne
`descripteur → compteur → bit → mot` est complète et vérifiée de bout en bout.

### ★ Une **seconde** copie des 5 compteurs (l. 231755-231768)

```asm
                mov     r0, #0
                mov     word_CCB0, r0
                movb    byte_CCAF, rl0
                mov     r1, #0CCAAh            ; ← source : 5 octets 0xCCAA..0xCCAE
                mov     r2, #0C9F8h            ; ← destination : 0xC9F8..0xC9FC
loc_CF57E:
                movb    rl3, [r1]
                movb    [r2], rl3              ; copie
                add     r2, #1
                movb    [r1], rl0              ; ET EFFACEMENT de la source
                add     r1, #1
                cmp     r1, #0CCAFh            ; 5 octets
                jmpr    cc_C, loc_CF57E
```

**⇒ `0xC9F8..0xC9FC` = un second tableau de 5 octets**, alimenté par recopie depuis
**`0xCCAA..0xCCAE`** (source effacée au passage), avec **`byte_CCAF` et `word_CCB0` remis à zéro**.

À noter : **`0xCCAA..0xCCB1` précède immédiatement `0xCCB2`**, la table des 96 mots de codes de défaut.
C'est donc un **bloc de travail accolé à la table des défauts** : vraisemblablement un **instantané**
des 5 compteurs au moment d'une requête de diagnostic (puis remis à zéro).

*Cohérence de forme* : `word_C548`/`word_C54A` d'un côté (résumé par bits), `0xC9F8` de l'autre
(copie brute par octets) — **deux représentations du même état**, l'une pour un service interne,
l'autre pour une transmission.

---

## 3. ✘ Action 2 — `word_18F6` : l'hypothèse « triple copie » est **RÉFUTÉE**

Contenu à `0xE5368` (32 octets = 16 mots) :

```
77, 1200, 2400, 300, 600, 3000, 4, 3990,
3000, 2000, 50, 850, 5000, 5000, 30, 150,
−427, −427, −427, −301, 0, −427, −512, −555
```

J'avais annoncé une valeur « −427 répétée trois fois » comme signature d'un enregistrement triple.
**La lecture complète réfute cette lecture :**

- **−427 apparaît quatre fois**, pas trois (mots 16, 17, 18 **et 21**) ;
- la suite **−427, −427, −427, −301, 0, −427, −512, −555** n'est **pas monotone** ⇒ ce n'est pas un
  axe ;
- et surtout, **ce n'est pas la forme d'un enregistrement triple** : un enregistrement triple de
  l'étape 45 est **un mot suivi de deux copies contiguës** (`value, value, value`) sur 6 octets. Ici
  la répétition est **interrompue**.

⇒ **Hypothèse retirée.** Le bloc `word_18F6` mêle une première moitié de valeurs **toutes positives et
croissantes** (77, 1200, 2400, 300, 600, 3000, 4, 3990, 3000, 2000, 50, 850, 5000, 5000, 30, 150) à
une seconde moitié **négative**. C'est la signature d'un **bloc composite**, pas d'un enregistrement.

**Observation** (non retenue comme preuve) : **5000, 5000** aux mots 12-13 et **1200** au mot 1
rappellent les ordres de grandeur de `word_1474` (régimes, et le ±1200 de `word_142A`).

---

## 4. Action 3 — `word_1952` : bloc **hétérogène**, avec de la virgule fixe

Contenu à `0xE63BE` (62 octets = 31 mots) :

```
6000, 3000, 4031, 13107, 10000, 7000, 2185, 0,
10000, 10000, 7000, 9000, 2931, 2881, 3731, 3831,
−9, 1000, −3000, 9331, 10, 5731, 9231, 0, ...
```

**Trois familles de valeurs cohabitent :**

1. **des multiples de 1000 jusqu'à 10000** — `6000, 3000, 7000, 9000, 10000, 10000, 10000`. Or
   **10000 = 0x2710 = « 100 % »** est la convention de codage que tu as fixée pour les grandeurs
   internes. ⇒ **ces valeurs sont des pourcentages ×100** ;
2. **`13107 = 0x3333`** — une constante de **virgule fixe** (0x3333 / 65536 = **0,2000**). Ce n'est ni
   un pourcentage ni une mesure : c'est un **coefficient de calcul** ;
3. **des valeurs signées** `−9`, `−3000`, et des valeurs « à queue » `2931, 2881, 3731, 3831, 9331,
   5731, 9231`.

⇒ **Le bloc est délibérément composite** : l'idée d'une « frontière de blocs » que j'évoquais est
**inutile** — c'est bien **un seul bloc** (la table des pointeurs ne place aucune frontière dedans),
mais il regroupe **paramètres de pourcentage, coefficients et décalages**.

**Conséquence méthodologique** : un « handle » ne désigne **pas** une grandeur unique. Il désigne **un
bloc de paramètres** consommé par un sous-programme. C'est cohérent avec l'erratum de l'étape 47 §1, et
cela **ferme** la question « un tag = une valeur ».

---

## 5. ✘ Action 4 — `word_1474` : **pas** une paire « valeur + borne »

J'ai relevé **tous** les accès à `word_1474` (25 sites, lignes 155409-156126). Le motif est
**systématiquement le même** : lire **un** offset, comparer à **une** variable dédiée.

| offset | valeur | variable comparée | lignes |
|---|---|---|---|
| **+0x00** | 360 | `word_D6EE` | 155410-155411 |
| **+0x02** | 60 | `word_D6F6` | 155760 |
| **+0x04** | **60** | `word_D6F0`, `word_D6F2`, `word_D6F4`, `word_D6F8` (**4 variables**) | 155516-155835 |
| **+0x06** | 325 | `word_C5B8` | 156049 |
| **+0x1A** | **250** | `word_D6FA` | 156042 |

**⇒ `word_1474` est un bloc de seuils indépendants**, un par compteur. L'hypothèse « `+0x18` et
`+0x1A` = valeur + borne » est **réfutée** : **chaque offset est une limite autonome**, et les deux 250
voisins sont simplement **deux limites égales**.

**Et `+0x18` n'est lu nulle part** dans la couche visible — sur les 25 sites, aucun ne touche cet
offset ; sa valeur `250` est donc **inutilisée ici**, ou consommée par la couche absente.

### ★ Le vrai résultat de cette action : une **famille de 7 compteurs**

`word_D6EE, D6F0, D6F2, D6F4, D6F6, D6F8, D6FA` — **sept compteurs**, chacun avec **sa propre
limite** tirée de `word_1474`, plus :

- **`byte_D6FC`** = octet de drapeaux (bit 0 remis à zéro juste après le chargement de `word_D6FA`,
  étape 46 §3) ;
- **`word_D6FE`** = **décompte** (étape 46 §3).

**⇒ Sept quantités, sept filtres à seuil indépendant, un octet de drapeaux, un décompte** : c'est un
**banc de temporisation / d'apprentissage**, pas un mécanisme de sécurité unique.

*Coïncidence à signaler sans la transformer en preuve* : **7** est aussi le nombre de défauts que la
mémoire peut retenir (`byte_E466` = 0…7, `0xE467` + 7 × 22 o).

---

## 6. Bilan des quatre actions

| action | verdict |
|---|---|
| 1. `0xC9F3` | **★ Fermé** : 5 compteurs de défauts par niveau ; chaîne complète jusqu'à `word_C548`/`C54A` ; 2ᵉ copie à `0xC9F8` |
| 2. `word_18F6` | **✘ Réfuté** : pas de triple copie, répétition interrompue et non monotone |
| 3. `word_1952` | **Bloc composite** : pourcentages ×100, coefficient Q16 `0x3333`, valeurs signées ⇒ **un handle = un bloc, pas une grandeur** |
| 4. `word_1474` | **✘ Réfuté** : seuils indépendants ; découverte d'une **famille de 7 compteurs `word_D6xx`** |

**Deux hypothèses de ma part tombent** (triple copie de `word_18F6` ; paire valeur+borne de
`word_1474`). **Un mécanisme entier se ferme** (`0xC9F3` → `word_C548`). **Un outil nouveau** apparaît
(les bornes de blocs calculables).

---

## 7. Prochaines actions

1. **`word_D6EE…word_D6FA`** : qui les incrémente ? Si ce sont 7 compteurs d'événements, leur
   déclencheur révèle la grandeur de `word_C5B8`.
2. **`byte_D6FC`** : les 8 bits, qui les pose ?
3. **`word_1818` n'a que 6 octets pour 5 entrées** : vérifier s'il existe un **second handle** voisin
   portant 6 entrées ou plus — le mécanisme de la boucle est **paramétré par la calibration**, donc
   **le nombre de niveaux pourrait varier selon le Datensatz**.
4. **`word_1998`/`word_19xx`** : appliquer l'outil de bornes de blocs aux blocs voisins de `word_1952`
   pour cartographier d'un coup toute la zone `0xE63xx`.
