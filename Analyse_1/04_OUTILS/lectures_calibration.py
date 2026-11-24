#!/usr/bin/env python3
"""
Recensement de TOUS les sites de lecture de la zone calibration.

Idiome identifie (etape 59) :

    mov   r4, word_1474      ; r4 <- valeur du pointeur (offset dans la page 0xE0000)
    mov   r5, [r4]           ; lecture dans la structure

Toute lecture de calibration passe donc par une adresse indirecte issue d'un
mot de la table de pointeurs. Ce script :

  1. releve chaque site « mov rN, word_1xxx » suivi d'un usage [rN(+k)] ;
  2. rattache le site a sa fonction englobante ;
  3. releve l'OFFSET lu dans la structure (+0, +2, +4...) ;
  4. detecte les fonctions qui lisent >=3 mots CONSECUTIFS a la meme base
     -> candidats correcteurs PI / PID.

Sorties : lectures_calibration.csv, candidats_pid.csv
"""
import re, csv, collections

ASM = '/home/user/clean.asm'
OUT = '/home/user/analyse_edc15c2_4hx'

RE_HANDLE = re.compile(r'^\s*mov\s+r(\d+),\s*(word|byte)_(1[0-9A-F]{3})\b')
RE_LABEL = re.compile(r'^(sub_[0-9A-F]+|[a-z]+_[0-9A-F]+|loc_[0-9A-F]+):')
RE_USE = re.compile(r'\[\s*r(\d+)\s*(?:\+\s*(0x[0-9A-F]+|\d+))?\s*\]')


def scan():
    lines = open(ASM, encoding='latin-1').read().split('\n')
    sites = []
    func = '(hors fonction)'
    for i, ln in enumerate(lines):
        m = RE_LABEL.match(ln)
        if m and ln.startswith('sub_'):
            func = m.group(1)
        m = RE_HANDLE.match(ln)
        if not m:
            continue
        reg, kind, num = int(m.group(1)), m.group(2), m.group(3)
        h = int(num, 16)
        if not (0x1400 <= h <= 0x1E30):
            continue
        # chercher l'usage [rN] dans les 4 lignes suivantes (ou la meme)
        for j in range(i, min(i + 5, len(lines))):
            for u in RE_USE.finditer(lines[j]):
                if int(u.group(1)) != reg:
                    continue
                off = 0
                if u.group(2):
                    off = int(u.group(2), 16) if u.group(2).startswith('0x') else int(u.group(2))
                # distinguer lecture / ecriture
                ecrit = bool(re.match(r'^\s*mov\s*\[\s*r\d+', lines[j]))
                sites.append(dict(ligne=i + 1, fonction=func, handle='0x%04X' % h,
                                  offset=off, sens='E' if ecrit else 'L',
                                  instr=lines[j].strip()[:44]))
                break
            else:
                continue
            break
    return sites


def main():
    sites = scan()
    print('sites de lecture/ecriture calibration : %d' % len(sites))
    with open(OUT + '/lectures_calibration.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['ligne', 'fonction', 'handle', 'offset', 'sens',
                                          'instr'], delimiter=';')
        w.writeheader(); w.writerows(sites)

    par_f = collections.Counter(s['fonction'] for s in sites)
    print('fonctions concernees : %d' % len(par_f))
    print('\n=== les 12 fonctions qui lisent le plus la calibration ===')
    for f, n in par_f.most_common(12):
        print('  %-14s %4d sites' % (f, n))

    # ---- candidats PI / PID : >=3 offsets distincts et consecutifs, meme fonction + handle
    grp = collections.defaultdict(set)
    for s in sites:
        if s['sens'] == 'L':
            grp[(s['fonction'], s['handle'])].add(s['offset'])
    pid = []
    for (f, h), offs in grp.items():
        o = sorted(offs)
        # plus longue suite d'offsets pairs consecutifs
        best = run = [o[0]] if o else []
        for a, b in zip(o, o[1:]):
            if b - a == 2:
                run = run + [b] if run and run[-1] == a else [a, b]
            else:
                run = [b]
            if len(run) > len(best):
                best = run
        if len(best) >= 3:
            pid.append(dict(fonction=f, handle=h, offsets=','.join('+%d' % x for x in best),
                            n=len(best)))
    pid.sort(key=lambda r: -r['n'])
    with open(OUT + '/candidats_pid.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['fonction', 'handle', 'offsets', 'n'], delimiter=';')
        w.writeheader(); w.writerows(pid)
    print('\n=== candidats correcteurs : >=3 mots consecutifs lus a la meme base ===')
    for r in pid[:15]:
        print('  %-14s handle %s  offsets %s' % (r['fonction'], r['handle'], r['offsets']))

    # ---- couverture : combien de handles distincts
    hs = set(s['handle'] for s in sites)
    print('\nhandles distincts atteints : %d' % len(hs))
    print('offsets le plus souvent lus :',
          collections.Counter(s['offset'] for s in sites if s['sens'] == 'L').most_common(8))


if __name__ == '__main__':
    main()
