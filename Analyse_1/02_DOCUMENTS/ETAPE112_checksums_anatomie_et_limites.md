# ÉTAPE 112 — Checksums : anatomie complète, et ce qui résiste

**Résultat honnête : la structure du système est maintenant élucidée, l'algorithme n'est PAS cassé.**
**Trois des cinq « checksums » de l'Étape 105 n'en sont pas — et c'est une bonne nouvelle.**

---

## 1. ★★★ La vraie structure : des trailers de 6 octets `94 C7` + u32

Chaque bloc se termine par **6 octets** : marqueur `94 C7` puis **un checksum 32 bits**.
**14 occurrences** dans le dump :

| # | EA du marqueur `94 C7` | u32 stocké (LE) | domaine |
|---|---|---|---|
| 1 | `0x8FFFA` | — | code |
| 2 | `0x93FFA` | — | code |
| 3 | `0xAC2CC` | — | code |
| 4 | `0xAC404` | — | code |
| 5 | `0xD2998` | — | code |
| 6 | `0xDFFFA` | `0x130D40FC` | code (fin de page D) |
| 7 | **`0xE0FFA`** | **`0xB20532C9`** | ★ calibration banque A, 1er bloc |
| 8 | **`0xEBCFA`** | **`0x5BD935DD`** | ★ calibration banque A, bloc principal |
| 9 | **`0xF0FFA`** | `0xC0CDD4CD` | ★ banque B, 1er bloc |
| 10 | **`0xFBCFA`** | **`0xAF775C20`** | ★ banque B, bloc principal |
| 11 | `0xFC2FA` | `0xD97B6BB1` | appendix / records BOOT |
| 12 | `0xFC5FA` | `0x276E5435` | appendix |
| 13 | `0xFC8FA` | `0xCC8254A1` | appendix |
| 14 | `0xFEBFA` | `0xF0262558` | appendix |

⇒ Les vrais checksums qui protègent notre patch sont **#8 (`0xEBCFC-FF`)** et **#10 (`0xFBCFC-FF`)**.

## 2. ★★★ Trois fausses pistes de l'Étape 105, levées

| site | ce que l'Étape 105 disait | réalité | preuve |
|---|---|---|---|
| **`0xE0FF6-9`** = `3D D3 3D D3` | checksum | **signature `0xD33D` répétée 2 fois**, comparée à une **constante** dans le code | `sub_BCEBE` l.198817-198827 : `mov r0,#3FF8h / mov r1,#3FF6h / extp r2,#1 / cmp r4,#0D33Dh` ×2 ; `loc_90686` l.111788-111792 : `cmp r0, word_DFFF8 / subc r0, #0D33Dh` |
| **`0xE434D`** | checksum | **l'unique octet qui diffère entre les deux banques** (`0x23` en A, `0x03` en B) ⇒ **octet de variante de codage** | comparaison intégrale des blocs `0xE1000-0xEBCF9` / `0xF1000-0xFBCF9` : 44 282 octets, **1 seule différence**, à `0xE434D` |
| **`0xEBF1B`** | checksum | **champ ASCII** : `"WGDWPF1"`, `"075WF2S010384"` ⇒ **identifiant logiciel/pièce** | dump du contexte immédiat |

★ **Conséquence directe** : notre patch ne touche **ni la signature `0xD33D`, ni l'octet de variante, ni les chaînes ASCII**. Rien à recalculer de ce côté.

## 3. Ce qui protège réellement notre patch

`0xE2788` et `0xE2792` (banque A) sont dans le bloc **`0xE1000 → 0xEBCF9`**, protégé par le
trailer `0xEBCFA` (`94 C7` + `0x5BD935DD`). Idem banque B avec `0xFBCFA` (`0xAF775C20`).

**★ Contrainte structurale majeure** : les deux mots du u32 ont **tous les deux changé** quand un
seul octet du bloc a changé (`0x35DD·0x5BD9` → `0x5C20·0x77AF`). Donc **ce ne sont pas deux
checksums indépendants de deux sous- zones**, mais **un seul checksum 32 bits sur la zone entière**.

## 4. ★★ Ce que le différentiel nous apprend (et ce qu'il exclut)

Deux banques identiques à **1 octet près** ⇒ expérience idéale : la variation de checksum est une
**fonction pure de (valeur modifiée, distance à la fin de zone)**.

- variation **XOR** = `0x5BD935DD ^ 0xAF775C20` = **`0xF4AE69FD`**
- variation **arithmétique** = `0x539E2643`

Un delta aussi énorme pour un octet passant de `0x23` à `0x03` **exclut toute somme additive**
(une somme simple n'aurait bougé que de `±0x20`), **exclut les sommes pondérées** (`±0x20 × position`
= au plus `0x0024xxxx`, pas `0x539E2643`).

**Balayages effectués, tous négatifs :**

| famille testée | variantes | résultat |
|---|---|---|
| **CRC-32/16 standards** | 48 combinaisons (poly `1021`, `8005`, `3D65`, `8BB7`, `04C11DB7`, `1EDC6F41` × refin/refout × init × xorout) × 3 blocs × 2 ordres d'octets | **0 match** |
| **Sommes additives** | somme octets, octets swappés, mots LE, mots BE, repliement 16 bits, complément à 1/2, XOR | **0 match** |
| **Sommes pondérées** | `Σ i·octet`, `Σ (i+1)·octet`, `Σ (i+1)·mot` | **0 match** |
| **Bornes de zone** | 9 combinaisons de début (`0xE0000`, `0xE1000`, `0xE0E72`) et de fin (dernier octet ≠ `C3` = `0xEBC47`, `0xEBCF6`, `0xEBCFA`) | **0 match** |
| **★ Différentiel CRC-32** | opérateur linéaire « ajouter un octet nul » (réfléchi *et* non réfléchi, polys 32 bits), distances 0 → 48 000 | **aucune distance ne produit `0xF4AE69FD`** |

⇒ **Ce n'est pas un CRC standard, ni une somme.** C'est un **calcul propriétaire Bosch**
(vraisemblablement à tables nibble/octet spécifiques), et son code **n'est pas dans `clean.asm`** :
aucune référence aux adresses `0xE0FFC`, `0xEBCFC`, ni à la constante `0xC794` n'existe dans le
désassemblage. Le vérificateur est donc dans une zone **non désassemblée** (bibliothèque effacée
ou second étage du boot).

## 5. Un point troublant, à noter

Le code (`sub_BCEBE`, `loc_90686`) cherche la signature `0xD33D` à **`0xDFFF6` / `0xDFFF8`**
(`extp` page `0x37` = `0xDC000` + `0x3FF6/0x3FF8`). Or le dump contient à ces adresses
**`0x0000` et `0xC794`**, et la paire `0xD33D` se trouve à **`0xE0FF6` / `0xE0FF8`** — soit
**exactement `+0x1000`**.

Deux hypothèses, non tranchées :
1. **l'adresse effective (runtime) de la calibration diffère de l'adresse fichier de `0x1000`** ;
2. le dump est une image d'atelier dont la signature n'est pas à l'emplacement vérifié.

C'est important : si (1) est vrai, alors **les trailers aussi sont décalés** dans l'espace runtime,
et c'est l'image entière qu'il faut re-mapper avant tout calcul.

---

## 6. Conséquence pratique pour le patch 2nde / 20 km/h

**Le patch n'est pas flashable en l'état** — non pas à cause des 8 octets modifiés, mais parce que
les 2 checksums de zone ne peuvent pas être recalculés sans l'algorithme.

### Protocole de test sûr et réversible (à faire avant tout)

> **Modifier UN seul octet de remplissage `C3`** dans la zone protégée (par ex. `0xE0E80` = `C3`),
> flasher, et observer :
> - **DTC de checksum / refus de démarrage** ⇒ les trailers sont **vérifiés** par l'ECU ⇒ toute
>   modification de calibration est impossible sans casser l'algorithme ;
> - **aucun défaut, comportement inchangé** ⇒ les trailers ne sont **pas** vérifiés à l'exécution
>   (ils servent au outil de programmation) ⇒ **notre patch passe tel quel**.

Ce test ne change **strictement rien** au comportement : `0xE0E80` est dans le remplissage.

### Autres voies, par ordre de préférence

1. **Outil de checksum EDC15C2 existant** : la famille Bosch EDC15 est couverte par plusieurs
   correcteurs de checksum ; c'est la voie la plus rapide et la plus sûre.
2. **Retrouver le vérificateur** : il faut désassembler la zone du boot (les records `A5A5` de
   l'Étape 107 sont à `0xFC000`, mais leur code est ailleurs) ou identifier si le dump contient
   réellement la bibliothèque.
3. **Contourner la vérification** : si le vérificateur est trouvé, on peut aussi le **neutraliser**
   (c'est la voie « unpatchable fixable » du cahier des charges).
4. ⚠ **Ne pas** flasher les 8 octets en espérant que ça passe : le risque est un ECU en défaut,
   voire un boot bloqué selon où le contrôle est fait.

## 7. État du patch

| élément | état |
|---|---|
| valeurs à modifier (4 mots, 2 banques) | ✅ identifiées et vérifiées |
| copie dupliquée du bloc repérée | ✅ patchée |
| signature `0xD33D` | ✅ **hors sujet** (constante, non dépendante des données) |
| octet de variante `0xE434D` | ✅ **hors sujet** |
| chaînes ASCII `0xEBF1B` | ✅ **hors sujet** |
| checksums de zone `0xEBCFC` / `0xFBCFC` | ❌ **algorithme propriétaire non cassé** |
| binaire `edc_2nde_20kmh.bin` | ⏸ **en attente** — données patchées, checksums non recalculés |
