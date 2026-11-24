# ÉTAPE 113 — Après le souhait : la cascade de limitation jusqu'à `C6B2`

Suite de l'Étape 108. `C6A6` (souhait conducteur) n'est **pas** utilisé directement : il traverse
**une cascade de 8 limiteurs** qui produisent `C6B2`.

---

## 1. Les consommateurs de `C6A6` — inventaire définitif (7 sites)

| ligne | usage | variable produite |
|---|---|---|
| `195504` | **production** : `C6A6 = souhait(C91C, C952)` (`sub_B56F8`, sélection par ratio 539) | `C6A6` |
| `171719`/`171723` | ΔIQ : `D2F4 = C6A6 − D834` | `D2F4` |
| `171734`, `171813` | comparaisons dans la boucle ΔIQ | — |
| `182735` | entrée de la cascade (+ `C69E`) | `D9A6` |
| `182752` | entrée de la cascade (directe) | `D9A6` |
| `185007` | arbitrage FGR : `cmp C6A6, C698` ⇒ `FD18.4` | drapeau |

## 2. ★★★ La cascade (seg015, l.182725 → 182880)

Sémantique vérifiée instruction par instruction — attention, **certains testent un plancher,
d'autres un plafond** :

```asm
182730  C91C = C42E                        ; régime
182732  if (byte_D9AC == 1)                        ; ★ mode « offset »
182735      D9A6 = C6A6 + C69E                     ; souhait + offset
182752  else D9A6 = C6A6                           ; souhait direct
182756  C6B8 = D9A6                        ; ★ SAUVEGARDE du souhait non limité
182759  if (D9A6 > C680) skip ; else D9A6 = C680   ; ← PLANCHER  (cc_SGT)
182765  D3E2 = D9A6
182768  if (D9A6 < C67E) skip ; else D9A6 = C67E   ; ← PLAFOND   (cc_SLT)
182775  if (D9A6 < C696) skip ; else D9A6 = C696   ; ← PLAFOND
182781  C6A4 = D9A6                        ; ★ valeur après 3 limiteurs
182783  if (D9AC == 1) D9AA = max(0, C6A4 − C69E) else D9AA = C6A4
182808  D3D4 = D9AA
182810  byte_C8F8 = courbe(word_1B5E, C91C, D9AA) ; ★ carto 2-D (régime × IQ)
182815  if (D9A6 > C688) skip ; else D9A6 = C688   ; ← PLANCHER
182822  D3E8 = D9A6 ; C6AE = D9A6           ; ★
182825  if (D9A6 < C682) skip ; else D9A6 = C682   ; ← PLAFOND
182832  C6AA = D9A6                         ; ★
182834  if (D9A6 < C6C0) skip ; else D9A6 = C6C0   ; ← PLAFOND
182841  byte_C33D = (C6C0 < C6AA)          ; ★ drapeau « bridé »
182853  D9A6 = sub_AF75A(D9A6)             ; ★ transformation
182856  if (D9A6 > C686) skip ; else D9A6 = C686   ; ← PLANCHER
182862  if (D9A6 < C684) skip ; else D9A6 = C684   ; ← PLAFOND
182869  C6B2 = D9A6                        ; ★★★ SORTIE FINALE
```

### Tableau des limiteurs

| var | sens | valeur d'init (sentinelle) | qui l'écrit réellement |
|---|---|---|---|
| `C680` | **plancher** | `0` (l.182707) | ★ **`C698` = demande du régulateur** (l.186652) |
| `C67E` | plafond | `0x7FFF` (l.182716) | jamais réécrit ⇒ inactif |
| `C696` | plafond | `0x7FFF` (l.182712) | jamais réécrit ⇒ inactif |
| `C688` | **plancher** | `0` (l.182706) | 4 sites : l.179821, 180409, 181315, 182706 |
| `C682` | plafond | `0x7FFF` (l.182715) | 4 sites : l.179820, 180333, 181239, 182715 |
| `C6C0` | plafond | `0x7FFF` (l.182713) | jamais réécrit ⇒ inactif |
| `C686` | **plancher** | `0` (l.182705) | tâche couple seg014 : l.177448, 178001 |
| `C684` | plafond | `0x7FFF` (l.177447) | tâche couple seg014 : l.177920 |

## 3. ★★★ Découverte : le régulateur agit par PLANCHER, pas par substitution

```asm
186644  mov  r4, word_C698
186645  cmp  r4, word_C690        ; saturation du PID
186647  mov  r5, word_C690
186648  mov  word_C698, r5
186651  mov  r4, word_C698
186652  mov  word_C680, r4        ; ★★ C680 (plancher de la cascade) = demande FGR
```

Combiné à l'arbitrage de l'Étape 108 :

```asm
185007  mov  r4, word_C6A6        ; pédale
185008  cmp  r4, word_C698        ; régulateur
185016  bset word_FD18.4          ; ★ la pédale reprend la main
```

⇒ **Le régulateur n'écrase jamais la pédale. Il impose un *minimum* d'injection.**
Quand la pédale demande moins que la consigne de régulation, c'est la consigne qui passe
(la voiture accélère / maintient) ; dès que la pédale demande **plus**, elle gagne
automatiquement par le simple jeu du plancher, ce qui lève `FD18.4`.

**C'est exactement le « cartes inversées remplaçant la pédale, sauf dépassement »** — mais
l'implémentation est remarquablement élégante : **une seule affectation, `C680 = C698`**, et le
comportement « sauf dépassement » est un effet émergent de la cascade.

## 4. Les variables intermédiaires produites (traces exploitables au log)

| variable | contenu |
|---|---|
| `C6B8` | **souhait brut**, avant tout limiteur ★ |
| `C6A4` | souhait après 3 limiteurs (plancher FGR, 2 plafonds) |
| `C6AE` | après plancher `C688` |
| `C6AA` | après plafond `C682` |
| `C6B2` | ★★★ **IQ finale** de la cascade |
| `D3E2` / `D3D4` / `D3E8` | traces étagées (segments) |
| `D9A6` | accumulateur de travail |
| `byte_C33D` | = 1 si `C6C0 < C6AA` ⇒ **« bridé »** |
| `byte_C8F8` | sortie de la carto 2-D `word_1B5E` |

**Preuve d'exploitation de `C6B2`** (l.178423-178428) :
```asm
178423  mov r4, word_C6B2
178424  cmp r4, word_C6A4        ; ★ IQ finale vs valeur après 3 limiteurs
178425  jmpr cc_NZ, loc_B0380    ; ≠  ⇒ un limiteur aval a agi
178426  mov r4, word_C6C0
178427  jmpr cc_NZ, loc_B038A
```
⇒ `C6B2 ≠ C6A4` alimente le **drapeau « limitation active »** (`bset USR0` l.178445, puis bit `0x40`
dans le mot d'état). C'est **l'indicateur à loguer** pour savoir si le couple est bridé.

## 5. La carto 2-D au milieu de la cascade

`word_1B5E → 0xE8A06` :
```
EA E8A06 : 2E C4 | 0A 00 | 00 00 58 02 EE 02 E8 03 ...
            tagY   n=10   axe : 0 · 600 · 750 · 1000 · ...
```
`tagY = 0xC42E` = **régime**. Évaluée à `(C91C, D9AA)` ⇒ `byte_C8F8`. C'est la seule **carte** de la
cascade ; tous les autres limiteurs sont des scalaires.

## 6. Le bloc `paramètre` du limiteur de débit : `word_18B2 → 0xE4E2C`

```
mots   : 2000 · 1500 · −2000 · −2500 · 5000 · 4500 · 13000 · 1100 · 600 · −15587
           35 ·  −20 ·   −10 ·  3000 · −15616 · −11788 · 8 · 0 · 500 · 1000
```

Utilisé dans la chaîne de l'Étape 104 (l.155117-155160) : les mots `+0x0E = 1100` et `+0x10 = 600`
encadrent `word_C8FE`, le résultat est stocké en `[r0+0x40]` puis **`[r0+0x08] = valeur + C596`**
(`C596 = 120`), avant le calcul `D1B6` et la correction `C594 = courbe(word_18A4, D1B6)`.

---

## 7. Où reprendre ensuite

1. **`sub_AF75A`** (l.182854) — la transformation appliquée juste avant les deux derniers limiteurs :
   c'est probablement l'arrondi/quantification d'injection. Non encore décodée.
2. **Les 3 sentinelles inactives** (`C67E`, `C696`, `C6C0`) : jamais réécrites ⇒ **aucun limiteur
   de couple actif sur ces voies** dans ce dump. À confirmer par un log (`C6B2` vs `C6A4`).
3. **Les limiteurs réels** `C682/C688` (4 sites : l.180333, 180409, 181239, 181315) — à identifier :
   ce sont eux qui brident réellement, avec la tâche couple seg014 (`C684`/`C686`).
4. **Le lien vers la durée d'injection** : qui lit `C6AE` / `C6AA` / `C6B2` en aval ?
