# Étape 1 — La segmentation par cylindre : la table circulaire `0xD926` et le cluster `0xD916`

*ECU 0 281 010 877 — EDC15C2 / C167CR‑4RM — image `edc.bin`*
*Adresses = EA du listing IDA (offset `.bin` = EA − 0x80000). Toutes les variables `0xC***`/`0xD***` sont des **adresses proches** en page 3 (DPP3 = 3), donc de la RAM externe à `0x30000 + adresse`.*

---

## 1. Ce qui est prouvé — la table et son index

Tout le mécanisme tient dans un seul bloc, dans le segment `0xB0000` :

```
loc_B2030:                                   ; ---- INITIALISATION
        jb      word_FD0C.15, loc_B2050
        mov     r4, word_141E                ; pointeur (mémoire basse absente)
        movb    rl5, [r4+#4]
        movbz   r5, rl5
        mov     word_D91A, r5                ; D91A = N
        shl     r5, #1
        mov     word_D91C, r5                ; D91C = 2N   <-- LE MODULO

loc_B2050:
        mov     r4, word_D91C
        mov     word_D916, r4
        mov     r12, #0D94Ch ; r13 = 0 ; r14 = 9 ; calls 0, unk_2152   ; memset
        mov     r12, #0D95Eh ; ... idem                                   ; memset
        mov     r12, #0D970h ; ... idem                                   ; memset
        mov     r4, word_1B3C
        mov     r5, [r4+#16h]
        mov     r2, word_D91A
        mov     MDL, r5
        divu    r2
        mov     word_D948, MDL               ; D948 = [1B3C+16h] / N
        mov     r3, [r4+#12h]
        mov     r1, [r4+#14h]
        mul     r3, r1
        mov     word_D94A, MDL               ; D94A = [1B3C+12h] * [1B3C+14h]
        mov     word_D924, ZEROS             ; D924 = 0  (jamais réécrit ensuite)
```

et, dans la tâche synchrone suivante (`loc_B20E2`, identifiant de tâche `#610`) :

```
        movb    rl4, byte_C2E9               ; index d'événement courant (voir étape 0)
        movb    byte_C8F3, rl4
        mov     r4, word_C428                ; valeur mesurée à ranger
        mov     word_C91A, r4
        movbz   r2, byte_C8F3
        add     r2, word_D924                ; + offset (= 0)
        mov     r3, word_D91C                ; modulo 2N
        mov     MDL, r2
        divu    r3
        mov     word_D91E, MDH               ; D91E = slot = index mod 2N
        mov     r2, MDH
        shl     r2, #1
        mov     [r2+#0D926h], r4             ; table[slot] = word_C428
```

**Donc :** un tableau de 16 bits, indexé par `(index d'événement) mod 2N`, reçoit à chaque événement la valeur `word_C428`.

---

## 2. La taille du tableau est 16 mots — et c'est démontrable

Trois éléments concordent :

1. **La carte mémoire.** `word_D946` (résultat du calcul qui suit) est utilisée juste après et commence **exactement** à `0xD926 + 32 = 0xD946`. Un tableau plus long empiéterait sur les variables voisines (`D946`, `D948`, `D94A`…), qui sont toutes utilisées comme variables indépendantes.
2. **Les accès indexés** sont les seuls (`+0D926h`, `+0D928h`) et l'index est multiplié par 2 : `2 × slot ≤ 32` ⇒ `slot ≤ 15`.
3. **Le code somme 8 slots pairs + 8 slots impairs** (voir §5) : il traite donc le tableau comme **deux groupes de 8**.

⟹ **2N = 16, donc `word_D91A` (l'octet `[word_141E+4]`) vaut 8.**

> ⚠️ C'est un point important : **ce n'est pas 58**. La grille de traitement par événement n'est donc pas la roue 60‑2 dent par dent, mais un découpage de **16 pas par cycle** (deux groupes de 8). On y revient au §6.

---

## 3. Le contenu : ce que le slot mémorise

`word_C428` est une valeur « publiée » à chaque événement par la tâche synchrone du segment `0xC0000`. Elle est recopiée depuis les valeurs du noyau de mesure (`word_C42E` ↔ `word_C91C`, `word_C428` ↔ `word_C91A`) :

```
loc_C7E64:
        mov     r0, word_C91C
        mov     word_C42E, r0
        mov     r0, word_C91C
        mov     word_F8F6, r0
        mov     r0, word_C91A
        mov     word_C428, r0        ; publication vers le reste du système
```

Ce n'est donc pas une période de dent (celle‑ci reste dans `word_F65A/F65C` et `word_C420/C422`, voir étape 0), mais un **résultat déjà élaboré par la tâche synchrone** (typiquement la période du segment ou un temps normalisé).

---

## 4. La seconde table, plus parlante encore : `0xD5C0`

Dans le segment `0x90000` (`loc_9EExx`) il existe **une seconde grille, indexée par le même index d'événement**, mais en 32 bits :

```
        movbz   r2, byte_C8F3
        shl     r2, #2
        mov     r4, [r2+#0D5C0h]        ; horodatage 32 bits du slot (mot bas)
        mov     r5, [r2+#0D5C2h]        ; ... (mot haut)
        mov     r10, word_D6B2
        mov     r11, word_D6B4
        sub     r10, r4
        subc    r11, r5
        mov     word_D6B6, r10          ; delta = horodatage courant - table[slot]
        mov     word_D6B8, r11
        ...
        neg     r4 / addc r5,#0 / neg r5 ; valeur absolue
```

et plus loin `mov [r2+#0D5C0h], r4` / `mov [r2+#0D5C2h], r5` : **on réécrit l'horodatage du slot**.

Interprétation : chaque slot garde **son propre** dernier horodatage ; la différence est donc le temps écoulé **depuis le dernier passage dans le même slot**, c'est‑à‑dire **la période d'un cycle complet vue par ce slot**. Les 16 slots sont donc des « fenêtres de mesure » indépendantes qui se recouvrent.

C'est précisément la structure qui permet « pour chaque cylindre, une valeur, moyennée, filtrée ».

---

## 5. L'exploitation : comparaison des deux moitiés

`loc_B2214` → `loc_B228C` :

```
        mov     r2, word_D928 ; + D92C + D930 + D934 + D938 + D93C + D940 + D944
        mov     word_D984, r2          ; SOMME DES 8 SLOTS IMPAIRS
        mov     r3, word_D926 ; + D92A + D92E + D932 + D936 + D93A + D93E + D942
        mov     word_D982, r3          ; SOMME DES 8 SLOTS PAIRS
        mov     r12, r3
        sub     r12, word_D984         ; différence des deux moitiés
        mov     r13, word_D948         ; période angulaire de référence
        mov     r14, #2710h            ; 10000
        calls   0, unk_20AC            ; routine OS : normalisation / limite
        mov     word_D946, r4          ; résultat
```

Puis, par slot :

```
        mov     r5, word_D91E
        and     r5, #1                 ; slot pair ?
        jmpr    cc_NZ, loc_B22E0
        mov     r2, [table + 2*slot]                 ; valeur du slot
        ...  r1 = [table + 2*((slot + 2N - 1) mod 2N)] ; valeur du slot PRÉCÉDENT
        add     r1, word_D946
        cmp     r2, r1
        jmpr    cc_SGE, loc_B22E0
        ; sinon : incrémente un compteur par PAIRE de slots (0xD960 + 2*(slot/2))
```

Autour, deux jeux d'accumulateurs (8 mots chacun, `0xD94C…0xD95C` et `0xD970…0xD97E`) et un **compteur de fenêtre** :

```
loc_B2306:  sub word_D95E, ONES
loc_B230A:
            mov r4, word_1B3C
            mov r5, [r4+#12h]
            cmp r5, word_D95E
            jmpr cc_SGT, loc_B2380        ; fenêtre pas terminée -> on sort
            ; sinon : on reporte les 8 accumulateurs de 0xD970 dans 0xD94C
```

et l'armement de tout ça est conditionné par une batterie de seuils lus dans la structure `word_1B3C` :

```
        mov r2, [r5+#4]  ; cmp r2, word_C91C   (borne basse régime ?)
        mov r2, [r5+#6]  ; cmp r2, word_C91C   (borne haute régime ?)
        mov r2, [r5+#8]  ; cmp r2, word_C68A
        mov r2, [r5+#0Ah] ; cmp r2, word_C68A
        mov r2, [r5+#0Ch] ; cmp r2, word_C562
        mov r2, [r5+#0Eh] ; cmp r2, word_C908
        movb rl3, [r5+#10h] ; [r5+#11h]
```

---

## 6. Interprétation d'ensemble (et conséquence sur la roue 60‑2)

Le tableau de 16 slots, la comparaison **somme paire / somme impaire**, les seuils d'armement (régime, charge) et le compteur par paire de slots dessinent un algorithme classique Bosch :

> **mesure par fenêtre glissante de la régularité cycle à cycle**, avec un résultat normalisé (`word_D946`), un comptage de dépassements par paire de slots (`0xD960`), et un report dans des accumulateurs (`0xD94C`, `0xD970`) pour la sortie vers la régulation.

Et surtout, la conséquence sur ta question de départ :

* **Les 58 dents ne sont pas dans cette table.** Le pas de la grille est de **16 événements par cycle**, en deux groupes de 8. Si `word_D948 = [1B3C+16h]/8` correspond bien à **900 (soit 90,0° en dixièmes de degré)**, on a 8 × 90° = **720°** : la grille serait alors de **8 slots de 90°**, soit **4 par tour de vilebrequin** — exactement ton hypothèse des « 4 calculs par tour » — et le tableau de 16 mots stockerait **deux cycles** (comparaison cycle N / cycle N‑1).
* Si au contraire `[1B3C+16h]` vaut 3600 (360,0°), la grille serait de 8 × 45°… sur un tour, et les « 4 par tour » viendraient d'un sous‑échantillonnage ultérieur.
* Dans les deux cas, **le comptage dent par dent (58) et la détection du gap ne sont pas ici** : ils sont en amont, dans la couche qui produit `byte_C2E9` — et c'est un argument de plus pour aller voir la mémoire basse absente (étape 2).

---

## 7. Ce qu'il reste à relever (précis, actionnable)

| # | Quoi | Comment |
|---|---|---|
| 1 | `word_D91A` = **8** (déduit) | confirmé par la taille du tableau ; à recouper avec `[word_141E+4]` |
| 2 | `[word_1B3C+0x16]` → angle par slot | si = 7200 alors `D948` = 900 = 90,0° |
| 3 | `[word_1B3C+0x12]` et `[+0x14]` | `D94A = [+12]×[+14]`, `word_D95E` comparé à `[+12]` = nombre d'événements par fenêtre |
| 4 | signature de `unk_20AC` | appelée 250× dans tout le firmware : c'est la routine OS de normalisation/limitation. `(valeur, référence, 10000)` |
| 5 | qui lit `word_D946`, `word_D982`, `word_D94C`, `word_D970` | 2 à 4 lecteurs chacun → la suite de la chaîne (régulation) |
| 6 | `word_C428` exactement | ce que publie la tâche `#610` : période de segment ou temps normalisé |

Les points 2 à 5 sont **inaccessibles dans le dump actuel** : la structure `word_1B3C` est pointée depuis la mémoire basse absente (§5 de l'étape 0). Le point 1 est en revanche verrouillé par la structure du code.

---

## 8. Carte mémoire du cluster (pour IDA)

```
0xD916  = D91C (copie)              0xD94C..0xD95C  accumulateurs (9 mots en pratique)
0xD918  = snapshot byte_C2DE        0xD95E          compteur de fenêtre (décrémenté)
0xD91A  = N (=8)                    0xD960..0xD96E   8 compteurs, un par paire de slots
0xD91C  = 2N (=16) -> MODULO        0xD970..0xD980   8 accumulateurs (report)
0xD91E  = slot courant (reste)      0xD982          somme des 8 slots IMPAIRS
0xD920  = compteur de référence     0xD984          somme des 8 slots PAIRS
0xD922  = drapeau                   0xD5C0..0xD5FF  table des HORODATAGES 32 bits / slot
0xD924  = offset (toujours 0)
0xD926..0xD945 = TABLE 16 mots (valeur par slot)
0xD946  = résultat normalisé (appel OS unk_20AC)
0xD948  = période de référence angulaire
0xD94A  = produit de deux facteurs de calibrage
```

---

*Étape 1 terminée. Étape 2 (à suivre) : la détection du gap et la synchronisation — à chercher dans les routines qui lisent `byte_C2E9` en `0x9EExx`, `0xB20xx`, `0xC61xx`, `0xDExxxx`, avec la conclusion ci‑dessus : le gap est probablement **en amont** de cette grille, donc soit dans la tâche `#610`, soit dans l'OS absent.*
