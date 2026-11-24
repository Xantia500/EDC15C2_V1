# ÉTAPE 9 — Typologie des données, corrections d'unités, et inventaire des cartes

Suite de l'étape 8. **Véhicule de référence : Peugeot 406 2.2 HDi 16v « 4HX » (DW12TED4) avec FAP, calculateur EDC15C2 (0 281 010 877).** Toutes mes estimations de plage sont désormais recalées sur ce moteur — **2 179 cm³, 4 cylindres 16 soupapes, injection directe common rail** (le suffixe **C2** de l'EDC15C2 désigne bien la variante *Common Rail*, ce qui est cohérent avec les grandeurs trouvées : pression de rampe, quantité, avance, EGT, FAP) — et non plus sur un 1,9 TDI.

---

## 1. Corrections validées — les températures sont en **K × 10**

**Vous avez raison, et c'est une correction importante.** `2731` = **273,1 K = 0 °C**, `3531` = **353,1 K = 80 °C**.

Cela **invalide ma lecture « pression en mbar »** de l'étape 8 et reclasse tout un groupe de tags :

| Tag | Étendue brute | Lecture erronée (étapes 7-8) | **Lecture correcte (étape 9)** |
|---|---|---|---|
| `0xC3D2` (36 axes !) | 2231 → 4231 | pression 2,2–4,2 bar | **température −50 → +150 °C** |
| `0xC3BA` (13 axes) | 2231 → 4081 | pression | **−50 → +135 °C** |
| `0xC3B0` (5 axes) | 2531 → 3931 | pression | **−20 → +120 °C** |
| `0xC5A4` | 2431 → 3331 | pression | **−30 → +60 °C** |
| `0xC5FA` | 2331 → 3631 | pression | **−40 → +90 °C** |
| `0xC5FE` | 2431 → 3931 | pression | **−30 → +120 °C** |
| `0xC588` | 2631 → 3331 | pression | **−10 → +60 °C** |
| `0xD3CC` | 2231 → 4231 | pression | **−50 → +150 °C** |
| `0xD230/232/234` | 2531 → 2931 | pression | **−20 → +20 °C** |
| **`0xC586`** | **3731 → 8731** | — | **100 → 600 °C = température des gaz d'échappement (sonde EGT, FAP)** |
| `0xD5A2` | 4731 → 5731 | — | **200 → 300 °C** (plage de régénération FAP) |
| `0xD094` | 2731 → 4051 | — | **0 → 132 °C** |

**Trois vérifications indépendantes de la conversion :**

1. La constante **`0x0AAB` = 2731** apparaît dans le code comme **offset** : `unk_20AC(word_C904 − 0AABh, r6, #2710h) + 0AABh` (listing 131780-131786) — c'est l'interpolation d'une température **entre 0 °C et un maximum**, ce qui n'aurait aucun sens avec une pression.
2. Toutes les étendues du groupe tombent dans **−50…+150 °C**, plage exacte des capteurs de température d'un calculateur diesel (eau, air, gasoil).
3. `0xC586` (100–600 °C) ne peut être qu'une **température de gaz d'échappement** — cohérent avec le **FAP** de la 4HX.

**Conséquences sur les cartes déjà identifiées :**

| Carte | Axe X | Axe Y (corrigé) | Sortie | Nouvelle lecture |
|---|---|---|---|---|
| `0xE80A0` | régime 100→1000 | `C3D2` **temp. −25→+100 °C** | 1300→12500 | correction/valeur à froid |
| `0xE8444` | régime 0→5200 | **`C3E6` débit d'air 3,0→11,5 g/s** | 0→7600 | **loi de RCO (EGR ou N75)** |
| `0xE86F4` | régime 0→1760 | `C3D2` temp. −30→+80 °C | 0→9230 | post-démarrage / froid |
| `0xE880A` | régime 1300→4000 | `C3D2` temp. 111→122 °C | 0→7040 | protection thermique |

Et votre remarque sur les **RCO sans unité physique** est la bonne : les sorties `2482 → 7600` se lisent très bien comme **rapport cyclique en 0,01 %** (24,82 % → 76,00 %), et les seuils `word_C690` / `word_C626` que j'avais appelés « bornes d'intégrateur » sont alors des **plafonds / planchers de RCO** — ce que vous soupçonniez. Les mots « ce sont des plafonds » sont donc cohérents avec la structure du code (`mov word_C690, r4` puis comparaisons `cmp` avec des consignes).

---

## 2. « Datensatz » : d'où vient ce mot, et ce qu'il y a vraiment dans le fichier

**Réponse honnête : le mot n'est PAS dans le binaire.** Vérifié par recherche de chaîne sur les 524 288 octets :

| Chaîne cherchée | Occurrences |
|---|---|
| `Datensatz` / `DATENSATZ` / `datensatz` | **0** |
| `Kennfeld` / `KENNFELD` | **0** |

« **Datensatz** » est un mot **allemand** qui signifie « **jeu de données / ensemble de données** » (littéralement « l'ensemble de ce qui est posé là »). C'est la terminologie **Bosch** pour désigner le bloc de **données d'adaptation/calibration** d'un calculateur — je l'ai employé comme étiquette de travail, pas comme une donnée lue. Il faut donc le lire comme « **zone de calibration** ».

Ce qui est réellement **observé** dans le fichier :

| Élément | Adresse | Nature |
|---|---|---|
| Signature `55 55 00 00` puis table de 151 dwords | `0xE0000` (et `0xF0000`) | en-tête de la zone de calibration |
| Enregistrements `<tag><n><n valeurs>` + grilles | `0xE1000` → `0xEBEFF` | **axes, cartes 2-D, courbes** (§4) |
| Bloc d'identification | `0xEBF00` | `75vGB075WF2S010384`, `__NWGDWPF1`, `1037353776` (doublon en `0xFBF00`, où le 2ᵉ se lit `__NFGDWPF1`) |
| Numéro de logiciel Bosch | `0xFCC00` | **`0281010877`** (= 0 281 010 877, la référence du calculateur) + `B075WF2S01` |
| Variante de calibration | `0xF0000`–`0xFFFFF` | même arborescence, **14 147 octets différents** (bloc `0xEC000`–`0xEFF5F`) |

Le terme correct pour ce que nous analysons : **zone de calibration (segments `0xE` et `0xF`)**, contenant **axes + cartes + courbes + bloc d'identification**.

---

## 3. Typologie des données rencontrées (types réels, pas théoriques)

| Type | Où c'est prouvé | Échelle / unité observée |
|---|---|---|
| **Mot 16 bits non signé** | 96 des 98 tags ; toutes les grilles et tous les axes | variable selon le tag (§ tableau) |
| **Octet 8 bits** | 2 tags seulement : `0xC337` (0→250), `0xD369` (0→255) — **adresses impaires** | brut 0…255 |
| **ADC 10 bits brut** | ~20 tags `0xD0xx` avec étendues 0…1023, 10…991, 32→1023… | **entrées analogiques brutes** (avant conversion) |
| **Valeur « signée » 16 bits** | `0xC5BC` (32768→36128), `0xD356` (60036→61046) | si relu en signé : −32768→−29408 et −5500→−4490 ⇒ **grandeurs pouvant être négatives** (à confirmer) |
| **Régime** | `0xC42E` : 104 axes, 0→6000 | **tr/min**, pas de mise à l'échelle |
| **Température** | 13 tags (§1) | **K × 10** (2731 = 0 °C) |
| **Débit d'air** | `0xC3E6` : 2 axes, 3000→11500 | **mg/s** (confirmé) |
| **Quantité / consigne** | `0xC6DA` (118→10000), `0xC562` (0→20000), `0xC5A8` (100→11000) | **0,01 mg/hub** probable |
| **Rapport cyclique** | sorties de cartes 2482→7600, 1300→12500 | **0,01 %** probable |
| **Grilles** | 44 cartes | **toujours des mots** (aucune grille d'octets détectée) |

Fichier joint : **`tags_inventaire.csv`** — 98 tags avec `type ; nb d'axes ; min ; max ; unité proposée ; copie de travail ; nb d'appels 2-D ; nb d'appels 1-D`. *(Le classement automatique de l'unité est une proposition : quelques lignes restent à trancher, par ex. `0xC3EC` = 700→850 lue comme régime de ralenti et non comme ADC, `0xD072/D080/D082` = petits compteurs.)*

**Rappel structurant (étape 8)** : le « type » d'une donnée est **porté par son adresse** — parité (impair = octet), et c'est l'étendue des axes qui fixe l'échelle. Les tags **sont** les adresses du banc d'interface `0xC3xx`–`0xC8xx`, recopiées dans le banc de travail `0xC9xx` au début de chaque tâche.

---

## 4. Inventaire des cartes, courbes et valeurs

### 4.1 Cartes 2-D — 44 cartes distinctes (× 2 segments)

Décodées dans la zone de calibration (étape 7), validées par la fermeture des enregistrements. Fichier : **`cartographies_datensatz.csv`**.

Appelées dans le code par **`unk_1D50(descripteur, x, y)`** — **72 sites** d'appel, dont :
* `r13` (axe X) = **régime** dans **37** cas ;
* `r14` (axe Y) = débit d'air `C3E6` (3), température (via `C908`/`C904`), quantité `C952`, etc.

### 4.2 Courbes 1-D — **168 appels** dans le code

Appelées par **`unk_1D36(descripteur, x)`** (2 arguments seulement). Fichier : **`appels_unk_1D36.csv`**.

| Descripteur | Appels | Descripteur | Appels |
|---|---|---|---|
| `word_18CE` | 7 | `word_18C0` | 3 |
| `word_18B6` | 5 | `word_1628`, `word_1638`, `word_18B4`, `word_19B6`, `word_1B5C`, `word_1E28`, `word_1E2E` | 2 chacun |
| `word_162A`, `word_1B4E` | 4 chacun | + une trentaine à 1 appel | |

Entrée des courbes (`r13`) :

| Source | Appels | Grandeur |
|---|---|---|
| `word_C91C` | 33 | **régime** |
| `word_C908` | 21 | **température** (copie de `C3D2`) |
| `word_C904` | 14 | **température** (copie de `C3BA`) |
| `word_C940` | 11 | copie de `C60A` (régime/charge) |
| `r9`, `[r0+#2]`, `r4` | 28 | valeurs locales (résultats intermédiaires) |

→ **Les courbes 1-D sont massivement des corrections de température et de régime** : c'est exactement la structure d'un EDC15 (corrections de débit et d'avance en fonction de T°eau/T°air/T°gasoil).

### 4.3 Valeurs scalaires (paramètres)

Ce sont les mots lus aux **offsets des blocs descripteurs** `0x14xx`–`0x17xx` (couche C de l'étape 8, en mémoire basse absente — on ne voit que les **offsets utilisés**) :

| Bloc | Offsets déjà cartographiés | Rôle |
|---|---|---|
| `0x141C` | +1,+2,+4,+6,+8,+9,**+0Ah**,+0Fh,+18h,+27h | **octets de coding/variante** (`byte_C2C9` ← `[+0Ah]`) |
| `0x141E` | +2,+4,+8,+14h,+29h,+2Ah | paramètres de fonction + drapeaux |
| `0x1430` | +0,+2,+4,+6,+8,+0Ah,+0Ch,+0Eh | bornes de régime, offsets |
| `0x1432` | +0 (consigne), +2 (repli), +16h, +1Eh, +20h | réglages du régulateur |
| `0x1438` | +0,+2,+4,+6,+8,+0Ah (seuil débit), +0Ch,+0Eh,+10h,+12h,+16h,+18h | seuils de diagnostic |
| `0x147E` | +0,+2 (bornes), +8,+0Ah | bornes de quantité |
| `0x149C` | +0Ch (facteur /1000) | normalisation |
| `0x15F0` | **+0 (base de conversion du débit)**, **+4 (valeur de remplacement du débit d'air)** | conversion + défaut |
| `0x1708` | +0,+2,+4,+6,+0Ch,+0Eh (facteur de gap ×10000), +14h | synchronisation 60-2 (étape 2) |

### 4.4 Ce que le décodage binaire ne couvre pas encore

Le parseur d'enregistrements de la zone de calibration reconnaît **80 cartes 2-D + 92 axes isolés** mais ne couvre que **26 %** de la zone `0xE1000`–`0xFBF00`. Il reste donc **des types d'enregistrements non décodés** (probablement : blocs de paramètres scalaires, cartes en octets, tables de correspondance). Piste : la zone `0xE1000`–`0xE10F0` est un **catalogue d'axes** (une soixantaine de « Stützstellen » consécutives, sans grille) — c'est un type d'enregistrement à part entière.

---

## 5. Entrées / sorties du calculateur — état des preuves

### Entrées

| Grandeur | Preuve | Statut |
|---|---|---|
| **Régime + synchro** (60-2, P2.6/CC6IO ; AAC P2.13/CC13IO) | `PECC5=7Fh`, `word_FCF4/FCF6`, étapes 1-3 | **prouvé** |
| **Débit d'air** `C3E6` (mg/s) | étape 8 + confirmation | **prouvé (grandeur)**, capteur exact à confirmer (débitmètre fil chaud) |
| **Températures** (eau, air, gasoil) `C3D2`/`C3BA`/`C3B0` | §1 (K×10) | **prouvé (grandeur)** |
| **EGT** `C586` (100→600 °C) | §1 | **très probable** (sonde FAP) |
| **Canaux ADC bruts** (tags 0…1023) | ~20 tags `0xD0xx` | **prouvé** (ce sont des entrées analogiques non converties) |
| **Consigne de quantité** `C6DA` | axe de la carte de quantité (étape 6) | **haut** |

### Sorties

| Grandeur | Preuve | Statut |
|---|---|---|
| **RCO EGR / N75** | valeurs de cartes 2482→7600 (0,01 %) + plafonds `word_C690`/`C626` | **plausible, non prouvé** : l'étage de sortie (compare CAPCOM) est **absent de l'image** (constat négatif étape 2 : aucune paire double-registre active) |
| **Avance / durée d'injection** | étapes 5-6 : `word_D404`, `word_C69C`, `word_C69E` | borné mais **conversion finale hors image** |
| **Actionneurs FAP** (post-injection, 5ᵉ injecteur) | non trouvé | **à chercher** — question prioritaire pour une 4HX FAP |

**Le point dur reste le même depuis l'étape 2** : la **moitié basse de la flash (`0x00000`–`0x7FFFF`) est absente de l'image**, et c'est là que vivent l'OS (descripteurs `0x14xx`–`0x17xx`, tokens de tâches) et l'étage de sortie. Tout ce qui concerne les **registres d'actionneurs** ne pourra pas être prouvé sans cette moitié.

---

## 6. Prochaines étapes proposées

1. **Compléter le décodage de la zone de calibration** (74 % non reconnus) : chercher les enregistrements « paramètres scalaires » et les éventuelles cartes en octets → cela donnerait la liste **complète** des valeurs utilisées (pas seulement celles dont on voit les offsets).
2. **Nommer les 98 tags** par recoupement : étendue + consommateurs + voisinage dans la zone. Objectif : passer de « `0xC3D2` » à « température d'eau » ou « température d'air ».
3. **Chercher la voie FAP** : les tags `0xC586` (EGT) et `0xD5A2` (200–300 °C) sont des axes de courbes → remonter aux cartes de **régénération** (post-injection, dosage).
4. **Trancher RCO EGR vs N75** : suivre `word_C690` (`loc_B26D2`) jusqu'à son écriture finale et au registre de compare.
5. **Reconstituer la moitié basse** (secteur boot `0xFC000`, étape « PLAN_RECUPERATION ») : c'est la seule voie pour les sorties.
