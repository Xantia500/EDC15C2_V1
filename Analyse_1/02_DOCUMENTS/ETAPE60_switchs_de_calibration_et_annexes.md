# ÉTAPE 60 — Les switchs de calibration : **253 options qui shunting 7 232 lignes**

---

## 1. ★★★ Le mécanisme, et pourquoi il est reconnaissable sans ambiguïté

```asm
mov   r5, word_141E        ; handle de calibration  ->  structure EA 0xE1148
movb  rl4, [r5+#0Dh]       ; OCTET d'option, offset 13
jmpa  cc_NZ, loc_A4916     ; si NON NUL  ->  SAUTE 864 LIGNES ENTIÈRES
```

Trois traits **simultanés**, donc pas de faux positif possible :

1. un **handle de calibration** est chargé ;
2. un **octet** (et non un mot) est lu dans la structure ;
3. un **saut long** (`jmpa`) suit immédiatement.

**Le discriminant décisif est le deuxième.** Les paramètres numériques sont des **mots** ; les
switchs sont des **octets**. C'est ce qui les sépare sans erreur — et c'est cohérent avec ce qu'on
avait vu dès l'étape 13 : tous les axes, seuils, gains se lisaient en mots, jamais en octets.

**Et le troisième trait dit la nature du switch :** `jmpa` = saut long = **shunt de bloc entier**.
On n'est pas devant un ajustement, mais devant une **décision**.

---

## 2. L'inventaire

| mesure | valeur |
|---|---|
| switchs conditionnels | **253** |
| fonctions concernées | **41** |
| structures de calibration porteuses d'options | **37** |
| **lignes de code shuntées au total** | **7 232** |
| actifs si l'octet est **NUL** | 109 |
| actifs si l'octet est **NON NUL** | 84 |

*(29 sites supplémentaires ont été écartés : le saut qui les suit est inconditionnel, ce ne sont donc
pas des switchs. Le tri est fait, pas supposé.)*

**7 232 lignes de code** dont l'exécution dépend d'un octet de calibration. Pour un firmware dont le
listing utile fait ~404 000 lignes, c'est **près de 2 % du code qui est piloté par des options**.

---

## 3. ★★★ `0x141E` → EA `0xE1148` : le **bloc d'options maître**

**60 options**, lues depuis **7 fonctions différentes**, **3 600 lignes shuntées** à lui seul.

Voici les octets, tels quels :

```
#0 ..#31 : 00 00 00 08 04 01 01 00 00 04 00 02 00 00 00 02 00 05 00 05 04 84 BE CA 64 00 01 01 01 00 01 96
#32..#63 : 00 00 01 01 01 02 02 00 00 00 02 00 00 00 00 00 01 01 00 00 FF FF FF FF FF FF FF FF FF FF FF FF
```

**Ce n'est pas de la calibration numérique, c'est un jeu d'options** : les valeurs sont 0, 1, 2, 4, 5
— des **codes de mode**, pas des grandeurs. Et la fin de la structure est un mur de `FF` =
**emplacements non utilisés**.

**25 des 60 options sont dans l'état actif** dans ce firmware. Les 35 autres désactivent leur bloc.

---

## 4. Les autres structures d'options — et un recoupement indépendant

| handle | EA | options | lignes shuntées | remarque |
|---|---|---|---|---|
| **`0x141E`** | `0xE1148` | **60** | **3 600** | **le bloc maître** — 7 fonctions le lisent |
| `0x1928` | `0xE5FE8` | 37 | — | options par **paires d'offsets** (0/1, 10/11, 16/17…) : un octet par stratégie |
| `0x1972` | `0xE6542` | 23 | — | groupes (22/23, 34/35, 36/37, 38/39, 44/45, 50/51) |
| `0x18EE` | `0xE52EE` | 19 | — | |
| **`0x18B2`** | `0xE4E2C` | 14 | — | **déjà identifié comme sélecteur de variante** (offsets 18 = `0x12` et 28 = `0x1C`) |
| `0x1D2C` | `0xEA314` | 10 | — | offsets **0,10,11,12,…,18** : tableau d'options séquentiel |
| `0x1A64` | `0xE7E84` | 10 | — | |
| `0x1E2C` | `0xEBC14` | 9 | — | |
| `0x148A`, `0x1904`, `0x1B22`, `0x147A` | — | 6-7 | — | options à l'offset 0 : un simple drapeau en tête |

**★★ Le recoupement qui compte :** `0x18B2` ressort avec des options aux offsets **18 (`0x12`) et
28 (`0x1C`)** — exactement le **masque de variante** identifié à l'étape 44 par une voie totalement
différente (les drapeaux `word_FD38`, `word_FD7A`, `word_FD7C` armés par le CAN). **Deux méthodes
indépendantes, même conclusion.**

---

## 5. Les vingt switchs qui shuntent le plus de code

| fonction | structure | offset | valeur ici | polarité | lignes shuntées |
|---|---|---|---|---|---|
| `sub_A1E9E` | `0xE1148` | +13 | `0x00` | actif si NON NUL | **864** |
| `sub_A5C92` | `0xE1148` | +12 | `0x00` | **actif si NUL** | **787** |
| `sub_AFAA0` | `0xE232A` | +0 | `0x01` | actif si NON NUL | 578 |
| `sub_BF750` | `0xE1148` | +41 | `0x00` | actif si NON NUL | 576 |
| `sub_AFAA0` | `0xE83DA` | +17 | `0x01` | **actif si NUL** | 387 |
| `sub_972FA` | `0xE1148` | +20 | `0x04` | actif si NON NUL | 363 |
| `sub_AFAA0` | `0xE81A4` | +0 | `0x01` | — | 227 |
| `sub_AFAA0` | `0xE1148` | +51 | `0x00` | actif si NUL | 151 |
| `sub_A7D96` | `0xE6542` | +39 | `0x04` | actif si NUL | 147 |
| `sub_A7D96` | `0xE6542` | +39 | `0x04` | actif si NUL | 118 |
| `sub_AF932` | `0xE2332` | +0 | `0x01` | actif si NUL | 103 |
| `sub_9BAF0` | `0xE232A` | +0 | `0x01` | actif si NON NUL | 97 ×3 |
| `sub_C1B5E` | `0xEA314` | +0 | `0x01` | — | 96 |
| `sub_ACD4A` | `0xE1148` | +36 | `0x01` | actif si NON NUL | 68 |
| `sub_D3C5A` | `0xE1148` | +44 | `0x00` | actif si NON NUL | 64 |

**Trois cas parlants, lus dans le code :**

- `sub_A1E9E` lit `[0xE1148+13]` = **0**, condition « actif si NON NUL » → **les 864 lignes sont
  exécutées** dans cette calibration ;
- `sub_A5C92` lit `[0xE1148+12]` = **0**, condition « **actif si NUL** » → **les 787 lignes sont
  shuntées**. Une stratégie entière est **désactivée** — pas atténuée : absente ;
- `sub_AFAA0` lit `[0xE232A+0]` = **1**, « actif si NON NUL » → 578 lignes actives. **Et cette même
  structure porte 7 options, lues depuis 4 fonctions différentes.**

**⇒ C'est exactement le mécanisme que tu décrivais.** Un octet autorise ou interdit une portion
entière de fonction, **sans toucher au code**. Et la taille des blocs shuntés (jusqu'à 864 lignes)
montre qu'ils contiennent des **algorithmes complets**, pas des cas particuliers.

---

## 6. ★ « Soit ignore, soit applique une autre stratégie »

Tu as vu juste sur ce point aussi, et il y a même les **deux formes** dans le code :

**Forme 1 — shunt pur** (le cas ci-dessus) : le bloc est sauté, la fonction continue sans lui.

**Forme 2 — aiguillage vers une autre stratégie.** L'exemple est déjà décodé (étape 59), c'est le
switch à **trois issues** de `sub_AC65E` :

```asm
mov  r5, word_141E
movb rl4, [r5+#23h]      ; octet d'option, offset 0x23
jmpr cc_Z, loc_ACC10     ; 0 -> source word_C616
cmpb rl4, #1
jmpr cc_Z, loc_ACC1A     ; 1 -> source word_C91C (régime)
jmpr cc_UC, loc_ACC24    ; autre -> source word_C93E
```

**Ce n'est pas « activé / désactivé » : c'est « quelle entrée ».** Dans ce firmware l'octet vaut
`0xCA`, donc la boucle de régulation travaille sur **`word_C93E`** — ni le régime, ni `C616`.

Et les comparaisons `cc_ULE` (40 sites) sont de la même famille : `mode ≤ N` = **choix dans une
gamme de stratégies**, pas un simple drapeau.

---

## 7. Consignation demandée : les annexes sont en fin de document

Le catalogue se termine désormais par deux annexes, comme tu l'as demandé :

| annexe | contenu |
|---|---|
| **§ 12 — Annexe A : correcteurs, filtres et boucles de régulation** | les 4 interpolateurs, les 2 traitements décodés (filtre récursif à coefficient calibré, canal de régulation complet), et la **table des 35 boucles** avec leur état persistant et leur cible |
| **§ 13 — Annexe B : les switchs de calibration** | le mécanisme, les mesures d'ensemble, les **37 structures d'options**, les 20 switchs majeurs avec **valeur effective et polarité**, et les exemples lus dans le code |

**Catalogue : 1 623 → 1 795 lignes.**

**Fichiers** : `switchs_calibration.csv` (282 sites : fonction, structure, offset, valeur, polarité,
lignes shuntées), `boucles_regulation.csv` (35 boucles), `outils/switchs_calibration.py`.

---

## 8. Ce que cela ouvre

1. **`0xE1148` est la table de configuration du calculateur.** 60 octets, dont 25 actifs. **C'est le
   premier endroit à lire pour comprendre ce que ce calculateur fait ou ne fait pas** — et le premier
   endroit où une modification change la stratégie sans toucher au code.
2. **Les 37 structures d'options** sont autant de tables de configuration secondaires. Les paires
   d'offsets de `0x1928` et `0x1972` suggèrent **un octet « valeur » + un octet « activation »** par
   stratégie.
3. **`sub_A7D96`** concentre **12 boucles de régulation** (annexe A) **et** lit des options de
   `0xE6542` : c'est le **cœur de régulation**, et la prochaine cible logique.
4. **L'octet `[0xE1148 + 0x23]`** vaut `0xCA` : la boucle de régulation n'utilise donc **pas** le
   régime comme entrée. Comprendre quelle grandeur est `word_C93E` dirait **ce que cette boucle
   régule**.
