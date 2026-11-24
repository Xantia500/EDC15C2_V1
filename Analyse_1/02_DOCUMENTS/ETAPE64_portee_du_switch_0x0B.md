# ÉTAPE 64 — Ce que fait `+0x0B`, et pourquoi ce n'est pas la même chose que les autres octets

> Ta question : *« seule la donnée en `0xE111E` désactive l'EGR ou la fonction principale ; que fait en
> plus ce switch en `0xE111E+0x0B` (`0xE1129`) ? Agit-il sur les mêmes fonctions ? »*
>
> Réponse en deux temps : **(1)** la donnée en `0xE111E` elle-même n'est lue par personne — c'est donc
> `+0x0B` qui coupe la boucle ; **(2)** non, il n'agit pas sur les mêmes fonctions : c'est l'octet de
> **portée la plus étroite** de tout le bloc.

---

## 1. ⚠ Correction : l'octet en `0xE111E` (offset `+0x00`) n'est **lu par aucun site**

Quatre vérifications indépendantes :

| test | résultat |
|---|---|
| accès sans déplacement (`movb rl5, [r4]`) dans les 9 sites | **aucun** |
| accès `[r4+#0h]` / `[r4+#00h]` | **aucun** |
| handles voisins susceptibles de déborder sur `0xE111E` | `word_1418` (→ `0xE1106`) n'accède qu'à `+8` ; `word_141A` (→ `0xE1112`) n'accède qu'à `+8` |
| arithmétique de pointeur (`mov r4, word_141C` puis `add r4, …`) | **aucune** |

**Conséquence** : l'octet à `0xE111E` vaut `0x00` mais **personne ne le lit** — il ne peut donc
désactiver ni l'EGR ni la fonction principale. Deux octets du bloc sont dans ce cas :

- `+0x00` → jamais lu ;
- `+0x04` (→ `byte_C2BB`) → **écrit mais jamais relu** (0 lecture).

**Reconcialition probable** : si une définition de fichier annonce « EGR off » à `0xE111E`, elle désigne
la **base du bloc**, pas un octet. L'octet que le code teste réellement est **`0xE1129` = `+0x0B`**.

---

## 2. Que fait `+0x0B` **en plus** ? Rien d'autre — et c'est mesurable

`+0x0B` n'a **que 2 sites**, tous deux dans **la même fonction**, tous deux sur l'entrée de la boucle :

| site | EA | variable |
|---|---|---|
| `l.196410` | `0xBB51E` | `word_DB64`, `word_DB66` |
| `l.196439` | `0xBB558` | `[r0]` → `word_D492` |

Plus la branche commune `loc_BB550` : `word_DB6C = 0`, `word_DB6E = 0`.

| variable | valeur forcée | ce que ça annule |
|---|---|---|
| `word_DB66` | `0` | la **consigne** (les *deux* chemins de calcul) |
| `word_DB64` | `0` | le terme remis à zéro à chaque transition |
| `word_D492` | `0` | la valeur interpolée de la carte `0xE9660` |
| `word_DB6C`, `word_DB6E` | `0` | le **terme accumulé** (intégrale) |

**Rien de plus.** Les images `word_D4xx` tombent à zéro **par conséquence** (elles recopient `DB66`/`DB68`),
ce n'est pas une action de l'octet. Et il ne touche ni le code d'état (`+0x0D`), ni le choix du
régulateur (`+0x0C`), ni les identifiants de diagnostic.

---

## 3. ★ Non, il n'agit pas sur les mêmes fonctions — portée mesurée

J'ai mesuré, pour **chaque** octet du bloc, le nombre de lectures et les **segments** atteints
(mapping ligne → EA via `addr.pkl`, puis EA → segment) :

| octet | miroir | lectures | segments atteints |
|---|---|---|---|
| **`+0x0B`** | *(test direct)* | **2 sites** | **seg015, 1 seule fonction** |
| `+0x27` | `byte_C2BA` | **61** | s13 = 11, s14 = 37, s15 = 7, s16 = 5, s17 = 1 |
| `+0x0E` | `byte_C2B7` | **29** | s13 = 14, s14 = 1, s15 = 10, s16 = 4 |
| `+0x10` | `byte_C2B6` | **24** | s13 = 5, s14 = 6, s15 = 11, s17 = 2 |
| `+0x03` / `+0x15` | `C2BD` / `C2C0` | 12 / 12 | s14-s15-s16 |
| `+0x17` / `+0x1A` | `C2B8` / `C2D1` | 8 / 8 | s13-s14-s16 / s16 |
| `+0x0A` | `C2C9` | 7 | s13 = 5, s15 = 2 |
| `+0x16` / `+0x18` / `+0x26` | `C2BF` / `C2B4` / `C2C4` | 6 / 6 / 6 | s14 / s13-s14-s15-s16 / s14-s15-s16 |
| `+0x01` / `+0x02` / `+0x19` | `C2B1` / `C2C5` / `C2D0` | 5 / 5 / 5 | s13-s16 / s14-s16 / s16 |
| `+0x09` | `C2B0` | 3 | s14, s16 |
| `+0x06` / `+0x0F` | `C2B9` / `C2B3` | 2 / 2 | s14 / s15 |
| `+0x1B`…`+0x25`, `+0x28` | 11 miroirs | **1 chacun** | **s16 uniquement** |

**Total : 214 lectures** pour les 31 miroirs.

**Le classement est sans ambiguïté :**

- **`+0x0B` = portée minimale** : 2 sites, 1 fonction, 1 boucle. C'est un **pur coupe-circuit de boucle**.
- **`+0x27` (`byte_C2BA`) = portée maximale** : 61 lectures, **5 segments** (dont 37 en seg014) — ce n'est
  pas une option de boucle, c'est une **option de configuration globale**.
- Les octets `+0x1B`…`+0x25` et `+0x28` ne sont lus **que dans seg016** : ils ne concernent qu'**un seul
  service** (probablement la couche communication/diagnostic).

⇒ **Réponse directe : non.** `+0x0B` n'agit pas sur les mêmes fonctions que les autres octets du bloc.
Le bloc n'est pas un ensemble d'interrupteurs d'une même fonction : c'est **une collection d'options
indépendantes**, chacune ayant sa cible propre. Un seul de ces octets touche la boucle d'air/EGR.

---

## 4. Ce que cela change dans la lecture d'ensemble

| question | réponse |
|---|---|
| « La donnée en `0xE111E` désactive-t-elle l'EGR ? » | **Non** : octet jamais lu. C'est `+0x0B` (`0xE1129`) qui coupe la boucle |
| « `+0x0B` fait-il plus que couper la boucle ? » | **Non** : 2 sites, 5 variables, tous sur l'entrée du régulateur |
| « Agit-il sur les mêmes fonctions ? » | **Non** : portée la plus étroite du bloc (1 fonction) contre jusqu'à 5 segments pour `+0x27` |
| « Y a-t-il un autre octet qui coupe la boucle ? » | **Aucun** — un seul octet du bloc touche ce régulateur, hors `+0x0C` (qui choisit *quel* régulateur) et `+0x0D` (qui fixe l'état) |

---

## 5. Consignation

- **`CATALOGUE_MAITRE.md` § 13 B.10** ajouté : portée mesurée des 31 octets, avec segments.
- **2 044 → 2 090 lignes.**

## 6. Prochains pas

1. **Trancher la nature de la boucle** : `word_C7B8` → source capteur (débitmètre ⇒ EGR, pression ⇒ VNT). **Toujours prioritaire.**
2. **`byte_C2BA` (`+0x27`, 61 lectures, 5 segments)** : désormais identifié comme *l'option globale* du bloc — c'est elle qu'il faut décoder en premier pour comprendre la variante véhicule.
3. **Les 11 octets « seg016 seulement »** : ils forment un groupe homogène ; les traiter ensemble donnera la logique de la couche communication d'un coup.
