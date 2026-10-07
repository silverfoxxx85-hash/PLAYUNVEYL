#!/usr/bin/env python3
"""unveil Pixel — i caratteri di unveil, disegnati pixel per pixel e scritti direttamente in TrueType (senza librerie).

Due pesi:
  Bold   (5×9, aste di 2 pixel)  — titoli, pulsanti, griglia. Solo maiuscole: le minuscole mostrano le maiuscole.
  Medium (4×9, aste di 1 pixel)  — messaggio e pillole. Maiuscole e minuscole con ascendenti e discendenti.
I pixel di una lettera sono uniti; si arrotondano solo gli angoli esterni (come le caselle del gioco).

Uso:  python3 tools/pixelfont.py   →  src/fonts/unveil-bold.ttf, src/fonts/unveil-medium.ttf
"""
import os, struct, time

P = 80                     # lato del pixel in unità del carattere
UPM = 1000
ASC, DESC = 960, 240       # 9 righe di maiuscola (720) + accenti sopra; 2 righe di discendenti (160) + margine. (960-240)/2 = 360 = metà della maiuscola: lettere centrate in altezza
RAD = 0.45                 # raggio degli angoli esterni, in pixel
EPS = 4                    # sovrapposizione tra pixel vicini (niente fessure all'antialias)

# ---------------------------------------------------------------- disegni
BOLD = {
'A':".###. ##.## ##.## ##.## ##### ##.## ##.## ##.## ##.##",'B':"####. ##.## ##.## ##.## ####. ##.## ##.## ##.## ####.",
'C':".###. ##.## ##... ##... ##... ##... ##... ##.## .###.",'D':"####. ##.## ##.## ##.## ##.## ##.## ##.## ##.## ####.",
'E':"##### ##... ##... ##... ####. ##... ##... ##... #####",'F':"##### ##... ##... ##... ####. ##... ##... ##... ##...",
'G':".###. ##.## ##... ##... ##.## ##.## ##.## ##.## .####",'H':"##.## ##.## ##.## ##.## ##### ##.## ##.## ##.## ##.##",
'I':"## ## ## ## ## ## ## ## ##",'J':"...## ...## ...## ...## ...## ...## ##.## ##.## .###.",
'K':"##.## ##.## ##.## ####. ###.. ####. ##.## ##.## ##.##",'L':"##... ##... ##... ##... ##... ##... ##... ##... #####",
'M':"##...## ###.### ####### ##.#.## ##...## ##...## ##...## ##...## ##...##",'N':"##..## ###.## ###.## ###### ##.### ##.### ##..## ##..## ##..##",
'O':".###. ##.## ##.## ##.## ##.## ##.## ##.## ##.## .###.",'P':"####. ##.## ##.## ##.## ####. ##... ##... ##... ##...",
'Q':".###. ##.## ##.## ##.## ##.## ##.## ##.## ##.#. .##.#",'R':"####. ##.## ##.## ##.## ####. ###.. ##.#. ##.## ##.##",
'S':".###. ##.## ##... ###.. .###. ..### ...## ##.## .###.",'T':"###### ..##.. ..##.. ..##.. ..##.. ..##.. ..##.. ..##.. ..##..",
'U':"##.## ##.## ##.## ##.## ##.## ##.## ##.## ##.## .###.",'V':"##.## ##.## ##.## ##.## ##.## ##.## ##.## .###. ..#..",
'W':"##...## ##...## ##...## ##...## ##...## ##.#.## ####### ###.### ##...##",'X':"##.## ##.## ##.## .###. ..#.. .###. ##.## ##.## ##.##",
'Y':"##..## ##..## ##..## .####. ..##.. ..##.. ..##.. ..##.. ..##..",'Z':"##### ...## ...## ..##. .##.. .##.. ##... ##... #####",
'0':".###. ##.## ##.## ##.## ##.## ##.## ##.## ##.## .###.",'1':".##. ###. .##. .##. .##. .##. .##. .##. ####",
'2':".###. ##.## ...## ...## ..##. .##.. ##... ##... #####",'3':"####. ...## ...## ...## .###. ...## ...## ...## ####.",
'4':"##.## ##.## ##.## ##.## ##### ...## ...## ...## ...##",'5':"##### ##... ##... ####. ...## ...## ...## ##.## .###.",
'6':".###. ##... ##... ####. ##.## ##.## ##.## ##.## .###.",'7':"##### ...## ...## ..##. ..##. .##.. .##.. .##.. .##..",
'8':".###. ##.## ##.## ##.## .###. ##.## ##.## ##.## .###.",'9':".###. ##.## ##.## ##.## .#### ...## ...## ...## .###.",
'!':"## ## ## ## ## ## .. ## ##",'?':".###. ##.## ...## ..##. .##.. .##.. ..... .##.. .##..",'.':".. .. .. .. .. .. .. ## ##",
',':".. .. .. .. .. .. .. ## ## .#",':':".. .. ## ## .. .. .. ## ##",';':".. .. ## ## .. .. .. ## ## .#",
"'":"## ## .# .. .. .. .. .. ..",'"':"##.## ##.## .#..# ..... ..... ..... ..... ..... .....",'-':"... ... ... ... ### ... ... ... ...",
'/':"...## ...## ..##. ..##. .##.. .##.. ##... ##... ##...",'(':".## ##. ##. ##. ##. ##. ##. ##. .##",')':"##. .## .## .## .## .## .## .## ##.",
'+':"..... ..... ..##. ..##. ##### ..##. ..##. ..... .....",'%':"##..# ##..# ...#. ..#.. ..#.. .#... #..## #..## .....",
'«':"...... ...... ..#..# .##.## ##.##. .##.## ..#..# ...... ......",'»':"...... ...... #..#.. ##.##. .##.## ##.##. #..#.. ...... ......",
'&':".##.. ##.#. ##.#. .##.. ###.# ##.## ##.#. ##.## .##.#",'#':"..... .#.#. ##### .#.#. .#.#. ##### .#.#. ..... .....",
'@':".###. ##..# ##.## ##### ##### ##### ##... ##..# .###.",'*':"..... #.#.# .###. ##### .###. #.#.# ..... ..... .....",
' ':"... ... ... ... ... ... ... ... ...",
}
MED = {
'A':".##. #..# #..# #..# #### #..# #..# #..# #..#",'B':"###. #..# #..# #..# ###. #..# #..# #..# ###.",'C':".##. #..# #... #... #... #... #... #..# .##.",
'D':"###. #..# #..# #..# #..# #..# #..# #..# ###.",'E':"#### #... #... #... ###. #... #... #... ####",'F':"#### #... #... #... ###. #... #... #... #...",
'G':".##. #..# #... #... #.## #..# #..# #..# .###",'H':"#..# #..# #..# #..# #### #..# #..# #..# #..#",'I':"### .#. .#. .#. .#. .#. .#. .#. ###",
'J':"..## ...# ...# ...# ...# ...# ...# #..# .##.",'K':"#..# #..# #.#. ##.. ##.. #.#. #..# #..# #..#",'L':"#... #... #... #... #... #... #... #... ####",
'M':"#...# ##.## #.#.# #.#.# #...# #...# #...# #...# #...#",'N':"#..# ##.# ##.# #.## #.## #..# #..# #..# #..#",'O':".##. #..# #..# #..# #..# #..# #..# #..# .##.",
'P':"###. #..# #..# #..# ###. #... #... #... #...",'Q':".##. #..# #..# #..# #..# #..# #..# #.#. .#.#",'R':"###. #..# #..# #..# ###. #.#. #..# #..# #..#",
'S':".##. #..# #... #... .##. ...# ...# #..# .##.",'T':"### .#. .#. .#. .#. .#. .#. .#. .#.",'U':"#..# #..# #..# #..# #..# #..# #..# #..# .##.",
'V':"#..# #..# #..# #..# #..# #..# #..# .##. .##.",'W':"#...# #...# #...# #...# #...# #.#.# #.#.# ##.## #...#",'X':"#..# #..# #..# .##. .##. .##. #..# #..# #..#",
'Y':"#.# #.# #.# #.# .#. .#. .#. .#. .#.",'Z':"#### ...# ...# ..#. .#.. .#.. #... #... ####",
'a':".... .... .... .##. ...# .### #..# #..# .###",'b':"#... #... #... ###. #..# #..# #..# #..# ###.",'c':".... .... .... .##. #..# #... #... #..# .##.",
'd':"...# ...# ...# .### #..# #..# #..# #..# .###",'e':".... .... .... .##. #..# #### #... #..# .##.",'f':"..## .#.. .#.. ###. .#.. .#.. .#.. .#.. .#..",
'g':".... .... .... .### #..# #..# #..# #..# .### ...# .##.",'h':"#... #... #... ###. #..# #..# #..# #..# #..#",'i':". # . # # # # # #",
'j':".. .# .. .# .# .# .# .# .# .# #.",'k':"#... #... #... #..# #.#. ##.. ##.. #.#. #..#",'l':"#. #. #. #. #. #. #. #. .#",
'm':"..... ..... ..... ####. #.#.# #.#.# #.#.# #.#.# #.#.#",'n':".... .... .... ###. #..# #..# #..# #..# #..#",'o':".... .... .... .##. #..# #..# #..# #..# .##.",
'p':".... .... .... ###. #..# #..# #..# #..# ###. #... #...",'q':".... .... .... .### #..# #..# #..# #..# .### ...# ...#",'r':"... ... ... #.# ##. #.. #.. #.. #..",
's':".... .... .... .### #... ##.. ..## ...# ###.",'t':".#.. .#.. .#.. ###. .#.. .#.. .#.. .#.. ..##",'u':".... .... .... #..# #..# #..# #..# #..# .###",
'v':".... .... .... #..# #..# #..# #..# .##. .##.",'w':"..... ..... ..... #...# #...# #...# #.#.# #.#.# .#.#.",'x':".... .... .... #..# #..# .##. .##. #..# #..#",
'y':".... .... .... #..# #..# #..# #..# #..# .### ...# .##.",'z':".... .... .... #### ...# ..#. .#.. #... ####",
'0':".##. #..# #..# #..# #..# #..# #..# #..# .##.",'1':".#. ##. .#. .#. .#. .#. .#. .#. ###",'2':".##. #..# ...# ...# ..#. .#.. #... #... ####",
'3':"###. ...# ...# ...# .##. ...# ...# ...# ###.",'4':"#..# #..# #..# #..# #### ...# ...# ...# ...#",'5':"#### #... #... ###. ...# ...# ...# #..# .##.",
'6':".##. #... #... ###. #..# #..# #..# #..# .##.",'7':"#### ...# ...# ..#. ..#. .#.. .#.. .#.. .#..",'8':".##. #..# #..# #..# .##. #..# #..# #..# .##.",
'9':".##. #..# #..# #..# .### ...# ...# ...# .##.",
'!':"# # # # # # # . #",'?':".##. #..# ...# ..#. .#.. .#.. .... .#.. .#..",'.':". . . . . . . # #",',':".. .. .. .. .. .. .. .# .# #.",
':':". . . # # . . # #",';':".. .. .. .# .# .. .. .# .# #.","'":"# # . . . . . . .",'"':"#.# #.# ... ... ... ... ... ... ...",
'-':"... ... ... ... ### ... ... ... ...",'/':"...# ...# ..#. ..#. .#.. .#.. #... #... #...",'(':".# #. #. #. #. #. #. #. .#",')':"#. .# .# .# .# .# .# .# #.",
'+':"... ... ... .#. ### .#. ... ... ...",'%':"#..# #..# ..#. ..#. .#.. .#.. #..# #..# ....",'«':"..... ..... ..#.# .#.#. #.#.. .#.#. ..#.# ..... .....",
'»':"..... ..... #.#.. .#.#. ..#.# .#.#. #.#.. ..... .....",'&':".#.. #.#. #.#. .#.. #.#.# #..#. #..#. .##.# .....",'#':".... .#.# #### .#.# .#.# #### .#.# .... ....",
'@':".##. #..# #.## #.## #.## #.## #... #..# .##.",'*':"... #.# .#. ### .#. #.# ... ... ...",
' ':"... ... ... ... ... ... ... ... ...",
}
ALIAS = {'’': "'", '‘': "'", '“': '"', '”': '"', '–': '-', '—': '-', 'ı': 'I', '…': None}

def parse(s):
    rows = [r.replace('.', '0').replace('#', '1') for r in s.split()]
    return len(rows[0]), {(x, y) for y, r in enumerate(rows) for x, c in enumerate(r) if c == '1'}

def accented(table, base, kind, bold):
    w, px = parse(table[base]); px = set(px); c = w // 2
    if base.isupper():
        y0 = -3
        if bold: px |= ({(c - 1, y0), (c, y0), (c, y0 + 1), (c + 1, y0 + 1)} if kind == 'g' else {(c, y0), (c + 1, y0), (c - 1, y0 + 1), (c, y0 + 1)})
        else: px |= ({(c - 1, y0), (c, y0 + 1)} if kind == 'g' else {(c, y0), (c - 1, y0 + 1)})
    elif base == 'i':
        px = {(1, y) for y in range(3, 9)} | ({(0, 0), (1, 1)} if kind == 'g' else {(1, 0), (0, 1)}); w = 2
    else:
        px |= ({(c - 1, 1), (c, 2)} if kind == 'g' else {(c, 1), (c - 1, 2)})
    return w, px

ACC = {'À': ('A', 'g'), 'È': ('E', 'g'), 'É': ('E', 'a'), 'Ì': ('I', 'g'), 'Ò': ('O', 'g'), 'Ù': ('U', 'g'),
       'à': ('a', 'g'), 'è': ('e', 'g'), 'é': ('e', 'a'), 'ì': ('i', 'g'), 'ò': ('o', 'g'), 'ù': ('u', 'g'), 'í': ('i', 'a'), 'ó': ('o', 'a'), 'ú': ('u', 'a'), 'á': ('a', 'a')}

def glyph_set(bold):
    table = BOLD if bold else MED
    out = {}
    for ch, s in table.items(): out[ch] = parse(s)
    for ch, (b, k) in ACC.items():
        if bold: out[ch] = accented(table, b.upper(), k, True)
        elif b in table: out[ch] = accented(table, b, k, False)
    if bold:   # le minuscole del Bold mostrano le maiuscole
        for ch in list(out):
            if ch.isupper() and ch.lower() not in out: out[ch.lower()] = out[ch]
    for a, b in ALIAS.items():
        if b and b in out: out[a] = out[b]
    w, px = out['.']; out['…'] = (w * 3 + 2, {(x + k * (w + 1), y) for k in range(3) for (x, y) in px})
    out['·'] = (1 if not bold else 2, {(x, 4) for x in range(1 if not bold else 2)} | ({(x, 5) for x in range(2)} if bold else set()))
    return out

# ---------------------------------------------------------------- contorni
def pixel_contours(px):
    """un contorno per pixel (in senso orario), con gli angoli esterni arrotondati da curve quadratiche"""
    cs = []
    r = RAD * P
    for (x, y) in sorted(px):
        e = lambda a, b: (a, b) in px
        x0, x1 = x * P, (x + 1) * P
        y1, y0 = (9 - y) * P, (8 - y) * P          # y in alto 0 → coordinate TrueType (in su)
        if e(x - 1, y): x0 -= EPS
        if e(x + 1, y): x1 += EPS
        if e(x, y - 1): y1 += EPS
        if e(x, y + 1): y0 -= EPS
        tl = not e(x - 1, y) and not e(x, y - 1); tr = not e(x + 1, y) and not e(x, y - 1)
        br = not e(x + 1, y) and not e(x, y + 1); bl = not e(x - 1, y) and not e(x, y + 1)
        pts = []   # (x, y, on_curve) in senso orario partendo dall'angolo in alto a sinistra
        def corner(cx, cy, rnd, ax, ay, bx, by):
            if rnd: pts.extend([(cx + ax, cy + ay, 1), (cx, cy, 0), (cx + bx, cy + by, 1)])
            else: pts.append((cx, cy, 1))
        corner(x0, y1, tl, 0, -r, r, 0)       # alto-sinistra: arriva dal lato sinistro, riparte verso destra
        corner(x1, y1, tr, -r, 0, 0, -r)      # alto-destra
        corner(x1, y0, br, 0, r, -r, 0)       # basso-destra
        corner(x0, y0, bl, r, 0, 0, r)        # basso-sinistra
        cs.append([(round(a), round(b), o) for a, b, o in pts])
    return cs

def glyf_entry(contours):
    if not contours: return b''
    pts = [p for c in contours for p in c]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    out = struct.pack('>hhhhh', len(contours), min(xs), min(ys), max(xs), max(ys))
    end = -1; ends = []
    for c in contours: end += len(c); ends.append(end)
    out += struct.pack('>' + 'H' * len(ends), *ends) + struct.pack('>H', 0)
    flags = bytes((p[2] & 1) | (0x40 if i == 0 else 0) for i, p in enumerate(pts))   # coordinate a 16 bit; 0x40 = contorni sovrapposti
    out += flags
    px = py = 0; dx = b''; dy = b''
    for x, y, _ in pts: dx += struct.pack('>h', x - px); px = x
    for x, y, _ in pts: dy += struct.pack('>h', y - py); py = y
    out += dx + dy
    if len(out) % 2: out += b'\0'
    return out

# ---------------------------------------------------------------- tabelle
def checksum(b):
    b += b'\0' * ((4 - len(b) % 4) % 4)
    return sum(struct.unpack('>%dI' % (len(b) // 4), b)) & 0xFFFFFFFF

def name_table(family, style, full, ps):
    recs = [(1, family), (2, style), (3, f'unveil:{ps}'), (4, full), (5, 'Version 1.000'), (6, ps)]
    strs = b''; entries = []
    for nid, s in recs:
        for (plat, enc, lang, data) in [(3, 1, 0x409, s.encode('utf-16-be')), (1, 0, 0, s.encode('mac_roman', 'replace'))]:
            entries.append((plat, enc, lang, nid, len(data), len(strs))); strs += data
    entries.sort()
    head = struct.pack('>HHH', 0, len(entries), 6 + 12 * len(entries))
    return head + b''.join(struct.pack('>HHHHHH', *e) for e in entries) + strs

def cmap_table(cmap):
    # formato 4, segmenti di un carattere ciascuno (pochi caratteri: va benissimo)
    codes = sorted(c for c in cmap if c < 0xFFFF)
    segs = [(c, c, cmap[c]) for c in codes] + [(0xFFFF, 0xFFFF, 0)]
    n = len(segs); sr = 2 * (1 << (n.bit_length() - 1)); es = (n.bit_length() - 1); rs = 2 * n - sr
    ends = b''.join(struct.pack('>H', e) for s, e, g in segs); starts = b''.join(struct.pack('>H', s) for s, e, g in segs)
    deltas = b''.join(struct.pack('>h', ((g - s) + 0x8000) % 0x10000 - 0x8000) if s != 0xFFFF else struct.pack('>h', 1) for s, e, g in segs)
    offs = b'\0\0' * n
    sub = struct.pack('>HHHHHHH', 4, 0, 0, 2 * n, sr, es, rs) + ends + b'\0\0' + starts + deltas + offs
    sub = sub[:2] + struct.pack('>H', len(sub)) + sub[4:]
    return struct.pack('>HH', 0, 2) + struct.pack('>HHI', 0, 3, 20) + struct.pack('>HHI', 3, 1, 20) + sub

def build(bold, path):
    gs = glyph_set(bold)
    order = ['.notdef'] + sorted(gs, key=lambda c: ord(c))
    glyfs, advs, bboxes = [], [], []; maxpts = maxcont = 0
    for name in order:
        if name == '.notdef':
            cs = [[(P, 0, 1), (P, 720, 1), (4 * P, 720, 1), (4 * P, 0, 1)]]; w = 5
        else:
            w, px = gs[name]; cs = pixel_contours(px)
            cs = [[(a + P // 2, b, o) for a, b, o in c] for c in cs]   # mezzo pixel di spalla a sinistra e a destra: la lettera sta al centro del suo spazio
        glyfs.append(glyf_entry(cs)); advs.append((w + 1) * P)
        maxpts = max(maxpts, sum(len(c) for c in cs)); maxcont = max(maxcont, len(cs))
        pts = [p for c in cs for p in c]
        bboxes.append((min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)) if pts else (0, 0, 0, 0))
    loca = [0]
    for g in glyfs: loca.append(loca[-1] + len(g))
    glyf = b''.join(glyfs)
    nb = [b for b, g in zip(bboxes, glyfs) if g]
    xmin = min(b[0] for b in nb); ymin = min(b[1] for b in nb); xmax = max(b[2] for b in nb); ymax = max(b[3] for b in nb)
    weight, style = (800, 'Bold') if bold else (500, 'Medium')
    family = 'unveil Pixel'; ps = 'unveilPixel-' + style
    now = int(time.time()) + 2082844800
    head = struct.pack('>IIIIHHqqhhhhHHhhh', 0x00010000, 0x00010000, 0, 0x5F0F3CF5, 0b1011, UPM, now, now, xmin, ymin, xmax, ymax,
                       1 if bold else 0, 8, 2, 1, 0)
    hhea = struct.pack('>IhhhHhhhhhhhhhhhH', 0x00010000, ASC, -DESC, 0, max(advs), min(b[0] for b in nb), min(a - b[2] for a, b in zip(advs, bboxes) if b != (0, 0, 0, 0)),
                       xmax, 1, 0, 0, 0, 0, 0, 0, 0, len(order))
    maxp = struct.pack('>IHHHHHHHHHHHHHH', 0x00010000, len(order), maxpts, maxcont, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0)
    hmtx = b''.join(struct.pack('>Hh', a, b[0]) for a, b in zip(advs, bboxes))
    cmap = {ord(c): i for i, c in enumerate(order) if c != '.notdef'}
    os2 = struct.pack('>HhHHHhhhhhhhhhhh', 4, sum(advs) // len(advs), weight, 5, 0, 650, 700, 0, 140, 650, 700, 0, 480, 50, 300, 0)
    os2 += bytes([2, 11, 6, 6, 3, 5, 4, 2, 2, 4])   # PANOSE generico
    os2 += struct.pack('>IIII', 1, 0, 0, 0) + b'UNVL' + struct.pack('>HHH', (0x20 if bold else 0x40) | 0x80, min(cmap), max(c for c in cmap if c < 0xFFFF))
    os2 += struct.pack('>hhhHH', ASC, -DESC, 0, ASC, DESC) + struct.pack('>II', 1, 0) + struct.pack('>hhHHH', 560, 720, 0, 32, 0)
    post = struct.pack('>IIhhIIIII', 0x00030000, 0, -120, 60, 0, 0, 0, 0, 0)
    tables = {'OS/2': os2, 'cmap': cmap_table(cmap), 'glyf': glyf, 'head': head, 'hhea': hhea, 'hmtx': hmtx,
              'loca': b''.join(struct.pack('>I', o) for o in loca), 'maxp': maxp,
              'name': name_table(family, style, f'{family} {style}', ps), 'post': post}
    tags = sorted(tables); n = len(tags); sr = 16 * (1 << (n.bit_length() - 1))
    off = 12 + 16 * n; hdr = struct.pack('>IHHHH', 0x00010000, n, sr, n.bit_length() - 1, n * 16 - sr); dirs = b''; body = b''
    for t in tags:
        d = tables[t]; dirs += struct.pack('>4sIII', t.encode(), checksum(d), off + len(body), len(d))
        body += d + b'\0' * ((4 - len(d) % 4) % 4)
    font = bytearray(hdr + dirs + body)
    adj = (0xB1B0AFBA - checksum(bytes(font))) & 0xFFFFFFFF
    # posizione della tabella head per scrivere checkSumAdjustment
    pos = off
    for t in tags:
        if t == 'head': break
        pos += len(tables[t]) + (4 - len(tables[t]) % 4) % 4
    font[pos + 8:pos + 12] = struct.pack('>I', adj)
    open(path, 'wb').write(bytes(font))
    return len(order)

if __name__ == '__main__':
    root = os.path.join(os.path.dirname(__file__), '..', 'src', 'fonts')
    print('Bold:', build(True, os.path.join(root, 'unveil-bold.ttf')), 'glifi')
    print('Medium:', build(False, os.path.join(root, 'unveil-medium.ttf')), 'glifi')
