#!/usr/bin/env python3
"""
Decodage 'par usage' des handles du Datensatz.

Principe : un handle (word_xxxx) est charge dans un registre, puis le code lit ou
ecrit des champs a offset fixe :  mov r4, word_1474 / mov r5, [r4+#1Ah]

On suit les registres ligne a ligne et on releve tous les couples (handle, offset)
avec le sens (lecture / ecriture) et le numero de ligne de clean.asm.

Sortie : usage_handles_offsets.csv  et  usage_handles_resume.csv
"""
import re, csv
from collections import defaultdict

SRC = '/home/user/clean.asm'
OUT1 = '/home/user/analyse_edc15c2_4hx/usage_handles_offsets.csv'
OUT2 = '/home/user/analyse_edc15c2_4hx/usage_handles_resume.csv'

RE_LOAD = re.compile(r'^\s*(?:mov|movb|movbz)\s+r(\d+)\s*,\s*(word_[0-9A-F]{4})\b')
RE_ANYMOV = re.compile(r'^\s*mov[abz]*\s+r(\d+)\s*,')
RE_OFF = re.compile(r'\[r(\d+)(?:\+#([0-9A-F]+)h?)?\]')

def parse_off(m):
    """offset en octets ; #6 sans h = 6 (convention hexa du desassembleur)"""
    if m.group(2) is None:
        return 0
    return int(m.group(2).rstrip('h'), 16)

rows = []          # (handle, offset, sens, ligne, texte)
regs = {}          # registre -> handle
byt = {}
for ln, line in enumerate(open(SRC, encoding='latin-1'), 1):
    s = line.rstrip('\n')
    # 1) relever les champs [rN+#off] AVANT de mettre a jour les registres
    if regs:
        # position de la virgule separant source et destination
        for m in RE_OFF.finditer(s):
            r = int(m.group(1))
            if r not in regs:
                continue
            off = parse_off(m)
            if off > 0x100:      # acces absolus (image EEPROM, flash) : pas un champ
                continue
            # sens : si le crochet est avant la premiere virgule -> destination
            comma = s.find(',')
            pos = m.start()
            sens = 'ecriture' if (comma > 0 and pos < comma) else 'lecture'
            regs_used = regs[r]
            rows.append((regs_used, off, sens, ln, s.strip()))
    # 2) mise a jour de l'etat des registres
    m = RE_LOAD.match(s)
    if m:
        h = int(m.group(2)[5:], 16)
        if 0x1400 <= h <= 0x1E30:          # uniquement les vrais handles du Datensatz
            regs[int(m.group(1))] = m.group(2)
        else:
            regs.pop(int(m.group(1)), None)
    else:
        m2 = RE_ANYMOV.match(s)
        if m2:
            regs.pop(int(m2.group(1)), None)
        elif 'add' in s or 'sub' in s:
            pass

with open(OUT1, 'w', newline='') as f:
    wr = csv.writer(f)
    wr.writerow(['handle', 'offset', 'offset_hex', 'sens', 'ligne', 'instruction'])
    for h, off, sens, ln, txt in rows:
        wr.writerow([h, off, '0x%02X' % off, sens, ln, txt])

# resume par handle
per = defaultdict(lambda: {'lecture': set(), 'ecriture': set(), 'n': 0, 'lignes': []})
for h, off, sens, ln, txt in rows:
    p = per[h]
    p[sens].add(off)
    p['n'] += 1
    if len(p['lignes']) < 40:
        p['lignes'].append(ln)

with open(OUT2, 'w', newline='') as f:
    wr = csv.writer(f)
    wr.writerow(['handle', 'nb_acces', 'offsets_lus', 'offsets_ecrits', 'premieres_lignes'])
    for h in sorted(per):
        p = per[h]
        wr.writerow([h, p['n'],
                     ' '.join('0x%02X' % o for o in sorted(p['lecture'])),
                     ' '.join('0x%02X' % o for o in sorted(p['ecriture'])),
                     ' '.join(str(x) for x in p['lignes'][:6])])

print('acces releves        :', len(rows))
print('handles distincts    :', len(per))
print()
dense = 0
for h, p in per.items():
    lo = sorted(p['lecture'])
    if len(lo) >= 8 and lo[:4] == [0, 2, 4, 6]:
        dense += 1
print('handles lus en BALAYAGE SEQUENTIEL (0x00,0x02,0x04,0x06 + au moins 8 offsets) :', dense)
print()
print('=== 20 handles les plus utilises (nb d acces) ===')
for h, p in sorted(per.items(), key=lambda x: -x[1]['n'])[:20]:
    lo = sorted(p['lecture'])
    print('  %-10s %4d acces  %2d offsets lus : %s' % (
        h, p['n'], len(lo), ' '.join('0x%02X' % o for o in lo[:10])))
