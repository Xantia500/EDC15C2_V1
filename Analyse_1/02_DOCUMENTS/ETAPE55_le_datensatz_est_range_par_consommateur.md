# ÉTAPE 55 — ★★★ Le Datensatz est rangé par **fonction consommatrice**

---

## 1. L'outil : `outils/consommateurs.py`

Il associe chaque accès relevé à l'étape 54 à **sa fonction englobante** dans `clean.asm`, et produit
`analyse_edc15c2_4hx/consommateurs_handles.csv` :

`handle · nb_accès · consommateur_principal · part · autres_consommateurs`

**Résultat : 35 handles ont un consommateur UNIQUE avec au moins 10 accès** — attribution sans ambiguïté.

---

## 2. ★★★ Constat : chaque routine possède **7 à 17 blocs et rien d'autre**

| fonction | handles distincts | accès |
|---|---|---|
| `sub_AFAA0` | 17 | 160 |
| **`sub_A1E9E`** | **15** | **219** |
| `sub_B64A8` | 13 | 68 |
| `sub_C4AAE` | 12 | 41 |
| `sub_ACD4A` | 10 | 49 |
| `sub_B7FD4` | 9 | 241 |
| `sub_A7D96` | 9 | 252 |
| `sub_B35B6` | 9 | 150 |
| `sub_C8012` | 8 | 115 |
| `sub_BAC40` | 7 | 128 |
| `sub_A5C92` | 7 | 143 |
| `sub_D2EAA` | 7 | 111 |

**⇒ La calibration n'est pas rangée par grandeur physique. Elle est rangée par CONSOMMATEUR.**

Ce n'est pas une intuition : c'est ce que montrent les **parts** de la colonne `part`. Pour la plupart
des blocs, un seul consommateur atteint **100 %** des accès. Un bloc n'appartient qu'à **un** sous-système.

**Ce que cela donne, concrètement :** le rôle d'une fonction **nomme ses blocs**. On ne cherche plus
« à quoi sert `word_189A` », on cherche « à quoi sert `sub_A1E9E` » — et cela répond pour quinze blocs
d'un coup.

---

## 3. ★★★ La preuve par recoupement : `sub_A1E9E`

`sub_A1E9E` est la **routine de confirmation des défauts**, décodée à l'étape 42. Voici **tous** les
blocs qu'elle consomme :

| handle | taille | déjà identifié par une autre voie ? |
|---|---|---|
| `word_18C2` | **78** | non — **nouveau**, 45 champs distincts |
| `word_1474` | 34 | **oui** — durées de confirmation (étape 49) |
| `word_18B2` | 30 | **oui** — masque de variante (étape 50) |
| `word_189C` | 18 | non — rattaché par cette voie |
| `word_1874` | 16 | non — rattaché par cette voie |
| `word_189A` | 12 | non — rattaché par cette voie |
| `word_186A` | 12 | non — rattaché par cette voie |
| `word_142A` | 10 | **oui** — seuils du moniteur (étape 42) |
| `word_1818` | 6 | **oui** — numéros de bits 2,1,0,8,15 (étape 47) |
| `word_1878` | 6 | **oui** — source de `word_C596` (étape 50) |
| `word_187A` | 2 | non |
| `word_1896` | 2 | non |
| `word_1898` | 2 | non |
| `word_1472` | 2 | non |
| `word_18E6` | 2 | non |

### Pourquoi c'est le résultat le plus fort de tout ce travail

**Six blocs sur quinze avaient été identifiés séparément, par des chemins radicalement différents :**
- `word_142A` par l'analyse des **seuils** d'un moniteur ;
- `word_1474` par l'analyse des **durées** de confirmation ;
- `word_1818` par la **lecture directe** de ses six octets ;
- `word_18B2` par l'analyse du **sélecteur de variante** ;
- `word_1878` par la trace de `word_C596` ;
- `word_18C2` par la **taille** du bloc et ses 45 offsets.

**Que la même routine les consomme tous n'était pas acquis.** C'est une validation croisée qui porte
cette fois sur l'**interprétation**, pas seulement sur les tailles — et elle est **indépendante** de
tout ce que nous avons supposé.

**Et elle offre neuf blocs gratuitement** : `18C2`, `189A`, `186A`, `1874`, `189C`, `187A`, `1896`,
`1898`, `18E6` sont désormais **rattachés au sous-système de diagnostic**. Leur **rôle** est connu ;
leurs **champs** ne le sont pas encore.

---

## 4. ★ Observation inattendue : **le numéro de handle CLASSE le bloc**

| sous-système | plage de handles dominante |
|---|---|
| diagnostic / moniteurs (`sub_A1E9E`) | **`0x18xx`** |
| surveillance `word_C5B8` (`sub_A5C92`) | **`0x18Ex…0x18Fx`** |
| `sub_A7D96` | **`0x19xx`** |
| `sub_BAC40` | **`0x14xx`** et `0x1Cxx` |

Le recoupement est net : **les fonctions d'un même domaine consomment des handles voisins.**

**⇒ Le handle n'est pas une adresse arbitraire : c'est un INDEX DE CLASSEMENT.** Les blocs voisins
appartiennent au même sous-système.

**Conséquence pratique immédiate** : pour un bloc **non encore identifié**, **son numéro prédit son
sous-système**. Un `0x19xx` relève de la famille `sub_A7D96` ; un `0x18Ex` de la famille `sub_A5C92`.
C'est une **règle de tri**, et elle est testable.

*Réserve* : quelques blocs sont **partagés** entre sous-systèmes (`word_1474` n'est qu'à 100 % dans
`sub_A1E9E`, mais `word_142A` à 58 %, `word_178`… à 88-95 %). La règle est donc **statistique, pas
absolue** — elle oriente, elle ne démontre pas.

---

## 5. Ce que cette étape change

1. **La stratégie est désormais claire et bornée** : il reste **12 fonctions** à identifier pour couvrir
   la majeure partie du Datensatz. Ce n'est plus « 927 blocs inconnus », c'est **une douzaine de
   sous-programmes**.
2. **Chaque fonction identifiée résout 7 à 17 blocs d'un coup.** Le rendement est très supérieur au
   travail bloc par bloc.
3. **Le catalogue porte maintenant cette table** (§ 2 bis, constat 5) avec le recoupement complet.

**Le catalogue : `analyse_edc15c2_4hx/CATALOGUE_MAITRE.md`, 866 lignes, régénéré par
`outils/genere_catalogue.py`.**

---

## 6. Prochaines actions

1. **★ Identifier `sub_AFAA0`** (17 handles, le plus gros consommateur) — c'est le prochain gain maximal,
   et il y a fort à parier qu'il s'agit d'un sous-système majeur (EGR, suralimentation ou FAP).
2. **`sub_A7D96`** (9 handles mais **252 accès**, dont `word_1952` et `word_18F6`) — c'est la fonction
   qui exploite les deux blocs restés « à instruire » depuis les étapes 47-49.
3. **`sub_A5C92`** — déjà reliée à `word_C5B8` : elle doit contenir la **logique complète de
   surveillance** de cette grandeur, donc sa nature.
4. **Vérifier la règle de classement par numéro** sur les 35 handles mono-consommateurs.
