# ÉTAPE 40 — Table des sélecteurs de la mémoire des défauts, et un verrou « à gâchette »

---

## 1. ★ Le codage des sélecteurs est décodé : `octet haut = opération`, `octet bas = numéro de défaut`

Correspondance complète, relevée sur **tous** les appels de `sub_942CA` (lecture) et `sub_942DE`
(écriture) :

| sélecteur | voie | opération | preuve |
|---|---|---|---|
| **`0x8000`** | CA | **lire le nombre de défauts** | l. 207580, 207672 (`r13 = 0`) |
| **`0x9000`** | DE | **effacer toute la mémoire** | l. 207584 |
| **`0xFF00`** | CA | **lire l'enregistrement courant** | l. 201410, 201500 → `0xDC28` |
| **`0x80xx`** | CA | **lire les 154 octets** (tous) | `(rh6 & 0xE0)==0x80`, l. 229602 |
| **`0xEFxx`** | DE | **supprimer le défaut n° `xx`** | `0xEF57` (l. 152159), `byte_CFBE+0xEF00` (l. 153380) |
| **`0xDFxx`** | CA | **lire le défaut n° `xx`** | `byte_CFBE+0xDF00` (l. 153391) |
| **`0xD000`** | DE | **ajout / mise à jour** | l. 202007, **205291** |

**Preuve du codage** : `mov r12, #0EF57h` (l. 152158) tombe exactement sur les tests
`cmpb rh6, #0EFh` (*supprimer*) puis `cmpb rl6, rh5` (*si le numéro correspond*) — le `0x57` de
`0xEF57` **est** le numéro de défaut, donc **87**.

**Conséquence** : les 96 numéros de l'étape 39 ne sont pas une déduction — ils sont **utilisés
littéralement** (87 existe).

---

## 2. Qui touche la mémoire des défauts, et où

| ligne | sélecteur | contexte |
|---|---|---|
| **152159** | `0xEF57` (supprimer n° 87) | **dans le module EEPROM** (`loc_A1708`) |
| 153352 | `word_CFB6` → `0xCFBC` | lecture d'un enregistrement vers la zone EEPROM |
| 153380 | `byte_CFBE + 0xEF00` | suppression du défaut `byte_CFBE` |
| 153391 | `byte_CFBE + 0xDF00` | lecture du défaut `byte_CFBE` |
| 153464 | `0x0CF00` | — |
| 201410 / 201500 | `0xFF00` → `0xDC28` | lecture de l'enregistrement courant |
| 201715 … 201868 | `or r12,#1000h` puis `[r4+#0DC42h]+0xEF00` | lecture/suppression en série |
| 202007 | `0x0D000` | ajout/mise à jour |
| **205291** | `0x0D000` | **dans `sub_C008A` = service 0x04** |
| 206190 | `rl7` (dynamique) → `r0` | lecture sur le tampon de réponse |
| 207580 / 207584 | `0x8000` puis `0x9000` | **service 0x14 : compter puis effacer** |
| 207672 / 207717 | `0x8000` puis `word_DC90` | **service 0x17 : compter puis parcourir** |

**Deux observations qui comptent :**

1. Le **service 0x14** (effacement) fait bien `0x8000` (compter) **puis** `0x9000` (effacer) — il ne
   teste pas `r4 == 0` par hasard : il vérifie qu'il y a quelque chose à effacer.
2. **Le module EEPROM lui-même supprime le défaut n° 87** (l. 152159). C'est le seul point de
   contact direct que je trouve entre la zone EEPROM et la mémoire des défauts — **un indice, pas une
   preuve**, de l'existence d'une interaction EEPROM ↔ défauts.

---

## 3. ★ `sub_94C6A` : un verrou « à gâchette » (premier verdict gagnant)

```asm
sub_94C6A:
                movb    rl4, byte_F602
                jmpr    cc_NZ, locret_94C76    ; déjà posé -> on IGNORE
                mov     r5, r12
                movb    byte_F602, rl5         ; sinon on mémorise
locret_94C76:
                rets
```

**Neuf octets, et un mécanisme net : `byte_F602` enregistre le PREMIER code reçu et ignore tous les
suivants** jusqu'à remise à zéro.

Appelé avec **`0x0F`** et **`0xF0`** (l. 127586, 127603, 127610, 127925, 127931, 128658) : ce sont
des **masques de quartet**, pas des codes. ⇒ `byte_F602` mémorise **le premier verdict** sous forme
de quartet (`0x0F` = quart bas, `0xF0` = quart haut).

**Interprétation prudente** : c'est un **verrou d'état « premier événement »** — typiquement ce qui
fige la cause d'un refus avant que les vérifications suivantes ne la masquent. C'est le genre de
structure qu'un outil de diagnostic lit pour savoir **pourquoi** le calculateur a refusé quelque
chose. Je ne lui attribue pas l'antidémarrage : **ce n'est pas démontré.**

---

## 4. `sub_94C78` : un **tampon circulaire d'enregistrements de 4 octets**

```asm
sub_94C78:
                mov     r4, word_F60E          ; fin du tampon
                cmp     r4, word_F60C          ; == pointeur courant ?
                jmpr    cc_Z, loc_94CA8        ; vide -> rien
                mov     r5, word_F60C
                movb    [r12], [r5]            ; lit 1 octet
                mov     r4, word_F610          ; base
                add     r4, #4                 ; base + 4
                cmp     r4, word_F60C          ; rebouclage sur la base ?
                jmpr    cc_NZ, loc_94CA0
                mov     r4, word_F610
                mov     word_F60C, r4          ; oui -> retour à la base
                jmpr    cc_UC, loc_94CA4
loc_94CA0:
                sub     word_F60C, ONES
```

**Trois pointeurs** : `word_F610` = base, `word_F60E` = limite, `word_F60C` = curseur. Le
**rebouclage se fait sur `base + 4`** ⇒ les enregistrements font **4 octets** et le tampon est
parcouru **à rebours** (`sub word_F60C, ONES`).

⇒ C'est une **file d'événements de 4 octets**, consommée dans l'ordre inverse d'écriture. `byte_F602`
(§3) en est le **verrou de tête**.

*Note de rigueur* : la taille totale du tampon n'est pas connue (elle dépend de `word_F60E − word_F610`,
deux variables) ; je n'affirme donc ni le nombre d'emplacements ni la nature des événements.

---

## 5. Précision sur deux octets voisins, à ne pas confondre

| variable | rôle établi | étape |
|---|---|---|
| **`byte_F608`** | **verdict de cohérence de la configuration EEPROM** (commandes 0x0C/0x0D) | 36 §2.6 |
| **`byte_F62E`** | copie de `byte_F608` **protégée** par les deux mots magiques (`bclr IEN` si trahie) | 35 §3 |
| **`byte_F602`** | **verrou « premier verdict »** sous forme de quartet (`0x0F` / `0xF0`) | cette étape |

Trois octets proches en adresse, **trois rôles différents**. Les confondre conduirait à attribuer au
codage ce qui relève du verrou d'événement.

---

## 6. Tableau de bord

| question | état |
|---|---|
| codage des sélecteurs défauts | **décodé** (opération / numéro) ✔ |
| n° de défaut dans le code | **87 utilisé littéralement** ✔ |
| service 0x04 | fait un **ajout/mise à jour** de défaut (`0xD000`) ✔ |
| module EEPROM ↔ défauts | **supprime le défaut 87** (indice) |
| `byte_F602` | verrou à gâchette, quartets 0x0F/0xF0 ✔ |
| tampon `0xF6xx` | **file de 4 octets** à rebours ✔ (taille inconnue) |
| antidémarrage | toujours non localisé |

---

## 7. Prochaines actions

1. **`word_CFB6`, `byte_CFBE`, `0xCFBC`** : la petite zone de travail des défauts, **voisine des
   champs EEPROM** (`word_CF9E`, `byte_CFA0`) — c'est peut-être **le pont** entre défauts et EEPROM.
2. **`word_F60E` / `word_F610`** : bornes du tampon de 4 octets → nombre d'emplacements.
3. **Les 4 octets d'un enregistrement de la file** : chercher qui écrit `[word_F60C]` (et non qui
   lit).
4. **Antidémarrage** : après trois impasses (clé absente, `byte_F62E` = codage), la piste restante
   est la **chaîne de démarrage** — chercher une condition qui **inhibe l'injection** sur un bit, et
   non un mécanisme d'authentification.
