# ÉTAPE 45 — ★ Le bloc de configuration persistant `0xF7ED-0xF815` : enfin cartographié

*Suite de l'étape 44. C'était la vraie cible : la zone où le calculateur range ses options.*

---

## 1. ★ Le plan mémoire du bloc — établi par les déclarations, pas par conjecture

Extrait des déclarations de variables (l. 61132-61155) :

```
61132  byte_F7ED   ds 1     ; tag
61133  word_F7EE   ds 2  ┐
61134  word_F7F0   ds 2  ├ valeur en TRIPLE copie (6 o)
61135  word_F7F2   ds 2  ┘
61137  byte_F7F5   ds 1     ; tag
61138  word_F7F6   ds 2  ┐
61139  word_F7F8   ds 2  ├ valeur en TRIPLE copie
61140  word_F7FA   ds 2  ┘
61141  byte_F7FC   ds 1     ; tag
61142  byte_F7FD   ds 1  ┐
61144  byte_F7FE   ds 1  ├ valeur en TRIPLE copie (3 octets)
61146  byte_F7FF   ds 1  ┘
61148  byte_F800   ds 1  ┐
61150  byte_F801   ds 1  ├ compteur en triple copie
61152  byte_F802   ds 1  ┘
61155  word_F804   ds 2
61158  byte_F807
61160  word_F808   ds 2  ┐ accumulateur 32 bits
61161  word_F80A   ds 2  ┘
61163  byte_F80C   ds 1     ; tag courant
byte_F80D                  ; masque des éléments en attente
byte_F80E                  ; élément en cours de traitement
```

**⇒ Résultat structurel : un « enregistrement » = `1 octet de tag` + `une valeur rangée en TROIS
exemplaires`.**

Cela **résout définitivement** l'énigme de l'étape 36. Je l'avais décrite comme « cmd 0x0C = 3 mots »
et « cmd 0x0D = 3 octets » avec un vote à trois copies. **C'était bien une seule valeur, écrite trois
fois.** La « triple redondance masquée » n'est pas un mécanisme à part : c'est **la forme normale
d'écriture de ce bloc**.

| enregistrement | tag | valeur | commande | bit de `byte_F80D` |
|---|---|---|---|---|
| n°1 | `0xF7ED` | 1 mot ×3 (16 bits) | `0x0C` | **bit 0** |
| n°2 | `0xF7F5` | 1 mot ×3 (16 bits) | `0x0C` | **bit 1** |
| n°3 | `0xF7FC` | 1 octet ×3 (8 bits) | `0x0D` | **bit 2** |
| n°4 | `0xF800` | 1 octet ×3 (compteur) | — | **bit 7** |

*Preuve du lien tag → commande* : `sub_94BDC` lit `byte_F7FD`, `byte_F7FE`, `byte_F7FF`
(étiquetés `sub_94BDC+56`, `+62`, `+6E` dans les déclarations), et `sub_94BB6` écrit
`byte_F800/F801/F802` (`+10`, `+18`, `+20`) ainsi que `word_F808/F80A` (`+4`, `+8`).

---

## 2. ★ Le sélecteur `byte_F80D` : un masque d'éléments **en attente d'écriture**

l. 128317-128362 — trois blocs identiques :

```asm
loc_957D0:
                movbz r4, byte_F80D
                and   r4, #1
                jmpr  cc_Z, loc_957F0
                movb  rl4, #1
                movb  byte_F80E, rl4          ; élément courant = 1
                mov   r4, #0F7EDh             ; ← tampon de l'élément 1
                mov   word_C186, r4
                mov   r5, word_F91C
                mov   word_C124, r5           ; ← horodatage
                jmpr  cc_UC, loc_95840
loc_957F0:
                movbz r4, byte_F80D
                and   r4, #2
                ...
                mov   r4, #0F7F5h             ; élément 2
loc_95810:
                movbz r4, byte_F80D
                and   r4, #4
                ...
                mov   r4, #0F7FCh             ; élément 3
loc_95830:
                movbz r4, byte_F80D
                and   r4, #80h                ; élément 7 : bit 7
```

**Décodage :**

- **`byte_F80D` = masque des éléments dont la valeur a changé et doit être persistée** ;
- **`byte_F80E` = numéro de l'élément en cours** (0, 1, 2, 3 observés) ;
- **`word_C186` = pointeur sur le tampon de cet élément** — c'est le « pointeur de commande
  calculée » repéré à l'étape 44 §3 (famille F4) ;
- **`word_C124` = `word_F91C`** = horodatage, pour le rythme d'écriture ;
- l'écriture se fait ensuite par la commande `0x0B` (l. 127438).

**⇒ Voilà la réponse à « où est codée la présence du régulateur, de la clim, etc. »** : dans **des
enregistrements à tag, à valeur unique, écrits en triple copie, sélectionnés par un masque de bits.**
Ce ne sont pas des champs isolés dispersés : c'est **un bloc cohérent, à 4 emplacements**.

Les 20 écritures de `byte_F80D` sont **toutes situées entre les lignes 127179 et 128305** — un seul
sous-système, cohérent, qui gère cette configuration de bout en bout.

---

## 3. ★ Le seul endroit du code visible où des **bits d'option sont effacés**

l. 127204-127222 :

```asm
loc_94C26:
                mov   r12, #0F800h
                calls 9, sub_94AE8          ; ← lecture avec consensus
                cmpb  rl4, #0
                jmpr  cc_NZ, loc_94C60
                movb  rl4, byte_F7FD
                andb  rl4, #9Fh             ; ← EFFACEMENT des bits 5 et 6
                movb  byte_F7FD, rl4
                movb  rl5, byte_F7FE
                andb  rl5, #9Fh             ; idem
                movb  byte_F7FE, rl5
                movb  rl3, byte_F7FF
                andb  rl3, #9Fh             ; idem (les 3 copies)
                movb  byte_F7FF, rl3
                movb  rl2, #4
                movb  byte_F80D, rl2        ; programme la réécriture
```

**Le masque `0x9F` efface précisément les bits 5 et 6** de la valeur de l'enregistrement n°3, **dans
les trois copies**, puis **programme la réécriture** (`byte_F80D = 4`).

- Ce n'est pas une initialisation générique : c'est un **effacement ciblé de deux bits**.
- Ce n'est pas une lecture : c'est une **écriture forcée** sur la mémoire permanente.
- La condition est **la nullité du compteur `0xF800`**.

**Je ne conclus pas** sur ce que sont les bits 5 et 6 (deux options du véhicule), mais **c'est le
seul site du code visible qui force des bits d'option à zéro**, et il est **conditionné par un
compteur** — donc il ne se déclenche **qu'une fois**, typiquement peu après la mise en service. Un
candidat sérieux pour un mécanisme de **verrouillage/déverrouillage d'option par le constructeur**. À
rapprocher de la remarque de l'utilisateur sur l'**immo bypassable simplement**.

---

## 4. Le compteur `0xF800` et l'accumulateur à **62 500**

l. 127160-127176 :

```asm
                mov   r8, r4
                mov   r9, r5
                sub   r4, word_F808
                subc  r5, word_F80A
                sub   r4, #0F424h           ; 62 500
                subc  r5, #0
                jmpr  cc_C, loc_94C26
                mov   r4, #0F424h
                mov   r5, #0
                add   word_F808, r4
                addc  word_F80A, r5
                mov   r12, #0F800h
                calls 9, sub_94AE8
                movb  rl6, rl4
                subb  rl6, #1               ; ← DÉCRÉMENTE
                movb  byte_F800, rl6
                movb  byte_F801, rl6
                movb  byte_F802, rl6
                movb  rl4, #4
                movb  byte_F80D, rl4
```

**Lecture :** à chaque **tranche de 62 500 unités** d'un compteur 32 bits amont (`r8:r9` comparé à
`word_F808:F80A`), on **décrémente** le compteur triple `0xF800` et on **réécrit l'EEPROM**.

**Interprétation prudente** : c'est une **fenêtre de réglage** — le calculateur laisse passer N
tranches de 62 500, puis ferme. La valeur `0x9F` du §3 s'applique quand ce compteur atteint zéro.

*Unité non tranchée.* Trois pistes, aucune retenue : distance (62,5 km si l'unité est le mètre ×1),
temps (62 500 × 10 ms ≈ 10 min), ou un compteur de cycles. **Je ne tranche pas.**

---

## 5. Deux fonctions déjà connues prennent leur rôle définitif

| fonction | rôle |
|---|---|
| **`sub_94AE8`** | **lecture avec consensus** d'un enregistrement triple (`r12` = adresse, `rl4` = valeur retenue). C'est le vote déjà vu à l'étape 36. |
| **`sub_94BB6`** | **écriture** d'un enregistrement triple (`0xF800-0xF802`, `word_F808/F80A`). |
| **`sub_94BDC`** | **gestionnaire** : teste, décrémente, assainit, programme la réécriture. |
| `sub_94C6A` | verrou à gâchette (étape 40 §3) — même famille de petites fonctions, `0x94Cxx`. |

⇒ **La famille `0x94Axx-0x94Cxx` est le « gestionnaire de mémoire permanente courte »** : lecture
consensus, écriture triple, verrou à gâchette, sélection d'élément. C'est un module **distinct** du
module `sub_A0002` (lui-même le pilote bas niveau). **Trois couches** :

```
applicatif  →  gestionnaire 0x94Axx-0x94Cxx  →  pilote sub_A0002  →  image 0xE5CE
               (redondance, rythme, options)     (page + offset)
```

---

## 6. Bilan de la question posée depuis le début

> « La présence du régulateur, de la clim, etc. est codée dans l'EEPROM ⇒ trouver le codage. »

**Ce que nous savons maintenant, et avec quel degré de certitude :**

| élément | certitude |
|---|---|
| la configuration passe par **4 enregistrements** `0xF7ED`, `0xF7F5`, `0xF7FC`, `0xF800` | **lu** (déclarations + sélecteur) |
| chaque enregistrement = **tag + une valeur unique en triple copie** | **lu** |
| l'écriture est **différée** et **sélectionnée par le masque `byte_F80D`** | **lu** |
| l'écriture aboutit à la commande **`0x0B`** de `sub_A0002` | **lu** |
| les **valeurs** (quel bit = régulateur, quel bit = clim) | **hors de portée** : dans la couche absente |
| les bits **5 et 6** de l'enregistrement n°3 sont **effaçables** par le calculateur lui-même | **lu** (masque `0x9F`), sens **inconnu** |

**Le point dur reste le même, et il est maintenant circonscrit avec précision** : la
correspondance « bit ↔ option » est **dans le code absent** (`nullsub_8`, et les fonctions non
désassemblées). Elle n'est **pas** dans le Datensatz, car un Datensatz ne contient que des nombres et
des axes, pas des affectations d'options.

⇒ **Conséquence pratique importante** : la seule voie accessible pour retrouver le codage est
**l'expérience** — comparer deux EEPROM de véhicules de configurations connues. Le code nous dit
**où** et **comment** lire ; il ne nous dit pas **quoi**.

---

## 7. Prochaines actions

1. **`sub_94AE8`, `sub_94BB6`, `sub_94BDC`** : lecture intégrale (≈ 200 lignes). Le vote à trois
   copies y est peut-être **pondéré** — ce qui révélerait la tolérance à une falsification.
2. **`byte_C2EC`** : byte de mode global, écrit l. 111754, lu par **10 fonctions** dont les deux
   voies EEPROM. **C'est le meilleur candidat « variante globale » restant.**
3. **`word_F804`, `byte_F807`** : les deux champs voisins non encore expliqués.
4. **`byte_C2DC`** (l. 127629) : testé juste après la remise à zéro du masque.
