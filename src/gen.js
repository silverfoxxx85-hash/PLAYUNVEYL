/* ============================================================
   UNVEIL WORDS — Generatore griglia (puro, deterministico)
   Stesso input (msg, hide, seed, diff, versione) => stessa griglia.
   NON modificare il comportamento senza aumentare GEN_VERSION.
   ============================================================ */
const UnveilGen = (() => {
  const GEN_VERSION = 2;
  const MIN_LETTERS = 10;
  const MAX_LETTERS = 50;
  const MAX_CHARS = 140;
  // cornice 3:4, riempimento max ~80%
  const TIERS = [
    { cols: 4, rows: 5, max: 15 },
    { cols: 5, rows: 7, max: 27 },
    { cols: 6, rows: 8, max: 38 },
    { cols: 7, rows: 9, max: 50 },
  ];
  // parole funzionali tenute visibili di default (≥3 lettere)
  const STOP = new Set(('che per con una uno del dei dal nel sul gli non sei hai era ero ' +
    'alla alle allo agli dalla dalle dallo dagli nella nelle nello negli sulla sulle sullo sugli ' +
    'della delle dello degli dai nei sui tra fra come anche piu sono cui chi gia poi mai ' +
    'the and you for are').split(' '));
  // frequenze lettere italiano (approssimate, per il riempimento)
  const IT_FREQ = 'AAAAAAAAAAAEEEEEEEEEEEIIIIIIIIIIOOOOOOOOONNNNNNNLLLLLLRRRRRRRTTTTTTTSSSSSSCCCCCDDDDPPPUUUMMMVVGGHFBZQ';
  const DIRS = [[-1,-1],[0,-1],[1,-1],[-1,0],[1,0],[-1,1],[0,1],[1,1]];

  function mulberry32(a) {
    return function () {
      a |= 0; a = a + 0x6D2B79F5 | 0;
      let t = Math.imul(a ^ a >>> 15, 1 | a);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  function hash(...nums) {
    let h = 2166136261 >>> 0;
    for (const n of nums) { h ^= (n >>> 0); h = Math.imul(h, 16777619) >>> 0; h ^= h >>> 13; }
    return h >>> 0;
  }
  function normalize(s) {
    return s.normalize('NFD').replace(/[̀-ͯ]/g, '').toUpperCase();
  }

  /* Spezza il messaggio in segmenti: parole (lettere) e separatori (tutto il resto).
     "l'amore," => [w:"l"] [p:"'"] [w:"amore"] [p:","] */
  function tokenize(msg) {
    const segs = [];
    const re = /[\p{L}\p{M}]+|[^\p{L}\p{M}]+/gu;
    let m;
    while ((m = re.exec(msg)) !== null) {
      const text = m[0];
      if (/^[\p{L}\p{M}]/u.test(text)) {
        const norm = normalize(text);
        const hideable = norm.length >= 3 && /^[A-Z]+$/.test(norm);
        segs.push({ type: 'w', text, norm, hideable });
      } else {
        segs.push({ type: 'p', text });
      }
    }
    return segs;
  }

  /* Selezione automatica: tutte le parole nascondibili tranne le funzionali;
     se si superano MAX_LETTERS si scoprono prima le più corte. */
  function defaultHidden(segs) {
    let idx = [];
    segs.forEach((s, i) => {
      if (s.type === 'w' && s.hideable && !STOP.has(s.norm.toLowerCase())) idx.push(i);
    });
    const drop0 = new Set(conflicts(segs, idx).map(([short]) => short));
    idx = idx.filter(i => !drop0.has(i));
    let total = idx.reduce((a, i) => a + segs[i].norm.length, 0);
    if (total > MAX_LETTERS) {
      const byLen = [...idx].sort((a, b) => segs[a].norm.length - segs[b].norm.length || b - a);
      const drop = new Set();
      for (const i of byLen) {
        if (total <= MAX_LETTERS) break;
        drop.add(i); total -= segs[i].norm.length;
      }
      idx = idx.filter(i => !drop.has(i));
    }
    return idx;
  }

  /* Una parola contenuta in un'altra (anche al contrario) si potrebbe sempre comporre
     sulle caselle della più lunga: le due non possono essere nascoste insieme.
     Ritorna le coppie [corta, lunga] di indici in conflitto. */
  function conflicts(segs, hide) {
    const out = []; const h = [...hide];
    for (const a of h) for (const b of h) {
      const A = segs[a].norm, B = segs[b].norm;
      if (a === b || A.length >= B.length) continue;
      if (B.includes(A) || B.includes([...A].reverse().join(''))) out.push([a, b]);
    }
    return out;
  }

  /* Stima della difficoltà (diff 3 = percorsi tortuosi senza lettere esca):
     dipende dalla taglia della griglia, cioè dalle lettere da trovare. */
  const LEVELS = [
    { name: 'Facile', minutes: '1 minuto', hint: 20, tip: 'Perfetta anche per chi non gioca mai.' },
    { name: 'Media', minutes: '2 minuti', hint: 30, tip: 'Una bella sfida, senza esagerare.' },
    { name: 'Impegnativa', minutes: '3-4 minuti', hint: 40, tip: 'Lascia visibile qualche parola per renderla più facile.' },
    { name: 'Sfida', minutes: '5 minuti o più', hint: 50, tip: 'Per veri appassionati: lascia visibile qualche parola per alleggerirla.' }
  ];
  function estimate(nLetters) {
    const ti = tierFor(nLetters);
    if (ti < 0) return null;
    return { level: ti, ...LEVELS[ti], cols: TIERS[ti].cols, rows: TIERS[ti].rows };
  }

  function countLetters(segs, hide) {
    return hide.reduce((a, i) => a + (segs[i] ? segs[i].norm.length : 0), 0);
  }
  function tierFor(n) {
    const i = TIERS.findIndex(t => n <= t.max);
    return i < 0 ? -1 : i;
  }

  /* Piazza le parole come percorsi in 8 direzioni senza sovrapposizioni.
     diff 0 = percorsi dritti, 1 = liberi, 2 = tortuosi */
  function placeAll(cols, rows, lens, rnd, diff, budget) {
    const N = cols * rows;
    const g = new Int16Array(N).fill(-1);
    let steps = 0;
    const free = (x, y) => x >= 0 && y >= 0 && x < cols && y < rows && g[y * cols + x] < 0;
    const deg = (x, y) => { let d = 0; for (const [dx, dy] of DIRS) if (free(x + dx, y + dy)) d++; return d; };
    const paths = lens.map(() => []);

    function word(i, x, y, k, pdx, pdy) {
      if (++steps > budget) return false;
      g[y * cols + x] = i; paths[i].push(y * cols + x);
      if (k === lens[i] - 1) {
        if (placeWord(i + 1)) return true;
      } else {
        const cand = [];
        for (const [dx, dy] of DIRS) {
          const nx = x + dx, ny = y + dy;
          if (!free(nx, ny)) continue;
          const turn = k > 0 && (dx !== pdx || dy !== pdy);
          const diag = dx !== 0 && dy !== 0;
          let score = deg(nx, ny) + rnd() * 1.5;
          if (diff === 0) score += (turn ? 3 : 0) + (diag ? 0.6 : 0);
          else if (diff >= 2) score += (turn ? 0 : 1.6) + (diag ? 0 : 0.5);
          cand.push([score, nx, ny, dx, dy]);
        }
        cand.sort((a, b) => a[0] - b[0]);
        for (const [, nx, ny, dx, dy] of cand) {
          if (word(i, nx, ny, k + 1, dx, dy)) return true;
          if (steps > budget) break;
        }
      }
      g[y * cols + x] = -1; paths[i].pop();
      return false;
    }
    function placeWord(i) {
      if (i === lens.length) return true;
      const starts = [];
      for (let y = 0; y < rows; y++) for (let x = 0; x < cols; x++)
        if (free(x, y)) starts.push([deg(x, y) + rnd() * 2.5, x, y]);
      starts.sort((a, b) => a[0] - b[0]);
      for (const [, x, y] of starts.slice(0, 12)) {
        if (word(i, x, y, 0, 0, 0)) return true;
        if (steps > budget) return false;
      }
      return false;
    }
    return placeWord(0) ? paths : null;
  }

  /* Piazza una singola parola sulle caselle libere (owner < 0). */
  function placeOne(cols, rows, owner, len, rnd, diff) {
    const free = (x, y) => x >= 0 && y >= 0 && x < cols && y < rows && owner[y * cols + x] < 0;
    const used = new Uint8Array(cols * rows); const path = []; let steps = 0;
    function dfs(x, y) {
      if (++steps > 4000) return false;
      const i = y * cols + x; used[i] = 1; path.push(i);
      if (path.length === len) return true;
      const cand = [];
      for (const [dx, dy] of DIRS) {
        const nx = x + dx, ny = y + dy;
        if (free(nx, ny) && !used[ny * cols + nx]) cand.push([rnd(), nx, ny]);
      }
      cand.sort((a, b) => a[0] - b[0]);
      for (const [, nx, ny] of cand) if (dfs(nx, ny)) return true;
      used[i] = 0; path.pop(); return false;
    }
    const starts = [];
    for (let y = 0; y < rows; y++) for (let x = 0; x < cols; x++) if (free(x, y)) starts.push([rnd(), x, y]);
    starts.sort((a, b) => a[0] - b[0]);
    for (const [, x, y] of starts) { if (dfs(x, y)) return [...path]; if (steps > 4000) break; }
    return null;
  }

  /* Trova tutti i percorsi che compongono `w` (si ferma a `limit`). */
  function findPaths(letters, cols, rows, w, limit, accept) {
    const out = [];
    const used = new Uint8Array(cols * rows);
    const path = [];
    function dfs(idx, k) {
      if (out.length >= limit) return;
      if (letters[idx] !== w[k]) return;
      used[idx] = 1; path.push(idx);
      if (k === w.length - 1) { if (!accept || accept(path)) out.push([...path]); }
      else {
        const x = idx % cols, y = (idx / cols) | 0;
        for (const [dx, dy] of DIRS) {
          const nx = x + dx, ny = y + dy;
          if (nx < 0 || ny < 0 || nx >= cols || ny >= rows) continue;
          const ni = ny * cols + nx;
          if (!used[ni]) dfs(ni, k + 1);
        }
      }
      used[idx] = 0; path.pop();
    }
    for (let i = 0; i < letters.length && out.length < limit; i++) dfs(i, 0);
    return out;
  }
  const keyOf = cells => [...cells].sort((a, b) => a - b).join(',');

  /* Entry point.
     opts: { msg, hide:[indici segmenti], seed, diff:0|1|2 }
     ritorna { version, cols, rows, letters:[], words:[{seg, norm, text, cells}], filler:[] } o null */
  function generate({ msg, hide, seed, diff }) {
    const segs = tokenize(msg);
    const hidden = (hide || []).filter(i => segs[i] && segs[i].type === 'w' && segs[i].hideable);
    const n = countLetters(segs, hidden);
    const t0 = tierFor(n);
    if (n === 0 || t0 < 0 || conflicts(segs, hidden).length) return null;
    // ordine di piazzamento: più lunghe prima (stabile)
    const order = hidden.map((seg, k) => ({ seg, k, norm: segs[seg].norm }))
      .sort((a, b) => b.norm.length - a.norm.length || a.k - b.k);
    const lens = order.map(o => o.norm.length);

    for (let ti = t0; ti < TIERS.length; ti++) {
      const { cols, rows } = TIERS[ti];
      for (let attempt = 0; attempt < 40; attempt++) {
        const rnd = mulberry32(hash(seed, ti, attempt, GEN_VERSION));
        const paths = placeAll(cols, rows, lens, rnd, diff, 25000);
        if (!paths) continue;

        const N = cols * rows;
        const letters = new Array(N).fill(null);
        const words = order.map((o, j) => {
          paths[j].forEach((c, k) => { letters[c] = o.norm[k]; });
          return { seg: o.seg, norm: o.norm, text: segs[o.seg].text, cells: paths[j] };
        });
        const pool = diff === 2 ? order.map(o => o.norm).join('') : IT_FREQ;
        const owner = new Int16Array(N).fill(-1);
        words.forEach((w, j) => w.cells.forEach(c => { owner[c] = j; }));
        for (let i = 0; i < N; i++) if (owner[i] < 0) letters[i] = pool[Math.floor(rnd() * pool.length)];

        // Garanzia di unicità: ogni parola deve poter essere composta SOLO sulle sue caselle
        // (in entrambi i versi: findPaths(w) trova anche i percorsi letti al contrario,
        // perché sono lo stesso insieme di caselle percorso all'indietro).
        // Riparazioni, dalla più leggera: cambiare una lettera di riempimento sul percorso
        // abusivo; invertire il verso di una parola coinvolta; spostare una parola coinvolta.
        const isPal = s => s === [...s].reverse().join('');
        let clean = false;
        for (let it = 0; it < 500; it++) {
          const valid = {};
          for (const w of words) (valid[w.norm] = valid[w.norm] || new Set()).add(keyOf(w.cells));
          let bad = null, badWord = null;
          for (const w of Object.keys(valid)) {
            const p = findPaths(letters, cols, rows, w, 1, p => !valid[w].has(keyOf(p)))[0];
            if (p) { bad = p; badWord = w; break; }
          }
          if (!bad) { clean = true; break; }
          const fix = bad.filter(i => owner[i] < 0);
          if (fix.length) {
            const cell = fix[Math.floor(rnd() * fix.length)];
            let allowed = [...pool].filter(ch => !badWord.includes(ch));
            if (!allowed.length) allowed = [...IT_FREQ].filter(ch => !badWord.includes(ch));
            letters[cell] = allowed[Math.floor(rnd() * allowed.length)];
            continue;
          }
          const involved = [...new Set(bad.map(c => owner[c]))];
          const j = involved[Math.floor(rnd() * involved.length)];
          const w = words[j];
          if (!isPal(w.norm) && rnd() < 0.5) { // inverti il verso
            w.cells.reverse(); w.cells.forEach((c, k) => { letters[c] = w.norm[k]; });
            continue;
          }
          // sposta la parola in un altro punto libero (o sulle sue stesse caselle, con altra forma)
          w.cells.forEach(c => { owner[c] = -1; });
          const np = placeOne(cols, rows, owner, w.norm.length, rnd, diff);
          if (np) {
            w.cells.forEach(c => { letters[c] = pool[Math.floor(rnd() * pool.length)]; });
            w.cells = np;
          }
          w.cells.forEach((c, k) => { owner[c] = j; letters[c] = w.norm[k]; });
        }
        if (!clean) continue; // ancora ambiguo: si riprova con un altro piazzamento
        const filler = [];
        for (let i = 0; i < N; i++) if (owner[i] < 0) filler.push(i);
        const best = [...letters];
        words.sort((a, b) => a.seg - b.seg); // ordine del messaggio
        return { version: GEN_VERSION, cols, rows, letters: best, words, filler, tier: ti };
      }
    }
    return null;
  }

  return { GEN_VERSION, MIN_LETTERS, MAX_LETTERS, MAX_CHARS, TIERS, tokenize, defaultHidden,
           countLetters, tierFor, generate, conflicts, estimate, LEVELS, normalize, keyOf };
})();
if (typeof module !== 'undefined') module.exports = UnveilGen;
