# ÉTAPE 92 — Le régulateur de vitesse : machine à états, ressources de calibration, et **le bloc d'identifiants `0x0F00`–`0x0F1E`**

> Inventaire complet des moyens du régulateur : **la machine à états `sub_AC65E` (5 états)**, les **12 handles**
> qu'elle consomme avec leurs adresses et contenus, **5 courbes sur `C3AE`** (axe 1 000-4 500), et le
> **bloc d'identifiants `0x0F00`-`0x0F1E`** qui contient — entre autres — **deux séries de 6 variables
> consécutives** (par cylindre) et les deux grandeurs du mode (`C562`/`C576`).

---

## 1. La machine à états : `sub_AC65E` (l.171280)

```c
r4 = word_C42E ; word_C91C = r4          ; copie de travail du régime
r5 = word_1C94
r2 = [r5+#2] (= 150) ; cmp r2, C91C ; cc_SGE → état 0
r2 = [r5+#4] (= 300) ; cmp r2, C91C ; cc_SLE → état 0
sinon r12 = 1                             ; fenêtre d'activation

r4 = word_C7DE ; and r4, #8 → byte_D82A = 0
rl4 = byte_D82A ; cmpb rl4, #4 ; cc_UGT → sortie
r4 = rl4 << 1 ; add r4, #0A10h ; jmpi [r4]     ; ★ TABLE DE SAUTS (5 états)
```

| état | ce qui est fait |
|---|---|
| **0** | remise à zéro : `C140 = 0`, `C786 = 0`, `C7DE = 0`, état → 1 |
| 1…4 | voir ci-dessous (fenêtre `[0x14A2]`, seuils, courbes) |

Les états lisent `word_14A2` (`[+0Ah]` vs `word_1C94 [0]`) : c'est la **comparaison consigne / mesure**.

## 2. Les ressources de calibration du régulateur

| handle | EA | contenu (10 premiers mots) | lecture |
|---|---|---|---|
| `0x141E` | `0xE1148` | 0 · 2048 · 260 · 1 · 1024 · 512 · 0 · 512 · 1280 · 1280 | **bloc configuration véhicule** (contient `C60E` à `+0x26`) |
| `0x14A2` | `0xE2728` | 2000 · 2000 · 20 · 20 · 0 · 0 · 20 · 0 · 2 · 68 | **paramètres du régulateur** |
| `0x17B2` | `0xE4584` | 1000 · −1 · 69 · −1 · 0 · 1 · −1 · 0 · 1 · −1 | paramètres / pas de réglage |
| `0x1C94` | `0xE964A` | **500** · **150** · **300** · 1000 · 3000 · … · 2 · 1000 · 3000 · 5000 | **bloc d'état** (`[0]`, `[+2]`, `[+4]` = fenêtre) |
| `0x1DDA` | `0xEB9DA` | `[C3D2][2][2431 2531]` … | **axe de température** (−30 / −20 °C) |

### Les 5 courbes du régulateur, toutes sur `C3AE`

| handle | EA | axe |
|---|---|---|
| `0x19C8` | `0xE6C10` | `[C3AE][8]` 1000 · 1300 · 1500 · 1750 · 2000 · 2500 · 3000 · 4500 |
| `0x19CA` | `0xE6C34` | idem |
| `0x19CC` | `0xE6C58` | idem |
| `0x19D0` | `0xE6CB0` | idem |
| `0x19CE` | `0xE6C7C` | `[C3AE][12]` 1000 · 1250 · 1500 · 1750 · 2000 · 2500 · 2750 · 3000 · … |

⇒ **`C3AE` est la grandeur d'entrée de ces 5 courbes**, et `C3AE` porte l'identifiant **`0x1F40`**.
C'est aussi l'axe de la courbe `0xE86F4` (`[C3AE][10][0 50 300 500 600 1000 1150 1250 1750 1760]`).
**Hypothèse forte : `C3AE` = régime de travail du régulateur** — mais je n'ai pas encore la preuve,
et le fait que `C3AE ← [0xF884]` (RAM non symbolisée) laisse la porte ouverte à une **consigne**.

Sous-programmes employés : **`unk_1D36`** (1-D) et **`unk_20AC`** (mise à l'échelle) — deux primitives seulement.

## 3. ★ Le bloc d'identifiants `0x0F00`–`0x0F1E` (41 identifiants)

C'est le cœur de la trame de mesure, et il répond à beaucoup de questions en attente :

| ID | RAM | note |
|---|---|---|
| `0x0F00` | `C3D2` | T liquide de refroidissement |
| `0x0F01` | `C3BA` | T air d'admission |
| `0x0F02` | `C3B0` | T carburant |
| `0x0F06` | `C6E8` | — |
| **`0x0F08`** | **`C562`** | **quantité de référence (8 000 = 80 mg)** |
| `0x0F0A` | `C552` | état associé |
| **`0x0F0B`** | **`C576`** | **indice de mode / nervosité** |
| `0x0F0C` | `C6EA` | — |
| **`0x0F10`** | **`C42E`** | **régime** |
| `0x0F12` | `C428` | — |
| `0x0F13`…`0x0F18` | **`C442` `C444` `C446` `C448` `C44A` `C44C`** | **6 variables consécutives** |
| `0x0F19`…`0x0F1E` | **`C436` `C438` `C43A` `C43C` `C43E` `C440`** | **6 variables consécutives** |

⇒ **deux séries de six**, exactement la signature de valeurs **par cylindre** (corrections/quantités
individuelles). C'est une piste neuve et concrète : `0x0F13`-`0x0F18` et `0x0F19`-`0x0F1E` sont les deux
jeux à instruire.

Et la **trame `0x0E80`-`0x0EA8`** (19 identifiants) pointe vers `C4B6`…`C502` — **le bloc EGR** déjà repéré
(étape 61).

## 4. Vitesse et rapport engagé : où j'en suis

| recherche | résultat |
|---|---|
| axe « vitesse » dans la calibration | **2 seulement** : `0xE4954` `[C337][2][0 250]` et `0xE5150` `[C590][8][0 20 30 40 50 60 70 90]` |
| carte exploitant `C590` | `0xE513C` : `[D202][8][1000…3000] × [C590][8][0…90]`, grille **constante en vitesse** (1005 → 1459 selon `D202`) |
| axe « rapport » `0,1,2,3,4,5,6` | **aucun** dans tout le Datensatz |

Deux conclusions possibles, et il faut trancher :

1. **Le rapport engagé n'est pas un axe de carte** : il est traité **en code** (variable d'état comparée à
   des seuils), ce que suggère l'absence totale d'axe `0..6`.
2. **La vitesse est reconstruite** par le calcul `unk_20AC(x, 1000, 0xC5A)` (l.156803, 157583) : ce n'est
   pas une mesure directe mais une **grandeur dérivée** — donc une carte à axe « vitesse » peut très bien
   n'avoir qu'un axe symbolique.

**Ce qu'il me faudrait de toi** : sur le 4HX, la vitesse arrive-t-elle par le **calculateur ABS/ESP** (trame
CAN/PSA) avec un identifiant de mesure dédié ? Si tu as le code identifiant de la vitesse au diagnostic,
je le remonte en trois lignes — et le rapport engagé se déduira de `vitesse / régime`.

## 5. Prochaines cibles

1. **Les 5 courbes `0xE6C10`…`0xE6CB0`** : les dumper (elles sont les gains du régulateur).
2. **Les deux séries de 6** `C436`-`C440` et `C442`-`C44C` : chercher leur producteur (correction par cylindre).
3. **Le producteur de `C576`/`C93E`** (l.140049, 171718, 172956, 176887) : c'est là que se décide le mode.

## 6. Consignation

**`CATALOGUE_MAITRE.md` § 13 B.39** — machine à états `sub_AC65E`, les 12 handles du régulateur avec EA et
contenus, les 5 courbes sur `C3AE`, le bloc d'identifiants `0x0F00`-`0x0F1E` avec les deux séries de 6,
et l'état de la recherche « vitesse / rapport ».
