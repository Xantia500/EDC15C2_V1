# ÉTAPE 69 — La mémoire de défauts : 7 enregistrements de 22 octets, 96 descripteurs, et le bloc EEPROM de 176 octets

> Tu voulais le cœur du sujet : **où sont les défauts, quelle est leur structure, et où sont les seuils**.
> Les trois réponses tiennent en une page. Et au passage : **le premier bloc EEPROM précisément localisé.**

---

## 1. Géographie complète

| adresse | taille | rôle | preuve |
|---|---|---|---|
| **`0xE467` – `0xE500`** | **`0x9A` = **154** o = **7 × 22** | enregistrements de défauts | `mov r2, #9Ah` l. **229619** ; `mov r1, #16h ; mulu` l. **229640-229644** |
| `byte_E466` | 1 o | **nombre d'enregistrements courants** (0…7) | l. 229606, 229661, 229896 |
| `byte_E501` | 1 o | **index du dernier enregistrement** (pointeur d'insertion) | l. 229585, 229918, 229938 |
| `byte_E502`, `0xE503 + i` | 1 o | octets annexes du service diagnostic | l. 231679, 231711, 231717 |
| `0xCAD0 + 4·code` | 96 × 4 o | état par code | étape 68 |
| **`0xCCB2 + 2·code`** | **96 × 2 o** | **pointeurs vers les descripteurs** | `mov r1, #0CCB2h` + boucle de `0xC0` = 192 o, l. **231163-231172** |
| `0xCE00` | 96 o | instantané de `0xFD21` | l. 230346 |

**7 × 22 = 154** exactement, et la borne du listing est `0xE467 + 0x9A = 0xE501` : les trois nombres concordent.
C'est cette concordance qui donne la certitude, pas la plage de valeurs.

## 2. Champs de l'enregistrement de 22 octets

| offset | rôle | preuve |
|---|---|---|
| `+0` | **code du défaut** | `movb rh2, [r3]` l. 229620 ; `cmpb rl2, rl6` l. 229668 |
| `+1` | **octet d'état** — bit 0 = actif, bit 6, bit 2 | `jnb r0.0` l. 229940 ; `jb r0.6` l. 231296 |
| `+2` | **compteur de conditions** = nombre de bits à 1 | `jnb r0.0 / add r4,#1 / shr r0,#1` l. 229947-229958 |
| `+3` | doit être **non nul** (validité) | l. 229695, 229699 |
| `+4` | **compteur de guérison**, comparé à `[descr+#1Dh]` | l. 231251-231257 |
| `+5` | comparé à `[descr+#1Eh]` (0 → 1) | l. 231258-231266 |
| `+6` | comparé à `[descr+#1Ch]` **et** à `word_142A+9` | l. 231273-231282 |
| `+7` | seuil `1` / `>1`, aiguillé par le bit 3 | l. 231285-231292 |
| `+8` … `+21` | non exploités à ce stade (14 octets) | — |

★ **Conséquence directe : les seuils de maintien d'un défaut ne sont pas dans le code, ils sont dans le Datensatz.**
`[0xCCB2 + 2·code]` pointe un bloc dont les champs `+0x1C`, `+0x1D`, `+0x1E` sont comparés aux octets de
l'enregistrement. Un défaut se maintient ou s'efface selon **combien de cycles** il dépasse son seuil — et
ce nombre de cycles est **calibrable**.

## 3. `sub_CE256` — le service de la mémoire de défauts

La **commande est dans `rh6`** :

| commande | effet | preuve |
|---|---|---|
| `0xFF` | rend le **dernier** enregistrement (`byte_E501`) + son pointeur de descripteur | l. 229583-229599 |
| `0x80`–`0x9F` (masque `0xE0` = `0x80`) | **dump complet : les 154 octets** depuis `0xE467` | l. 229603-229621 |
| `0xCF` | **compte** les défauts (bits de `+2` si `+1`.0, `+4`=0, `+6`≠0) | l. 229624-229650 |
| `0x00`–`0x1F` | **lit l'enregistrement n° `rl6`** (offset `22 × rl6`) + descripteur | l. 229631-229652 |
| `0x20`–`0x7F`, `0xA0`+, `0xE0`+ | **recherche par code** (`0xEF`/`0xDF` = variantes), bits `r6.12…15` | l. 229663-229740 |

## 4. ★ Deux tables de 96 entrées, une par code, dans la page `0x33`

| EA | taille | contenu relevé | rôle |
|---|---|---|---|
| **`0xCF5EC`** | 96 × 2 o | `1CF4 1492 1C64 1E0A 15B4 15B6 153E 183E …` — **toutes les valeurs tombent dans la plage des handles `0x1400`–`0x1E30`** | **un bloc de descripteur par code** ; recopié au démarrage vers `0xCCB2` (`mov r0, #0B5ECh` + `extp #33h`, `add r2, #0C0h`, l. 231163-231172) |
| **`0xCF6AC`** | 96 × 1 o | `0D 80 FC 00 CC CC F8 7F 00 FC C8 78 1F F8 FC F8 F8 C4 FE …` | **masque par code**, OR-é dans `0xCAD0 + 4·code` à l'init (boucle `r12 = 0xB6AC`, `r13 = 0xCAD1`, `r14 = 0x60`, l. **231221-231232**) |

Le fait que les 96 pointeurs de `0xCF5EC` tombent **tous** dans la plage des handles est le recoupement qui
prouve leur nature : ce ne sont pas des adresses quelconques, ce sont des **numéros de bloc du Datensatz**.

## 5. ★★ Le bloc EEPROM de la mémoire de défauts — **offset `0x2467`, 176 octets**

```asm
loc_CF030:
  r1 = word_C45A ; r0 = word_C46A ; extp r0, #1 ; rl0 = [r1]
  r0 = 22 × rl0 ; MDH = 0xE467 + r0        ; ★ enregistrement pointé par l'EEPROM
  ...
  r0 = word_C46A ; shr r0, #2 ; jmpr cc_NZ, loc_CF072
  mov r0, #0E467h ; mov r2, #0B0h ; calls unk_2A9A   ; ★ EEPROM vierge -> 176 o remis à zéro
loc_CF072:
  mov r1, #2467h      ; ★ offset EEPROM
  mov r0, #0B0h       ; ★ 176 octets = 8 × 22
  mov r2, #3
  mov r3, r1
  calls 9, sub_9FFE2  ; ★ lecture / écriture EEPROM
```

**`0xB0` = 176 = 8 × 22.** L'image EEPROM réserve **8 enregistrements**, la RAM n'en gère que **7** en marche.
Le test `shr r0, #2` sur `word_C46A` (valeur de page) décide : EEPROM vierge → **176 octets remis à zéro**
au lieu d'être lus.

## 6. Correction d'une affirmation de l'étape 68

J'y avais écrit « `sub_CE43C` reconstruit les états **depuis l'EEPROM** ». C'est imprécis : il les reconstruit
depuis les **enregistrements RAM `0xE467`**, eux-mêmes chargés de l'EEPROM par `sub_9FFE2` (§ 5). La chaîne
complète est donc :

**EEPROM (offset `0x2467`, 176 o) → `sub_9FFE2` → RAM `0xE467` (7 × 22) → `sub_CE43C` → `0xFD21 + code` (96 o) → `sub_CE57E` → `0x0000`/`0xFFFF` dans la réponse diagnostic.**

## 7. Consignation

- **`CATALOGUE_MAITRE.md` § 13 B.15** (2 313 → **2 383 lignes**).
- La ligne « EEPROM » du § B.14 est corrigée.

## 8. Ce qui manque encore, et qui est maintenant très ciblé

1. **Les 14 octets `+8`…`+21`** de l'enregistrement : probablement la **freeze-frame** (valeurs des grandeurs au moment du défaut). Méthode : chercher les écritures à `[r3+#8]`… dans `sub_CE256` et les routines de capture.
2. **Les champs `+0x1C`/`+0x1D`/`+0x1E` des 96 descripteurs** : ce sont les **seuils calibrables** de maintien/guérison. Il faut dumper les 96 blocs (handles de `0xCF5EC` → `0x61400`) et lire ces trois octets de chacun. **C'est la partie directement exploitable pour toi.**
3. **Le masque `0xCF6AC`** : comprendre quels bits il force dans le statut au démarrage.
