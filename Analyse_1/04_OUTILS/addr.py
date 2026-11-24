import re,collections,pickle
lines=open('edc.asm',encoding='utf-8',errors='replace').read().split('\n')
segbase={'ROM':0x80000,'seg013':0x90000,'seg014':0xA0000,'seg015':0xB0000,'seg016':0xC0000,'seg017':0xD0000,'seg018':0xE0000,'seg019':0xF0000}
seg=None; cur=None; base=0; addr=0
blocks=collections.defaultdict(collections.Counter)
insaddr={}   # line -> ea
lab_re=re.compile(r'^([A-Za-z_0-9]+):\s*(.*)$')
lab_num=re.compile(r'^(?:loc|sub|word|byte|dword|unk|off|stru|asc|word3|byte3|qword)_([0-9A-F]{3,6})$')
for i,l in enumerate(lines):
    m=re.match(r'^(seg\d+|ROM)\s+section',l)
    if m: seg=m.group(1); base=segbase[seg]; addr=base; continue
    if seg is None: continue
    s=l.strip()
    mm=lab_re.match(s)
    if mm:
        nm,rest=mm.group(1),mm.group(2)
        m2=lab_num.match(nm)
        if m2:
            a=int(m2.group(1),16)
            if a>=0x80000: addr=a
        s=rest.strip()
        if not s: continue
    if not s or s.startswith(';'): continue
    if s.startswith('db '): b=1
    elif s.startswith('dw '): b=2
    elif s.startswith('dd '): b=4
    elif s.startswith('ds '): b=2
    else:
        b=4 if ('#' in s or ',' in s) else 2
        if re.match(r'^(ret|rets|reti|retp|nop|idle|pwrdn|srvwdt|diswdt|einit|srst|jmpr|jb|jnb|jbc|jnbs|bclr|bset)\b',s): b=2
        elif re.match(r'^(calls|calla|jmpa|jmps)\b',s): b=4
    blk=(addr//0x1000)*0x1000
    blocks[blk]['db' if s.startswith('db ') else 'cd']+=1
    insaddr[i+1]=addr
    addr+=b
pickle.dump((insaddr,dict(blocks)),open('addr.pkl','wb'))
tot=0
for blk in sorted(blocks):
    c=blocks[blk]; tot+=c['db']+c['cd']
print('lines mapped',tot,'of',len(lines))
# print compact map for flash region
row=[]
for blk in range(0x80000,0x100000,0x1000):
    c=blocks.get(blk)
    if not c: row.append('....'); continue
    r=c['db']/(c['db']+c['cd'])
    row.append('D' if r>0.9 else ('c' if r<0.1 else 'x'))
print(''.join(row))
for blk in range(0x80000,0x100000,0x1000):
    c=blocks.get(blk)
    if c: print(hex(blk), f"db={c['db']:5d} code={c['cd']:5d} ({c['db']/(c['db']+c['cd'])*100:.0f}% data)")
