# ÉTAPE 119 — Suivre le code APRÈS le driver's wish : qui consomme quoi

Méthode imposée : **on ne nomme rien avant que le code le nomme.** Ce document suit donc les
consommateurs réels, ligne par ligne.

---

## 1. ERRATA E28 — alignement de la courbe plein gaz

Tu avais raison : **le 74,3 mm³ est à 2000 tr/min**, pas à 1750. La cause est une règle d'alignement
que je n'avais pas vue :

> **`valeur[k]` correspond à `axe[k+1]`** — l'axe compte **un point de plus** que le bloc de valeurs
> (19 points d'axe, 17 valeurs réelles). Mon tableau lisait `valeur[k] ↔ axe[k]` : tout était décalé
> d'une rangée.

**Tableau corrigé** (tag `0xC42E`, n=19, valeurs en 0,01 mm³) :

| tr/min | 50 | 800 | 1000 | 1250 | 1500 | 1750 | **2000** | 2250 | 2500 |
|---|---|---|---|---|---|---|---|---|---|
| **mm³** | 35,2 | 35,2 | 44,9 | 58,0 | 66,6 | 70,6 | **74,3** | 72,8 | 70,6 |

| tr/min | 2750 | 3000 | 3500 | 3750 | 4000 | 4250 | 4500 | 4800 |
|---|---|---|---|---|---|---|---|---|
| **mm³** | 68,7 | 68,1 | 64,4 | 62,7 | 62,4 | 56,9 | 53,0 | 47,5 |

`0xE83F8` = axe · `0xE841E` = séparateur `0` · `0xE8420` = première valeur.

## 2. ERRATA E29 — le modèle des « handles » était faux

Jusqu'ici je traitais `word_1446`, `word_1BE8`… comme des **identifiants de cartes**. C'est faux.

**Le code les DÉRÉFÉRENCE** — preuve, `sub_B64A8` :

```asm
mov     r4, word_1BE8
movb    rl5, [r4+#1]      ; octet à ptr+1
...
mov     r4, word_1BE8
movb    rl4, [r5]         ; octet à ptr+0
```

et `sub_BA684` :

```asm
mov     r4, word_148E
mov     r5, [r4+#16h]     ; mot à ptr+0x16
cmp     r5, word_C3C0
...
mov     r5, [r4+#18h]
```

⇒ **`0x1400–0x1FFF` = variables pointeurs en RAM**, initialisées au démarrage par la table de flash à
`0x61400` (`u16@(0x61400 + h − 0x1400)`). Ce ne sont pas des « numéros de cartes » mais **des
adresses de blocs de calibration**.

**Vérification** : `word_148E → 0xE2348`, et ses champs `+0x16 = 6000`, `+0x18 = 1200`, `+0x1A = 1200`
sont comparés à `C3C0` / `C3BE` — des seuils.

★ **Et cela confirme ta suspicion** : les pointeurs voisins `0x1BE0 … 0x1BEC` valent
`0xE8E06 · 0xE8E08 · 0xE8E0A · 0xE8E0C · 0xE8E0E · 0xE8E10 · 0xE8E12` — soit **2 octets d'écart**.
Ils pointent dans **le même bloc**, pas sur des cartes indépendantes. **Ce ne sont pas des cartes.**

## 3. Inventaire des consommateurs (extrait par le code)

Balayage de tous les `mov r14, word_1xxx` suivis d'un appel d'interpolation :

| | |
|---|---|
| sites **2-D** (`word_1D94`) | **63** — 32 variables pointeurs |
| sites **1-D** (`unk_1D6C`) | **44** — 21 variables pointeurs |
| total | **107 sites** |

Répartition par fonction (CSV complet : `sites_maps_usage.csv`) :

| fonction | sites | ce qu'elle utilise |
|---|---|---|
| `sub_B64A8` | 24 | 2-D `0x1444 · 0x1446 · 0x1448 · 0x1BEE · 0x1BF8 · 0x1BFA · 0x1C04` · 1-D `0x144A · 0x144C · 0x144E · 0x1C0C` |
| *(bloc après `sub_AFAA0`)* | 24 | 2-D `0x1446 · 0x1448` · 1-D `0x144E` |
| `sub_A7D96` | 23 | 2-D `0x18F8 · 0x18FA · 0x190E … 0x1918` · 1-D `0x1900 · 0x1902 · 0x190A · 0x190C · 0x192C · 0x1948 · 0x1958` |
| `sub_BAC40` | 11 | 2-D `0x1C84 · 0x1CAC … 0x1CBC` · 1-D `0x140A · 0x140C` |
| `sub_AB3AC` | 10 | 2-D `0x197C · 0x197E` · 1-D `0x1978 · 0x197A` |
| `sub_BF750` | 7 | 2-D `0x1DD8 · 0x1DEC · 0x1DEE · 0x1DF0 · 0x1DF6` · 1-D `0x1DE0 · 0x1DE6` |
| `sub_97FF8` | 3 | 2-D `0x1606` · 1-D `0x143C · 0x143E` |
| `sub_B7788` | 3 | 2-D `0x1CA6 · 0x1CA8` · 1-D `0x140A` |

## 4. ★★★ Le limiteur de fumée, trouvé par le code

`sub_B64A8`, l.188584-188592 :

```asm
mov     r4, word_C6A2      ; C6A2 = CHARGE (grandeur connue)
mov     word_C94C, r4      ; C94C := charge   (copie de travail, convention de la bibliothèque)
mov     r12, word_1BEC     ; pointeur de courbe
mov     r13, r4            ; entrée = charge
calls   0, unk_1D36        ; interpolation 1-D
mov     word_DA4E, r4      ; résultat intermédiaire
add     r4, word_C662      ; + OFFSET C662
mov     word_DA4E, r4
mov     word_C664, r4      ; ★ C664 = IQ max autorisé par la charge
```

⇒ **`C664 = courbe(charge) + C662`**. C'est la forme exacte d'un **limiteur de fumée (Rauchbegrenzung)**,
et il est **en mm³**, alimenté par la **charge** — pas par la vitesse, pas par un « couple ».

**Réserve honnête** : `C664` est écrit **une seule fois** et **jamais relu** dans la zone désassemblée
⇒ son consommateur est dans la bibliothèque / une tâche non désassemblée. On peut donc affirmer ce
qu'il **est**, pas encore **où il agit**.

Autres sorties du même sous-programme : `D412` (l.188569), `C914` (l.188575), `C94C` (l.188585),
`DA4E` (l.188589).

## 5. ★★★ La suite APRÈS le souhait, telle que le code la donne

### 5.1 Le triplet de sortie

l.189152-189187 :

```asm
mov     r12, r0
mov     r13, word_C6AA     ; ← l'IQ final (après le plafond C6C0)
mov     r14, word_144C     ; 1-D  -> 0xE13C6
calls   0, unk_1D6C
mov     r12, #6
add     r12, r0            ; X = pointeur r0+6
mov     r13, r0            ; Y = pointeur r0
mov     r14, word_1444     ; 2-D  -> 0xE130E
calls   0, word_1D94
mov     [r0+#12h], r4
add     r4, word_C678      ; + offset
mov     [r0+#12h], r4
...
loc_B6D5E:
mov     word_D41C, r8      ; ★
mov     word_D41A, r6      ; ★
mov     r4, [r0+#12h]
mov     word_D418, r4      ; ★
mov     r5, r8
sub     r5, word_C640
mov     word_C63E, r5      ; écart 1
mov     r2, r6
sub     r2, word_C640
mov     word_C63C, r2      ; écart 2
mov     r3, [r0+#12h]
sub     r3, word_C640
mov     word_C63A, r3      ; écart 3
```

**Trois évaluations de la même carte `0x1444` sur trois IQ différents → `D41C`, `D41A`, `D418`**, puis
**trois écarts à la référence `C640` → `C63E`, `C63C`, `C63A`**.

Puis `l.189194` : `D41E = D41C − C404` (branche conditionnée par `byte_C2C0`).

### 5.2 Qui consomme ces écarts

| variable | écrite | relue par le code |
|---|---|---|
| `C63A` | l.189188 | ★ **l.139993** et **l.140183** |
| `C640` | l.189482 | ★ l.140224 |
| `D418`/`D41A`/`D41C`/`D41E` | l.189176-194 | **jamais relues** dans le dump ⇒ bibliothèque |

### 5.3 La conversion finale en grandeur d'injecteur

`sub_9AE42` / `sub_9B0E0` (l.139990 et suivantes) :

```asm
mov     r12, word_C63A        ; l'écart d'IQ
mov     r5, word_1660
mov     r13, [r5]             ; paramètre lu dans un bloc de calibration
mov     r2, word_1658
mov     r14, [r2+#2]          ; second paramètre
calls   0, unk_20AC           ; ★ conversion
...
cmp     r4, #0FEh             ; saturation 0 … 254
movb    byte_C821, rl4        ; ★ sortie octet
```

Même bloc, l.140223 : `r12 = word_C640` → `byte_C822`.
Même famille : `byte_C820`, `byte_C823`, `byte_C824`, `byte_C81B … byte_C81F`, `byte_C88A`.

**Lecture par usage** : un IQ (mot, en 0,01 mm³) entre dans `unk_20AC`, ressort **saturé sur 8 bits
(0…254)** et est écrit dans un **octet**. C'est la signature d'une **grandeur de commande
d'injecteur** (durée / temps de conduction), pas d'un couple. Ces octets sont ensuite relus
(l.141404 `byte_C825`, l.141420 `byte_C827`, l.141664 `byte_C828`, l.141908 `byte_C829`).

### 5.4 La chaîne complète, désormais établie

```
pédale/régulateur
   └→ C6A6  (souhait, mm³)
        └→ limiteurs (plancher C680, plafonds C67E/C696) → C6A4
             └→ C8F8 = courbe0xE8A06( régime, C6A4−C69E )
                  └→ planchers/plafonds C688 / C682   ← courbes sur axe RPM (0xE83xx…)
                       └→ sub_AF75A → C6AA
                            └→ 1-D 0xE13C6 + 2-D 0xE130E  (×3 évaluations)
                                 └→ D418 / D41A / D41C
                                      └→ écarts C63A / C63C / C63E vs C640
                                           └→ unk_20AC → saturation 0…254
                                                └→ byte_C81B…C829, byte_C88A
                                                     └→ commande d'injecteur
```

**100 % des maillons ci-dessus sont adossés à des lignes de `clean.asm`.**

## 6. Ce que ça change pour tes objectifs

1. **La limitation de couple n'est nulle part en N.m** : elle est en **mm³**, produite par des courbes
   sur **axe régime** (`0xE83F4` : 74,3 mm³ à 2000 tr/min) et par le **limiteur de charge** `C664`.
2. **Les blocs 162 octets ne sont pas des cartes** : leurs pointeurs pointent à 2 octets d'intervalle
   dans un même bloc ⇒ ils désignent des **champs**, pas des grilles.
3. **Pour agir sur la 1re/2de**, les candidats réels sont maintenant : la courbe plein gaz `0xE83F4`,
   le limiteur de charge `C664` (`C662` = son offset), et les courbes `0xE8928`/`0xE89A8` (dont une
   vaut `10000` = aucune limitation).
4. **Reste à faire** : `sub_A7D96` (23 sites) et `sub_BAC40` (11 sites) ne sont pas encore lus — ce
   sont les deux prochains consommateurs à décortiquer pour fermer la chaîne côté fumée/air.
