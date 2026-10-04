const G=require('../src/gen.js');
const D=[[-1,-1],[0,-1],[1,-1],[-1,0],[1,0],[-1,1],[0,1],[1,1]];
function allPaths(L,cols,rows,w){const out=[];const used=new Uint8Array(L.length);const path=[];
 function dfs(i,k){if(L[i]!==w[k])return;used[i]=1;path.push(i);if(k===w.length-1)out.push([...path]);else{const x=i%cols,y=(i/cols)|0;for(const[dx,dy]of D){const nx=x+dx,ny=y+dy;if(nx<0||ny<0||nx>=cols||ny>=rows)continue;const ni=ny*cols+nx;if(!used[ni])dfs(ni,k+1);}}used[i]=0;path.pop();}
 for(let i=0;i<L.length;i++)dfs(i,0);return out;}
const rev=s=>[...s].reverse().join('');
const dict=(process.argv[2]||"amore casa sole mare luna notte giorno stella cuore sorriso viaggio regalo festa torta candela musica ballo bacio abbraccio sempre insieme domani stasera cena vino fiori rose sogno anima vita tempo fortuna gioia pace luce cielo vento").split(' ');
const STEP=+(process.argv[3]||1), TR=+(process.argv[4]||40);
let tot=0,nulls=0,bump=0,bad=0,times=[],BN={},skipped=0;
for(let n=10;n<=50;n+=STEP)for(let trial=0;trial<TR;trial++){
 let x=n*1000+trial;const rnd=()=>((x=Math.imul(x^x>>>15,2246822507)+12345|0)>>>0)/4294967296;
 let words=[],s=0; while(s<n){let w=dict[Math.floor(rnd()*dict.length)]; if(s+w.length>n){const rem=n-s; if(rem<3){words.pop(); s=words.join('').length; continue;} w=w.slice(0,rem);} words.push(w); s+=w.length;}
 const msg=words.join(' ');const segs=G.tokenize(msg);const hide=segs.map((q,i)=>q.type==='w'&&q.hideable?i:-1).filter(i=>i>=0);
 if(G.countLetters(segs,hide)!==n)continue; if(G.conflicts(segs,hide).length){skipped++;continue;}
 for(const diff of [3]){tot++;const t1=Date.now();const r=G.generate({msg,hide,seed:trial*13+diff,diff});times.push(Date.now()-t1);
  if(!r){nulls++;BN[n]=(BN[n]||0)+1;continue;} if(r.tier>G.tierFor(n))bump++;
  for(const w of r.words){ if(w.cells.map(c=>r.letters[c]).join('')!==w.norm) bad++;
    const okSets=new Set(r.words.filter(o=>o.norm===w.norm||o.norm===rev(w.norm)).map(o=>G.keyOf(o.cells)));
    let isBad=false; for(const target of [w.norm,rev(w.norm)]) for(const p of allPaths(r.letters,r.cols,r.rows,target)) if(!okSets.has(G.keyOf(p))) isBad=true;
    if(isBad) bad++;
  }}}
times.sort((a,b)=>a-b);
console.log(JSON.stringify(BN));
console.log({tot,skipped,nulls,bump,badWords:bad,p50:times[times.length>>1],p95:times[Math.floor(times.length*.95)],max:times[times.length-1]});
