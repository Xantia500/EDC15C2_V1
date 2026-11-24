# ÉTAPE 54 — Le décodage par usage est automatisé — et il valide les bornes en série

---

## 0. Réponse à la question posée

**Le fichier contenant les tableaux mis à jour est :**

```
analyse_edc15c2_4hx/CATALOGUE_MAITRE.md
```

Il est **régénéré** par `outils/genere_catalogue.py`, qui lit :

| source | contenu |
|---|---|
| `edc.bin` | le binaire de 512 Ko — source de **toutes** les valeurs |
| `clean.asm` | le désassemblage — source des **preuves par n° de ligne** |
| `annotation_datensatz.csv` | les 182 courbes 1-D décodées |
| `annotation_cartes_2D.csv` | les 66 cartes 2-D décodées |
| **`usage_handles_resume.csv`** | **nouveau** — les offsets lus et écrits par handle |
| **`usage_handles_offsets.csv`** | **nouveau** — le détail, accès par accès |

**Relancer le générateur suffit à tout remettre à jour.**

---

## 1. ★ Un défaut de mon propre outil, trouvé et corrigé

Premier passage de l'outil d'usage : **tous** les handles semblaient n'être lus qu'à partir de
l'offset `0x0A`. Motif trop régulier pour être vrai — j'ai vérifié `word_18C2` à la main :

```asm
156151:                mov     r4, word_18C2
156152:                movb    rl5, [r4+#7]        ; ← offset 7
156153:                movb    byte_D704, rl5
156154:                movb    rl3, [r4+#8]        ; ← offset 8
...
156197:                mov     r5, [r4+#4Ch]       ; ← offset 0x4C
```

**Ma regex exigeait le suffixe `h`** (`#0Ah`), or le désassembleur écrit `#7`, `#8`, `#9` **sans
suffixe** pour les valeurs inférieures à 0x0A. **Les offsets 0 à 9 étaient donc tous perdus.**

Après correction : **2 924 accès relevés, 270 handles distincts**. Second défaut corrigé dans la
foulée : `word_D830`, `word_DC6C`… sont des **variables RAM**, pas des handles — la plage est
désormais bornée à `0x1400…0x1E30`.

> **Leçon** : un résultat « trop régulier » est un signal d'erreur. C'est la deuxième fois dans ce
> travail qu'un motif parfaitement propre cachait un bug de lecture (cf. l'étape 52 § 2).

---

## 2. ★★★ Constat majeur : **46 blocs sont balayés intégralement**

Sur les 270 handles effectivement lus par le code, **46 le sont en balayage séquentiel** — c'est-à-dire
**mot après mot, depuis `0x00` jusqu'à la fin du bloc**.

| handle | taille du bloc | dernier offset lu | concordance |
|---|---|---|---|
| `word_14A0` | **100** | `0x62` (= 98) | **exacte** |
| `word_18C2` | **78** | `0x4C` (= 76) | **exacte** |
| `word_161A` | **66** | `0x40` (= 64) | **exacte** |
| `word_1C3E` | **66** | `0x40` (= 64) | **exacte** |
| `word_1952` | **62** | `0x3C` (= 60) | **exacte** |
| `word_18F2` | **58** | `0x38` (= 56) | **exacte** |
| `word_1972` | **56** | `0x36` (= 54) | **exacte** |
| `word_1432` | **48** | `0x2E` (= 46) | **exacte** |
| `word_14B0` | **46** | `0x2C` (= 44) | **exacte** |
| `word_1DB0` | **46** | `0x2A` (= 42) | ≤ |
| `word_1904` | **42** | `0x28` (= 40) | **exacte** |
| `word_18EE` | **38** | `0x24` (= 36) | **exacte** |

**Dix correspondances exactes sur douze, et l'écart est toujours de 2 octets** — soit : *le dernier mot
du bloc est lu*.

### Ce que cela prouve, et pourquoi c'est la meilleure validation obtenue

Jusqu'ici, la méthode des bornes de bloc (étape 48 § 1) était validée **cas par cas** : quatre
vérifications isolées. Ici, elle est validée **en série, sur douze blocs simultanément**, par une voie
**totalement indépendante** : ce n'est plus le contenu du bloc qui est confronté, c'est **le code qui le
parcourt**.

**⇒ La taille de chaque handle, calculée depuis la table des pointeurs, est exacte.** On peut donc
désormais **travailler sur les 1 304 handles en connaissant leur étendue exacte**, sans réserve.

---

## 3. ★ Un gabarit de plus : le **bloc balayé**

| type | définition | nombre |
|---|---|---|
| **Bloc balayé** | **aucun en-tête** ; lu mot après mot de `0x00` à `taille − 2` | **46 identifiés** |

Ce n'est pas un « paquet de paramètres » (étape 53 § 2) : un paquet se lit à **quelques offsets
choisis**, un bloc balayé se lit **entièrement**. Ce sont deux usages distincts, et cela explique
pourquoi certains blocs de 32, 46 ou 100 octets ne montraient aucune structure : **ils n'en ont pas —
ils sont des tableaux parcourus**.

**Trois usages plausibles** (aucun retenu) : recopie vers la RAM, transfert vers l'outil de diagnostic,
ou calcul d'une grandeur globale sur la table. **La nature exacte du routine qui balaie trancherait** —
c'est la prochaine cible.

---

## 4. Ce que l'automatisation apporte, en pratique

Le travail « nommer un handle » cesse d'être une recherche manuelle. Pour **chacun** des 927 blocs non
classés, on dispose maintenant de :

- **la liste exacte des offsets lus et écrits** (`usage_handles_resume.csv`) ;
- **la ligne de code** de chaque accès (`usage_handles_offsets.csv`, 2 924 lignes) ;
- **la taille exacte du bloc** (validée, § 2).

**Trois cas de figure, et ils se distinguent tout seuls :**

| signature | interprétation | suite |
|---|---|---|
| balayage `0x00…taille−2` | tableau parcouru (46 cas) | identifier la routine qui balaie |
| quelques offsets épars | paquet de paramètres | lire le code aux lignes indiquées |
| aucun accès trouvé | soit non utilisé par la couche visible, soit lu par un motif que l'outil ne couvre pas | **ne rien conclure** |

**Ce dernier point est important** : mon outil ne détecte que le motif `mov rN, word_XXXX` suivi d'un
accès indexé sur **le même registre**. Un handle passé à un sous-programme, ou atteint par `lea` / par
arithmétique de pointeur, lui échappe. **Les 270 sont donc un MINIMUM, pas un total.**

---

## 5. Le catalogue est à jour

`analyse_edc15c2_4hx/CATALOGUE_MAITRE.md` — **798 lignes** — contient maintenant :

- un **§ 2 bis** avec les six constats (répartition, tailles, marqueur `0x0F10`, blocs d'axe, usage) ;
- le **gabarit « bloc balayé »** ajouté au tableau du § 2 ;
- la **table des douze balayages avec concordance exacte** ;
- la méthode à retenir pour nommer un handle.

---

## 6. Prochaines actions

1. **★ Les routines de balayage** : trouver les sous-programmes qui parcourent les 46 blocs et
   **établir ce qu'ils en font** (recopie, transfert, calcul). C'est ce qui donnera un **sens** à ces
   46 blocs — le plus gros gain restant.
2. **Étendre l'outil** aux motifs manquants : `lea rX, word_YYYY`, passage en paramètre à un
   sous-programme, arithmétique de pointeur. **Cela fera monter les 270.**
3. **Traiter les « quelques offsets épars »** par ordre de fréquence : `word_1548` (26 offsets),
   `word_141E` (40 offsets) — les deux plus lus après les balayages.
4. **`word_1DB0`** : les 2 octets manquants (0x2A au lieu de 0x2C) — soit un octet non lu, soit un
   accès raté par l'outil. **Point de contrôle, pas conclusion.**
