/* Typography guard.
   Prints the font size actually used by every element on every screen and
   fails loudly if the auto fitter had to shrink anything, which would mean
   the hierarchy is no longer uniform. Run it after any copy change:
     NODE_PATH=/opt/node22/lib/node_modules node check.js            */
const { chromium } = require('playwright');
const path = require('path');
(async()=>{
const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://' + path.join(__dirname, 'video.html'));
await p.waitForFunction('window.ready===true');
const out=await p.evaluate(()=>{
  const rows=Array.from(document.querySelectorAll('.scene')).map(sec=>{
    const ls=Array.from(sec.querySelectorAll('.line:not(.sp)'));
    const byCls={};
    ls.forEach(e=>{const k=e.className.replace('line ','').trim();
      (byCls[k]=byCls[k]||new Set()).add(Math.round(parseFloat(getComputedStyle(e).fontSize)));});
    const nav=sec.querySelectorAll('.blk')[0], cre=sec.querySelectorAll('.blk')[1];
    return {id:sec.dataset.id,
      sizes:Object.entries(byCls).map(([k,v])=>k+':'+[...v].join('/')).join('  '),
      nav:[nav.offsetTop, nav.offsetTop+nav.offsetHeight],
      cre: cre?[cre.offsetTop, cre.offsetTop+cre.offsetHeight]:null};
  });
  return {rows, warn: window.FITWARN, total: window.TOTAL, TYPE: window.TYPE};
});
console.log('TYPE', JSON.stringify(out.TYPE));
out.rows.forEach(r=>console.log(r.id.padEnd(11), String(r.nav).padEnd(11),
  String(r.cre||'').padEnd(12), r.sizes));
console.log('\ntotal', out.total.toFixed(1)+'s');
console.log(out.warn.length ? 'AUTO SHRINK: '+out.warn.join(' | ') : 'AUTO SHRINK: none — scale is uniform');
await b.close();
process.exit(out.warn.length ? 1 : 0);})();
