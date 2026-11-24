#!/usr/bin/env python3
"""
ETAPE 61 — Trier les switchs, et dire CE QUE CHAQUE BLOC SHUNTE CONTIENT.

Avertissement pris en compte : tous les octets lus en calibration ne sont pas des
switchs. Certains sont des DONNEES (coefficients 8 bits, gains, index).

Trois classes, decidees par ce qui SUIT immediatement la lecture :

  SWITCH      movb rlX, [rN+#k]  puis  jmpa/jmpr cc_XX, loc     (0 ou 1 ligne d'ecart)
              -> l'octet commande un saut                     = un INTERRUPTEUR
  MODE        movb rlX, [rN+#k]  puis  cmpb rlX, #v  puis saut
              -> l'octet choisit parmi N strategies           = un SELECTEUR
  DONNEE      movb rlX, [rN+#k]  puis  movbz/and/add/mul ...
              -> l'octet est une VALEUR, pas un interrupteur   = une DONNEE

Pour chaque SWITCH et MODE, on analyse ensuite le BLOC SHUNTE : combien
d'interpolations il contient, QUELS handles il appelle, et quels mots RAM il ecrit.
C'est cela qui dit ce que le switch fait.

Sorties : switchs_classes.csv, switchs_contenu.csv
"""
import re, csv, collections, struct

ASM = '/home/user/clean.asm'
BIN = '/home/user/edc.bin'
OUT = '/home/user/analyse_edc15c2_4hx'

RE_SUB = re.compile(r'^(sub_[0-9A-F]+):')
RE_LABEL = re.compile(r'^(loc_[0-9A-F]+):')
RE_HANDLE = re.compile(r'^\s*mov\s+r(\d+),\s*word_(1[0-9A-F]{3})\b')
RE_BYTE = re.compile(r'^\s*movb\s+(rl\d+),\s*\[\s*r(\d+)\s*(?:\+\s*#([0-9A-F]+)h)?\s*\]')
RE_JMP = re.compile(r'^\s*(jmpa|j[a-z]+)\s+(?:cc_([A-Z]{1,3}),\s*)?(loc_[0-9A-F]+)')
RE_CMP = re.compile(r'^\s*cmpb?\s+(rl\d+),\s*#([0-9A-F]+)h')
RE_INT = re.compile(r'^\s*calls\s+0,\s*(unk_1D[0-9A-F]+|word_1D[0-9A-F]+)')
RE_ARG = re.compile(r'^\s*mov\s+r(\d+),\s*(word_[0-9A-F]{4}|r\d+|#?[0-9A-F]+h?)')
RE_WR = re.compile(r'^\s*mov\s+(word_[0-9A-F]{4}),\s*')
RE_ARITH = re.compile(r'^\s*(movbz|and|or|xor|add|sub|mul\w*|div\w*|cmp|shl\w*|shr\w*|ashr|exts|extu)\b')

d = open(BIN, 'rb').read()
PTR = {0x1400 + i: struct.unpack_from('<H', d, 0x61400 + i)[0]
       for i in range(0, 0x61E30 - 0x61400, 2)}


TA = {0xC42E: 'régime', 0xC3E6: 'air mgx10', 0xC6A2: 'charge%', 0xC3D2: 'T LDR',
      0xC3BA: 'T air', 0xC3B0: 'T carb', 0xC5A8: 'masse air/tour', 0xC3C2: 'RCO',
      0xC596: 'réf'}


def label(ea):
    """etiquette lisible d'une structure de calibration"""
    s = struct_axes(ea)
    if not s:
        return '?'
    w0, n, tx, nx = s
    if tx:
        return '%s(%d)x%s(%d)' % (TA.get(w0, '%04X' % w0), n, TA.get(tx, '%04X' % tx), nx)
    return '%s n=%d' % (TA.get(w0, '%04X' % w0), n)


def struct_axes(ea):
    """renvoie (tagY, nY, tagX, nX) si ea est une carte 2-D, sinon (tag, n, None, 0)"""
    o = 0x60000 + ea - 0xE0000
    try:
        w0, n = struct.unpack_from('<2H', d, o)
    except Exception:
        return None
    if not (2 <= n <= 48):
        return (w0, 0, None, 0)
    oy = o + 4 + 2 * n
    try:
        tx, nx = struct.unpack_from('<2H', d, oy)
    except Exception:
        return (w0, n, None, 0)
    if 2 <= nx <= 48 and 0xC000 <= tx <= 0xDFFF:
        return (w0, n, tx, nx)
    return (w0, n, None, 0)


def main():
    lines = open(ASM, encoding='latin-1').read().split('\n')
    labels = {}
    for i, ln in enumerate(lines):
        m = RE_LABEL.match(ln)
        if m and m.group(1) not in labels:
            labels[m.group(1)] = i

    func, rows = '?', []
    for i, ln in enumerate(lines):
        if '; End of function' in ln:
            func = '(code non nomme)'
            continue
        m = RE_SUB.match(ln)
        if m:
            func = m.group(1)
            continue
        m = RE_HANDLE.match(ln)
        if not m:
            continue
        reg, h = m.group(1), int(m.group(2), 16)
        if not (0x1400 <= h <= 0x1E30):
            continue
        for j in range(i + 1, min(i + 3, len(lines))):
            b = RE_BYTE.match(lines[j])
            if not b or b.group(2) != reg:
                continue
            breg = b.group(1)
            off = int(b.group(3), 16) if b.group(3) else 0
            ea = 0xE0000 + PTR[h]
            vo = 0x60000 + ea - 0xE0000 + off
            val = d[vo] if 0 <= vo < len(d) else None

            # ---- ce qui suit, strictement adjacent
            k = j + 1
            kind, cond, tgt, cmps = None, '', None, []
            if k < len(lines):
                c = RE_CMP.match(lines[k])
                if c and c.group(1) == breg:
                    cmps.append(int(c.group(2), 16))
                    k2 = k + 1
                    while k2 < len(lines) and k2 <= k + 3:
                        s = RE_JMP.match(lines[k2])
                        if s:
                            tgt = labels.get(s.group(3))
                            kind, cond = 'MODE', s.group(2) or ''
                            break
                        if RE_CMP.match(lines[k2]):
                            cmps.append(int(RE_CMP.match(lines[k2]).group(2), 16))
                        k2 += 1
                else:
                    s = RE_JMP.match(lines[k])
                    if s:
                        tgt = labels.get(s.group(3))
                        kind, cond = 'SWITCH', s.group(2) or ''
                    elif RE_ARITH.match(lines[k]) or re.match(r'^\s*movbz', lines[k]):
                        kind = 'DONNEE'
            if kind is None:
                continue

            dec = 0
            if tgt is not None:
                dec = tgt - k

            # ---- contenu du bloc shunte
            info = dict(taille_bloc=dec, interpolations=0, calibres='', axes='', ecritures='')
            if tgt is not None and dec > 0:
                blk = lines[k + 1:tgt]
                ints, cal, ax, wr = 0, [], [], collections.Counter()
                for q, bl in enumerate(blk):
                    mi = RE_INT.match(bl)
                    if mi:
                        ints += 1
                        # handle passe en r12 dans les 5 lignes precedentes
                        for p in range(max(0, q - 5), q):
                            a = RE_ARG.match(blk[p])
                            if a and a.group(1) == '12' and a.group(2).startswith('word_'):
                                hh = int(a.group(2)[5:], 16)
                                if 0x1400 <= hh <= 0x1E30:
                                    cal.append('%04X' % hh)
                                    ax.append(label(0xE0000 + PTR[hh]))
                                break
                    mw = RE_WR.match(bl)
                    if mw:
                        wr[mw.group(1)] += 1
                info.update(interpolations=ints, calibres=','.join(cal[:8]),
                            axes=','.join(sorted(set(ax))[:6]),
                            ecritures=','.join('%s(%d)' % (w, n) for w, n in wr.most_common(3)))
            rows.append(dict(fonction=func, ligne=i + 1, handle='0x%04X' % h,
                             structure='0x%05X' % ea, offset=off,
                             valeur='0x%02X' % val if val is not None else '?',
                             classe=kind, condition=cond,
                             cmp='' if not cmps else '/'.join(str(c) for c in cmps),
                             **info))
            break

    for name, flds in (('switchs_classes.csv', ['fonction', 'ligne', 'handle', 'structure',
                                                'offset', 'valeur', 'classe', 'condition']),
                       ('switchs_contenu.csv', ['fonction', 'ligne', 'structure', 'offset',
                                                'valeur', 'classe', 'condition', 'taille_bloc',
                                                'interpolations', 'calibres', 'axes', 'ecritures'])):
        with open(OUT + '/' + name, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=flds, delimiter=';', extrasaction='ignore')
            w.writeheader(); w.writerows(rows)

    print('sites lus en OCTET dans la calibration : %d' % len(rows))
    print('  classes :', dict(collections.Counter(r['classe'] for r in rows)))
    sw = [r for r in rows if r['classe'] in ('SWITCH', 'MODE')]
    print('\n=== SWITCHS + MODES : %d ===' % len(sw))
    print('\nles 18 plus gros blocs shuntees, avec leur CONTENU :')
    print('  %-12s %-8s %-4s %-4s %-5s %-3s %-3s %s'
          % ('fonction', 'struct', '+off', 'val', 'bloc', 'int', 'e', 'axes/calibres'))
    for r in sorted(sw, key=lambda x: -x['taille_bloc'])[:18]:
        print('  %-12s %-8s %-4s %-4s %-5d %-3d %-3d %s'
              % (r['fonction'], r['structure'], r['offset'], r['valeur'],
                 r['taille_bloc'], r['interpolations'], r['taille_bloc'],
                 (r['axes'] or '-')[:46]))


if __name__ == '__main__':
    main()
