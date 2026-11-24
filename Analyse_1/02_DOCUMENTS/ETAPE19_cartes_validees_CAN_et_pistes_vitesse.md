# ÉTAPE 19 — Tes cartes validées : ce que ça change. Et le CAN : réponse négative, preuves à l'appui

## 1. Ton arbitrage enregistré

Ordre des cartes, tel que tu le fixes (et tel que je le retiens désormais) :

| rang | enregistrement | EA des valeurs | rôle |
|---|---|---|---|
| 1 | `0xE83F4` | `0xE841E` | **main torque limiter** — tout passe par lui en dernier |
| 2 | `0xE8906` | `0xE8928` | **1ʳᵉ** — couple surmultiplié |
| 3 | `0xE8946` | `0xE8968` | **2ᵉ** — couple surmultiplié |
| 4 | `0xE8986` | `0xE89A8` | **3ᵉ et au-delà** — 100 mm³ = pas de limite propre |

### 1.1 Ce que je retire de mon étape 18

Je maintiens les **faits** mesurés, mais je retire la **conclusion** « pas consommées ». Puisque tu as
validé ces cartes en pratique, elles sont lues : ce que j'ai démontré n'est donc pas leur inutilité,
c'est seulement que **leur adresse n'apparaît nulle part** dans le code ni dans les descripteurs.
Autrement dit : **l'accès n'est pas littéral, il est calculé.** C'est une indication, pas une impasse.

### 1.2 La forme d'accès est maintenant contrainte

Deux mesures de l'étape 18 se recoupent :

- les trois courbes sont **contiguës avec un pas constant de `0x40`** (64 octets = un enregistrement
  complet) à partir de `0xE8906` : `0xE8906 + rapport × 0x40` ;
- dans le répertoire de `0xE1B16`, elles occupent les **indices consécutifs 31, 32, 33**.

⇒ L'accès est donc **nécessairement** de la forme `base + rapport × 64`, ou `répertoire[31 + rapport]`.
Il n'y a pas d'autre possibilité arithmétique. Le sélecteur est donc **un octet 0…2 multiplié par 64**.

J'ai cherché cette multiplication partout : `shl rX, #6` → **6 occurrences dans tout le programme**,
aucune dans un contexte de couple (l'une est une conversion BCD, l. 130925 ; les autres traitent des
mots d'état). Donc, sous cette forme non plus, le chemin n'est pas dans `edc.bin`.

### 1.3 Trois hypothèses, et le test qui les sépare

1. **Le répertoire est lu à l'initialisation** et le pointeur de base est recopié en RAM : alors la
   multiplication par 64 se fait sur le *pointeur*, pas sur un index — ce qui expliquerait l'absence
   de `shl #6`. À vérifier : chercher une copie de 424 octets (212 entrées × 2) vers la RAM au
   démarrage, et un mot RAM contenant `1B16`.
2. **C'est une autre variante logicielle.** `byte_C2B7` code déjà des tâches différentes selon la
   variante ; si le calculateur que tu as validé n'est pas celui de `edc.bin`, la comparaison des deux
   binaires trancherait en dix minutes.
3. **La sélection est faite en amont, par un indicateur de rapport calculé**, et les courbes sont
   lues par un index 0/1/2 produit par cet indicateur — c'est le cas le plus probable si le rapport
   n'est pas mesuré mais estimé (§4.3).

**Changement de méthode que je propose** : arrêter de remonter depuis les cartes, et **descendre
depuis la quantité injectée**. On connaît déjà la chaîne aval ; il faut trouver la variable de
quantité finale et, juste avant elle, le `min`/`cmp` qui l'écrête. Le terme écrêtant *est* la sortie
du limiteur par rapport, et il nous mènera au sélecteur par le chemin inverse. C'est plus sûr.

## 2. L'axe d'air : ton facteur ×10 est confirmé, et il est cohérent

Avec ton ordre de grandeur (**1000-1100 mg par tour moteur**) :

| rpm | soupapes/cycle·s (4 cyl.) | air à 1 000 mg/tour | en unités de l'axe (×10 mg/s) |
|---|---|---|---|
| 1000 | 33,3 /s | 33,3 g/s | 3 330 |
| 2000 | 66,7 /s | 66,7 g/s | **6 670** |
| 4000 | 133,3 /s | 133,3 g/s | 13 330 |

L'axe de la smoke map va de **3 000 à 11 500** (30…115 g/s = **108…414 kg/h**). Le point de
fonctionnement typique (6 670 à 2000 rpm) tombe **au milieu de l'axe** : le facteur ×10 est donc
le bon, et l'axe couvre exactement la plage utile du 2.2 HDi. C'est cohérent avec ton chiffre, et
cela confirme l'erratum de l'étape 18 §5 — à appliquer à **toutes** les cartes dont l'axe X porte
`0xC3E6`, y compris la carte (débit × dP) → seuil.

Note au passage : `0xB2` = 178 apparaît dans une routine de conversion à la ligne 130925
(`div 0B2h` puis `mul 0AAh`) — c'est du BCD/décimal, sans rapport avec nos cartes.

## 3. Le CAN : négatif, et voici les quatre preuves

Tu me proposes la trame ABS → BSI et/ou EDC15C2. J'ai testé le logiciel dans les quatre directions
possibles. Les quatre sont négatives, et elles se recoupent :

**(a) Aucun registre CAN n'est utilisé.** Recherche exhaustive des noms du contrôleur CAN du C167
(`C1CSR`, `C1IR`, `C1BTR`, `C1GMS`, `C1UGML`, `C1LGML`, `C1UMLM`, `C1LMLM`, `C1MCR`, `C1MCFG`,
`C1FCR`, `C1FDR`, `C1FMR`, `C1TRL`, `C1TRR`, `XP0IC`) : **zéro occurrence**. Les seuls registres
CAN présents sont les *déclarations* d'interruption `CAN_0IC … CAN_7IC` ; et `CAN_0IC` n'a **qu'une
seule référence en écriture**, à `sub_8874E+154`, à l'intérieur d'une séquence qui désactive des
interruptions de périphériques non utilisés (l. 96935-96937 : `bclr word_F17E.6`, `bclr IIC_DIC.6`,
`bclr IIC_PEIC.6`). Ce n'est pas une initialisation CAN, c'est une mise hors service.

**(b) Le bloc d'adresses du CAN est entièrement occupé par autre chose.** Le contrôleur CAN du C167
occupe `EF00h–EFFFh`. Or `sub_9CF70` (l. 143770-143812) écrit **16 blocs de 16 octets** à
`0xEF00 + slot×16`, slots `0` à `0x0F` — soit **exactement tout le bloc `0xEF00–0xEFFF`**, avec :

- `+0` = `5595h` (marqueur d'entrée valide) ;
- `+2` = numéro de tâche encodé ;
- `+4` = **zéro, systématiquement** ← c'est précisément l'emplacement du *bit timing* ;
- `+6` = `0xFF00 | (paramètre << 4) | drapeau`.

Écrire zéro dans un registre de *bit timing* rend tout CAN impossible. Donc, soit la variante de
C167 utilisée **n'a pas de CAN** (son RAM va jusqu'à `0xEFFF`, ce que confirment les tests de bornes
`cmp r4, #0EF00h` aux l. 98054/98084/98101), soit le CAN n'est jamais configuré. **Même conclusion
dans les deux cas.**

**(c) Les broches CAN ne sont pas activées.** `RXDCAN`/`TXDCAN` sont des fonctions alternatives de
P4.5/P4.6, sélectionnées par `ALTSEL0P4` / `ALTSEL1P4` / `ODP4`. Ces trois registres sont **déclarés
mais jamais écrits** (0 occurrence), alors que `P4` et `DP4` sont utilisés en port ordinaire
(10 et 5 accès). Les broches restent donc des entrées/sorties normales.

**(d) Aucune trace textuelle.** Le programme ne contient quasiment aucune chaîne : un balayage
complet des chaînes ASCII ≥ 4 caractères ne rend qu'un faux positif (` bSI`). Il n'y a **rien** du
type *vitesse*, *roue*, *ABS*, *CAN*, *rapport* dans le binaire — les noms des paramètres de
diagnostic sont donc **côté outil de test**, pas dans le calculateur.

⇒ **Sur ce logiciel, la vitesse véhicule n'entre pas par le CAN.** Ce n'est pas contradictoire avec
ce que tu sais du véhicule : la trame ABS peut parfaitement exister sur le réseau et aller au **BSI
et au combiné** sans que l'EDC15C2 la reçoive. C'est le cas de figure classique sur cette
architecture : deux mondes qui partagent le véhicule mais pas le bus.

## 4. Où cela laisse la recherche — trois pistes classées

**4.1 Le signal impulsionnel par fil dédié, mesuré en rapport cyclique.**
Le seul dispositif de capture du calculateur est `CC1_CC13`, et il mesure une période **quasi
constante** (fenêtre 9900…10100, ±1 %) avec un seuil à **−5 %** (`word_D898 = 0,95 × D896`, étape 17).
Or c'est exactement la signature d'un **signal à période fixe dont l'information est dans le rapport
cyclique** — le fameux « signal vitesse » PWM que certains calculateurs ABS/BSI envoient. Le canal
alterne deux modes (nibble `M3` = 1 puis 2, l. 174807/174814) : si ces deux modes sont deux **fronts**
de capture, la différence des deux donne la **durée du niveau haut**, donc le rapport cyclique, donc
la vitesse. **C'est la piste la plus prometteuse et elle est vérifiable** : il faut regarder ce que
fait le code de la *seconde* valeur capturée.

**4.2 Le bus I²C.** Le calculateur a bien un I²C actif (`IIC_DIC`, `IIC_PEIC`, `IIC_IR`, et l'attente
`byte_D89F == 0x14` de l'étape 16). Un ABS n'est pas un périphérique I²C, donc cette piste est peu
probable pour la vitesse — mais elle mérite d'être identifiée,ne serait-ce que pour savoir ce qui est
sur ce bus (mémoire ? ASIC de surveillance ?).

**4.3 Le rapport estimé, pas mesuré.** Beaucoup de versions EDC15 n'ont **aucun** capteur de vitesse
côté injection : l'indicateur de rapport est calculé à partir du régime et de la quantité (ou de la
pression de suralimentation), par une petite table. Si c'est le cas ici, les trois courbes sont
sélectionnées par un **indicateur 0/1/2 calculé**, et il n'y a **pas** de vitesse véhicule à trouver
dans le calculateur — ce qui serait cohérent avec l'absence de CAN **et** avec l'absence de tout
autre chemin d'entrée.

## 5. Ce dont j'aurais besoin de toi pour trancher

1. **Le brochage** : sur le connecteur du calculateur, les broches correspondant à P4.5/P4.6
   (CAN_H/CAN_L) sont-elles câblées ? Si elles sont vides, le CAN est réglé définitivement.
2. **Le signal vitesse** : sur le 406, le fil « vitesse véhicule » vers le calculateur moteur
   existe-t-il ? S'il arrive sur une broche, dis-moi laquelle et je cherche son traitement
   (entrée numérique, capture, ou ADC).
3. **La comparaison de binaires** : si tu as le dump du calculateur réellement validé pour ces cartes,
   je le compare à `edc.bin` sur ce point précis — c'est le test le plus rapide pour l'hypothèse 1.3-2.
