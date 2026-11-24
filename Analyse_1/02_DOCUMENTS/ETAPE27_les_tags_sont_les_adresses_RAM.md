# ÉTAPE 27 — La clé structurelle : **les tags d'axe sont les adresses RAM des variables**

C'est le résultat qui débloque tout le reste, et il répond à la question posée depuis l'étape 1
(« adresse = identité + type + tag ») : **le tag *est* l'identité.**

---

## 1. La preuve, triple

En-tête du smoke map `EA 0xE8444`, octet par octet :

| champ | valeur | vérification |
|---|---|---|
| `tagY` | **`0xC42E`** | `word_C42E` = le **régime** ; axe `0 … 5200` tr/min ✔ |
| `tagX` | **`0xC3E6`** | `word_C3E6` = le **débit d'air** ; axe `3000 … 11500` = **300 … 1150 mg/s** ✔ |
| (autre carte) | **`0xC38E`** | `word_C38E` = la **pression atmosphérique** ; axe `850 … 960` **mbar** ✔ |

Trois variables indépendamment identifiées, trois tags qui tombent exactement sur leur adresse.
**Ce n'est pas une corrélation : c'est le mécanisme.**

⇒ Dans un en-tête d'enregistrement, le mot qui précède le nombre de points n'est pas un « type »
abstrait : c'est **l'adresse de la variable d'axe en RAM**. Le calculateur y lit sa variable au
moment de l'interpolation.

## 2. L'inventaire des axes — 44 variables

Scan de toute la zone de calibration (`0xE0000-0xEBFFF`) : **273 enregistrements** à tag valide,
dont **65 cartes 2-D**, et **44 tags distincts**. Chaque tag est une variable d'axe.

| tag (adresse RAM) | nb cartes | axe | unité déduite | statut |
|---|---|---|---|---|
| `0xC42E` | **112** | 200 → 4000 | **régime tr/min** | **identifié** |
| `0xC3D2` | 42 | 2901 → 3731 | **température K×10** (−27…+100 °C) | déduit |
| `0xC6A2` | 36 | 0 → 7000 | régime ou débit | **inconnu** |
| `0xC60A` | 20 | 700 → 750 | pression (mbar) | déduit |
| `0xC3BA` | 15 | 2581 → 3331 | température K×10 | déduit |
| `0xC7C2` | 11 | 1190 → 14000 | débit / mg | inconnu |
| `0xC60E` | 8 | 800 → 7000 | pression ou régime | inconnu |
| `0xC3B0` | 7 | 3271 → 3931 | température K×10 | déduit |
| `0xC3EE` | 6 | 0 → 4910 | ? | inconnu |
| `0xC68A` | 5 | 0 → 7000 | ? | inconnu |
| `0xC3C2` | 5 | 0 → 508 | mg/cycle (0…50,8) | déduit |
| `0xC5A8` | 5 | 100 → 11000 | ? | inconnu |
| `0xC78A` | 4 | 200 → 6000 | régime | déduit |
| `0xC3A8` | 4 | 400 → 2400 | mg/cycle | déduit |
| `0xC562` | 4 | 0 → 20000 | ? | inconnu |
| `0xC3E6` | 4 | 3000 → 11500 | **débit d'air mg/s ×10** | **identifié** |
| `0xC6DA` | 4 | 118 → 10000 | ? | inconnu |
| `0xC612` | 3 | 700 → 850 | pression mbar | déduit |
| `0xC5BC` | 3 | 32768 → 36128 | **couple** (offset 32768) | déduit |
| `0xC5FA` | 3 | 2331 → 3031 | température K×10 | déduit |
| `0xC586` | 3 | 5231 → 8231 | ? | inconnu |
| `0xC7C6` | 3 | 3000 → 12000 | débit mg/s | déduit |
| `0xC63C` | 2 | 0 → 15360 | ? | inconnu |
| `0xC77A` | 2 | 6667 → 28333 | ? | inconnu |
| `0xC38E` | 2 | 850 → 960 | **pression atmo mbar** | **identifié** |
| `0xC58E` | 1 | **0 → 1** | **axe booléen** (!) | remarquable |
| `0xC590` | 1 | 0 → 90 | % ou °C | déduit |
| `0xC337` | 1 | **0 → 250** | **km/h ?** | **candidat — voir §3** |

*(les 17 autres tags sont dans le même fichier de scan ; liste complète reproductible par
`outils/scan_tags.py`)*

**À retenir** : sur 44 variables d'axe, **une seule** couvre une plage compatible avec une vitesse
véhicule (0…250 sur un octet). C'est une contrainte quantitative forte, et elle donne un candidat.

## 3. `0xC337` — le candidat vitesse, et ce qui le contredit

```asm
; production — l. 182810-182814 (seg015)
mov  r12, word_1B5E       ; ← handle d'une carte 2-D
mov  r13, word_C91C       ; X = régime
mov  r14, word_D9AA       ; Y = variable secondaire
calls 0, unk_1D50         ; interpolation 2-D
movb byte_C8F8, rl4       ; ← résultat, un OCTET
```

```asm
; passage de relais — l. 139693-139696 (début de tâche seg013)
mov  r4, word_C42E ; mov word_C91C, r4     ; le régime
movb rl4, byte_C337 ; movb byte_C8F8, rl4  ; … et C337, ensemble
```

et la courbe 1-D `EA 0xE4954` qui l'utilise comme axe :

| champ | valeur |
|---|---|
| `tagY` | **`0xC337`** |
| `n` | 2 |
| axe | **0, 250** |
| valeurs | **1000, 9000** |

**Ce qui plaide pour la vitesse** : plage 0…250 sur un octet, unique parmi 44 axes ; recopié en
même temps que le régime (le couple « état moteur » du calculateur).

**Ce qui contredit la vitesse** : `C337` est la **sortie d'une carte 2-D indexée par le régime**.
Une vitesse obtenue par une carte (régime × Y) n'a pas de sens physique direct — alors qu'un
**couple en Nm** (0…250) en aurait un parfaitement (protection couple/régime).
**Je ne tranche pas.** Les deux lectures tiennent.

⇒ Test décisif proposé : décoder `word_1B5E` (la carte 2-D qui produit `C8F8`) et regarder la
**forme de la grille**. Une grille « couple vs régime × rapport » ou « couple max vs régime »
révélera la nature ; une grille de vitesse serait plate en régime, ce qui serait anormal.

## 4. Ce que cela change pour la question du rapport

Le modèle « adresse + type + tag » étant établi, on peut enfin formuler la recherche correctement :
**le rapport engagé n'a pas besoin d'être calculé si une carte peut le fournir.** Et l'on voit
apparaître une architecture cohérente :

- `word_1B5E` : carte 2-D → **une variable d'état** (`C8F8`/`C337`) ;
- `C337` sert ensuite d'**axe** à la courbe `0xE4954` (→ 1000…9000) ;
- et cette courbe alimente la chaîne de couple.

Ta lecture (v et RPM → ratio) et la lecture « carte » ne s'excluent plus : **les deux passent par
`C337`**. Si `C337` est bien la vitesse, alors la vitesse **existe** (tu avais raison) et elle est
produite par une carte — ce qui expliquerait pourquoi aucune division vitesse/régime n'existe.

## 5. Le kilométrage : où chercher

Ton raisonnement (copie du total km dans le BSI et l'ABS, sauvegarde ECU à la coupure) est
plausible et **testable**, même sans dump de l'EEPROM. Ce que j'ai déjà vérifié :

| piste | résultat |
|---|---|
| interface **SSC/SPI** (EEPROM série typique) | **aucun SFR SSC** dans le désassemblage → pas d'EEPROM sérielle classique |
| **bit-bang** sur ports (`bset Px.y` / `bclr Px.y`) | **aucune** instruction de ce type |
| écritures de port | `P2`, `P3`, `P4` (`#1`, `#2`), `P9` — à qualifier |
| **PEC** (Peripheral Event Controller) | **50 accès** aux registres `PECC0-7` → transferts rapides par événement |
| redondance `xor #0FFFFh` (signature d'une paire valeur/inverse) | **5 sites seulement** : l. 97916, 98216, 199051, 200177, 210590 |

⇒ Il n'y a **pas** d'EEPROM série visible. Deux lectures possibles, et je les donne sans trancher :
soit la sauvegarde passe par une routine de la **bibliothèque absente** (`calls 0, …`, 1288 appels),
soit elle utilise une **zone flash émulée** écrite par le PEC.

**Prochaine action concrète** : le **power latch**. La séquence de coupure est reconnaissable (elle
écrit les apprentissages puis coupe le relais principal). En la localisant, on trouve la fonction de
sauvegarde — et donc le compteur kilométrique qu'elle écrit.

## 6. Livrables

- `outils/scan_tags.py` — extrait les 273 enregistrements et les 44 tags (reproductible).
- Les trois identifications de tags sont **vérifiées sur les octets**, pas inférées.

## 7. Lu / inféré

| affirmation | statut |
|---|---|
| tag d'axe = adresse RAM de la variable d'axe | **lu + vérifié 3×** |
| 273 enregistrements / 65 cartes 2-D / 44 axes | **lu** (scan reproductible) |
| axe = plage de la variable, donc son unité probable | **inféré** (cohérent sur les 3 cas connus) |
| `C337` = vitesse | **non tranché** — plage compatible, production par carte contradictoire |
| pas d'EEPROM série visible | **lu** (absence de SFR SSC et de bit-bang) |
| sauvegarde km dans la bibliothèque absente ou flash émulée | **inféré** |
