DONNÉES — 54 CSV + compléments
==============================
Les trois à connaître :
  inventaire_cartes_2D_axes_v2.csv   86 cartes 2-D. EXACT À 100 % (double scan).
  registre_appels_interpolation.csv  385 appels. 385/385 lignes exactes, 0 écart d'EA.
  identifiants_vers_RAM.csv          identifiants de mesure -> variables RAM.

⚠️ Séparateur ';' mais 8 lignes du registre contiennent un ';' DANS un champ
   ("#64h ; 'd'"). Parser avec le module csv, jamais avec split(';').

Autres tables notables : cartographie_memoire, courbes_1D_datensatz, inventaire_fonctions,
taches_jeton_CC27, defauts_96_*, dtc_records_*, duplication_datensatz, usage_handles_*.
