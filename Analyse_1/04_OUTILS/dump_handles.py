import struct, sys
d = open('/home/user/edc.bin','rb').read()
T = 0x61400
def ea_of(h):
    i = h - 0x1400
    if i < 0 or T+i+2 > len(d): return None
    v = struct.unpack_from('<H', d, T+i)[0]
    if v == 0 or v == 0xFFFF: return None
    return 0xE0000 + v
def words(ea, n):
    fo = 0x60000 + (ea - 0xE0000)
    return struct.unpack_from('<%dH'%n, d, fo)
def bytes_(ea, n):
    fo = 0x60000 + (ea - 0xE0000)
    return d[fo:fo+n]
n = int(sys.argv[1])
for a in sys.argv[2:]:
    h = int(a,16)
    ea = ea_of(h)
    if ea is None:
        print('handle 0x%04X : non résolu'%h); continue
    print('handle 0x%04X -> EA 0x%05X (fo 0x%05X)'%(h, ea, 0x60000+(ea-0xE0000)))
    ws = words(ea, n)
    for k in range(0, n, 8):
        print('  +%02X : %s'%(2*k, ' '.join('%5d'%w for w in ws[k:k+8])), '   |', ' '.join('%04X'%w for w in ws[k:k+8]))
    print('  octets:', ' '.join('%02X'%b for b in bytes_(ea, min(n*2, 64))))
