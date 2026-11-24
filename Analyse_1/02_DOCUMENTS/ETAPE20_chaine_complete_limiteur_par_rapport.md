# ÉTAPE 20 — LA CHAÎNE EST TROUVÉE : le limiteur de couple par rapport, de bout en bout

## 0. Erratum majeur — j'avais tort, et voici pourquoi

Aux étapes 18 et 19 j'ai conclu que tes cartes n'étaient « pas consommées ». **C'est faux, et je le
corrige sans ambiguïté.** L'erreur venait d'une hypothèse non vérifiée : j'ai supposé que la table
des handles du Datensatz s'arrêtait à **666 mots** (`word_1400 … word_1932`). **Elle continue.**

Ce que j'avais appelé « répertoire à `0xE1B16`, 212 entrées » n'est rien d'autre que **la suite de
cette même table de handles** : `word_1B16`, `word_1B18`, … Tes cartes sont donc référencées, par
des handles parfaitement normaux :

| handle | cible | carte |
|---|---|---|
| `word_1B3E` | `EA 0xE83F4` | **main torque limiter** (courbe 19 pts) |
| `word_1B40` | `EA 0xE8444` | **smoke map** (régime × air, grille 16×16) |
| `word_1B54` | `EA 0xE8906` | **1ʳᵉ** |
| `word_1B56` | `EA 0xE8946` | **2ᵉ** |
| `word_1B58` | `EA 0xE8986` | **3ᵉ** |
| `word_1B5C` | `EA 0xE89FA` | courbe 2 points `635 / 680` (valeur de repli) |
| `word_1B5E` | `EA 0xE8A06` | carte (régime × `word_D9AA`) → `byte_C8F8` |
| `word_1B64` | `EA 0xE8B10` | **4ᵉ** |

Mon erreur était donc une erreur de **méthode**, pas de mesure : j'ai cherché une adresse alors que
le code ne manipule que des **numéros de handle**. Leçon retenue pour la suite : toute recherche de
consommateur doit partir des `word_1xxx`, jamais des `0xExxxx`.

## 1. Le bloc de sélection, verbatim (l. 183011-183065)

```asm
l.183011  movbz r4, byte_C330
l.183014  and   r4, #80h
l.183016  jmpr  cc_Z, loc_B3116
l.183018  mov   r12, word_1B5C          ; bit 7 → courbe de repli pour tous les rapports
l.183022  ...   r13 = word_C91C ; calls unk_1D36 ; word_D9A2 = r4

loc_B3116:
l.183022  movb  rl4, byte_C330
l.183024  andb  rl4, #0Fh               ; ← NIBBLE BAS = RAPPORT ENGAGÉ
l.183026  subb  rl4, #1
l.183028  cmpb  rl4, #0Bh
l.183030  jmpr  cc_UGT, loc_B318C       ; > 11 → PAS de limitation par rapport
l.183031  movbz r4, rl4 ; shl r4,#1 ; add r4,#0A62h ; mov r4,[r4] ; jmpi cc_UC,[r4]
             cas 1 → word_1B54 (1ʳᵉ) , r13 = word_C91C , calls unk_1D36 → word_D9A2
             cas 2 → word_1B56 (2ᵉ)   (idem)
             cas 3 → word_1B58 (3ᵉ)   (idem)
             cas 4 → word_1B64 (4ᵉ)   (idem)
             cas 5 → word_1B5C        (idem)
loc_B318C:  word_D9A2 = word_D9A8       ; repli : aucune limitation par rapport
loc_B3194:  word_D3EC = word_D9A2       ; ← publication dans la chaîne d'injection
```

**Confirmation de ta description, mot pour mot** : X = **`word_C91C` = le régime**. Il est fabriqué
juste avant, à la ligne 139690 (`sub_9AE42`) : `mov r4, word_C42E ; mov word_C91C, r4`. La sortie de
la courbe choisie va dans `word_D9A2`, puis `word_D3EC`.

Note importante : la même fonction passe aussi `word_D9A2` dans un **écrêtage** juste avant
(l. 183032-183050 : comparaison à `word_C62C` puis à `word_D9A0`), donc la valeur publiée dans
`word_D3EC` est `min(courbe_de_rapport, plafonds)`.

## 2. D'où vient le rapport — la réponse est complète

### 2.1 `byte_C330 & 0x0F` = code de rapport

Deux écrivains seulement dans tout le programme :

- **remise à zéro** (l. 177450) : `mov r5, word_1B26 ; movb byte_C330, [r5]` — et `word_1B26`
  pointe sur `EA 0xE837C` dont le **premier octet vaut `00`** ⇒ au démarrage, rapport = 0 ⇒ le
  sélecteur prend le repli `loc_B318C` ⇒ **aucune limitation par rapport**. C'est cohérent.
- **calcul** (l. 178003) : `mov r4, r9 ; movb byte_C330, rl4`, où `r9` vient de
  `movb rl5, [word_1B22 + k] ; movbz r9, rl5`.

### 2.2 La table de traduction des rapports

`word_1B22` → **`EA 0xE835A`**, contenu :
`30 01 02 03 04 00 00 00 00 0B 00 00 00 00 00 C3`

| index `k` | 0 | 1 | 2 | 3 | 4 | 5-8 | 9 | >14 |
|---|---|---|---|---|---|---|---|---|
| code rapport | `0x30` | 1 | 2 | 3 | 4 | 0 | `0x0B` (inconnu) | `0x30` |

Et l'index `k` est **`byte_C240 & 0x0F`** (l. 177545-177556), avec `cmpb rl4, #0Eh` et une table de
sauts en `#0A2Ch` — donc **0 à 14 rapports possibles**, ce qui couvre largement une boîte 6.

### 2.3 `byte_C240` = l'indicateur de rapport calculé

Quatre écrivains, l. 139477, 140993, 141203, 141208 :

- trois fois : `movb rl5, [r4+#8]` avec `r4 = word_1658` ⇒ **valeur de calibration** (valeur par défaut) ;
- une fois (l. 141199-141208) :
  ```asm
  cmpb  rl6, #0Fh
  jmpr  cc_NZ, loc_9B9A6        ; si rl6 ≠ 0x0F → on garde la valeur calculée
  mov   r4, word_1658 ; movb rl5, [r4+#8] ; movb byte_C240, rl5   ; sinon → défaut calibré
  loc_9B9A6:
  movb  byte_C240, rl6          ; ← LA VALEUR CALCULÉE
  loc_9B9AA:
  movbz r4, byte_C872           ; ← variable lue immédiatement après
  ```

⇒ **Il existe bien un rapport engagé calculé**, et il est produit dans **`sub_9B796`** (la fonction
qui contient la ligne 141199). `0x0F` est le code « inconnu », remplacé par le défaut de
calibration — exactement la structure d'un indicateur de rapport avec repli.

## 3. La chaîne complète, désormais établie

```
impulsions vitesse  ──►  ???                       (à trouver : sub_9B796)
        │
word_C42E (régime) ──► word_C91C ──┐
                                   ▼
                    byte_C240 & 0x0F  ──►  table 0xE835A  ──►  byte_C330 & 0x0F
                                                                     │
                       ┌─────────────────────────────────────────────┘
                       ▼   table de sauts 0x0A62
   word_1B54/56/58/64 (1ʳᵉ/2ᵉ/3ᵉ/4ᵉ) ──► unk_1D36(handle, régime) ──► word_D9A2
   word_1B5C (repli)  ─────────────────►                             │
   (rapport > 11) ──► word_D9A2 = word_D9A8                         │
                                                                     ▼
                                                     écrêtage (C62C / D9A0) → word_D3EC
                                                                     │
                                                          chaîne d'injection
```

Et le **main torque limiter** (`word_1B3E` → `0xE83F4`, utilisé l. 182008) et la **smoke map**
(`word_1B40` → `0xE8444`, utilisée l. 181911 et 181947) sont bel et bien dans cette même chaîne :
`word_1B40` est passée à `unk_1D50` avec **régime × air**, ce qui recoupe le §2 de l'étape 19.

## 4. Le prochain objectif, précis

**`sub_9B796`** (dans `seg013`, autour de la ligne 141199). C'est la fonction qui produit
`byte_C240` — donc celle qui **compare le régime à la vitesse** pour en déduire le rapport. Deux
choses à y chercher :

1. la **division** (ou la multiplication croisée) entre le régime et une variable d'impulsions :
   le diviseur *est* la vitesse ;
2. la variable **`byte_C872`**, lue immédiatement après l'écriture de `byte_C240` (l. 141210) :
   elle est candidate au rôle de grandeur de vitesse elle-même.

C'est le dernier chaînon, et il est maintenant borné à **une seule fonction**. Je m'y attelle.
