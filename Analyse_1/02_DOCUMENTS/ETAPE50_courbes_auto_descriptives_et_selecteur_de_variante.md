# ÉTAPE 50 — ★★★ Les courbes **nomment leur variable**, et le sélecteur de variante est piloté par le CAN

---

## 1. ★★★ Un en-tête de courbe 1-D contient **l'adresse de sa variable d'entrée**

`word_18AA` → EA `0xE4D9C`. Contenu brut :

```
+0x00  A8 C5  08 00  14 05  D0 07  B8 0B  A0 0F  70 17  58 1B  28 23  F8 2A
+0x14  00 00  00 00  00 00  0F 00  0F 00  0F 00  0F 00  0F 00
```

**Décodage, et il tombe juste à l'octet :**

| offset | contenu | lecture |
|---|---|---|
| `+0x00` | **`0xC5A8`** | **l'adresse de `word_C5A8`** — la variable d'entrée |
| `+0x02` | `8` | nombre de points `n` |
| `+0x04` … `+0x13` | `1300, 2000, 3000, 4000, 6000, 7000, 9000, 11000` | **l'axe** (8 mots) |
| `+0x14` … `+0x23` | `0, 0, 0, 15, 15, 15, 15, 15` | **les valeurs** (8 mots) |

**La taille qui en résulte est `4 + 4n` octets = `4 + 32` = 36 = `0x24`.**
**Et la différence entre les pointeurs de `word_18AA` et `word_18AC` est exactement `0x24`.**

⇒ **La structure d'une courbe 1-D est `[adresse de la variable][n][axe…][valeurs…]`, et sa taille est
calculable.** C'est la **cinquième** validation indépendante du découpage du Datensatz (étapes 48-49).

### Pourquoi c'est important

**C'est la réponse directe à la question posée au tout début** : « adresse = identité + type + tag ».
En réalité, le Datensatz est **auto-descriptif** : **chaque courbe porte l'adresse mémoire de la
variable qu'elle traite.** Le firmware n'a donc pas besoin de « savoir » à quoi correspond une courbe —
**la courbe le dit**.

Deux conséquences pratiques immédiates :

1. **On peut nommer automatiquement les courbes** : il suffit de lire le premier mot et de le rapprocher
   des variables déjà identifiées. C'est une **méthode d'annotation automatique du Datensatz**.
2. **`word_18AA` et `word_18AC` traitent tous deux `word_C5A8`** — ce sont bien les **deux bornes d'une
   fenêtre sur la même grandeur**, ce que l'étape 49 §1 déduisait du code.

*Réserve honnête* : les 36 premiers octets de `word_18AA` et de `word_18AC` sont **identiques** dans
les octets que j'ai lus (même en-tête, même axe, mêmes valeurs `0/15`). Le bloc de `word_18AC`
contient ensuite une **seconde entrée** commençant à `+0x24` (en-tête `0xC5A8`, `n=8`, axe
**`500, 2000, 3000, 4000, 6000, 6283, 9000, 11000`**, valeurs **`254, 481, 627, 743`** …). **Je
n'explique pas encore cette duplication** : ce peut être un couple (basse/haute) ou un artefact de
découpage. **Non tranché.**

---

## 2. ★★★ `[word_18B2 + 0x12]` : un **masque de bits de variante**, sélectionné par le CAN

C'est la découverte la plus importante de cette étape. Code l. 155300-155375 :

```asm
                mov     r4, word_18B2
                movb    rl5, [r4+#12h]        ; ← OCTET DE MASQUE dans le Datensatz
                andb    rl5, #4
                jmpr    cc_NZ, loc_A3558      ; bit 2 → cas A
loc_A34F2:
                movb    rl4, word_FD38
                jmpr    cc_Z, loc_A3506
                mov     r4, word_18B2
                movb    rl5, [r4+#12h]
                andb    rl5, #8
                jmpr    cc_NZ, loc_A3558      ; bit 3 → cas A   (si word_FD38 ≠ 0)
loc_A3506:
                movb    rl4, word_FD38+1
                ...
                andb    rl5, #10h             ; bit 4 → cas A   (si word_FD38+1 ≠ 0)
loc_A351A:
                movb    rl4, word_FD7A
                ...
                andb    rl5, #20h             ; bit 5 → cas A   (si word_FD7A ≠ 0)
loc_A352E:
                movb    rl4, word_FD7A+1
                ...
                andb    rl5, #40h             ; bit 6 → cas A   (si word_FD7A+1 ≠ 0)
loc_A3542:
                movb    rl4, word_FD7C
                ...
                andb    r5, #80h              ; bit 7 → cas A   (si word_FD7C ≠ 0)
loc_A3558:
                mov     r4, word_18B2
                mov     r5, [r4+#14h]
                mov     word_D1BE, r5         ; ┐
                mov     r2, [r4+#16h]
                mov     word_D1BA, r2         │ quatre valeurs de calibration
                mov     r3, [r4+#18h]
                mov     word_D1B2, r3         │ chargées d'un bloc
                mov     r9, [r4+#1Ah]
                mov     word_C5A8, r9         ; ┘ dont la 4ᵉ est word_C5A8
loc_A358C:
                movb    byte_C308, ZEROS      ; sinon : on ne charge RIEN
```

### Décodage

- **`[word_18B2 + 0x12]` = un octet de masque**, dont les **bits 2 à 7** sont testés ;
- **chaque bit est « armé » par un drapeau différent** : `word_FD38`, `word_FD38+1`, `word_FD7A`,
  `word_FD7A+1`, `word_FD7C` — tous dans la zone **`0xFDxx`**, c'est-à-dire les **drapeaux de trames
  CAN** déjà identifiés ;
- **si le bit correspondant est posé, on charge le groupe de quatre valeurs `+0x14, +0x16, +0x18,
  +0x1A`** ; sinon **rien n'est chargé** (`byte_C308 = 0`, l. 155387) ;
- `byte_C308` = **le drapeau « valeurs de variante chargées »**.

**⇒ Le Datensatz contient jusqu'à SIX jeux de valeurs de variante, et c'est une trame CAN qui décide
lequel s'applique.**

### ★★ C'est le mécanisme de codage de la configuration véhicule — côté calculateur

Tu avais posé : *« la présence du régulateur, de la clim, etc. est codée dans l'EEPROM »*. **Voilà une
seconde moitié du mécanisme, et elle est plus directe :**

```
Lexia / Diagbox  →  code le BSI  →  trame CAN  →  word_FD38 / FD7A / FD7C
                                                  ↓
                              [word_18B2 + 0x12] : quel bit est autorisé
                                                  ↓
                     groupe de valeurs +0x14/+0x16/+0x18/+0x1A du Datensatz
                                                  ↓
                                           word_C5A8, word_D1B2/BА/BE
                                                  ↓
                                  courbes de surveillance → états → défauts
```

**Le Datensatz porte les valeurs ; le CAN porte le choix.** Et cela **n'exclut pas** un miroir en
EEPROM (étape 45) : les deux peuvent coexister — la configuration reçue serait **recopiée** dans
l'enregistrement persistant, ce qui est exactement ce que fait un calculateur qui doit retrouver sa
configuration au prochain contact sans attendre le BSI.

**Je ne prétends pas que ce soit démontré** : ce que je montre, c'est que **la sélection par le CAN
existe, est lue dans le Datensatz, et pilote des valeurs de travail**. Le lien vers le régulateur ou la
clim n'est **pas** établi.

---

## 3. Ce que devient `word_C5A8` — et ce que les valeurs suggèrent

`word_C5A8` = **la quatrième valeur** du groupe de variante (`+0x1A`), et **l'entrée commune des deux
courbes de surveillance**.

L'axe des courbes est **`1300, 2000, 3000, 4000, 6000, 7000, 9000, 11000`**, soit une plage
**1300 → 11000**. Deux lectures possibles, et **une seule tient bien** :

- si l'axe est en **mg/s**, la plage est 1300…11000 mg/s, soit 4,7 à 40 kg/h — **plausible pour un
  débit d'air**, mais faible en charge ;
- si l'axe est en **mg par tour ×10** (la convention que tu as posée pour les grandeurs internes),
  la plage est **130,0 à 1100,0 mg/tour** — et **tu avais donné ≈1000-1100 mg/tour en pleine charge**.

**La seconde lecture s'ajuste nettement mieux aux deux extrémités** : 130 mg/tour au ralenti,
1100 mg/tour à pleine charge. **Je la retiens comme hypothèse forte, pas comme preuve** — l'axe est
une donnée de calibration, et l'unité ne peut être tranchée que par comparaison avec une mesure.

**Et `word_C596`**, l'autre opérande de la comparaison, est chargé par `[word_1878 + 4]` avec un
**verrou** (`word_CFF2` mémorise, restauré si `word_FD78+1` est nul, l. 154276-154292).
⇒ **`word_C596` = une valeur de référence avec valeur de repli** : comportement typique d'une
**mesure avec valeur par défaut de calibration**.

---

## 4. Bilan

| question | état |
|---|---|
| format d'une courbe 1-D | **`[adresse variable][n][axe…][valeurs…]`**, taille `4+4n` ✔✔ |
| les courbes sont-elles auto-descriptives | **OUI** — elles nomment leur variable ✔✔ |
| `word_18AA` / `word_18AC` | deux bornes sur `word_C5A8`, axe 1300…11000 ✔ |
| sélection de variante | **masque `[word_18B2+0x12]` bits 2-7, armé par 5 drapeaux CAN** ✔✔ |
| unité de l'axe | **mg/tour ×10 (hypothèse forte)**, non tranchée |
| duplication `word_18AA`/`word_18AC` | **non expliquée**, signalée |
| lien vers régulateur / clim | **non établi** |

---

## 5. Prochaines actions

1. **★ Balayer TOUT le Datensatz avec la méthode de l'étape 50 §1** : lire le premier mot de chaque
   courbe 1-D et **annoter automatiquement les 273 enregistrements par la variable qu'ils nomment**.
   C'est un gain considérable et il est mécanique.
2. **`word_18B2`** : cartographier son bloc entier (taille, contenu de `+0x12`, des six groupes
   `+0x14…+0x1A`). C'est **le bloc de variante** — la pièce maîtresse.
3. **Les 5 drapeaux CAN** `word_FD38`, `word_FD38+1`, `word_FD7A`, `word_FD7A+1`, `word_FD7C` : à
   relier aux trames du bus — c'est le point d'entrée de la configuration véhicule.
4. Vérifier si `word_18B2 + 0x12` a un **écho en EEPROM** (miroir de configuration).
