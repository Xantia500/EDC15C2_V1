# ÉTAPE 68 — `0xFD21` : les 96 octets d'état de défaut, et la chaîne complète défaut → valeur de mesure

> Réponse à « qui écrit `0xFD21` ? » : **un seul service, `sub_CE9B4`, appelé 686 fois.** Et en le
> décodant, la boucle se referme : `0xFD21` est le **sélecteur** qui décide si une mesure répond
> `0x0000` ou `0xFFFF`. Voici la chaîne entière, avec ses preuves.

---

## 1. `0xFD21` = 96 octets d'état, **un par code de défaut `0x00`–`0x5F`**

| évidence | ligne |
|---|---|
| remise à zéro de 96 octets : `mov r0, #0FD21h` … `mov r2, #5Fh ; calls unk_2A9A` | **229851-229852** |
| **écrivain : `sub_CE9B4`** — `movb rl4, [r4+#0FD21h]`, `andb rl4, rl2`, `orb rl4, rh6`, réécriture | **230438, 230466, 230476** |
| `sub_CE43C` reconstruit les états depuis les enregistrements EEPROM (`0xE467`, pas `0x16` = **22 octets**, `byte_E466` = nombre, fin `0xE501`) et remet `0xFD21 + code` à zéro pour les défauts effacés | **229816-229964** |
| copie de travail : `0x0CE00` ← `0xFD21`, 96 octets | **230346-230350** |
| lecture par le service « lire un bloc » : `mov r9, #0FD21h ; add r9, r13` avec `r13 = 16·(code − 0x90)`, 7 codes ⇒ `0xFD21`–`0xFD80` | **206936-206942** |

**`unk_2A9A` est une copie d'octets avant** (`dst = r0`, `src = r1`, `n = r2`) ; le firmware l'utilise en
la faisant **se chevaucher** (`dst = src+1`) pour obtenir un `memset` — d'où le `movb [r0], ONES ;
add r0, #1 ; calls unk_2A9A`. C'est ce qui explique les blocs de `0xFF` du Datensatz.

## 2. `sub_CE9B4` = le **poseur d'état de défaut** (686 appels)

```asm
sub_CE9B4:                          ; r1 = descripteur, rl2 = masque, rh2 = n° de code
    movbz r5, rh2
    shl   r5, #2
    add   r5, #0CAD0h               ; enregistrement de 4 octets par code
    movb  rl0, [r5]
    andb  rl0, rh6                  ; rh6 = ~masque
    ...
    movb  rh0, [r5+#1]
    orb   rh0, rh6
    movb  [r5+#1], rh0
    movbz r4, rh2
    movb  rl4, [r4+#0FD21h]         ; ★ état courant
    andb  rl4, rl2                  ;   & masque
    jnb   r6.0, loc_CEA1C
    orb   rl4, rh6                  ;   pose / lève
```

**Deux mémoires mises à jour en parallèle :**

| adresse | taille | rôle |
|---|---|---|
| `0xFD21 + code` | 96 × 1 octet | **bits d'état courants** (bit 0, bit 1…) |
| `0xCAD0 + 4·code` | jusqu'à 96 × 4 octets | enregistrement `[0]` = état, `[1]` = bits cumulés |

⇒ Mon étape 67 disait « `sub_CE9B4` ne touche pas la zone » : c'était vrai des **handles**, mais
**`sub_CE9B4` alimente précisément le sélecteur `0xFD21`** qui choisit entre `word_1420` et `word_1422`.
La zone est donc reliée aux **défauts**, par ce détour.

## 3. ★ `sub_CE57E` décodé en entier — le pont « défaut → valeur de mesure »

```asm
sub_CE57E:
    cmp  r12, #11h          ; i = 0…17   ⇒ 18 mesures surveillées
    jmpr cc_UGT, locret_CE5DE
    add  r12, r12           ; ★ l'index est DOUBLÉ
    mov  r3, #0E4Eh         ; ★ RAM 0x0E4E : 18 couples d'octets
    add  r3, r12
    movb rl2, [r3+]         ; c1 = 1er code de défaut de la mesure i
    movb rh2, [r3]          ; c2 = 2e code (0xFF = aucun)
    cmpb rl2, #60h          ; borne : code < 96  (⇒ cohérent avec les 96 octets de 0xFD21)
    jmpr cc_NC, locret_CE5DE
    movbz r3, rl2
    movb rl3, [r3+#0FD21h]  ; ★ état du code c1
    andb rl3, #1
    jmpr cc_NZ, loc_CE5B0   ; bit 0 -> word_1422
    ...
loc_CE5B0:
    mov  r3, word_1422      ; = 0xE11A0, 18 mots de 0x0000
    add  r3, r12
    mov  r3, [r3]
    mov  [r13], r3
loc_CE5D4:
    mov  r3, word_1420      ; = 0xE117C, 18 mots de 0xFFFF
```

**Résultat exact :**

| condition | valeur écrite |
|---|---|
| bit 0 de l'état de `c1` **ou** de `c2` posé | **`0x0000`** (`word_1422`, `0xE11A0`) |
| bit 1 de l'état de `c1` **ou** de `c2` posé | **`0xFFFF`** (`word_1420`, `0xE117C`) |

Les deux tables de 18 mots du Datensatz ne sont donc **pas des lois de calibration** : ce sont des
**valeurs de substitution**. La mesure `i` est remplacée par `0x0000` / `0xFFFF` (indicateur « non
disponible / invalide ») dès qu'un de ses deux codes de défaut est actif.

## 4. Le consommateur final : la réponse diagnostique `0x42`

`sub_BE10C` → `sub_942F2` (l. **201240**) → `sub_CE57E`. L'en-tête `0x42` est la réponse positive du
service KWP `readDataByCommonIdentifier`. Dans `sub_BE2BA` (l. **201482-201530**) :

```asm
mov  r4, [r8]              ; word_1424[i]
movbz r5, rl6              ; identifiant demandé
cmp  r4, r5
movb rl5, [r4+#0DC2Ch]     ; octet de la table RAM 0xDC2C (8 entrées)
mov  [r0], r4
cmp  r4, #0FEh             ; -> pointeur word_1422 + 2·code   (0x0000)
cmp  r4, #0FFh             ; -> pointeur word_1420 + 2·code   (0xFFFF)
```

Et `movb rl6, [word_DC06+#1]` : l'identifiant demandé est le **1er octet** du message, aiguillé sur
`0x00 0x02 0x20 0x40 0x60 0x80 0xA0 0xC0 0xE0` (l. 201330-201345) avant d'arriver à la table.

## 5. Bilan de la zone — ce qu'elle est vraiment

| bloc | EA | contenu réel | certitude |
|---|---|---|---|
| `0x141C` | `0xE111E` | 42 octets d'option (switchs + données) | **établi** (étape 66) |
| `0x141E` | `0xE1148` | 52 octets d'option, 39 offsets lus, 5 segments | **établi** (étapes 65-66) |
| **`0x1422`** | `0xE11A0` | **18 × `0x0000` = valeur de substitution « mesure disponible »** | **établi** (ce jour) |
| **`0x1420`** | `0xE117C` | **18 × `0xFFFF` = valeur de substitution « mesure invalide »** | **établi** (ce jour) |
| `0x1424` | `0xE11C4` | 20 identifiants/pointeurs de points de mesure — **1 seule passe** le test `cmp #11h` | partiel |
| `0x1426` | `0xE11EC` | 32 octets : `FE FF`, 18 octets, puis `0F10 0F00 0F66 0B00 0F7F FF00 C300` | non décodé |

## 6. Corrections apportées

- **ERRATA étape 67 § 2f** : « table de mots `EA 0xE4E4E` » → **RAM `0x0E4E`**, et l'index est **doublé** (`add r12, r12`) avant indexation.
- **ERRATA étape 67 § 3** : les « trous » de `0xE11C4` restent vrais pour ce site, mais la table RAM `0x0E4E` est maintenant **décodée** (18 couples de codes).
- **Nuance étape 67 § 2d** : `sub_CE9B4` n'utilise pas les handles de la zone, **mais il écrit le sélecteur `0xFD21`** — le lien existe donc, indirectement.

## 7. Consignation

- **`CATALOGUE_MAITRE.md` § 13 B.14** (2 238 → **2 313 lignes**).
- `ETAPE67` porte désormais un encadré **ERRATA** renvoyant ici.
- Catalogue : les tables `0xE117C` / `0xE11A0` sont reclassées **« valeurs de substitution diagnostic »**, plus « tables de 18 mots ».

## 8. Prochain pas proposé

1. **`word_1424` (`0xE11C4`)** : trancher entre « pointeurs `0x0Fxx` vers la RAM basse » et « deux codages mêlés ». Méthode : chercher qui écrit `0x0F10`, `0x0F61`, `0x1F5A`… dans le listing (`[rN+#0F10h]`).
2. **`0xE11EC` (`0x1426`)** : les 14 derniers octets (`0F10 0F00 0F66 0B00 0F7F FF00 C300`) ressemblent à un **en-tête de table** (`0xC300` = sentinelle connue) ⇒ probablement le début d'une structure non encore rattachée à un handle.
3. **Enregistrement EEPROM de 22 octets** (`0xE467`, pas `0x16`) : cartographier ses champs (`[0]`=code, `[1]`=statut, `[2] [3] [4] [5] [6] [7]` comparés à des seuils aux l. 231290-231330) — c'est la **mémoire de défauts**, donc une pièce maîtresse pour tout ce qui touche FAP/EGR.
