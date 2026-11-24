#!/usr/bin/env python3
"""
Recherche systematique des TABLES OUBLIEES du Datensatz EDC15C2.

Quatre verifications independantes :

  1. COUVERTURE   — quels octets de 0xE1000..0xEC000 ne sont atteints par AUCUN handle ?
  2. DUPLICATION  — le Datensatz est-il stocke deux fois (0xE0000 et 0xF0000) ?
  3. TYPOLOGIE    — les blocs sans en-tete 1-D : quelle structure interne ?
  4. CARTES PLATES — les grands blocs sans en-tete sont-ils des cartes 2-D sans axes ?

Sorties CSV dans analyse_edc15c2_4hx/.
"""
import csv, struct, collections, os

BIN   = '/home/user/edc.bin'
OUT   = '/home/user/analyse_edc15c2_4hx'
BASE  = 0x60000          # offset fichier de l'EA 0xE0000
TBL   = 0x61400          # offset fichier de la table de pointeurs (EA 0xE1400)

d = open(BIN, 'rb').read()

def W(ea, n=1):
    return struct.unpack_from('<%dH' % n, d, BASE + ea - 0xE0000)

def raw(ea, n):
    o = BASE + ea - 0xE0000
    return d[o:o + n]

# ---------------------------------------------------------------- table de pointeurs
vals = {0x1400 + i: struct.unpack_from('<H', d, TBL + i)[0]
        for i in range(0, 0x61E30 - TBL, 2)}
CIBLES = sorted(set(0xE0000 + v for v in vals.values()))


# ================================================================ 1. COUVERTURE
def normalise(ea):
    """les CSV d'axes contiennent les DEUX exemplaires : ramener a l'exemplaire E"""
    return ea - 0x10000 if ea >= 0xF0000 else ea


def intervalles():
    iv = []
    for x in csv.DictReader(open(OUT + '/annotation_datensatz.csv'), delimiter=','):
        try:
            iv.append((normalise(int(x['EA'], 16)), int(x['taille_bloc'])))
        except Exception:
            pass
    for x in csv.DictReader(open(OUT + '/axes_datensatz.csv'), delimiter=';'):
        a = normalise(int(x['EA'], 16))
        iv.append((a, 4 + 2 * int(x['nb_points'])))
    iv.sort()
    merged = []
    for a, t in iv:
        b = a + t
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return merged


def couverture(lo=0xE1000, hi=0xEC000):
    merged = intervalles()
    trous, cur = [], lo
    for a, b in merged:
        if b <= lo or a >= hi:
            continue
        a, b = max(a, lo), min(b, hi)
        if a > cur:
            trous.append((cur, a))
        cur = max(cur, b)
    if cur < hi:
        trous.append((cur, hi))
    return merged, trous


def classe_contenu(x):
    if not x:
        return 'vide'
    if all(v == 0xC3 for v in x):
        return 'remplissage 0xC3'
    if all(v == 0 for v in x):
        return 'zeros'
    if all(v == 0xFF for v in x):
        return '0xFF'
    w = struct.unpack('<%dH' % (len(x) // 2), x[:len(x) // 2 * 2])
    if len(w) >= 3 and all(w[i] < w[i + 1] for i in range(len(w) - 1)):
        return 'suite croissante'
    if len(w) >= 3 and all(w[i] > w[i + 1] for i in range(len(w) - 1)):
        return 'suite decroissante'
    return 'donnees'


# ================================================================ 2. DUPLICATION
def duplication():
    diffs = [i for i in range(0xC000)
             if d[BASE + i] != d[BASE + 0x10000 + i]]
    runs = []
    for i in diffs:
        if runs and i == runs[-1][1] + 1:
            runs[-1][1] = i
        else:
            runs.append([i, i])
    return diffs, runs


# ================================================================ 3. TYPOLOGIE
def typologie():
    tags = set()
    for x in csv.DictReader(open(OUT + '/annotation_datensatz.csv'), delimiter=','):
        if x['verdict'] == 'TAILLE EXACTE' and x['variable']:
            tags.add(int(x['variable'], 16))
    for x in csv.DictReader(open(OUT + '/annotation_cartes_2D.csv'), delimiter=','):
        tags.add(int(x['tagY'], 16))
        tags.add(int(x['tagX'], 16))

    rows = [x for x in csv.DictReader(open(OUT + '/annotation_datensatz.csv'), delimiter=',')
            if x['verdict'] == 'pas d en-tete 1-D']
    out = []
    for x in rows:
        ea, S = int(x['EA'], 16), int(x['taille_bloc'])
        nw = S // 2
        k = 'NON CLASSE'
        if S == 2:
            k = 'scalaire 1 mot'
        elif S == 4:
            k = 'paire de mots'
        elif S == 6:
            k = 'triplet (3 mots)'
        elif S >= 6 and (S - 4) % 2 == 0:
            n = (S - 4) // 2
            w0, wn = W(ea, 2)
            if wn == n and n >= 2:
                k = 'axe (tag connu)' if w0 in tags else 'axe (tag inconnu)'
        if k == 'NON CLASSE' and S >= 4 and (S - 2) % 2 == 0:
            n = (S - 2) // 2
            if W(ea)[0] == n and n >= 2:
                k = 'liste nue (n puis valeurs)'
        if k == 'NON CLASSE' and nw >= 3:
            w = W(ea, nw)
            if all(w[i] < w[i + 1] for i in range(nw - 1)):
                k = 'suite croissante'
            elif all(w[i] > w[i + 1] for i in range(nw - 1)):
                k = 'suite decroissante'
        out.append(dict(handle=x['handle'], EA='0x%05X' % ea, taille=S, type=k))
    return out


# ================================================================ 4. CARTES PLATES
def lissage(w, nx):
    ny = len(w) // nx
    s = c = 0
    for r in range(ny):
        for i in range(r * nx, r * nx + nx - 1):
            s += abs(w[i + 1] - w[i]); c += 1
    for r in range(ny - 1):
        for i in range(r * nx, r * nx + nx):
            s += abs(w[i + nx] - w[i]); c += 1
    return s / c


def cartes_plates(taille_min=128):
    rows = [x for x in csv.DictReader(open(OUT + '/annotation_datensatz.csv'), delimiter=',')
            if x['verdict'] == 'pas d en-tete 1-D']
    out = []
    for x in rows:
        ea, S = int(x['EA'], 16), int(x['taille_bloc'])
        nw = S // 2
        if S < taille_min or nw % 2 or nw < 64:
            continue
        w = W(ea, nw)
        if max(w) >= 0xFF00:            # sentinelles 0xFFxx : pas une grille pure
            continue
        best = (9e9, 0)
        for nx in range(6, min(41, nw // 6 + 1)):
            if nw % nx or nw // nx < 6:
                continue
            v = lissage(w, nx)
            if v < best[0]:
                best = (v, nx)
        if best[1]:
            v = 'grille plausible'
            if max(w) == min(w):
                v = 'uniforme (bloc rempli)'
            elif best[0] > 500:
                v = 'suspect (trame douteuse)'
            out.append(dict(EA='0x%05X' % ea, taille=S, mots=nw,
                            nX=best[1], nY=nw // best[1],
                            lissage='%.1f' % best[0],
                            min=min(w), max=max(w), verdict=v))
    out.sort(key=lambda r: -r['taille'])
    return out


# ================================================================ MAIN
if __name__ == '__main__':
    merged, trous = couverture()
    cov = sum(b - a for a, b in merged if not (b <= 0xE1000 or a >= 0xEC000))
    print('=== 1. COUVERTURE 0xE1000..0xEC000 ===')
    print('couverts %d o (%.1f %%), %d trou(s)' % (cov, 100 * cov / 0xB000, len(trous)))
    with open(OUT + '/etat_couverture.csv', 'w', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['EA_debut', 'EA_fin', 'taille', 'contenu', 'classe'])
        for a, b in trous:
            w.writerow(['0x%05X' % a, '0x%05X' % b, b - a,
                        raw(a, min(b - a, 16)).hex(' '), classe_contenu(raw(a, b - a))])
            print('  trou 0x%05X-0x%05X %5d o  %s' % (a, b, b - a, classe_contenu(raw(a, b - a))))

    diffs, runs = duplication()
    print('\n=== 2. DUPLICATION 0xE0000..0xEBFFF vs 0xF0000..0xFBFFF ===')
    print('octets differents : %d, en %d plage(s)' % (len(diffs), len(runs)))
    with open(OUT + '/duplication_datensatz.csv', 'w', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['EA_exemplaire_E', 'EA_exemplaire_F', 'taille', 'valeur_E', 'valeur_F'])
        for a, b in runs:
            w.writerow(['0x%05X' % (0xE0000 + a), '0x%05X' % (0xF0000 + a), b - a + 1,
                        raw(0xE0000 + a, b - a + 1).hex(' '),
                        raw(0xF0000 + a, b - a + 1).hex(' ')])
            print('  0x%05X  E=%s  F=%s' % (0xE0000 + a,
                  raw(0xE0000 + a, b - a + 1).hex(' '), raw(0xF0000 + a, b - a + 1).hex(' ')))

    typ = typologie()
    print('\n=== 3. TYPOLOGIE DES BLOCS SANS EN-TETE 1-D (%d) ===' % len(typ))
    c = collections.Counter(r['type'] for r in typ)
    o = collections.Counter()
    for r in typ:
        o[r['type']] += r['taille']
    with open(OUT + '/typologie_blocs_sans_entete.csv', 'w', newline='') as f:
        csv.DictWriter(f, fieldnames=['handle', 'EA', 'taille', 'type'], delimiter=';').writerows(typ)
    for k, v in c.most_common():
        print('  %-28s %4d blocs  %6d o' % (k, v, o[k]))

    cp = cartes_plates()
    with open(OUT + '/cartes_plates_sans_axes.csv', 'w', newline='') as f:
        fld = ['EA', 'taille', 'mots', 'nX', 'nY', 'lissage', 'min', 'max', 'verdict']
        w = csv.DictWriter(f, fieldnames=fld, delimiter=';')
        w.writeheader(); w.writerows(cp)
    print('\n=== 4. CARTES PLATES SANS AXES (%d) ===' % len(cp))
    for r in cp:
        print('  %s %4d o %3d mots  %2d x %-3d lissage %7s  %5d..%-5d  %s'
              % (r['EA'], r['taille'], r['mots'], r['nX'], r['nY'], r['lissage'], r['min'], r['max'], r['verdict']))
