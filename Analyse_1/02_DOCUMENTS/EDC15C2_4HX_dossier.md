# Bosch EDC15C2 + Infineon C167CR-4RM — PSA 2.2 HDi 16v (moteur 4HX / DW12TED4)

Dossier technique — état des connaissances publiques (documents PSA/Bosch, forums de reprogrammation, retours d'atelier).
_Version du 22/11/2026. Les valeurs marquées « typ. » ou « à vérifier » varient selon la référence exacte du calculateur : toujours confirmer sur l'unité ouverte._

---

## 1. Identification

| Élément | Donnée |
|---|---|
| Calculateur | **Bosch EDC15C2** (famille EDC15 « C » = Common Rail, génération 2) |
| Microcontrôleur | **Infineon/Siemens SAK-C167CR-4RM** (marquages Bosch sur le boîtier : `B59233` FA, `B59388` GA, `B00017` HA) |
| Moteur | **4HX / DW12TED4** — 2.2 HDi 16v, 2179 cm³, alésage × course 85 × 96 mm, Rv 18:1 |
| Puissance / couple | 98 kW (133/136 ch) à 4000 tr/min — 314 à 317 N·m à 1750–2000 tr/min |
| Injection | Common rail Bosch 1re génération (pompe **CP1**, injecteurs électromagnétiques **0 445 110 036**) |
| Véhicules | Peugeot 406 / 406 Coupé / 406 Break, **607**, Citroën C5 I (2000–2004). Version détarée 4HW (94 kW/128 ch) sur 807 / C8 |
| Réf. Bosch typiques | `0 281 010 262`, `0 281 010 370/371`, `0 281 010 597`, `0 281 010 880`, `0 281 010 933/934`, `0 281 011 361`, `0 281 011 516`, `0 281 011 781`… |
| Réf. PSA associées | 96 378 740 80, 96 387 948 80, 96 422 148 80, 96 482 681 80, 96 521 842 80… |
| Suffixes logiciels | `EDC15C2-5.3`, `-10.1`, `-34`… = générations HW/SW distinctes (les définitions de cartographies ne sont **pas** interchangeables) |
| Boîtier | PSA : versions **1 connecteur** et **3 connecteurs** (les 2.2 HDi 16v sont généralement en 3 connecteurs — vérifier) |

L'EDC15C2 équipe tous les HDi PSA common rail de 1999 à ~2004 (RHY, RHZ, RHS, RHW, 4HX, 4HW…). C'est le pendant PSA des EDC15P/V/VM du groupe VAG : même cœur C167, même 29F400, même logique de lecture boot mode.

---

## 2. Architecture matérielle du calculateur

### 2.1 Le C167CR-4RM

Cœur 16 bits de la famille C166 (Siemens/Infineon), architecture Von Neumann, 16 Mo d'espace d'adressage linéaire :

- **32 Ko de ROM masquée interne** — masque **Bosch** : routines bas niveau, bootstrap loader, accès flash/EEPROM, gestion du watchdog. C'est ce qu'on appelle le « **IROM** » dans le milieu du reverse engineering EDC15 (dumpable via le moniteur interne/Minimon).
- **4 Ko de RAM interne** (2 Ko IRAM + 2 Ko XRAM) — la RAM de travail du firmware ; les variables de calibration vivantes sont en RAM externe.
- Pipeline 4 étages, cycle d'instruction 80 ns @ 25 MHz ; PLL interne + horloge externe (quartz typ. 20 MHz sur les EDC15, à confirmer sur la carte).
- **1 CAN 2.0B actif** (15 objets de messages), **2 canaux série** (ASC0/ASC1 asynchrones + SSC synchrone utilisé en **SPI** pour l'EEPROM), **ADC 10 bits 16 voies**, 2 blocs CAPCOM 16 voies, PWM 4 voies, 5 chip-selects, 111 E/S, boîtier MQFP-144, 5 V.
- Broche **EA** : versions « ROM » ⇒ exécution depuis la ROM interne au reset, puis saut vers la flash externe. C'est ce mécanisme qui rend le **boot mode** possible (voir § 6).

### 2.2 Mémoires de la carte

| Composant | Type | Contenu |
|---|---|---|
| **29F400BT / 29F400BB** (TSOP48) | Flash 512 Ko (4 Mo) | Firmware complet + **zone de calibration (cartographies)**. Structure Intel : 1×16 Ko + 2×8 Ko + 1×32 Ko (boot sector) + 7×64 Ko |
| SRAM externe (2 × 32 Ko typ.) | RAM | Variables, stacks, buffers de diagnostic, apprentissages volatils |
| **95P08 / 5P08 (SPI, 1 Ko)** | EEPROM série | **Antidémarrage (immo)**, code injecteurs, VIN, adaptations, registres de défauts, compteurs (kilométrage ECU, temps de fonctionnement, régime maxi…) |
| ASIC Bosch + driver d'injecteurs | logique | Watchdog, étage de puissance injecteurs (peak & hold, convertisseur élévateur), commandes électrovannes |

Conséquences pratiques :

- **512 Ko = la totalité du dump flash** (pas de zone séparée « map » : les cartographies sont noyées dans le firmware, sans séparation nette, d'où l'intérêt des fichiers DAMOS/OLS).
- L'**EEPROM 1 Ko n'est pas lisible en OBD** : un vrai clonage (ou une reprise d'immo) impose le banc, le boot mode ou le dessoudage.
- Les pannes « plus de communication / antidémarrage » viennent très souvent de cette 95P08, pas de la flash.

### 2.3 Ce que le calculateur pilote (contexte 4HX)

Entrées : capteur de pression de rampe, capteur PMH inductif, capteur AAC (Hall), température d'eau, température d'air, pression de suralimentation, débitmètre **Siemens** à film chaud, température gasoil, capteur de pédale (2 pistes), contact de pédale de frein/embrayage, pression de clim.

Sorties : 4 électrovannes d'injecteurs, **régulateur de débit d'entrée (IMV)** sur la pompe CP1, électrovanne EGR, électrovanne de **géométrie variable** du turbo (Garrett/AlliedSignal, commande par dépression), **doseur d'air** Bosch (volet + doseurs air froid/chaud), relais de préchauffage, relais de pompe de gavage, voyants, climatisation, régulation de vitesse.

Sur les versions **FAP** (607 2.2 HDi notamment) : stratégie de régénération par post-injection gérée par l'EDC15C2, l'additif cérine étant géré par un calculateur d'additif séparé. À garder en tête avant toute modification de la cartographie d'injection : les modes « régénération » utilisent des post-injections dédiées.

---

## 3. Organisation du logiciel et de la calibration

- Code 16 bits C167 (compilé Bosch, outils internes), **sans symboles** dans le binaire commercial.
- En tête de flash : **bloc d'identification** (références Bosch/PSA, numéro logiciel type `1037xxxxxx`, variante, compteurs). C'est lui qu'on lit en « ECU ID » avec MPPS/Galletto/KT200 — d'où parfois des « points » à l'affichage sur ces vieux calculateurs, sans que cela empêche lecture/écriture.
- Zone de calibration : jeux de cartographies 8/16 bits + axes (paires de vecteurs), typiquement :
  - souhait conducteur / demande de couple, limiteurs de couple (par vitesse, par rapport),
  - quantité injectée (pilote + principale), cartographie de **début d'injection (SOI)**, correction par température/pression,
  - **pression de rampe** (consigne + régulation IMV), débit de pompe,
  - **EGR** (débit, taux, conditions), **suralimentation** (consigne de pression turbo / GV),
  - limiteur de fumée (rapport air/carburant), correction d'altitude, démarrage à froid, coupure à la décélération,
  - **régime maxi / limiteur de vitesse**, préchauffage, ventilateurs, climatisation.
- **Sommes de contrôle** : l'EDC15C2 vérifie l'intégrité de la calibration (deux sommes 16 bits + bloc de contrôle en fin de zone). Toute modification doit être suivie d'une **correction de checksum** (plugin EDC15C2 de WinOLS, correcteur ECM Titanium, etc.). Checksum non corrigé ⇒ défaut type P0601/P0602, voire non-démarrage.
- Versions SW (`-5.3`, `-10.1`, `-34`) : les adresses et l'allure des cartographies changent. Toujours partir d'un **dump complet de l'unité réellement montée**, jamais d'un fichier « équivalent ».

---

## 4. Communication et diagnostic

- Diagnostic moteur historique : **K-line ISO 9141 / KWP2000 (ISO 14230)** sur la broche 7 de la prise OBD, en 10 400 bauds (jusqu'à 38 400 / 124 800 pour les transferts). Côté outil : DiagBox/PP2000 + interface Actia, ou n'importe quel outil KWP2000.
- Le **CAN** du C167 sert aux échanges internes véhicule (ABS/ESP, BVA, combiné selon modèle) — les 406/607 de cette génération utilisent aussi un bus VAN pour le confort.
- Fonctions disponibles en diagnostic : lecture/effacement défauts, mesures (pression rampe réelle/consigne, débit, avance, EGR, turbo, débitmètre), tests d'actionneurs, codage injecteurs, télécodage d'options.
- Le régime de « **programmation** » (flash via OBD) existe : lecture/écriture flash possible par la prise diagnostic **quand l'antidémarrage n'est pas verrouillé**, ce qui est le cas de la plupart des EDC15C2 PSA — mais pas de l'EEPROM.

---

## 5. Chaîne d'injection — points de repère

| Élément | Référence / valeur |
|---|---|
| Pompe HP | Bosch **CP1** (simple piston, lubrifiée par le gasoil), régulation par **IMV** en entrée de pompe |
| Pression maxi | ~1350 bar (consigne courante 300–1350 bar selon charge) |
| Injecteurs | Bosch **0 445 110 036** ( électromagnétiques, 4 trous, code de correction par injecteur à saisir dans l'ECU) |
| Capteur de rampe | piézo-résistif 0–1500 bar, alimentation 5 V, sortie 0,5–4,5 V |
| Débitmètre | Siemens à film chaud (HFM5) |
| Turbo | Garrett/AlliedSignal VNT commandé par électrovanne de dépression |
| EGR | électrovanne pneumatique + doseur d'air Bosch |

Pièges classiques de ces moteurs, souvent mis à tort sur le compte du calculateur : injecteurs qui fuient (retours), capteur de rampe dérivant, IMV encrassée/coincée, durites de dépression, EGR bloquée ouverte, doseur d'air.

---

## 6. Lecture / écriture — les quatre voies

### a) OBD / K-line (le plus simple)
- Flash uniquement (512 Ko), EEPROM non accessible.
- Outils : MPPS, Galletto 1260/54, KESS, KT200, Autotuner, kw1281test (open source), etc.
- Nécessite le véhicule ou un banc correctement alimenté (+12V permanent, +APC, masse, K-line). Certaines cartes PSA demandent un montage « full mode » avec résistances 120 Ω sur des lignes spécifiques.

### b) Boot mode (recommandé sur banc, ou ECU verrouillé / brické)
- On force le C167 à démarrer dans son **bootstrap loader** (9600 bauds) au lieu d'exécuter le firmware : on met à la masse une broche du 29F400 pendant la mise sous tension puis on relâche après quelques secondes. Sur les cartes PSA, c'est **la broche 24 du 29F400** (d'autres cartes/utilisations citent la broche 2 : vérifier sur votre révision).
- Procédure type : ECU hors tension → masse sur la broche → appliquer +12V → retirer la masse après 3–5 s → lancer la lecture (« Generic Bosch EDC15Cx K-line », « Siemens-Infineon C167 / ME7 – flash 400 boot mode » selon l'outil).
- Permet lecture flash **et** EEPROM, y compris sur un calculateur verrouillé ; risque de brick très faible (on peut toujours recommencer).

### c) Banc « pinout » (full mode)
- Connexion directe sur les connecteurs du calculateur, sans véhicule. Utile pour un dump complet avant/après.
- Plus de câblage (alims, masse, K-line, parfois lignes de « wake-up » avec résistances).

### d) Dessoudage du 29F400 + programmateur
- La solution ultime (lecture certaine, récupération d'un ECU très abîmé), mais risque de destruction de la carte ; à réserver aux cas désespérés ou au clonage d'EEPROM 95P08 (l'EEPROM en SO8 peut aussi être lue sur place avec une pince).

### Outils logiciels
WinOLS (le plus courant, plugins checksum + drivers EDC15C2), ECM Titanium, Swiftec, CMD/CMDFlash, TunerPro (avec XDF communautaires), et pour le côté RE : **kw1281test** (flash/EEPROM EDC15 en KWP2000 et boot mode), désassembleurs/IDA Pro module **C166**, Ghidra (support C166), émulateurs C167.

---

## 7. Reprogrammation / préparation — ordres de grandeur et limites

- **Stage 1 réaliste** sur 4HX : ~118–132 kW et 370–400 N·m, en gardant de la marge sur le limiteur de fumée et la pression de rampe. Au-delà, la CP1, les injecteurs d'origine, l'embrayage/volant bi-masse et le refroidissement deviennent les facteurs limitants.
- Cartographies à toucher dans le bon ordre : limiteurs de couple d'abord (sinon la demande est bridée), puis quantité/pression de rampe, puis SOI, puis EGR/turbo, et **limiteur de fumée en dernier garde-fou**.
- Ne jamais modifier la zone « code » ni le boot sector : uniquement la calibration, avec correction de checksum.
- Sur version FAP : ne pas supprimer les stratégies de post-injection sans traiter la régénération (colmatage, dilution d'huile).
- Copies/échanges : un ECU d'occasion du même HW/SW se remplace en recopiant l'EEPROM (immo + code injecteurs) ; sinon il faut un outil de codage (DiagBox/PP2000) ou une désactivation d'immo.
- **Aspect légal FR** : la modification de la cartographie, la suppression d'EGR/FAP impactent la conformité (pollution, contrôle technique, assurance). À cadrer selon l'usage (circuit, véhicule de collection, projet d'étude).

---

## 8. Pannes connues et réparation

1. **Antidémarrage / plus de communication** : 95P08 corrompue (coupure de batterie, arc de soudure, « + » inversé). Réparation : réécriture EEPROM ou immo off, jamais un simple effacement de défauts.
2. **Micro-soudures** des broches de connecteurs (surtout les grosses broches d'alim) et du 29F400 : symptômes intermittents, coupures à chaud.
3. **Condensateurs électrolytiques** vieillissants (alim interne, filtrage) : reset aléatoires, démarrages difficiles à chaud.
4. **Étage injecteurs** (peak & hold) : destruction après court-circuit d'un injecteur ou injecteur très fuyant — panne souvent collatérale, à diagnostiquer avec les injecteurs.
5. **Entrée d'eau** dans le caisson du calculateur (607/406 : zone batterie) : oxydation, faux contacts.
6. **Faux « calculateur HS »** : dans 80 % des cas, le problème est capteur/actionneur ou faisceau. Avant de remplacer, contrôler pression de rampe réelle vs consigne, retours injecteurs, IMV, capteur PMH.

---

## 9. À retenir en 6 points

1. EDC15C2 + **C167CR-4RM** = plateforme PSA 1999–2004 ; 4HX est la version 2.2 HDi 16v 98 kW.
2. Le C167 a **32 Ko de ROM masquée Bosch** (IROM) + 4 Ko RAM ; tout le reste est **externe** : flash 29F400 de 512 Ko + SRAM + EEPROM SPI 95P08 de 1 Ko.
3. Le dump « flash » de 512 Ko contient firmware **et** cartographies ; l'EEPROM 1 Ko contient l'immo et les apprentissages — **deux mémoires, deux accès différents**.
4. OBD/K-line = flash seulement. Boot mode (masse sur broche 24 du 29F400 au power-up) ou banc = flash + EEPROM.
5. Toute modif de calibration exige une **correction de checksum**, et un dump de départ propre issu de l'unité montée.
6. Les variantes `EDC15C2-x.y` sont des SW différents : ne jamais mélanger fichiers et définitions.

---

## 10. Ressources utiles

- Forums de référence : nefariousmotorsports (thread « Reverse Engineering EDC15 », identification C167ROM), ecuconnections, lesamisdelaprog, ecuedit.
- Open source : `kw1281test` (gmenounos) — lecture/écriture flash et EEPROM EDC15 en KWP2000 et boot mode, calcul de checksum, sources du loader C166.
- Docs véhicule : Revue Technique Automobile 406/C5/607 2.2 HDi, documentation PSA « Haute Pression Direct Injection ».
- Datasheets : Infineon C167CR (peripheral + boot loader), Micron/AMD 29F400BT/BB, ST 95P08.
