import struct, sys, subprocess

d = open('/home/user/edc.bin', 'rb').read()
T = 0x61400

def find(ea):
    """retourne les handles (word_xxxx) dont la valeur = ea - 0xE0000"""
    target = ea - 0xE0000
    out = []
    for i in range(0, 0x61E30 - T, 2):
        if struct.unpack_from('<H', d, T + i)[0] == target:
            out.append(0x1400 + i)
    return out

for arg in sys.argv[1:]:
    ea = int(arg, 16)
    hs = find(ea)
    print('EA 0x%05X -> offset 0x%04X -> handles: %s' % (
        ea, ea - 0xE0000, ', '.join('word_%04X' % h for h in hs) if hs else 'AUCUN'))
