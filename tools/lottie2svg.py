"""Converte l'animazione Lottie dell'icona in un SVG animato con SMIL (nessuna libreria).
Supporta solo ciò che usa questo file: forme con morph, tratti, rettangoli, trim path, matte alfa invertito."""
import json, sys
SRC, OUT = sys.argv[1], sys.argv[2]
d = json.load(open(SRC))
FR, OP = d['fr'], d['op']
DUR = OP / FR
INK, ACC = '#130f16', '#ffffff'           # tratti scuri, accenti (turchese originale) in bianco
def color(c):
    r, g, b = c[:3]
    return ACC if (r < .5 and g > .5) else INK
def fmt(x): return ('%.2f' % x).rstrip('0').rstrip('.')
def pathd(sh):
    v, i, o, c = sh['v'], sh['i'], sh['o'], sh.get('c', False)
    if not v: return 'M0 0'
    s = 'M%s %s' % (fmt(v[0][0]), fmt(v[0][1]))
    n = len(v); segs = n if c else n - 1
    for k in range(segs):
        a, b = v[k], v[(k + 1) % n]
        s += 'C%s %s %s %s %s %s' % (fmt(a[0] + o[k][0]), fmt(a[1] + o[k][1]), fmt(b[0] + i[(k + 1) % n][0]), fmt(b[1] + i[(k + 1) % n][1]), fmt(b[0]), fmt(b[1]))
    return s + ('Z' if c else '')
def anim(attr, kfs, conv, offset=0):
    """keyframe Lottie -> <animate> con keyTimes e keySplines (tempi in fotogrammi della composizione)"""
    pts = []
    for k in kfs:
        if 's' in k: pts.append((k['t'] + offset, conv(k['s']), k))
    vals, times, splines = [], [], []
    sp_prev = '0 0 1 1'
    t0 = pts[0][0]
    if t0 > 0: vals.append(pts[0][1]); times.append(0)
    for idx, (t, v, k) in enumerate(pts):
        if times and t / OP == times[-1] and vals: vals[-1] = v; continue
        if times: splines.append(sp_prev)
        vals.append(v); times.append(t / OP)
        o, nxt = k.get('o'), (pts[idx + 1][2] if idx + 1 < len(pts) else None)
        if o and nxt and nxt.get('i'):
            ox, oy = (o['x'][0] if isinstance(o['x'], list) else o['x']), (o['y'][0] if isinstance(o['y'], list) else o['y'])
            ix, iy = (nxt['i']['x'][0] if isinstance(nxt['i']['x'], list) else nxt['i']['x']), (nxt['i']['y'][0] if isinstance(nxt['i']['y'], list) else nxt['i']['y'])
            sp_prev = '%s %s %s %s' % (fmt(ox), fmt(oy), fmt(ix), fmt(iy))
        else: sp_prev = '0 0 1 1'
    if times[-1] < 1: splines.append('0 0 1 1'); vals.append(vals[-1]); times.append(1)
    if times[0] > 0: pass
    return '<animate attributeName="%s" dur="%ss" repeatCount="indefinite" calcMode="spline" values="%s" keyTimes="%s" keySplines="%s"/>' % (
        attr, fmt(DUR), ';'.join(vals), ';'.join(fmt(t) for t in times), ';'.join(splines))
def ltr(ks):
    p, a, r, s = ks['p']['k'], ks['a']['k'], ks.get('r', {'k': 0})['k'], ks['s']['k']
    t = 'translate(%s %s)' % (fmt(p[0]), fmt(p[1]))
    if r: t += ' rotate(%s)' % fmt(r)
    if s[0] != 100 or s[1] != 100: t += ' scale(%s %s)' % (fmt(s[0] / 100), fmt(s[1] / 100))
    if a[0] or a[1]: t += ' translate(%s %s)' % (fmt(-a[0]), fmt(-a[1]))
    return t
def shapes(items, offset, fill_override=None):
    out = []
    trim = next((x for x in items if x['ty'] == 'tm'), None)
    for g in items:
        if g['ty'] != 'gr': continue
        it = g['it']; tr = next(x for x in it if x['ty'] == 'tr')
        st = next((x for x in it if x['ty'] == 'st'), None); fl = next((x for x in it if x['ty'] == 'fl'), None)
        if st and st['o']['k'] == 0: continue                      # tratto invisibile (rettangolo guida)
        if fill_override: paint = 'fill="%s"' % fill_override
        elif st: paint = 'fill="none" stroke="%s" stroke-width="%s" stroke-linecap="%s" stroke-linejoin="round"' % (color(st['c']['k']), fmt(st['w']['k']), {1: 'butt', 2: 'round', 3: 'square'}[st['lc']])
        else: paint = 'fill="%s"' % color(fl['c']['k'])
        for sh in it:
            if sh['ty'] == 'sh':
                ks = sh['ks']
                extra = ''
                if trim and not fill_override:
                    # trim path: start e fine con stroke-dasharray su pathLength 100 (fine-inizio = parte visibile)
                    extra = ' pathLength="100"'
                if ks['a']:
                    el = '<path d="%s" %s%s>%s' % (pathd(ks['k'][0]['s'][0]), paint, extra, anim('d', ks['k'], lambda s: pathd(s[0]), offset))
                else:
                    el = '<path d="%s" %s%s>' % (pathd(ks['k']), paint, extra)
                if trim and not fill_override: el += trim_anim(trim, offset)
                out.append('<g transform="%s">%s</path></g>' % (ltr(tr), el))
    return ''.join(out)
def trim_anim(tm, offset):
    # parte visibile = [e, s] con s che va 100->0 e e 100->0 (m=1): dash = s-e, offset = -e
    def sample(prop, t):
        ks = prop['k']
        if t <= ks[0]['t'] + offset: return ks[0]['s'][0]
        if t >= ks[-1]['t'] + offset: return ks[-1]['s'][0]
        a, b = ks[0], ks[-1]; u = (t - a['t'] - offset) / (b['t'] - a['t'])
        # easing (.42,0,.58,1) approssimato con smoothstep
        u = u * u * (3 - 2 * u); return a['s'][0] + (b['s'][0] - a['s'][0]) * u
    frames = list(range(0, OP + 1, 2))
    da, do, op = [], [], []
    for f in frames:
        s, e = sample(tm['s'], f), sample(tm['e'], f)
        lo, hi = min(s, e), max(s, e); L = max(0.0001, hi - lo)
        da.append('%s %s' % (fmt(L), fmt(200))); do.append(fmt(-lo)); op.append('1' if L > .5 else '0')   # niente puntini delle estremità tonde
    kt = ';'.join(fmt(f / OP) for f in frames)
    return ('<animate attributeName="stroke-dasharray" dur="%ss" repeatCount="indefinite" values="%s" keyTimes="%s"/>' % (fmt(DUR), ';'.join(da), kt) +
            '<animate attributeName="stroke-dashoffset" dur="%ss" repeatCount="indefinite" values="%s" keyTimes="%s"/>' % (fmt(DUR), ';'.join(do), kt) +
            '<animate attributeName="stroke-opacity" calcMode="discrete" dur="%ss" repeatCount="indefinite" values="%s" keyTimes="%s"/>' % (fmt(DUR), ';'.join(op), kt))
L = {x['ind']: x for x in d['layers']}
null = L[5]
body = []
mask = L[3]
mid = 'icoMask'
mask_svg = '<mask id="%s" maskUnits="userSpaceOnUse" x="-50" y="-50" width="600" height="600"><rect x="-50" y="-50" width="600" height="600" fill="#fff"/><g transform="%s"><g transform="%s">%s</g></g></mask>' % (
    mid, ltr(null['ks']), ltr(mask['ks']), shapes(mask['shapes'], mask.get('st', 0), '#000'))
for ind in (4, 2, 1):   # dal basso verso l'alto: persona (con matte), mano, linee
    ly = L[ind]
    inner = shapes(ly['shapes'], 0)
    g = '<g transform="%s"><g transform="%s"%s>%s</g></g>' % (ltr(null['ks']), ltr(ly['ks']), '', inner)
    if ind == 4: g = '<g mask="url(#%s)">%s</g>' % (mid, g)
    body.append(g)
svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500"><defs>%s</defs>%s</svg>' % (mask_svg, ''.join(body))
open(OUT, 'w').write(svg); print(len(svg))
