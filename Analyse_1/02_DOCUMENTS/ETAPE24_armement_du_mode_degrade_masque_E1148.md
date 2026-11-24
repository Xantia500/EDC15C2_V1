# ÉTAPE 24 — Ce qui arme le mode dégradé : quatre mots de défauts et un masque de calibration

L'étape 23 avait laissé une question : qui met `byte_C33C` à 1 ? Réponse : un **assemblage de
défauts** construit dans une routine unique (l. 182399-182518), puis **filtré par un masque
de calibration**. C'est ce dernier point qui est le plus utile pour toi.

## 1. Quatre octets = quatre groupes de bits de défaut

Chaque octet n'est pas un drapeau binaire mais un **champ de bits**, rempli par `orb` successifs.

### `byte_D98E` (l. 182418-182447)

| bit | condition | ligne |
|---|---|---|
| *résultat* | `calls 0Ah, sub_AF4E0` → `orb byte_D98E, rl4` | 182418-182419 |
| `0x02` | `byte_C32B & 2 == 2` | 182420-182426 |
| `0x01` | `word_FD24.0` levé | 182428-182431 |
| `0x20` | `word_FD3E.13` levé | 182433-182436 |
| `0x40` | `word_FD6A+1 ≠ 0` | 182438-182442 |
| `0x10` | `word_FD3E ≠ 0` | 182444-182448 |

### `byte_D98F` (l. 182450-182451) — `sub_AF3FE` seulement
### `byte_D990` (l. 182452-182461)
| bit | condition | ligne |
|---|---|---|
| `0x02` | `word_FD42.4` levé | 182454-182457 |
| `0x04` | `word_FD42.13` levé | 182459-182462 |

### `byte_D991` (l. 182464-182492)
| bit | condition | ligne |
|---|---|---|
| `0x80` | `word_FD20.15` levé | 182466-182473 |
| `0x04` | `byte_C2F0 ≠ 0` | 182471-182477 |
| `0x08` | `word_FD50 ≠ 0` | 182479-182482 |
| `0x20` | `word_FD52 ≠ 0` | 182484-182487 |
| `0x40` | `word_FD28+1 ≠ 0` | 182489-182493 |

Les quatre `sub_AF4xx` (segment `0x0A`) renvoient chacun un octet de bits
supplémentaires ; leur contenu n'est pas analysé ici.

## 2. Le masque de calibration — `EA 0xE1148`

```asm
loc_B2C3C:
  mov   r4, word_141E        ; l.182495  ← handle
  movb  rl5, [r4+#15h]
  andb  byte_D98E, rl5       ; l.182497
  movb  rl5, [r4+#16h]
  andb  byte_D98F, rl5       ; l.182499
  movb  rl5, [r4+#17h]
  andb  byte_D990, rl5       ; l.182501
  movb  rl5, [r4+#18h]
  andb  byte_D991, rl5       ; l.182503
```

`word_141E` → offset `0x1148` → **`EA 0xE1148`**. Les quatre octets lus :

| offset | EA | valeur |
|---|---|---|
| `+0x15` | `0xE115D` | **`0x84`** |
| `+0x16` | `0xE115E` | **`0xBE`** |
| `+0x17` | `0xE115F` | **`0xCA`** |
| `+0x18` | `0xE1160` | **`0x64`** |

*(vérifié octet par octet dans `edc.bin` : `… 00 05 00 05 04 84 BE CA 64 00 01 …`)*

## 3. Ce que ce masque fait concrètement

| octet | masque | bits conservés | conséquences |
|---|---|---|---|
| `D98E` | `0x84` | **7, 2** | sur six conditions possibles, **seules deux** restent actives : `sub_AF4E0` (bit 7) et `byte_C32B & 2` (bit 2) |
| `D98F` | `0xBE` | 7,5,4,3,2,1 | seuls les bits 6 et 0 sont inhibés |
| `D990` | `0xCA` | 7,6,3,1 | **`word_FD42.13` (bit 2) est inhibé**, `word_FD42.4` (bit 1) reste actif |
| `D991` | `0x64` | 6,5,2 | **`word_FD20.15` (bit 7) et `word_FD50` (bit 3) sont inhibés** ; `C2F0`, `FD52`, `FD28+1` restent actifs |

⇒ Le mode dégradé n'est **pas** armé par n'importe quel défaut : la calibration décide quels bits
ont le droit d'y mener. Trois conditions au moins sont **neutralisées d'usine** sur ce Datensatz.

## 4. Publication et déclenchement

```asm
movbz r5, byte_D98F ; shl r5,#8 ; or r5, byte_D98E ; mov word_D3CE, r5   ; l.182504-182508
movbz r2, byte_D991 ; shl r2,#8 ; or r2, byte_D990 ; mov word_D3D0, r2   ; l.182509-182513
movb  rl4, byte_D98E ; orb rl4, byte_D98F ; orb rl4, byte_D990 ; orb rl4, byte_D991
movb  byte_C33C, rl4                                                      ; l.182514-182518
```

`word_D3CE` et `word_D3D0` = les deux mots de diagnostic publiés ; `byte_C33C` = **OU des quatre**,
donc « au moins un défaut non masqué ». Et l'effet (l. 181028-181036) reste celui de l'étape 23 :
bit 10 de `word_D90C` et `word_D90E`, `byte_C232 = 0`, `bclr r9.0`, `bset word_FD16.14`.

## 5. Lu / inféré

| affirmation | statut |
|---|---|
| masque `84 BE CA 64` @ `EA 0xE1148` (+0x15…+0x18) | **lu** (handle + octets) |
| construction bit à bit des quatre octets | **lu** (lignes citées) |
| `byte_C33C` = OU des quatre octets masqués | **lu** |
| bits neutralisés par ce Datensatz | **lu** (simple ET binaire) |
| signification de chaque bit (quel défaut) | **inconnu** — aucun libellé dans le binaire |
| les `sub_AF4xx` produisent des bits de défaut | **inféré** (même usage que les autres bits) |
| `word_D90C/D90E` bit 10 = mode dégradé | **inféré** (repris de l'étape 23) |

## 6. Suite

Le maillon manquant du mode dégradé est maintenant **la signification des bits** — et elle est
hors de portée du binaire seul (il faudrait la documentation Bosch des « Fehlerpfade »).
En revanche, **le masque est un point d'action concret** : c'est lui qui décide si le repli à
38 mm³ s'arme.
