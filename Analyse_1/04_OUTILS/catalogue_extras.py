#!/usr/bin/env python3
"""
Extras du CATALOGUE MAITRE : nomenclature des cartes et axes, schemas des boucles
comprises, et chaine entree/sortie.

Regle d'or : un nom n'est donne que si l'on sait. Sinon on ecrit explicitement
« non identifie » et on donne ce qui EST etabli (axe, magnitude, consommateur).
"""

# ------------------------------------------------------------------ temperatures
# Convention (utilisateur) : les temperatures sont codees en KELVIN x 10.
# Verification : 2731 = 0 C, 3531 = 80 C.
def kelvin_c(x):
    """valeur brute -> chaine 'xx,x C (yyy,y K)'"""
    try:
        k = x / 10.0
        return '%+.1f C' % (k - 273.15)
    except Exception:
        return '?'

# ------------------------------------------------------------------ axes
# nom, unite, confiance, note
AXES = {
    'word_C42E': ('Régime moteur', 'tr/min', 'lu', 'plage 0…6000, 91 axes — axe dominant du calculateur'),
    'word_C3E6': ('Quantité d’air mesurée par le débitmètre — abscisse de la smoke map',
                  'mg ×10 (500 mg = 5000 en flash)', 'CONFIRMÉ utilisateur, 100 %',
                  'vérifié : carte 0xE8444 = régime × C3E6, 16×16'),
    'word_C3D2': ('Température liquide de refroidissement', 'K×10 (°C = v/10 − 273,15)',
                  'CONFIRMÉ utilisateur, 100 %',
                  'chaîne voie 11 + courbe 0xE8084 (ralenti 1100→750 tr/min, axe 2531=−20 °C … 3231=+50 °C)'),
    'word_C3BA': ('Température air d’admission', 'K×10', 'lu',
                  'chaîne voie 6, prouvée C3BA→C904→D094 ; axes 2231…4081 = −50…+135 °C'),
    'word_C3B0': ('Température carburant', 'K×10', 'CONFIRMÉ utilisateur',
                  'vérifié : EXACTEMENT deux cartes l’utilisent (0xE7F7E 8×4 et 0xE8000 8×6)'),
    'word_C5A4': ('Température (sonde non tranchée)', 'échelle non tranchée', 'inf',
                  'axes 2431…3331 → −30…+60 °C si K×10, ou 243…333 °C si °C×10'),
    'word_C586': ('Température d’échappement (probable)', '°C×10 (ou K×10 : non tranché)',
                  'inf', 'axes 3731…8731 → 373…873 °C si °C×10, ou 100…600 °C si K×10'),
    'word_C6A2': ('Grandeur de charge', '0…100 % (×100)', 'lu', 'plage 0…10000 ; presque toujours en X'),
    'word_C3C2': ('Rapport cyclique (RCO)', '0…1000', 'inf', 'plage 0…678 — électrovannes / EGR / N75'),
    'word_C5A8': ('Masse d’air par tour', 'mg ×10', 'inf', 'axes 1300…11000 = 130…1100 mg/tour'),
    'word_C7C2': ('Grandeur non identifiée', '?', '?', 'plage très large 6…14000'),
    'word_C60A': ('Grandeur non identifiée', '?', '?', 'plage étroite 600…1800'),
    'word_D004': ('Grandeur non identifiée', '?', '?', 'plage 0…7000'),
    'word_C3EE': ('Grandeur non identifiée', '?', '?', 'plage 0…4910'),
    'word_C60E': ('Grandeur non identifiée', '?', '?', 'plage 0…7000'),
    'word_C3A8': ('Grandeur non identifiée', '?', '?', 'plage 400…2400'),
    'word_C612': ('Grandeur non identifiée', '?', '?', 'plage 700…2200'),
    'word_C77A': ('Grandeur non identifiée', 'profil de limitation', 'inf', 'valeurs 0,5000,10000,10000,0'),
    'word_C562': ('Grandeur non identifiée', '?', '?', 'plage 0…20000'),
    'word_D1F4': ('Grandeur non identifiée', '?', '?', 'plage 0…5000'),
    'word_C68A': ('Grandeur non identifiée', '?', '?', ''),
    'word_C78A': ('Grandeur non identifiée', '?', '?', ''),
    'word_D012': ('Grandeur non identifiée', '?', '?', ''),
    'word_D002': ('Grandeur non identifiée', '?', '?', ''),
    'word_D006': ('Grandeur non identifiée', '?', '?', ''),
    'word_D094': ('Grandeur non identifiée', '?', '?', ''),
    'word_C63C': ('Grandeur non identifiée', '?', '?', ''),
    'word_C5BC': ('*** ANOMALIE ***', 'axe négatif', '?', 'axe −32768…−29408 : alignement à vérifier'),
}


def nom_axe(tag):
    a = AXES.get(tag)
    if a:
        return a[0]
    return 'non identifiée'


def nom_carte(tagY, tagX):
    """nom explicite d'une carte 2-D"""
    y = nom_axe(tagY)
    x = nom_axe(tagX)
    return '%s × %s' % (y, x)


def etendue_c(tag, lo, hi):
    """si l'axe est une temperature, donner l'equivalent en °C"""
    a = AXES.get(tag)
    if a and 'K×10' in a[1]:
        return '%s … %s' % (kelvin_c(lo), kelvin_c(hi))
    return ''


# ------------------------------------------------------------------ chaine E/S
def lignes_io(csv_path):
    """construit la table entree/sortie depuis capteurs_ADC_et_chaines_de_mesure.csv"""
    import csv
    try:
        rows = list(csv.DictReader(open(csv_path), delimiter=';'))
    except Exception:
        return []
    out = []
    for r in rows:
        v = (r.get('verdict_etape13') or '')
        cap = 'non identifié'
        up = v.upper()
        for key, lab in (('DEBITMETRE', 'Débitmètre (2 éléments)'),
                         ("PRESSION D'ENVIRONNEMENT", 'Pression d’environnement (mbar)'),
                         ("AIR D'ADMISSION", 'Température air d’admission (CTN)'),
                         ('GASOIL', 'Température gasoil (CTN)'),
                         ('EGT', 'Température d’échappement (thermocouple)'),
                         ('LIQUIDE DE REFROIDISSEMENT', 'Température LDR (CTN)'),
                         ('CTN', 'Sonde CTN (2ᵉ gamme)'),
                         ('FENETRE', 'Voie de plausibilité (pas de conversion)'),
                         ('mV', 'Voie brute en mV')):
            if key in up:
                cap = lab
                break
        if 'paire redondante' in v:
            cap = 'Voie ratiométrique redondante (0,5-4,5 V)'
        out.append(dict(
            tache=r.get('tache', ''), voie=r.get('voie_ADC', ''),
            capteur=cap, courbe=r.get('courbe_EA', ''), n=r.get('n_pts', ''),
            sortie='%s…%s' % (r.get('sortie_min', ''), r.get('sortie_max', '')),
            ram=r.get('RAM_physique_D0xx', ''), c3=r.get('copie_travail_C3xx', ''),
            defaut=(r.get('chemin_defaut_r3') or '').strip(),
            note=v[:150]))
    return out


# ------------------------------------------------------------------ schemas
SCHEMAS = r'''
### Boucle A — Acquisition capteur → grandeur physique

Tout passe par une **tâche périodique** identifiée par un numéro (`0x302`, `0x308`, `0x318`…).
La chaîne est toujours la même :

```
   capteur            ADC                descripteur          COURBE 1-D
 (CTN, débitmètre) ──► voie n ──► [EA descripteur] ──► [EA courbe] ──► valeur
                          │            (0xE349C)          (0xE34A8)     physique
                          │                                              │
                          │                                              ▼
                          │                                    word_D0xx  (valeur brute + copie)
                          │                                              │
                          │                                              ▼
                          └──────────────► chemin de défaut (r3) ──► word_C3xx (copie de travail)
                                                                         │
                                                                         ▼
                                                              word_C9xx  (instantané du diagnostic)
                                                                         │
                                                                         ▼
                                                          cartes / courbes (axe = cette variable)
```

**Preuve de bout en bout (voie 6, air d'admission)** :
`0xE353C` (descripteur) → `0xE3548` (courbe 16 pts, 4031…2331) → `word_D06C` →
`word_C3BA` → `word_C904` → `word_D094`.
Ce chaînage est **établi** (étape 13) et c'est lui qui donne le sens de l'axe.

**Table complète : voir § 12.**

---

### Boucle B — Diagnostic : du seuil au défaut mémorisé

```
   grandeur mesurée (word_C3D2 = température LDR)
            │
            ▼
   instantané  word_C908  ◄── copie à chaque cycle (l. 153232)
            │
            ▼
   MONITEUR  ──►  word_CFD4 : 1 bit par moniteur (16 max)
            │        bit 0 = critère de DURÉE   (seuil n°2, [word_142A+6])
            │        bit 7 = critère de VALEUR  (seuil n°1, [word_142A+0])
            │
            │  inhibitions : byte_C2F5, byte_CFDC, word_C0BC
            │  inhibition globale : word_FD2E
            │  power latch : word_FD0C.15 GÈLE l'évaluation (l. 153175)
            ▼
   CONFIRMATION  sub_A1E9E
            │        and word_CFD4, r12
            │        décompte byte_CFC4   (anti-rebond)
            ▼
   word_CFD6  = DÉFAUT CONFIRMÉ  (1 bit par moniteur)
            │
            ▼
   mémoire des défauts  0xCAD0 : 96 × 4 octets  (+0 drapeau, +2 mot)
            │            byte_E466 = nombre mémorisé (0…7)
            │            0xE467 : 7 enregistrements × 22 octets
            ▼
   code transmis  0xCCB2 : 96 mots  →  descripteur au mot + 0x1C
            │                         bits 0-1 = classe, bit 2 = drapeau
            ▼
   services 0x04 (ajout/mise à jour) · 0x14 (compter + effacer) · 0x17 (lecture)
```

**Boucle de comptage, établie (l. 231394)** :

```
   pour les 96 entrées de 0xCAD0 :
        si bit 0 de l'entrée est posé  (= défaut PRÉSENT)
        alors lire [entrée + 0x1C], puis pour chaque bit haut à 1 :
                 incrémenter 0xC9F3 + n
   puis : 0xC9F3+n ≠ 0  ──►  poser le bit [word_1818 + n]
                             (word_1818 = 02 01 00 08 0F)
                             ──►  word_C548 bits 0,1,2  et  word_C54A bits 8,15
```

**Seuils réels du moniteur LDR** (`word_142A`, EA `0xE122C`) — et ils sont **parlant** une fois
les températures décodées :

| offset | valeur | lecture |
|---|---|---|
| `+0` | **3431** | **343,1 K = +70 °C** — seuil d'activation du moniteur |
| `+2` | 220 | 22 K d'incrément → borne **3651 = +92 °C** |
| `+4` | 100 | autorisation (≠ `0xFFFF`) |
| `+6` | 100 | 10 K — critère de durée |

**⇒ Le moniteur de température LDR s'active entre 70 °C et 92 °C : c'est le domaine du thermostat.
Un défaut n'est confirmé qu'à l'intérieur de cette fenêtre** — comportement exactement attendu d'un
diagnostic qui ne veut juger qu'à chaud.

---

### Boucle C — Surveillance à hystérésis et anti-rebond

```
   entrée commune  word_C5A8   (masse d'air par tour, mg ×10 ; axe 1300…11000)
            │
      ┌─────┴─────┐
      ▼           ▼
  courbe       courbe
  word_18AA    word_18AC        (les DEUX BORNES d'une fenêtre)
  borne basse  borne haute
      │           │
      └─────┬─────┘
            ▼
   comparé à  word_C596   (référence, avec valeur de repli word_CFF2)
            │
            ▼
   état courant dans  rl6 bit 1  /  byte_D6FC
            │
            ▼
   DÉCOMPTE  word_D6EE … word_D6FA   (7 compteurs)
            │   durée = [word_1474 + n]   (360, 60, 60, 325, 250 cycles)
            ▼
   à zéro ──► BASCULE de l'état  (orb / andb sur le bit)
   condition non tenue ──► compteur remis à 0  ⇒ il faut N cycles CONSÉCUTIFS
```

**⇒ Comparateur de Schmitt logiciel.** C'est un mécanisme **générique**, répliqué sept fois.

---

### Boucle D — Anti-falsification (et pourquoi il n'y a pas de checksum)

```
   valeur courante  word_C5B8   (PERSISTÉE en EEPROM)
            │
            ├──► historique 5 niveaux  C5D2, C5D4, C5D6, C5D8, C5DA
            │        (tourne à chaque mise à jour — l. 161143)
            │        PERSISTÉ en EEPROM  ⇒ survit à la coupure du contact
            │        │
            │        ▼
            │    moyenne  word_C5AE  (somme / 5, via sub_97DDC)
            │        ▼
            │    comparée à [word_18F2 + 0x14] = 120
            │
            └──► comparée à [word_18F2 + 0x38] = 2
                 comparée à [word_1474 + 0x06] = 325 ──► décompte word_D6FE ──► byte_C317
```

**Sept algorithmes de checksum ont été testés sans succès sur les 512 Ko.** La protection réelle est
cet **historique persistant** : on ne peut pas falsifier une valeur sans falsifier en même temps ses
cinq dernières valeurs et leur moyenne, ni sans franchir des seuils dont les valeurs sont dans le
**Datensatz** — donc hors de l'EEPROM.

---

### Boucle E — EEPROM : trois couches

```
   applicatif
      │
      ▼
   GESTIONNAIRE  0x94Axx … 0x94Cxx        redondance, rythme, options
      │  sub_94AE8  lecture avec consensus (vote à 3 copies)
      │  sub_94BB6  écriture triple
      │  sub_94BDC  gestionnaire (teste, décrémente, assainit)
      │  sub_94C6A  verrou à gâchette (mémorise le PREMIER code)
      ▼
   PILOTE  sub_A0002 (l. 149775)          handle = [2 bits page][14 bits offset]
      │  descripteur 12 octets @ 0x0BA6 ; table de 64 mots @ 0x0FE00
      │  adresse = 0xE5CE + offset
      ▼
   IMAGE  RAM  0xE5CE  (1 Ko)            13 groupes
```

**Confinement prouvé** : les **74 occurrences** de la constante `0xE5CE` sont **toutes** entre les
lignes **149820 et 152100**. Aucune fonction applicative ne calcule jamais une adresse EEPROM.

---

### Boucle F — Codage de variante : le Datensatz propose, le CAN choisit

```
   Lexia / Diagbox
        │  code le BSI
        ▼
   trame CAN ──► word_FD38 · word_FD38+1 · word_FD7A · word_FD7A+1 · word_FD7C
        │
        ▼
   [word_18B2 + 0x12]   masque de variante, bits 2 à 7
        │   bit 2 : inconditionnel
        │   bit 3 : armé par word_FD38
        │   bit 4 : armé par word_FD38+1
        │   bit 5 : armé par word_FD7A
        │   bit 6 : armé par word_FD7A+1
        │   bit 7 : armé par word_FD7C
        ▼
   groupe de quatre valeurs du Datensatz : +0x14, +0x16, +0x18, +0x1A
        │
        ▼
   word_D1BE · word_D1BA · word_D1B2 · word_C5A8     (+ byte_C308 = « chargées »)
```

**Et la moitié EEPROM** : quatre enregistrements à tag, à valeur unique **écrite en triple copie**,
sélectionnés par le masque `byte_F80D`, persistés par la commande `0x0B`.

**Limite** : le lien entre ces drapeaux et **le régulateur, la clim, BVM/BVA** n'est **pas** établi.
La correspondance « bit ↔ option » est dans la **couche absente**.

---

### Boucle G — Chaîne d'injection : ce qui est établi, et ce qui manque

**Statut honnête : la chaîne complète n'est PAS établie.** Voici les fragments qui le sont.

```
   [ÉTABLI]  couple demandé / limiteur
             cartes de couple : X = RÉGIME, résultat en mm³ × 100
             limiteur principal appliqué EN DERNIER
                    │
                    ▼
   [FRAGMENT] masse d'air par tour  word_C5A8  (130…1100 mg, axe mg ×10)
              et débit d'air  word_C3E6  (mg/s)
                    │
                    ▼
   [MANQUANT]  calcul de la masse de carburant (mm³ par tour)
               → conversion mm³ → durée d'injection
               → avance / pilotage des injecteurs
```

**Ce que l'on sait avec certitude :**
- les **cartes de couple** existent et sont **consommées** (leur non-consommation a été réfutée) ;
- leur **X est le régime** (`word_C42E`, 0…6000) et leur **résultat est en mm³ × 100** ;
- le **limiteur principal est appliqué en dernier** ;
- les grandeurs internes se lisent en `0…10000` = `0…100 %`.

**Ce que l'on ne sait pas** : la **conversion mm³ → temps d'ouverture des injecteurs**, l'**avance**,
et le **pilotage final**. Ces éléments sont dans la **couche absente** (bloc `0xFC000-0xFFFFF`, programme
autonome) — et **on ne les inventera pas**.
'''
