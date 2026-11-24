# ÉTAPE 43 — Le bit de power latch, la grandeur surveillée, et une boucle à 5 entrées

---

## 1. ★ `word_FD0C.15` : **premier usage sémantique** du power latch

l. 153175 :

```asm
                jb      word_FD0C.15, loc_A1FD2
                mov     r4, word_142A
                ...
```

Depuis l'étape 28, `word_FD0C` était **lu 160 fois, jamais écrit** — un constat négatif qui bloquait
toute interprétation. Nous tenons enfin un **usage daté** :

- **bit 15 = 1 ⟹ on saute** l'initialisation du moniteur (`loc_A1FD2` = sortie) ;
- **bit 15 = 0 ⟹ on configure** le moniteur et ses bornes.

⇒ **`word_FD0C.15` est bien l'indicateur « alimentation maintenue / après-arrêt »**, et il **gèle
l'évaluation des moniteurs**. Le power latch n'est plus une hypothèse : il **agit** sur le
diagnostic. Que son écrivain soit absent du dump reste vrai, mais son rôle ne l'est plus.

*Second bit du même genre* : `word_FD5A.15`, testé l. 153236 dans la même chaîne.

---

## 2. ★ Le descripteur de calibration d'un moniteur, entièrement cartographié **par usage**

`word_142A` est un handle. Ses quatre premiers mots sont maintenant tous identifiés :

| offset | usage observé | ligne |
|---|---|---|
| **+0** | **seuil n°1** → `word_CFB2` | 153179 |
| **+2** | **incrément**, ajouté au précédent → `word_CFB4` = **borne haute de validité** | 153180-153182 |
| **+4** | **autorisation** : `0xFFFF` ⟹ `byte_CFDC = 1` (**inhibition permanente**) ; sinon ⟹ `word_C0BC = word_F91C` | 153183-153192 |
| **+6** | **seuil n°2** (critère de durée) | 153314 |

```asm
                mov     word_CFB2, [r4]        ; +0
                mov     r5, [r4+#2]            ; +2
                add     r5, word_CFB2
                mov     word_CFB4, r5          ; borne = seuil + incrément
                mov     r2, [r4+#4]            ; +4
                cmp     r2, #0FFFFh
                jmpr    cc_Z, loc_A1F7E        ; 0xFFFF -> inhibition permanente
                mov     r2, word_F91C
                mov     word_C0BC, r2          ; sinon -> inhibition par horloge
```

**C'est la démonstration la plus complète du modèle `handle + offset`** de toute la session : quatre
champs, quatre rôles distincts, tous prouvés par le code.

---

## 3. ★ La grandeur surveillée est `word_C3D2` — une **variable d'axe de 42 cartes**

l. 153231-153234 :

```asm
                mov     r4, word_C3D2
                mov     word_C908, r4          ; ← instantané de la mesure
```

Or `word_C3D2` est, d'après l'inventaire de l'étape 27, **le deuxième tag le plus utilisé : 42
cartes s'en servent comme axe**. Et `word_C908` est la variable que les moniteurs comparent aux
seuils (étapes 41-42).

⇒ **Le calculateur surveille précisément les grandeurs sur lesquelles il interpole.** Le diagnostic
et la gestion moteur regardent **la même variable**, l'une via un instantané (`word_C908`), l'autre
via l'axe de carte. C'est cohérent et cela **ferme** la question du « à quoi sert un tag ».

---

## 4. ★ Une boucle à **exactement 5 entrées** qui construit deux cartes de bits

l. 153197-153228 :

```asm
                mov     r12, word_1818         ; ← handle (numéros de bits, en calibration)
                mov     r15, #0C9F3h           ; ← tableau de drapeaux en RAM
                mov     r13, #0
                mov     r14, #0
                movb    rl6, #0
loc_A1F92:
                movb    rl4, [r15]
                cmpb    rl4, #0
                jmpr    cc_ULE, loc_A1FB4      ; drapeau nul -> rien
                movb    rl4, [r12]
                cmpb    rl4, #7
                jmpr    cc_ULE, loc_A1FAA
                movb    rl4, [r12]
                movbz   r4, rl4
                mov     r5, #1
                shl     r5, r4
                or      r14, r5                ; bit dans le mot HAUT
                jmpr    cc_UC, loc_A1FB4
loc_A1FAA:
                movb    rl4, [r12]
                movbz   r4, rl4
                mov     r5, #1
                shl     r5, r4
                or      r13, r5                ; bit dans le mot BAS
loc_A1FB4:
                addb    rl6, #1
                add     r12, #1
                add     r15, #1
                cmpb    rl6, #5
                jmpr    cc_C, loc_A1F92
                mov     r4, r13
                shl     r4, #4
                or      r13, r4                ; duplication du quartet
                mov     r4, r14
                shr     r4, #8
                or      r14, r4                ; duplication de l'octet
                mov     word_C548, r13
                mov     word_C54A, r14
```

**Décodage :**

- **5 entrées** exactement (`cmpb rl6, #5`), indices 0…4 ;
- pour chacune : un **drapeau** en RAM (`0xC9F3 + n`) et un **numéro de bit** lu dans la
  **calibration** via le handle `word_1818` ;
- si le drapeau est non nul, on pose `1 << numéro` dans le **mot bas** (numéro ≤ 7) ou le **mot
  haut** (numéro > 7) ;
- puis **duplication** : le quartet bas est recopié en haut (`r13 | r13<<4`), et l'octet bas
  recopié en haut (`r14 | r14>>8`) ;
- résultat publié dans **`word_C548`** et **`word_C54A`**.

**Ce que je ne conclus pas** : la nature des 5 entrées. Je note seulement deux coïncidences, sans les
transformer en preuve :
- **5** est aussi le nombre d'**identifiants EEPROM** mémorisés par des commandes dédiées
  (0x1E / 0x21 / 0x22 / 0x24 / 0x25, étape 33 §4) ;
- la **duplication** quartet→quartet / octet→octet est le style de redondance déjà rencontré deux fois
  (triple copie masquée, étape 36).

Les numéros de bits venant de la **calibration**, c'est le contenu du Datensatz qui décide de la
correspondance — donc **hors de notre portée**, comme les masques de `word_B8E/B90/B92`.

---

## 5. Le bloc `0xFD2x` de l'étape 39 trouve son rôle

l. 153234-153240 :

```asm
loc_A200A:
                movb    rl4, word_FD2E
                jmpr    cc_Z, loc_A201A
                movb    rl5, #1
                movb    byte_CFDC, rl5         ; ← INHIBITION PERMANENTE
                mov     word_C0BC, ZEROS
```

⇒ **`word_FD2E` force l'inhibition de tous les moniteurs.** C'est le drapeau « ne pas diagnostiquer »
(typiquement : calculateur en mode particulier, ou télécodage en cours). Cela **explique enfin** une
variable du bloc de 96 octets que je n'avais pas su interpréter.

---

## 6. Un compteur jamais chargé

`byte_CFC4` (le compteur de confirmation, étape 42 §3.2) n'est **que décrémenté** (l. 153153) et
**testé** (l. 153147). **Aucune écriture de valeur initiale dans la couche visible.**

⇒ Sa valeur de départ est posée par la couche absente — ou reste celle laissée par l'initialisation
RAM. **Conséquence importante** : si elle vaut 0, `sub_A1E9E` sort immédiatement (`jmpr cc_Z`) et
**aucun défaut ne peut être confirmé**. C'est donc un point de contrôle à connaître, pas un détail.

---

## 7. Tableau de bord

| question | état |
|---|---|
| power latch | **`word_FD0C.15` gèle les moniteurs** ✔ |
| descripteur de moniteur | `+0` seuil, `+2` incrément, `+4` autorisation, `+6` seuil 2 ✔ |
| grandeur surveillée | **`word_C3D2`** (axe de 42 cartes), instantané dans `word_C908` ✔ |
| inhibition globale | `word_FD2E` ✔ |
| boucle à 5 entrées | → `word_C548` / `word_C54A`, **numéros de bits en calibration** ✔ |
| compteur de confirmation | `byte_CFC4`, **jamais chargé** |
| antidémarrage | non localisé |

---

## 8. Prochaines actions

1. **`word_C548` / `word_C54A`** : qui les lit ? Si personne dans la couche visible, ce sont des
   **valeurs persistées** (candidat EEPROM sérieux).
2. **`0xC9F3` + 5 octets** : qui pose ces drapeaux ? Réponse = la nature des 5 entrées.
3. **`word_1818`** : le handle des numéros de bits — sa valeur dans le Datensatz est lisible !
   `python3 outils/ea2handle.py` permet de la retrouver.
4. **Antidémarrage** : angle « inhibition » — chercher une mise à **zéro de la quantité injectée**
   conditionnée par un drapeau, et non un échange d'authentification.
