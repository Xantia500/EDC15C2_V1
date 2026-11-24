SOURCES — source de vérité du projet
====================================
edc.bin          le binaire (524 288 o). NE JAMAIS MODIFIER EN PLACE.
clean.asm        désassemblage IDA nettoyé (412 022 lignes). Référence pour
                 toute citation de code : citer le label + l'EA, la ligne en secours.
edc.asm          désassemblage IDA d'origine, non nettoyé (conservé pour comparaison).
recon.bin        reconstruction intermédiaire produite par l'outillage.
recon_partielle.bin  idem, partielle.
edc_2nde_20kmh.bin   LE SEUL PATCH PRODUIT (8 octets) : 2e + régulation dès 20 km/h.
                 ATTENTION : checksums non recalculés => non flashable en l'état.

Vérifier les empreintes contre ../MANIFESTE_SHA256.txt avant de commencer.
Si edc.bin ou clean.asm diffèrent, tout le dossier perd sa valeur.
