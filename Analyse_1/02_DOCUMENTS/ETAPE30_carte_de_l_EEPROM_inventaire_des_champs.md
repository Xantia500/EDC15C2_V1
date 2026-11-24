# ÉTAPE 30 — Carte de l'EEPROM : inventaire complet des champs, avec colonne d'offset 0…1024

`sub_A0CCC` est maintenant lu **en entier** (l. 151122 → 151640). Voici l'inventaire exhaustif, la
colonne d'offset que tu demandes, et — je le dis d'emblée — **la raison précise pour laquelle cette
colonne ne peut pas encore être remplie de nombres**, avec le moyen de la remplir.

---

## 1. Tableau A — tous les champs de l'image (`0xE5CE` en RAM interne)

| ligne(s) | groupe d'offset | position dans l'image | champ écrit | source (variable vive) |
|---|---|---|---|---|
| 151472-151475 | `word_C5A` | +0 | 1 mot | `word_C70A` |
| 151485-151498 | (calculé) | +0 | **10 octets** | copie depuis `0xC895` (`unk_2128`, longueur `0x0A`) |
| 151500-151503 | `word_BFA` | +0 | 1 mot | **`CC1_T0`** (horodatage timer) |
| 151504-151509 | `word_D7A` | +0 / +2 / +4 | **3 mots = 6 octets** | `word_C838`, `word_C83A`, `word_C83C` |
| 151510-151537 | `word_D6E`, `word_D70` | bloc entier | **checksum** en `image[D6E+D70−2]` | somme négative des mots du bloc |
| 151543 | `word_CF6` | +2 | 1 octet | `byte_C30D` |
| 151546 | `word_CF6` | +4 | 1 mot | `word_C3A6` |
| 151549-151560 | `word_CF6` | +6 | 1 octet | `byte_C309` → `0`, sinon `byte_C30A`, sinon `byte_C30F` |
| 151562-151578 | `word_C1E` | +0 / +2 / +4 / +6 / +8 / +A | 5 mots + 1 octet | `C5D2, C5D4, C5D6, C5D8, C5DA`, `byte_C31D` |
| 151582-151585 | `word_C4E` | +0 … | bloc | (second jeu, suite en l. 151586) |
| 151586-151589 | `word_?` | +0 | 1 mot | `word_C5E8` |
| 151590-151599 | `word_D26` | +0 / +2 / +4 | 3 mots | `C5BE`, `C5C0`, `C58C` |
| 151600-151615 | `word_D1A` | +0 / +2 / +4 / +6 / +8 | 5 mots | `C5EE`, `C5F2`, `C5EA`, `C5F6`, `C5E6` |
| 151616-151635 | `word_D4A` | +0 / +2 / **+6** / +8 / +A | 5 mots (**+4 absent = trou**) | `C5EC`, `C5E4`, `C5F4`, `C5B8`, `C5F0` |
| 151636-151645 | `word_CD2` | +0 | 1 mot | **`word_C77A`** |
| 151646-151649 | `word_CDE` | +0 | 1 mot | **`word_C3DA`** |
| 151658-151663 | `word_BCA` | +0 | **bloc de codage (15 octets)** | lu ensuite par `sub_BD464` |

Deux observations de structure :

- les groupes occupent **jusqu'à 12 octets** (`+0 … +A`) → **enregistrements de 12 octets** ;
- `word_D4A` saute `+4` : le trou est **volontaire**, il correspond à un champ absent pour cette
  variante — signature d'une disposition **calibrée**, pas d'une structure C figée.

## 2. Tableau B — la colonne « offset EEPROM 0…1024 »

Voici pourquoi elle est vide de nombres : **l'offset n'est pas une constante, c'est une variable
d'exécution.** Chaque champ est écrit à `0xE5CE + <variable>`, et ces variables sont **remplies par
la couche absente** (aucune écriture dans le dump — vérifié pour chacune).

| groupe | variable d'offset | **adresse RAM à lire** | offset EEPROM (0…1024) |
|---|---|---|---|
| C5A | `word_C5A` | **`0x0C5A`** | = valeur lue |
| BFA | `word_BFA` | **`0x0BFA`** | = valeur lue |
| D7A | `word_D7A` | **`0x0D7A`** | = valeur lue |
| D26 | `word_D26` | **`0x0D26`** | = valeur lue |
| D1A | `word_D1A` | **`0x0D1A`** | = valeur lue |
| D4A | `word_D4A` | **`0x0D4A`** | = valeur lue |
| C1E | `word_C1E` | **`0x0C1E`** | = valeur lue |
| C4E | `word_C4E` | **`0x0C4E`** | = valeur lue |
| CD2 | `word_CD2` | **`0x0CD2`** | = valeur lue |
| CDE | `word_CDE` | **`0x0CDE`** | = valeur lue |
| CF6 | `word_CF6` | **`0x0CF6`** | = valeur lue |
| bloc checksumé | `word_D6E` (début) | **`0x0D6E`** | = valeur lue |
| longueur du bloc | `word_D70` | **`0x0D70`** | (longueur, pas un offset) |
| codage | `word_BCA` | **`0x0BCA`** | = valeur lue |
| zone à checksum quadruplet | `word_BBE` / `word_BC0` | **`0x0BBE` / `0x0BC0`** | = valeurs lues |

**Ce sont des adresses RAM, donc lisibles sur un calculateur vivant** (émulateur ou lecture mémoire en
ligne). Onze mots suffisent à remplir définitivement la colonne 0…1024.

### Ce que l'on peut déjà dire sans les lire

L'image est en **RAM interne**, qui s'arrête à `0xE7FF`. Donc :

```
offset max = 0xE7FF − 0xE5CE = 0x231 = 561
```

⇒ **Aucun offset ne dépasse 561.** L'image ne recouvre donc **au plus que les 562 premiers octets**
de ton EEPROM de 1 Ko : **le miroir est partiel**, et la seconde moitié est gérée directement par la
couche absente. C'est une contrainte forte, et elle explique pourquoi le code présent ne « voit » pas
tout l'espace.

## 3. Deux checksums différents, à deux niveaux

| niveau | routine | algorithme | preuve |
|---|---|---|---|
| **bloc principal** | `sub_A0CCC`, l. 151510-151537 | somme des **mots** du bloc `[word_D6E … word_D6E+word_D70−2]`, puis **`neg`**, écrit en fin de bloc | lignes citées |
| **zone secondaire** | `sub_A0B72`, l. 151196-151222 | somme des **quartets** des `word_BC0` octets à `image+word_BBE`, résultat `& 0x0F` | `addb rl6,rl4` / `shr r4,#4` / `and r4,#0Fh` |

Deux algorithmes distincts pour deux zones distinctes : la zone à quartets est probablement le
**codage / la zone critique** (petit volume, contrôle rapide), le bloc principal les **données
d'adaptation** (volume plus grand).

`sub_A0B72` construit aussi un **mot d'état** : `word_BC4 & 0xC000` + `word_BC0`, avec le bit `0x80`
testé sur l'octet `image[word_BBE]` et `0x4000` posé si le checksum quadruplet est non nul,
`0x800` si le bit `0x80` est absent.

## 4. Une table de descripteurs de 12 octets en RAM (`0x0BA6`)

`sub_A0BE0` (l. 151268-151290) calcule l'index `byte_CFA0 × 12` :

```asm
movbz r4, byte_CFA0
mov   r5, r4
shl   r5, #2
sub   r5, r4
shl   r5, #2            ; r5 = index × 12
mov   r9, [r5+#0BA6h]   ; ← premier mot du descripteur = OFFSET
add   r9, word_CF9E     ; + base de groupe
mov   r12, r9
movb  rl4, [r9+#0E5CEh] ; accès à l'image
```

⇒ Il existe une **table de descripteurs de 12 octets à `0x0BA6`**, dont le premier mot est un offset
dans l'image et où `word_CF9E` sert de base de groupe. C'est la « carte » que tu cherchais — elle est
en RAM, pas en flash, et elle est alimentée par la couche absente.

## 5. Ce que contiennent les champs — hypothèses classées

| champ | indice | confiance |
|---|---|---|
| **bloc de 15 octets** `word_BCA` | décodé par `sub_BD464` → bits de `byte_C2B7` (régulateur, clim, variante) | **élevée** |
| **10 octets** copiés depuis `0xC895` | taille typique d'un identifiant immo | moyenne |
| **6 octets** `C838/C83A/C83C` | compteur long (kilométrage) | moyenne |
| **`word_C77A` et `word_C3DA`** sauvegardés | **et** ce sont des **axes de cartes** (axes `6667…28333`) → **valeurs apprises** réinjectées dans l'interpolation | **notable** |
| `CC1_T0` | horodatage d'écriture | moyenne |
| `byte_C30D`, `C309/C30A/C30F` | drapeaux conditionnels → contexte figé (freeze frame) | moyenne |

Le point `word_C77A` / `word_C3DA` est le plus intéressant : **des valeurs apprises sont sauvegardées
en EEPROM puis utilisées comme axes de cartes**. C'est un mécanisme d'auto-adaptation persistant —
à creuser, car il touche directement la compréhension du Datensatz.

## 6. Croisement avec ta liste

| élément de ta liste | statut dans cette étape |
|---|---|
| kilométrage | **candidat identifié** : champ de 6 octets (`word_D7A`) — à confirmer par son incrément |
| erreurs DTC / P codes | pas encore trouvé dans l'image ; la table des codes doit être en calibration |
| freeze frames | **candidat** : champs conditionnels `C309/C30A/C30F` |
| immo / déverrouillage | **candidat** : bloc de 10 octets copié depuis `0xC895` |
| codage (régulateur, clim) | **acquis** : bloc de 15 octets décodé par `sub_BD464` |
| suie / cérine FAP | pas encore identifié — à chercher parmi les groupes `C1E`, `C4E`, `D1A`, `D26`, `D4A` |

## 7. Prochaines actions (dans l'ordre)

1. **`word_C838/C83A/C83C`** : trouver l'incrément → confirmer ou écarter le kilométrage.
2. **`sub_C2DB0`** (contrôle des 15 octets du codage) : algorithme de validation.
3. **`sub_A0BE0` en entier** : comportement de la table `0x0BA6` (lecture seule ? écriture ?).
4. **Groupes `C1E`, `C4E`, `D1A`, `D26`, `D4A`** : suivre les variables sources (`word_C5xx`) jusqu'à
   leurs producteurs — c'est là que se cachent suie/cérine s'ils existent.
