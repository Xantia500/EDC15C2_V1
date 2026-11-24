#!/usr/bin/env python3
"""Associe a chaque handle du Datensatz la fonction de clean.asm qui le consomme."""
import re, csv
from collections import defaultdict

src = open('/home/user/clean.asm', encoding='latin-1').read().split('\n')
func = [None] * (len(src) + 2)
cur = None
for i, l in enumerate(src, 1):
    m = re.match(r'^(sub_[0-9A-F]+):', l)
    if m:
        cur = m.group(1)
    func[i] = cur

acc = list(csv.DictReader(open('/home/user/analyse_edc15c2_4hx/usage_handles_offsets.csv')))
byf = defaultdict(lambda: defaultdict(int))
byh = defaultdict(lambda: defaultdict(int))
for r in acc:
    f = func[int(r['ligne'])]
    if f is None:
        continue
    byf[f][r['handle']] += 1
    byh[r['handle']][f] += 1

out = '/home/user/analyse_edc15c2_4hx/consommateurs_handles.csv'
with open(out, 'w', newline='') as fh:
    wr = csv.writer(fh)
    wr.writerow(['handle', 'nb_acces', 'consommateur_principal', 'part', 'autres_consommateurs'])
    for h in sorted(byh, key=lambda x: -sum(byh[x].values())):
        d = byh[h]
        f0 = max(d, key=d.get)
        tot = sum(d.values())
        wr.writerow([h, tot, f0, '%.0f%%' % (100.0 * d[f0] / tot),
                     ' '.join('%s(%d)' % (k, v) for k, v in sorted(d.items(), key=lambda x: -x[1])[1:4])])

print('handle -> consommateur ecrit dans', out)
print()
print('=== fonctions consommant le plus de handles distincts ===')
rank = sorted(byf.items(), key=lambda x: -len(x[1]))
for f, d in rank[:16]:
    print('  %-12s %3d handles, %4d acces' % (f, len(d), sum(d.values())))
print()
print('=== handles mono-consommateur (une seule fonction, >=10 acces) ===')
mono = [(h, d) for h, d in byh.items() if len(d) == 1 and sum(d.values()) >= 10]
print('  ', len(mono), 'handles')
