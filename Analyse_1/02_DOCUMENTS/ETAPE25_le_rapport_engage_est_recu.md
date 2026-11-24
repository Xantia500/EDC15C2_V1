# ÉTAPE 25 — Le rapport engagé est **reçu**, il n'est pas calculé

C'est la réponse à la question ouverte depuis longtemps. Elle bouscule l'hypothèse de départ
(« il faut la vitesse pour en déduire le rapport ») : **ce calculateur ne déduit rien**, il **lit
un rapport qu'on lui envoie**.

---

## 1. Le calcul, dans `sub_9B796` (l. 140975)

### Entrée : un garde d'initialisation

```asm
sub_9B796:
  movb  rl4, byte_C24F
  movb  byte_C8B3, rl4
  movbz r4, rl4
  cmp   r4, #0AAh            ; l.140981-140983
  jmpr  cc_Z, loc_9B7F8      ; 0xAA = "initialisé" → chemin normal
```

Chemin **non initialisé** (l. 140985-141005) : tout est remis à zéro et les valeurs de repli
viennent d'un **descripteur du Datensatz** :

```asm
mov  r4, word_1658
mov  r5, [r4+#4] ; mov word_C404, r5
movb rl5, [r4+#8] ; movb byte_C240, rl5     ; ← rapport par défaut
mov  r5, [r4+#6] ; mov word_C3FC, r5
```

### Chemin normal : le rapport est un **nibble**

```asm
loc_9B98A:
  movb  rl6, byte_C871
  movbz r6, rl6
  shr   r6, #4                 ; r6 = octet C871 >> 4
  cmpb  rl6, #0Fh              ; l.141199-141201
  jmpr  cc_NZ, loc_9B9A6
  mov   r4, word_1658
  movb  rl5, [r4+#8]           ; 0xF = inconnu → valeur par défaut
  movb  byte_C240, rl5         ; l.141203
  jmpr  cc_UC, loc_9B9AA
loc_9B9A6:
  movb  byte_C240, rl6         ; l.141208  ← byte_C240 = C871 >> 4
```

**`byte_C240` (le code de rapport 0…14) = le quartet supérieur de `byte_C871`.**
`0xF` signifie « rapport inconnu » et renvoie au défaut de calibration.

## 2. Qui écrit `byte_C871` ? Personne dans le listing

`byte_C871` n'a **qu'une seule occurrence** en lecture (l. 141196) et **aucune écriture** dans
`clean.asm`. Ce n'est pas un oubli : le bloc est rempli **par pointeur indirect**, juste avant
l'appel de `sub_9B796` (l. 143199-143209) :

```asm
mov   r4, #7
mov   [-r0], r4              ; argument empilé = 7
mov   r12, #9
mov   r13, #1
mov   r14, #1
mov   r15, #0C86Eh           ; ← destination du bloc
calls 9, sub_9D166
add   r0, #2
calls 9, sub_9B796           ; ← puis on décode le rapport
```

Le bloc de **7 octets** va de `C86E` à `C874`, et `C871` en est le **4ᵉ octet**.

## 3. `sub_9D166` = lecture d'un message (l. 143979)

```asm
movb  rl7, [r0+#0Ch]         ; argument empilé
subb  rl7, #1                ; slot = argument − 1
movbz r4, rl7
shl   r4, #4                 ; ×16
add   r4, #0EF11h            ; l.144000  → descripteur = 0xEF11 + 16×(slot−1)
mov   r9, r4
mov   r4, r9
add   r4, #6                 ; → champ pointeur de données
movb  rl4, [r9]              ; octet d'état du message
mov   word_CF84, r4
and   r5, #3
cmpb  rl5, #2                ; état & 3 == 2 → message frais
jmpr  cc_NZ, loc_9D214       ; sinon on abandonne
...
movb  rl4, #0FDh
movb  [r9], rl4              ; l.144033-144034 : message marqué consommé
```

⇒ **`sub_9D166` lit un message reçu dans un créneau, copie sa charge utile vers la destination
demandée, puis marque le créneau consommé (`0xFD`).** Aucune écriture du producteur n'est dans ce
code : le producteur est **hors du calculateur**.

## 4. Le gestionnaire de messages : 16 créneaux de 16 octets

Initialisation dans `sub_99838` (l. 135639-135700) :

```asm
mov r4, #41h
mov r5, #0EF00h ; mov [r5], r4        ; créneau 0 = configuration
mov r4, #5555h
mov r5, #0EF10h ; mov [r5], r4        ; … puis 0xEF20, 0xEF30, … 0xEFF0
```

puis le **créneau 0** est rempli depuis le Datensatz (`word_1456`, champs +2/+4/+6/+8/+0A →
`0xEF06/08/0A/0C/0E`). Donc : **`0xEF00-0xEFFF` = 16 créneaux × 16 octets**, en mémoire externe,
et **le créneau 0 est paramétré par la calibration**.

## 5. La carte des messages (sites vérifiés)

| l. appel | `r12` | `r13` | `r14` | argument empilé | destination | longueur |
|---|---|---|---|---|---|---|
| 143208 | 9 | 1 | 1 | 7 | **`0xC86E`** | **7** ← rapport de boîte |
| 143719 | 10 | 5 | 0 | 3 | `0xC7E8` | 3 |
| 143142 | 11 | 2 | 1 | 8 | `0xC87D` | 8 |
| 143315 / 143330 / 143395 / 143481 / 143583 | 12 | 3 | 1 | 5 | `0xC811` | 5 |
| 143363 / 143452 / 143552 | 13 | 6 | 0 | 6 | `0xC816` | 5 |
| 143226 / 143238 | 14 | 4 | 1 | 4 | `0xC825` | 5 |
| 143732 | 8 | 7 | 0 | 6 | `0xC82B` | 6 |

*(14 sites dans le listing ; les paramètres `r12/r13/r14` restent non nommés.)*

## 6. Contenu du message n° 9 (7 octets)

| octet | usage lu | ligne |
|---|---|---|
| `C86E` | bit 4 testé (`& 0x10`) | 141006 |
| `C86F` | comparé à `0xFF` | 141022 |
| `C870` | **champ d'état** : bit0→`C28C`, bit1→`C290`, bits2-3→`C244` (`0x80`/`0x81`), bit4→`C28F`, bit7→`C241` | 141139-141190 |
| `C871` | **quartet haut = rapport**, `0xF` = inconnu | 141196-141208 |
| `C872` | comparé à `0xFF` → défaut, sinon repli `[word_1658+6]` | 141211-141235 |
| `C873` | non lu | — |
| `C874` | comparé (xor) à `C872` | 141213-141228 |

**La vitesse n'est pas dans ce message.** On y trouve un rapport, un état de boîte et deux valeurs
non identifiées.

## 7. Conséquences — et ce que cela corrige

1. **Le rapport est transmis, pas calculé.** Les courbes de couple par rapport sont donc sélectionnées
   par un **nibble reçu**, et non par un quotient vitesse/régime. L'hypothèse « la vitesse doit
   exister en amont du rapport » **ne s'applique pas à ce calculateur** : il n'a pas besoin de la
   vitesse pour connaître le rapport.
2. **La vitesse reste à trouver**, mais ailleurs : la voie filaire déjà identifiée (impulsions sur
   `CC1_CC15`, accumulateur `word_FC04`) reste la seule piste ouverte.
3. **Le repli est calibré** : si le message est absent ou invalide (`0xF`, `0xFF`), le calculateur
   utilise `[word_1658+8]` (rapport), `[+4]` (`word_C404`), `[+6]` (`word_C3FC`). Un véhicule dont
   la boîte ne parle pas garde donc un comportement par défaut, cohérent et non bloquant.

## 8. Lu / inféré — et réserves

| affirmation | statut |
|---|---|
| `byte_C240 = byte_C871 >> 4`, `0xF` → défaut `[word_1658+8]` | **lu** (l. 141196-141208) |
| 16 créneaux de 16 octets à `0xEF00`, init `0x5555`, créneau 0 par `word_1456` | **lu** (l. 135639-135700) |
| `sub_9D166` : slot = arg−1, `0xEF11+16×(slot−1)`, état `&3==2`, consommation `0xFD` | **lu** (l. 143994-144034) |
| le bloc `0xC86E` est le message n° 9, 7 octets | **lu** (l. 143203-143208) |
| **le rapport vient de l'extérieur du calculateur** | **inféré** — solide (producteur absent du code), mais non prouvé |
| **le support physique** (CAN, K-line, autre) | **inconnu** — aucun SFR CAN trouvé ; le gestionnaire est en mémoire externe, donc **logiciel** ; je ne tranche pas |
| `byte_C2B7 & 1` = bit de codage qui autorise la lecture du message | **inféré** (l. 143200-143207 : le test précède l'appel) |
| signification de `C872` / `C874` / `C86F` | **inconnue** |

## 9. Suite

- `word_1658` : lire le descripteur complet (il contient le rapport par défaut et deux valeurs) —
  6 octets, à l'adresse que donnera le handle.
- `byte_C2B7` : cartographier les autres bits de codage (déjà vus : `&1` = boîte, `&6` = variante,
  `&8`, `&10`).
- Puis reprendre la **vitesse** par la voie filaire, seul chemin encore ouvert.
