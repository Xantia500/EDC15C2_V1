# ÉTAPE 114 — `sub_AF75A` : un filtre conditionnel, pas une quantification

Suite de l'Étape 113. Le maillon `182853 D9A6 = sub_AF75A(D9A6)` est **entièrement décodé**.

---

## 1. Le corps de la fonction (complet, 20 instructions)

```asm
sub_AF75A:                          ; CODE XREF: seg015:2F6A↓P  (= l.182854)
    mov  [-r0], r9
    mov  r9, r12                    ; r9 = valeur d'entrée (l'IQ de la cascade)
    movb rl4, byte_C2C0
    cmpb rl4, #4
    jmpr cc_NZ, loc_AF790           ; ★ PORTE 1 : codage C2C0 doit valoir 4
    movb rl5, byte_C227
    andb rl5, #2
    jmpr cc_Z, loc_AF790            ; ★ PORTE 2 : bit 1 de C227 doit être à 1
    jnb  word_FD16.13, loc_AF77C
        mov  word_D8C2, r9          ; ★★ référence = entrée courante
        mov  word_D8C0, ZEROS       ; ★★ reset de l'état du filtre
        bclr word_FD16.13           ; ★ armement
loc_AF77C:
    mov  r12, word_1A96             ; handle calibration du filtre
    mov  r13, r9                    ; X = entrée
    mov  r14, #0D8C0h               ; destination = D8C0 (état D8C0 / sortie D8C2)
    calls 0, unk_1E50               ; ★ filtre (routine bibliothèque)
    mov  r4, word_D8C2              ; ★ sortie = valeur filtrée
    jmpr cc_UC, loc_AF794

loc_AF790:
    bset word_FD16.13               ; désarmement : au retour, on réinitialisera
    mov  r4, r9                     ; ★★ PASSE-PLAT : entrée rendue telle quelle

loc_AF794:
    mov  r9, [r0+]
    rets                            ; retour = r4
```

## 2. Ce que fait réellement la fonction

| aspect | conclusion | preuve |
|---|---|---|
| nature | **filtre à état** (lissage), pas une quantification | état `D8C0` persistant + sortie `D8C2` |
| condition d'activation | **`byte_C2C0 == 4`** ET **`(byte_C227 & 2) != 0`** | l.178614-178619 (code ci-dessus) |
| sinon | **passe-plat strict** (`r4 = r9`) | `loc_AF790` |
| réinitialisation | quand `FD16.13` est **armé**, on recopie l'entrée dans la sortie et on remet l'état à 0 ⇒ **pas de rampe au réengagement** | `jnb word_FD16.13` |
| paramétrage | `word_1A96` → `0xE7FF2` | dump handle |

⇒ **Ce n'est pas l'arrondi d'injection.** C'est un **lissage optionnel de l'IQ finale**, propre à
une **variante de codage** (`C2C0 == 4`).

## 3. `unk_1E50` : routine de bibliothèque non désassemblée

```asm
unk_1E50:  ds 1   ; CODE XREF: sub_9C56A+1E2↓P, seg014:D2AC↓P, sub_AF75A+30↓P, ...
```

C'est un **stub** (la zone bibliothèque n'est pas dans le dump — même limite que les checksums).
Sa **signature** est en revanche constante sur tous ses appelants :

```
unk_1E50(r12 = handle de calibration, r13 = X, r14 = adresse de destination)
   → écrit 2 mots consécutifs à [r14] et [r14+2]
```

C'est exactement le schéma d'un **filtre du 1er ordre dont la constante de temps est une courbe** :
`[dest]` = état interne, `[dest+2]` = sortie filtrée. On retrouve le même schéma à l'Étape 110
(`unk_1E50(word_1A98, C91C, &D8C8)` → `D8C8`/`D8CA`).

**Paramètres du filtre de `sub_AF75A`** : `word_1A96 → 0xE7FF2` = `01 00 | 00 40 | …` ; le mot lu
est **`0x4000`** (16 384). Le handle voisin `word_1A98 → 0xE7FF4` donne **`0x0302`** (770).
*(format de description non encore tranché — les deux handles pointent à 2 octets d'écart, donc sur
deux mots d'un même descripteur.)*

## 4. Les deux portes, et ce qu'elles valent ici

- **`byte_C2C0`** : octet de **codage variante**, lu 10 fois. Le code le compare à **`1`**
  (l.163017, l.163143, l.178618) et à **`4`** (ici). C'est donc un sélecteur de variante à plusieurs
  valeurs, et non un booléen.
- **`byte_C227` bit 1** : `C227` est écrit par `seg013:loc_99828` (l.135629), donc par la chaîne
  **CAN / entrées** — un état externe au groupe motopropulseur.

**Dans ce dump, la variante par défaut n'est pas `4`** : le bloc de codage `0xE111E` (word_141C)
commence par `00 01 01 00 00 01 00 01 …`, et toutes les autres lectures de `C2C0` dans le code
attendent `1`. ⇒ **`sub_AF75A` est très probablement INACTIF** sur cette calibration, et
`D9A6` traverse la cascade sans filtrage.

> ⚠ À confirmer par log : si `D8C2` reste à 0 alors que `D9A6` bouge, le filtre est bien inactif.

## 5. Conséquence sur la lecture de la cascade (Étape 113 corrigée)

La cascade est donc, en pratique, **8 opérations de clamp pur** :

```
D9A6 = C6A6 [+ C69E si D9AC == 1]
C6B8 = D9A6                      (sauvegarde)
  plancher C680 = C698           ← régulateur
  plafond  C67E (0x7FFF, inactif)
  plafond  C696 (0x7FFF, inactif)
C6A4 = D9A6
  plancher C688
  plafond  C682
  plafond  C6C0 (0x7FFF, inactif)
  [filtre sub_AF75A — inactif sauf codage C2C0 == 4]
  plancher C686
  plafond  C684
C6B2 = D9A6                      (sortie)
```

Aucune non-linéarité cachée : ce qui entre dans `C6B2`, c'est le souhait **borné** par les
limiteurs. C'est ce qui rend la cartographie des limiteurs (`C680`, `C684`, `C686`, `C688`, `C682`)
**directement actionnable**.

## 6. Ce qu'il faut loguer pour valider

| variable | rôle |
|---|---|
| `D9A6` → `C6B2` | IQ finale de la cascade |
| `C6B8` | souhait brut, avant limiteurs |
| `C6A4` | après les 3 premiers limiteurs |
| `C680` | plancher = demande du régulateur (`C698`) |
| `D8C2` | sortie du filtre — **reste à 0 si `C2C0 != 4`** |
| `byte_C2C0` / `byte_C227` | les deux portes du filtre |

## 7. Suite

1. **`unk_1E50`** : impossible à décoder ici (bibliothèque absente). On peut en revanche en déduire
   la constante de temps par mesure : si `C2C0 == 4` un jour, comparer `D8C2` à `D9A6` sur un échelon.
2. **Les limiteurs réels `C682` / `C688`** (l.180333, 180409, 181239, 181315) — ce sont eux qui
   brident, avec la tâche couple seg014 (`C684`/`C686`). Prochain chantier logique.
3. **Le lien aval vers la durée d'injection** : qui lit `C6AE` / `C6AA` / `C6B2` ?
