#!/usr/bin/env python3
"""
patch_2nde_20kmh.py — autorise la 2nde et 20 km/h au régulateur de vitesse.

Cibles (bloc FGR `word_14B0`, présent DEUX fois dans le dump) :
  +0x00  vitesse minimale      2500 (25,00 km/h)  ->  2000 (20,00 km/h)
  +0x0A  ratio minimum          768               ->   380

Le bloc existe à EA 0xE2788 (fo 0x62788) et EA 0xF2788 (fo 0x72788) : les DEUX copies
sont patchées (piège des blocs dupliqués).

Sortie : edc_2nde_20kmh.bin + rapport sur stdout.
ATTENTION : checksums propriétaires NON recalculés (cf. Étape 105) -> binaire non flashable tel quel.
"""
import sys

SRC = "edc.bin"
DST = "edc_2nde_20kmh.bin"

# (offset fichier, adresse effective, libellé, ancienne, nouvelle)
PATCHES = []
for fo, ea in ((0x62788, 0xE2788), (0x72788, 0xF2788)):
    PATCHES.append((fo + 0x00, ea + 0x00, "vitesse mini (x0,01 km/h)", 2500, 2000))
    PATCHES.append((fo + 0x0A, ea + 0x0A, "ratio mini (V*256/N)", 768, 380))


def main():
    d = bytearray(open(SRC, "rb").read())
    print(f"source : {SRC} ({len(d)} octets)")
    ok = True
    for fo, ea, label, old, new in PATCHES:
        cur = d[fo] | (d[fo + 1] << 8)
        flag = "OK " if cur == old else "!! "
        if cur != old:
            ok = False
        print(f"{flag}EA 0x{ea:05X} (fo 0x{fo:05X})  {label:26s} "
              f"{cur:5d} -> {new:5d}   [{d[fo]:02X} {d[fo+1]:02X}] -> "
              f"[{new & 0xFF:02X} {new >> 8:02X}]")
        d[fo] = new & 0xFF
        d[fo + 1] = new >> 8
    if not ok:
        print("\nERREUR : une valeur d'origine ne correspond pas — abandon.")
        return 1
    open(DST, "wb").write(d)
    print(f"\nécrit : {DST}")
    print("checksums à recalculer : 0xE0FF6-9, 0xE0FFC-F, 0xE434D, 0xEBCFC-FF, 0xEBF1B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
