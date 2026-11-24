# ÉTAPE 52 — Nouveaux gabarits, **sentinelles**, et le CATALOGUE MAÎTRE

---

## 1. ★★★ Le CATALOGUE MAÎTRE existe, et il est **régénérable**

**`analyse_edc15c2_4hx/CATALOGUE_MAITRE.md`** — généré par **`outils/genere_catalogue.py`**.

Il contient, de façon **exhaustive et lisible** :

| § | contenu |
|---|---|
| 1 | conventions, adressage, niveaux de confiance (**lu / util / inf / ?**) |
| 2 | les **six gabarits** d’enregistrement, avec leur taille et leur preuve |
| 3 | **inventaire des variables** : axes 1-D/2-D, plage globale, grandeur, unité, statut |
| 4 | **table exhaustive des 182 courbes 1-D** : ID, EA, taille, variable, n, axe, **valeurs**, unité |
| 5 | **table exhaustive des 66 cartes 2-D** : ID, EA, axe Y, nY, axe X, nX, plage de grille |
| 6 | paramètres scalaires, blocs réservés, **sentinelles** |
| 7 | blocs de paramètres identifiés **par leur usage** (`word_142A`, `word_1474`, `word_18B2`…) |
| 8 | **EEPROM** : trois couches, pilote, magasin, quatre enregistrements, 20 appelants, validité, anti-falsification, variante |
| 9 | **diagnostic** : mémoire des défauts, descripteur, moniteurs, compteurs |
| 10 | **registre des erratas** — 11 hypothèses retirées, conservées pour ne pas les réintroduire |
| 11 | **ce qui reste à trouver** |

**La mise à jour est mécanique** : relancer le script après chaque trouvaille. Les tableaux sont
recalculés depuis le binaire, donc **jamais désynchronisés**. Les sections narratives sont dans le
script, à côté du code qui les produit.

---

## 2. ★★ ERratum à l’étape 51 : **182 courbes + 66 cartes**, et non « 248 courbes »

En construisant le catalogue, j’ai trouvé un **défaut de mon propre classement** : 66 cartes 2-D
avaient été comptées comme courbes 1-D, parce que la détection 1-D passait en premier et qu’un en-tête
de carte ressemble à un en-tête de courbe.

**Je préfère désormais le décodage dont la taille calculée ÉGALE la taille du bloc.** Résultat corrigé :

| type | nombre | tailles exactes |
|---|---|---|
| **courbes 1-D** | **182** | **182 / 182** |
| **cartes 2-D** | **66** | **66 / 66** |
| **total décodé** | **248** | **248 / 248** |

**Le total ne change pas (248 = 182 + 66), mais la répartition est juste — et le taux de réussite
devient 100 %, ce qui est en soi un résultat plus fort que celui que j’annonçais.**

*Leçon méthodologique* : quand deux gabarits sont possibles, **c’est la confrontation à la taille du
bloc qui arbitre**, pas l’ordre de test.

---

## 3. ★★★ Sentinelles : `0xFFFE`, `0xFF00`, `0xC300` — et la fin de l’« anomalie 0xC300 »

Les blocs « réservés » contiennent, à la fin, les octets `00 FF 00 C3` :

```
0xE45BA : FE FF 00 00 00 00 00 00 00 00 00 00 00 00 00 00
          00 00 00 00 00 00 00 00 00 00 00 00 00 00 FF 00 C3
```

| sentinelle | position | sens proposé |
|---|---|---|
| **`0xFFFE`** | **premier mot** d’un bloc | **bloc sans variable** — emplacement non affecté |
| **`0xFF00`** | fin des blocs réservés | marqueur de fin |
| **`0xC300`** | **fin** des blocs réservés ; aussi `[word_1474+0x08]` et `[word_142A+0x22]` | **« pas de valeur »** |

### Conséquence — et elle me corrige encore

À l’étape 51 §5 j’avais noté `0xC300` comme une **« anomalie à instruire »**, en la lisant comme
`−15 616`. **C’est faux** : `0xC300` est une **sentinelle d’absence de valeur**.

⇒ les champs qui la contiennent (`word_1474+0x08`, `word_142A+0x22`, le bloc de 2 octets à `0xE2290`)
sont **vides**, pas remplis d’une valeur bizarre. **Cette piste est close**, et elle l’est proprement.

**Bilan honnête** : ce qui ressemblait à une incohérence de mes décodages était en réalité **un
marqueur documenté du format**. Le format est plus propre que je ne le pensais.

---

## 4. ★ Les nouveaux gabarits

| type | gabarit | taille | nombre | lecture |
|---|---|---|---|---|
| **Paramètre scalaire** | un seul mot | **2 octets** | **91** | le bloc ne contient qu’**une valeur** ; le premier mot **est** la valeur, **pas** une adresse de variable |
| **Bloc réservé** | `0xFFFE` + zéros + `0xFF00 0xC300` | 32 octets | **7** | **emplacement libre** — le constructeur a prévu de la place pour des tables supplémentaires |
| **Table d’index** | `0xFFF2` puis `1136, 1137, 1138, 1139, 1140…` | 32 octets | ≥ 1 | **suite d’entiers consécutifs** — une énumération, pas une calibration |

**Répartition finale des 1 304 handles :**

```
182 courbes 1-D  +  66 cartes 2-D  +  7 blocs réservés  +  91 scalaires  +  958 non décodés  =  1 304
```

**346 handles sont désormais compris (26 %)** — et parmi les 958 restants, beaucoup relèvent
probablement des trois nouveaux gabarits ou de structures composites.

---

## 5. Ce que le catalogue apporte de neuf, en le lisant

Quelques lignes tirées du document, qui montrent l’intérêt de la mise en tableau :

- **`word_C42E` : 42 axes en 1-D + 49 en 2-D = 91 axes** — le régime est **la référence de tout** ;
- **`word_C3D2` : 27 + 8 = 35 axes**, plage 2 231…4 231 — la masse d’air par tour vient juste après ;
- **`word_C6A2` : 14 axes en X contre 1 en 1-D** ⇒ c’est **presque exclusivement un axe de carte**, ce
  qui est cohérent avec une grandeur de charge en abscisse ;
- une courbe à **16 points** (`word_D048`, axe 32…1023) descend de **11 731 à 6 137** — une **loi de
  conversion de capteur**, à rapprocher des chaînes ADC ;
- `word_C77A` : axe **6 667…31 667** avec des valeurs butoir `0, 5000, 10000, 10000, 0` — profil
  d’une **limitation** (montée, plateau, retombée).

---

## 6. Prochaines actions

1. **Attaquer les 958 non décodés** en cherchant les gabarits par **récurence de taille** (le tableau
   `word_1946…195C` de l’étape 49 en est un exemple réussi).
2. **Instruire la table d’index** (`0xFFF2`, `1136, 1137, 1138…`) : à quoi sert une énumération
   d’entiers consécutifs dans une calibration ?
3. **`word_C77A`** : le profil « limitation » est une piste pour du **couple** ou une **Vmax**.
4. **Compléter le catalogue** au fur et à mesure — c’est désormais le point d’entrée unique du dossier.
