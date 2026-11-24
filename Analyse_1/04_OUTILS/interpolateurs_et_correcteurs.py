#!/usr/bin/env python3
"""
ETAPE 59 — L'etage d'interpolation et la chasse aux correcteurs.

Deux etages identifies :

    unk_1D36 (r12 = handle de courbe, r13 = x)        -> interpolation 1-D
    unk_1D50 (r12 = handle de carte,  r13 = x, r14=y) -> interpolation 2-D

Les CORPS de ces deux routines sont dans la couche absente (0xFC000-0xFFFFF) :
le code visible ne fait que les APPELer. Mais les sites d'appel et leurs
ARGUMENTS sont lisibles. On peut donc etablir, sans connaitre l'interpolateur :

    quelle courbe est interpolee, contre quelle grandeur, dans quelle fonction

Et chercher les correcteurs : une fonction qui appelle un interpolateur ET qui
accumule dans un mot RAM (lu puis reecrit) est un candidat integrateur.

Sorties : interpolations.csv, candidats_correcteurs.csv
"""
import re, csv, collections

ASM = '/home/user/clean.asm'
OUT = '/home/user/analyse_edc15c2_4hx'

RE_SUB = re.compile(r'^(sub_[0-9A-F]+):')
RE_CALL = re.compile(r'^\s*calls\s+0,\s*(unk_1D[0-9A-F]+)\b')
RE_MOV_ARG = re.compile(r'^\s*mov\s+r(\d+),\s*(word_[0-9A-F]{4}|r\d+|#?[0-9A-F]+h?)')
RE_MOVL = re.compile(r'^\s*mov\s+(word_[0-9A-F]{4}),\s*r(\d+)')
RE_MOVR = re.compile(r'^\s*mov\s+r(\d+),\s*(word_[0-9A-F]{4})')


def main():
    lines = open(ASM, encoding='latin-1').read().split('\n')
    func = '(hors fonction)'
    calls = []                       # sites d'appel des interpolateurs
    acc = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    # acc[fonction][word] = [nb lectures, nb ecritures]
    for i, ln in enumerate(lines):
        m = RE_SUB.match(ln)
        if m:
            func = m.group(1)
            continue
        m = RE_MOVR.match(ln)
        if m:
            acc[func][m.group(2)][0] += 1
            continue
        m = RE_MOVL.match(ln)
        if m:
            acc[func][m.group(1)][1] += 1
            continue
        m = RE_CALL.match(ln)
        if m:
            # remonter les 6 lignes precedentes pour lire les arguments
            args = {}
            for j in range(max(0, i - 6), i):
                a = RE_MOV_ARG.match(lines[j])
                if a:
                    args[int(a.group(1))] = a.group(2)
            calls.append(dict(ligne=i + 1, fonction=func, routine=m.group(1),
                              r12=args.get(12, ''), r13=args.get(13, ''), r14=args.get(14, '')))

    print('sites d appel d interpolateur : %d' % len(calls))
    print('  par routine :', dict(collections.Counter(c['routine'] for c in calls)))

    # ---- resolution handle -> EA -> type de structure
    import struct
    d = open('/home/user/edc.bin', 'rb').read()
    def ptr(h):
        return 0xE0000 + struct.unpack_from('<H', d, 0x61400 + h - 0x1400)[0]
    def kind(ea):
        try:
            w0, n = struct.unpack_from('<2H', d, 0x60000 + ea - 0xE0000)
        except Exception:
            return '?'
        if 0xE0000 <= ea <= 0xEC000:
            return 'structure Datensatz'
        return '?'

    rows = []
    for c in calls:
        h = c['r12']
        ea = ''
        if h.startswith('word_'):
            hv = int(h[5:], 16)
            if 0x1400 <= hv <= 0x1E30:
                ea = '0x%05X' % ptr(hv)
        rows.append(dict(ligne=c['ligne'], fonction=c['fonction'], routine=c['routine'],
                         courbe=c['r12'], EA=ea, x=c['r13'], y=c['r14']))
    with open(OUT + '/interpolations.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['ligne', 'fonction', 'routine', 'courbe', 'EA',
                                          'x', 'y'], delimiter=';')
        w.writeheader(); w.writerows(rows)

    # ---- courbes reellement interpolees, et contre quoi
    par_courbe = collections.defaultdict(set)
    for r in rows:
        if r['courbe']:
            par_courbe[r['courbe']].add(r['x'])
    print('\ncourbes distinctes interpolees : %d' % len(par_courbe))
    print('  entrees x distinctes :', dict(collections.Counter(
        x for s in par_courbe.values() for x in s).most_common(10)))

    # ---- candidats correcteurs : interpolateur + accumulateur
    callers = collections.Counter(r['fonction'] for r in rows)
    cand = []
    for f, n in callers.items():
        for w_, (rd, wr) in acc.get(f, {}).items():
            if rd >= 1 and wr >= 1:
                cand.append(dict(fonction=f, appels=n, mot=w_, lectures=rd, ecritures=wr))
    cand.sort(key=lambda r: (-r['appels'], -r['lectures']))
    with open(OUT + '/candidats_correcteurs.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['fonction', 'appels', 'mot', 'lectures',
                                          'ecritures'], delimiter=';')
        w.writeheader(); w.writerows(cand)
    print('\n=== candidats correcteurs (interpolateur + mot accumule) : %d ===' % len(cand))
    for r in cand[:20]:
        print('  %-14s %2d appels  %s  %dx lu / %dx ecrit'
              % (r['fonction'], r['appels'], r['mot'], r['lectures'], r['ecritures']))


if __name__ == '__main__':
    main()
