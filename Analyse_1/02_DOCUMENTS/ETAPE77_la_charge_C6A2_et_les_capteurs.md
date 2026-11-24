# ÉTAPE 77 — `C6A2` : c'est la **charge**. Et le retour aux capteurs par les DTC

> Réponse à ta question, puis la campagne systématique : **tous** les identifiants présents dans les 93 records,
> traduits en adresses RAM, regroupés par famille de défaut, et confrontés aux grandeurs déjà établies.
> Deux capteurs neufs sortent nommés (pression différentielle FAP, préchauffage), et une règle de tri
> importante apparaît : **les 5 champs d'un record ne sont pas toujours des identifiants**.

---

## 1. Réponse directe : `C6A2` = la charge moteur

`C6A2` est **le 2ᵉ axe de toutes les cartes « régime × charge »** (l'axe Y), et en même temps **la mesure
d'une boucle fermée** dont la consigne est `C628`. Ce n'est **pas un capteur** : c'est une grandeur
**calculée, plafonnée puis filtrée**. C'est exactement pour cela qu'aucun DTC ne la surveille — elle
n'apparaît dans les records que comme **variable de contexte** figée au moment du défaut
(P1003, P1107, P1429, P1517).

## 2. Les cinq preuves

**P1 — c'est l'axe des cartes.** Onze cartes portent `C6A2` comme axe (avec `C42E` régime en axe 1) :

| EA de l'axe | nb points | valeurs |
|---|---|---|
| `0xE10BA` | 16 | 0 200 400 800 1200 1600 2000 2400 2800 3200 3600 4000 4500 5000 6000 7000 |
| `0xE10DE` | 8 | 500 1000 2000 4000 6000 8000 11000 12000 |
| `0xE13C6` | 9 | 0 1000 2000 3000 4000 5000 6000 7000 8000 |
| `0xE2AEE` | 7 | 500 1500 6000 7000 8000 9000 10000 |
| `0xE5468` / `0xE54F2` | 5 | 900 2200 3000 4000 5000 |
| `0xE5602` | 5 | 800 1200 1600 2000 3500 |
| `0xE5610` | 16 | 800 … 7000 |
| `0xE609A` / `0xE6102` / `0xE61B2` | 6 | 900 1600 2200 3000 4000 5000 |
| `0xE622E` / `0xE627A` / `0xE62C6` | 6 | 400 700 1000 1400 2000 2500 |
| `0xE7DAC` | 6 | 0 2200 3300 3800 4600 6000 |
| `0xE8E12` | 4 | 0 400 700 5000 |
| `0xE8EE0` | 8 | 0 … 7000 |
| `0xEAFBA`, `0xEB6CE` | 2 | 0–3500, 0–10000 |

**P2 — la structure d'une carte le dit noir sur blanc.** `EA 0xE2ADC` (handle `0x14CE`) :

```
[C42E][0007][02EE 03E8 0514 05DC 07D0 0A28 1388][C6A2][0007][01F4 05DC 1770 1B58 1F40 2328 2710][grille]
        régime : 750,1000,1300,1500,2000,2600,5000                charge : 500,1500,6000,7000,8000,9000,10000
```

**P3 — elle sert de mesure dans une interpolation + mise en %.** `sub_D4C1A` (l.241445) :
`r13 = C91C = C42E`, `r14 = C94C = C6A2`, `calls unk_2EE2` (2-D), puis
`mul r4, word_C7E0` / `divl #2710h` → résultat en **pour cent de 10000**.

**P4 — l'écart consigne − mesure est calculé.** `loc_A3FDA` (l.156386-156387) :
`r4 = word_C628 − word_C94C` → écart. `C628` est écrite à `loc_B2818` (l.182038, `mov word_C628, r9`) :
c'est la **consigne**. Et `loc_A4576` (l.156983) compare `C94C` à trois seuils de calibration
`[cal+#14h] / [#16h] / [#18h]` pour choisir l'une de deux valeurs.

**P5 — le producteur est un calcul borné.** Bloc `seg015 0xB71xx–0xB73xx` (l.189566 → 189860) :

```
r9 borné ≥ 0                                            (l.189610)
r9 plafonné par [word_142C+#0Eh] + word_C690            (l.189624)
r8 = word_C6A0 + r9                                     (l.189632)
machine d'état word_C948 ∈ {1,2,3} + compteurs C0EE/C0F0/DAF8   (l.189777-189840)
word_C94C ← r9     puis     word_C6A2 ← word_C94C      (l.189835 / 189839)
word_C6A2 ← 0      quand word_FD0C.15                   (l.189566)
```

`word_C690` est la sortie de la **carte de limite de fumée** : `unk_1D50(handle 0x1B40 = EA 0xE8444, régime C42E, air C3E6)`
(`loc_B26D2`, → `word_C690` puis → aussi `word_C626`).

⇒ **la charge = l'air admis mesuré, plafonné par la limite de fumée, filtré et maintenu par une machine d'état.**
C'est une grandeur élaborée, et cela répond à ta remarque : *« il existe sans doute d'autres valeurs
intermédiaires entre l'entrée et C3E6 »* — en voici la dernière marche de l'échelle.

## 3. De quoi est-elle la charge ? — les trois variables d'air, enfin distinctes

| RAM | identifiant | rôle | preuve |
|---|---|---|---|
| `C3E6` = `C3E8` = `C3E2` | **`0F30`** | **air admis mesuré** (trois miroirs du même mot) | `loc_97324` (l.131318-131322) : `[word_15F0+#4]` → `C3E8`, `C3E6`, `C3E2` ; `unk_1D50(0x1B40, C42E, C3E6)` |
| **`C6A2`** | **`0F8C`** | **charge retenue** = axe de carte + mesure de la boucle | P1 → P5 |
| `C5A8` | `E4D2` | masse d'air par tour (grandeur physique) | DTC P1429 |
| `C3EC` | *(aucun)* | **variante** d'air, sélectionnée par `byte_C2C9 < 0x30` (l.181913 vs 181922) | deux chaînes d'air possibles |

- **Unité** : mêmes décades que les variables d'air (axes 0 → 12000) ⇒ **mg d'air par tour × 10**
  (0…12000 ⇔ 0…1200 mg), exactement la convention de `C3E6` (500 mg = 5000).
  **Confiance : moyenne** — la décade est cohérente, mais une plage ne prouve pas une grandeur.
- **Le rôle (axe + mesure de boucle + consigne `C628`) : certain.**

## 4. La méthode pour remonter aux capteurs (et son piège)

Les **5 identifiants** d'un record DTC sont les **variables figées au moment du défaut** (freeze-frame) :
conditions de test et contexte. **Ce n'est pas forcément le capteur surveillé.**
Le capteur se reconnaît à l'identifiant **exclusif** de la famille :

- `0E80` → `C4B6` : présent dans P0401/0402/0403 **et rien d'autre** ⇒ EGR ;
- `0E91` → `C4DC` : P0530 seul ⇒ pression de clim ;
- `0EA2`/`0EA8` → `C4F6`/`C4E8` : P1608 seul ⇒ calculateur/pompe ;
- `0F40`+`0F41`+`0F42` → `C612`+`C60A`+`C614` : P0470 (+ airflow) ⇒ **pression échappement** ;
- `0F10` → `C42E` régime : dans **53** records sur 93 ⇒ variable de contexte universelle.

## 5. Tableau maître : les identifiants des records, leur RAM, leur fréquence

| identifiant | RAM | nb DTC | grandeur (confiance) |
|---|---|---|---|
| `0F10` | `C42E` | 53 | **régime moteur** (établi) |
| `0F80` | `C68A` | 27 | à nommer (contexte quasi universel) |
| `0F7F` | `C6E0` | 18 | à nommer (idem `0F7C`) |
| `0F00` | `C3D2` | 16 | **température LDR** (établi) |
| `0F01` | `C3BA` | 14 | à nommer |
| `0F30` | `C3E8` | 13 | **air admis mg/tour ×10** (= `C3E6`) |
| `0F65` | `C3C2` | 13 | **RCO EGR** (établi) |
| `2066` | `C376` | 10 | à nommer |
| `0FFC` | `C3AC` | 9 | à nommer |
| `0F40` | `C612` | 6 | pression (échappement/suralim.) |
| `0F71` + `0F70` | `C416` | 6 + 4 | **même adresse** (deux identifiants) |
| `0F08` + `000D` | `C562` | 5 + 1 | **même adresse** |
| `0F32` | `C3EA` | 5 | voisin de l'air — seconde grandeur d'air |
| `0E80` | `C4B6` | 4 | **EGR** (propre) |
| `0F60` | `C3C0` | 4 | à nommer |
| `0F8C` | `C6A2` | 4 | **charge** (cette étape) |
| `0FFA` | `C3BE` | 4 | à nommer |
| `E4D1` | `C5B8` | 4 | FAP / turbo |
| `0EA5` | `C4D6` | 3 | rampe (EGR-bloc réutilisé) |
| `0F64` | `C3A8` | 3 | rampe |
| `0F86` | `C6B4` | 3 | à nommer |
| `E4D3` | `C5BC` | 3 | FAP |
| `E4D6` | `C31E` | 3 | turbo |
| `E4E2` | `C248` | 3 | FAP |
| `0F41` / `0F42` | `C60A` / `C614` | 2 / 1 | **pression échappement** |
| `0FF6` | `C3C6` | 2 | à nommer |
| `0FF8` / `0FF9` | `C7EC` / `C7F0` | 2 / 2 | rampe (P1169/1170) |
| `0FFB` / `1114` | `C396` / `C39E` | 2 / 2 | turbo |
| `E4D4` | `C5F4` | 2 | FAP |
| `E4D7` | `C5A4` | 2 | turbo |
| `E4E3` | `C228` | 2 | FAP |
| `0E82` | `C4DE` | 1 | PAP (P1402) |
| `0E91` | `C4DC` | 1 | **pression clim** (P0530) |
| `0EA2` / `0EA8` | `C4F6` / `C4E8` | 1 / 1 | calculateur (P1608) |
| `0F8A` | `C690` | 1 | **sortie carte limite de fumée** |
| `0FD7` | `C33B` | 1 | FAP (P1435) — *octet* |
| `0FD8` | `C6AA` | 1 | P1003 |
| `0FF7` | `C3C8` | 1 | P1614 |
| `1E81` | `C4F8` | 1 | P1107 |
| `E4D0` | `C596` | 1 | turbo (P1429) |
| `E4D2` | `C5A8` | 1 | masse d'air/tour |
| `E4D8` / `E4D9` / `E4DA` / `E4DB` | `C598` / `C2FA` / `D212` / `C321` | 1 chacun | additif FAP (P1451) |

**Livraison :** `identifiants_dans_DTC.csv` (103 identifiants distingués dans les records, RAM + nb de DTC)
et `capteurs_par_DTC.csv` (famille → DTC → identifiants → RAM).

## 6. ★ Le retour aux capteurs : tableau par famille

| famille | DTC | identifiants → RAM |
|---|---|---|
| **Débitmètre / air** | P0100, P0101 | `0F01`→`C3BA`, `0F10`→`C42E`, `0F30`→`C3E8`, `0F32`→`C3EA`, `0F40`→`C612` |
| | P0104, P0106 | littéraux (`000A`, `0045`, `6463`…) — pas des identifiants |
| **T° air admission** | P0110 | `0F00`→`C3D2`, `0F01`→`C3BA`, `0F10`, `0F30`, `0F7F`→`C6E0` |
| **T° LDR** | P0115 | `0F00`→`C3D2`, `0F01`, `0F10`, `0F80`→`C68A`, `2066`→`C376` |
| **Pédale / potentiomètres** | P0121, P0221 | `0F60`→`C3C0`, `0F71`→`C416`, `0F80`, `0FFA`→`C3BE` |
| **T° carburant** | P0180 | `0F00`, `0F10`, `0F80`, `0FFC`→`C3AC`, `2066` |
| **Pression rampe** | P0190, P0191, P1168 | `0EA5`→`C4D6`, `0F10`, `0F64`→`C3A8`, `0FFC`, `2066` |
| | P1135 | `0F00`, `0F10`, `0F7F`, `0F80`, `0FFC` |
| | P1169, P1170 | `0F10`, `0F65`, `0F80`, `0FF8`→`C7EC`, `0FF9`→`C7F0` |
| **Injecteurs 1-4** | P0201…P0204 | `0F10`, `0F30`→`C3E8`, `0F80`, `0FFC`, `2066` |
| **Préchauffage** | P0381 | `0F00`→`C3D2`, `0F01`, `0F10`, `0F65`, `0F7F` ⇒ surveillé en **T° LDR × régime** |
| **EGR** | P0401…P0403 | `0E80`→**`C4B6`**, `0F10`, `0F30`→**air**, `0F32`→`C3EA`, `0F80` |
| **Pression échappement / ΔP FAP** | P0470 | `0F10`, `0F40`→`C612`, `0F41`→**`C60A`**, `0F42`→**`C614`**, `0F7F` |
| **Vitesse véhicule** | P0503 | littéraux (`01F4`=500, `F8FF`, `C301`) |
| **Pression fluide clim** | P0530 | `0E91`→**`C4DC`**, `0F00`, `0F01`, `0F10`, `0F7F` |
| **Batterie / alternateur** | P0560, P0568, P0571 | `0F08`→`C562`, `0F10`, `0F65`, `0F70`→`C416`, `0F71`, `0F86`→`C6B4`, `0F7F` |
| **Calculateur / pompe** | P0604, P1601, P1606, P1608, P1614 | `0EA2`→`C4F6`, `0EA6`, `0EA8`→`C4E8`, `0FF6`→`C3C6`, `0FF7`→`C3C8`, `0F65`, `0F7F` |
| **Électrovannes EGR/PAP** | P1402, P1403, P1404 | `0E80`→`C4B6`, `0E82`→`C4DE`, `0F30`, `0F70`, `0F7F`, `0F80` |
| **Turbo / suralimentation** | P1421, P1425, P1458 | `0FFB`→`C396`, `1114`→`C39E`, `E4D6`→`C31E` |
| | P1429 | `0F8C`→**`C6A2` charge**, `E4D0`→`C596`, `E4D1`→`C5B8`, `E4D2`→`C5A8` |
| **FAP / additif** | P1435 | `0FD7`→`C33B` *(octet)*, `E4D1`, `E4D3`, `E4E2` |
| | P1442, P1446 | `E4D1`, `E4D3`, `E4D4`→`C5F4`, `E4E2`, `E4E3`→`C228` |
| | P1451 | `0F10`, `E4D8`→`C598`, `E4D9`→`C2FA`, `E4DA`→`D212`, `E4DB`→`C321` |
| **Dosage / volet** | P1517 | `0F08`, `0F10`, `0F65`, `0F7F`, `0F8C`→**charge** |
| | P1521, P1537 | `0F10`, `0F60`, `0F71`, `0F80`, `0F86` |
| **Boîte / CAN / ABS** | P0700, U0300/301/303, U1008, C1014 | **littéraux uniquement** (200, 3431, 5000, 9000…) |

## 7. Trois découvertes de cette étape

1. **Le ΔP FAP est nommé.** P0470 s'appuie sur **trois mots voisins** `C60A`, `C612`, `C614` ⇒ le capteur de
   pression différentielle du FAP travaille dans `C60A`–`C614`. C'est la première zone FAP identifiée
   **par un DTC** et non par supposition.
2. **Le préchauffage est surveillé en T° LDR × régime** : P0381 = `0F00` (`C3D2`) + `0F10` (`C42E`).
   Cela confirme la carte bougies (RPM, T_LDR) déjà repérée : le diagnostic utilise les mêmes deux axes.
3. **Règle de tri nouvelle** : dans les records, **les 5 champs peuvent porter un identifiant OU une constante**.
   Preuve : P0106 porte `6463 6968 7270 7574 7776` (ASCII « cdihrptuv » = valeurs de seuil),
   U0300 porte `00C8 0D67 1388 2328` (200, 3431, 5000, 9000). Sur 93 records, **103 identifiants** seulement
   sont de vraies variables ; le reste est numérique.

## 8. Prochaines cibles

1. Nommer les **quatre gros génériques** : `C68A` (`0F80`, 27 DTC), `C6E0` (`0F7F`, 18), `C3BA` (`0F01`, 14),
   `C376` (`2066`, 10) — ils portent le contexte de la moitié des records, les nommer éclaire tout le reste.
2. Le bloc EGR `C4B6` – `C4F6` : dix variables à nommer, `C4B6` d'abord.
3. Vérifier l'unité de `C6A2` par une voie indépendante (chaîne ADC ou table de PID).
4. Décoder le 3ᵉ tableau parallèle `EA 0x91794` (format / validité par identifiant).

## 9. Consignation

**`CATALOGUE_MAITRE.md` § 13 B.23** — charge `C6A2` et ses 5 preuves, les trois variables d'air,
le tableau identifiant → RAM des records, le tableau par famille de capteur, la règle identifiant/constante.
