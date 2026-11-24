# EDC15C2 / PSA 2.2 HDi 4HX — DOSSIER DE REPRISE

> **But de ce document** : permettre à un nouveau chat, sans aucun historique, de reprendre le projet
> exactement là où il s'est arrêté — sans refaire le travail déjà fait, et **sans répéter les erreurs
> déjà commises**. Il est autosuffisant : tout ce qui est affirmé ici est adossé aux fichiers du paquet.
>
> Version du dossier : **fin d'étape 125** (audit adversarial). 125 documents, 54 CSV.

---

## A. En trente secondes

On rétro-documente un calculateur **Bosch EDC15C2** monté sur **Peugeot 406 2.2 HDi 4HX FAP** (full-mux,
3 broches). Objectif : comprendre et documenter, preuve en main, la chaîne de mesure, le CAN, la pédale, le
rapport engagé (FGR), la régulation, la chaîne « souhait conducteur → injecteurs », et tout le filtre à
particules. Le binaire est désassemblé par IDA ; chaque affirmation doit être vérifiable dans `clean.asm`
ou `edc.bin`.

**Ce qui est solide** : l'adressage de la calibration, les 86 cartes 2-D, les courbes 1-D, le registre des
385 appels d'interpolation, la voie FAP complète, la chaîne de conversion des quantités d'injection.

**Ce qui n'est pas prouvé** : le lien handle→adresse (validé empiriquement, jamais prouvé par le code),
les **noms** des axes, l'unité mm³ (elle vient de l'utilisateur), et l'absence de post-injection séparée.

---

## B. Les sources et leur empreinte — à vérifier AVANT tout

| Fichier | Taille | SHA-256 | Rôle |
|---|---|---|---|
| `01_SOURCES/edc.bin` | 524 288 o | `a31de40386f9eb24748fa60163d0406f96b2597d58cc3178918511db0902dcea` | **le binaire. source de vérité n°1** |
| `01_SOURCES/clean.asm` | 412 022 l. | `981542b8ff5444c46dc23491aa60723338b376ba0182805ec68a5bd01b61aec6` | **le désassemblage IDA nettoyé. source de vérité n°2** |
| `01_SOURCES/edc.asm` | 12,4 Mo | — | désassemblage IDA d'origine, non nettoyé |
| `01_SOURCES/recon.bin`, `recon_partielle.bin` | 512 Ko | — | reconstructions intermédiaires (outillage) |
| `01_SOURCES/edc_2nde_20kmh.bin` | 524 288 o | — | **le seul patch produit** (voir §L) |

**Règle absolue** : si le SHA-256 de `edc.bin` ou `clean.asm` ne correspond pas, **tout le dossier perd sa
valeur**. Ne pas continuer avant d'avoir vérifié.

**Ne jamais éditer `edc.bin` en place.** Travailler sur une copie.

---

## C. Modèle d'adressage — la pierre angulaire

### C.1 Les formules

```
Conversion fichier → adresse d'exécution (image de 512 Ko) :
    EA = fo + 0x80000                      (valable pour TOUTE l'image)

Table de pointeurs de la calibration :
    entrée = u16 @ (0x60000 + h)           ← DÉCALAGE EN OCTETS (≡ 0x61400 + (h − 0x1400))
    EA_cible = 0xE0000 + entrée

Structures de calibration :
    1-D : [tag][n][axe n mots][valeurs n mots]
    2-D : [tagY][nY][axeY][tagX][nX][axeX][grille nY×nX]
    → Aucun mot séparateur. Axes croissants. Petits-boutistes.
    → Règle de lecture d'une grille : valeur[k] ↔ axe[k+1]
```

### C.2 Statut de cette formule — à lire attentivement

**Elle n'est pas prouvée par le code.** Aucune instruction de `clean.asm` ne lit `0x61400` : `grep` sur
412 022 lignes ne renvoie rien. C'est une **inférence**, validée empiriquement de façon très forte :

- les **6 courbes FAP** re-dumpées par cette formule ont exactement les tags, dimensions, axes et valeurs
  attendus (6/6) ;
- **298 structures** de calibration se parsent proprement avec elle ;
- les **385 entrées** du registre d'appels se re-dérivent à l'identique (348 non vides, **0 désaccord**) ;
- la formule concurrente « base RAM 0x1000 » ne donne que **1,5 %** de structures valides — elle est éliminée.

**Piège vécu (errata E41)** : écrire `0x61400 + 2×(h−0x1400)` (lecture en mots) donne **9,3 %** de validité
et fait croire que tout est faux. La formule est un décalage **en octets**.

### C.3 Autres conversions utiles

```
Segment E (données) :  fo = 0x60000 + (EA − 0xE0000)
Pages 0x9xxxx       :  fo = EA − 0x80000
Handle -> variable  :  h est l'adresse de la variable pointeur (word_XXXX en RAM)
Offset 0x1400 en RAM = première entrée de la table (0x60000 + 0x1400 = 0x61400)
```

---

## D. Carte de l'image (vérifiée par runs de `0xC3`)

| Plage EA | Taille | Contenu |
|---|---|---|
| `0x80000` – `0x87FFF` | 32 768 o | padding `0xC3` (100 %) |
| `0x88020` – `0xD5414` | **316 405 o** | **CODE** |
| `0xD5415` – `0xDFFFF` | 44 011 o | stub de 16 o + padding `0xC3` (100 %) |
| `0xE0000` – `0xFBFFF` | **114 688 o** | **CALIBRATION** (cartes, courbes, Datensatz) |
| `0xFC0EA` – `0xFEB22` | 10 809 o | **CODE** (queue) |
| `0xFEB23` – `0xFFFFF` | 5 341 o | boot / vecteurs |

⇒ **Le code utile est intégralement présent dans `clean.asm`.** Il n'existe aucune zone de code cachée.
Corollaire : on ne peut **plus** dire « telle fonction est dans la moitié non désassemblée ». Si elle
n'apparaît pas, elle n'existe pas dans ce logiciel.

**Duplication `0xF0000`** : le bloc `0xE0000`–`0xEFFFF` est recopié à l'identique en `0xF0000`–`0xFFFFF`
(vérifié à l'octet). Toute modification de calibration doit donc être **appliquée deux fois** — c'est le
piège n°1 du projet. Le padding de `0xEF880` est réel (run `0xEBFBA`–`0xEFFFF`, 16 454 o).

**Identité du calculateur** (vérifiée) : `1037353776` présent 3× (`EA 0xEBFB0`, `EA 0xFBFB0`, `EA 0xFFEF0`) ·
`0281010877` présent **1×** à `EA 0xFCC00` · `0281010597` **absent du fichier** ⇒ ce binaire est bien un
**full-mux 2.2 HDi**, pas un semi-mux.

---

## E. État des connaissances, par domaine

Niveaux de confiance : **P** = prouvé par le code · **V** = validé empiriquement sur les données ·
**A** = affirmation de l'utilisateur (non vérifiable dans le binaire, tenue pour acquise) · **?** = hypothèse.

### E.1 Chaîne de mesure et Datensatz
- 21 voies de mesure, **2 EGT + 1 EGT estimée** ; pressions différentielles FAP ; 3 températures. (**V**)
- Datensatz stocké en **deux exemplaires complets** (d'où la duplication). (**V**)
- Variables connues : `C42E` régime · `C952`/`C6DA` pédale · `C3D2`/`C908` T° LDR · `C3B0`/`C900` T°
  carburant · `C562` vitesse · `C576` rapport · `C7C2` pression rail ×10 · `C60A` T° air.
  ⚠️ **Les NOMS de ces variables sont des hypothèses de plage (55 %), pas des preuves** — voir §H.
- Identifiants → RAM : `0F00→C3D2` (T° LDR), `0F02→C3B0` (T° carburant), `0F41→C60A`, `0F08→C562`,
  `0F0B→C576`, `0F10→C42E`. (**V**, table `identifiants_vers_RAM.csv`)

### E.2 CAN (**A**, non vérifiable dans le binaire)
- Vitesse = trame `0x38D`, `u16` big-endian `/100` km/h → `C811`. Roues : `0x412` → `C87D`. `0x468` option.
- Bus 250 kbit/s, 10–20 ms. Le **rapport n'est jamais reçu par CAN** : il est **calculé** dans l'ECU.

### E.3 Pédale (**A** + **V**)
- 0–100 % codé **0–10000** sur **deux** signaux (4,5 V et 5 V, l'un = moitié de l'autre). Tâche `0x326`.
- ⚠️ Erreur historique corrigée : `C18C & 80h` **n'est pas** un bit de pédale.

### E.4 Rapport engagé / FGR (**A** pour les seuils, **V** pour le calcul)
- `ratio = (C578 × 256) / C42E` → `C576 = C93E` ; `byte_C330 & 0x10` = 4ᵉ et plus.
- Barème de `0xE81A4` : 202–234→01 · 234–338→0B · 338–559→02 · 559–826→03 · 826–1116→04 · ≥1116→05.
- Le rapport sert à : (a) l'agrément d'injection, (b) l'autorisation du régulateur, (c) la **limitation de
  couple en 1er/2e**. (**A**)
- Seuils FGR 16 bits LoHi : `vMin` 4000/4500/5000 · `vMax` 22000/25000 · `nMin` 1200/1300 · `GangMin` `04 00`.
- BVM/BVA vient de l'**EEPROM de codage**. (**A**)

### E.5 Chaîne souhait conducteur → injecteurs (document `ETAPE121`, **V/P**)
19 cartes, toutes avec site d'appel :
```
0xE8BD4 si C576<539 sinon 0xE8B50   (seuil 0xE8C58 = 539, VÉRIFIÉ)
  → C6A6 → smoke map 0xE8444 (16×16, grille 0xE848C) → C690 (9 sites)
  → C698/C680 → 0xE87D6 → 0xE8000/0xE7F7E → D8C4
  → 0xE80A0/0xE86F4/0xE868C/0xE880A/0xE3908 → 0xE13DC → 0xE2078/0xE211A
  → C682/C688 → 0xE8A06  ⇒ byte_C8F8 (commande de POMPE, pas une IQ)
  arbitrage : C6B8 → C6A4 → D9AA → C6AE → C6AA → sub_AF75A → C6B2
```
- `0xE8A06` → `byte_C8F8` **confirmé** : l. 182810-182814, `mov r12, word_1B5E` / `calls unk_1D50` /
  `movb byte_C8F8, rl4`. **Ce n'est pas une cascade de fumée** (errata E30).
- Les deux cartes de souhait ne diffèrent que de **5 cases sur 48**, toutes en colonne pédale 2000
  (`2400/2132/1844/1520/1260` vs `2350/1782/1344/1070/910`) — **vérifié à l'unité**.
  ⇒ patcher `0xE8BD4` est quasi invisible ; le levier réel est `0xE8444`.
- Courbe plein gaz `0xE83F4` (19 pts) : 1000→44,9 · 1500→66,6 · **2000→74,3** · 2500→70,6 · 3000→68,1 ·
  4000→62,4 · 4800→47,5. ⚠️ **Axe et valeurs ne sont pas alignés index à index.**

### E.6 Régulateur (tâche `0x340`)
- Cartes « inversées » remplaçant la pédale, sauf en cas de dépassement ; surveille frein, embrayage,
  régime, vitesse. (**A**)
- Consommateurs du souhait : chaîne `ETAPE113`→`119`.

### E.7 FAP / régénération / post-injection (documents `ETAPE10` à `ETAPE14`, réaudités en `ETAPE124`)
**Architecture complète (P/V) :**
```
word_141C[+27h] → byte_C2BA  (1 seule écriture, l. 151775 ; 63 lectures) = présence FAP
tâche 0x12C (l. 163238, scxt CC2_CC27, #12Ch) — gardée par byte_C2BA
  état : byte_D7A8 ∈ 0..5, table de sauts en 0xA04
  drapeaux : byte_D7B8  (bit1 fenêtre charge/régime · bit2 ⇒ mode 8 · bit4 = DEMANDE · bit 8 · 0x80)
  intégrateur de suie : word_D7B0 += unk_20AC(x,#1,#0x64), saturation 0x7FFF/0x8000,
                        plafond [word_1904+0x16]
  seuil : word_D7B2 = courbe EGT (byte_D7B8 & 2) ; recopié dans word_D294 (0 lecteur = miroir)
  déclenchement : D7B0 > D7B2 ⇒ byte_D7B8 |= 4
  fin de cycle : D7B0 := 0 ; D28E := 0
```
**Six courbes FAP, toutes 1-D** (aucune carte 2-D n'a un axe FAP sur 86) :

| Handle | EA | tag axe | axe | valeurs | rôle |
|---|---|---|---|---|---|
| `0x191E` | `0xE5F9C` | `C586` | 5231, 8231 | 100, 3200 | seuil bas |
| `0x1922` | `0xE5FC0` | `C586` | 5231, 8731 | 100, 32767 | seuil haut ⇒ régén. impossible |
| `0x1950` | `0xE639A` | `C586` | 3731…8531 | 7231…5131 | limitation décroissante |
| `0x18A2` | `0xE4D14` | `D1B6` | 500…11000 | 117…655 | EGT normalisée |
| `0x18A4` | `0xE4D38` | `D1B6` | 500…11000 | 15…260 | variante |
| `0x1DFA` | `0xEBA84` | `D5A2` | 4731, 5731 | **10000, 10000** | **neutralisée** |

**Post-injection : il n'en existe pas de séparée (80 %).** La régénération **élargit le temps principal** :
- `word_C69E` ∈ [0, 60 mm³] — 1 écriture l. 187528 ; `clamp(BDBC|BDDC selon BDAC&1, 0, 6000)` ;
  porte `byte_C8EB == 1` ; `[word_1434] & 0x80 = 0` ⇒ pas de doublement.
- `word_C77C` = `0xE6B86[0,0]` + `0xE6B92[1000,1000]` = **1000 constant (+10 mm³)**.
- `sub_ACD46` (l. 172038) = `mov r4,#1` / `rets`, **XREF unique** `loc_ACFC6` ⇒ la branche additive est
  **inconditionnelle**.
- `word_D5A2` : 1 écriture l. 204416, **0 lecture** ⇒ miroir télédiag. Sa table `0xEBA84` est neutralisée.

### E.8 Diagnostic / DTC / EEPROM
- 96 descripteurs de défauts, records de 32 o, mémoire des défauts en segment E.
- `byte_C820` = octet d'**état** (code cylindre `C330 & 0F` comparé à `word_1656[0..7]` → index, `shl #4`,
  `orb #8` si `C2BA` & `C297`). `byte_C821/C822/C823/C824` ← `C642`/`C63A`/`C63C`/`C63E`, saturation `0xFE`.
- ⚠️ **Ces octets ne commandent PAS les injecteurs** : 1 écriture et **0 lecture** chacun. Leur seul accès
  indirect est `sub_9CFD0`, qui **lit** le bloc pour le mémoriser (record de 16 o indexé par `r12`,
  identifiant dérivé de `r15`, copie de `n` octets depuis `r14`). Voir errata E32/E38.

---

## F. Cartes et courbes — où est la vérité

| Élément | Nombre | Fichier de référence | Statut |
|---|---|---|---|
| Cartes 2-D | **86** | `03_DONNEES/inventaire_cartes_2D_axes_v2.csv` | **exact à 100 %** (double scan, 0 désaccord) |
| Courbes 1-D | 182 | catalogue §4 | à re-vérifier |
| Appels d'interpolation | **385** | `03_DONNEES/registre_appels_interpolation.csv` | **385/385 lignes exactes**, 0 désaccord d'EA |
| Cartes 2-D sans aucun site d'appel | **8** | `ETAPE125` §3 | **inédit** — voir §I |

⚠️ Les chiffres **66** (catalogue §5) et **91** (errata 57) sont **FAUX**. Le bon chiffre est **86**.

**Les 8 cartes orphelines** (aucune référence nominale dans 412 022 lignes) : `0xE22F4` (h. `0x1482`),
`0xE230C` (h. `0x1484`), `0xE3B2C` (h. `0x15FC`), `0xE6306` (h. `0x1946`), `0xE7D44` (h. `0x1A54`),
`0xE7DAC` (h. `0x1A56`), `0xEAFB2` (h. `0x1DB8`), `0xEBB46` (h. `0x1E1A`).
⇒ la règle « aucune carte sans site d'appel » n'est satisfaite que pour **78/86**.

---

## G. Errata — les erreurs déjà commises, à ne pas refaire

Registre complet : `02_DOCUMENTS/CATALOGUE_MAITRE.md` §10. Les plus dangereuses :

| Réf. | Erreur | Correction |
|---|---|---|
| **E30** | `0xE8A06` présentée comme « cascade de fumée » | c'est la **commande de pompe** (`byte_C8F8`, octet) |
| **E31** | `D3D4` pris pour une variable propre | c'est une **copie de `D9AA`** |
| **E32→E38** | `C820`–`C829` = « commande des injecteurs » | 1 écriture, **0 lecture** ; `sub_9CFD0` est une routine de **mémorisation** |
| **E33** | `word_C642` = quantité absolue | **écart signé** `r6 − C640` |
| **E34** | `word_C69E` = 6 sites | **11 sites** de code (5 `add` + 4 `sub` + 1 lecture + 1 écriture) |
| **E35** | `word_C586` = 8 sites | **9 sites** de code |
| **E36** | `word_D294` = consigne de régénération | recopie de `D7B2`, **0 lecteur** |
| **E37** | 66 / 91 cartes 2-D | **86** |
| **E39** | — | **8 cartes orphelines** (voir §F) |
| **E40** | « les `l.N` sont décalés de 1 à 20 » | vrai pour la **prose** ; **faux pour les CSV** (385/385 exacts) |
| **E41** | formule d'adressage lue en mots | `u16 @ (0x60000 + h)`, décalage **en octets** |
| **56** | conclure sur un ratio de tags | méthode **condamnée** : un nom d'axe n'est pas prouvé par sa plage |
| **57** | 91 cartes | voir E37 |

**Règle de méthode qui découle de tout ça** : ne jamais reprendre un « N sites » sans le recompter ;
citer **le label + l'EA**, la ligne en secours.

---

## H. Ce qui n'est PAS démontré — à ne pas présenter comme acquis

1. **Le lien handle → adresse** : validé empiriquement (§C.2), jamais prouvé par le code.
2. **Les noms des axes** (`C42E` = régime, `C6DA` = pédale…) : hypothèses de plage. Confiance **55 %**.
   Les **valeurs** sont prouvées ; les **noms** non. C'est exactement la faute condamnée en errata 56.
3. **L'unité mm³** : vient de l'utilisateur, aucune preuve interne. Confiance **60 %**.
4. **`unk_20AC(…, 0x2710)` = plein échelle** : `0x2710` existe dans le code mais **pas dans `unk_20AC`**
   (bibliothèque absente, remplie de `0xC3`).
5. **La nature de `sub_9CFD0`** : la lecture du bloc est établie, la destination ne l'est pas.
6. **« Le code est couvert à 100 % »** : solide, mais repose sur l'hypothèse que tout run ≥ 64 o de `0xC3`
   est du remplissage.
7. **L'absence de post-injection séparée** : conséquence de 1 et 6. Confiance **80 %**.

---

## I. Chantiers ouverts, par ordre de rentabilité

1. **Trouver ce qui écrit la table `0x61400`.** C'est la seule façon de transformer l'inférence
   d'adressage (§C.2) en preuve. Piste : routines de démarrage, bloc `0xEF000` (celui qu'indexe
   `sub_9CFD0`), et les 5 120 mots de la table.
2. **Trancher le sort des 8 cartes orphelines** : calibration morte ou accès calculé ?
3. **Cartographier `sub_9CFD0`** : tous les couples (index de record, identifiant) appelés → liste
   officielle des blocs mémorisés. Cela nommerait `0x348` et `0x388`.
4. **`byte_C8EB`** (64 références) : porte du terme `C69E`. Déterminer son origine.
5. **`word_BDAC`/`BDBC`/`BDDC`** : origine de la quantité additionnelle ; confirmer l'unité.
6. **Capteur de pression différentielle** : `ETAPE12` le donnait pour non localisé (« loi cubique ») ;
   à reprendre avec la carte d'image (§D) — le conditionnement est forcément dans `0x88020`–`0xD5414`.
7. **Courbes 1-D** : les 182 du catalogue §4 n'ont pas été re-vérifiées comme les 86 cartes 2-D.
8. **Requalifier les noms d'axes** avec une méthode qui ne soit pas la plausibilité de plage.

---

## J. Règles de travail imposées par l'utilisateur — non négociables

1. **Ne rien inventer.** Toute affirmation doit être adossée à `clean.asm` ou `edc.bin`.
2. **Preuve d'injection** = présence de `1F40`/`1F41`/`1F4D`/`2109` dans le **code**.
3. **Pas de « carte à plat / à zéro »** sans dump complet des `n1×n2` mots.
4. **Nommage** : `ETAPE<n>_*.md`, sections `B.<n>` dans le catalogue. Errata **explicites**, jamais silencieux.
5. **Traçabilité de chaque carte** : `tagY`/`nY`/`axeY`/`tagX`/`nX`/`axeX`/`grille`.
6. **Le code d'abord**, les cartes ensuite. Aucune carte sans site d'appel.
7. **Une carte 2-D a besoin de 2 paramètres X et Y** ; la vitesse n'a rien à voir avec le couple.
8. **L'ECU ne travaille qu'en quantité injectée (mm³)**. Les unités « N.m » sont **rejetées**.
9. **Checksums = sujet abandonné.** Ne pas reproposer de recalcul ni de protocole.
10. Sur la courbe plein gaz, **74,3 mm³ est à 2000 tr/min** ⇒ axe et valeurs **ne sont pas** alignés
    index à index.
11. **Duplication** : toute modification de calibration doit être appliquée aux **deux** copies.
12. Faits de référence : `0xEF880` = padding (≠ `0xF884`) · facteur d'angle `0,0234375 °CRK/pas` ·
    `C7C2` = pression rail × 10 · températures en **K×10** · pédale 0–10000.
13. **HW `0281010877`** = 2.2 HDi **full-mux 3 broches** ; **`0281010597`** = semi-mux 4HX.

---

## K. Boîte à outils — ce qui marche, ce qui est dangereux

| Fichier | État | Remarque |
|---|---|---|
| `04_OUTILS/parse.py`, `addr.py`, `addr2.py` | OK | parsing du désassemblage, construction des index |
| `04_OUTILS/edc15_analyze.py` | OK | analyse de la calibration |
| `04_OUTILS/patch_2nde_20kmh.py` | OK | génère `edc_2nde_20kmh.bin` |
| `04_OUTILS/ida_sweep_zones.py` | OK | balayage des zones |
| `04_OUTILS/genere_catalogue.py` | OK | génère le catalogue ; **appeler `compile()` avant tout patch** |
| `04_OUTILS/ctx.py` | ⚠️ | lève un `TypeError` selon le contexte Python |
| `04_OUTILS/dump_handles.py` | ❌ **FAUX** | utilise `0x61400+(h−0x1400)` **en mots** ⇒ formule erronée (voir E41) |
| `04_OUTILS/segmente_blocs.py` | ❌ **NE PAS RELANCER** | a produit des artefacts |

**Pièges d'outillage déjà rencontrés** : `%X format: an integer is required` et `bitwise_and` sur `uint64`
numpy ⇒ caster. Les CSV utilisent `;` comme séparateur — et **8 lignes du registre contiennent un `;`
dans un champ** (`"#64h ; 'd'"`), ce qui casse un `split(';')` naïf : parser avec le module `csv`.

---

## L. Le patch existant

`01_SOURCES/edc_2nde_20kmh.bin` — **8 octets modifiés** : autorise la 2ᵉ et la régulation dès **20 km/h`
au lieu du seuil d'origine. Généré par `04_OUTILS/patch_2nde_20kmh.py`.

⚠️ **Les checksums n'ont pas été recalculés** (sujet abandonné, §J.9). Le patch est donc à considérer comme
**non flashable en l'état**. Ne pas relancer ce chantier sans demande explicite.

---

## M. Index des documents

- `02_DOCUMENTS/CATALOGUE_MAITRE.md` — **le document maître** (~5 300 l.) : conventions, gabarits,
  inventaire des variables, courbes 1-D, cartes 2-D, boucles, registre des erratas (§10), ce qui reste
  à trouver (§11), puis les sections d'étape `B.1` → `B.72`. **Commencer par là.**
- `02_DOCUMENTS/ETAPE1_*` → `ETAPE125_*` — 125 documents d'étape, dans l'ordre chronologique.
  Les plus structurants : **10–14** (FAP), **113–119** (consommateurs du souhait), **120** (pompe,
  smoke map, limitations), **121** (chaîne complète), **122** (fonctions), **123** (audit),
  **124** (audit FAP), **125** (audit adversarial — **le plus à jour**).
- ⚠️ `ETAPE116` et `ETAPE117` portent un bandeau **PÉRIMÉ** en tête.
- ⚠️ `ETAPE10` et `ETAPE121` portent un bandeau de **correction** (errata E32/E34/E35).
- `03_DONNEES/*.csv` — 54 tables. Les trois à connaître : `inventaire_cartes_2D_axes_v2.csv` (86 cartes,
  exact), `registre_appels_interpolation.csv` (385 appels, exact), `identifiants_vers_RAM.csv`.
- `05_REFERENCES/` — manuels C166/C167 (jeu d'instructions, datasheet) et le binaire d'origine.

---

## N. Démarrer dans un nouveau chat — procédure

1. Envoyer le prompt de `00_PROMPT_DE_REPRISE.txt` (ou coller son contenu).
2. Faire vérifier les SHA-256 (`MANIFESTE_SHA256.txt`) : c'est le premier réflexe.
3. Faire relire `ETAPE125` en entier : c'est l'état le plus récent et le plus critique du dossier.
4. Choisir un chantier dans §I et l'attaquer, en respectant §J.

**Ce qu'il ne faut PAS refaire** : re-dériver l'adressage (fait, §C), recompter les 86 cartes (fait),
recompter les 385 appels (fait), re-chercher la post-injection par la porte `sub_ACD46` (fait, §E.7),
relancer les checksums (abandonné), relancer `segmente_blocs.py` (dangereux).
