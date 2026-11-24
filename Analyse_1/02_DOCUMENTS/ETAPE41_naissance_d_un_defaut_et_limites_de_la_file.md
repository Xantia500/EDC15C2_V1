# ÉTAPE 41 — Comment naît un défaut, et deux choses que je ne tranche pas

---

## 1. ★ La chaîne de détection : un **seuil de calibration** comparé à une valeur vive

Bloc `loc_A20xx`, l. 153330-153400. C'est la **première fois** que nous voyons un défaut se former.

### 1.1 Le seuil

```asm
                mov     r2, word_142A        ; ← HANDLE Datensatz (0x1400…0x1E2E)
                mov     r3, [r2]             ; ← valeur de calibration lue en flash
                cmp     r3, word_C908        ; ← comparée à une valeur VIVE
                jmpr    cc_NC, loc_A20D6     ; calibration >= mesure -> pas de défaut
                mov     r3, #80h
                or      word_CFD4, r3        ; ← bit 0x80 : condition détectée
                movb    byte_C2F5, ONES      ; ← marqueur
```

**`word_142A` est un handle** — donc `[word_142A]` lit **un seuil dans la calibration**
(`0xE0000 + valeur`). Le comparer à `word_C908` (valeur vive) est **exactement** l'usage attendu
d'un handle, et cela **valide une fois de plus** le modèle « handle = pointeur vers le Datensatz »
posé dès les premières étapes.

### 1.2 La mise en attente

```asm
loc_A20D6:
                mov     r4, word_CFD4
                jmpr    cc_Z, loc_A20EE
                movb    rl4, #1
                movb    byte_C2F6, rl4       ; « un défaut est en attente »
                mov     word_CFB6, ZEROS     ; index de parcours = 0
                movb    byte_CFDB, ZEROS
                movb    byte_CFDA, ZEROS
```

### 1.3 Le parcours de la mémoire des défauts

```asm
loc_A20EE:
                movb    rl4, byte_C2F6
                jmpr    cc_Z, loc_A2188
                mov     r12, word_CFB6
                mov     r13, #0CFBCh
                calls   9, sub_942CA         ; lit l'enregistrement courant -> 0xCFBC
                mov     word_CFB8, r4
                cmp     r4, #0FFFFh
                jmpr    cc_NZ, loc_A2134     ; trouvé
```

Puis, selon le verdict de `sub_A1E9E(0x80)` et `sub_A1E9E(0xFF)` :

```asm
                movbz   r12, byte_CFBE
                add     r12, #0EF00h         ; → SUPPRIMER le défaut n° byte_CFBE
                calls   9, sub_942DE
...
                movbz   r12, byte_CFBE
                add     r12, #0DF00h         ; → RELIRE le défaut n° byte_CFBE
                calls   9, sub_942CA
...
loc_A217E:
                sub     word_CFB6, ONES      ; décrémente l'index de parcours
```

### 1.4 Le statut recopié

```asm
                movb    rl7, byte_C2F4
                andb    rl7, #0FCh
                orb     rl7, byte_CFDB       ; 2 bits
                movb    byte_C2F4, rl7
                movb    rl7, byte_C2F3
                andb    rl7, #0FEh
                orb     rl7, byte_CFDA       ; 1 bit
                movb    byte_C2F3, rl7
```

**⇒ Chaîne complète, de bout en bout :**

```
seuil Datensatz (word_142A)  ──comparé à──  valeur vive (word_C908)
        ↓
word_CFD4 |= 0x80          (condition remplie)
        ↓
byte_C2F6 = 1              (défaut en attente)
        ↓
parcours word_CFB6 → 0xCFBC (enregistrement)
        ↓
suppression 0xEFxx  ou  relecture 0xDFxx  (numéro dans byte_CFBE)
        ↓
byte_C2F4 (2 bits) / byte_C2F3 (1 bit)   (statut publié)
```

C'est la réponse à une question laissée ouverte depuis longtemps : **un défaut naît d'une comparaison
seuil/mesure, pas d'une table**.

---

## 2. La grappe `0xCF9A-0xCFDF` : **partagée**, mais je ne conclus pas au « pont »

Déclarations contiguës :

```
byte_CF9A CF9B CF9C CF9D | word_CF9E | byte_CFA0 | ... | word_CFA8 | word_CFAA
word_CFAC CFAE CFB0 CFB2 CFB4 CFB6 CFB8 | word_CFBC | byte_CFBE CFBF | byte_CFC2 C3 C4
word_CFD4 CFD6 ...
```

Deux familles y cohabitent :

- **gestion des blocs EEPROM** : `word_CF9E`, `byte_CFA0` (index de la table `0x0BA6`, étape 30),
  `word_CFAA`, `word_CFAC` ;
- **mémoire des défauts** : `word_CFB6` (index), `word_CFBC` (tampon), `byte_CFBE` (numéro),
  `word_CFD4` (bits de condition), `word_CFD6/CFD8`.

**Fait** : les deux familles occupent la même grappe et sont écrites depuis **la même région de code**
(`EA ≈ 0xA1Fxx-0xA21xx`). **Ce que je ne conclus pas** : qu'il existe un lien fonctionnel. Une
allocation de variables de travail par le même module suffit à expliquer la proximité. **À ne pas
présenter comme un pont entre EEPROM et défauts.**

---

## 3. `sub_8F22E` : initialisation du bloc `0xF608-0xF61F` — et une unité que je ne tranche pas

```asm
sub_8F22E:
                mov     word_F610, ZEROS
                movb    byte_F608, ZEROS
                mov     r4, #0FFh
                mov     word_F612, r4
                movb    byte_F609, rl4
                ...
                movb    rl5, #28h ; '('
                movb    byte_F60B, rl5
                ...
                movb    word_F60C, ZEROS
                movb    rl5, #14h
                movb    word_F60C+1, rl5     ; → word_F60C = 0x1400
                ...
                movb    word_F60E, ZEROS
                mov     r5, #0FFh
                movb    word_F60E+1, rl5     ; → word_F60E = 0xFF00
```

Valeurs posées : `word_F608..F61F` = `{0x0000, 0x00FF, 0x0000, 0x00FF, 0x0000, 0x00FF, 0x0000,
0x00FF}` aux mots pairs, et les octets `F608=00, F609=FF, F60A=00, F60B=28`, plus **`word_F60C =
0x1400`**, **`word_F60E = 0xFF00`**, **`word_F610 = 0x0000`**.

**Ce qui est établi** : ces trois mots sont bien les **bornes de la file de 4 octets** de `sub_94C78`
(étape 40 §4) — même adresse, même usage (`base`, `limite`, `curseur`).
**Ce que je ne tranche pas** : leur **unité**. `0x0000` / `0xFF00` / `0x1400` ne sont pas des adresses
RAM cohérentes avec un tampon de quelques dizaines d'octets, et le test de rebouclage
(`base + 4 == curseur`) ne s'applique pas à ces valeurs. Deux lectures possibles — **adresse dans
une page sélectionnée par DPP**, ou **segment:offset** — et je n'ai **aucune preuve** pour l'une
plutôt que l'autre. Je laisse ouvert.

*Note* : `byte_F608` est bien celui du verdict de configuration (étape 36) — il est remis à zéro ici,
ce qui est cohérent avec une initialisation de démarrage.

---

## 4. Tableau de bord

| question | état |
|---|---|
| naissance d'un défaut | **seuil Datensatz vs valeur vive** ✔ |
| handle `word_142A` | **confirme le modèle handle → flash** ✔ |
| parcours / suppression / relecture | `word_CFB6`, `byte_CFBE`, `0xEFxx`/`0xDFxx` ✔ |
| statut publié | `byte_C2F4` (2 bits), `byte_C2F3` (1 bit) ✔ |
| grappe `0xCF9A-0xCFDF` | partagée EEPROM + défauts — **lien fonctionnel non prouvé** |
| bornes de la file | valeurs connues (0, 0xFF00, 0x1400), **unité inconnue** |
| antidémarrage | non localisé |

---

## 5. Prochaines actions

1. **`sub_A1E9E`** : c'est lui qui décide, pour un enregistrement donné, entre *supprimer* et
   *relire*. C'est le **cœur de la logique de défaut** — priorité.
2. **`byte_CFDB` / `byte_CFDA`** : les 3 bits de statut publiés → remonter à qui les lit
   (probablement l'allumage du voyant et le mode dégradé).
3. **`word_CFD4`** : la carte des bits de condition — combien de moniteurs, lesquels.
4. **Antidémarrage** : angle « inhibition » — chercher un test de drapeau qui force la **quantité
   injectée à zéro** (et non un échange d'authentification).
