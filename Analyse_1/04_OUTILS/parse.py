import re,json,collections
txt=open('edc.asm',encoding='utf-8',errors='replace').read().split('\n')
MNEM=set("""add addb addc addcb and andb ashr atomic band bclr bcmp bfldh bfldl bmov bmovn bor bset bxor calla calli calls callr cmp cmpb cmpd1 cmpd2 cmpi1 cmpi2 cpl cplb diswdt div divl divlu divu einit extr exts extp extpr ext tr idiv idivl? idle jb jbc jmpa jmpi jmpr jmps jnb jnbs mov movb movbs movbz mul mulu neg negb nop or orb pcall pop prior push pwrdn ret reti retp rets rol ror scxt shl shr srst srvwdt sub subb subc subcb trap xor xorb""".split())
MNEM={m for m in MNEM if m.isalpha()}
def clean_comment(l):
    # cut inline annotations added by previous analysis at '; [EDC15'
    return l
funcs={}
cur=None; seg=None
warn=0
for i,l in enumerate(txt):
    l=l.rstrip()
    m=re.match(r'^(seg\d+|ROM)\s+section',l)
    if m: seg=m.group(1); continue
    m=re.match(r'^; End of function (\S+)',l)
    if m:
        if cur: cur['end_line']=i+1; funcs[cur['name']]=cur; cur=None
        continue
    m=re.match(r'^([A-Za-z_0-9]+):\s*(.*)$',l)
    if m and cur is not None:
        # inner label
        cur['labels'].append(m.group(1))
        rest=m.group(2)
        if rest.strip(): l=' '*16+rest
    if cur is None:
        m=re.match(r'^(sub_[0-9A-Fa-f]+):\s*(.*)$',l)
        if m:
            cur={'name':m.group(1),'ea':int(m.group(1)[4:],16),'seg':seg,'line':i+1,'labels':[m.group(1)],'instr':[],'data':[],'calls':[]}
            rest=m.group(2)
            if rest.strip(): l=' '*16+rest
            else: continue
    if cur is None: continue
    s=l.strip()
    if not s or s.startswith(';'): continue
    mm=re.match(r'^([a-z]+)\s*(.*)$',s)
    if not mm: continue
    mn=mm.group(1)
    if mn in MNEM:
        op=mm.group(2)
        op=re.sub(r'\s*;.*$','',op).strip()
        cur['instr'].append((mn,op,i+1))
print('functions parsed',len(funcs))
json.dump({k:{'ea':v['ea'],'seg':v['seg'],'n_instr':len(v['instr']),'labels':v['labels']} for k,v in funcs.items()},open('funcs.json','w'))
import pickle
pickle.dump(funcs,open('funcs.pkl','wb'))
# stats
c=collections.Counter(v['seg'] for v in funcs.values())
print(c)
print(sorted([ (v['ea'],k,len(v['instr'])) for k,v in funcs.items()])[:5])
