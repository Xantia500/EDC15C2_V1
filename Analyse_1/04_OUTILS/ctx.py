#!/usr/bin/env python3
"""Outils de navigation dans clean.asm (listing IDA du 0 281 010 877).

Usage:
  python3 ctx.py sub <ligne> ...        # sous-programme englobant
  python3 ctx.py var <nom> ...          # toutes les references + sous-prog englobant
  python3 ctx.py show <ligne> <n>       # n lignes autour
  python3 ctx.py ea <EA_hex>            # ligne du listing correspondant a une adresse EA
  python3 ctx.py map                    # table des sous-programmes (debut, fin, taille)
"""
import re, sys, bisect

ASM = "/home/user/clean.asm"

def load():
    with open(ASM, "r", errors="replace") as f:
        return f.read().splitlines()

def subs(lines):
    out = []
    for i, l in enumerate(lines, 1):
        m = re.match(r"^(sub_[0-9A-Fa-f]+|[a-zA-Z_][\w]*):\s*(;.*)?$", l)
        if m and (l.strip().startswith("sub_") or l.startswith("loc_")):
            out.append((i, m.group(1)))
    return out

def enclosing(lines, ln):
    if not hasattr(enclosing, "_c"):
        enclosing._c = [s for s in subs(lines) if s[1].startswith("sub_")]
    s = enclosing._c
    starts = [x[0] for x in s]
    k = bisect.bisect_right(starts, ln) - 1
    if k < 0:
        return None, None
    end = starts[k+1] if k+1 < len(s) else len(lines)
    return s[k], end

def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    cmd = sys.argv[1]
    lines = load()
    if cmd == "sub":
        for a in sys.argv[2:]:
            ln = int(a)
            r = enclosing(lines, ln)
            if not r[0]: print("?"); continue
            (st, name), end = r
            print(f"ligne {ln} -> {name} (lignes {st}-{end}, {end-st} lignes)")
    elif cmd == "var":
        pat = re.compile(r"\b(%s)\b" % "|".join(re.escape(v) for v in sys.argv[2:]))
        for i, l in enumerate(lines, 1):
            if pat.search(l) and not l.strip().startswith(";"):
                r = enclosing(lines, i)
                name = r[0][1] if r[0] else "?"
                print(f"{i:7d}  {name:<22} {l.strip()}")
    elif cmd == "show":
        ln = int(sys.argv[2]); n = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        r = enclosing(lines, ln)
        (st, name), end = r if r[0] else ((ln,"?"), ln)
        print(f"### {name} lignes {st}-{end}")
        for i in range(max(1, ln-n), min(len(lines), ln+n)+1):
            print(f"{i:7d}  {lines[i-1]}")
    elif cmd == "ea":
        ea = int(sys.argv[2], 16)
        pat = re.compile(r"^%s:" % re.escape(f"{ea:05X}"))
        for i, l in enumerate(lines, 1):
            if pat.match(l.strip()):
                print(f"{i}: {l}"); break
        else:
            print("introuvable")
    elif cmd == "map":
        s = subs(lines)
        names = [x for x in s if x[1].startswith("sub_")]
        for k, (st, name) in enumerate(names):
            end = names[k+1][0] if k+1 < len(names) else len(lines)
            print(f"{name:<22} {st:7d}-{end:7d}  {end-st:5d}")
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
