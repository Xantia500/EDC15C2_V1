# ÉTAPE 72 — Comment un défaut s'inscrit, se maintient ou disparaît (explication simple, puis les preuves)

> C'est la pièce que je cherchais depuis deux étapes, et elle est **trouvée**. Je commence par le
> fonctionnement en français courant, puis je donne les preuves ligne par ligne.

---

## 1. Le principe, en clair

Un calculateur ne « voit » pas un défaut. Il surveille des **conditions**, et il garde en mémoire
**7 fiches de 22 octets** (c'est le maximum qu'il peut stocker). Chaque fiche dit :

- **quel code** de défaut (octet 0),
- **dans quel état** il est (octet 1 : actif, confirmé, mémorisé…),
- **deux compteurs** (octets 4 et 5) : ils comptent les cycles,
- **un numéro de variante** (octet 6),
- **un niveau** (octet 7).

À chaque cycle, le calculateur repasse sur ces fiches et se pose **six questions**. Si une seule réponse
est mauvaise, **la fiche est effacée**. C'est ce mécanisme qui décide si un défaut FAP ou EGR
« tient » ou s'efface tout seul.

## 2. Le schéma de la chaîne complète

```
   capteur / mesure
        │
        ▼
   test diagnostic  ──(686 sites appellent sub_CE9B4)──►  état du défaut
                                                            ├─ RAM 0xFD21 + code   (1 octet de bits)
                                                            └─ RAM 0xCAD0 + 4·code (4 octets)
        │
        ▼
   fiche de défaut (7 × 22 octets en RAM 0xE467)
        │                    ▲
        │                    └── alimentée / relue de l'EEPROM (offset 0x2467, 176 octets)
        ▼
   ★ SIX QUESTIONS DE MAINTIEN  ← ← ←  c'est ici que TOUT se décide
        │
        ├── si la fiche est effacée  →  plus de défaut
        └── si elle reste → l'état 0xFD21 sert au diagnostic :
                 bit 0 posé  →  la mesure répond 0x0000
                 bit 1 posé  →  la mesure répond 0xFFFF
                 (tables 0xE11A0 et 0xE117C du Datensatz)
```

## 3. ★ Les six questions — l'algorithme exact

`r3` = la fiche, `r0` = le descripteur du code (`[0xCCB2 + 2·code]`).

| # | question posée | ligne | si la réponse est mauvaise |
|---|---|---|---|
| 1 | le code est-il **valide** ? (`descr+0x00` bit 0 = 0) | 231252 | fiche **supprimée** |
| 2 | **classe** (`descr+0x1C` bits 0-1) : si **< 2**, l'octet 1 bit 0 doit valoir **1** ; si **≥ 2**, il doit valoir **0** | 231257-231268 | supprimée |
| 3 | **niveau** (octet 7) : `0` ⇒ supprimée ; `1` ⇒ le bit 3 de l'octet 1 doit être **0** ; `>1` ⇒ il doit être **1** | 231270-231283 | supprimée |
| 4 | si l'octet 1 bit 6 est posé, l'**octet 6** doit être **égal** à `word_142A + 9` — un octet de **variante / codage** | 231284-231289 | supprimée |
| 5 | **compteur A** (octet 4) ≤ **`descr+0x1D`** | 231290-231293 | supprimée |
| 6 | **compteur B** (octet 5) ≤ **`descr+0x1E`** (si ce seuil vaut 0, on prend **1**) | 231294-231299 | supprimée |

**Les deux seuils numériques d'un code de défaut sont donc `+0x1D` et `+0x1E` de son descripteur.**
Et la question 4 est capitale : **un octet de codage décide de la survie de tout un ensemble de défauts.**

## 4. Deux corrections que je dois te faire

1. **`0xCCB2 + 2·code` n'est jamais écrit en marche.** J'ai vérifié les **13 sites** qui le référencent :
   tous le **lisent**. Il est rempli **une seule fois au démarrage** (l.231171-231180).
2. **`descr+0x1C` n'est pas un seuil.** C'est un **code de classe 0…3** (bits 0-1) doublé d'un **masque**
   (bits 3-7, `andb #0F8h` l.231777). Les seuils sont `+0x1D` et `+0x1E`. Mon tableau de l'étape 69
   mélangeait les deux.

## 5. Ce que ça change concrètement

- **Un défaut n'apparaît pas parce qu'une mesure dépasse un seuil** : il apparaît parce que les **six
  questions** ci-dessus sont satisfaites. La sensibilité de la détection se règle donc sur `+0x1D`,
  `+0x1E`, la classe et la variante — **pas** sur une carte de mesure.
- **`word_142A + 9`** est un octet de **codage** : c'est un levier direct sur la liste des défauts conservés.
  C'est typiquement ce qui distingue deux versions du même calculateur.
- Les **7 fiches** sont le maximum : un calculateur qui a 7 défauts pleins **n'en enregistre plus** de
  nouveaux. C'est un comportement à connaître avant de lire une mémoire de défauts chargée.

## 6. Ce qui reste incertain (et je ne le maquille pas)

- L'adresse exacte des descripteurs `[0xCCB2 + 2·code]` : la valeur est du type `0xA1A8`, et selon la page
  en vigueur elle tombe en RAM (`0xA1A8`) ou en flash (`0xEA1A8`). **Cela ne change rien à l'algorithme
  des six questions** — mais cela change l'endroit où lire les valeurs de `+0x1D` / `+0x1E`.
- Les 14 octets `+8…+21` de la fiche restent non exploités.

## 7. Consignation

- **`CATALOGUE_MAITRE.md` § 13 B.18** (2 472 → **2 500 lignes**) : les six conditions, les corrections.
- Étapes liées : 68 (états `0xFD21`), 69 (fiches de 22 octets), 71 (pages et plages RAM).

## 8. Où j'irais ensuite

1. **`word_142A + 9`** : lire cette valeur pour ta configuration et voir **quels codes** dépendent d'elle
   (question 4). C'est le levier le plus directement utile.
2. **`descr+0x1D` / `+0x1E`** : une fois la page tranchée, extraire les **96 couples de seuils** et les
   présenter en tableau — c'est un livrable directement lisible pour toi.
