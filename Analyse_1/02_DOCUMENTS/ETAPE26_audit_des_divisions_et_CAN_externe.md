# ÉTAPE 26 — Où le rapport n'est pas calculé : audit des 124 divisions, et découverte d'un CAN **externe**

Ta position : le rapport **doit** être calculé (v, RPM, ratio), et le paramètre de taille de roue
existe dans le Lexia/PPS. Je prends ça comme l'hypothèse à tester, pas comme une conclusion à
contredire. Voici ce que le test donne — avec deux découvertes au passage.

---

## 1. Test n° 1 — `byte_C240` : quatre écrivains, aucun calcul

| ligne | écriture | nature |
|---|---|---|
| 139477 | `movb byte_C240, rl5` depuis `[word_1658+8]` | **défaut** (bloc de reset de `sub_9A8B8`) |
| 140993 | idem | **défaut** (reset de `sub_9B796`) |
| 141203 | idem | **défaut** (message invalide, quartet = `0xF`) |
| 141208 | `movb byte_C240, rl6` avec `rl6 = byte_C871 >> 4` | **nibble reçu** |

**Aucune** de ces quatre écritures ne calcule un quotient. Une valeur calculée devrait passer par
l'une d'elles. Elle n'y passe pas. *(Lu. Ce constat ne dit rien de l'origine du nibble : voir §3.)*

## 2. Test n° 2 — les divisions : 124 sites catalogués

J'ai listé les **124** instructions `div/divl/divu/divlu` et, pour chacune, les variables présentes
dans les 6 lignes qui précèdent.

- **Sites avec une variable de vitesse identifiée : 0.**
- **Sites avec le régime (`word_C91C`) : 1 seul**, l. 240613-240619 :

```asm
mov  word_D582, r4
shl  r4, #1              ; 2 × X
mov  r1, word_C91C       ; régime
shl  r1, #2              ; 4 × rpm
mov  r2, #7A12h          ; 31250
mul  r4, r1              ; produit 32 bits
mov  r1, MDH
divl r2                  ; / 31250
mov  r4, MDL
```

⇒ `résultat = (2·X × 4·rpm) / 31250 = X · rpm / 3906,25`. C'est une **conversion « par cycle » vers
« par unité de temps »** (le régime est **multiplié**, pas divisé) : typiquement mm³/cycle → débit.
**Ce n'est pas un rapport de transmission.** *(Lu ; l'interprétation « débit » est inférée.)*

**Limite du test, à énoncer nettement** : il ne prouve pas l'absence du calcul.
Une division par le régime peut être faite **par multiplication par un inverse** (fixe-point) ou par
`unk_2160` (dans la bibliothèque absente). Et surtout, **la variable de vitesse n'est pas encore
identifiée** : tant qu'elle ne l'est pas, mon filtre ne peut pas la trouver.

## 3. Découverte — trois contrôleurs CAN **externes** en mémoire

C'est le résultat le plus important de cette étape, et il explique un point resté en suspens.

```asm
cmp  r2, #1 ; mov r4, #8000h      ; l.98033-98035
cmp  r2, #2 ; mov r4, #0B000h     ; l.98038-98040
cmp  r2, #3 ; mov r4, #0EF00h     ; l.98043-98045
mov  r1, #747h
mov  [r4+#0], r1                  ; registre de contrôle
cmp  r4, #0EF00h
...
mov  r1, [r4+#2]
jb   r1.7, ...                    ; attente d'un bit d'état (init/bus-off)
mov  r1, #61h ; mov [r4+#2], r1
mov  r1, [r4+#1Eh] ; … [r4+#2Eh] ; …[r4+#3Eh] ; …[r4+#4Eh]
```

Trois **fenêtres mémoire** (`0x8000`, `0xB000`, `0xEF00`) sélectionnées par un paramètre, avec
**exactement la même carte de registres** : `+0x00` contrôle, `+0x02` état/commande, puis des
**objets de 16 octets** (`+0x1E`, `+0x2E`, `+0x3E`, `+0x4E`…). Et l'initialisation écrit `0x5555`
dans **15 objets** (l. 135639-135679), le premier étant configuré depuis le Datensatz
(`word_1456` → `0xEF06/08/0A/0C/0E`, l. 135681-135700).

**Conclusion** : ce ne sont pas des structures logicielles — c'est un (ou trois) **contrôleur CAN
externe(s)** monté(s) en mémoire. Cela **réconcilie** deux faits qui semblaient contradictoires :
tu n'as trouvé **aucun SFR CAN** dans le C167 (c'est exact), et pourtant **le CAN existe** — il est
hors du microcontrôleur.

Conséquences, à énoncer séparément :

1. **Le bloc de 7 octets du rapport (étape 25) est lu dans un objet de ce contrôleur** : le rapport
   arrive donc bien par un **bus de messages**, pas par un fil dédié.
2. **Cela ne dit rien de la vitesse**, qui reste sur son entrée à impulsions — les deux affirmations
   coexistent sans conflit.
3. **Mais cela n'établit pas non plus que le producteur est extérieur** : un calculateur peut écrire
   dans son propre objet d'émission. C'est le point qui reste ouvert, et le §5 dit comment le fermer.

## 4. Le paramètre de taille de roue — ce que dit le fichier

Recherche dans les 512 Ko, en u16 petit-boutiste :

| valeur cherchée | sens | occurrences |
|---|---|---|
| `0x0FC8` (4040) | impulsions/km | **0** |
| `0x0FDA` (4058) | impulsions/km | **0** |
| `0x0FB4` (4020) | impulsions/km | **0** |
| `0x07BC` (1980) | circonférence mm | **0** |
| `0x07C6` (1990) | circonférence mm | **0** |
| `0x07A2` (1954) | circonférence mm | **0** |
| `0x07D0` (2000) | circonférence mm | 3 (`0xA2254`, `0xA2278`, `0xA239C` — **hors Datensatz**) |
| `0x0FDE` (4062) | impulsions/km | 1 (`0xBF261` — **hors Datensatz**) |

⇒ Sous forme de constante simple, **le paramètre roue n'est pas dans la zone de calibration**.
Deux lectures possibles, et je ne tranche pas :

- il est stocké **ailleurs** (EEPROM / zone de configuration, absente de ce dump de flash) —
  c'est le cas habituel des paramètres modifiables au Lexia ;
- il est stocké **sous un code**, pas sous une valeur. Cette hypothèse est soutenue par un fait
  observé : `byte_FAD2` est un **codage par bits** qui sélectionne la vitesse de la liaison
  diagnostic (`cmpb rl1,#1 / #2 / #4 / #8 / #10h / #20h / #40h / #80h`, l. 98759-98775).
  Les paramètres de ce calculateur sont **codés**, pas écrits en clair.

## 5. Verdict de l'étape

| question | réponse |
|---|---|
| le rapport est-il calculé dans les routines visibles ? | **non trouvé** — et `byte_C240` n'a aucun écrivain calculé |
| l'hypothèse v/RPM est-elle réfutée ? | **non** — aucune division vitesse/régime trouvée, mais la variable de vitesse n'est pas identifiée et une division peut être déguisée en multiplication |
| d'où vient le nibble de rapport ? | d'un **objet de message** lu dans un contrôleur CAN externe |
| le CAN existe-t-il ? | **oui**, en périphérique **externe** (0x8000 / 0xB000 / 0xEF00) |
| le paramètre roue est-il dans ce fichier ? | **pas sous forme de constante identifiable** |

**Les trois refuges possibles du calcul**, et le test qui trancherait chacun :

1. **La variable de vitesse** → suivre `word_FC04` (période accumulée, l. 97139) jusqu'à son
   convertisseur, puis relancer l'audit des divisions avec le **bon nom**. *Test décisif.*
2. **`unk_2160`** (bibliothèque absente, 27 appels) → déterminer empiriquement s'il multiplie ou
   divise, en le confrontant à des appels dont les deux opérandes sont des constantes connues
   (ex. l. 141055-141059 : `[word_1664] = 5243`, `[+2] = 65280`). *Test faisable sur les données.*
3. **Le producteur du message** → chercher la routine qui écrit dans un objet **d'émission**
   (statut « neuf ») et voir si elle calcule v/RPM avant d'écrire. *Test direct.*

## 6. Prochaine action que je propose

**Le test n° 1** : identifier la variable de vitesse. C'est le pivot — tant qu'elle n'a pas de nom,
ni l'audit des divisions ni la recherche du paramètre roue ne peuvent aboutir. Je partirai de
`word_FC04` (période) et de son usage en l. 98973-98986, puis je remonterai au calcul de vitesse.
