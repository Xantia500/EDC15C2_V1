# ÉTAPE 35 — Freeze frames localisées, et un **contrôle anti-falsification** décodé

Les quatre pistes du §10 de l'étape 34, plus une découverte non prévue.

---

## 1. Freeze frames / défauts : la chaîne complète

### 1.1 Le service 0x17 et le format de réponse

`sub_C1544`, l. 207645-207764. La requête donne un mot `r9 = (octet1 << 8) | octet2` :

| valeur | action |
|---|---|
| **`0xFF00`** | **lire le nombre de défauts** : `word_DC90 = 0` puis `sub_942CA(0x8000, 0)` → `byte_DC92 = rl4` |
| **`0xFFFF`** | `byte_DC92 -= 8` ; si ≤ 0 → 0 puis NRC 0x12 |
| autre | NRC 0x12 |

Réponse : `'W'` (**0x57 = réponse positive à 0x17** ✔), puis le compteur, puis **une boucle sur les
enregistrements** (l. 207720-207743) :

```asm
loc_C15F2:
                mov     r4, [r0]
                mov     r5, [r4]
                shr     r5, #8
                movb    [r2], rl5          ; 1er octet émis = octet HAUT du mot 0
                mov     r5, [r4]
                movb    [r2], rl5          ; 2e octet émis  = octet BAS du mot 0
                movb    rl4, [r0+#5]
                movb    [r5], rl4          ; 3e octet émis  = octet +5 de l'enregistrement
```

⇒ **Un défaut = `[code sur 2 octets, poids fort d'abord][statut]`** — exactement la forme KWP
`statusOfDTC` (DTC high, DTC low, status). **Le code défaut est un mot à l'offset 0 de
l'enregistrement, le statut est à l'offset +5.** La taille minimale d'un enregistrement est donc
**6 octets**.

### 1.2 `sub_942CA` n'est pas un accesseur : c'est un **changement de contexte**

```asm
sub_942CA:
                add     CP, #18h            ; ← CP = Context Pointer : change de banc de registres
                calls   0Ch, sub_CE256
                push    r4
                sub     CP, #18h
                nop
                pop     r4
                rets
```

Idem `sub_942DE → sub_CE43C`, `sub_942F2 → sub_CE57E`. ⇒ **La mémoire des défauts est gérée par un
module séparé**, appelé à travers un changement de banc. `sub_CE256` (EA `0xCE256`) est le vrai
gestionnaire.

### 1.3 `sub_CE256` — la structure mémoire des défauts

```asm
                cmpb    rh6, #0FFh                  ; sélecteur 0xFF...
                movbs   r4, byte_E501
                cmp     r4, ONES                    ; 0xFF = aucun défaut sélectionné
                mov     r2, r4
                add     r2, r2
                add     r2, #0CCB2h                 ; ← TABLE DES CODES (mots)
                mov     [r5+], [r2]                 ; émet le CODE du défaut
                mov     r0, r5
                mov     r1, #0E501h
                mov     r2, #16h                    ; 22 octets
                calls   0, unk_2A9A                 ; copie la structure de 0xE501
```

**La mémoire des défauts, en RAM :**

| adresse | rôle | preuve |
|---|---|---|
| **`byte_E466`** | **nombre de défauts enregistrés** | l. 229606, 229623, 229661, 229694, 229844 (`= 0` à l'effacement) |
| **`0xE467` + 154 octets** | **tableau des enregistrements** | l. 229585-229600 (`r1 = 0xE467`, `r2 = 0x9A`) |
| **`0xCCB2 + 2×index`** | **table des codes défaut** (mots) | 9 sites : l. 229592, 229672, 229699, 230031, 230040, 230738, 230868, 230904 |
| **`byte_E501`** | **index du défaut courant**, `0xFF` = aucun | l. 229585, 229835, 229920 |
| **`0xE501` + 22 octets** | **structure de 22 octets** = la **freeze frame** | l. 229595-229600 |

**Ce qui est prouvé** : les 22 octets sont copiés *avec* le code défaut quand le sélecteur est
`0xFF` → c'est bien un bloc de **données d'environnement mémorisées avec le défaut**.

**Ce qui ne l'est pas** : 154 = 22 × 7 **et** 154 = 7 × 22. Deux organisations compatibles
(**7 défauts de 22 octets** ou **22 défauts de 7 octets**). **Je ne tranche pas** : il faut lire
`byte_E466` en fonctionnement, ou voir la borne de comparaison.

### 1.4 ★ Constat structurel : la mémoire des défauts est **contiguë à l'image EEPROM**

```
0xE466 ─ compteur                    ┐
0xE467 ─ 154 octets de défauts       │ mémoire des défauts
0xE501 ─ index + 22 octets (frame)   │
0xE517 ─ (fin)
   ...
0xE5CC ─ checksum de l'image
0xE5CE ─ DÉBUT DE L'IMAGE EEPROM     ┘
```

Les défauts occupent **`0xE466-0xE516`**, soit **exactement la zone qui précède l'image `0xE5CE`**,
sans recouvrement. **Ce n'est pas un hasard d'allocation** : le linker a aligné deux blocs
persistants voisins.

### 1.5 Conséquence importante — et contraire à l'hypothèse courante

**Aucun tableau de défauts n'est présent dans l'image EEPROM** telle que `sub_A0CCC` la construit
(13 groupes, étape 30). Et **aucun code visible ne recopie `0xE466…0xE516` vers l'image**.

⇒ Avec ce que nous avons : **les défauts et freeze frames sont en RAM vive**, sans chemin de
persistance visible. Trois explications possibles, aucune prouvée :
1. la sauvegarde est faite par la **couche absente** (power latch) — cohérent avec `word_FD0C` sans
   écrivain ;
2. ils sont écrits dans une **zone EEPROM non couverte par `sub_A0CCC`** ;
3. ils ne sont **pas** persistants au-delà de la mise hors tension longue.

**Je ne conclus pas**, mais je note que le dossier externe affirmait « les DTC sont en EEPROM
0x0350-0x03FF » : **rien dans ce binaire ne le confirme**.

---

## 2. La signature `A5A5` — réponse nette

**`0x0A5A5` n'est testé par AUCUNE instruction** (0 occurrence de `#0A5A5h`). ⇒ L'en-tête `A5A5` de
`0xFC000` n'est **pas validé par le code présent** : il appartient au domaine du boot absent.

**Mais `0xAA55` est comparé**, à deux endroits (l. 128814, 129593) — dans un mécanisme différent,
décrit ci-dessous.

---

## 3. ★ Un contrôle anti-falsification à **deux mots magiques**

### 3.1 Le poseur : `sub_95C8C(r12)`

```asm
                cmpb    rl4, #0
                jmpr    cc_NZ, loc_95CAA
                mov     r4, #0C1C6h
                mov     word_FA22, r4        ; état A
                mov     r5, #3FA9h
                mov     word_DDF2, r5
                movb    rl4, #1
                movb    byte_F62E, rl4       ; drapeau = 1
                jmpr    cc_UC, loc_95CBE
loc_95CAA:
                mov     r4, #3E39h
                mov     word_FA22, r4        ; état B
                mov     r5, #0C336h
                mov     word_DDF2, r5
                movb    byte_F62E, ZEROS     ; drapeau = 0
loc_95CBE:
                movb    rl4, byte_F62E
                movb    byte_F608, rl4
```

### 3.2 Le vérificateur : `sub_95CC8`

```asm
                mov     r13, word_FA22
                xor     r13, #6B93h          ; ← constante de brouillage
                movb    rl4, #1
                movb    [r12], rl4           ; défaut : INVALIDE
                mov     r4, word_DDF2
                sub     r4, #170h
                xor     r4, #6B93h
                cpl     r4                   ; complément
                cmp     r13, r4
                jmpr    cc_NZ, locret_95CF0
                cmp     r13, #0AA55h         ; ← la signature attendue
                jmpr    cc_NZ, locret_95CF0
                movb    rl4, #0
                movb    [r12], rl4           ; VALIDE
```

### 3.3 Vérification arithmétique (indépendante)

| état | `word_FA22` | `^ 0x6B93` | `word_DDF2` | `− 0x170` | `^ 0x6B93` | `cpl` |
|---|---|---|---|---|---|---|
| A | `0xC1C6` | **`0xAA55`** | `0x3FA9` | `0x3E39` | `0x55AA` | **`0xAA55`** ✔ |
| B | `0x3E39` | **`0x55AA`** | `0xC336` | `0xC1C6` | `0xAA55` | **`0x55AA`** ✔ |

**Les deux états sont cohérents, et le second produit `0x55AA` — ce qui explique pourquoi le
second site compare à `0xAA55` *et* `0x55AA`** (l. 129593-129597). ✔

### 3.4 Et la sanction

l. 129593-129605 :

```asm
                cmp     r9, #0AA55h
                jmpr    cc_Z, loc_963E0      ; -> byte_F62E = 1, byte_F608 = 1
                cmp     r9, #55AAh
                jmpr    cc_Z, loc_963F0      ; -> byte_F62E = 0, byte_F608 = 0
                jmpr    cc_UC, loc_963FC
loc_963FC:
                bclr    IEN                  ; ← COUPE LES INTERRUPTIONS
```

**Toute autre valeur ⇒ `bclr IEN`** (arrêt de l'application). Le contrôle est **périodique** : il est
gardé par `byte_F843` qui compte jusqu'à 9 (l. 129580-129586).

⇒ **C'est un dispositif anti-falsification** : un booléen (`byte_F62E`/`byte_F608`) est **doublé**
dans deux mots RAM liés par une relation non triviale (`⊕0x6B93`, `−0x170`, complément), et
revérifié en boucle. **Modifier un seul des deux mots met le calculateur à l'arrêt.**

**Ce que je ne sais pas** : ce que signifie le booléen. Il est branché sur un **buffer de réception**
`0xF62x-0xF64x` (`byte_F623` comparé à 4, `word_F646` pointeur, `byte_F63A/3D/3E/3F` champs
d'en-tête) et posé après `sub_94B1A(0xF7FD)` (l. 127876). **Hypothèse non validée** : un état
d'autorisation issu d'une trame reçue. À creuser — c'est très probablement **le verrou
d'antidémarrage côté application**.

---

## 4. Les préconditions de sécurité du boot

| variable | écrit par | lu par |
|---|---|---|
| **`byte_CF30`** | **uniquement seg019** (l. 403772, 403940) | `sub_FE62E` (l. 406157) |
| **`byte_CF31`** | **uniquement seg019** (l. 403789, 405305, 406302) | `sub_FE62E` (l. 406169) |
| **`word_FC10`** | **l'application** (l. 96112, 96346) + seg019 (403823, 403828, 404023, 406314, 406380) | `sub_FE62E` (l. 406150) |

⇒ **`word_FC10` est le seul point de contact entre les deux programmes sur la sécurité** : posé au
démarrage par l'application (`0x9xxxx`), et **exigé nul** par le service 0x27 du boot. Autrement
dit : **l'application elle-même décide si la sécurité du boot secondaire est ouverte.**
`byte_CF30` = « déjà déverrouillé », `byte_CF31` = « clé en attente ».

---

## 5. Les 4 sites `0xCFA4`

`0xCFA4` n'apparaît **que** comme pointeur de sortie, aux l. 152331, 152520, 152789, 152978, et
**n'est relu nulle part** sous ce nom. Chaque site lit un **numéro de commande EEPROM dans un
pointeur** (`word_C462`, `word_C464`, `word_C466`, `word_C468`) :

```asm
loc_A1874:
                mov     r4, word_C462
                movb    rl5, [r4]
                movbz   r12, rl5           ; commande = 1er octet pointé
                mov     r13, #0CFA4h       ; sortie
                calls   0Ah, sub_A0002
```

⇒ **Quatre canaux identiques, dont le numéro de commande est variable.** C'est un **mécanisme
d'accès indirect** aux blocs EEPROM — exactement le motif que tu m'as demandé de ne jamais écarter
(« cartes validées ⇒ chercher l'accès indirect »). Les quatre `word_C46x` font partie d'une
structure à quatre entrées, à identifier.

---

## 6. Corrections et limites de cette étape

1. Je **n'ai pas** examiné `sub_FE4AE` (service 0x21 du boot) : **reporté**, pas oublié.
2. L'interprétation « `word_C70A` = compteur + complément » (étape 34 §7) reste **inférée**.
3. Le nombre de défauts mémorisables (**7 ou 22**) est **indéterminé**.
4. La persistance des défauts est **non résolue** — et **rien ne la place dans l'image EEPROM**.

---

## 7. Prochaines actions

1. **`sub_FE4AE`** : la liste des identifiants locaux du boot (accès mémoire direct ?).
2. **`byte_F62E`** : remonter jusqu'à ce qui pose le résultat de `sub_94B1A(0xF7FD)` → candidat
   n°1 pour **le verrou d'antidémarrage applicatif**.
3. **`word_C462…C468`** : la structure à quatre canaux EEPROM.
4. **`byte_E466`** : borne de comparaison → tranchera 7 × 22 ou 22 × 7.
