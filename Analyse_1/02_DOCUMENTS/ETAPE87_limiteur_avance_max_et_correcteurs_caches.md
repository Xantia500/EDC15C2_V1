# ÉTAPE 87 — ★★★★★ Le « Max SOI Limiter » est trouvé : `0xEA658` = **plat à 1 280 = 30,0°** · et les 3 correcteurs cachés

> Ta fiche a mis le doigt exactement où il fallait. Le limiteur d'avance maximale existe, il est **plat à
> 30,0°**, il est **câblé en dur dans la chaîne de calcul** (`min(avance, C754)`), et il est entouré de
> **trois cartes de correction** appliquées en pourcentage. Tout est identifié, adresses et valeurs.

---

## 1. La chaîne complète, telle que le code la calcule

`loc_D2A6E` → `loc_D2AFC` (l.238062-238124) :

```
r15 = C744                                  (saturation 0x7FFF / 0x8000)
C740 = r15 ;  C75? = unk_2FAC(r3 = h 0x1D9A)   → carte cachée n°2
C742 = C750 × C976 / 10000  ←  mul + divl #2710h = POURCENTAGE
r15 += C742
C75? = unk_2FAC(r3 = h 0x1D9C)               → carte cachée n°3
r15 += (…)                                   → C73C
C75? = unk_2FAC(r3 = h 0x1D98)               → LIMITEUR
C754 ← r4                                    ← « MAX SOI »
```

et dans la chaîne principale (`loc_D4798` → `loc_D483C`) :
`D518 = Σ correctifs` → `+= carte 0xE2816` → **`min(·, C754)`** → `D51A`.

⇒ **`C754` est bien le plafond de l'avance totale**, exactement comme tu l'annonçais.

## 2. Les quatre cartes du bloc `0x1D96`–`0x1D9C`

Chacune fait **128 mots = 16 × 8**, à `EA` espacés de `0x100`.

| handle | EA | non nuls | plage brute | **en degrés (°CRK)** | rôle |
|---|---|---|---|---|---|
| `0x1D96` | `0xEA558` | 30/128 | 0 … 171 | 0 … **4,0°** | correcteur n°1 (très creux) |
| **`0x1D98`** | **`0xEA658`** | **128/128** | **1280 constant** | **30,0° constant** | **★ MAX SOI LIMITER** |
| `0x1D9A` | `0xEA758` | 38/128 | 0 … 256 | 0 … **6,0°** | correcteur n°2 (par blocs de 85 = 2,0°) |
| `0x1D9C` | `0xEA858` | 75/128 | −72 … 277 | **−1,7° … +6,5°** | correcteur n°3 (le plus riche) |

### Le limiteur `0xEA658` — 128 mots, une seule valeur : **1280**

`1280 × 0,0234375 = ` **`30,000°`** exactement.

⇒ **l'avance totale est plafonnée à 30,0° avant PMH**, quelle que soit la charge, le régime ou la température.

### ⚠ Conséquence pratique immédiate pour toute modification SOI

La carte principale `0xE2816` culmine à **25,0°**. Le limiteur est à **30,0°**.
**Il reste donc 5,0° de marge** avant que le plafond ne morde. Au-delà de 30,0° demandés dans `0xE2816`,
**tout gain est purement et simplement écrasé** — et sans aucun code défaut, ce qui rend le symptôme
« ma map ne fait rien » particulièrement déroutant.

### Les correcteurs, en degrés

`0xEA758` (h `0x1D9A`), blocs de 85 = 2,0° :

```
   0    0    0    0    0    0    0    0    0    0    0    0    0    0    0    0
 2,0  2,0    0    0    0    0    0    0  2,0  2,0    0    0    0    0    0    0
 2,0  2,0    0    0    0    0    0    0  2,0  2,0    0    0    0    0    0    0
 2,0  2,0  2,0    0    0    0    0    0  2,0  2,0  2,0    0    0    0    0    0
```

`0xEA858` (h `0x1D9C`), le plus actif — 170 = 4,0° :

```
   0    0    0    0    0    0 -0,7 -0,7    0    0    0    0    0    0    0 -1,7
   0    0    0  2,0  1,0  0,4  0,4 -0,7  4,0  4,0  4,0  2,8  2,9  3,3  4,7  4,7
 4,0  4,0  4,0  3,7  3,0  3,0  4,3  4,3  4,0  4,0  4,0  2,8  2,5  2,5  4,1  4,1
 4,0  4,0  4,0  2,6  1,6  1,4  1,4  1,4  4,0  4,0  4,0  2,5  1,0  0,3  0,3  0,3
```

Ces deux cartes sont appliquées **en pourcentage** (`× C75x / 10000`) : ce ne sont pas des degrés ajoutés
tels quels, mais des **modulations** de la grandeur amont.

## 3. Ce que ta fiche apporte, confronté à ce qu'on a

| ta règle | vérification dans le 4HX |
|---|---|
| `RPM + 0..7000` = **IQ** | ✅ exactement les axes de `0xE2816` (`C42E` 200-5000 × `C6A2` 0-7000) |
| `P_rail + 0..7000` = **TI** | ⚠ notre couple `C7C2`(119-1350 bar) × `C78A`(0-7900) : **`C78A` n'est ni IQ ni TI** — à trancher |
| Température `2431, 2531, 2731…` + facteur `0,1` / offset `−273,1` | ✅✅ **exactement** ce qu'on a établi (53 axes, 98 % d'entiers) |
| Rail `1500…13500` × `0,1` | ✅ `C7C2` = 1190…13500 |
| Turbo/atmo `900…2500` × `1` | cohérent avec les axes de suralimentation (800-2200 mbar) |
| Limiteur d'avance maxi | ✅✅✅ **trouvé**, `0xEA658`, plat à 30,0° |
| Correcteurs de température (petites maps 6×6 / 8×8) | ✅ 3 correcteurs trouvés (16×8) + les axes de température |
| Switch EGR (valeur simple 1 → 0) | ⏳ déjà identifié comme validé véhicule ; le **mécanisme** reste à documenter proprement |

## 4. `C562` : ton hypothèse IQ contre la mienne — le test qui tranche

| lecture | axe `0, 300, 10000, 12000, 14016, 18000` | crédibilité |
|---|---|---|
| **IQ** (÷1000) | 0 · 0,3 · **10** · **12** · **14** · **18** mg/cycle | très propre |
| **Pédale** (×0,01) | 0 % · 3 % · **100 %** · 120 % · 140 % · 180 % | **100 %** tombe pile, mais 180 % est impossible |

Les deux marchent sur les premiers points, la pédale casse au-delà de 120 %.
**Le test est trivial sur le véhicule** : `C562` porte l'identifiant **`0x0F08`** — une log de `0x0F08`
tranche en 30 secondes : s'il suit la pédale → pédale ; s'il suit la quantité injectée → IQ.

Et dans les deux cas la conclusion sur la carte reste la même : `0xE868C` est la **durée d'injection
additionnelle = f(T_LDR, charge)** — nulle à charge zéro, plafonnée à **9 230 µs ≈ 9,2 ms**.

## 5. `C78A`, le dernier axe inconnu

`0, 200, 1000, 1500, 2000, 3000, 4000, 6000, 7000, 7100 … 7900` (18 points, pas fin de 100 au-delà de 7 000).

Test des facteurs binaires que tu proposes : `7900/128 = 61,7` · `/64 = 123,4` · `/32 = 246,9` → **aucun
chiffre rond**, donc pas un facteur 1/128, 1/64 ou 1/32.
Test degrés : `7900 × 0,0234375 = 185°` — absurde pour une avance.
⇒ la forme (pas fin près du maximum) désigne un **régime** ou un **compteur de butée**, et `C78A` porte
l'identifiant **`0x1F64`** : une log de `0x1F64` le nomme directement.

## 6. Consignation

**`CATALOGUE_MAITRE.md` § 13 B.33** — chaîne `loc_D2A6E`→`loc_D2AFC`, les 4 cartes `0xEA558`/`0xEA658`/
`0xEA758`/`0xEA858` avec leurs valeurs en degrés, **MAX SOI = 30,0°**, marge de 5,0° sur la carte
principale, confusion possible `C562` IQ / pédale, test `C78A`.
