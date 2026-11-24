# ÉTAPE 111 — Autoriser la 2nde et 20 km/h au régulateur : solution chiffrée

**Bonne nouvelle : aucune modification de code n'est nécessaire.** Deux mots de calibration suffisent.
**Et une correction importante de l'Étape 109 s'impose d'abord (errata E24).**

---

## 1. Errata E24 — la numérotation des rapports était fausse

L'Étape 109 lisait les 6 fenêtres de `0xE81A4` comme « 1re à 6e ». C'est faux : la 2e fenêtre
n'est **pas un rapport**, c'est une **bande de transition**. Preuve : sa « bande certaine »
`[234,256[` est collée au **bord inférieur** de la fenêtre `[234,338[`, alors que toutes les autres
sont centrées (410-453 dans 338-559 ; 652-720 dans 559-826 ; 910-1015 dans 826-1116).

**Table corrigée** (codes = octets `+0` à `+5` de `0xE81A4` : `01 · 0B · 02 · 03 · 04 · 05`) :

| fenêtre | ratio | bande certaine | code | rapport | V/N (km/h / 1000 tr) | V à 2000 tr |
|---|---|---|---|---|---|---|
| 1 | 202 → 234 | — | `01` | **1re** | 0,79-0,91 | 16-18 km/h |
| 2 | 234 → 338 | 234-256 | `0B` | **transition** | 0,91-1,32 | 18-26 km/h |
| 3 | 338 → 559 | 410-453 | `02` | **2nde** | 1,60-1,77 | 32-35 km/h |
| 4 | 559 → 826 | 652-720 | `03` | **3e** | 2,55-2,81 | 51-56 km/h |
| 5 | 826 → 1116 | 910-1015 | `04` | **4e** | 3,55-3,97 | 71-79 km/h |
| 6 | ≥ 1116 | — | `05` | **5e** | ≥ 4,36 | ≥ 87 km/h |

### Ce que cela change

1. **Le seuil 768 tombe dans la bande de 3e** (`559-826`), pas de 4e ⇒ la règle est bien
   **« 3e minimum »**, exactement comme tu l'avais dit. ✔
2. **Le code `0x0B` ne bloque PAS la 2nde** : la 2nde renvoie `0x02`, qui **n'est pas** dans la
   liste des codes refusés (`6 · 0 · 9 · 0B · 0C · 0D`, l.178349-178360 et l.184427-184432).
   ⇒ **aucune modification de la table des fenêtres n'est nécessaire.** L'avertissement de
   l'Étape 110 §5 était erroné.
3. Le seuil `539` de la carte souhait (`sub_B56F8`) tombe **dans la bande de 2nde** (`338-559`) :
   la carte « basse » couvre donc **1re + transition + presque toute la 2nde** ⇒ la limitation de
   couple en 1re/2de est bien celle-là. ✔ (cohérent, sans changement)

---

## 2. Les deux seuls verrous à modifier

```asm
184672  mov  r4, word_14B0        ; bloc 0xE2788
184673  mov  r5, [r4]             ; +00 = 2500
184674  cmp  r5, word_C562        ; vitesse
184675  jmpr cc_SLE, loc_B40E6    ; 2500 <= V -> OK sinon 0x86
...
184705  mov  r5, [r4+#0Ah]        ; +0A = 768
184706  cmp  r5, word_C93E        ; ratio
184707  jmpr cc_SLE, loc_B413E    ; 768 <= ratio -> OK sinon 0x89
```

| adresse | valeur d'origine | signification | nouvelle valeur | effet |
|---|---|---|---|---|
| **`0xE2788`** | `2500` | V ≥ 25,00 km/h | **`2000`** | V ≥ **20,00 km/h** |
| **`0xE2792`** | `768` | ratio ≥ 768 (3e) | **`380`** | autorise la **2nde** (430), refuse encore la 1re (218) et la transition (234-338) |

`380` est choisi **juste sous** la bande certaine de 2nde (410-453) et **au-dessus** du haut de la
bande de transition (338) : marge de 12 % sous la valeur réelle de 2nde, et aucun risque de
confondre avec la 1re.

**Cohérence physique à 20 km/h** : en 2nde, N = V×256/ratio = 2000×256/430 ≈ **1190 tr/min**, donc
au-dessus du régime minimum `1000` (porte `+0x06`). ✔ Les deux patching sont compatibles.

## 3. ★ Le piège des blocs dupliqués — confirmé

Le bloc FGR existe **deux fois** dans le dump :

| copie | offset fichier | EA |
|---|---|---|
| 1 | `0x62788` | `0xE2788` |
| 2 | `0x72788` | `0xF2788` |

Recherche du motif de 16 octets `C4 09 A8 61 E8 03 94 11 00 0A 00 03 A0 0F E8 03` ⇒ 2 occurrences.
**Les deux copies sont patchées** (sinon la modification peut être ignorée selon la banque active).

## 4. Le patch, exécuté

`outils/patch_2nde_20kmh.py` → **`edc_2nde_20kmh.bin`** (8 octets modifiés) :

```
OK EA 0xE2788  vitesse mini   2500 -> 2000   [C4 09] -> [D0 07]
OK EA 0xE2792  ratio mini      768 ->  380   [00 03] -> [7C 01]
OK EA 0xF2788  vitesse mini   2500 -> 2000   [C4 09] -> [D0 07]
OK EA 0xF2792  ratio mini      768 ->  380   [00 03] -> [7C 01]
```

Bloc après patch : `D0 07 A8 61 E8 03 94 11 00 0A 7C 01 A0 0F E8 03`

## 5. ⚠ Ce qui reste à faire avant de flasher

1. **Checksums propriétaires non recalculés** (Étape 105) : `0xE0FF6-9`, `0xE0FFC-F`, `0xE434D`,
   `0xEBCFC-FF`, `0xEBF1B`. Le binaire **n'est pas flashable** en l'état — il faut passer par un
   outil de correction ou rejouer le calcul.
2. **Bit `0x10` de `C330`** : l'autorisation générique passe par cet état (`byte_D8CC == 2`,
   « décollage confirmé »). Il faut **vérifier par log** qu'il est bien établi à 20 km/h en 2nde.
   S'il ne l'est pas, aucune des deux modifications ci-dessus ne suffira.
3. **Seuil de dérive `+0x08 = 2560`** : à basse vitesse, l'écart filtré peut dépasser plus vite ce
   seuil et produire des coupures `0x8A`. À surveiller ; passer à `3200` si des cycles apparaissent.
4. **Plancher de consigne 40 km/h** (`[word_14AA+0x0A] = 0xE276C = 4000`, l.185291-185306) : ce
   n'est **pas** une porte d'engagement mais un maintien de consigne (état `D9CC = 0x50`).
   Ne pas y toucher dans un premier temps.
5. **Diagnostic en cas d'échec** : lire `byte_D9B3` — `0x86` = vitesse hors plage, `0x89` = ratio,
   `0x87`/`0x88` = régime, `0x92` = rapport indéterminé, `0x8A` = dérive.

## 6. Variantes

| objectif | `0xE2788` | `0xE2792` |
|---|---|---|
| 2nde + 20 km/h (recommandé) | `2000` | `380` |
| 2nde dès 30 km/h (plus prudent) | `3000` | `380` |
| 1re + 2nde (non recommandé) | `2000` | `200` |
| marge sous 20 km/h | `1900` | `380` |
