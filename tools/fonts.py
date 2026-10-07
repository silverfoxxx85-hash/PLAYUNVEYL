#!/usr/bin/env python3
"""Prepara i caratteri da incorporare (src/fonts/originali -> src/fonts/*.woff).
- Figtree (variabile, 300-900) per tutti i testi; Silkscreen Bold per titoli e griglia, Silkscreen Regular per le parole da trovare nella frase. Entrambi SIL OFL 1.1.
- Si tengono solo i caratteri latini che servono (italiano, punteggiatura tipografica, euro e frecce): file molto piu' leggeri.
- Silkscreen: ascendente portato a 875 (era 1030) cosi' (875-250)/2 = 312 = meta' dell'altezza delle maiuscole (625, 5 pixel da 125):
  nelle caselle le lettere stanno esattamente al centro in altezza.
Uso: python3 tools/fonts.py   (poi tools/build.sh)"""
import os
from fontTools.ttLib import TTFont
from fontTools import subset
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
UNI = [*range(0x20, 0x7F), *range(0xA0, 0x100), 0x131, 0x152, 0x153, *range(0x2013, 0x2015), *range(0x2018, 0x201F), 0x2022, 0x2026, 0x2039, 0x203A, 0x20AC, 0x2190, 0x2192, 0x21BB]
def make(src, out, fix=None):
    f = TTFont('src/fonts/originali/' + src)
    o = subset.Options(); o.layout_features = ['*']; o.flavor = 'woff'; o.name_IDs = ['*']; o.notdef_outline = True
    s = subset.Subsetter(o); s.populate(unicodes=UNI); s.subset(f)
    if fix: fix(f)
    f.flavor = 'woff'; f.save('src/fonts/' + out); print(out, os.path.getsize('src/fonts/' + out), 'byte')
def center_caps(f):
    asc = 875; f['hhea'].ascent = asc; f['OS/2'].sTypoAscender = asc; f['OS/2'].usWinAscent = asc
    f['OS/2'].fsSelection |= 0x80   # USE_TYPO_METRICS
make('Figtree-VariableFont_wght.ttf', 'figtree.woff')
make('Silkscreen-Bold.ttf', 'silkscreen-bold.woff', center_caps)
make('Silkscreen-Regular.ttf', 'silkscreen-regular.woff', center_caps)   # parole del gioco nella frase
