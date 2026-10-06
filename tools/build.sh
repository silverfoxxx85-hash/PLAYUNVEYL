#!/bin/sh
# Compone index.html: app + generatore + icone animate + caratteri incorporati (un solo file)
cd "$(dirname "$0")/.." && python3 - <<'PY'
import base64, glob, json, os
a = open('src/app.html').read(); g = open('src/gen.js').read()
def face(fam, f, w):
    b = base64.b64encode(open('src/fonts/' + f, 'rb').read()).decode()
    return "@font-face{font-family:'%s';src:url(data:font/woff;base64,%s) format('woff');font-weight:%s;font-style:normal;font-display:swap}" % (fam, b, w)
fonts = face('Unbounded', 'unbounded.woff', '500 800') + '\n' + face('DM Sans', 'dmsans.woff', '400 700')
# src/art/ico-NOME.svg -> ICONS.NOME (le genera tools/lottie2svg.py dai file in src/art/lottie)
icons = {os.path.basename(f)[4:-4]: open(f).read() for f in sorted(glob.glob('src/art/ico-*.svg'))}
icons_js = 'const ICONS = ' + json.dumps(icons, ensure_ascii=False) + ';'
open('index.html', 'w').write(a.replace('/*__FONTS__*/', fonts).replace('/*__GEN__*/', g).replace('/*__ICONS__*/', icons_js))
PY
