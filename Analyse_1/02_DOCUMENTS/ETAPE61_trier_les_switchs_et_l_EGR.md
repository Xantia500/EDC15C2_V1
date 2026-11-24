# ÉTAPE 61 — Trier les switchs, dire ce qu'ils font, et l'état honnête de l'EGR

> Ta mise en garde était nécessaire : **36 % des octets que j'avais comptés comme switchs sont des
> données.** Le tri est fait, et la lecture des blocs shuntés est faite.

---

## 1. Le tri : 122 lectures d'octets → **78 SWITCH / 44 DONNÉE**

Critère **strictement adjacent** : que fait l'instruction qui suit immédiatement la lecture ?

| classe | nombre | critère |
|---|---|---|
| **SWITCH** | **78** | l'octet est testé **immédiatement** par un saut conditionnel |
| **DONNÉE** | **44** | l'octet part dans un calcul (`movbz`, `and`, `add`, `mul`) |

**Exemple net de donnée déguisée en switch :** les octets de `0xE5FE8` (handle `0x1928`, 37 octets)
sont lus puis **combinés arithmétiquement**. Ce sont des **coefficients**, pas des options.

**Et l'erreur de méthode que cela corrige :** mon premier outil acceptait un saut situé jusqu'à
4 lignes après la lecture. Trop large. Avec un test **strictement adjacent**, 122 sites sur 282
survivent — les autres étaient des octets lus puis utilisés plus loin, avec un saut sans rapport.

---

## 2. ★★ Correction de vocabulaire : « actif si NUL » était ambigu

Ma formulation précédente inversait la lecture pour qui ne suit pas le code. La bonne formulation :

> **le saut est pris si l'octet est NUL** → le bloc est **exécuté** quand l'octet est **non nul**.

Une inversion de lecture inverse la conclusion. Le catalogue est corrigé.

---

## 3. ★★ La vraie forme dominante : des **sélecteurs**, pas des interrupteurs

Le patron à deux états existe, mais le plus fréquent est une **cascade de stratégies**. Exemple
intégral, option `[0xE6542 + 0x16]` :

```asm
mov  r5, word_1972
movb rl4, [r5+#16h]        ; octet d'option = 0x01 dans ce firmware
jmpr cc_Z, loc_AA736       ; 0     -> bclr word_FD0E.3        TOUJOURS INACTIF
cmpb rl4, #1
jmpr cc_Z, loc_AA73A       ; 1     -> piloté par le drapeau CAN word_FD7C.8
cmpb rl4, #2
jmpr cc_Z, loc_AA746       ; 2     -> piloté par le SEUIL calibré [0xE6542+0x12]
jmpr cc_UC, loc_AA75C      ; autre -> 4e stratégie
```

**C'est exactement ton « soit ignoré, soit une autre stratégie ».** Les stratégies sont :
**désactivé · par le CAN · par un seuil de calibration · autre**. L'octet ne dit pas oui/non :
**il dit qui décide.**

**Et les options de `0xE6542` vont par paires d'offsets** — (16/17), (22/23), (28/29), (34/35),
(44/45), (50/51) — chacune ne shuntant que **8 lignes** : c'est une **substitution**, pas un bloc.
Un octet « stratégie » + un octet « état » par fonction.

**Le recoupement avec le CAN est direct** : la stratégie `1` dépend de `word_FD7C.8`, c'est-à-dire
des mêmes drapeaux de variante que ceux identifiés à l'étape 44. **La calibration et le CAN se
partagent le choix de stratégie.**

---

## 4. Ce que contiennent les blocs shuntés

| fonction | structure | +off | valeur | bloc | interpolations | axes appelés |
|---|---|---|---|---|---|---|
| *(code non nommé)* | `0xE1148` | +13 | `0x00` | **864** | **5** | `C588` n=8, `C5A4` n=4, carte `D1E6 × D1F6`, `D1FE` n=4, carte `D202 × C590` |
| `sub_A5C92` | `0xE1148` | +12 | `0x00` | **787** | **5** | **régime** n=10 |
| *(code non nommé)* | `0xE232A` | +0 | `0x01` | **578** | **9** | — |
| *(code non nommé)* | `0xE83DA` | +17 | `0x01` | 387 | 0 | — |
| `sub_AF932` | `0xE2332` | +0 | `0x01` | 103 | 0 | — |
| `sub_9BAF0` | `0xE232A` | +0 | `0x01` | 97 | 0 | — |
| *(code non nommé)* | `0xE1148` | +25 | `0x00` | 9 | 1 | carte **`RCO × T LDR`** |

**Le plus gros bloc (864 lignes) contient 5 interpolations, dont deux cartes.** Ce n'est pas un cas
particulier : c'est **un étage de calcul entier** qui s'active ou disparaît selon un octet.

---

## 5. ⚠ Deux réserves de méthode, désormais inscrites au catalogue

**1. L'attribution des fonctions n'est pas fiable partout.** Le désassembleur laisse des zones
**sans étiquette**. J'avais attribué à `sub_AFAA0` des switchs situés 2 000 lignes plus loin — or
**`sub_AFAA0` ne fait que 10 lignes** (elle recopie `word_1AA8` et `word_1AFE` dans `D8F2`/`D8F4` et
met deux octets à `0xFF`).

**Les quatre plus gros switchs sont tous dans du code non nommé.** Le catalogue les marque
`(code non nommé)` : c'est plus utile qu'un nom faux.

**2. Un octet de calibration n'est pas un switch par nature.** Il faut lire la suite immédiate.

---

## 6. ★ L'EGR : la région est identifiée, le switch ne l'est pas encore

### Ce qui est établi

La zone de calibration `0xE83C8 … 0xE88F6` (handles `0x1B36` à `0x1B50`) est la **zone air** :

| handle | EA | contenu |
|---|---|---|
| `0x1B3C` | `0xE83DA` | bloc de paramètres (ses octets sont lus **9 fois** dans un même calcul) |
| `0x1B3E` | `0xE83F4` | courbe sur le **régime**, 19 points, 0…5200 → 0…7430 |
| **`0x1B40`** | **`0xE8444`** | **CARTE 16 × 16 — régime 0…5200 × air mesuré 300…1150 mg → 0…7600** |
| `0x1B44` | `0xE86F4` | carte préchauffage (régime × T LDR) |
| `0x1B4C` | `0xE8872` | seconde carte régime × air, **grille nulle** (emplacement vacant) |

**Ces handles sont interpolés à quelques lignes d'une lecture de la masse d'air mesurée**
(`word_C5A8` / `word_C3E6`). C'est le schéma d'une **limitation par la masse d'air**, dont la carte
`0xE8444` est l'élément central. Une vanne EGR se commande précisément pour **atteindre une masse
d'air cible** : la région est donc la bonne.

### Candidats, et ce que j'écarte

| site | structure + off | valeur | effet |
|---|---|---|---|
| `l.181491` | `0xE83DA + 17` | `0x01` | saute 387 lignes **si NUL** → bloc **exécuté** ici |
| `l.178313` | `0xE7FF8 + 0` | `0x01` | bloc de 6 lignes |
| `l.167740` & suivants | `0xE6542` paires | 0/1/2 | **sélecteurs de stratégie** (§ 3) |

**Ce que j'écarte, et pourquoi.** Le bloc gaté par `[0xE83DA+17]` (387 lignes) contient une
**division avec reste** :

```asm
mov  r4, word_D920
add  r4, #1
mov  r5, word_D91C
mov  MDL, r4
divu r5
mov  r4, MDH            ; le RESTE de la division
cmp  r4, word_D91E
```

C'est un **compteur modulo comparé à une valeur** = un **processus périodique / une base de temps**,
pas une fonction EGR. **Je ne le retiens pas comme switch EGR** — et je préfère l'écrire que de le
laisser croire.

### Conclusion honnête

**La région EGR est identifiée ; le switch EGR ne l'est pas encore.** Il manque un **lien
fonctionnel** : savoir **quel mot RAM porte la consigne de l'électrovanne EGR**. Tant que ce mot
n'est pas nommé, un octet de cette zone peut aussi bien commander la suralimentation, la vanne EGR
ou le volet d'admission.

**Le prochain pas est donc d'identifier la SORTIE, pas l'entrée.** Trois pistes concrètes :

1. **Chercher quel mot est écrit puis consommé par une sortie PWM/RCO.** Une électrovanne EGR est
   pilotée en rapport cyclique ; les mots écrits par la zone air et jamais relus par un calcul sont
   des sorties.
2. **`word_FD0E`** : le sélecteur de `0xE6542+0x16` agit sur le **bit 3** de ce mot. Suivre les
   autres bits de `word_FD0E` dirait à quoi correspondent ces options.
3. **Les 40 comparaisons `cc_ULE`** (`mode ≤ N`) : ce sont des choix dans une gamme de stratégies.
   Les trier par structure donnerait la carte des fonctions à plusieurs modes.

---

## 7. Consignation

| section | ajout |
|---|---|
| **§ 13 B.3** | le tri switch / donnée, et pourquoi 36 % sont des données |
| **§ 13 B.4** | le patron sélecteur à N stratégies, avec l'exemple intégral |
| **§ 13 B.5** | le contenu des blocs shuntés (interpolations et axes) |
| **§ 13 B.6** | les deux réserves de méthode (attribution, polarité) |
| **§ 13 B.7** | l'EGR : ce qui est établi, les candidats, ce qui est écarté, ce qui manque |

**Catalogue : 1 795 → 1 900 lignes.**

**Fichiers** : `switchs_contenu.csv` (122 sites classés, avec taille de bloc, nombre
d'interpolations, axes appelés, mots écrits), `switchs_classes.csv`, `outils/analyse_switchs.py`.
