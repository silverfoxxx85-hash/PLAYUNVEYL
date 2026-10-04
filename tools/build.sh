#!/bin/sh
# Compone index.html: app + generatore + caratteri incorporati (un solo file)
cd "$(dirname "$0")/.." && python3 - <<'PY'
import base64
a = open('src/app.html').read(); g = open('src/gen.js').read()
def face(fam, f, w):
    b = base64.b64encode(open('src/fonts/' + f, 'rb').read()).decode()
    return "@font-face{font-family:'%s';src:url(data:font/woff;base64,%s) format('woff');font-weight:%s;font-style:normal;font-display:swap}" % (fam, b, w)
fonts = face('Unbounded', 'unbounded.woff', '500 800') + '\n' + face('DM Sans', 'dmsans.woff', '400 700')
open('index.html', 'w').write(a.replace('/*__FONTS__*/', fonts).replace('/*__GEN__*/', g))
PY
