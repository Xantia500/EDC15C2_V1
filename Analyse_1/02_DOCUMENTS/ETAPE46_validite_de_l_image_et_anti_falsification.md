# ÉTAPE 46 — ★ `byte_C2EC` : la validité de l'image, et le **vrai** mécanisme anti-falsification

---

## 1. ★ `byte_C2EC` = **deux bits**, et ils décident de la validité de l'image EEPROM

`byte_C2EC` n'est écrit que **deux fois** dans tout le listing, mais **lu par 10 fonctions** — dont
les deux voies EEPROM. C'est donc un **état global**, pas un compteur.

### Écriture n°1 — « image valide » (l. 152021-152024)

```asm
                mov     r4, word_CFAA
                jmpr    cc_NZ, loc_A1564
                movb    rl4, #1
                orb     byte_C2EC, rl4          ; byte_C2EC |= 1
```

**Condition : `word_CFAA == 0`.** Or `word_CFAA` appartient à la grappe `0xCF9A-0xCFDF`
(étape 41 §2) — c'est-à-dire **le domaine de l'EEPROM**. Et il n'est écrit qu'aux lignes
**149916** (`= 0`) et **149922** (`= r4`), c'est-à-dire **dans le module `sub_A0002` lui-même**.

⇒ **`word_CFAA` = état de l'opération EEPROM en cours. Nul ⟹ l'image est saine.**
⇒ **`byte_C2EC` bit 0 = « l'image EEPROM est valide, utilisez-la ».**

### Écriture n°2 — « image vierge » (l. 111754)

```asm
loc_90618:
                mov     r0, #170h
                mov     word_DDFA, r0
                movb    rl0, #2
                movb    byte_C2EC, rl0          ; byte_C2EC = 2   (bit 1, PAS bit 0)
```

Atteint lorsque **`word_DE22 ∈ {0x28, 0x29, 0x2A, 0x2B}** (l. 111738-111746).

⇒ **`byte_C2EC` bit 1 = « forcer les valeurs par défaut »**. C'est le chemin **vierge / usine**.

**`byte_C2EC` est donc un champ de 2 bits : `bit 1` = forcer les défauts, `bit 0` = image valide.**
C'est exactement le mécanisme qu'utilise un **télécodage** ou un calculateur **neuf**.

---

## 2. ★ Ce que fait le bit 0 : il **saute l'initialisation par défaut**

Cinq sites testent `byte_C2EC & 1`, et **tous les cinq** ont la même forme :
*si le bit est nul → écrire les valeurs par défaut ; s'il est à 1 → ne rien faire.*

| ligne | si bit 0 = 0 (image non valide) on écrit |
|---|---|
| **154442** | `word_C5BE = 0x7FFF`, `word_C5C0 = 0x7FFF`, `word_C5F4 = 0` |
| **160911** | **`word_C5D2 = word_C5D4 = word_C5D6 = 0xFA`** |
| **167312** | `word_C58C`, `word_C5A6`, `word_D7F6`, `word_C5EE`, `word_C5F2`, `word_C5EA`, `word_C5F6` → **0** |
| **213355** | `word_C3A6 = 0` |
| **210888** | recopie dans **`word_FD18.15`** (drapeau d'interruption) |

```asm
154439:  movb  rl4, byte_C2EC
         andb  rl4, #1
         jmpr  cc_NZ, loc_A2D16        ; bit 0 = 1  -> ON SAUTE
         mov   r4, #7FFFh              ; bit 0 = 0  -> DEFAUTS
         mov   word_C5BE, r4
```

**Et les variables concernées sont précisément les champs EEPROM de l'étape 30**
(`C5BE`/`C5C0` groupe `word_D26` ; `C5D2…C5DA` groupe `word_C1E` ; `C5EE`/`C5F2`/`C5EA`/`C5F6`
groupe `word_D1A` ; `C5EC`/`C5E4`/`C5F4`/`C5B8`/`C5F0` groupe `word_D4A`).

⇒ **Le calculateur possède une table de valeurs par défaut pour ses champs permanents, et un seul
bit décide s'il l'applique.** Voilà le `byte_C2EC` : **le commutateur « mémoire vierge / mémoire
exploitée »**.

**Deux valeurs par défaut remarquables :**
- **`0x7FFF`** = sentinelle « pas de limite » (mot le plus grand signé positif) ;
- **`0xFA` = 250** — et 250 est précisément l'une des deux valeurs que tu avais posées pour la
  **Vmax (240 ou 250 ?)**. **Première apparition de la constante 250 dans un contexte fonctionnel.**
  Je le signale comme **piste**, pas comme réponse : rien n'établit encore l'unité.

---

## 3. ★ Le mécanisme anti-falsification **n'est pas un checksum** — c'est un historique

C'était la question ouverte depuis longtemps : « il y a des checksums, et peut-être de la
redondance ». **Le checksum reste introuvable (7 algorithmes testés sans succès, étape 39).** Mais
voici ce qui **tient lieu** de protection, et c'est beaucoup plus solide.

### Le registre à 5 niveaux (l. 161143-161152)

```asm
                mov     r4, word_C5D8
                mov     word_C5DA, r4        ; C5DA <- C5D8
                mov     r5, word_C5D6
                mov     word_C5D8, r5        ; C5D8 <- C5D6
                mov     r2, word_C5D4
                mov     word_C5D6, r2        ; C5D6 <- C5D4
                mov     r3, word_C5D2
                mov     word_C5D4, r3        ; C5D4 <- C5D2
                mov     r1, word_D788
                mov     word_C5D2, r1        ; C5D2 <- valeur du moment
```

**Cinq mots consécutifs `C5D2, C5D4, C5D6, C5D8, C5DA` = les cinq dernières valeurs**, décalées à
chaque mise à jour. Et **ces cinq mots sont persistés** (groupe `word_C1E` de l'étape 30) : **l'historique survit à la coupure du contact.**

### La moyenne (l. 161157-161179)

```asm
                mov     r4, word_C5D2
                ...                                  ; somme des 5 en 32 bits
                add     r4, r10                      ; (répété 5 fois)
                mov     [r0+#8], r4
                mov     [r0+#0Ah], r5
                mov     r12, r5
                mov     r13, r4
                mov     r14, #5
                calls   9, sub_97DDC                 ; division
                mov     word_C5AE, r4                ; moyenne des 5
```

### La comparaison aux seuils de calibration

| ligne | comparaison | conséquence |
|---|---|---|
| **162157** | `[word_18F2 + 0x14]` vs **`word_C5AE`** (la moyenne) | `word_FD0A.11` |
| **162350** | `[word_18F2 + 0x38]` vs `word_C5B8` | `word_FD0A.9` |
| **156051** | `[word_1474 + 0x6]` vs `word_C5B8` | **décompte `word_D6FE`**, puis `byte_C317 |= 1` |
| **162339** | `word_C5B8` vs `word_C5E2` | branche d'état |

```asm
162150:  mov   r4, word_18F2
         mov   r5, [r4+#14h]
         cmp   r5, word_C5AE          ; seuil de calibration  vs  MOYENNE
         jmpr  cc_UGT, loc_A75D0
```

**⇒ Voilà la vraie protection :**

```
valeur courante  →  (persistée en EEPROM)  ─┐
                                            ├→  historique 5 niveaux (persisté)
                                            └→  moyenne  ─→ comparaison à [handle+0x14]
                 └→  comparaison à [handle+0x38], [handle+0x6]
                 └→  décompte word_D6FE  ─→  byte_C317
```

**On ne peut pas falsifier une valeur sans falsifier simultanément son historique de 5 valeurs et sa
moyenne**, elles-mêmes persistées, et sans franchir plusieurs seuils de calibration **dont les
valeurs sont dans le Datensatz** — donc **hors de l'EEPROM**. C'est plus difficile à contourner qu'un
checksum.

---

## 4. Convergence inattendue : **les structures de calibration partagent leur plan**

| structure | offset | rôle |
|---|---|---|
| `word_142A` | **+0** | seuil n°1 |
| | **+2** | incrément (borne) |
| | **+4** | autorisation (`0xFFFF` = inhibé) |
| | **+6** | **seuil n°2** |
| `word_1474` | `+1A` | (usage non décodé) |
| | **+6** | **seuil — comparé à `word_C5B8`** |
| `word_18F2` | `+14` | seuil — comparé à la moyenne |
| | `+38` | seuil — comparé à la valeur |

**Deux structures différentes (`word_142A`, `word_1474`) portent un seuil à `+6`.** Ce n'est
probablement pas un hasard : **les descripteurs de calibration ont un en-tête commun**, puis divergent
(`+0x14`, `+0x38`…). C'est la première indication d'un **format de descripteur partagé** — et cela
renforce beaucoup le modèle « identité + type + tag ».

**`word_18F2`** est à rapprocher de **`word_18F6`** et **`word_1952`** (pistes laissées ouvertes
depuis longtemps) : même famille d'adresses, même usage « handle → champ de calibration ».

---

## 5. Ce que je n'établis pas

- **La grandeur physique mesurée par `word_C5B8`.** Éléments contraignants : persistée en EEPROM,
  historisée sur 5 valeurs, moyennée, comparée à ≥3 seuils, défaut = **250**, et entourée d'un
  compteur d'état `byte_C30D` (borné entre 2 et 7) et d'un décompte `word_D6FE`.
  **Candidats** : niveau d'additif, masse de suie, kilométrage interne, niveau de service.
  **Aucun n'est retenu** : la valeur par défaut 250 exclut un kilométrage, et rien ne permet de
  trancher entre les autres.
- **La correspondance bit ↔ option** : toujours dans la couche absente (étape 45 §6).
- **L'emplacement du PIN, du VIN, de l'immo** : toujours hors d'atteinte.

---

## 6. Prochaines actions

1. **`word_18F2`** : localiser son handle dans le Datensatz (`outils/ea2handle.py`) et **lire les
   valeurs à `+0x14` et `+0x38`**. Si ce sont des seuils plausibles, cela identifiera la grandeur.
   **C'est l'action la plus rentable** : elle transforme une comparaison en mesure réelle.
2. **`word_1474`** : même méthode, lecture de `+0x6`.
3. **`byte_D6FE` / `byte_C30D`** : la machine d'état autour de `word_C5B8` — combien d'états, quelle
   progression.
4. **`word_FD0A`** : les bits 9, 11, 12 — que déclenchent-ils en aval ?
