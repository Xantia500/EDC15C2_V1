#!/usr/bin/env python3
"""
Segmentation INTERNE des blocs du Datensatz.

Constat (etape 58) : un bloc adresse par un handle peut contenir PLUSIEURS structures.
Le decodeur d'origine testait une seule structure au debut du bloc ; tout bloc dont la
premiere structure n'avait pas l'en-tete attendu etait classe « pas d'en-tete 1-D ».
Exemple : 0xE8872 (carte Regime x Air) est suivie de 0xE88DA, 0xE870C, 0xE882A...

Ce script parcourt chaque bloc du debut a la fin, a tout alignement pair, et essaie :
  - 1-D : [tag][n][axe n][valeurs n]                taille 4+4n
  - 2-D : [tagY][nY][axeY][tagX][nX][axeX][grille]  taille 8+2nY+2nX+2nY.nX
et ne retient une structure que si elle tient dans le bloc et si ses axes sont monotones.

Sortie : structures_dans_les_blocs.csv, blocs_segmentes.csv
"""
import struct, csv, collections

BIN = '/home/user/edc.bin'
OUT = '/home/user/analyse_edc15c2_4hx'
BASE, TBL = 0x60000, 0x61400
d = open(BIN, 'rb').read()


def rd(ea, n=1):
    v = struct.unpack_from('<%dH' % n, d, BASE + ea - 0xE0000)
    return v[0] if n == 1 else v


def monotone(a):
    return (len(a) >= 2 and
            (all(a[i] <= a[i + 1] for i in range(len(a) - 1)) or
             all(a[i] >= a[i + 1] for i in range(len(a) - 1))))


def charge_tags():
    T = set()
    for x in csv.DictReader(open(OUT + '/annotation_datensatz.csv'), delimiter=','):
        if x.get('variable'):
            T.add(int(x['variable'], 16))
    for x in csv.DictReader(open(OUT + '/annotation_cartes_2D.csv'), delimiter=','):
        T.add(int(x['tagY'], 16)); T.add(int(x['tagX'], 16))
    for x in csv.DictReader(open(OUT + '/axes_datensatz.csv'), delimiter=';'):
        if x.get('tag'):
            T.add(int(x['tag'], 16))
    for t in (0xC3D2, 0xC3E6, 0xC42E, 0xC3EC, 0xC562, 0xC3BA, 0xC3B0,
              0xC5A8, 0xC6A2, 0xC586, 0xC3C2):
        T.add(t)
    return T


TAGS = charge_tags()


def essai(ea, limite):
    """essaie 1-D puis 2-D a l'adresse ea, borne par limite (EA de fin de bloc)"""
    if ea + 8 > limite:
        return None
    w = rd(ea)
    if w in TAGS:
        n = rd(ea + 2)
        if 2 <= n <= 48:
            sz = 4 + 4 * n
            if ea + sz <= limite:
                ax = rd(ea + 4, n)
                if monotone(ax) and ax[0] != ax[-1]:
                    return dict(kind='1D', tag=w, n=n, nY=0, nX=0, taille=sz, EA=ea)
        nY = rd(ea + 2)
        if 2 <= nY <= 48 and ea + 8 + 2 * nY + 2 <= limite:
            tx = rd(ea + 4 + 2 * nY)
            if tx in TAGS:
                nX = rd(ea + 6 + 2 * nY)
                if 2 <= nX <= 48:
                    sz = 8 + 2 * nY + 2 * nX + 2 * nY * nX
                    if ea + sz <= limite:
                        axY = rd(ea + 4, nY)
                        axX = rd(ea + 8 + 2 * nY, nX)
                        if monotone(axY) and monotone(axX):
                            return dict(kind='2D', tag=w, n=nY, nY=nY, nX=nX,
                                        tagX=tx, taille=sz, EA=ea)
    return None


def segmente(EA, taille):
    """retourne (structures, trous) pour un bloc"""
    limite = EA + taille
    st, trous, o, debut_trou = [], [], EA, None
    while o + 2 <= limite:
        r = essai(o, limite)
        if r:
            if debut_trou is not None:
                trous.append((debut_trou, o)); debut_trou = None
            st.append(r); o += r['taille']
        else:
            if debut_trou is None:
                debut_trou = o
            o += 2
    if debut_trou is not None and debut_trou < limite:
        trous.append((debut_trou, limite))
    return st, trous


def main():
    vals = {0x1400 + i: struct.unpack_from('<H', d, TBL + i)[0]
            for i in range(0, 0x61E30 - TBL, 2)}
    cibles = sorted(set(0xE0000 + v for v in vals.values()))
    taille = {}
    for k, c in enumerate(cibles):
        taille[c] = (cibles[k + 1] if k + 1 < len(cibles) else 0xEC000) - c

    lignes, resume = [], []
    for c in cibles:
        st, tr = segmente(c, taille[c])
        if len(st) > 1 or (st and st[0]['EA'] != c):
            for s in st:
                lignes.append(dict(bloc='0x%05X' % c, EA='0x%05X' % s['EA'],
                                   type=s['kind'], taille=s['taille'],
                                   tag='0x%04X' % s['tag'],
                                   tagX='0x%04X' % s['tagX'] if s['kind'] == '2D' else '',
                                   n=s['n'], nY=s['nY'], nX=s['nX']))
        resume.append(dict(bloc='0x%05X' % c, taille=taille[c], n_struct=len(st),
                           octets_struct=sum(s['taille'] for s in st),
                           octets_trou=sum(b - a for a, b in tr)))

    with open(OUT + '/structures_dans_les_blocs.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['bloc', 'EA', 'type', 'taille', 'tag', 'tagX',
                                          'n', 'nY', 'nX'], delimiter=';')
        w.writeheader(); w.writerows(lignes)
    with open(OUT + '/blocs_segmentes.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['bloc', 'taille', 'n_struct',
                                          'octets_struct', 'octets_trou'], delimiter=';')
        w.writeheader(); w.writerows(resume)

    multi = [r for r in resume if r['n_struct'] > 1]
    print('blocs analyses            : %d' % len(cibles))
    print('blocs contenant >=2 struct: %d' % len(multi))
    print('structures trouvees au total : %d' % len(lignes))
    print('  par type :', dict(collections.Counter(r['type'] for r in lignes)))
    print('octets de structures : %d' % sum(r['octets_struct'] for r in resume))
    print('octets non expliques : %d' % sum(r['octets_trou'] for r in resume))
    print('\n=== blocs a >=3 structures (les plus « charges ») ===')
    for r in sorted(multi, key=lambda r: -r['n_struct'])[:12]:
        print('  %s taille %4d -> %2d structures, %d o de trou'
              % (r['bloc'], r['taille'], r['n_struct'], r['octets_trou']))


if __name__ == '__main__':
    main()
