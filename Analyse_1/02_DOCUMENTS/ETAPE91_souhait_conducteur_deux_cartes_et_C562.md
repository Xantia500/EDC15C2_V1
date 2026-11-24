# ÉTAPE 91 — ★★★★★ Les DEUX cartes « souhait conducteur » · la sélection par la nervosité · **`C562` enfin tracé : c'est la quantité (8 000 = 80 mg)**

> Tout se recolle. Les deux cartes à axe pédale sont **deux variantes de réponse** qui ne diffèrent que
> sur **une seule colonne** (pédale = 20 %) — c'est exactement la « nervosité ». Le sélecteur est lu,
> **`sub_B56F8`**. Et `C562`, que nous cherchions depuis trois étapes, est le **compagnon de la même
> structure** : `C562 ← C578 = 8 000`.

---

## 1. Les deux cartes : `0xE8B50` et `0xE8BD4` (handles `0x1B66` / `0x1B68`)

```
[C42E][8] [0 600 750 1000 1300 1750 2250 5000]      ← axe Y = RÉGIME
[C6DA][6] [118 2000 4000 6000 8000 10000]           ← axe X = PÉDALE (0 → 100 %)
[grille 8 × 6]
```

**`0xE8BD4` (h `0x1B68`) — variante « normale » :**

| tr/min ↓ / pédale → | 1,18 % | 20 % | 40 % | 60 % | 80 % | 100 % |
|---|---|---|---|---|---|---|
| 0 | 1060 | 3372 | 5660 | 7260 | 8000 | 8000 |
| 600 | 460 | 2608 | 4928 | 6768 | 8000 | 8000 |
| 750 | 320 | 2400 | 4688 | 6684 | 8000 | 8000 |
| 1000 | 140 | 2132 | 4444 | 6408 | 8000 | 8000 |
| 1300 | 0 | 1844 | 4104 | 6064 | 8000 | 8000 |
| 1750 | 0 | 1520 | 3616 | 5606 | 7660 | 8000 |
| 2250 | 0 | 1260 | 3208 | 5180 | 7180 | 8000 |
| 5000 | 0 | 680 | 1846 | 3656 | 5740 | 8000 |

**`0xE8B50` (h `0x1B66`) — variante « nerveuse » : identique SAUF la colonne 20 %.**

| tr/min ↓ / écart | 1,18 % | **20 %** | 40 % | 60 % | 80 % | 100 % |
|---|---|---|---|---|---|---|
| 0 | 0 | **0** | 0 | 0 | 0 | 0 |
| 600 | 0 | **0** | 0 | 0 | 0 | 0 |
| 750 | 0 | **+50** | 0 | 0 | 0 | 0 |
| 1000 | 0 | **+350** | 0 | 0 | 0 | 0 |
| 1300 | 0 | **+500** | 0 | 0 | 0 | 0 |
| 1750 | 0 | **+450** | 0 | 0 | 0 | 0 |
| 2250 | 0 | **+350** | 0 | 0 | 0 | 0 |
| 5000 | 0 | **0** | 0 | 0 | 0 | 0 |

### Lecture

- L'unité est la même que partout ailleurs : **valeur / 100 = mg par cycle**. Plafond **8 000 = 80 mg**.
- La différence entre les deux cartes est **concentrée sur la colonne 20 % de pédale**, entre 750 et
  2 250 tr/min, avec un maximum de **+500 = +5 mg**.
- ⇒ **c'est très exactement la « nervosité à la pédale »** : la même demande finale, mais une montée en
  couple plus franche dès les premiers pour-cents. Rien d'autre ne change.

## 2. Le sélecteur : `sub_B56F8` (l.186826-186848)

```c
sub_B56F8:
  r8 = r13 ; r9 = r12                  ; mémorise les deux arguments (régime, pédale)
  r4 = word_C576
  word_C93E = r4                       ; copie de travail
  r5 = word_1B6A                       ; handle → EA 0xE8C58, [0] = 539
  r2 = [r5]
  cmp r2, word_C93E                    ; ★ LE TEST DE NERVOSITÉ
  jmpr cc_SLE, loc_B5722
      r12 = word_1B68 ; unk_1D50(r12, r13, r14)     ; carte NORMALE
  loc_B5722:
      r12 = word_1B66 ; unk_1D50(r12, r13, r14)     ; carte NERVEUSE
```

- Le seuil est **539** (`[0xE8C58]`), en regard de **`C93E`** (copie de `C576`).
- **`C93E > 539` ⇒ carte nerveuse `0x1B66`** ; sinon carte normale `0x1B68`.
- Les deux appels passent par `unk_1D50` (2-D) avec les deux axes : **régime et pédale**.

⇒ c'est bien **un sélecteur de mode** (ta « nervosité »), pas une carte unique — et il explique pourquoi
deux cartes quasi identiques cohabitent.

## 3. ★ `C562` : enfin tracé, et c'est la quantité

`loc_CFDA0` (l.232852-232870) :

```c
r7 = word_1470
r2 = [r7+#6]                 ; = 8000   (champ de calibration, EA 0xE2260)
r3 = 0
MDL = 0
word_C93E = MDL              ; C93E = 0
r0 = word_C93E
word_C576 = r0               ; C576 = C93E = 0
word_C578 = r2               ; C578 = 8000
word_F908 = r2               ; F908 = 8000
byte_F91A = r3               ; = 0
word_F904 |= 8000h

loc_CFDD2:
MDL = word_C578              ; MDL = 8000
word_C562 = MDL              ; ★★ C562 = 8 000
r0 = byte_F91A
word_C552 = r0               ; C552 = 0
```

**`C562`, `C576`/`C93E`, `C578`/`F908`, `C552`/`byte_F91A` forment une seule et même structure** :

| variable | rôle | valeur de repos |
|---|---|---|
| **`C562`** = `C578` = `F908` | **la quantité** (8 000 = **80 mg**) | 8 000 |
| **`C576`** = `C93E` | **l'indice de nervosité / mode** | 0 |
| `C552` = `byte_F91A` | l'état associé | 0 |

⇒ **`C562` n'est pas un capteur : c'est la quantité de carburant de référence de l'arbitrage**, à
**80 mg**, et son indice de mode associé est `C576`/`C93E` — celui-là même qui choisit entre les deux
cartes de souhait conducteur. **Ta lecture était juste** : c'est bien lié à l'IQ, dans le code de gestion
de l'injection, en aval des cartes à pédale.

## 4. Le lien avec le régulateur de vitesse

`sub_B56F8` est appelé depuis **`seg015:ABE0`**, et le site `C562` (l.187031) tombe dans la **même zone**
(l.1868xx-187.0xx) que l'arbitre `unk_1FE8` (étape 88). C'est cohérent avec ce que tu décris :

- le souhait conducteur est calculé **une fois**, par les deux cartes ;
- il entre dans un **arbitre** avec la demande du régulateur ;
- la « carte inversée » du régulateur est l'autre voie de la même fonction `unk_1D50` — il faut maintenant
  trouver la carte à **axe vitesse** correspondante.

**Question ouverte que tu poses** : arbitrage en **% pédale** ou en **IQ (mm³)** ? La réponse est dans ce
qu'on vient de voir : les deux cartes sortent **de l'IQ (mg)**, et `C562` = **80 mg** est la quantité de
l'arbitre ⇒ **l'arbitrage se fait en quantité**, pas en pourcentage de pédale.

## 5. Prochaines cibles

1. **L'autre carte** de la paire (axe vitesse ou consigne de régulateur) — chercher les objets à axe
   vitesse et à valeurs **décroissantes** (carte « inversée »).
2. **Le producteur de `C576`/`C93E`** : écrit en `l.140049`, `171718`, `172956`, `176887` — c'est là que
   se décide le mode (nervosité, clim, etc.), exactement comme tu le soupçonnes.
3. Retrouver la **colonne 20 %** dans le fichier pour qui veut modifier la réponse à la pédale : il suffit
   de toucher `0xE8B74`+… (les six mots de la 2ᵉ colonne), sans rien changer d'autre.

## 6. Consignation

**`CATALOGUE_MAITRE.md` § 13 B.38** — les deux cartes `0xE8B50`/`0xE8BD4` avec leurs grilles et leurs
écarts, `sub_B56F8` et le seuil 539, la structure `C562`/`C576`/`C578`/`C552`, et la conclusion
« l'arbitrage se fait en quantité (mg), pas en % de pédale ».
