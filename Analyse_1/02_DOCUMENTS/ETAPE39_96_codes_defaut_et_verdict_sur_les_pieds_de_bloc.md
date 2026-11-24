# ÉTAPE 39 — 96 codes de défaut possibles, et deux verdicts négatifs utiles

---

## 1. ★ `0xCAD0` et `0xFD21` : **96 entrées**, indexées par le **numéro de code défaut**

Le code de `sub_CE43C` est explicite (l. 229923-229935) :

```asm
                movbz   r3, rh5             ; rh5 = numéro du code défaut ([r2+#0])
                add     r3, #0FD21h         ; ← tableau 1 : 1 octet par NUMÉRO
                movb    [r3], ZEROS
                movbz   r3, rh5
                shl     r3, #2              ; ← NUMÉRO × 4
                add     r3, #0CAD0h         ; ← tableau 2
                movb    [r3], ZEROS         ;     octet à +0
                add     r3, #2
                mov     [r3], ZEROS         ;     un MOT à +2
```

### 1.1 L'arithmétique tombe juste

| bloc | taille effacée | structure déduite |
|---|---|---|
| `0xFD21` … `0xFD80` | **96 octets** | **1 octet par numéro de défaut** → numéros **0 … 95** |
| `0xCAD0` … `0xCC4F` | **384 octets** | **96 × 4** : 1 octet à `+0`, 1 mot à `+2` (`+1` inutilisé à ce stade) |

`0xFD21 + 95 = 0xFD80` — **exactement** la fin de la zone effacée. ✔
`0xCAD0 + 4 × 96 = 0xCC50` — **exactement** la fin du bloc. ✔

⇒ **Le calculateur connaît jusqu'à 96 codes de défaut distincts**, chacun avec un drapeau et un état
de 4 octets. Mais il n'en **mémorise que 7** avec leur contexte (`0xE467`, 7 × 22 octets, étapes
36-37).

**Distinction importante** : 96 = **codes possibles** (table d'états), 7 = **codes mémorisés**
(table d'enregistrements). Ce sont deux structures différentes, souvent confondues.

### 1.2 La table des codes elle-même

`0xCCB2 + 2 × n` = un **mot par numéro de défaut** (192 octets, `0xCCB2-0xCD71`).
Deux usages observés :

- **émission** : `add r2, r2; add r2, #0CCB2h; mov [r5+], [r2]` → le mot est **envoyé tel quel**
  comme code de défaut (étape 35 §1.3) ;
- **consultation** : l. 230034-230040 → `shl r0,#1; mov r0,[r0+#0CCB2h]; movb rh0,[r0+#1Ch]; andb rh0,#3`
  → le mot sert alors d'**index d'accès** à un descripteur situé à `mot + 0x1C`.

⇒ Le mot de `0xCCB2` est **à la fois** le code transmis et un index dans une table de descripteurs
qui se trouve, elle, **dans la couche absente**. C'est cohérent avec le style Bosch
(code → classe/viellissement/stratégie), mais je ne peux pas le prouver : `mot + 0x1C` tombe sous
`0x80000`, donc hors du dump. **Je le signale comme fortement probable, pas comme établi.**

---

## 2. Verdict : **le pied de bloc n'est jamais vérifié par le code visible**

Recherche des seules formes qu'aurait un test de pied :

| forme testée | occurrences |
|---|---|
| `#0FFCh` (offset du checksum) | **0** |
| `#0FFAh` (offset de la marque `94C7`) | **0** |
| `0C794h` (la marque comme constante) | **0** |
| `#0F000h` (masque de fin de bloc) | **0** |

⇒ **Aucune instruction du programme présent ne relit, ne compare ni ne recalcule les 4 octets de
pied ni la marque `94C7`.** Ils appartiennent entièrement au boot absent (étape 35 §2 : `0A5A5h`
également 0 occurrence).

**Conséquence pour la suite du travail** : il est **inutile** de chercher l'algorithme du checksum
dans les 512 Ko que nous avons. J'ai déjà testé 4 CRC-16 et 3 sommes (étape 38 §3, tous ✘) ; la
conclusion est maintenant **structurelle**, pas seulement empirique.

---

## 3. `unk_7EC8` : une impasse par les appelants

`unk_7EC8` (EA `0x07EC8`, le calcul de graine du service 0x27) a **exactement un appelant** :
`sub_FE62E+7A` (l. 406181). Son corps est absent du dump (`ds 1`).

⇒ Pas de piste par les usages : c'est une **feuille** de la couche basse, appelée seulement par le
service de sécurité du bloc de boot, avec `r12 = 0xFC2E` (graine) et `r13 = 0xFC34` (clé).
**L'algorithme restera hors de portée sans le boot primaire.**

---

## 4. Ce que la mémoire des défauts contient, récapitulé

```
0xCAD0  96 × 4 octets   état par numéro de code   [0]=drapeau, [2]=mot
0xCCB2  96 × 2 octets   code de défaut / index de descripteur
0xCD8C …                (variables nommées, rôle non établi)
0xE466  compteur        nombre de défauts MÉMORISÉS (0…7)
0xE467  7 × 22 octets   enregistrements (code + contexte)
0xE501  22 octets       enregistrement courant (index 0xFF = aucun)
0xFD21  96 octets       par numéro de code
```

---

## 5. Tableau de bord

| question | état |
|---|---|
| codes de défaut possibles | **96** ✔ (0xFD21 = 96 octets, 0xCAD0 = 96 × 4) |
| défauts mémorisés | **7 × 22 octets** ✔ |
| table des codes | `0xCCB2`, 96 mots ✔ |
| descripteurs de défaut | **couche absente** (`mot + 0x1C`), probable |
| checksum de bloc | **jamais vérifié** par le code visible ✔ |
| clé de sécurité | `unk_7EC8`, **feuille sans autre appelant** ✔ |
| antidémarrage | non localisé |

---

## 6. Prochaines actions

1. **Branche d'ajout de `sub_CE43C`** (l. 229880-230000) : c'est là que se décident
   **l'incrémentation, le vieillissement et la remontée** d'un défaut — donc la partie « DTC
   persistants » que tu cherches.
2. **`0xCAD0 + 4n` : le mot à `+2`** — probablement un compteur d'occurrences ou une date ; à
   identifier par ses lecteurs.
3. **Anti-démarrage** : puisque la clé est hors d'atteinte, chercher la **décision** — c'est-à-dire
   quel drapeau autorise ou interdit l'injection. Piste concrète : les appelants de
   `sub_94C6A(0x0F/0xF0)` et la chaîne `byte_F608`.
4. **`word_CCB0` / `word_CCA4` / `byte_CCA7`** : la tête du bloc de diagnostic, non encore lue.
