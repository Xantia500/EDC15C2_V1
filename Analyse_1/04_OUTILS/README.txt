OUTILS — scripts Python
=======================
ÉTAT DES OUTILS (à respecter)
  OK          parse.py, addr.py, addr2.py, edc15_analyze.py, patch_2nde_20kmh.py,
              ida_sweep_zones.py, genere_catalogue.py, scan_tags.py, consommateurs.py,
              usage_handles.py, lectures_calibration.py, tables_oubliees.py,
              interpolateurs_et_correcteurs.py, switchs_calibration.py, div_sites.py,
              nea2handle.py, annote_datensatz.py, analyse_switchs.py, msg_map.py,
              catalogue_extras.py
  ⚠️ fragile  ctx.py            (lève un TypeError selon le contexte Python)
  ❌ FAUX     dump_handles.py   (formule en MOTS au lieu d'OCTETS — voir errata E41)
  ❌ DANGER   segmente_blocs.py (a produit des artefacts — NE PAS RELANCER)

Rappels : appeler compile() de genere_catalogue.py avant tout patch.
Pièges : `%X format: an integer is required` et `bitwise_and` sur uint64 numpy => caster.
