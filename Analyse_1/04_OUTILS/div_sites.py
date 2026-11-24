import re
L = open('/home/user/clean.asm', errors='replace').read().split('\n')
sites = []
for i, l in enumerate(L):
    if re.match(r'\s+(div|divl|divu|divlu)\s', l):
        ctx = L[max(0, i - 6):i + 1]
        ctxs = '\n'.join(ctx)
        vs = sorted(set(re.findall(r'\b(?:word|byte)_[0-9A-F]{4}\b', ctxs)))
        sites.append((i + 1, l.strip(), vs))
print('sites de division :', len(sites))
rpm = {'word_C91C', 'word_C576', 'word_C42E', 'word_C908', 'word_C3D2'}
speedish = {'word_FC04', 'word_C404', 'word_C3FC', 'word_D41E'}
print('\n--- sites avec un candidat REGIME ---')
for n, ins, vs in sites:
    if rpm & set(vs):
        print('l.%-7d %-28s %s' % (n, ins, ' '.join(vs)))
print('\n--- sites avec un candidat VITESSE ---')
for n, ins, vs in sites:
    if speedish & set(vs):
        print('l.%-7d %-28s %s' % (n, ins, ' '.join(vs)))
print('\n--- 12 premiers sites (apercu) ---')
for n, ins, vs in sites[:12]:
    print('l.%-7d %-28s %s' % (n, ins, (' '.join(vs))[:110]))
