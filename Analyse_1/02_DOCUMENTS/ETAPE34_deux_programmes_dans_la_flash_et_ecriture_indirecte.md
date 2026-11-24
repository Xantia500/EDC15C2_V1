# ÉTAPE 34 — Deux programmes dans la flash, et l'EEPROM écrite **indirectement**

Ta remarque sur le code immo en partie haute était juste : **il y a un second programme dans la
flash**, avec son propre serveur KWP2000. Et il change l'architecture générale du calculateur.

---

## 1. L'EEPROM n'est jamais écrite par un service de diagnostic

J'ai testé les 15 gestionnaires de services : **aucun n'appelle `sub_A0002`**, aucun ne touche
`0xE5CE`.

Ce qu'ils font à la place — exemple du service **0x14** (effacement des défauts), l. 207578-207607 :

```asm
                movb    rl4, #1
                movb    byte_C238, rl4        ; ← simple variable RAM
                ...
                movb    rl3, #1
                movb    byte_C30D, rl3        ; ← variable RAM (groupe word_CF6)
                movb    rl2, #2
                movb    byte_C31D, rl2        ; ← variable RAM (groupe word_C1E)
```

Or **`byte_C30D` et `byte_C31D` sont précisément deux champs de l'image EEPROM** (étape 30).
⇒ **L'interface avec l'EEPROM n'est pas une fonction d'écriture : ce sont les variables RAM.**
`sub_A0CCC` recopie ensuite l'ensemble dans l'image, une fois, au moment opportun.

**Conséquence pratique, et elle est importante** : « trouver toutes les fonctions qui écrivent
l'EEPROM » revient à « trouver tous les écrivains des ~30 variables recopiées par `sub_A0CCC` ».
C'est fini et dénombrable — contrairement à une recherche de pilote.

---

## 2. ★ La flash contient **deux programmes**, pas un

| plage | contenu | dans le dump |
|---|---|---|
| `0x00000-0x7FFFF` | boot primaire + bibliothèque (vecteurs, `memcpy`@0x2128, pilote EEPROM, table `0x0BA6`, table de pages `0x0FE00`, `unk_7EC8`) | ✘ |
| `0x80000-0xFBFFF` | **application** : gestion moteur + serveur KWP (seg 0x0C) | ✔ |
| **`0xFC000-0xFFFFF`** | **bloc de boot secondaire** : second serveur KWP + enregistrement « BOOT » + références | ✔ |

### Preuve de la séparation

- **26 appels** `calls 0Fh, …` existent (l. 403765 → 406405) : **tous sont situés à l'intérieur du
  bloc `0xFxxxx`**. L'application ne saute **jamais** dans ce bloc. ✓
- Le bloc a **ses propres buffers** : requête à **`0xFA24`**, pointeur de requête `word_FC1A`,
  pointeur de réponse `word_FC0C`, **octet de service `byte_FC3F`**, état de session `byte_FC12`.

⇒ C'est un **programme autonome**, entré seulement par un vecteur du boot primaire (absent).

---

## 3. Le second serveur KWP2000 (répartiteur l. 404206-404310)

| octet de service | destination | rôle KWP |
|---|---|---|
| `0x3E` | `unk_56CC` | TesterPresent |
| `0x10` | `sub_FE332` | StartDiagnosticSession |
| `0x31` | `word_CF44/word_CF46` + `unk_EAA` | StartRoutine (par pointeur far) |
| **`0x34`** | **`sub_FD6B6`** | **RequestDownload** |
| `0x35` | `sub_FE3A8` | RequestUpload |
| `0x82` | `sub_FE8FC` | (PSA spécifique) |
| **`0x27`** | **`sub_FE62E`** | **SecurityAccess** |
| `0x21` | `sub_FE4AE` | ReadDataByLocalIdentifier |
| autre | `sub_FEB22` | NRC 0x11 |

**0x34 / 0x35 = téléchargement/téléversement de flash** : c'est bien le serveur de
**programmation** (le « boot mode » K-Line). La précondition d'entrée est une session spéciale :
`byte_FC12 == 0xDC` (l. 404206).

---

## 4. Le service 0x27 (sécurité) — et où est l'algorithme

`sub_FE62E`, l. 406136+ :

```asm
                extp    #3Fh, #1
                movb    rl4, byte_FEC00      ; ← constantes en EA 0xFEC00-0xFEC01
                ...
                mov     r4, word_FC10
                jmpa    cc_NZ, loc_FE8E4     ; précondition : word_FC10 == 0
                jb      word_FDDE.1, loc_FE666
                ...
                movb    rl4, byte_CF30       ; précondition : byte_CF30 != 0
                ...
                cmpb    rl3, #81h            ; sous-fonction 0x81 = demande de graine
                cmpb    rl3, #82h            ; sous-fonction 0x82 = envoi de clé
                ...
                bset    word_FDDE.2
                mov     r12, #0FC2Eh
                mov     r13, #0FC34h
                calls   0, unk_7EC8          ; ← le calcul de graine
```

⇒ **L'algorithme de sécurité est `unk_7EC8`, à l'adresse EA `0x07EC8`** — donc dans la couche
absente. Graine en `0xFC2E`, réponse attendue en `0xFC34`, constantes en `0xFEC00`.

**C'est la localisation précise de la « clé » dont tu parles : elle n'est ni dans l'EEPROM, ni dans
l'application — elle est dans le boot primaire, à `0x07EC8`.**

---

## 5. Les enregistrements de structure en fin de flash

### `EA 0xFFF00` — l'enregistrement « BOOT »

```
AA 55 75 14 89 11 30 AA | 42 4F 4F 54 00 00 00 00   ← "BOOT"
puis une liste de pointeurs 24 bits :
  0x0FC000  0x0FFFFE  0x0FCC14  0x0DFF00  0x0FBF00  0x0FCC5A  0x0FCC2A
  0x0FFF00  0x000000  0x0FC300  0x0FC600  0x0FC000  0x0FD000
  0x0FEC00  0x0FD000  0x0FEC04  0x0FED9C        0x008A  BB BB  A5 A5
```

Cette liste **désigne les zones gérées** : le bloc `0xFC000-0xFFFFE`, la zone d'identification
(`0xFCC14`), la copie `0xDFF00`, `0xFBF00`, et les sous-blocs `0xFC300`, `0xFC600`, `0xFD000`,
`0xFEC00`, `0xFED9C`. C'est un **manifeste**, pas du code.

### `EA 0xFC000` — en-tête du bloc secondaire

```
A5 A5 14 C0 00 00 | 00 C0 00 00 | 40 C0 00 00 | 00 C3 00 00 | 01 E6 00 00 | 08 00 | 10 00
```
Signature **`A5A5`** (retrouvée aussi en `0xFC2FA+5`, `0xFC5FA+5`, `0xFEBFA+4`, `0xFFF53`), suivie
d'une série de valeurs 16 bits. Décodage **non abouti** : je ne l'interprète pas encore.

### `EA 0xFBEF9` / `word_FBF38` / `word_FBF3A`

Le bloc secondaire **lit des données situées dans la zone application** (`0xFBEF9`, `word_FBF38 =
0x232C`, `word_FBF3A = 0x3E`) — l. 405978-405985. ⇒ **La zone `0xFBxxx` porte des données
partagées**, pas seulement la copie du Datensatz.

---

## 6. Les défauts : première localisation

Le service **0x17** (`sub_C1544`) n'utilise que `word_DC66`, `word_DC6A`, `word_DC6C`, **`word_DC90`,
`byte_DC92`**. La zone RAM `0xDC80-0xDCD0` est le **plan de travail du diagnostic** :

```
byte_DC82 .. byte_DC8E   (9 octets)
word_DC90 / byte_DC92    ← base de la liste des défauts
word_DC9E .. word_DCCE   (25 mots)
byte_DCA8  word_DCAC  word_DCB0  word_DCB6..word_DCC8
```

**Je ne conclus pas** sur la structure des freeze frames : la zone est identifiée, le format ne l'est
pas. C'est la prochaine cible, avec l'outil `msg_map.py`.

---

## 7. ★ `byte_C89E` prend **1, 2 et 3** — ce n'est pas un simple octet « immo »

Deux services différents écrivent ce même octet et **recalculent** `word_C70A` :

| service | valeur écrite | ligne |
|---|---|---|
| 0x04 | `1` (et `2` dans une branche) | 151094 / 151130 |
| **0x14 (effacement défauts)** | **`3`** | 207601 |

et à chaque fois : `word_C70A = N | (0xFF−N)<<8` avec `N = byte_DC64 + 1`.

⇒ **Interprétation (inférée)** : `word_C70A` est un **compteur croissant protégé par son complément**,
et `byte_C89E` code **l'action qui a provoqué la dernière écriture** (1, 2, 3). Ce serait un journal
de sécurité du calculateur. **À vérifier** — mais cela **affaiblit** l'hypothèse « bloc de 10 octets
= PIN » : un PIN ne changerait pas de valeur quand on efface les défauts.

**Je corrige donc ma propre étape 33 §4** : le bloc de 10 octets est un **enregistrement d'état à
usage multiple**, pas nécessairement un identifiant d'antidémarrage. L'hypothèse « 8 octets + état »
reste ouverte mais n'est plus privilégiée.

---

## 8. Corrections de méthode

1. **Le numéro de segment n'est pas `EA >> 14`** : c'est **l'octet haut de l'EA**. Preuve :
   `calls 0Ah, sub_A0002` → EA `0xA0002` ; `calls 0Fh, sub_FDB08` → EA `0xFDB08`. La règle
   « segment = octet haut, opérande = 16 bits bas » est cohérente sur **tous** les cas vérifiés.
   *(La conclusion de l'étape 33 §7 « `unk_2128` = 0x2128, absent » reste valable : seg 0 ⇒ EA
   `0x02128`.)*
2. **Le bloc `0xFxxxx` n'est pas « la copie du Datensatz »** comme je l'ai écrit : `0xF0000-0xFBFFF`
   en est la copie, mais **`0xFC000-0xFFFFF` est un programme** (et `0xFBxxx` porte des données
   partagées).

---

## 9. Bilan de l'architecture (état actuel)

```
0x00000 ┌─────────────────────────────────────────────┐ ABSENT
        │ boot primaire, vecteurs, bibliothèque,      │
        │ memcpy, pilote EEPROM, table 0x0BA6,        │
        │ table de pages 0x0FE00, sécurité unk_7EC8   │
0x80000 ├─────────────────────────────────────────────┤ PRÉSENT
        │ APPLICATION                                  │
        │  · gestion moteur (cartes, régulation, FAP)  │
        │  · serveur KWP seg 0x0C (sub_C28B6, 18 svc.) │
        │  · API EEPROM sub_A0002 (42 commandes)       │
        │  · sub_A0CCC : image EEPROM ← variables RAM  │
0xFC000 ├─────────────────────────────────────────────┤ PRÉSENT
        │ BLOC SECONDAIRE (boot/programmation)         │
        │  · serveur KWP seg 0x0F (session, 0x27,       │
        │    0x34, 0x35, 0x21)                         │
        │  · « BOOT » + manifeste de pointeurs         │
        │  · références 0281010877 / 1037353776        │
0xFFFFF └─────────────────────────────────────────────┘
```

**L'antidémarrage est donc réparti sur trois couches** : la **décision** dans l'application (via
CAN), l'**état** dans l'EEPROM (champ + `byte_C89E`), et la **clé/graine** dans le boot primaire
(`unk_7EC8`). Aucune des trois n'est entièrement dans le dump.

---

## 10. Prochaines actions

1. **Format des freezes frames** dans `0xDC80-0xDCD0` (service 0x17, `word_DC90`/`byte_DC92`).
2. **En-tête `0xA5A5`** de `0xFC000` : décoder les 16 bits suivants.
3. **`sub_FE4AE`** (service 0x21 du boot) : la liste des « local identifiers » du boot — accès direct
   à la mémoire ?
4. **`byte_CF30` / `byte_CF31` / `word_FC10`** : les préconditions de sécurité (qui les pose ?).
5. **Les 4 sites `0xCFA4`** (commandes EEPROM dynamiques).
