# ÉTAPE 56 — Catalogue enrichi : **noms, axes, schémas, entrées/sorties** — et la clé des températures

---

## 1. ★★★ La découverte : **les températures sont codées en Kelvin × 10**

Tu avais donné la convention : **2731 = 0 °C, 3531 = 80 °C**, soit **K × 10**. Confrontée aux plages
d'axes réellement présentes dans le Datensatz, elle **explique d'un coup toute une famille de
variables** :

| variable | plage d'axe | **en °C** | grandeur |
|---|---|---|---|
| `word_C3D2` | 2 231 … 4 231 | **−50,0 … +150,0 °C** | **température liquide de refroidissement** |
| `word_C3BA` | 2 231 … 4 081 | **−50,0 … +135,0 °C** | **température air d'admission** |
| `word_C3B0` | 2 531 … 3 931 | **−20,0 … +120,0 °C** | **température gasoil** |
| `word_C5A4` | 2 431 … 3 331 | −30…+60 °C *ou* 243…333 °C | échelle non tranchée |
| `word_C586` | 3 731 … 8 731 | 100…600 °C *ou* 373…873 °C | échappement probable |

**Ce n'est pas une coïncidence de réglage** : −50…+150 °C est **exactement** la plage d'une sonde de
liquide de refroidissement, et ces bornes **recoupent** celles que tu avais annoncées (−40…+120 °C).
La convention n'a pas été choisie pour faire coller ces plages — elle les fait coller.

### ⚠ Deux échelles coexistent, et il faut le dire

| famille | échelle | preuve |
|---|---|---|
| **CTN** (LDR, air, gasoil) | **K × 10** | 2731 = 0 °C, 3531 = 80 °C ; plages cohérentes |
| **thermocouple d'échappement** | **°C × 10** | la valeur de repli de la 2ᵉ EGT vaut **6231 = 623,1 °C** ; la loi monte à **11731 = 1173,1 °C** — maximum d'échappement réaliste |

**Les deux lectures ne peuvent pas être fusionnées** : en K × 10, la température LDR donnerait 233 °C à
−40 °C (absurde) ; en °C × 10, la plage −40…+120 °C des axes CTN deviendrait inatteignable. **Ce sont
donc deux conventions, une par famille de capteur** — ce qui est logique : la loi d'une CTN produit des
Kelvin, un thermocouple fournit des °C.

---

## 2. ★★★ Ce que cela donne sur les seuils déjà décodés

`word_142A` (EA `0xE122C`), le descripteur du moniteur de température LDR :

| offset | valeur | lecture **avec la clé des températures** |
|---|---|---|
| `+0` | **3431** | **343,1 K = +70 °C** — seuil d'activation |
| `+2` | 220 | +22 K → borne **3651 = +92 °C** |
| `+4` | 100 | autorisation |
| `+6` | 100 | +10 K — critère de durée |

**⇒ Le moniteur de température LDR s'active entre 70 °C et 92 °C.** C'est **le domaine du thermostat**,
et c'est exactement le comportement attendu d'un diagnostic qui refuse de juger à froid. Ce qui était
« 3431 et 220 » est devenu **un seuil thermostat, lisible par un mécanicien.**

**Et cela confirme la chaîne** : `word_C3D2` (LDR) → `word_C908` (instantané) → moniteur → `word_CFD6`.

---

## 3. Ce qui a été ajouté au catalogue

`analyse_edc15c2_4hx/CATALOGUE_MAITRE.md` — **1 241 lignes** (contre 866).

### § 4 et § 5 — noms explicites des courbes et des cartes

Chaque enregistrement reçoit un **nom construit**, jamais inventé :

- courbe : **`Loi <grandeur d'entrée> → sortie`**, avec `n`, axe, **axe converti en °C quand c'est une
  température**, valeurs, magnitude de sortie observée ;
- carte : **`CARTE <lignes> × <colonnes>`**, avec dimensions, bornes des deux axes, et **magnitude de
  sortie** (min…max de la grille) — qui oriente sans affirmer.

Deux règles explicites, inscrites dans le document :
- quand la sortie n'est pas identifiée, **c'est écrit « sortie non identifiée »** — aucun nom inventé ;
- la colonne « consommateur » porte un avertissement : **`—` signifie « non établi », pas « non
  consommé »** (les cartes sont lues via un handle passé en paramètre, motif que l'outil ne couvre pas
  encore — et leur non-consommation a été réfutée dès l'étape 25).

### § 5 bis — signification des axes

Table complète : variable, plage, conversion, grandeur, **niveau de confiance** (`lu` / `util` / `inf`
/ `?`). Vingt-huit axes documentés, dont **cinq températures identifiées**.

### § 5 ter — **sept schémas de boucles réellement comprises**

| boucle | contenu | statut |
|---|---|---|
| **A — Acquisition** | capteur → ADC → descripteur → courbe → `word_D0xx` → `word_C3xx` → `word_C9xx` → axes de cartes | **établie** (preuve bout en bout voie 6) |
| **B — Diagnostic** | mesure → `word_C908` → moniteur (`word_CFD4`) → confirmation (`sub_A1E9E`) → `word_CFD6` → mémoire → codes → services | **établie** |
| **C — Hystérésis / anti-rebond** | deux courbes = deux bornes → comparaison → 7 compteurs → N cycles consécutifs → bascule | **établie** |
| **D — Anti-falsification** | valeur → historique 5 niveaux → moyenne → seuils | **établie** |
| **E — EEPROM** | applicatif → `0x94Axx` → `sub_A0002` → image `0xE5CE` | **établie** |
| **F — Variante** | CAN → masque `[word_18B2+0x12]` → groupe de valeurs → `word_C5A8` | **établie** (lien vers régulateur/clim **non** établi) |
| **G — Injection** | cartes de couple (X = régime, mm³×100) → … → **MANQUANT** | **partielle, et dite comme telle** |

**Sur la boucle G, je suis explicite** : la chaîne complète n'est **pas** établie. Ce qui est sûr est
écrit (cartes de couple consommées, X = régime, résultat en mm³ × 100, limiteur principal en dernier,
grandeurs en 0…10000 = 0…100 %). Ce qui manque est écrit **« MANQUANT »** : conversion mm³ → durée
d'injection, avance, pilotage final. Ces éléments sont dans le **bloc `0xFC000-0xFFFFF`** — programme
autonome — et **on ne les inventera pas**.

### § 5 quater — entrées et sorties

- **Table des 21 voies d'acquisition** : tâche KWP, voie ADC, **capteur identifié**, EA de la courbe,
  nombre de points, plage de sortie, **variable brute**, **copie de travail**, chemin de défaut.
- **Table « où chaque grandeur est traitée »** : grandeur → variable de travail → instantané diagnostic
  → nombre d'axes → consommateur identifié.
- **Table des sorties** : EGR et N75 (RCO, seuils = plafonds), injection (**chaîne non établie**),
  post-injection/FAP (**non localisé**), voyant (lien dans la couche absente).

**Capteurs identifiés grâce au travail de l'étape 13, désormais interprétables :** débitmètre à deux
éléments, pression d'environnement (600-1200 mbar), **température air d'admission**, **température
gasoil**, **deux thermocouples d'échappement**, **température LDR**, plus cinq voies de plausibilité ou
brutes.

---

## 4. Ce que cette étape apporte au-delà de la documentation

1. **La clé des températures transforme des dizaines de courbes en lois lisibles** — et elle **valide le
   sens du moniteur principal** (70-92 °C, thermostat).
2. **Les schémas ne contiennent que du code lu** : chaque boucle renvoie à ses numéros de ligne dans les
   étapes. **Aucune boucle n'est dessinée par vraisemblance.**
3. **La boucle G est volontairement incomplète** : c'est plus utile qu'un schéma plausible et faux.

---

## 5. Prochaines actions

1. **Appliquer la clé Kelvin à toutes les courbes dont l'axe tombe dans 2000-4500** : beaucoup sont des
   lois de CTN, et leur **sortie** est alors directement une température — ce qui nommerait la sortie,
   pas seulement l'entrée.
2. **`sub_AFAA0`** (17 handles, plus gros consommateur) : l'identifier nommerait une famille entière de
   cartes.
3. **Trancher l'échelle de `word_C586` et `word_C5A4`** en regardant la loi de conversion du
   thermocouple (`0xE3076`) : si elle produit des °C, `word_C586` est en °C × 10.
4. **Compléter les noms de sortie** au fur et à mesure — la colonne existe, elle n'attend que des
   preuves.
