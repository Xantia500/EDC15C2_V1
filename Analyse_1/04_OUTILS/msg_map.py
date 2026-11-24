import re
L = open('/home/user/clean.asm', errors='replace').read().split('\n')
nd = 0
rows = []
for i, l in enumerate(L):
    if re.search(r'calls\s+9,\s*sub_9D166', l):
        nd += 1
        r12 = r13 = r14 = r15 = ln = None
        for j in range(i - 1, max(i - 14, 0), -1):
            s = L[j]
            m = re.search(r'mov\s+r12,\s*#([0-9A-Fa-f]+)h?', s)
            if m and r12 is None: r12 = int(m.group(1), 16)
            m = re.search(r'mov\s+r13,\s*#([0-9A-Fa-f]+)h?', s)
            if m and r13 is None: r13 = int(m.group(1), 16)
            m = re.search(r'mov\s+r14,\s*#([0-9A-Fa-f]+)h?', s)
            if m and r14 is None: r14 = int(m.group(1), 16)
            m = re.search(r'mov\s+r15,\s*#0([0-9A-Fa-f]{4})h', s)
            if m and r15 is None: r15 = int(m.group(1), 16)
            m = re.search(r'mov\s+r4,\s*#([0-9A-Fa-f]+)h?', s)
            if m and ln is None and j + 1 < len(L) and '[-r0]' in L[j + 1]:
                ln = int(m.group(1), 16)
        rows.append((i + 1, r12, r13, r14, r15, ln))
print('sites sub_9D166 :', nd)
print('ligne   idx r13 r14  dest     len')
for r in sorted(rows, key=lambda x: (x[1] if x[1] is not None else 999)):
    print('l.%-6d %-4s %-3s %-4s %-8s %s' % (
        r[0],
        '?' if r[1] is None else r[1],
        '?' if r[2] is None else r[2],
        '?' if r[3] is None else r[3],
        '?' if r[4] is None else '0x%04X' % r[4],
        '?' if r[5] is None else r[5]))
