#!/usr/bin/env python3
"""
Annotation automatique du Datensatz (EDC15C2 / PSA 2.2 4HX).

Principe (etape 50) : un enregistrement 1-D commence par
    [adresse de la variable d'entree][n][axe : n mots][valeurs : n mots]
soit une taille de 4 + 4n octets.

On confronte cette lecture a la taille reelle du bloc deduite de la table
des pointeurs (0xE1400), ce qui fournit une validation independante.

Sortie : annotation_datensatz.csv
"""
import struct, re, csv, sys

BIN = '/home/user/edc.bin'
TBL = 0x61400          # table des pointeurs (adresse 0xE1400)
BASE = 0x60000         # base fichier du Datensatz (adresse 0xE0000)
DBL = 0x70000          # Datensatz duplique (adresse 0xF0000)

d = open(BIN, 'rb').read()

# ---------------------------------------------------------------- pointeurs
vals = {}
for i in range(0, 0x61E30 - TBL, 2):
    vals[0x1400 + i] = struct.unpack_from('<H', d, TBL + i)[0]

uniq = sorted(set(vals.values()))
nxt = {}
for k, v in enumerate(uniq):
    nxt[v] = uniq[k + 1] if k + 1 < len(uniq) else None

inv = {}
for h, v in vals.items():
    inv.setdefault(v, []).append(h)

# ---------------------------------------------------------------- noms des variables
names = {}
for line in open('/home/user/clean.asm', encoding='latin-1'):
    m = re.match(r'^(byte|word)_([0-9A-F]{4,5}):\s+ds', line)
    if m:
        names[int(m.group(2), 16)] = m.group(1) + '_' + m.group(2)

def vname(addr):
    return names.get(addr, '')

RAM_LO, RAM_HI = 0x8000, 0xFFFE     # zone RAM plausible pour une adresse de variable

def w(ea, off):
    return struct.unpack_from('<H', d, BASE + (ea - 0xE0000) + off)[0]

def signed(x):
    return x - 0x10000 if x >= 0x8000 else x

def read_entry(ea, limit):
    """lit un enregistrement suppose 1-D ; retourne dict ou None"""
    w0 = w(ea, 0)
    n = w(ea, 2)
    if not (RAM_LO <= w0 <= RAM_HI):
        return None
    if not (2 <= n <= 128):
        return None
    size = 4 + 4 * n
    if limit is not None and size > limit:
        return None
    axis = [w(ea, 4 + 2 * k) for k in range(n)]
    vals_ = [w(ea, 4 + 2 * n + 2 * k) for k in range(n)]
    return dict(w0=w0, n=n, size=size, axis=axis, vals=vals_)

rows = []
stats = dict(total=0, ok=0, exact=0, short=0, nohead=0)

for h, v in sorted(vals.items()):
    ea = 0xE0000 + v
    lim = (nxt[v] - v) if nxt[v] is not None else None
    stats['total'] += 1
    e = read_entry(ea, lim)
    if not e:
        stats['nohead'] += 1
        rows.append([('%04X' % h), '0x%05X' % ea, lim if lim is not None else '', '', '', '', '', '', 'pas d en-tete 1-D'])
        continue
    stats['ok'] += 1
    verdict = ''
    if lim is not None:
        if e['size'] == lim:
            verdict = 'TAILLE EXACTE'
            stats['exact'] += 1
        elif e['size'] < lim:
            verdict = 'reste %d o' % (lim - e['size'])
            stats['short'] += 1
        else:
            verdict = 'deborde'
    ax = e['axis']
    mono = all(ax[i] <= ax[i + 1] for i in range(len(ax) - 1))
    rows.append([
        '%04X' % h, '0x%05X' % ea, lim if lim is not None else '',
        '0x%04X' % e['w0'], vname(e['w0']) or '?', e['n'], e['size'],
        '%d..%d' % (signed(ax[0]), signed(ax[-1])) + ('' if mono else ' NON MONOTONE'),
        verdict,
    ])

with open('/home/user/analyse_edc15c2_4hx/annotation_datensatz.csv', 'w', newline='') as f:
    wr = csv.writer(f)
    wr.writerow(['handle', 'EA', 'taille_bloc', 'variable', 'nom', 'n', '4+4n',
                 'axe min..max', 'verdict'])
    wr.writerows(rows)

print('handles total        :', stats['total'])
print('en-tete 1-D reconnu  :', stats['ok'])
print('  taille EXACTE      :', stats['exact'])
print('  taille < bloc      :', stats['short'])
print('pas d en-tete 1-D    :', stats['nohead'])
print()

# --- variables nommees les plus frequentes (les "tags" du Datensatz)
from collections import Counter
c = Counter(r[4] for r in rows if r[4] and r[4] != '?')
print('=== 25 variables les plus citees comme entree de courbe ===')
for nm, k in c.most_common(25):
    print('  %-12s %3d courbes' % (nm, k))

# ================================================================ 2-D
print()
print('=== tentative de decodage 2-D : [tagY][nY][axeY][tagX][nX][axeX][grille] ===')

def read_map2(ea, limit):
    ty = w(ea, 0)
    if not (RAM_LO <= ty <= RAM_HI): return None
    ny = w(ea, 2)
    if not (2 <= ny <= 64): return None
    p = 4 + 2 * ny
    tx = w(ea, p)
    if not (RAM_LO <= tx <= RAM_HI): return None
    nx = w(ea, p + 2)
    if not (2 <= nx <= 64): return None
    size = p + 4 + 2 * nx + 2 * ny * nx
    if limit is not None and size > limit: return None
    axY = [w(ea, 4 + 2 * k) for k in range(ny)]
    axX = [w(ea, p + 4 + 2 * k) for k in range(nx)]
    return dict(ty=ty, ny=ny, tx=tx, nx=nx, size=size, axY=axY, axX=axX)

m2 = dict(ok=0, exact=0, deb=0)
rows2 = []
for h, v in sorted(vals.items()):
    ea = 0xE0000 + v
    lim = (nxt[v] - v) if nxt[v] is not None else None
    e = read_map2(ea, lim)
    if not e: continue
    m2['ok'] += 1
    vd = ''
    if lim is not None:
        if e['size'] == lim: vd = 'TAILLE EXACTE'; m2['exact'] += 1
        elif e['size'] < lim: vd = 'reste %d' % (lim - e['size'])
        else: vd = 'deborde'; m2['deb'] += 1
    rows2.append(['%04X' % h, '0x%05X' % ea, lim, '0x%04X' % e['ty'], vname(e['ty']) or '?',
                  e['ny'], '0x%04X' % e['tx'], vname(e['tx']) or '?', e['nx'], e['size'],
                  '%d..%d' % (signed(e['axY'][0]), signed(e['axY'][-1])),
                  '%d..%d' % (signed(e['axX'][0]), signed(e['axX'][-1])), vd])
print('cartes 2-D reconnues :', m2['ok'], ' dont taille EXACTE :', m2['exact'], ' deborde :', m2['deb'])

with open('/home/user/analyse_edc15c2_4hx/annotation_cartes_2D.csv', 'w', newline='') as f:
    wr = csv.writer(f)
    wr.writerow(['handle','EA','taille_bloc','tagY','nomY','nY','tagX','nomX','nX','calc','axeY','axeX','verdict'])
    wr.writerows(rows2)

# ------------------------------------------------ plage d'axe par tag (1-D)
print()
print('=== plage d axe par variable (identification par les bornes) ===')
agg = {}
for r in rows:
    if r[3] and r[3] != '' and r[7]:
        try:
            lo, hi = r[7].split(' NON')[0].split('..')
            lo, hi = int(lo), int(hi)
        except Exception:
            continue
        a = agg.setdefault(r[4], [1e9, -1e9, 0])
        a[0] = min(a[0], lo); a[1] = max(a[1], hi); a[2] += 1
for nm, (lo, hi, k) in sorted(agg.items(), key=lambda x: -x[1][2])[:20]:
    print('  %-12s %3d courbes   axe global %6d .. %6d' % (nm, k, lo, hi))
