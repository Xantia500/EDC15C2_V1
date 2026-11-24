#!/usr/bin/env python3
"""
edc15_analyze.py — outillage d'analyse pour listing IDA d'un calculateur Bosch EDC15C2 (PSA 2.2 HDi 4HX).

Entrée : un listing IDA Pro (processeur C166) exporté en .asm/.txt pour une image flash
         de 512 Ko chargée à l'adresse 0x80000 (convention EA = 0x80000 + offset fichier).

Sorties :
  - cartographie par blocs de 4 Ko (code / données / remplissage 0xC3)
  - inventaire des fonctions (adresse, taille approx., nb d'appels, SFR utilisés)
  - chaînes ASCII et leurs adresses
  - tables de pointeurs 32 bits (détection automatique)
  - reconstruction PARTIELLE du binaire (octets de données uniquement) -> recon_partielle.bin
  - contrôle des empreintes d'une image .bin de référence (option --bin)

Usage :
  python3 edc15_analyze.py listing.asm [--bin image.bin] [--out dossier_sortie]
"""

import re, sys, os, csv, hashlib, zlib, collections, argparse

BASE = 0x80000          # adresse de chargement de l'image
FLASH_SIZE = 0x80000    # 512 Ko

MNEM_2 = ('ret', 'rets', 'reti', 'retp', 'nop', 'jmpr', 'mul', 'mulu', 'div', 'divu',
          'divl', 'divlu', 'shl', 'shr', 'rol', 'ror', 'ashr', 'cpl', 'cplb', 'neg', 'negb')
MISC4 = ('srst', 'idle', 'pwrdn', 'srvwdt', 'diswdt', 'einit', 'trap', 'atomic', 'extr',
         'scxt', 'pcall', 'bfldh', 'bfldl', 'band', 'bor', 'bxor', 'bcmp', 'bmov', 'bmovn',
         'extp', 'exts', 'extpr', 'extsr')

LAB_NUM = re.compile(r'^(?:loc|sub|word|byte|dword|unk|off|stru|asc|word3|byte3)_([0-9A-F]{3,6})$')


def instr_len(mn, op):
    """Longueur estimée (2 ou 4 octets) d'une instruction C166. Approximation fiable à ~95 %."""
    if mn in ('ret', 'rets', 'reti', 'retp', 'nop', 'jmpr'):
        return 2
    if mn in ('calls', 'calla', 'jmpa', 'jmps'):
        return 4
    if mn in ('jb', 'jnb', 'jbc', 'jnbs', 'bclr', 'bset'):
        return 2 if re.match(r'^r\d+\.\d+', op) else 4
    if mn in MISC4:
        return 4
    if re.search(r'\b(word|byte|dword|unk|off|stru|asc)_[0-9A-F]+', op):
        return 4
    if re.search(r'\b[A-Z][A-Z0-9_]{2,}\b', op):        # nom de SFR
        return 4
    if '#' in op:
        val = op.split('#')[1].strip()
        if val.startswith("'"):
            return 2 if mn.endswith('b') else 4
        m = re.match(r'^[0-9A-F]+h$', val)
        n = int(val[:-1], 16) if m else 0x100
        if mn.endswith('b') and n < 16 and mn not in ('cmpi2', 'cmpd2'):
            return 2
        if n < 8 and mn in ('add', 'addb', 'sub', 'subb', 'cmp', 'cmpb', 'and', 'or', 'xor',
                            'addc', 'subc'):
            return 2
        if mn in ('cmpi1', 'cmpd1', 'shl', 'shr', 'rol', 'ror', 'ashr') and n < 16:
            return 2
        return 4
    if mn in ('mov', 'movb', 'movbz', 'movbs') and '[' in op:
        return 2 if re.search(r'\[r\d+[+-]?\]', op) else 4
    if mn in MNEM_2:
        return 2
    return 4


def parse_listing(path):
    """Retourne (lines, insaddr, funcs, sfrs)."""
    lines = open(path, encoding='utf-8', errors='replace').read().replace('\r', '').split('\n')
    insaddr, funcs = {}, {}
    seg, addr = None, 0
    cur = None
    sfrs = set()
    in_sfr = False
    for i, raw in enumerate(lines):
        l = raw.rstrip()
        if re.match(r'^(seg\d+|ROM)\s+section', l):
            in_sfr = False
            m = re.search(r'seg(\d+)', l)
            seg = int(m.group(1)) if m else 12
            addr = BASE + (seg - 12) * 0x10000 if m else BASE
            # cas particulier : segment nommé "ROM" = base de l'image
            if not m:
                addr = BASE
            continue
        if l.startswith('SFR') and 'section' in l:
            in_sfr = True
            continue
        if in_sfr:
            mm = re.match(r'^([A-Za-z_0-9]+):\s+ds', l)
            if mm:
                sfrs.add(mm.group(1))
            if l.startswith('ROM') and 'section' in l:
                in_sfr = False
            else:
                continue
        if seg is None:
            continue

        s = l.strip()
        if s.startswith('; End of function') and cur:
            cur['end'] = i + 1
            funcs[cur['name']] = cur
            cur = None
            continue

        mm = re.match(r'^([A-Za-z_0-9]+):(.*)$', s)
        if mm:
            nm, rest = mm.group(1), mm.group(2).strip()
            lm = LAB_NUM.match(nm)
            if lm:
                a = int(lm.group(1), 16)
                if a >= BASE:
                    addr = a
            if cur is None and nm.startswith('sub_'):
                cur = {'name': nm, 'ea': int(nm[4:], 16), 'line': i + 1,
                       'instr': [], 'labels': [nm]}
            elif cur is not None and nm.startswith('sub_'):
                cur = {'name': nm, 'ea': int(nm[4:], 16), 'line': i + 1,
                       'instr': [], 'labels': [nm]}
            s = rest
            if not s:
                continue
        if not s or s.startswith(';') or s.startswith(('proc', 'endp', 'public', 'assume')):
            continue

        # longueur (commentaires retirés : ils contiennent parfois des chiffres)
        sc = s.split(';')[0]
        if sc.startswith('db'):
            b = max(1, len(re.findall(r"(?<![\w.])('.'|0?[0-9A-F]{1,2}h|\d+)", sc[2:])))
        elif sc.startswith('dw'):
            b = 2 * max(1, len(re.findall(r"(?<![\w.])(0?[0-9A-F]{1,4}h|\d+)", sc[2:])))
        elif sc.startswith('dd'):
            b = 4
        elif sc.startswith('ds'):
            b = 2
        else:
            mn = re.match(r'^([a-z]+)\s*(.*)$', s)
            if not mn:
                continue
            b = instr_len(mn.group(1), mn.group(2).split(';')[0])
            if cur is not None:
                cur['instr'].append((mn.group(1), mn.group(2).split(';')[0].strip(), i + 1))
        insaddr[i + 1] = addr
        addr += b
    if cur:
        funcs[cur['name']] = cur
    return lines, insaddr, funcs, sfrs


def reconstruct(lines, insaddr):
    """Reconstruit les octets de DONNÉES (db/dw) -> (img, mask). Le code reste à 0."""
    img, mask = bytearray(FLASH_SIZE), bytearray(FLASH_SIZE)

    def put(a, v):
        if BASE <= a < BASE + FLASH_SIZE:
            img[a - BASE] = v & 0xFF
            mask[a - BASE] = 1

    for i, l in enumerate(lines):
        a = insaddr.get(i + 1)
        if a is None:
            continue
        body = l.split(';')[0].strip()
        if re.match(r'^db\s', body):
            for k, t in enumerate(re.findall(r"(?<![\w.])('.'|0?[0-9A-F]{1,2}h|\d+)", body[2:])):
                v = ord(t[1]) if t.startswith("'") else (int(t[:-1], 16) if t.endswith('h') else int(t))
                put(a + k, v)
        elif re.match(r'^dw\s', body):
            for k, t in enumerate(re.findall(r"(?<![\w.])(0?[0-9A-F]{1,4}h|\d+)", body[2:])):
                v = int(t[:-1], 16) if t.endswith('h') else int(t)
                put(a + 2 * k, v)
                put(a + 2 * k + 1, v >> 8)
    return img, mask


def ascii_strings(img, mask, minlen=4):
    out, i = [], 0
    while i < len(img):
        if 32 <= img[i] < 127 and mask[i]:
            j = i
            while j < len(img) and mask[j] and 32 <= img[j] < 127:
                j += 1
            s = img[i:j].decode('latin1')
            if j - i >= minlen and sum(c.isalnum() for c in s) >= minlen - 1:
                out.append((BASE + i, s))
            i = j
        else:
            i += 1
    return out


def pointer_tables(img, min_entries=16):
    """Détecte les tables de pointeurs 32 bits pointant dans la flash."""
    tables, a = [], BASE
    while a < BASE + FLASH_SIZE - 4:
        run, b = [], a
        while b < BASE + FLASH_SIZE - 4:
            v = int.from_bytes(img[b - BASE:b - BASE + 4], 'little')
            if BASE <= v < BASE + FLASH_SIZE:
                run.append(v)
                b += 4
            else:
                break
        if len(run) >= min_entries:
            tables.append((a, len(run), run))
            a = b + 4
        else:
            a += 2
    return tables


def block_map(img, mask):
    """Classe chaque bloc de 4 Ko : vide (remplissage 0xC3) / code / données."""
    rows = []
    for a in range(BASE, BASE + FLASH_SIZE, 0x1000):
        seg = img[a - BASE:a - BASE + 0x1000]
        ms = mask[a - BASE:a - BASE + 0x1000]
        known = sum(ms)
        fill = sum(1 for k in range(len(seg)) if ms[k] and seg[k] == 0xC3)
        rows.append((a, known, fill))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('listing')
    ap.add_argument('--bin', dest='binfile')
    ap.add_argument('--out', default='sortie_analyse')
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    print(f"[*] Lecture de {args.listing} …")
    lines, insaddr, funcs, sfrs = parse_listing(args.listing)
    print(f"    lignes: {len(lines)}   instructions adressées: {len(insaddr)}   fonctions: {len(funcs)}   SFR connus: {len(sfrs)}")

    img, mask = reconstruct(lines, insaddr)
    cov = sum(mask)
    print(f"[*] Reconstruction des données : {cov} octets ({100*cov/FLASH_SIZE:.1f} % de l'image)")
    open(os.path.join(args.out, 'recon_partielle.bin'), 'wb').write(bytes(img))

    # chaînes
    strs = ascii_strings(img, mask)
    with open(os.path.join(args.out, 'chaines.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['adresse', 'chaine'])
        for a, s in strs:
            w.writerow([f'{a:06X}', s])
    print(f"[*] {len(strs)} chaînes ASCII")

    # tables de pointeurs
    tabs = pointer_tables(img)
    with open(os.path.join(args.out, 'tables_pointeurs.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['table_adresse', 'index', 'cible', 'cible_est_fonction_ida'])
        for ta, n, run in tabs:
            for k, v in enumerate(run):
                w.writerow([f'{ta:06X}', k, f'{v:06X}', 'oui' if v in {x['ea'] for x in funcs.values()} else 'non'])
    for ta, n, run in tabs:
        print(f"    table de pointeurs @0x{ta:06X} : {n} entrées (0x{run[0]:06X} … 0x{run[-1]:06X})")

    # fonctions
    callers = collections.defaultdict(set)
    for fn, d in funcs.items():
        for mn, op, ln in d['instr']:
            if mn in ('calls', 'call', 'calla'):
                m = re.search(r'(sub_[0-9A-F]+)', op)
                if m and m.group(1) in funcs:
                    callers[m.group(1)].add(fn)
    with open(os.path.join(args.out, 'fonctions.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['ea', 'nom', 'nb_instr', 'nb_cibles', 'nb_appelants', 'sfr_utilises'])
        for fn, d in sorted(funcs.items(), key=lambda kv: kv[1]['ea']):
            used = sorted({s for s in sfrs for mn, op, ln in d['instr'] if s in op})
            targets = {re.search(r'(sub_[0-9A-F]+)', op).group(1)
                       for mn, op, ln in d['instr']
                       if mn in ('calls', 'call', 'calla') and re.search(r'(sub_[0-9A-F]+)', op)}
            w.writerow([f"{d['ea']:06X}", fn, len(d['instr']),
                        len([t for t in targets if t in funcs]), len(callers.get(fn, ())),
                        ' '.join(used)])
    print(f"[*] fonctions exportées : {len(funcs)}")

    # cartographie
    with open(os.path.join(args.out, 'blocs_4k.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['bloc', 'octets_connus', 'dont_remplissage_C3', 'classe'])
        for a, known, fill in block_map(img, mask):
            if known == 0:
                cls = 'code/inconnu'
            elif fill > 0.9 * known:
                cls = 'vide (0xC3)'
            elif fill > 0.5 * known:
                cls = 'mixte'
            else:
                cls = 'données'
            w.writerow([f'{a:06X}', known, fill, cls])

    # empreintes d'une image de référence
    if args.binfile:
        data = open(args.binfile, 'rb').read()
        print(f"\n[*] Image de référence : {args.binfile} ({len(data)} octets)")
        print(f"    MD5    {hashlib.md5(data).hexdigest().upper()}")
        print(f"    SHA256 {hashlib.sha256(data).hexdigest().upper()}")
        print(f"    CRC32  {zlib.crc32(data) & 0xFFFFFFFF:08X}")
        if len(data) == FLASH_SIZE:
            # comparaison des deux copies du Datensatz
            a, b, n = 0xE0000 - BASE, 0xF0000 - BASE, 0xC000
            diff = [k for k in range(n) if data[a + k] != data[b + k]]
            print(f"    copies Datensatz 0xE0000 / 0xF0000 : {len(diff)} octet(s) différent(s)"
                  + (f" aux offsets {[hex(0xE0000+k) for k in diff[:10]]}" if diff else ""))
            for pat, label in ((b'0281010877', 'n° pièce Bosch'), (b'1037353776', 'n° SW'),
                               (b'B075WF2S01', 'désignation SW'), (b'TSW V2.31', 'version TSW'),
                               (b'\xAA\x55\x75\x14\x89\x11\x30\xAA', 'magic BOOT')):
                idx = [hex(BASE + k) for k in range(len(data)) if data.startswith(pat, k)]
                print(f"    {label:20s} : {idx if idx else 'ABSENT'}")
    print(f"\n[*] Résultats dans {args.out}/")


if __name__ == '__main__':
    main()
