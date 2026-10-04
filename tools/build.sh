#!/bin/sh
cd "$(dirname "$0")/.." && python3 -c "
a=open('src/app.html').read(); g=open('src/gen.js').read()
open('index.html','w').write(a.replace('/*__GEN__*/', g))"
