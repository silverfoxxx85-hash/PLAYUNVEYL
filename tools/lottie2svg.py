"""Converte un'animazione Lottie (icona a tratti) in un SVG animato con SMIL, senza librerie.
Gestisce: livelli forma e precomposizioni, genitori, trasformazioni animate (posizione/rotazione),
forme con morph, rettangoli, tratti/riempimenti, gruppi annidati, trim path, matte alfa (normale e invertito).
Uso: python3 lottie2svg.py animazione.json uscita.svg"""
import json, sys
SRC, OUT = sys.argv[1], sys.argv[2]
d = json.load(open(SRC))
FR, OP = d['fr'], d['op']
DUR = OP / FR
INK, ACC = '#130f16', '#ffffff'          # tratti scuri; il turchese dell'originale diventa bianco
ASSETS = {a['id']: a for a in d.get('assets', [])}
uid = [0]
def nid(p): uid[0] += 1; return '%s%d' % (p, uid[0])
def fmt(x): return ('%.2f' % x).rstrip('0').rstrip('.') if abs(x) > 1e-9 else '0'
def color(c):
    r, g, b = c[:3]
    return ACC if (r < .5 and g > .5) else INK
def first(x): return x[0] if isinstance(x, list) else x
def splines_of(kfs):
    sp = []
    for a, b in zip(kfs, kfs[1:]):
        o, i = a.get('o'), a.get('i')
        if a.get('h') == 1: sp.append(None)
        elif o and i: sp.append('%s %s %s %s' % (fmt(first(o['x'])), fmt(first(o['y'])), fmt(first(i['x'])), fmt(first(i['y']))))
        else: sp.append('0 0 1 1')
    return sp
def smil(attr, kfs, conv, tag='animate', extra=''):
    """keyframe -> animazione SMIL con keyTimes/keySplines, su tutta la durata della composizione"""
    pts = [k for k in kfs if 's' in k]
    vals = [conv(k['s']) for k in pts]
    # l'ultimo keyframe spesso non ha 's' ma solo 't' (fine del segmento precedente): in quel caso vale 'e' del penultimo
    if len(pts) < len(kfs) and 'e' in pts[-1]:
        vals.append(conv(pts[-1]['e'])); pts = pts + [kfs[len(pts)]]
    times = [k['t'] / OP for k in pts]
    sp = splines_of(pts)
    if times[0] > 0: vals.insert(0, vals[0]); times.insert(0, 0); sp.insert(0, '0 0 1 1')
    if times[-1] < 1: vals.append(vals[-1]); times.append(1); sp.append('0 0 1 1')
    sp = [s or '0 0 1 1' for s in sp]
    return '<%s attributeName="%s" %sbegin="indefinite" dur="%ss" repeatCount="indefinite" calcMode="spline" values="%s" keyTimes="%s" keySplines="%s"/>' % (
        tag, attr, extra, fmt(DUR), ';'.join(vals), ';'.join(fmt(t) for t in times), ';'.join(sp))
def pathd(sh):
    v, i, o, c = sh['v'], sh['i'], sh['o'], sh.get('c', False)
    if not v: return 'M0 0'
    s = 'M%s %s' % (fmt(v[0][0]), fmt(v[0][1]))
    n = len(v)
    for k in range(n if c else n - 1):
        a, b = v[k], v[(k + 1) % n]
        s += 'C%s %s %s %s %s %s' % (fmt(a[0] + o[k][0]), fmt(a[1] + o[k][1]), fmt(b[0] + i[(k + 1) % n][0]), fmt(b[1] + i[(k + 1) % n][1]), fmt(b[0]), fmt(b[1]))
    return s + ('Z' if c else '')
def xform(ks, inner):
    """trasformazione di livello o gruppo: translate(p) rotate(r) scale(s) translate(-a), animabili"""
    p, a, r, s = ks.get('p', {'k': [0, 0]}), ks.get('a', {'k': [0, 0]}), ks.get('r', {'k': 0}), ks.get('s', {'k': [100, 100]})
    out = inner
    ak = a['k']
    if ak[0] or ak[1]: out = '<g transform="translate(%s %s)">%s</g>' % (fmt(-ak[0]), fmt(-ak[1]), out)
    sk = s['k']
    if not s.get('a') and (sk[0] != 100 or sk[1] != 100): out = '<g transform="scale(%s %s)">%s</g>' % (fmt(sk[0] / 100), fmt(sk[1] / 100), out)
    if r.get('a'): out = '<g transform="rotate(%s)">%s%s</g>' % (fmt(first(r['k'][0]['s'])), smil('transform', r['k'], lambda v: fmt(first(v)), 'animateTransform', 'type="rotate" '), out)
    elif r['k']: out = '<g transform="rotate(%s)">%s</g>' % (fmt(r['k']), out)
    if p.get('a'): out = '<g transform="translate(%s %s)">%s%s</g>' % (fmt(p['k'][0]['s'][0]), fmt(p['k'][0]['s'][1]), smil('transform', p['k'], lambda v: '%s %s' % (fmt(v[0]), fmt(v[1])), 'animateTransform', 'type="translate" '), out)
    elif p['k'][0] or p['k'][1]: out = '<g transform="translate(%s %s)">%s</g>' % (fmt(p['k'][0]), fmt(p['k'][1]), out)
    return out
def trim_anims(tm):
    def sample(prop, t):
        ks = prop['k'] if prop.get('a') else [{'t': 0, 's': [prop['k']]}]
        if t <= ks[0]['t']: return first(ks[0]['s'])
        if t >= ks[-1]['t']: return first(ks[-1]['s'])
        for a, b in zip(ks, ks[1:]):
            if a['t'] <= t <= b['t']:
                u = (t - a['t']) / (b['t'] - a['t']); u = u * u * (3 - 2 * u)
                return first(a['s']) + (first(b['s']) - first(a['s'])) * u
    frames = list(range(0, OP + 1, 2)); da, do, op = [], [], []
    for f in frames:
        s, e = sample(tm['s'], f), sample(tm['e'], f)
        lo, hi = min(s, e), max(s, e); L = max(.0001, hi - lo)
        da.append('%s 200' % fmt(L)); do.append(fmt(-lo)); op.append('1' if L > .5 else '0')
    kt = ';'.join(fmt(f / OP) for f in frames)
    trim_anims.base = ' stroke-dasharray="%s" stroke-dashoffset="%s" stroke-opacity="%s"' % (da[0], do[0], op[0])
    A = lambda attr, vals, extra='': '<animate attributeName="%s" %sbegin="indefinite" dur="%ss" repeatCount="indefinite" values="%s" keyTimes="%s"/>' % (attr, extra, fmt(DUR), ';'.join(vals), kt)
    return A('stroke-dasharray', da) + A('stroke-dashoffset', do) + A('stroke-opacity', op, 'calcMode="discrete" ')
def paint_attr(p, matte):
    if p['ty'] == 'st':
        w = p['w']['k']
        col = '#000' if matte else color(p['c']['k'])
        return 'fill="none" stroke="%s" stroke-width="%s" stroke-linecap="%s" stroke-linejoin="round"' % (col, fmt(w), {1: 'butt', 2: 'round', 3: 'square'}[p.get('lc', 2)])
    return 'fill="%s"' % ('#000' if matte else color(p['c']['k']))
def render_items(items, paints, trim, matte):
    """un livello di elementi (come in un gruppo Lottie): le pitture valgono per le forme dello stesso livello e di quelli annidati"""
    own = [x for x in items if x['ty'] in ('st', 'fl') and not x.get('hd') and (x.get('o', {'k': 100})['k'] if not x.get('o', {}).get('a') else 100) > 0]
    paints = own + paints if own else paints
    trim = next((x for x in items if x['ty'] == 'tm'), trim)
    out = ''
    for it in items:
        if it.get('hd'): continue
        if it['ty'] == 'gr':
            inner = render_items(it['it'], paints, trim, matte)
            tr = next((x for x in it['it'] if x['ty'] == 'tr'), None)
            out += xform(tr, inner) if tr else inner
        elif it['ty'] in ('sh', 'rc'):
            if not paints: continue
            for pnt in paints:
                attrs = paint_attr(pnt, matte)
                tr_extra = ' pathLength="100"' if (trim and pnt['ty'] == 'st') else ''
                if it['ty'] == 'sh':
                    ks = it['ks']
                    if ks.get('a'): el = '<path d="%s" %s%s>%s' % (pathd(ks['k'][0]['s'][0]), attrs, tr_extra, smil('d', ks['k'], lambda s: pathd(s[0])))
                    else: el = '<path d="%s" %s%s>' % (pathd(ks['k']), attrs, tr_extra)
                    if tr_extra:
                        anims = trim_anims(trim); el = el.replace(tr_extra + '>', tr_extra + trim_anims.base + '>', 1) + anims
                    out += el + '</path>'
                else:
                    sz, ps, rr = it['s']['k'], it['p']['k'], it['r']['k']
                    out += '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" %s/>' % (fmt(ps[0] - sz[0] / 2), fmt(ps[1] - sz[1] / 2), fmt(sz[0]), fmt(sz[1]), fmt(rr), attrs)
    return out
def layer_content(L, layers, matte):
    if L['ty'] == 4: return render_items(L['shapes'], [], None, matte)
    if L['ty'] == 0: return render_layers(ASSETS[L['refId']]['layers'], matte)
    return ''
def with_parents(L, byind, inner):
    out = xform(L['ks'], inner)
    while L.get('parent'):
        L = byind[L['parent']]; out = xform(L['ks'], out)
    return out
def render_layers(layers, matte=False):
    byind = {x['ind']: x for x in layers}
    out = []
    for idx, L in enumerate(layers):
        if L.get('td') or L['ty'] == 3 or L.get('hd'): continue
        if L['ks'].get('o', {}).get('k', 100) == 0 and not L['ks']['o'].get('a') and L['ty'] != 3: continue
        g = with_parents(L, byind, layer_content(L, layers, matte))
        if L.get('tt') and not matte:
            M = layers[idx - 1]; mid = nid('m')
            inv = L['tt'] == 2
            mg = with_parents(M, byind, layer_content(M, layers, True))
            if not inv: mg = mg.replace('#000', '#fff')
            out.append('<mask id="%s" maskUnits="userSpaceOnUse" x="-100" y="-100" width="700" height="700"><rect x="-100" y="-100" width="700" height="700" fill="%s"/>%s</mask><g mask="url(#%s)">%s</g>' % (
                mid, '#fff' if inv else '#000', mg, mid, g))
        else: out.append(g)
    return ''.join(reversed(out))   # in Lottie il primo livello è quello in alto
svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d">%s</svg>' % (d['w'], d['h'], render_layers(d['layers']))
open(OUT, 'w').write(svg); print(len(svg))
