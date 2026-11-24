# ÉTAPE 44 — Revue transversale : **toutes** les portes de l'EEPROM dans le listing

*Revue demandée : balayage complet du désassemblage sur l'axe EEPROM, sans hypothèse préalable.*

---

## 0. Le résultat de la revue, en une phrase

**L'EEPROM n'a que deux portes dans tout `clean.asm`**, et une seule est « officielle » :

| porte | plage | nature |
|---|---|---|
| **module `sub_A0002`** | 149 775 → 152 100 (≈ 2 300 lignes) | image EEPROM, primitives, descripteur 12 o |
| **`sub_95E78`** | 128 999 → 129 403 (404 lignes) | **magasin à 6 enregistrements auto-descriptifs** |

Tout le reste du calculateur (défauts, cartes, CAN, immo) **ne calcule jamais une adresse
EEPROM** : il passe par l'une de ces deux portes.

---

## 1. ★ Preuve du confinement : les 74 sites de la constante `0xE5CE`

La base de l'image EEPROM est `0xE5CE` (étape 33). J'ai relevé **les 74 occurrences** :

- **la première est à la ligne 149820**, la dernière à **152096** (+ les 4 reports à `0xCFA4`) ;
- **aucune occurrence avant 149820, aucune après 152100.**

```asm
149820:  mov  r5, #0E5CEh
...
150171:  movb rl5, [r4+#0E5CEh]      ; lecture unitaire
150180:  movb [r4+#0E5CEh], rl6      ; écriture unitaire
...
152096:  mov  r3, #0E5CEh
```

⇒ **Aucune fonction applicative ne construit une adresse EEPROM à la main.** Le calcul
`handle → page → offset → 0xE5CE + offset` (étape 33) est **l'unique voie d'accès**. C'est une
garantie forte : si un champ EEPROM existe, il est **forcément** atteignable par un handle du
descripteur `0x0BA6`, donc **forcément** visible dans l'inventaire des 1 304 handles.

**Corollaire négatif, important** : la quête « trouver la fonction qui écrit le kilométrage / le PIN /
le VIN » ne peut pas aboutir à une fonction exotique hors module. Elle aboutit à **un numéro de
commande** de `sub_A0002`. C'est là qu'il faut chercher.

---

## 2. ★ `sub_95E78` : un magasin de **6 enregistrements**, en deux tables

Découverte de cette revue. Les enregistrements sont en RAM et ont **deux tailles** :

| table | adresses | pas | taille | nombre |
|---|---|---|---|---|
| **A** | `0xF819`, `0xF821`, `0xF829` | **8 o** | 8 octets | 3 |
| **B** | `0xF831`, `0xF835`, `0xF839` | **4 o** | 4 octets | 3 |

Les trois adresses de B sont à **pas de 4** — donc B est bien une table distincte, pas la suite de A.
Preuves : écritures `byte_F819/F821/F829/F831/F835/F839` (l. 129022, 129036, 129050, 129064,
129078, 129092) et lectures via pointeurs `0F819h…0F839h` (l. 129779-129822).

### Le sélecteur

l. 129765-129822 :

```asm
                movb  rl4, byte_F842
                cmpb  rl4, #0
                jmpr  cc_Z, loc_96596          ; -> 0F819h
                cmpb  rl4, #1
                jmpr  cc_Z, loc_965A0          ; -> 0F821h
                cmpb  rl4, #2
                jmpr  cc_Z, loc_965AA          ; -> 0F829h      (table A)
loc_965B4:
                movbz r4, byte_F83C
                and   r4, #2
                jmpr  cc_Z, ...                ; porte : bit 1 de byte_F83C
                movb  rl4, byte_F842
                jmpr  cc_Z, loc_965CC          ; -> 0F831h
                cmpb  rl4, #1
                jmpr  cc_Z, loc_965D6          ; -> 0F835h
                cmpb  rl4, #2
                jmpr  cc_Z, loc_965E0          ; -> 0F839h      (table B)
```

⇒ **`byte_F842` (0/1/2) choisit l'indice**, `byte_F83C & 2` **autorise la table B**. Le pointeur
retenu est publié dans **`word_C18A`**.

### ★ L'enregistrement est **auto-descriptif**

l. 129904-129907 :

```asm
                movb  rl4, byte_F83D
                cmpb  rl4, #3
                ...
                mov   r4, word_C18A           ; l'enregistrement selectionne
                movb  rl5, [r4]               ; [enregistrement + 0]
                movbz r12, rl5                ; -> COMMANDE de sub_A0002
                mov   r13, r0
                calls 0Ah, sub_A0002
```

⇒ **le premier octet de l'enregistrement sert de numéro de commande** pour le module EEPROM.
Chaque enregistrement **sait comment se persister**.

Valeurs observées à `[+0]` : **0x1D** (0xF819), **0x21** (0xF821), **0x24** (0xF829),
**0x1E** (0xF831), **0x22** (0xF835) — l. 129022/129036/129050/129064/129078.
La sixième (0xF839) est écrite l. 129092, valeur non relevée.

*Réserve honnête* : le chemin de **construction** (l. 129028, 129065, 129075, 129085) passe des
immédiats **explicites** — `#21h`, `#1Eh`, `#22h`, `#25h` — qui ne coïncident pas toujours avec
`[+0]`. Je ne tranche pas entre « `[+0]` = commande » et « `[+0]` = identifiant de contenu » : les
deux lectures sont défendables selon le chemin. **Ce point est à vérifier, pas à retenir.**

### Le rythme d'écriture est **temporisé**

l. 129826-129860 :

```asm
                movb  rl4, byte_F83D
                cmpb  rl4, #1
                jmpr  cc_NZ, loc_96646
                mov   r4, word_C468
                jmpr  cc_Z, loc_96624
                mov   r5, word_C126
                cmp   r5, word_F91C
                jmpr  cc_NC, loc_9660C            ; correction de rebouclage
                mov   r4, word_C126
                sub   r4, word_F91C
                sub   r4, #1
loc_9660C:
                mov   r4, word_C126
                sub   r4, word_F91C
loc_96614:
                cmp   r4, #23h ; '#'              ; 35 unites
```

⇒ **même idiome temporel que partout** (`word_F91C`, correction `−1` au rebouclage) et **seuil 35**.
Donc l'écriture n'est pas immédiate : elle est **lissée** — ce qui est exactement ce qu'on attend d'une
donnée qui change vite (un compteur) et qu'on ne veut pas voir user l'EEPROM.

### Appelants

- **`sub_9694E + 0x3C`** (fonction englobante) ;
- **l. 130184 `calls 9, sub_95E78`** — second point d'entrée.

`byte_C8F5` est écrit en entrée de fonction (`sub_95E78+0x16`) : c'est le **drapeau d'activité**
du magasin.

---

## 3. Les 20 appelants de `sub_A0002`, classés en 4 familles

| famille | sites | ce qui est persisté |
|---|---|---|
| **F1 — configuration à triple redondance** | l. 127438 (cmd `0x0B`), 127491 (`0x0C`), 127544 (`0x0D`) | `0xF7F6` (3 mots) et `0xF7FD` (3 octets), XOR avec `word_B8E/B90/B92` — étape 36 |
| **F2 — le magasin `sub_95E78`** | l. 129029, 129040, 129055, 129065, 129075, 129085, 129904 | les 6 enregistrements (§2) |
| **F3 — les 4 files de report** | l. 152332, 152521, 152790, 152979 | `word_C462/C464/C466/C468` → tampon `0xCFA4`, `byte_CF9D` = drapeau |
| **F4 — les deux sélecteurs dynamiques** | l. 128443 (`byte_F80E == 3` → `word_C186`), 206384 (`MDH + 0x10`) | commande **calculée à l'exécution** |

### Famille F3 — le mécanisme de report, vu de près

l. 152326-152334 (identique à ×4, seul le numéro de slot change) :

```asm
                mov   r12, word_C462
                calls 0Ah, nullsub_8          ; ← FONCTION ABSENTE
                movb  byte_CF9D, ZEROS
                mov   word_C462, ZEROS
                mov   r4, word_C462
                movb  rl5, [r4]
                movbz r12, rl5
                mov   r13, #0CFA4h            ; ← tampon commun
                calls 0Ah, sub_A0002
```

Trois observations :

1. **`nullsub_8` = fonction vide dans le listing** — c'est la **couche absente** qui refait surface :
   `r12` reçoit `word_C462` et l'appel ne fait rien de visible. C'est le **hook** par lequel le
   firmware d'origine vidait la file. **Nous ne pouvons pas le reconstituer.**
2. **le drapeau est remis à zéro avant l'appel** (`byte_CF9D = 0`) : la demande est **consommée
   d'abord, écrite ensuite** — pas de double écriture si l'écriture échoue, mais **perte possible**.
3. **un seul tampon `0xCFA4` pour 4 slots** : les 4 files sont donc **sérialisées** par ce tampon.

---

## 4. ★ ERratum à l'étape 43 §4

J'avais noté une « coïncidence » entre les **5 entrées** de la boucle `0xC9F3` (étape 43 §4) et les
« 5 identifiants EEPROM ». **La revue la réfute** : le magasin compte **6** enregistrements
(3 × 8 o + 3 × 4 o), pas 5. **La coïncidence tombe.** Les 5 entrées de l'étape 43 restent
non identifiées.

Je conserve en revanche l'autre remarque (la duplication de bits comme style de redondance) : elle
reste une observation de forme, pas une preuve.

---

## 5. Ce que la revue change dans la stratégie

Réponse directe à la question posée : **oui, il y a d'autres liens**, et ils sont de trois ordres.

1. **Un magasin inconnu jusqu'ici (`sub_95E78`)** — 6 enregistrements, persistés par commande,
   rythmés à 35 unités d'horloge, pilotés par `byte_F842`/`byte_F83C`. **C'est le meilleur candidat
   restant pour « ce que l'ECU mémorise de lui-même »** : ces enregistrements ne viennent pas d'une
   requête de diagnostic, ils sont **internes**.
2. **Deux points d'entrée à commande calculée** (F4) : `word_C186` et `MDH+0x10`. Ce sont les seuls
   endroits où le numéro de commande **n'est pas un immédiat** — donc les seuls où une *table* de
   commandes existe en RAM. À creuser : `word_C186`.
3. **La couche absente a un nom** : `nullsub_8`, appelée **exactement 4 fois**, une par slot de la
   famille F3. Ce n'est plus « du code manquant » indistinct : c'est **une fonction précise, à un
   rôle précis**, dont il ne reste que la signature d'appel.

---

## 6. Prochaines actions

1. **`word_C186`** (famille F4) : où est-il construit ? C'est le seul endroit où une commande EEPROM
   vient d'une table.
2. **`sub_95E78` : lire son entrée** (l. 128999-129030) pour savoir **ce qui déclenche** la mise à
   jour des 6 enregistrements — c'est la réponse à « qui écrit et pourquoi ».
3. **`byte_C8F5`** : drapeau d'activité du magasin, à relier au power latch (`word_FD0C.15`).
4. Rechercher `nullsub_8` dans le listing IDA (`uploads/…ANALYSE_R13.asm.txt`) pour vérifier s'il y
   porte un nom — l'IDA peut avoir résolu ce que le listing plat n'a pas résolu.
