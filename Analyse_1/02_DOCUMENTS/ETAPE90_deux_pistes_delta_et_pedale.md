# ÉTAPE 90 — Les deux pistes : le delta part dans la **trame de mesure** · la pédale est publiée en `C6DA`/`C952`

> Les deux pistes ont donné. La première est une **découverte de structure** : il existe une trame de
> mesure relogeable, et `C3A6` y est écrit. La seconde donne le **relais** pédale → cartographie :
> `C6DA` (copie de travail `C952`) porte l'axe `0…10000` dans la calibration.

---

## 1. Piste A — le delta `C3A6` va dans la **trame de mesure**

`sub_A0CCC` (l.151536-151552) :

```c
mov r5, word_CF6
movb [r5+#0E5D0h], rl4      ; slot 0xE5D0 ← byte_C30D
mov r4, #0E5D2h
add r4, word_CF6            ; ← BASE RELOGEABLE
mov [r4], word_C3A6         ; slot 0xE5D2 ← ★ le delta pédale
```

**`word_CF6` est la base d'une trame** : les offsets `0xE5D0`, `0xE5D2`, `0xE5D4`… sont des **emplacements
numérotés**, écrits par `base + offset`. C'est le mécanisme d'export vers la lecture de mesure — et c'est
très probablement celui qui a publié `D518`/`D51A` (identifiant `0x1F4D`) à l'étape 82.

Juste après, `sub_A0CCC` aiguille sur `byte_C309`, `byte_C30A`, `byte_C30F` — plusieurs variantes de trame
selon configuration.

⇒ **le delta pédale n'est donc pas un « mode éco/sport » caché : il est publié tel quel** au diagnostic
(offset `0xE5D2`). Sa valeur est bornée à **−12 / +9** par la calibration (`0xE31FE`).

## 2. Piste B — la pédale est publiée en `C6DA` / `C952`

Le relais est net dans le code :

| ligne | écriture | lecture |
|---|---|---|
| l.191961 | `word_C952 ← word_C6DA` | copie de travail en début de tâche |
| l.194713 | `word_C952 ← word_C6DA` | idem (autre tâche, `#33Ch`) |
| l.195521 | `word_C6DA ← word_C952` | recopie inverse en fin de calcul |
| l.195389 | `word_C952 ← word_DB38` | variante (source `DB38`) |

À côté, le même motif est appliqué au régime : `word_C91C ← word_C42E`. C'est le **schéma « valeur / copie
de travail »** de tout le logiciel.

### Et l'axe `0…10000` existe bien dans la calibration

| EA | tag | n | axe |
|---|---|---|---|
| `0xE8B64` | **C6DA** | 6 | **118 · 2000 · 4000 · 6000 · 8000 · 10000** |
| `0xE8BE8` | **C6DA** | 6 | **118 · 2000 · 4000 · 6000 · 8000 · 10000** |
| `0xEB6CE` | C6A2 | 2 | 0 · 10000 |
| `0xE6D28` | C6B6 | 8 | 0 · 1500 · 3000 · 4500 · 6000 · 7500 · 9000 · 10000 |
| `0xE4D5C`… | C5A8 | 8 | 100 · 2000 · 3000 · 4000 · 5000 · 6000 · 7000 · 11000 |

⇒ **`0…10000` = 0…100 %**, exactement comme tu l'annonçais. Les deux cartes `0xE8B64` et `0xE8BE8` sont
les **cartes « souhait conducteur »** (Driver's Wish) : axe pédale `C6DA`, 6 points, dans la zone `0xE8xxx`.

### `C36C`, lui, n'est pas la pédale publiée

Une seule lecture dans tout le code : `cmp r3, word_C36C` (l.154237), avec `r3 = [handle 0x1878] = **25**`.
C'est une **condition d'activation** (pédale > 25), combinée à régime, `byte_C8F9` et au drapeau de delta
`byte_C216`, qui lève un bit vers `word_FD78.10`.

⇒ `C36C` est la **valeur d'entrée consolidée** (moyenne des deux voies), et `C6DA`/`C952` la **pédale
exploitée** par les cartes. Il y a donc un passage entre les deux que je n'ai pas encore isolé.

## 3. Où en est `C562`

| fait | état |
|---|---|
| n'apparaît pas dans la chaîne d'entrée | ✅ vérifié (étape 89) |
| n'apparaît pas dans la boucle pédale `C36C`/`C6DA` | ✅ vérifié ici |
| source : `C562 ← C3FA` (`sub_CF8C8`) ; `C3FA ← h 0x1470 +6` = **8000** ; secours `0xFF` | ✅ code |
| argument de `unk_1FE8` (10 paramètres) | ✅ étape 88 |
| identifiant `0x0F08` | ✅ dictionnaire |

**Ton aiguillage est le bienvenu sur ce point précis** : `C562` n'a que **trois** écritures, et sa seule
source « vivante » est `C3FA`, lui-même recopié d'un **champ de calibration** (`0xE2260` = 8000) ou remis à
0. Donc soit `C562` est une **demande** recopiée d'une table (et le calcul se fait sur `C3FA` **avant**),
soit il est écrit **par un site que la trace IDA ne voit pas** (écriture indexée `[r4+#…C562]`).

Question précise : **la cartographie qui utilise la pédale et qui touche `C562`, tu la situes côté
`0xE8xxx` (les deux cartes `C6DA`) ou ailleurs ?** Si tu me donnes même une plage d'adresses, je remonte
par le handle au lieu de partir du RAM.

## 4. Consignation

**`CATALOGUE_MAITRE.md` § 13 B.37** — trame de mesure `word_CF6` + slot `0xE5D2` (`C3A6`), relais
`C6DA`/`C952`, axes pédale `0…10000` (`0xE8B64`, `0xE8BE8`, `0xEB6CE`, `0xE6D28`, `0xE4D5C`), seuil 25 de
`C36C`, état de `C562`.
