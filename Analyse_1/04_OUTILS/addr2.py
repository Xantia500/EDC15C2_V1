import re,collections,pickle
lines=open('edc.asm',encoding='utf-8',errors='replace').read().split('\n')
segbase={'ROM':0x80000,'seg013':0x90000,'seg014':0xA0000,'seg015':0xB0000,'seg016':0xC0000,'seg017':0xD0000,'seg018':0xE0000,'seg019':0xF0000}
seg=None; addr=0
insaddr={}; drift=collections.Counter()
lab_num=re.compile(r'^(?:loc|sub|word|byte|dword|unk|off|stru|asc|word3|byte3|qword|word_F|byte_F)_([0-9A-F]{3,6})$')
JUMP2=re.compile(r'^(ret|rets|reti|retp|nop|jmpr|jb|jnb|jbc|jnbs|bclr|bset|push|pop|mul|mulu|div|divu|divl|divlu|shl|shr|rol|ror|ashr|cpl|cplb|neg|negb|movbz|movbs)\b')
MISC4=re.compile(r'^(srst|idle|pwrdn|srvwdt|diswdt|einit|trap|atomic|extr|scxt|pcall|bfldh|bfldl|band|bor|bxor|bcmp|bmov|bmovn|extp|exts|extpr|extsr)\b')
def length(mn,op):
    if mn in ('ret','rets','reti','retp','nop'): return 2
    if mn in ('srst','idle','pwrdn','srvwdt','diswdt','einit'): return 4
    if mn in ('calls','calla','jmpa','jmps'): return 4
    if mn=='jmpr': return 2
    if mn in ('jb','jnb','jbc','jnbs'):
        return 2 if re.match(r'^r\d+\.\d+',op) else 4
    if mn in ('bclr','bset'):
        return 2 if re.match(r'^r\d+\.\d+',op) else 4
    if mn in ('scxt','pcall','bfldh','bfldl','atomic','extr','extpr','extsr','trap'): return 4
    if mn in ('band','bor','bxor','bcmp','bmov','bmovn'):
        # reg,bitaddr(non-reg) -> 4
        return 2 if all(re.match(r'^[a-z]{2}\d(\.\d)?$',x.strip()) for x in op.split(',')) else 4
    # memory symbol operand → 4
    if re.search(r'\b(word|byte|dword|unk|off|stru|asc)_[0-9A-F]+',op): return 4
    if re.search(r'\b[A-Z][A-Z0-9_]{2,}\b',op): return 4   # SFR name
    if '#' in op:
        val=op.split('#')[1].strip()
        m=re.match(r"^'(.?)'",val)
        if m: return 2 if mn.endswith('b') else 4
        m=re.match(r'^[0-9A-F]+h$',val)
        if m:
            n=int(val[:-1],16)
        else:
            try:
                if val.startswith('0') and len(val)>1 and all(c in '01234567' for c in val): n=int(val,8)
                else: n=int(val)
            except: n=0x100
        if mn.endswith('b') and n<16 and mn not in ('cmpi2','cmpd2'): return 2
        if n<8 and mn in ('add','addb','sub','subb','cmp','cmpb','and','or','xor','addc','subc'): return 2
        if mn in ('cmpi1','cmpd1','shl','shr','rol','ror','ashr') and n<16: return 2
        return 4
    if mn in ('movb','movbz','movbs') and '[' in op: return 2
    if mn in ('mov','movb') and ('[' in op): 
        return 2 if re.search(r'\[r\d+[+-]?\]',op) else 4
    if mn in ('add','sub','cmp','and','or','xor','addc','subc','mul','mulu','shl','shr','rol','ror','ashr','pri or'.replace(' ','')): return 2
    return 4
cur=None
for i,l in enumerate(lines):
    m=re.match(r'^(seg\d+|ROM)\s+section',l)
    if m: seg=m.group(1); addr=segbase[seg]; continue
    if seg is None: continue
    s=l.strip()
    mm=re.match(r'^([A-Za-z_0-9]+):(.*)$',s)
    if mm:
        nm=mm.group(1); rest=mm.group(2).strip()
        m2=lab_num.match(nm)
        if m2:
            a=int(m2.group(1),16)
            if a>=0x80000:
                if addr in insaddr.values(): pass
                drift[a-addr]+=1
                addr=a
        s=rest
        if not s: continue
    if not s or s.startswith(';') or s.startswith('proc') or s.startswith('endp'): continue
    if s.startswith('db'):
        n=len(re.findall(r'\b(?:0)?[0-9A-F]{1,2}h\b|\b\d+\b',s.split(';')[0].replace('db','')))
        b=max(1,n)
    elif s.startswith('dw'):
        b=2
    elif s.startswith('dd'):
        b=4
    elif s.startswith('ds'):
        b=2
    else:
        mn=re.match(r'^([a-z]+)\s*(.*)$',s)
        if not mn: continue
        b=length(mn.group(1),mn.group(2).split(';')[0])
    insaddr[i+1]=addr
    addr+=b
print('lines',len(insaddr))
print('drift histogram (computed-label):', drift.most_common(8))
pickle.dump(insaddr,open('addr.pkl','wb'))
