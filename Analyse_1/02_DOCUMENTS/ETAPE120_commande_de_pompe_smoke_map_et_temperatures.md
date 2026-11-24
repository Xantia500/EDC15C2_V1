# ÉTAPE 120 — Recadrage : la commande de pompe, la smoke map et les limitations par température

Tu as raison sur les deux points. Je corrige et je réponds.

---

## 1. ★★★ ERRATA E30 — `0xE8A06` n'est PAS dans la cascade d'IQ

**Preuve, l.182807-182815 :**

```asm
loc_B2EEA:
                mov     r4, word_D9AA
                mov     word_D3D4, r4      ; D3D4 := la DEMANDE d'IQ (D9AA)
                mov     r12, word_1B5E     ; pointeur -> EA 0xE8A06
                mov     r13, word_C91C     ; X = RÉGIME
                mov     r14, word_D9AA     ; Y = IQ
                calls   0, unk_1D50        ; interpolation 2-D
                movb    byte_C8F8, rl4     ; ★ sortie = UN OCTET
```

Axes lus dans la donnée : **tag1 `0xC42E`** (régime, 10 pts, 0…5002) et **tag2 `0xD3D4`**
(10 pts, **0…8000 = 0…80 mm³**).

⇒ **`0xE8A06 = f(RPM, IQ) → byte_C8F8`, une valeur 0…250 sur un OCTET.** C'est bien la **commande de
pompe haute pression**, calculée **à côté** de la chaîne de quantité, pas dedans.

**Ce que je retire** : dans l'Étape 113 j'avais placé `C8F8 = courbe(0xE8A06, …)` **dans** la cascade
d'IQ. Faux : `C8F8` est un octet de commande de pompe. La cascade de quantité, elle, continue
séparément à l.182816 avec `D9A6` vs `C688` / `C682` / `C6C0`.

**ERRATA E31** : `D3D4` n'est qu'une **copie de `D9AA`** (l.182808-182809) — l'axe IQ de cette carte
est donc bien la demande de quantité.

---

## 2. ★★★ OÙ EST LA SMOKE MAP : `0xE8444`

**Le code, l.181905-181930 :**

```asm
loc_B26F2:
                mov     r12, word_1B46     ; variante "froide" -> 0xE87D6
                mov     r13, word_C42E     ; X = RÉGIME
                mov     r14, word_C3EC
                calls   0, unk_1D50
                mov     word_D986, r4
...
loc_B2706:
                mov     r4, word_D986
                mov     word_C690, r4      ; ★ sortie
```

et pour la variante principale (l.181913) : `r12 = word_1B40`, `r13 = word_C42E` (régime),
`r14 = word_C3E6` → `C690`.

**La preuve du handle** : `word_1B40 → EA 0xE8444` (table `0x61400`), et la carte à cette adresse a
exactement les axes attendus :

| | |
|---|---|
| **adresse** | **`0xE8444`** |
| axe 1 | `0xC42E` — **régime**, 16 points, **0 … 5200 tr/min** |
| axe 2 | **`0xC3E6`** — **masse d'air**, 16 points, **3000 … 11500** (0,1 mg/coup ⇒ 300…1150 mg) |
| sortie | **1500 … 7600** (0,01 mm³ ⇒ 15 … 76 mm³) |
| grille | **16 × 16** |

⇒ **c'est la carte de limitation de fumée : IQ max = f(régime, masse d'air).**

**Et la preuve qu'elle limite bien la quantité** — `C690` est un **plafond appliqué à `C698`** :

```asm
loc_B4D1A:                          ; l.185814
                mov     r4, word_C698
                cmp     r4, word_C690
                jmpa    cc_SLE, loc_B53E4      ; si C698 <= C690 : on garde
                mov     r5, word_C690
                mov     word_C698, r5          ; sinon C698 := C690
```

`C698` = la valeur issue du pédale/régulateur (connue : « `C680 = C698` »). **La fumée plafonne donc
la demande**, exactement l'architecture Bosch attendue.

**Origine de l'axe air** : `C3E6` vient du bloc `word_15F0 → 0xE3AD0`, champ `[+4]` (l.131319-131320).
Il est aussi utilisé en `0xE8872` (6×6) et `0xE8444`.

**Variante froide** : `word_1B46 → 0xE87D6` = `f(régime 200…620, C3EC 700…850)` — un correcteur de
démarrage à froid (régime très bas + température).

---

## 3. ★★★ OÙ SONT LES LIMITATIONS PAR TEMPÉRATURE

Le dictionnaire déjà construit nomme les axes :

| variable | nom établi |
|---|---|
| `C3D2` | **T° liquide de refroidissement** (identifiant `0F00`) |
| `C3B0` | **T° carburant** (identifiant `0F02`) |

Et les échelles le confirment : les axes de ces cartes vont de **2431 à 3831** ⇒ **Kelvin × 10** =
−30 °C … +110 °C.

**Famille « température moteur » (`C3D2`)** :

| carte | axes | sortie | lecture |
|---|---|---|---|
| **`0xE80A0`** | régime **100-1000** × `C3D2` **2481-3731** | 1300 … 12500 | **démarrage / très froid** |
| **`0xE3908`** | régime 1000-2500 × `C3D2` 2531-3131 | 0 … 4200 | froid (-20…+40 °C) |
| **`0xE86F4`** | régime 0-1760 × `C3D2` 2431-3531 | 0 … 9230 | ralenti selon T° |
| **`0xE868C`** | `C3D2` 2431-3831 × `C562` (vitesse 0…18000) | 0 … 9230 | **T° × vitesse** |
| **`0xE880A`** | régime 1300-4000 × `C3D2` **3841-3951** | 0 … 7040 | **surchauffe 111…122 °C → protection** |
| `0xE68F4` | `C3C2` × `C3D2` | 0 … 1500 | correcteur fin |
| `0xEBB46` | `D5B0` 100-500 × `C3D2` 2431-3731 | | |
| `0xE39D8` | `D094` 2731-4051 × `D092` 700-2002 | 650 … 2280 | |

**Famille « température carburant » (`C3B0`)** :

| carte | axes | sortie | lecture |
|---|---|---|---|
| **`0xE8000`** | régime 800-4800 × `C3B0` **3051-3751** (32…102 °C) | 1500 … 7600 | **limitation par T° gasoil** |
| **`0xE7F7E`** | régime 800-4800 × `C3B0` **3601-3751** (87…102 °C) | 1500 … 7630 | **gasoil chaud → réduction** |
| `0xE7F7E`/`0xE8000` | grilles 8×4 et 8×6 | | les deux se lisent ensemble |

**Deux autres familles « température » moins évidentes** (axes à confirmer) :
`0xE6306` (`C596` 98-3000 × `C5FA` **2331-3631** = −40…+90 °C) et `0xE39C0` / `0xE38D8` (axe `C3BA`
2331-3331).

---

## 4. Ce que je corrige dans la méthode

| erreur | correction |
|---|---|
| « `0xE8A06` est dans la cascade d'IQ » | **hors cascade** : commande de pompe, sortie **octet** `C8F8` |
| « les cartes 162 octets sont des cartes de couple » | retiré (É.118) puis **E29** : ce sont des champs pointés |
| « la limitation vient des courbes `0xE83xx` » | partiellement : **la limitation vient de `C690` (smoke map) + `C688`/`C682` + températures** |

**Deux fonctions d'interpolation distinctes**, à ne plus confondre :

| routine | entrées | usage |
|---|---|---|
| `unk_1D50(ptr, X, Y)` | **valeurs** | cartes classiques (smoke map, wish…) |
| `word_1D94(ptrX, ptrY, ptr)` | **pointeurs** | cartes de la bibliothèque |

## 5. Inventaire livré

`inventaire_cartes_2D_axes.csv` — **85 cartes 2-D** détectées par leur signature
`[tagY][nY][axeY][tagX][nX][axeX]`, avec les deux variables d'axe et l'étendue de chaque axe.
C'est désormais la base de travail : **on part des cartes et de leurs axes**, le code ne sert qu'à
confirmer le consommateur.

## 6. Prochaine étape utile

1. Nommer `C3E6` avec certitude (remonter `word_15F0 → 0xE3AD0` champ `[+4]`) → l'axe air de la smoke map.
2. Repérer les **cartes qui plafonnent `C698`** en plus de `C690` : `C688`, `C682`, et voir lesquelles
   sont **par température** → c'est là que se joue une limitation « à froid » réelle.
3. Pour la 1re/2de : la smoke map `0xE8444` est **le bon levier** (elle plafonne tout), bien avant les
   courbes `0xE83xx`.
