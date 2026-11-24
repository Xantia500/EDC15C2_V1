# ÉTAPE 107 — La navigation `A5 A5` : trois records de 768 octets, le répertoire `BOOT`, et le **record d'identification**

---

## 1. Il n'y a que **trois** `A5 A5` (le quatrième est un faux positif)

Scan complet des 512 Ko :

| EA | suite immédiate | verdict |
|---|---|---|
| **`0xFC000`** | `14 C0 00 00 · 00 C0 00 00 · 40 C0 00 00 · 00 C3 00 00` | record 1 |
| **`0xFC300`** | `14 E0 00 00 · 2E E0 00 00 · 40 E0 00 00 · 00 E3 00 00` | record 2 |
| **`0xFC600`** | `14 E3 00 00 · 1C E3 00 00 · 20 E3 00 00 · 00 E6 00 00` | record 3 |
| `0xFFF58` | `C3 C3 C3 …` | faux positif (aligné sur du padding) |

**Pas = `0x300` = 768 octets exactement.** Ce sont trois structures de même taille dans la queue
`0xFC000-0xFC8FF`.

## 2. La structure d'un record

```
A5 A5 | u32 p1 | u32 p2 | u32 p3 | u32 p4 | u16 id | u16 n | n × u16 valeurs | …code C166…
```

| record | p1 | p2 | p3 | p4 | id | n |
|---|---|---|---|---|---|---|
| 1 `0xFC000` | `0xC014` | `0xC000` | `0xC040` | `0xC300` | `0xE601` | payload effacé (`C3`) |
| 2 `0xFC300` | `0xE014` | `0xE02E` | `0xE040` | `0xE300` | `0x4702` | **12** |
| 3 `0xFC600` | `0xE314` | `0xE31C` | `0xE320` | `0xE600` | `0xD380` | puis `8 · 0 · 16` |

★ **Les quatre pointeurs suivent un schéma constant** :
`…014 / …02E / …040 / …300` (record 2), `…314 / …31C / …320 / …600` (record 3),
`…C014 / …C000 / …C040 / …C300` (record 1). ⇒ **même structure, page différente** : ce sont des
records **indexés par page mémoire** (0xE0, 0xE3, 0xC0).

★ **Les 12 valeurs du record 2** (`0xFC316`) :
`8 9 10 11 12 13 14 15 0x0F80 0x0FA0 0x0FC0 0x1000` — une liste d'indices + quatre descripteurs de
page. Le compteur `n = 12` colle exactement (24 octets).

★ **Chaque record contient du CODE C166** à partir de `+0x40` :
prologue `88 90 88 80 88 70 88 60` = `mov [-r0], r9 / r8 / r7 / r6`, épilogue `DB 00` = `rets`.
Ex. `0xFC340` : `88 90 88 80 88 70 88 60 26 F0 16 00 EC 00 DC 4D A8 4C …`
⇒ **ce ne sont pas des tables : ce sont des blocs « code + données »** (extensions du firmware
stockées dans le Datensatz, pas dans le noyau de code).

## 3. ★ Le répertoire `BOOT` à `0xFFF00`

```
EA FFF00 | AA 55 75 14 89 11 30 AA | 42 4F 4F 54 | 00 00 00 00
                                    B  O  O  T
EA FFF10 | 00 C0 0F 00 | FE FF 0F 00 | 14 CC 0F 00 | 00 FF 0D 00
EA FFF20 | 00 BF 0F 00 | 5A CC 0F 00 | 2A CC 0F 00 | 00 FF 0F 00
```

Les 8 pointeurs, en **u32 LE**, sont :

`0xFC000` · `0xFFFFE` · `0xFCC14` · `0xDFF00` · `0xFBF00` · `0xFCC5A` · `0xFCC2A` · `0xFFF00`

⇒ **c'est bien le répertoire** : il pointe sur le record 1 (`0xFC000`), sur la table d'identification
(`0xFCC14`, `0xFCC2A`, `0xFCC5A`), sur deux records hors queue (`0xDFF00`, `0xFBF00`), et **sur
lui-même** (`0xFFF00`), avec la borne haute `0xFFFFE`.

## 4. ★★★ Le record d'identification — et la confirmation HW/SW

```
EA FCC00 | 30 32 38 31 30 31 30 38 37 37 00 00 00 00 00 00 | 0281010877......
EA FCC10 | 00 00 00 00 02 04 02 0A 00 00 37 35 76 47 0A 00 | ..........75vG..
EA FCC20 | 42 30 37 35 57 46 32 53 30 31 00 00 00 00 41 92 | B075WF2S01....A.
EA FCC30 | 0A 60 00 CC 0F 00 41 94 0A 60 F0 FE 0F 00 48 01 | .`....A..`....H.
EA FCC40 | 02 00 00 00 00 00 48 02 02 00 00 00 00 00 48 8A | ......H.......H.
EA FCC50 | 02 00 00 00 00 00 FF FF FF FF 00 00 00 00 48 8A | ..............H.
```

| contenu | EA | valeur |
|---|---|---|
| **numéro HW** | **`0xFCC00`** | **`"0281010877"`** ★★ |
| libellé interne | `0xFCC1A` | `"75vG"`, `"B075WF2S01"` |
| pointeur pair | `0xFCC30` | `(0x600A9241, 0x000FCC00)` → **vers `"0281010877"`** |
| pointeur pair | `0xFCC38` | `(0x600A9441, 0x000FFEF0)` → **vers `"1037353776"`** |
| **numéro SW** | **`0xFFEF0`** | **`"1037353776"`** ★★★ |
| répertoire boot | `0xFFF08` | `"BOOT"` |

### ⇒ Trois conséquences

1. **Le couple `1037353776` / `0281010877` que tu m'avais donné est bien celui de ce fichier** — et
   c'est donc une calibration **2.0 HDi** (`0281010877`), pas `0281010597` (2.2 HDi).
2. **Le numéro SW n'est pas une donnée isolée** : il est **référencé par un pointeur** depuis la
   table d'identification `0xFCC14`. C'est cette table — et non le Datensatz — que lisent WinOLS /
   ECUSafe pour afficher l'identité du calculateur.
3. **`0xEFEF0` et `0xFCC00` sont hors de la zone de calibration utile** : ils vivent dans la queue
   `0xFC000-0xFFFFF`, qui est **effacée dans le bloc A** (`0xEC000`). ⇒ **seul le bloc B porte
   l'identité du calculateur.**

## 5. Ce que la navigation nous apprend — et ce qu'elle ne donne pas

**Acquis :**
- la queue `0xFC000-0xFFFFF` est un **appendix structuré** : 3 records de 768 o (header + code C166),
  une table d'identification à `0xFCC14`, un répertoire `BOOT` à `0xFFF00` ;
- les records sont **indexés par page mémoire** (`0xC0`, `0xE0`, `0xE3`) ⇒ ils décrivent des **blocs
  RAM**, pas la calibration `0xE0000-0xEFFFF` ;
- **aucune référence** à ces adresses dans `clean.asm` (ni label, ni immédiat) ⇒ la région n'est pas
  désassemblée ; le code qui l'exploite est **ailleurs** (ou dans la bibliothèque effacée).

**Non acquis :** la table qui énumère les **structures du Datensatz** (les courbes/cartes) n'est pas
ici. Elle reste la table de handles `0x61400` (1 305 entrées), qui est bien la seule « navigation »
du Datensatz de calibration. `A5 A5` est la navigation de **l'appendix**, pas celle de la calibration.

⇒ **Conclusion utile** : il n'y a pas de « répertoire caché » à trouver pour la calibration — notre
inventaire par handles est complet et suffisant. La queue `0xFC000` est une couche **différente**
(identité + extensions), et c'est là que WinOLS lit le HW/SW.

## 6. Errata
- **E20** : `A5 A5` n'ouvre pas des sous-blocs de descripteurs de calibration (Étape 106, errata E19
  était trop large) mais **trois records de 768 o indexés par page RAM** dans l'appendix.
- **E21** : `0xEFEF4` → l'offset exact du n° SW est **`0xEFEF0`**.
