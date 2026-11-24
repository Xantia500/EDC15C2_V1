# ÉTAPE 101 — ★★★ **La réponse globale** : la carte d'effacement, les deux blocs, et les deux octets de télécodage qui décident de tout

Cette étape ne cherche plus une fonction : elle explique **pourquoi** on ne trouvait pas, et elle
livre les deux octets qui commandent tout ce qu'on a étudié.

---

## 1. ★★★ La carte d'effacement du dump — ce qui manque, et où

Comptage des `0xC3` par tranches de 8 Ko sur les 512 Ko :

| plage (fo) | plage (EA) | % `0xC3` | verdict |
|---|---|---|---|
| **0x00000-0x07FFF** | **0x80000-0x87FFF** | **100 %** | **BIBLIOTHÈQUE EFFACÉE (32 Ko)** |
| 0x08000-0x11FFF | 0x88000-0x91FFF | 0-18 % | code |
| **0x12000-0x13FFF** | **0x92000-0x93FFF** | **99,9 %** | **effacé (8 Ko)** |
| 0x14000-0x53FFF | 0x94000-0xD3FFF | 0-9 % | code |
| 0x54000-0x5FFFF | 0xD4000-0xDFFFF | 37→100 % | fin de code + **40 Ko effacés** |
| 0x60000-0x6BFFF | 0xE0000-0xEBFFF | 0,5-5 % | **calibration (bloc A)** |
| **0x6C000-0x6FFFF** | **0xEC000-0xEFFFF** | **100 %** | **queue du bloc A effacée** |
| 0x70000-0x7BFFF | 0xF0000-0xFBFFF | 0,5-5 % | calibration (bloc B) = **identique à A** |
| **0x7C000-0x7FFFF** | **0xFC000-0xFFFFF** | **22,8 %** | **queue du bloc B : PRÉSENTE** |

**Conclusion décisive** : les 32 Ko de `0x80000-0x87FFF` — exactement la plage qui contient les
adresses de la bibliothèque (`0x1D36`, `0x1FE8`, `0x20AC`, `0x24BA`, `0x2EE2`, toutes < `0x3000`) —
sont **100 % effacés**. Le corps de `unk_24BA`, `unk_1FE8`, `unk_1D36` **n'existe pas dans ce
fichier**. Ce n'est pas une piste à creuser : c'est une **limite du dump**. Il faudra un dump
complet (ou la version non effacée) pour aller plus loin sur la bibliothèque.

## 2. ★★ Les « 2-3 codeblocks » : la bonne nouvelle

Comparaison octet à octet de `0xE0000-0xEFFFF` et `0xF0000-0xFFFFF` :

- **14 147 octets différents**, mais répartis en **12 plages seulement** ;
- la partie `0xE0000-0xEBFFF` est **identique**, sauf **4 plages minuscules** :

| EA | bloc A | bloc B | interprétation |
|---|---|---|---|
| `0xE0FF6` | `3D D3 3D D3 94 C7 C9 32 05 B2` | `C3 C3 00 00 94 C7 D4 CD C0 17` | empreinte / checksum |
| `0xE434D` | `23` | `03` | octet isolé |
| `0xEBCF2` | `DD 35 D9 5B` | `20 5C 77 AF` | **checksum de bloc (32 bits)** |
| `0xEBF1B` | `57` | `46` | octet isolé |

⇒ **Les deux blocs sont le même Datensatz.** Une modification de valeur doit être faite dans **les
deux** (par sécurité), mais il n'y a **pas** de variante BVA/BVM cachée dans ce fichier : la
différence BVA/BVM est dans l'**EEPROM**, pas ici. Et il y a **deux checksums à recalculer** :
`0xE0FF6`/`0xE0FFA` et `0xEBCF2`.

---

## 3. ★★★ `byte_C2C0` : **BVM confirmée → la Gangberechnung EST active**

Décodeur de codage `sub_BD464` (l.199493), sur l'octet `[codage + 2]` :

```asm
movb  rl4, [r0+#2]           ; ★ octet de codage, index 2
cmpb  rl4, #1  → C2C0 = 1    ; boîte manuelle
cmpb  rl4, #2  → C2C0 = 1    ; boîte manuelle
cmpb  rl4, #8  → C2C0 = 2 ; C2B7 |= 1 ; C22C |= 1   ; boîte auto (trame CAN)
cmpb  rl4, #10h→ C2C0 = 4 ; C2B7 |= 1 ; C22C |= 1   ; boîte auto
sinon          → rl6 = 3 (codage refusé)
```

Et dans ce fichier : **`[word_141C + 2] = [0xE111E + 2] = ` `0x01`** ⇒ **`byte_C2C0 = 1`**.

Or `loc_AFB34` ne prend le chemin Gangberechnung que si **`C2C0 == 1`** :

```asm
movb  rl4, byte_C2C0
cmpb  rl4, #1
jmpr  cc_NZ, loc_AFB5A        ; ≠ 1 → trame boîte
mov   r12, word_C93E          ; ★ ratio V×256/N
calls 0Bh, loc_B0000+2        ; ★★ Gangberechnung
```

### ⇒ Ce que ça implique, définitivement

Sur **ce** véhicule (BVM, `C2C0 = 1`) :

- le **ratio `V×256/N` est calculé** à chaque cycle (`divlu`, l.232301) ;
- la **Gangberechnung classe le rapport** (`0xE81A4`) → `byte_C330` ;
- la **limitation de couple 1re/2nde est active** (`0xE8906`/`0xE8946`, valeurs `0xE8928`/`0xE8968`) ;
- **ta description Bosch était juste de bout en bout.** Mes étapes 96 et 97 étaient fausses.

---

## 4. ★★ `byte_C2BD` : **le régulateur est inhibé par le télécodage**

```asm
; loc_BD7D6 (l.199997), chemin « copie directe » du bloc de codage
mov  r4, word_141C            ; = 0xE111E
movb rl5, [r4+#3]
movb byte_C2BD, rl5           ; ★ C2BD = [0xE111E + 3]
```

**`[0xE111E + 3] = 0x00`** ⇒ `byte_C2BD = 0x00`.

Et dans la tâche `0x340` :

```asm
cmpb rl4, #80h  → loc_B3852   ; actif
cmpb rl4, #1    → loc_B3852   ; actif
cmpb rl4, #0    → loc_B3CEC   ; ★ inhibé
                 loc_B3CF4    ; inhibé
loc_B3CEC:  movb rl4, #2 ; movb byte_D9B2, rl4    ; ★ INHIBITION
            → byte_D9B3 = 0x8E (cause de refus)
```

### ⇒ La réponse à toute la question du régulateur

**Ce n'est pas la vitesse mini (25 km/h), ni le régime, ni le rapport : c'est `byte_C2BD = 0`.**
Le régulateur est **coupé par télécodage** dans ce fichier, et **toutes** les valeurs FGR qu'on a
passées au crible (`2500`, `25000`, `1000`, `4500`, `20000`) sont de la **calibration morte** —
d'où l'absence totale de `40`/`60` km/h, d'hystérésis et de `FGR_GangMin` dedans : le Datensatz n'a
jamais eu à les renseigner pour ce codage.

### Les deux valeurs à changer pour l'activer

| EA | actuel | à mettre | effet |
|---|---|---|---|
| **`0xE111E + 3`** | **`0x00`** | **`0x01`** (ou `0x80`) | `byte_C2BD` ≠ 0 ⇒ branche `loc_B3852`, machine d'états FGR complète |
| `0xE276A` | `20000` | inchangé | `FGR_vMax` = 200 km/h |
| — | — | — | **+ recalculer les 2 checksums** (`0xE0FF6`/`0xE0FFA`, `0xEBCF2`) |

Et l'octet de cohérence : **`[0xE111E + 0x0E] = 0x08`** = `byte_C2B7` ⇒ bit 0 = 0 = **pas de trame
boîte** — cohérent avec `C2C0 = 1` (BVM). Si tu actives le FGR sans toucher à ça, la chaîne reste
cohérente.

⚠ **Réserve honnête** : `sub_BD464` a **deux** chemins — la copie directe depuis le bloc flash
(`[0xE111E+3]`), et un chemin « décodé » (`[r0+#7]`, avec une correspondance `1 → C2BD = 1`,
`2 → C2BD = 0`). Le chemin direct est celui qui s'exécute normalement (`rl6 ≠ 0`). Dans le doute :
**vérifier `byte_C2BD` à la valise** avant de toucher au flash. Mais la valeur *lue* ici est bien
`0x00`.

---

## 5. Ce qu'il reste à faire, dans l'ordre

1. **Dump complet** : les 32 Ko de `0x80000-0x87FFF` sont indispensables pour la bibliothèque
   (`unk_24BA` = le filtre du ratio, `unk_1FE8` = le coordinateur de consigne, `unk_1D36` = la
   courbe). Sans eux, la boucle fermée du régulateur restera partiellement opaque.
2. **EEPROM de codage** : y lire les octets équivalents à `+2` (BVM/BVA) et `+3` (`FGR`). C'est la
   seule source qui dise la vérité du véhicule — le flash ne contient que le défaut.
3. **La queue du bloc B (`0xFC000-0xFFFFF`, 16 Ko présents)** : contenu unique, non-code (0 `rets`),
   avec des motifs de pointeurs RAM (`14 C0 00 00` = `0xC014`, `40 C0 00 00` = `0xC040`) ⇒
   probablement une **table de descripteurs**. À cartographier : elle pourrait contenir les pointeurs
   manquants vers la zone `0xE80xx`.
4. **`FGR_GangMin`** : à chercher **dans l'EEPROM**, pas dans ce Datensatz — puisque `C2BD = 0` rend
   la zone FGR morte, rien n'obligeait Bosch à y écrire un rapport minimum.
