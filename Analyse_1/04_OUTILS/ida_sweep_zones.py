# ida_sweep_zones.py — IDAPython (IDA 7.4 -> 9.x)
# EDC15C2 / 0 281 010 877 — force le désassemblage des zones restées en `db`.
# À lancer depuis IDA : File > Script file…  (ou Alt+F7)
# IMPORTANT : travailler sur une COPIE de la base (.idb / .i64).

import ida_bytes, ida_ua, ida_funcs, ida_idp, idc, ida_kernwin

# ---------------------------------------------------------------------------
# 1) Entrées atteintes par la table de pointeurs du Datensatz (0xE0008, 151 entrées)
#    (adresse EA, préfixe de 2 octets rencontré juste avant l'entrée)
# ---------------------------------------------------------------------------
ENTRIES = [
    0x090082, 0x09445C, 0x097F8C, 0x097FD8, 0x099544, 0x099C3C, 0x099FB4,
    0x09A47E, 0x09EC8A, 0x0A31FA, 0x0A6EB4, 0x0AE4EE, 0x0AE63A, 0x0BFDD6,
    0x0BFEF6, 0x0C3248,
]

# ---------------------------------------------------------------------------
# 2) Zones « db » à rebalayer : (début, taille, étiquette)
#    Priorité 1 = interruptions, 2 = gros blocs, 3 = le reste, 0 = NE PAS toucher
# ---------------------------------------------------------------------------
ZONES = [
    # -- priorité 1 : interruptions / dispatch
    (0x09400A, 0x00060, "ISR principal (entrée réelle, pas 0x94002)", 1),
    (0x094108, 0x00100, "handlers (3 reti dans le secteur)", 1),
    (0x094232, 0x0008A, "suite cluster interruption", 1),
    # -- priorité 2 : gros blocs
    (0x099C32, 0x003BC, "bloc code 956 o (2 cibles table)", 2),
    (0x099FF2, 0x008C6, "bloc code 2246 o (cible 0x9A47E)", 2),
    (0x0FC8CC, 0x007E0, "bloc 2016 o dans le secteur BOOT", 2),
    (0x09F900, 0x00306, "bloc code 774 o", 2),
    (0x09DA4E, 0x0026A, "bloc code 618 o", 2),
    (0x09EC18, 0x0022A, "bloc code 554 o (cible 0x9EC8A)", 2),
    (0x0BF096, 0x001D2, "bloc 466 o", 2),
    (0x0FC21A, 0x001D2, "bloc 466 o (secteur BOOT)", 2),
    # -- priorité 3 : blocs moyens / petits
    (0x0A6EA4, 0x001C0, "bloc 448 o (cible 0xA6EB4)", 3),
    (0x0AE4E2, 0x0019C, "bloc 412 o (cibles 0xAE4EE/0xAE63A)", 3),
    (0x0C322A, 0x0016E, "bloc 366 o (cible 0xC3248)", 3),
    (0x0BFDC2, 0x0013E, "bloc 318 o (cibles 0xBFDD6/0xBFEF6)", 3),
    (0x08FFB8, 0x0017A, "bloc 378 o (cible 0x90082)", 3),
    (0x088CBA, 0x00136, "bloc 310 o", 3),
    (0x0CF5D8, 0x00134, "bloc 308 o", 3),
    (0x09031C, 0x00112, "bloc 274 o", 3),
    (0x0D1050, 0x000FE, "bloc 254 o", 3),
    (0x0A31EE, 0x000D8, "bloc 216 o (cible 0xA31FA)", 3),
    (0x0FEB22, 0x000DE, "bloc 222 o (fin du code diag, avant zone effacée)", 3),
    (0x09017A, 0x0009C, "bloc 156 o", 3),
    (0x094454, 0x000E0, "bloc 224 o (cible 0x9445C)", 3),
    (0x09953C, 0x00072, "bloc 114 o (cible 0x99544)", 3),
    (0x097F88, 0x00070, "bloc 112 o (cibles 0x97F8C/0x97FD8)", 3),
    (0x090E64, 0x0006E, "bloc 110 o", 3),
    (0x0C49FC, 0x00050, "bloc 80 o", 3),
    (0x0B7F64, 0x00048, "bloc 72 o", 3),
    (0x0D0072, 0x00040, "bloc 64 o", 3),
    # -- NE PAS TOUCHER
    (0x0CDD5E, 0x00292, "TABLE (motif CC 00 CC 00 DB 00) — PAS du code", 0),
    (0x090F32, 0x030CE, "76 % de remplissage — ne rien forcer", 0),
]

log = []


def sweep(ea, size, tag=""):
    """U (undefine) puis C (make code) sur [ea, ea+size), puis P (create function)."""
    ida_bytes.del_items(ea, ida_bytes.DELIT_SIMPLE, size)
    cur, n = ea, 0
    while cur < ea + size:
        if not ida_ua.create_insn(cur):
            break
        n += 1
        nxt = idc.get_item_end(cur)
        if nxt <= cur:
            break
        cur = nxt
    fn = ida_funcs.get_func(ea)
    if fn is None:
        ok = ida_funcs.add_func(ea, cur)
        fn = ida_funcs.get_func(ea)
        created = bool(ok)
    else:
        created = False
    if tag:
        old = idc.get_cmt(ea, 0)
        idc.set_cmt(ea, (old + " | " if old else "") + "sweep: " + tag, 0)
    log.append((ea, size, n, cur, fn is not None, created))
    return n, cur


def run(prio=(1, 2, 3)):
    ida_kernwin.msg("=== ida_sweep_zones: début ===\n")
    # a) les entrées de la table des 151 pointeurs (longueur estimée : jusqu'au prochain rets)
    for ea in ENTRIES:
        sweep(ea, 0x200, "entrée table 151")
    # b) les zones
    for start, size, label, p in ZONES:
        if p in prio and size:
            sweep(start, size, label)
    ida_kernwin.msg("=== bilan ===\n")
    for ea, size, n, cur, isfn, created in log:
        ida_kernwin.msg(
            "%06X  %4d octets  %3d instructions  fin=%06X  fonction=%s%s\n"
            % (ea, size, n, cur, "oui" if isfn else "NON", " (créée)" if created else "")
        )
    ida_kernwin.msg("=== fin : vérifier visuellement, puis Ctrl+W / sauvegarde ===\n")


if __name__ == "__main__":
    run()
