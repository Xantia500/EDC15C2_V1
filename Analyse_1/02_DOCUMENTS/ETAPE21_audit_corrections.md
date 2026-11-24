# ÉTAPE 21 — AUDIT du travail : 2 erreurs trouvées, 1 fausse alerte, 1 doute levé

Tu as eu raison de demander un contrôle. L'erreur des 666 handles invalidait potentiellement tout ce
qui en dépendait. Voilà le résultat, vérification par vérification.

---

## ERREUR 1 (majeure, corrigée) — la table des handles : **1304**, pas 666

| | ce que j'avais écrit | réalité mesurée |
|---|---|---|
| nombre de handles | 666 | **1304** |
| plage de handles | `word_1400 … word_1932` | **`word_1400 … word_1E2E`** |
| plage des pointeurs | `0x100A … 0x60F2` | **`0x100A … 0xBC38`** |
| handles pointant en `EA 0xE8000-0xE9FFF` | 0 | **275** |

Méthode de mesure : la table démarre à l'offset fichier `0x61400` ; on avance de 2 octets tant que la
valeur reste un pointeur plausible (`0x0800…0xBFFE`) — la suite s'arrête d'elle-même à 1304 entrées,
et **les 1304 pointeurs sont tous distincts** (aucun handle partagé).

**Conséquences, à assumer :**

1. ma conclusion des étapes 18-19 (« zone non consommée, cartes non référencées ») est **morte** ;
2. **tous les inventaires de session bâtis sur 666 sont tronqués d'environ la moitié** :
   `table_pointers_datensatz_0E1400.csv` (666 lignes), `cartographies_datensatz.csv`
   (44 cartes × 2 banques), `courbes_1D_datensatz.csv` (104), `axes_datensatz.csv` (678),
   `tags_inventaire.csv` (98). **Le recensement que tu m'as demandé (toutes les maps 1-D/2-D) doit
   être refait sur 1304 handles.** J'ai commencé : voir §5.
3. C'est une erreur de **méthode** : j'ai repris un chiffre sans le vérifier, puis j'ai construit une
   conclusion dessus. C'est exactement ce que tu m'as demandé d'éviter (provenance de chaque
   affirmation) — la leçon est retenue : **tout dénombrement doit être recalculé, pas repris.**

---

## ERREUR 2 (de détail, corrigée) — l'attribution des cas du sélecteur

J'avais conclu « cas 1 → 1ʳᵉ, 2 → 2ᵉ, 3 → 3ᵉ, 4 → 4ᵉ, 5 → repli » **d'après l'ordre d'apparition du
code**. C'était une inférence, pas une lecture. La vraie **table de sauts** :

- elle est en flash à **`EA 0xE0A62`** (offset fichier `0x60A62`, copie banc F à `0x70A62`) ;
- l'instruction `add r4, #0A62h` désigne un **offset dans le segment `0xE`**, pas une adresse
  physique — c'est aussi ce qui explique mon dump raté sur `0x3110` (remplissage `0xC3`) avant que
  je corrige la convention ;
- 12 entrées, index = `(byte_C330 & 0x0F) − 1` :

| code rapport | cible | effet |
|---|---|---|
| **1** | `0x3132` → `word_1B54` = `0xE8906` | courbe **limitée** (35…65 mm³) |
| **2** | `0x3144` → `word_1B56` = `0xE8946` | courbe **limitée**, identique à la 1ʳᵉ |
| **3** | `0x3156` → `word_1B58` = `0xE8986` | **100 mm³ = aucune limite** |
| 4, 5, 6, 7, 8, 10 | `0x318C` | **repli** : `word_D9A2 = word_D9A8` |
| 9 | `0x317A` → `word_1B5C` = `0xE89FA` | courbe 2 points, 100 mm³ |
| **11, 12** | `0x3168` → `word_1B64` = `0xE8B10` | courbe **identique à la 1ʳᵉ** ⇒ **marche arrière** |

`word_1B64` (`EA 0xE8B10`, 15 points, 635…4000 rpm) vaut **exactement** les mêmes valeurs que la
courbe de 1ʳᵉ : `3516, 3516, 3516, 4485, 5800, 6660, 6400, 6350, 6300, 6330, 6400, 6500, 6440, 6270,
6240`. Une marche arrière protégée comme la 1ʳᵉ, c'est exactement ce qu'on attend.

**Et le plus important : la table de sauts confirme ta description mot pour mot** — 1ʳᵉ et 2ᵉ
limitées, 3ᵉ sans limite, 4ᵉ et au-delà sans limite. Ce n'est plus une hypothèse, c'est le contenu de
la table.

---

## NON-ERREUR vérifiée — le format des enregistrements

Contrôle par la taille, indépendamment de toute interprétation :

```
carte 2-D de word_1B40 : 0xE8444
  4 + 2×16 (tagY=0xC42E + axe) + 4 + 2×16 (tagX=0xC3E6 + axe) + 2×16×16 (grille) = 584 = 0x248
  0xE8444 + 0x248 = 0xE868C  →  et à 0xE868C commence un enregistrement  tag 0xC3D2, n = 6
```

La taille prédite par le format tombe **exactement** sur le début de l'enregistrement suivant. Le
format `[tag][n][axe n][valeurs n]` et sa variante 2-D sont donc **confirmés**, ainsi que la grille
16×16 de la smoke map.

## NON-ERREUR vérifiée — l'axe secondaire de `word_1B5E`

La carte de `word_1B5E` (`EA 0xE8A06`) déclare comme second axe **`0xD3D4`**, alors que le code
(l. 182810) passe `r14 = word_D9AA`. Ce n'est pas une contradiction : les lignes 182800-182803 font
`mov r4, word_D9AA ; mov word_D3D4, r4` **juste avant** l'appel. **Les tags d'axe du Datensatz nomment
la variable de travail, pas la variable source.** Mon test « tag2 == D9AA » était mal posé — le
décodage, lui, était juste.

## DOUTE LEVÉ — `byte_C337` n'est pas une vitesse

J'avais signalé `word_1814` (axe 0…250, tag `0xC337`) comme candidat « Vmax ». **C'est faux** :
`byte_C337` est la **sortie** de la carte `word_1B5E` (régime × `D3D4`), recopiée par
`sub_9AE42` (l. 139696) puis publiée comme axe. La plage 0…250 est celle d'un **résultat**, pas
d'une vitesse. À rayer de la liste des pistes.

---

## 5. Inventaire refait sur 1304 handles — état et limite

Fichier produit : **`inventaire_complet_1304_handles.csv`** (291 enregistrements classés, avec type,
largeur d'axe/valeurs, `X_min`/`X_max`, tag et taille du second axe).

| type | nombre |
|---|---|
| 1-D mot (axe 16 bits, valeurs 16 bits) | **182** |
| 2-D mot × mot | **67** |
| 1-D octet | **42** |
| **non classés** | **1013** |

**Limite honnête** : mon classement reposait sur `taille = pointeur_suivant − pointeur_courant`, donc
sur l'hypothèse que les enregistrements sont contigus dans l'ordre des pointeurs. Elle est vraie pour
291 d'entre eux et **fausse pour les autres** — il existe d'autres formes d'enregistrements (les
« blocs » repérés dès la session, dimensions d'axe hors de mes bornes, ou enregistrements pointés en
leur milieu). **Je ne présente donc pas cet inventaire comme complet** : il faudra le refaire par la
méthode des descripteurs, comme pour les cartes, et non par différence de pointeurs.

En revanche, un chiffre est solide : **275 handles désignent des données situées en `EA 0xE8000-0xE9FFF`**,
donc la moitié du Datensatz que j'avais déclarée inutilisée est en réalité consommée.

---

## 6. Ce qui reste à faire, dans l'ordre

1. **`sub_9B796`** — la fonction qui calcule `byte_C240` (le rapport 0…14). C'est là que régime et
   impulsions se rencontrent. Cibles : la division, et `byte_C872`.
2. **La table de sauts `#0A2Ch` = `EA 0xE0A2C`** — le sélecteur de `byte_C240` (même mécanisme que
   `0xE0A62`, que je viens de lire). Elle dira quels codes 0…14 existent réellement.
3. **Refaire l'inventaire** des 1304 handles par descripteurs, pour répondre proprement à ta demande
   initiale de recensement.
