# ÉTAPE 59 — ★★★ La bibliothèque d'accès à la calibration, **et les correcteurs : trouvés**

> La question que tu posais — « identifier des correcteurs PI/PID ou des traitements lisant dans la
> flash zone calibration » — a une réponse, et elle est plus intéressante que prévu.

---

## 1. Le mécanisme de lecture, en une ligne

```asm
mov  r4, word_1474      ; r4 <- valeur du pointeur de la table 0xE1400
mov  r5, [r4]           ; lecture dans la structure de calibration
```

Le handle `0x14xx` **est** l'offset de l'entrée de pointeur : `0xE0000 + handle`. La valeur lue est
l'**offset de la structure**, dans la **même page**. Un seul mécanisme, deux additions.

Cela explique la régularité observée depuis des dizaines d'étapes : les pointeurs sont des offsets
14 bits (max `0xBC38`), donc **tout le Datensatz tient dans une page unique**.

---

## 2. ★★★ Le code visible **ne lit jamais** la calibration lui-même

Il appelle une **bibliothèque** — et cette bibliothèque est dans la **couche absente**
(`0x1D36` … `0x1DDA`). On n'en connaît pas le corps, mais **les sites d'appel, les arguments et les
effets sont entièrement lisibles**. Voici l'API reconstituée :

| routine | appels | rôle établi | signature |
|---|---|---|---|
| **`unk_1D36`** | **168** | **interpolation 1-D** | `(r12 = handle, r13 = x)` → **r4 = y** |
| **`unk_1D50`** | **72** | **interpolation 2-D** | `(r12 = handle, r13 = x, r14 = y)` → **r4** |
| **`unk_1D6C`** | **44** | interpolation 1-D, **destination en mémoire** et **mémorisation de l'axe** | `(r12 = dest, r13 = x, r14 = handle)` → écrit `[r12]` |
| **`unk_1D7E`** | **54** | idem **sans nouvelle variable** : réutilise l'axe déjà chargé | `(r12 = dest, r13 = handle)` → **r4** |
| **`word_1D94`** | **64** | interpolation entre **deux bases fournies par pointeurs** (cœur du calcul) | `(r12, r13 = bases, r14 = handle)` |
| `word_1DA8` | 14 | non identifié | — |
| **`word_1DDA`** | **35** | **pas de régulation** | `(r12 = mode, r13 = état, r14 = cible)` → **r4 = nouvel état** + drapeau `USR0` |

**338 sites d'appel, 203 courbes distinctes réellement interpolées.**

---

## 3. ★★ La réponse définitive aux « axes partout, sans carte »

C'est écrit noir sur blanc :

```asm
mov  r12, r0            ; r0 = pointeur de ZONE DE TRAVAIL
mov  r13, word_C91C     ; x = régime
mov  r14, word_1604     ; handle de la 1re courbe
calls 0, unk_1D6C       ; l'axe est chargé et MÉMORISÉ dans [r0]
mov  r12, r0
mov  r13, word_1602     ; handle de la 2e courbe
calls 0, unk_1D7E       ; réutilise l'axe déjà en place
mov  r12, r0
mov  r13, word_1600     ; handle de la 3e courbe
calls 0, unk_1D7E       ; encore le même axe
```

**Une série de courbes partage un axe chargé une seule fois dans une zone de travail.**

Ce n'étaient donc **ni** des axes orphelins, **ni** des cartes sans axes : ce sont des **axes mis en
cache**. Et cela **valide** les 19 grilles nues de l'étape 57 — leurs axes vivent dans la zone de
travail, pas à côté de la grille.

---

## 4. ★★★ Les correcteurs : `word_1DDA` est le primitif de régulation

Les **35 sites** suivent tous le même patron — sans une seule exception dans l'échantillon :

```asm
mov  r12, <mode>          ; #0, #2710h (= 10000), ou un registre
mov  r13, word_X          ; r13 = VALEUR PRÉCÉDENTE — l'état persistant
mov  r14, <cible>         ; la consigne du pas courant
calls 0, word_1DDA
mov  word_X, r4           ; réécriture de l'état
bmov word_FD00.n, USR0    ; USR0 remonte saturation / signe
```

**Un état persistant + une cible + un mode + un indicateur de saturation = un pas d'intégration.**

C'est un **limiteur de pente / filtre du premier ordre**, et **chaque boucle possède son propre mot
d'état** (`CF4A`, `CFE8`, `D75C`, `D836`…). Le drapeau `USR0` remonté par `bmov` est la **détection
de saturation** — indispensable dans un intégrateur, signature classique d'un PI.

---

## 5. ★★★ Une chaîne de régulation complète, décodée (`0xAC65E`)

```asm
mov  r12, word_19D0         ; courbe de calibration
mov  r13, [r0+#4]           ; entrée mesurée
calls 0, unk_1D36           ; r4 = CONSIGNE interpolée
mov  MDL, #2710h            ; /10000  ->  échelle 0…100 %
div  r8
mov  r13, word_D836         ; état précédent
mov  r14, r8                ; consigne du pas
calls 0, word_1DDA          ; PAS DE RÉGULATION
mov  word_D836, r4          ; nouvel état
```

Puis, immédiatement, une **seconde courbe** (`word_19C8`) interpolée **contre la même entrée**, son
résultat publié en `word_D2EE`, l'état en `word_D2F0`.

**C'est un canal de régulation complet : entrée → courbe → mise à l'échelle → pas → sortie.**

**Et le détail qui tue :** l'entrée `[r0+#4]` est choisie, un peu plus haut, entre `word_C616`,
`word_C91C` **et** `word_C93E` **selon `[word_141E + 0x23]`** — un octet de calibration.

**⇒ La source de la boucle est elle-même calibrée.** C'est la version la plus radicale de « aucune
valeur en dur » : même le choix de ce qu'on régule est dans le Datensatz.

---

## 6. ★★ Un filtre à coefficient calibré (`0xACD4A`)

```asm
mov  r12, word_19F6         ; courbe de calibration
mov  r13, word_C91C         ; x = RÉGIME
calls 0, unk_1D36           ; r4 = coefficient K(régime)
mov  r5, word_C940          ; valeur précédente
add  r5, word_D854          ; + entrée
add  r5, r4                 ; + K(régime)
ashr r5, #1                 ; / 2
mov  word_C940, r5          ; stockage
```

**`y[n] = ( y[n−1] + u[n] + K(régime) ) / 2`**

Un **filtre récursif du premier ordre dont le coefficient est une courbe de calibration interpolée
sur le régime**. C'est le « traitement qui lit dans la zone calibration » — et il est **entièrement
décodé**, ligne par ligne.

---

## 7. Bilan de la chasse

| question | réponse |
|---|---|
| le code lit-il la calibration ? | **oui — 338 sites d'appel** vers 4 interpolateurs |
| combien de courbes réellement utilisées ? | **203** |
| y a-t-il des correcteurs ? | **oui — 35 boucles à état persistant** via `word_1DDA` |
| un PID complet est-il visible ? | **non** : le **pas** est dans la couche absente ; **toute la chaîne qui l'entoure est décodée** |
| des valeurs en dur ? | **quasiment aucune** : les gains sont des courbes, l'échelle est `#2710h`, et **jusqu'au choix de l'entrée est un octet de calibration** |

**Ton hypothèse est confirmée — non plus comme intuition de méthode, mais observée sur 338 sites.**

---

## 8. Les grandeurs d'entrée les plus interpolées

| variable | interpolations | lecture |
|---|---|---|
| **`word_C91C`** | **62** | **copie de travail du régime moteur** — variable indépendante dominante |
| `word_C908` | 23 | température LDR (instantané diagnostic) |
| `word_C940` | 13 | copie de `word_C60A` (0…1800) |
| `word_C904` | 12 | air d'admission |
| `word_C5A8` | 4 | masse d'air par tour |
| `word_C68A` | 3 | non identifiée |

**Le régime est l'abscisse de 62 des 203 interpolations** : c'est le squelette du calculateur.

---

## 9. Ce qui change dans le catalogue

| section | ajout |
|---|---|
| **§ 7 bis** | **nouveau et majeur** — la bibliothèque d'accès calibration, l'API de la couche absente, le mécanisme des axes mis en cache, `word_1DDA`, les deux chaînes décodées |

Catalogue : **1 489 → 1 623 lignes**.

**Nouveaux fichiers** : `interpolations.csv` (338 sites, arguments lisibles), `candidats_correcteurs.csv`,
`lectures_calibration.csv` (308 sites de lecture directe, 180 handles, 71 fonctions),
`outils/interpolateurs_et_correcteurs.py`, `outils/lectures_calibration.py`.

---

## 10. Prochaines actions

1. **`unk_20AC` — 250 appels, le plus appelé de tous.** Non identifié. C'est la plus grosse fonction
   inconnue du firmware ; la comprendre éclairerait tout le reste.
2. **Les 35 boucles de `word_1DDA`** : pour chacune, remonter la courbe qui fournit la cible
   (`r14`). On aurait alors **35 boucles nommées, avec leur consigne calibrée et leur état**.
3. **L'octet `[word_141E + 0x23]`** : c'est le sélecteur de source des boucles. Un seul octet de
   calibration commande le choix de l'entrée — à décoder en priorité.
4. **`unk_1D6C` / `unk_1D7E`** : recenser les **groupes de courbes qui partagent un axe**. C'est la
   carte des axes mis en cache, et donc la structure logique du Datensatz.
