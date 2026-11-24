# ÉTAPE 38 — Structure des blocs (`A5A5` … `94C7` + checksum) et **les deux banques ne sont pas identiques**

---

## 1. ★ Les deux banques de 48 Ko diffèrent de **14 octets** — correction

J'avais écrit (étapes 28-31) que `0xF0000` était « la copie » de `0xE0000`. **C'est faux au sens
strict.** Comparaison exhaustive `0xE0000-0xEBFFF` ↔ `0xF0000-0xFBFFF` : **14 octets diffèrent.**

| offset Datensatz | banque E (`0xE…`) | banque F (`0xF…`) | nature |
|---|---|---|---|
| `0x00FF6` | `3D` | `C3` *(remplissage)* | donnée présente d'un côté seulement |
| `0x00FF7` | `D3` | `C3` *(remplissage)* | idem |
| `0x00FF8` | `3D` | `00` | idem |
| `0x00FF9` | `D3` | `00` | idem |
| `0x00FFC` … `0x00FFF` | `C9 32 05 B2` | `D4 CD C0 17` | **checksum** |
| **`0x0434D`** | **`23`** | **`03`** | **donnée réelle des deux côtés** |
| `0x0BCFC` … `0x0BCFF` | `DD 35 D9 5B` | `20 5C 77 AF` | **checksum** |
| **`0x0BF1B`** | **`57`** | **`46`** | **donnée réelle des deux côtés** |

**Lecture** : ce ne sont pas deux copies d'un même contenu, mais **deux versions voisines du
Datensatz**, différant par **2 octets de données** (`0x434D`, `0xBF1B`), **4 octets présents/absents**
(`0xFF6-0xFF9`) et **8 octets de checksum** — les checksums diffèrent **parce que** les données
diffèrent. La banque E porte `3D D3 3D D3` là où la F n'a que du remplissage.

⇒ **Il y a deux jeux de calibration dans ce calculateur**, dont l'un est très légèrement modifié.
C'est un fait, pas une hypothèse — et il explique pourquoi il faut **toujours préciser de quelle
banque on parle**.

---

## 2. ★ Structure d'un bloc : en-tête `A5A5`, pied `94 C7` + checksum 32 bits

Le rapprochement de plusieurs observations donne un format cohérent.

### 2.1 Le pied de bloc

Fin du premier bloc de 4 Ko, banque E (`EA 0xE0FF0`) :

```
0xFF0: C3 C3 C3 C3 C3 C3 | 3D D3 | 3D D3 | 94 C7 | C9 32 05 B2
                          donnée  donnée  marque   checksum 32 bits
```

Et dans le bloc de boot (`EA 0xFC2FA`) :

```
94 C7 | B1 6B 7B D9 | A5 A5 | 14 E0 00 00 …
marque   valeur 32      en-tête du bloc suivant
```

**⇒ Un bloc se termine par `94 C7` (marque fixe) suivi de 4 octets, et le bloc suivant commence par
`A5 A5`.** Le pied du premier bloc occupe **exactement les 6 derniers octets** des 4 Ko
(`0xFFA-0xFFF`). ✔

### 2.2 Le `94 C7` est bien une **marque**, pas un checksum

`94 C7` (= `0xC794`) apparaît **identique dans les deux banques** à l'offset `0x0FFA`, alors que les
4 octets qui suivent diffèrent. S'il s'agissait d'un checksum des données, il aurait changé.
⇒ **`94 C7` = signature de pied de bloc.** Les 4 octets qui suivent = **checksum 32 bits**.

Occurrences relevées : `EA 0xE0FFA`, `0xF0FFA`, `0xFC2FA`, `0xFC5FA`, `0xFC8FA`, `0xFEBFA`.

---

## 3. L'algorithme du checksum n'est **pas** celui de `sub_A0CCC`

Tests effectués sur le bloc `[0x0000, 0x0FF6[` et `[0x0000, 0x0FF8[` et `[0x0000, 0x0FFA[`,
comparés à la cible `0xC794` **et** aux valeurs 32 bits stockées :

| algorithme | résultat |
|---|---|
| somme de **mots** + `neg` (celui de l'image EEPROM, étape 29) | ✘ aucun des candidats |
| somme d'**octets** + `neg` | ✘ |
| somme de **quartets** `& 0x0F` (zone secondaire) | ✘ |
| CRC-16 CCITT-FALSE / XMODEM / IBM / ARC | ✘ (tableau ci-dessus : 0x01A7, 0x83C4, 0xFE32, 0xF42A…) |

**Conclusion honnête** : le checksum de bloc 32 bits **n'est aucun de ceux que nous avons décodés**.
Il est calculé par la couche absente (comme `94C7`/`A5A5` ne sont testés nulle part dans le code
visible — cf. étape 35 §2). **Je n'invente pas d'algorithme.**

*Note* : les 4 octets pourraient aussi être autre chose qu'un checksum (un pointeur, une date). La
seule chose établie est qu'ils **varient avec le contenu** et occupent la place d'un pied de bloc.

---

## 4. ★ Correction : la « table à `EA 0xFA32C` » est du **Datensatz**

À l'étape 37 j'ai présenté `EA 0xFA32C` comme une table dédiée au service 0x21 du boot. Vérification :

- `EA 0xFA32C` et **`EA 0xEA32C` ont un contenu identique** (`96 40 93 81 80 00 03 96 45 53 28 80 …`) ;
- c'est donc du **Datensatz dupliqué**, à l'offset `0xA32C`, et non une table propre au boot.

**Formulation corrigée** : le service 0x21 (identifiant `0x80`) lit **22 octets de données de
calibration** à partir du pointeur constant stocké en flash (`word_FBF38 = 0x232C`,
`word_FBF3A = 0x3E` → `0x3E × 0x4000 + 0x232C = 0xFA32C`). C'est un accès **en lecture aux données
Datensatz**, pas à un annuaire caché.

Le contenu observé confirme le style de la maison — des **valeurs triplées** :
```
… 2C 00 55 00 | 2C 00 55 00 …        (0x002C, 0x0055 deux fois)
… 0D 00 80 00 | 0D 00 80 00 …        (0x000D, 0x0080 deux fois)
… 04 00 00 00 | 04 00 00 00  …       (4, 4)
… 33 00 61 06 | 33 00 61 06  …       (0x0033, 0x0661 deux fois)
```

---

## 5. L'en-tête `A5A5` : ce qui est lu, ce qui ne l'est pas

Octets de `EA 0xFC000` :

```
A5 A5 | 14 C0 00 00 | 00 C0 00 00 | 40 C0 00 00 | 00 C3 00 00 | 01 E6 00 00 | 08 00 00 00 | 10 00
```

Valeurs 32 bits : `0xC014`, `0xC000`, `0xC040`, `0xC300`, `0xE601`, `8`, `0x10`.
Pour le bloc suivant (`EA 0xFC2FF`) : `0xE014`, `0xE02E`, `0xE040`, `0xE300`.

**Je ne décode pas ces valeurs.** Elles ont la forme d'adresses en RAM (`0xC000-0xC300`) mais je n'ai
aucune preuve, et `0xA5A5` n'étant testé par aucune instruction (étape 35 §2), **aucune lecture du
code ne peut les valider**. Je les laisse ouvertes plutôt que de leur donner un sens plausible.

---

## 6. Les blocs RAM liés aux défauts

| bloc | taille | variables nommées |
|---|---|---|
| `0xCAD0` … `0xCC4F` | 384 octets | `byte_CCA8` (mis à `0xFF` à l'effacement) |
| `0xFD21` … `0xFD80` | 96 octets | `word_FD20`, `byte_FD23`, `word_FD24/FD26/FD28/FD2A/FD2C/FD2E` |

Ces variables nommées ne couvrent que **16 octets sur 96** pour le second bloc → l'essentiel de ces
zones n'est pas indexé par le code visible. **À cartographier**, pas interprété.

---

## 7. Tableau de bord

| question | état |
|---|---|
| banques E / F | **2 versions**, 14 octets d'écart ✔ |
| structure de bloc | `A5A5` en tête, `94C7` + 32 bits en pied ✔ |
| checksum de bloc | **algorithme inconnu** (4 CRC et 3 sommes testés : ✘) |
| en-tête `A5A5` | **non décodé** — je ne spécule pas |
| service 0x21 id 0x80 | lit 22 octets de **Datensatz** ✔ |
| défauts | 7 × 22 octets ✔ ; blocs `0xCAD0`, `0xFD20` à cartographier |
| antidémarrage | non localisé |

---

## 8. Prochaines actions

1. **Cartographier `0xCAD0` (384 o)** et `0xFD20` (96 o) par leurs indexations.
2. **Trancher le sens des 4 octets de pied** : chercher dans le code **visible** si un pied de bloc
   est comparé (adresse `…FFA`/`…FFC`) — sinon, acter qu'il est invérifiable.
3. **Branche d'ajout de `sub_CE43C`** (l. 229880-230000) : comptage d'occurrences, vieillissement.
4. **Antidémarrage** : reprendre `unk_7EC8` (EA `0x07EC8`) par ses **appelants** — c'est la seule
   fonction de clé identifiée.
