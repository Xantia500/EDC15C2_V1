#!/usr/bin/env python3
"""
ETAPE 60 — Les SWITCHS de calibration : tableau des options.

Forme exacte relevee dans le code :

    mov   r5, word_141E        ; handle de calibration  -> structure EA 0xE1148
    movb  rl4, [r5+#0Dh]       ; OCTET d'option, offset 13
    jmpa  cc_NZ, loc_A4916     ; si NON NUL -> saute 864 lignes entieres

Trois traits simultanes, donc pas d'ambiguite :
  - un handle de calibration est charge ;
  - un OCTET (et non un mot) est lu dans la structure ;
  - un saut LONG (jmpa) ou un saut conditionnel franc suit immediatement.

Le script releve, pour chaque site : la structure, l'offset, la VALEUR EFFECTIVE
dans ce firmware, la POLARITE (cc_NZ = actif si non nul, cc_Z = actif si nul)
et la TAILLE du bloc shunte.

Sorties : switchs_calibration.csv, options_par_structure.csv
"""
import re, csv, collections, struct

ASM = '/home/user/clean.asm'
BIN = '/home/user/edc.bin'
OUT = '/home/user/analyse_edc15c2_4hx'

RE_SUB = re.compile(r'^(sub_[0-9A-F]+):')
RE_LABEL = re.compile(r'^(loc_[0-9A-F]+):')
RE_HANDLE = re.compile(r'^\s*mov\s+r(\d+),\s*word_(1[0-9A-F]{3})\b')
RE_BYTE = re.compile(r'^\s*movb\s+(rl\d+),\s*\[\s*r(\d+)\s*\+\s*#([0-9A-F]+)h\s*\]')
RE_BYTE0 = re.compile(r'^\s*movb\s+(rl\d+),\s*\[\s*r(\d+)\s*\]')
RE_JMP = re.compile(r'^\s*(jmpa|jmpr?|j[a-z]+)\s+(?:cc_([A-Z]{1,3}),\s*)?(loc_[0-9A-F]+)')

d = open(BIN, 'rb').read()
PTR = {0x1400 + i: struct.unpack_from('<H', d, 0x61400 + i)[0]
       for i in range(0, 0x61E30 - 0x61400, 2)}


def ea_of(h):
    return 0xE0000 + PTR[h]


def byte_at(ea):
    o = 0x60000 + ea - 0xE0000
    return d[o] if 0 <= o < len(d) else None


def main():
    lines = open(ASM, encoding='latin-1').read().split('\n')
    labels = {}
    for i, ln in enumerate(lines):
        m = RE_LABEL.match(ln)
        if m and m.group(1) not in labels:
            labels[m.group(1)] = i

    func, sites = '?', []
    for i, ln in enumerate(lines):
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
        for j in range(i + 1, min(i + 4, len(lines))):
            b = RE_BYTE.match(lines[j])
            off = None
            if b and b.group(2) == reg:
                off = int(b.group(3), 16)
            else:
                b0 = RE_BYTE0.match(lines[j])
                if b0 and b0.group(2) == reg:
                    off = 0
            if off is None:
                continue
            for k in range(j + 1, min(j + 5, len(lines))):
                s = RE_JMP.match(lines[k])
                if not s:
                    if RE_HANDLE.match(lines[k]) or RE_BYTE.match(lines[k]):
                        break
                    continue
                tgt = labels.get(s.group(3))
                if tgt is None:
                    continue
                ea = ea_of(h)
                val = byte_at(ea + off)
                sites.append(dict(
                    fonction=func, ligne=i + 1, handle='0x%04X' % h,
                    structure='0x%05X' % ea, offset=off,
                    valeur='0x%02X' % val if val is not None else '?',
                    polarite=('actif si NON NUL' if s.group(2) == 'NZ'
                              else 'actif si NUL' if s.group(2) == 'Z'
                              else 'cc_%s' % (s.group(2) or '?')),
                    instr=s.group(1), bloc_shunte=tgt - k))
                break
            break

    sites.sort(key=lambda r: -r['bloc_shunte'])
    with open(OUT + '/switchs_calibration.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['fonction', 'ligne', 'handle', 'structure',
                                          'offset', 'valeur', 'polarite', 'instr',
                                          'bloc_shunte'], delimiter=';')
        w.writeheader(); w.writerows(sites)

    print('=== SWITCHS DE CALIBRATION ===')
    print('sites : %d   fonctions : %d   structures distinctes : %d'
          % (len(sites), len(set(s['fonction'] for s in sites)),
             len(set(s['handle'] for s in sites))))
    print('\n=== STRUCTURES PORTEUSES D\'OPTIONS (par nombre d\'options) ===')
    per = collections.Counter(s['handle'] for s in sites)
    for h, n in per.most_common(12):
        ea = ea_of(int(h, 16))
        print('  handle %s  EA 0x%05X  %2d options  (offsets %s)'
              % (h, ea, n, ','.join(str(s['offset']) for s in sites if s['handle'] == h)[:70]))

    print('\n=== LES 20 SWITCHS QUI SHUNTENT LE PLUS ===')
    print('  %-12s %-8s %-7s %-4s %-6s %-18s %s'
          % ('fonction', 'struct', 'offset', 'val', 'bloc', 'polarite', 'ligne'))
    for s in sites[:20]:
        print('  %-12s %-8s +%-6d %-4s %-6d %-18s %d'
              % (s['fonction'], s['structure'], s['offset'], s['valeur'],
                 s['bloc_shunte'], s['polarite'], s['ligne']))

    print('\n=== activite des options sur la structure principale ===')
    main_h = per.most_common(1)[0][0]
    sel = [s for s in sites if s['handle'] == main_h]
    act = [s for s in sel if (s['valeur'] != '0x00') == (s['polarite'] == 'actif si NON NUL')]
    print('  handle %s : %d options, dont %d dans l\'etat ACTIF dans ce firmware'
          % (main_h, len(sel), len(act)))
    print('  total des lignes shuntees par cette structure : %d'
          % sum(s['bloc_shunte'] for s in sel))


if __name__ == '__main__':
    main()
