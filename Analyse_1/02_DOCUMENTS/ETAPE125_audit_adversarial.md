# ÉTAPE 125 — Audit adversarial : tout est faux jusqu'à preuve

**Demande** : *« Analyse tous les documents produits, croise leurs données, vérifie-les à nouveau en supposant qu'à priori tout est faux et que rien n'est démontré (sauf ce que j'ai affirmé), vérifie tout ! »*

**Postulat de travail** : aucun document antérieur n'a d'autorité. Aucun script antérieur n'a d'autorité. Chaque affirmation est **re-dérivée depuis `edc.bin` et `clean.asm`** avec du code neuf écrit dans cette étape. Ce qui ne peut pas être re-dérivé est **rétrogradé en non démontré**, même si un document l'affirme avec aplomb.

**Corpus** : 124 documents `ETAPE*.md` (22 773 lignes) + 54 CSV + `/home/user/clean.asm` (412 022 lignes) + `/home/user/edc.bin` (524 288 o).

**Portée honnête de la vérification** : les affirmations **porteuses** du dossier (adressage, cartes, chaîne FAP, chaîne injection, décomptes, registre d'appels) ont été re-dérivées une par une. Les 22 773 lignes de prose n'ont pas été relues intégralement ; les affirmations non structurantes qui y figurent restent au statut de « non vérifiée en É.125 ».

---

## 1. Résultat n°1 — la pierre angulaire était une inférence, pas une preuve

Tout le dossier repose sur une formule de décodage. Je l'ai testée avant de tester quoi que ce soit d'autre.

**Constat gênant** : `grep` sur `clean.asm` ⇒ **aucune référence à `0x61400`**. Aucune instruction ne lit cette table. La chaîne « handle → adresse » n'est donc **pas prouvée par le code** : elle est reconstruite depuis les données.

**Ce que j'ai fait** : tester la formule sur des structures dont le contenu est auto-vérifiant (tag, n, axe strictement croissant, valeurs), et la comparer à des formules concurrentes.

**Piège rencontré (et corrigé)** : ma première re-dérivation a donné **9,3 % de validité** — parce que j'avais écrit `0x61400 + 2×(h−0x1400)`. La formule correcte est un **décalage en octets** :

```
entrée de table : u16 @ fo = 0x60000 + h        (≡ 0x61400 + (h − 0x1400))
adresse cible   : EA = 0xE0000 + entrée
```

**Validation de la formule correcte** — les 6 courbes FAP, re-dumpées sans réutiliser aucun script antérieur :

| h | cible | EA | tag | n | axe | valeurs |
|---|---|---|---|---|---|---|
| `0x191E` | `0x5F9C` | `0xE5F9C` | `0xC586` | 2 | `5231, 8231` | `100, 3200` |
| `0x1922` | `0x5FC0` | `0xE5FC0` | `0xC586` | 2 | `5231, 8731` | `100, 32767` |
| `0x1950` | `0x639A` | `0xE639A` | `0xC586` | 8 | `3731 … 8531` | `7231 … 5131` |
| `0x18A2` | `0x4D14` | `0xE4D14` | `0xD1B6` | 8 | `500 … 11000` | `117 … 655` |
| `0x18A4` | `0x4D38` | `0xE4D38` | `0xD1B6` | 8 | `500 … 11000` | `15 … 260` |
| `0x1DFA` | `0xBA84` | `0xEBA84` | `0xD5A2` | 2 | `4731, 5731` | **`10000, 10000`** |

Six sur six, y compris les tags et les dimensions. La formule concurrente « base RAM 0x1000 » ne donne que 1,5 % de structures valides : elle est éliminée.

**Validation croisée indépendante** : les **385 entrées** du registre d'appels, re-dérivées par `EA = 0xE0000 + u16@(0x60000 + pointeur)` ⇒ **348 non vides, 348 conformes, 0 désaccord**.

**Verdict** : la formule est **validée empiriquement de façon très forte**, mais elle reste **non prouvée par le code**. C'est la faiblesse structurelle n°1 du dossier, et elle doit être écrite noir sur blanc plutôt que passée sous silence.

---

## 2. Résultat n°2 — les cartes : 86 confirmées, 66 et 91 sont fausses

Trois chiffres circulaient : **66** (catalogue §5), **86** (CSV v2), **91** (errata 57). Un scan neuf, indépendant, donne **89** cartes 2-D uniques — mais trois sont des **artefacts** :

| EA | tag | défaut |
|---|---|---|
| `0xE79EE` | `0x7D2B` | tag hors de l'espace RAM (`0xC000`–`0xDFFF`) |
| `0xE9835` | `0x0002` | **adresse impaire** — structure non alignée |
| `0xE9837` | `0x0002` | **adresse impaire** |

Après élimination : **89 − 3 = 86**.

Croisement avec `inventaire_cartes_2D_axes_v2.csv` :

- cartes du CSV absentes de mon scan : **0**
- **désaccords de dimension : 0**
- cartes de mon scan absentes du CSV : **3**, toutes artefacts

⇒ Le CSV v2 est **exact à 100 %**. Les valeurs 66 et 91 sont **fausses** et doivent disparaître du dossier (**errata E37**).

---

## 3. Résultat n°3 — huit cartes ne sont référencées nulle part

J'ai appliqué votre règle (« aucune carte sans site d'appel ») aux 86 :

| Statut | Nombre |
|---|---|
| site d'appel présent dans `registre_appels_interpolation.csv` | **62** |
| absent du registre, mais variable pointeur référencée dans le code | **16** |
| **aucune référence, sous aucun préfixe de libellé** | **8** |

Les huit orphelines, avec leur handle unique :

| EA | handle | voisinage |
|---|---|---|
| `0xE22F4` | `0x1482` | à côté de `0xE22B2` (carte 2×2 de la voie FAP) |
| `0xE230C` | `0x1484` | idem |
| `0xE3B2C` | `0x15FC` | — |
| `0xE6306` | `0x1946` | à côté de `0xE639A` (courbe EGT) |
| `0xE7D44` | `0x1A54` | — |
| `0xE7DAC` | `0x1A56` | — |
| `0xEAFB2` | `0x1DB8` | — |
| `0xEBB46` | `0x1E1A` | — |

**Attention à ne pas surinterpréter** : « aucune référence » signifie *aucune référence par nom de variable*. Une carte peut encore être atteinte par un pointeur **calculé**. Mais dans un ECU où 16 des 24 cartes non enregistrées sont bien référencées nommément, huit exceptions est un signal réel (**errata E39**). Deux hypothèses concurrentes, non tranchées : calibration morte (variante non utilisée) ou accès indirect.

---

## 4. Résultat n°4 — le registre d'appels est l'artefact le plus fiable du dossier

La défiance générale était de mise : on savait les `l.N` des documents décalés de 1 à 20 (19,5 % exacts). **Ce n'est pas vrai du registre.**

- **385 / 385** entrées : la ligne citée contient exactement le `calls` vers la fonction annoncée, **décalage 0**.
- **348 / 348** EA re-dérivées conformes.
- Les 6 courbes FAP y ont toutes un site d'appel : `0xE5F9C` l. 163862, `0xE5FC0` l. 163870, `0xE639A` l. 166436, `0xE4D14` l. 155221, `0xE4D38` l. 155192, `0xEBA84` l. 204419.

⇒ La dérive des citations touche la **prose**, pas les **données structurées** (**errata E40**). Corollaire pratique : dans les documents futurs, citer `EA + label`, et s'appuyer sur les CSV plutôt que sur les renvois en prose.

*Défaut mineur trouvé* : 8 lignes sur 385 contiennent un `;` à l'intérieur d'un champ (`"#64h ; 'd'"`), ce qui casse un `split(';')` naïf. À corriger dans le générateur.

---

## 5. Résultat n°5 — la voie FAP résiste intégralement

Tout ce qui a été affirmé en É.124 §3 a été recompté ligne à ligne, sans faire confiance au document précédent :

| Affirmation | Recomptage É.125 | Verdict |
|---|---|---|
| `sub_ACD46` = `mov r4,#1` / `rets` | corps relu ; **XREF unique** = `loc_ACFC6` | **CONFIRMÉ** |
| `byte_C2BA` : 63 références, 1 écriture | 63 occurrences ; 1 seule ligne `movb byte_C2BA,` (l. 151775) | **CONFIRMÉ** |
| `word_C69E` : 11 sites de code | **12 occurrences = 1 label + 11 sites** ; 1 écriture l. 187528 | **CONFIRMÉ** |
| `word_C586` : 9 sites de code | **10 occurrences = 1 label + 9 sites** | **CONFIRMÉ** |
| `word_C77C` = 0 + 1000 = **1000 constant** | courbes `0xE6B86` `[0,0]` et `0xE6B92` `[1000,1000]` re-dumpées | **CONFIRMÉ** |
| `0xE8A06` → `byte_C8F8` (pompe, pas IQ) | l. 182810-182814 : `mov r12, word_1B5E` … `calls unk_1D50` … `movb byte_C8F8, rl4` | **CONFIRMÉ** |
| `0xE8B50` vs `0xE8BD4` : 5 cases sur 48 | dump complet des deux grilles 8×6 | **CONFIRMÉ à l'unité** |
| seuil `0xE8C58` = 539 | `u16 = 539` | **CONFIRMÉ** |

Détail du dump des deux cartes de souhait (8×6, `tagY=C42E`, `tagX=C6DA`) — les 5 seules cases différentes, **toutes en colonne pédale 2000** :

| régime | `0xE8B50` | `0xE8BD4` |
|---|---|---|
| 750 | 2400 | 2350 |
| 1000 | 2132 | 1782 |
| 1300 | 1844 | 1344 |
| 1750 | 1520 | 1070 |
| 2250 | 1260 | 910 |

À 40 % de pédale et au-delà, les deux cartes sont **identiques**. Conclusion opérationnelle inchangée : patcher `0xE8BD4` est quasi invisible, le levier réel est `0xE8444`.

---

## 6. Résultat n°6 — l'errata E32 doit être réécrit : bonne conclusion, mauvaise preuve

En É.124 j'ai conclu que `byte_C820`–`C824` et `byte_C81B`–`C81F` étaient des **canaux de diagnostic**, sur la base de l'identité supposée de `sub_9CFD0` (« publieur de valeurs mesurées »). **Je n'avais pas lu son corps.** Je l'ai lu.

**Ce qui est démontré, et solide :**
- `byte_C820`, `C821`, `C822`, `C823`, `C824`, `C81B`, `C81C` : **exactement 1 écriture chacun** (l. 140141, 140182, 140223, 140264, 140302, 140353, 140354).
- **Zéro lecture directe**, dans les 412 022 lignes.

**Ce que montre le corps de `sub_9CFD0` :**
- les arguments sont empilés puis relus en `[r0+#12h]` = **r12**, `[r0+#16h]` = **r14**, `[r0+#18h]` = **r15** ;
- `r12` sert d'**index de record** : `shl r4,#4` puis `add r4,#0EF00h` ⇒ record de 16 o ;
- `r15` est réduit à un identifiant 2 octets : `key = ((r15 & 7) << 13) | ((r15 >> 3) & 0FFh)` ⇒ `0x348` → `0x0069`, `0x388` → `0x0071` ;
- `r14` est la **source** dont on copie un nombre d'octets donné par l'argument empilé (5 ou 6).

**Traduction** : `sub_9CFD0` **range** le contenu du bloc (`C820` avec le record 2 ; `C81B` avec le record 7) dans une table de records identifiée par `0x348` / `0x388`. Ce n'est **pas** un publieur de diagnostic : c'est une **routine de mémorisation / d'adaptation**, et le bloc est une **entrée**.

**Conséquence** — la conclusion tient, la raison change (**errata E38**) :

> `byte_C820`–`C829` ne commandent pas les injecteurs. Preuve : 1 écriture et 0 lecture directe chacune ; leur unique accès indirect est une routine qui **lit** le bloc pour le mémoriser. La nature exacte de cette mémorisation (EEPROM, auto-adaptation, bloc de mesure) **reste non démontrée**.

Le socle de l'É.121 (« dernier maillon = commande des injecteurs ») est donc **réfuté**, mais je ne peux plus prétendre que ces octets sont du diagnostic au sens OBD.

---

## 7. Errata de cette étape

| Réf. | Objet | Correction |
|---|---|---|
| **E37** | Nombre de cartes 2-D : 66 (catalogue §5) / 91 (errata 57) | **86**, confirmé par double scan indépendant ; 89 bruts − 3 artefacts |
| **E38** | É.124 E32 : `sub_9CFD0` = « publieur de diagnostic », canaux `0x348`/`0x388` | **Faux dans la forme** : c'est une routine de **mémorisation** (record 16 o indexé par `r12`, ID dérivé de `r15`, copie depuis `r14`). La conclusion (les octets ne commandent pas les injecteurs) **reste valide**, la preuve est reformulée |
| **E39** | 8 cartes 2-D sans aucune référence de pointeur | Nouveau ; liste en §3 ; hypothèse morte/indirecte non tranchée |
| **E40** | « les citations `l.N` des documents sont décalées de 1 à 20 » | Vrai pour la **prose**, faux pour les **CSV** : registre d'appels **385/385 exact** |
| **E41** | Formule d'adressage ambiguë (`0x61400+(h−0x1400)` pouvait se lire en mots) | Écrire désormais `u16 @ (0x60000 + h)`, **décalage en octets** ; l'erreur de lecture produit 9,3 % de validité au lieu de ~100 % |

---

## 8. Ce qui reste NON DÉMONTRÉ (et doit cesser d'être présenté comme acquis)

| # | Affirmation | Statut réel |
|---|---|---|
| 1 | Le lien `handle → adresse` | **Validé empiriquement, non prouvé par le code** : aucune instruction ne lit `0x61400` |
| 2 | Les **noms d'axes** (`C42E` = régime, `C6DA` = pédale, `C3D2` = T° LDR…) | Reposent sur la **plausibilité de plage** — méthode explicitement condamnée en errata 56. Les **valeurs** sont prouvées, les **noms** sont des hypothèses |
| 3 | L'unité **mm³** | Aucune preuve interne ; cohérente avec votre affirmation d'ECU mono-unité IQ |
| 4 | `unk_20AC(…, 0x2710)` = plein échelle | `0x2710` apparaît bien dans le code, mais **pas dans `unk_20AC`** (bibliothèque absente, `0xC3`) ⇒ non prouvé |
| 5 | Nature de `sub_9CFD0` | Voir E38 : lecture = établie, **destination = non établie** |
| 6 | « le code est couvert à 100 % » | Solide (runs de `0xC3`), mais repose sur l'hypothèse que tout run ≥ 64 o est du remplissage. Aucune séquence d'instructions crédible ne mesure 32 Ko de `0xC3` |
| 7 | Post-injection absente | Conséquence de 1 et 6 ; confiance **85 %**, pas 99 % |

---

## 9. Ce que je n'ai pas à vérifier : vos affirmations

Exemptées par votre consigne, et **non contredites** par le binaire :

- trames CAN (`0x38D` vitesse /100, `0x412`, `0x468`, 250 kbit/s) ;
- codage pédale 0–100 % → 0–10000, deux signaux dont un = moitié ;
- seuils FGR 16 bits LoHi (`vMin` 4000/4500/5000, `vMax` 22000/25000, `nMin` 1200/1300, `GangMin` `04 00`) ;
- HW `0281010877` = 2.2 HDi full-mux ; `0281010597` = semi-mux ;
- rapport calculé dans l'ECU (jamais reçu par CAN), servant à l'agrément, à l'autorisation du régulateur et à la limitation 1er/2e ;
- architecture mono-unité IQ, smoke map après les correcteurs.

**Vérification incidente utile** : la chaîne `0281010877` est présente **une seule fois**, à `EA 0xFCC00`, dans un contexte `…B075WF2S…`. La chaîne `0281010597` est **absente du fichier** — ce qui conforte votre correction : ce binaire n'est pas un semi-mux.

Et `1037353776` est présent **trois fois** : `EA 0xEBFB0`, `EA 0xFBFB0` (+`0x10000`, duplication) et `EA 0xFFEF0` (à côté de `BOOT`).

---

## 10. Tableau de confiance révisé

| Élément | É.124 | **É.125** | Motif de la révision |
|---|---|---|---|
| Formule d'adressage | 95 % | **90 %** | validée empiriquement sur 298 structures + 385 appels, mais sans preuve par le code |
| Nombre de cartes 2-D | 86 (incertain) | **99 %** | double scan, 0 désaccord, artefacts identifiés |
| Registre d'appels | 85 % | **99 %** | 385/385 exact |
| Porte `byte_C2BA` | 99 % | **99 %** | recompté |
| `sub_ACD46` = 1 | 99 % | **99 %** | corps + XREF unique |
| Machine à états FAP | 95 % | **95 %** | inchangé |
| Les 6 courbes FAP | 95 % | **99 %** | re-dumpées par formule corrigée |
| `C82x` ≠ commande d'injecteurs | 95 % | **90 %** | conclusion tenue, preuve reformulée (E38) |
| Noms d'axes | 80 % | **55 %** | méthode condamnée en errata 56, non remplacée |
| Unité mm³ | 85 % | **60 %** | aucune preuve interne |
| Absence de post-injection | 85 % | **80 %** | dépend de 1 et 6 |

---

## 11. Verdict

**Ce qui tient, et tient bien.** La formule d'adressage est validée sur trois voies indépendantes. Les 86 cartes sont exactes au bit. Le registre de 385 appels est exact à la ligne. La voie FAP (porte de codage, machine à six états, intégrateur de suie, six courbes, correction neutralisée) est re-dérivée sans un seul écart. Les cartes de souhait ne diffèrent que de 5 cases sur 48, valeurs à l'unité.

**Ce qui a été corrigé.** Le nombre de cartes (66 et 91 → 86). La nature de `sub_9CFD0` (publieur de diagnostic → routine de mémorisation). Huit cartes orphelines, jamais signalées. La formule d'adressage, désormais écrite sans ambiguïté. Et une distinction utile : la prose dérive, les CSV non.

**Ce qui doit cesser d'être présenté comme démontré.** Le lien handle→adresse n'est pas prouvé par le code — c'est une inférence très bien validée. Les **noms** des axes ne sont pas prouvés, seulement leurs plages : c'est précisément la faute condamnée en errata 56, et elle est encore présente dans une bonne partie du dossier. L'unité mm³ vient de vous, pas du binaire.

**Le point le plus inconfortable** : sur 86 cartes, 8 n'ont aucune référence nominale. Le dossier n'en parlait pas. Ce sont peut-être des cartes mortes de variante, peut-être des accès calculés — mais tant que ce n'est pas tranché, la règle « aucune carte sans site d'appel » n'est satisfaite que pour **78 cartes sur 86**.
