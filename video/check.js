/* QA gate. Run before every export:
     NODE_PATH=/opt/node22/lib/node_modules node check.js
   Fails if any line overflows its column, if a frame uses more than three
   sizes or two weights, if any readable text drops below 30px, or if
   anything lands inside a Reels interface zone. */
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 'video.html'));
  await p.waitForFunction('window.ready === true');

  const out = await p.evaluate(() => {
    const L = window.LAYOUT;
    const rows = Array.from(document.querySelectorAll('.scene')).map(sec => {
      const els = Array.from(sec.querySelectorAll('.line:not(.sp), .face span'));
      const sizes = new Set(), weights = new Set();
      let minSize = 999;
      els.forEach(e => {
        const cs = getComputedStyle(e);
        const s = Math.round(parseFloat(cs.fontSize));
        sizes.add(s); weights.add(cs.fontWeight); minSize = Math.min(minSize, s);
      });
      return { id: sec.dataset.id, sizes: [...sizes].sort((a, c) => c - a),
               weights: [...weights].sort(), minSize };
    });
    return { rows, warn: window.FITWARN, bounds: window.BOUNDS,
             total: window.TOTAL, TYPE: window.TYPE, L };
  });

  const L = out.L;
  const fail = [];
  console.log('TYPE ' + JSON.stringify(out.TYPE));
  console.log('column ' + (L.padRight - L.padLeft) + 'px   safe y ' + L.safeTop + ' to ' + L.safeBottom + '\n');

  out.rows.forEach((r, i) => {
    const bd = out.bounds[i];
    if (r.sizes.length > 3) fail.push(r.id + ': ' + r.sizes.length + ' sizes ' + r.sizes);
    if (r.weights.length > 2) fail.push(r.id + ': ' + r.weights.length + ' weights ' + r.weights);
    if (r.minSize < 30) fail.push(r.id + ': text at ' + r.minSize + 'px');
    if (bd.nav[0] < L.safeTop) fail.push(r.id + ': navy top ' + bd.nav[0]);
    const bot = bd.cream ? bd.cream[1] : bd.nav[1];
    if (bot > L.safeBottom) fail.push(r.id + ': content bottom ' + bot);
    console.log(r.id.padEnd(8) +
      ' nav ' + String(bd.nav).padEnd(11) +
      ' cream ' + String(bd.cream || '-').padEnd(12) +
      ' panel ' + String(bd.ch).padEnd(5) +
      ' sizes ' + String(r.sizes).padEnd(16) + ' weights ' + r.weights);
  });

  out.warn.forEach(w => fail.push(w));
  console.log('\nduration ' + out.total.toFixed(1) + 's  (target 48 to 55)');
  if (out.total < 48 || out.total > 55) fail.push('duration ' + out.total.toFixed(1) + 's outside 48 to 55');

  console.log(fail.length ? '\nFAIL\n  ' + fail.join('\n  ') : '\nPASS  all QA checks clear');
  await b.close();
  process.exit(fail.length ? 1 : 0);
})();
