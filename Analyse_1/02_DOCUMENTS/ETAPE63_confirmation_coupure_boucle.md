# ÉTAPE 63 — `0xE111E+0x0B` coupe bien la boucle : re-confirmation

> Tu me donnes la réponse (boucle EGR désactivée) et tu me demandes de la re-confirmer.
> **Je la confirme, mais avec le mot juste** : l'octet ne « débranche » pas une fonction nommée EGR —
> il **met toutes les entrées du régulateur à zéro**. Et j'apporte la preuve que la boucle est une
> **boucle d'air**, plus le seul doute qui subsiste.

---

## 1. Ce que l'octet fait exactement — les **trois** sites, pas un

`0xE111E + 0x0B` vaut **`0x00`** dans ce firmware et est testé **trois fois** :

| site | code | effet |
|---|---|---|
| `l.196410` | `jmpr cc_NZ, loc_BB548` | `word_DB64 = 0` **et** `word_DB66 = 0` → **consigne annulée** |
| `l.196439` | `jmpr cc_NZ, loc_BB566` | force `r5 = 0` puis `mov [r0], r5` → la valeur interpolée rangée dans `word_D492` est **zéro** |
| `loc_BB550` | branche atteinte | `word_DB6C = 0` **et** `word_DB6E = 0` → **terme accumulé effacé** |

**Consigne à zéro + intégrale à zéro ⇒ le régulateur ne peut plus rien produire.** C'est bien une
**coupure de boucle fermée**, pas une simple option d'affichage.

**Nuance de vocabulaire, pour rester exact** : ce n'est pas un « switch EGR » au sens d'un interrupteur
qui court-circuite un bloc de code nommé (comme les sélecteurs de `0xE6542`, étape 61). C'est un
**interrupteur de boucle** : il n'enlève pas le code, il met les entrées à zéro. L'effet observable est
le même — **la boucle ne régule plus**.

---

## 2. La boucle, étage par étage

| # | étage | preuve |
|---|---|---|
| 1 | **consigne** | carte **8 × 8** `word_1C98` → **EA `0xE9660`** ; appel `l.196401` : `unk_1D50(handle, word_C91C, r8)` |
| 2 | **repli** | constante calibrée `word_C506` si bits `0x800`/`0x200` de `[word_1468]` (`l.196419`) |
| 3 | **correction** | courbe `word_1C90` → **EA `0xE9626`**, n=2 → **valeurs `0` et `0` : correction neutre** |
| 4 | **régulateur PI** | `unk_2020` (2 appels) puis `unk_1EBC` ; **saturation `0x7FFF`/`0x8000`**, butées `[r7]`/`[r7+2]` |
| 5 | **anti-rebond** | `sub_BAC40` : état `[r13]` 0…`0xFF`, compare `r12`, rend 0/1 + drapeaux `DB84`/`DB86` |
| 6 | **moniteur de dérive** | `l.197160` : `word_DB68 + word_DB66` vs `[word_14A0+0x5C]`, 2ᵉ condition `[word_14A0+0x4C] ≥ word_DB52` ⇒ compteur `word_DB5E` **saturé à `0x7FFF`** |

---

## 3. ★★ La carte de consigne, décodée octet par octet

**`word_1C98` → EA `0xE9660`** (vérifié dans la table de pointeurs : entrée `0x1C98` = `0x9660`) :

| champ | valeur | lecture |
|---|---|---|
| tag Y | **`0xC42E`** | **régime moteur** |
| n Y | `8` | `200, 500, 750, 1000, 1500, 2000, 3000, 4000` |
| tag X | **`0xC7B8`** | grandeur **dérivée**, pas un capteur brut (recalculée `l.190859` après un **max-glissant** `word_DBB8`) |
| n X | `8` | `2000, 3000, 5000, 7000, 9000, 10000, 11000, 13000` |
| grille | `8 × 8` | 64 valeurs |

**C'est le point qui rend ta réponse cohérente** : une consigne bâtie sur une carte
« **régime × grandeur de 2 000 à 13 000** » n'est pas une consigne de carburant — le débit de carburant
se *calcule* (masse d'air / rapport stœchiométrique / limiteurs), il ne se lit pas sur une carte
8 × 8 de cette forme. **C'est une boucle d'air.**

---

## 4. Le seul doute qui subsiste — et je ne le masque pas

**`word_C7B8` : air (×10 ⇒ 200…1300 mg) ou pression (mbar) ?** Les deux donnent la même plage
2000…13000. Tant que ce mot n'est pas nommé, **je ne peux pas séparer EGR de suralimentation (VNT)** :
les deux se règlent en boucle fermée sur une carte régime × air/pression, avec PI et moniteur d'écart.

**Le test qui tranche** : remonter `word_C7B8` jusqu'à sa source capteur.
- s'il descend du **débitmètre** (`word_C3E6`, confirmé à 100 %) ⇒ **c'est l'EGR** ;
- s'il descend du **capteur de pression de collecteur** ⇒ c'est la **suralimentation**.

Je ne conclus donc pas « EGR prouvé », je conclus « **boucle d'air coupée par l'octet, EGR étant
l'hypothèse la plus probable, un seul test reste à faire** ».

---

## 5. Les sorties de la boucle ne pilotent rien directement

`word_D48E`, `word_D49C`, `word_D4A4`, `word_D49E`, `word_D4A8`, `word_D4AE`, `word_D4B0`, `word_D4B2`
sont **écrits et jamais relus** dans tout le listing (vérifié mot par mot) : ce sont des
**images de mesure** (bloc diagnostic / CAN), **pas des commandes**.

La grandeur qui sort réellement de la boucle est `word_DB6A` / `word_DB6E`, consommée **uniquement**
par la couche absente (`unk_2020`, `unk_1EBC`, corps `ds 1`).

⇒ D'où l'état exact de la question :

> **`+0x0B` neutralise bien la boucle — au niveau du calcul. L'actionneur physique, lui, n'est toujours
> pas nommé.** Ce n'est pas un recul : c'est la différence entre « la régulation est coupée » (prouvé ici)
> et « quelle électrovanne est au bout » (à faire).

---

## 6. Consignation

- **`CATALOGUE_MAITRE.md` § 13 B.9** ajouté (1 985 → **2 044 lignes**).
- Chaîne désormais documentée : `0xE111E+0x0B` → consigne zéro → `unk_2020` → `word_DB6A/DB6E` → couche absente.

## 7. Prochain pas (ordre de priorité)

1. **`word_C7B8` → source capteur.** Un seul grep bien mené sépare EGR de VNT. **Priorité absolue.**
2. **La sortie PWM** : chercher le mot écrit juste avant `CC1_CC1` / les canaux de rapport cyclique,
   et remonter jusqu'à `word_DB6A`.
3. `byte_C2BA` (`0xE111E+0x27`, 63 références) — le seul octet du bloc à fort rayonnement.
4. Le corps de `unk_2020` : les gains du PI restent invisibles dans la couche `ds 1`.
