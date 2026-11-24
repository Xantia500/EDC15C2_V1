# ÉTAPE 71 — Verrou DPP levé : les 1 277 pointeurs sont des **adresses RAM**, et chaque défaut possède sa plage

> J'ai suivi la chaîne d'appel jusqu'au bout : `sub_CEC02` ← code non étiqueté de `seg016` ← **rien**, aucun
> `scxt DPP`. Alors je suis allé voir où le firmware **fixe** ses pages. La réponse y était, en quatre lignes.

---

## 1. La configuration de pages du firmware — enfin établie

```asm
scxt DPP0, #0        ; l. 96805
scxt DPP1, #0        ; l. 96806   ← DPP1 = 0, PAS 1
scxt DPP2, #2        ; l. 96807
scxt DPP3, #3        ; l. 96808
```

⇒ **l'espace 16 bits couvre EA `0x00000`–`0x0FFFF`**, soit 64 Ko de RAM et de périphériques internes.
Les pages flash ne sont ouvertes que **localement, six fois** :

| page | valeur | lignes |
|---|---|---|
| `DPP0` | `0x22` (`0x88000`) | 96530, 97450, 98358, 98477, 98515, 111273 |
| `DPP1` | `0x21` (`0x84000`) | 98479 |
| `DPP2` | `0x24` (`0x90000`) | 233064, 233137 |
| `DPP2` | `0x48` | 111665 |

Le reste du temps, les DPP sont **sauvegardés puis restaurés** depuis `word_C1DA` / `word_C1DC`
(`mov word_C1DA, DPP0` l.112878 ; `scxt DPP0, word_C1DA` l.125397 ; écriture calculée l.199535).

## 2. Conséquence : les 1 277 pointeurs sont des **adresses RAM**

Aucune routine qui consomme les 96 listes (`sub_CEC02` et le bloc l.231157-231530) ne touche à un DPP.
⇒ un pointeur `0xA1A8` vaut **EA `0xA1A8`** : une **variable RAM**, pas une adresse flash.

Mon test de l'étape 70 (« le contenu à `fo 0xA1A8` est du code ») comparait donc **une adresse RAM à un
offset de fichier**. L'hypothèse à réfuter était mal posée — je le consigne tel quel.

## 3. ★ Ce que révèle la géométrie des pointeurs

| constat | mesure |
|---|---|
| plages **disjointes** | **3 paires sur 4 465** seulement se chevauchent ⇒ **chaque code possède sa plage RAM privée** |
| écarts entre pointeurs consécutifs | **6 o** (316×), 12 (132×), 4 (92×), 2 (83×), 32 (78×), puis 10, 8, 36, 28, 24 |
| taille des enregistrements | **6 / 12 / 32 octets** |

| code | plage RAM | enregistrements |
|---|---|---|
| **0** | `0xA1A8`–`0xBAB0` | **139** |
| 1 | `0x2372`–`0x2736` | 10 |
| 2 | `0x9462`–`0x94C8` | 14 |
| 3 | `0xBAB6`–`0xBB9A` | 11 |
| 7 | `0x4A70`–`0x4A96` | 3 |
| 8 | `0x94CE`–`0xA128` | 49 |

⇒ **Chaque code de défaut possède en RAM une table privée d'enregistrements de 6, 12 ou 32 octets**,
et la liste du Datensatz n'en est que l'index. Ces tables sont **construites au démarrage à partir de la
calibration** : c'est là que vivent les seuils, pas dans la liste.

C'est un résultat structurel important : le Datensatz ne contient pas les seuils de défaut **en clair**,
il contient **la carte des tables de travail**, et les seuils se trouvent dans les structures qui les
alimentent.

## 4. Retour sur `word_1424` (`0xE11C4`) — la question de l'étape 68 est tranchée

Les valeurs `0x0F10 0x0F61 0x0F80 0x0FFA …` sont dans le **même espace** : des **adresses RAM** de la page
`0x0F00`. Donc les « trous » de l'étape 67 ne sont pas des marqueurs : ce sont simplement **les entrées qui
ne sont pas des codes ≤ 17**. Seules `0x0005` et `0x000F` en sont.

**La lecture « tableau mixte » est la bonne, et elle est maintenant motivée :** les 18 autres entrées sont des
adresses de variables, les 2 dernières des codes. Ce n'est pas une table homogène — c'est pourquoi aucune
lecture uniforme ne collait.

## 5. Bilan des trois étapes

| question posée | réponse |
|---|---|
| Quelles grandeurs sont surveillées par un défaut ? | **≈ 13 enregistrements de 6/12/32 o, en RAM, dans une plage privée par code** |
| Où sont les seuils ? | **pas dans la liste** : dans les structures qui construisent ces tables au démarrage |
| `word_1424` = adresses ou indices ? | **adresses RAM**, sauf `0x0005` et `0x000F` qui sont des codes |

## 6. Consignation

- **`CATALOGUE_MAITRE.md` § 13 B.17** (2 417 → **2 472 lignes**).
- `defauts_96_listes.csv` reste la référence des 1 277 pointeurs.

## 7. Prochain pas — c'est maintenant de la mécanique, pas de la devinette

**Trouver qui écrit les plages RAM privées.** Le point d'entrée est identifié : le bloc l.231157-231530
(`mov r0, #0E467h ; mov r2, #0B0h` puis la boucle `r12 = 0xB6AC`) construit l'état, et `sub_CEC02` gère
les enregistrements. Il faut chercher, dans `seg016`, les écritures `[rX+#0]` à `[rX+#5]` (6 octets) et
`[rX+#0]`…`[rX+#1F]` (32 octets) sur des pointeurs issus de `0xCCB2`.

Je propose de le faire avec un script qui, pour chaque adresse des 96 listes, cherche dans tout `clean.asm`
une écriture `[rN+#XX]` dont la base est chargée depuis `0xCCB2` — c'est exactement le motif déjà repéré
(`mov r0, [r0+#0CCB2h]`, 12 sites).
