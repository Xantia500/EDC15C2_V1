# ÉTAPE 29 — L'image de l'EEPROM en RAM : structure, checksum, index de champs

Le power latch mène à quelque chose de bien meilleur que le power latch : **j'ai trouvé la structure
qui contient les données sauvegardées**, en RAM, et la façon dont elle est adressée. Et d'abord une
correction d'adressage que je te dois.

---

## 1. Correction — `#0E5CEh` n'est pas une adresse de calibration

J'ai d'abord annoncé `0xE25CE`, puis `0xEE5CE`. **Les deux sont faux.** Voici le raisonnement juste :

- `#0E5CEh` : les deux bits de poids fort valent `11` → la page est **3**, l'offset dans la page vaut
  **`0x25CE`**.
- Au boot : `mov DPP3, #3` (**l. 96443**) → la base de la page 3 est `3 × 0x4000 = 0xC000`.
- Donc l'adresse linéaire = `0xC000 + 0x25CE` = **`0xE5CE`**.

Et `0xE5CE` tombe dans la **RAM interne** (2 Ko à `0xE000-0xE7FF`) : c'est **une structure en RAM**,
pas de la calibration. La preuve directe : le code **écrit** dedans (`mov [r4], word_C5D2`,
l. 151563), ce qui est impossible en flash.

*(Note de méthode : chaque `mov rX, #0E5xxh` de ce programme désigne une adresse RAM, pas une adresse
de Datensatz ; c'est un piège que je viens de désamorcer à mes dépens.)*

## 2. La structure — une image de l'EEPROM, champ par champ

Tout se passe dans **`sub_A0CCC`**. La forme est toujours la même :
`image (0xE5CE) + variable d'offset` → on y écrit une variable vive.

| ligne | offset utilisé | ce qui est écrit | nature devinée |
|---|---|---|---|
| 151472-151475 | `word_C5A` | `word_C70A` | compteur (valeur avec partie basse testée en `& 0FFh`) |
| 151485-151498 | calculé | **copie de 10 octets** depuis `0xC895` (`unk_2128`, r12=dest, r13=`0xC895`, r14=`0x0A`) | **bloc de 10 octets** — code immo / identifiant |
| 151500-151503 | `word_BFA` | **`CC1_T0`** | **horodatage** (valeur du timer de capture) |
| 151504-151509 | `word_D7A` | `word_C838`, `word_C83A`, `word_C83C` (+0, +2, +4) | **6 octets consécutifs** — candidat kilométrage / compteur long |
| 151510-151537 | `word_D6E` … `word_D6E+word_D70` | **somme des mots, puis `neg`**, stockée en `0xE5CC + fin de bloc` | **checksum** |
| 151543-151546 | `word_CF6` | `byte_C30D`, `word_C3A6` | drapeau + valeur |
| 151549-151560 | `word_CF6 + 2 / +4` | `byte_C309`/`byte_C30A`/`byte_C30F` (conditionnels, sinon `0`) | **freeze frame** (valeurs conditionnelles) |
| 151562-151578 | `word_C1E` | `word_C5D2, C5D4, C5D6, C5D8, C5DA` + `byte_C31D` | **bloc de 11 octets** |
| 151582-151585 | `word_C4E` | (second bloc) | second jeu |
| 151658-151663 | `word_BCA` | (lu ensuite par `sub_BD464`) | **bloc de codage** |

### Le checksum, en clair (l. 151510-151537)

```asm
loc_A0EC2:
  mov  r4, word_D6E
  add  r4, word_D6C4            ; position courante dans le bloc
  mov  r5, #0E5CEh
  add  r5, r4
  mov  r4, [r5]
  add  word_D6C6, r4            ; somme des mots
  mov  r4, #2
  add  word_D6C4, r4
loc_A0EDC:
  mov  r4, word_D70
  sub  r4, #2
  cmp  r4, word_D6C4
  jmpr cc_UGT, loc_A0EC2        ; tant qu'on n'a pas atteint la fin
  mov  r4, word_D6C6
  neg  r4                       ; ← somme NÉGATIVE = checksum
  mov  [r2], r4                 ; stockée en fin de bloc
```

⇒ La sauvegarde est un **bloc borné par `word_D6E` (début) et `word_D70` (longueur)**, protégé par
une **somme complémentée à deux**. C'est exactement le schéma que tu décrivais.

## 3. La routine de codage — 15 octets, 12 décodés

```asm
sub_BD464:
  mov  r9, r12                  ; r9 = pointeur du bloc (0xE5CE + word_BCA)
  mov  r12, r9 ; r13 = #0Fh ; r14 = #0
  calls 0Ch, sub_C2DB0          ; contrôle sur 15 octets
  cmp  r4, #0
  jmpr cc_NZ, ...               ; échec → code 0
  mov  r12, r9 ; r13 = r0 ; r14 = r0+0Ch
  calls 0Bh, sub_BD03E          ; décodage vers 12 octets locaux
```

puis la machine d'états (l. 199600-199690) renseigne :

| variable | rôle constaté |
|---|---|
| `byte_C2C0` | valeur 1, 2 ou 4 selon le champ `[r0+#2]` ∈ {1, 2, 8, 0x10} |
| `byte_C2B8` | 0, 1 ou 2 |
| `byte_C2C3` | 0 ou 1 |
| **`byte_C2B7`** | bits posés par `orb` (0x08, 0x01…) |
| `byte_C22C` | bit posé en même temps que certains bits de `C2B7` |

Et `byte_C2B7` est complété plus loin par **une longue série de `orb`** (l. 199629 → 199994), avec un
`movb byte_C2B7, rl5` final. **C'est bien une construction bit à bit à partir du bloc de codage** —
donc **la présence du régulateur, de la clim, etc. est lue dans ce bloc**, comme tu l'affirmes.

## 4. Le point dur — les index de champs ne sont pas dans le dump

Les variables qui portent la position de chaque champ dans l'image :

`word_C5A`, `word_BFA`, `word_D7A`, `word_D6E`, `word_D70`, `word_CF6`, `word_C1E`, `word_C4E`, `word_BCA`

**Sont toutes en lecture seule dans le désassemblage** (aucune écriture : ni `mov`, ni `or`, ni
`bset`). Exemple : `word_D7A` apparaît 7 fois, uniquement en `add r4, word_D7A` à l'intérieur de
`sub_A0CCC`.

⇒ Le **catalogue de la disposition** (quel champ à quel offset) et le **pilote physique** de l'EEPROM
sont dans la **couche absente**. C'est cohérent avec le §3 de l'étape 28 (`word_FD0C` non écrit).

**Mais on peut faire l'inverse** : au lieu de lire les offsets, **décrire les champs par leur contenu**
— et c'est déjà beaucoup :

| champ | taille | contenu observé |
|---|---|---|
| bloc de codage | **15 octets** (12 décodés) | présence régulateur / clim / variante → `byte_C2B7` |
| identifiant | **10 octets** copiés depuis `0xC895` | immo / identifiant véhicule (hypothèse) |
| compteur long | **6 octets** (`C838/C83A/C83C`) | kilométrage (hypothèse) |
| bloc C1E | **11 octets** (5 mots + 1 octet) | à qualifier (FAP ? adaptatifs ?) |
| horodatage | 2 octets | `CC1_T0` |
| checksum | 2 octets | somme négative du bloc |

## 5. Ce que ça confirme de tes autres points

- **Troisième rapport sans limitation** : la courbe `EA 0xE8986` (`word_1B58`) = **15 points, tous à
  `10000`**. Un plafond à 100 % partout = **aucune limitation** : ton ordre validé (1ʳᵉ, 2ᵉ limitées,
  3ᵉ+ libres) est écrit dans le binaire.
- **Le codage 0…10000 = 0…100 %** : `#2710h` apparaît **307 fois**. C'est bien l'échelle interne, comme
  tu l'annonçais pour la commande d'accélérateur.
- **21 courbes** de la calibration ont toutes leurs points à `10000` : ce sont des plafonds « 100 % »,
  pas des valeurs physiques. À ne pas confondre avec des courbes de couple réelles.

## 6. Prochaines actions

1. **`sub_A0CCC` en entier** : énumérer **tous** les `mov [image+offset], variable` → squelette
   complet de l'EEPROM (une ligne par champ).
2. **`sub_C2DB0`** (contrôle des 15 octets) : donnera l'algorithme de vérification du bloc de codage —
   utile si tu veux comprendre comment un codage est validé.
3. **`word_C838/C83A/C83C`** : chercher leur consommateur (un compteur de 6 octets est facile à
   reconnaître : il s'incrémente avec des retenues en cascade).
4. Le **régulateur** : je n'ai pas encore trouvé sa courbe inverse. Piste : elle doit avoir une
   **entrée en 0…10000** et une **sortie en quantité** — donc une courbe dont les *valeurs* sont
   dans 0…10000 et qui n'est **pas** constante. Aucune ne ressort pour l'instant avec un axe
   commençant à 0 et finissant à 10000 : il faut élargir aux axes partiels (ex. 0…9000) et aux
   courbes à valeur de départ non nulle.
