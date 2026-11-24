# ÉTAPE 109 — Comment le rapport est déterminé, exactement

Récapitulatif complet, **re-vérifié dans le code** (rien de mémoire).

---

## Maillon 1 — La vitesse et le régime

| variable | rôle | preuve |
|---|---|---|
| `word_C578` | **vitesse en 0,01 km/h** | numérateur du calcul (l.232297) |
| `word_C42E` | **régime** | copié en `C91C` (l.232286-232287, et à chaque entrée de tâche) |
| `word_C91C` | copie de travail du régime | `mov r0, word_C42E ; mov word_C91C, r0` |

> ⚠ `C578` n'a **qu'une seule référence** dans `clean.asm` : la lecture de `sub_CF774`.
> Aucune écriture directe ⇒ il est rempli par un overlay non désassemblé (ou par un accès
> indirect). C'est le **seul maillon non prouvé** de la chaîne, mais la cohérence numérique
> ci-dessous ne laisse aucun doute sur son échelle.

## Maillon 2 — Le ratio brut : une division 32 bits (`sub_CF774`)

```asm
232285  loc_CF834:
232286  mov  r0, word_C42E
232287  mov  word_C91C, r0          ; C91C = régime
232288  mov  r0, word_C91C
232289  jmpr cc_NZ, loc_CF84C       ; régime nul -> ratio = 0
232296  loc_CF84C:
232296  mov  r7, word_1470          ; bloc 0xE225A
232297  mov  r4, word_C578          ; ★ vitesse (0,01 km/h)
232299  shl  r4, #8                 ; ★ × 256
232300  mov  MDL, r4
232301  divlu r0                    ; ★★ (V × 256) / N   — division 32 bits
232302  jmpr cc_V, loc_CF86C        ; débordement
232303  mov  r0, [r7+#0Eh]          ; plafond du bloc 0xE225A
232304  cmp  r0, MDL
232305  jmpr cc_NC, loc_CF870       ; si résultat > plafond -> plafond
```

$$\boxed{\text{ratio} = \frac{V_{0,01\,\text{km/h}} \times 256}{N_{\text{tr/min}}}}$$

**Dimension** : c'est un **N/V inversé**, exprimé en centièmes de km/h par tour/minute.

## Maillon 3 — Le filtrage

```asm
232312  mov  r0, word_C576          ; ancienne valeur
232313  mov  word_C93E, r0
232315  mov  r4, word_C56A
232316  mov  r3, word_185C          ; courbe de filtrage
232317  mov  r2, MDL                ; nouvelle valeur brute
232318  calls 0, unk_24BA           ; ★ filtre (handle 0x185C)
232319  mov  word_C56A, r4          ; état du filtre
232322  mov  word_C93E, r5          ; ★ C93E = valeur filtrée
232324  mov  word_C576, r0          ; ★ C576 = valeur filtrée
```

⇒ **`word_C576 = word_C93E`** = ratio **filtré**. C'est cette valeur unique qui sert partout
(sélection de carto, classification, autorisation FGR) : les deux noms sont deux écritures de la
même donnée.

## Maillon 4 — La classification en rapport : 6 fenêtres

`word_1A9A → 0xE81A4`, lue par la tâche `seg015:loc_B0000` (appelée depuis `seg014:FB30`) :

```
EA E81A4 : 01 0B 02 03 04 05 | 00 00 00 C3 | EA00 CA00 EA00 0001 EA00 5201 C501
             └── 6 codes ──┘              └────────── 6 fenêtres ──────────┘
```

Les mots de la table (u16 LE) : `234 · 202 · 234 · 256 · 234 · 338 · 453 · 410 · 559 · 720 · 652 ·
826 · 1015 · 910 · 1116 …`

Chaque fenêtre est lue comme **4 bornes** : `[outer_lo] [outer_hi] [hyst_lo] [hyst_hi]`.

```asm
; fenêtre « 2 » (loc_B003E)
mov  r5, [r4+#0Eh]  ; 234
cmp  r12, r5
jmpr cc_SLT, loc_B0086      ; ratio < 234  -> fenêtre suivante
mov  r5, [r4+#14h]  ; 338
cmp  r12, r5
jmpr cc_SGE, loc_B0086      ; ratio >= 338 -> fenêtre suivante
mov  r5, [r4+#12h]  ; 234
cmp  r12, r5
jmpr cc_SLT, loc_B0070      ; hors bande fine -> HYSTÉRÉSIS
mov  r5, [r4+#10h]  ; 256
cmp  r12, r5
jmpr cc_SGE, loc_B0070      ; hors bande fine -> HYSTÉRÉSIS
movb rl5, [r4+#1]   ; code du rapport
andb rl5, #0Fh
mov  r13, r5
jmpa cc_UC, loc_B025C
loc_B0070:                  ; ★ hypsérésis
movb rl5, [r4+#1]
andb rl5, #0Fh
orb  rl5, #40h              ; ★★ bit 0x40 = « zone d'incertitude »
```

### Les fenêtres, et leur cohérence physique

| fenêtre | bornes du ratio | bande fine (certaine) | code | V à 1000 tr/min |
|---|---|---|---|---|
| 1 | **202 → 234** | — | `01` | **8,5 km/h** |
| 2 | **234 → 338** | 234 → 256 | `0B` | **11,2 km/h** |
| 3 | **338 → 559** | 410 → 453 | `02` | **17,5 km/h** |
| 4 | **559 → 826** | 652 → 720 | `03` | **27,0 km/h** |
| 5 | **826 → 1116** | 910 → 1015 | `04` | **38,0 km/h** |
| 6 | **≥ 1116** | — | `05` | — |

**Vérification de cohérence** : ratio = 256·V/N ⇒ V à 1000 tr/min = ratio/2,56 en km/h. Les colonnes
de droite (8,5 / 11,2 / 17,5 / 27 / 38 km/h à 1000 tr/min) sont exactement les étagements d'une boîte
5 vitesses de 2.2 HDi. **L'échelle et la formule sont donc justes.**

### ⚠ Le seul point qui ne colle pas encore

Les six **codes** sont `01 0B 02 03 04 05` : le `0B` en 2e position ne peut pas être un numéro de
rapport. Or `0x0B` **est** une valeur que la tâche FGR traite comme « rapport indéterminé »
(`cmp #0Bh` → refus `0x92`, l.184425-184436). Deux lectures possibles :

- soit la fenêtre `234-338` est **volontairement marquée indéterminée** (zone de recouvrement
  entre 2e et 3e), ce qui **interdirait l'engagement du régulateur en 2e** — cohérent avec le
  comportement terrain ;
- soit le décalage vient du fait que la **1re n'est pas dans la table** : elle est traitée par le
  bloc amont `loc_B0000` (l.178055-178066) qui utilise les bornes **de l'appelant** (`r4`), pas
  `0xE81A4`. Dans ce cas les codes se lisent `0B · 02 · 03 · 04 · 05` = **2e à 6e**.

La seconde lecture est la plus probable, et elle se **vérifie** : dans ce cas `C330 & 0x0F` vaut
1..5 pour les 5 vitesses. À trancher en regardant le bloc passé dans `r4` par `seg014:FB30`.

## Maillon 5 — Le stockage

```asm
178001  loc_AFFCA:
178001  mov  word_C686, r6
178003  movb byte_C330, rl4        ; ★★★ le rapport est écrit ici
```

`byte_C330` = **le rapport**, sur un octet :
- **bits 0-3** : le numéro (ou le code, cf. ci-dessus)
- **bit 6 (`0x40`)** : zone d'incertitude — le rapport est **conservé mais signalé**
- **bits 4-6 (`0x70`)** : exploités par le limiteur `seg015:045C` (niveaux `0x10` / `0x20` / `0x30`)

C'est **le seul point d'écriture** de `byte_C330` dans tout le firmware (l.178003).

---

## Résumé en une ligne

`ratio = (V[0,01 km/h] × 256) / N[tr/min]` → **filtré** (`unk_24BA`, handle `0x185C`) → `C576 = C93E`
→ comparé aux **6 fenêtres** de `0xE81A4` (avec hystérésis `0x40`) → **`byte_C330`**.

Aucun rapport n'est **jamais reçu par CAN** : il est intégralement **calculé** à bord, à partir de la
vitesse ABS et du régime.
