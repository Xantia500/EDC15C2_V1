# ÉTAPE 32 — Confrontation du matériau externe au binaire : ce qui tient, ce qui tombe

Méthode : je traite ton dossier comme une **liste d'hypothèses**, et chaque point est confronté à ce
que le binaire montre. Trois catégories : **confirmé**, **contredit / non soutenu**, **invérifiable
ici**. Et une **rétractation** qui me concerne, au §5.

---

## 1. Ce que le binaire CONFIRME (et qui est fort)

### 1.1 La famille : EDC15**C2** ✔

Chaîne ASCII dans le code : **`TSW V2.31 071099 1217 C2/ESB/G40`** — `EA 0x88000`
(et `…C2/E` à `EA 0x8FFE0`). Le « C2 » est **écrit dans le binaire**.

### 1.2 La taille de la flash : 512 Ko = AM29F400 ✔

`edc.bin` = **524 288 octets**. L'AM29F400 est une 4 Mbit = 512 Ko. ✔

### 1.3 Les références HW/SW sont présentes — et l'une est **celle de ton tableau** ★

| EA | contenu ASCII |
|---|---|
| **`0xFCC00`** | **`0281010877`** |
| `0xFBFB0` | **`1037353776`** |
| `0xFFEF0` | **`1037353776`** |
| `0xFCC20` | `B075WF2S01` |

Soit : **HW 0 281 010 877**, **SW 1037 353 776**. Or ton dossier cite précisément
« 0 281 010 877 = 3 prises, multiplexé VAN/CAN, 2.2 HDi 136 ». **Si ce tableau est juste, ce
calculateur est la version 3 prises multiplexée.** C'est une identification de matériel, pas une
déduction : la référence est lue dans le binaire, seule son *interprétation* vient du dossier.

### 1.4 Le checksum par complément à deux sur des mots ✔ ★

Le dossier dit : « checksum 16 bits par complément à 2 (0x0000 − somme des mots 16 bits du bloc) ».
C'est **exactement** ce que fait le binaire (l. 151510-151537) :

```asm
add word_D6C6, r4      ; somme des mots du bloc
...
mov r4, word_D6C6
neg r4                 ; ← 0x0000 − somme
mov [r2], r4
```

**Concordance parfaite.** C'est le point où le dossier et le binaire se rejoignent le plus
précisément.

### 1.5 « L'EEPROM porte le codage ; au démarrage le C167 choisit le codeblock » ✔

Confirmé par la chaîne trouvée à l'étape 29 : `0xE5CE + word_BCA` → `sub_BD464` décode **15 octets**
→ pose les bits de `byte_C2B7`, et ces bits **sélectionnent réellement des variantes** (ex.
`byte_C2B7 & 1` décide si le message de rapport de boîte est lu — étape 25).

### 1.6 Une image RAM de l'EEPROM ✔

Confirmé : `0xE5CE`, remplie champ par champ, relue, protégée par checksum (étapes 29-31).

### 1.7 Un kilométrage interne indépendant du tableau de bord ✔

Confirmé : `word_C83A:C83C` (32 bits) + `word_C838` (accumulateur), sauvegardé dans l'image,
converti en km par division par 2000, et utilisé en **différence depuis un événement**.

---

## 2. Ce que le binaire CONTREDIT ou ne soutient pas

### 2.1 La localisation de l'image : `0x380000` ✘

Le dossier dit « XRAM autour de 0x380000 ». Le binaire écrit à **`0xE5CE`** (`mov r4, #0E5CEh`,
`mov DPP3, #3`, l. 96443). **Contredit.**

### 2.2 La formule « 0xFFFF − somme − n° de page » ✘

Le binaire utilise **deux** algorithmes, et aucun n'est celui-là :

| zone | algorithme réel | preuve |
|---|---|---|
| bloc principal | **somme de mots 16 bits**, puis **`neg`** (complément à 2) | l. 151510-151537 |
| zone secondaire | **somme de quartets** des octets, résultat **`& 0x0F`** | l. 151196-151222 (`addb` / `shr #4` / `and #0Fh`) |

Pas de `0xFFFF`, pas de soustraction d'index de page. **Non soutenu.**

### 2.3 Les « pages de 16 octets, checksum sur les 2 derniers » ✘

Ce que le binaire montre :

- des **enregistrements de 12 octets** dans l'image (`+0 … +A`) ;
- un **bloc de codage de 15 octets** (12 décodés) ;
- un bloc principal délimité **par deux variables** (`word_D6E` début, `word_D70` longueur) et non
  par une taille fixe.

**La structure 16 octets n'apparaît nulle part.**

### 2.4 Le dossier contient une **incohérence interne** ★

Il affirme que la page miroir est « recopiée **à l'identique** » et montre les deux lignes finissant
**`34 FF`** — puis calcule pour le miroir `0xFFFF − 0xC9 − 4 = 0xFF32`, soit **`32 FF`**. 

Or **les deux ne peuvent pas être vrais en même temps** : si le numéro de page entre dans le
checksum, deux lignes de données identiques situées à deux pages différentes ont forcément des
checksums **différents**. L'exemple affiché (« identique ») est donc incompatible avec la formule
donnée. *(Le calcul arithmétique de l'exemple est juste ; c'est la coexistence des deux énoncés qui
est impossible.)*

### 2.5 Le facteur du kilométrage : « ×10 ou ÷100 » ✘

Le binaire divise par **2000** (`0x7D0`), donc **1 unité = 0,5 m**, avec un accumulateur 16 bits
modulo `0x55D5`. Ni ×10, ni ÷100. **Non soutenu.**

### 2.6 « SPI avec 95P08 » — ni confirmé, ni réfuté

- **Aucun SFR SSC** dans le désassemblage (le C167 en a un : `SSCCON`, `STB`, `SRB`) ;
- **aucun bit-bang** (`bset/bclr` sur un port : zéro occurrence).

Donc l'interface n'est **pas visible** dans le code fourni. Elle peut être dans la couche absente —
mais je ne peux pas dire « SPI », et le dossier ne peut pas non plus le prouver par ce binaire.
*(À noter : les `#400h` du code sont des **masques de bit 10**, pas des longueurs de copie de 1024 —
j'ai vérifié, ils apparaissent en `or`/`xor`/`and`.)*

---

## 3. Ce qui est **invérifiable** avec ce que nous avons

| affirmation du dossier | pourquoi invérifiable ici |
|---|---|
| PIN en ASCII aux offsets 0x0110-0x0190 | ces offsets sont dans l'EEPROM, non fournie |
| octet d'état immo (01 verrouillé / 00 vierge) | idem |
| VIN `VF3…` sur 17 octets | idem (et **aucune** chaîne `VF3` dans la flash — normal) |
| classes d'injecteurs (01/02/03) | idem |
| zone DTC `0x0350-0x03FF` | idem |
| protection d'écriture 0x0300-0x03FF du 95P08 | relève de la puce, pas du firmware |

**Conclusion honnête** : tout le *milieu* du dossier (zones, adresses, formats PIN) porte sur un
objet que nous n'avons pas. Sur ce point, ni toi ni moi ne pouvons trancher **avec ce fichier**.

---

## 4. Ce que le dossier apporte **utilement** pour la suite

1. **Le bloc de 10 octets** copié depuis `0xC895` (étape 30) : le dossier décrit un PIN de
   4 ASCII + 4 compléments à 0xFF (8 octets). Avec **un octet d'état et son complément**, on tombe
   sur **10**. C'est **compatible**, pas démontré — mais c'est la première piste sérieuse pour
   identifier ce bloc. **À tester** : lire `0xC895`-`0xC89F` en exécution et vérifier si les octets
   4-7 sont le complément à `0xFF` des octets 0-3.
2. **Le principe de miroir** : notre inventaire montre 13 groupes ; savoir lesquels sont des copies
   est une question ouverte. Le seul indice structurel est la « zone secondaire » à checksum de
   quartets (`word_BBE` / `word_BC0`) — **à comparer** avec le bloc principal.
3. **Le défaut P0601 / checksum** : le dossier cite ce code. Notre binaire a bien deux vérifications
   d'intégrité ; identifier laquelle lève quel défaut est une piste concrète.

---

## 5. Rétractation — une de mes affirmations de l'étape 30 est fausse

J'avais écrit : « aucun offset ne dépasse **561**, donc le miroir RAM est partiel ». **C'est faux**,
et voici pourquoi :

- `0xE5CE + offset` avec `offset > 0x231` donne une adresse `> 0xE7FF` : elle **sort de la RAM
  interne** et, par le mécanisme de page du C166, tombe dans la zone suivante — parfaitement
  adressable. Rien n'interdit donc un offset jusqu'à **1023**, conformément à ta taille de 1 Ko.

⇒ **Je retire la borne « 562 octets » et la conclusion « miroir partiel ».** La taille de l'image
reste **inconnue** ; seul un relevé des variables d'offset la donnera.

---

## 6. Bilan en trois lignes

- **Le dossier a raison** sur : la famille C2, la flash 512 Ko, la référence **0281010877** (qu'il
  identifie comme 3 prises), le checksum en complément à 2 sur mots, le codage en EEPROM → variante,
  l'image RAM, le km interne.
- **Le dossier a tort ou n'est pas soutenu** sur : `0x380000`, la formule `0xFFFF − somme − page`,
  les pages de 16 octets, le facteur du km.
- **Et il contient au moins une incohérence interne** (miroir identique **et** checksum dépendant de
  la page).

## 7. Prochaines actions

1. **Test `0xC895`** : structure PIN (4 + 4 compléments) — le seul test qui valide ou casse la piste
   immo **avec ce que nous avons**.
2. **Comparer** les deux zones à checksum (bloc principal vs zone à quartets) → confirmer ou écarter
   le mécanisme de miroir.
3. **Chercher la table des DTC** dans la calibration par **structure** (suites de codes), puisque le
   dossier situe les DTC dans une zone que nous ne pouvons pas lire.
