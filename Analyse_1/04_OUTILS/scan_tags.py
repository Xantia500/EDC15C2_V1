import struct
from collections import Counter, defaultdict

d = open('/home/user/edc.bin', 'rb').read()
LO, HI = 0xE0000, 0xEC0000 - 0xE0000 * 0  # bornes EA
def u16(ea):
    return struct.unpack_from('<H', d, ea - 0x80000)[0]

maps = []
for ea in range(0xE0000, 0xEC000, 2):
    t = u16(ea)
    if not (0xC000 <= t <= 0xCFFF):
        continue
    n = u16(ea + 2)
    if not (2 <= n <= 64):
        continue
    if ea + 4 + 2 * n > 0xEC000:
        continue
    ax = [u16(ea + 4 + 2 * i) for i in range(n)]
    ok = all(ax[i] < ax[i + 1] for i in range(n - 1))
    if not ok:
        continue
    # 2-D ? tag X après l'axe Y
    xo = ea + 4 + 2 * n
    two_d = False
    if xo + 4 <= 0xEC000:
        tx = u16(xo); nx = u16(xo + 2)
        if 0xC000 <= tx <= 0xCFFF and 2 <= nx <= 64 and xo + 4 + 2 * nx <= 0xEC000:
            ax2 = [u16(xo + 4 + 2 * i) for i in range(nx)]
            if all(ax2[i] < ax2[i + 1] for i in range(nx - 1)):
                two_d = True
                maps.append((ea, t, n, tx, nx, ax, ax2))
    if not two_d:
        maps.append((ea, t, n, None, None, ax, None))

print('enregistrements avec tag valide : %d  (dont 2-D : %d)' % (len(maps), sum(1 for m in maps if m[3])))
tags = Counter()
for m in maps:
    tags[m[1]] += 1
    if m[3]:
        tags[m[3]] += 1
print('tags distincts :', len(tags))
print()
print('%-8s %-6s %s' % ('tag', 'nb', 'premier enregistrement / axe'))
for t, c in sorted(tags.items(), key=lambda x: -x[1]):
    ex = next(m for m in maps if m[1] == t or m[3] == t)
    if ex[1] == t:
        axs = ex[5]
    else:
        axs = ex[6]
    print('0x%04X  %-5d EA 0x%05X  n=%d  axe de %d a %d' % (t, c, ex[0], len(axs), axs[0], axs[-1]))
