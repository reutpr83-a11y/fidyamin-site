/* Animated caption renderer.

   The tint follows the spoken word: one plate per word, the word being said
   in colour, the rest white. That is how the delivered cuts read and what the
   user asked to have back.

   Two things make it affordable. The plates cover only the caption band
   rather than the whole frame, and the scrim is baked into every one of
   them, so the film takes a single overlay instead of one per caption. The
   earlier version stacked 34 full frame layers and ran at 1.5 frames a
   second.

   Reads captions.json entries with a "wt" array, one [start,end] per word.
   Writes out/caps/w####.png, a scrim only plate for the gaps, and
   out/caps/track.txt, a concat list with durations covering the whole film.

   Run: node captions-anim.js <film-duration-seconds>
*/
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');

const DIR = __dirname, OUT = path.join(DIR, 'out', 'caps');
const W = 1080, BAND_TOP = 1360, BAND_H = 400;   // 1360..1760 of a 1920 frame

/* Larger than the static pass: measured against the delivered cut, whose
   caption caps run 61px tall where 68px type gave 54. */
const STYLE = {
  plain:    { size: 82, weight: 600, align: 'center', lineHeight: 1.20 },
  emphasis: { size: 96, weight: 800, align: 'right',  lineHeight: 1.14, rule: true }
};
const SPEC = {
  color: '#ffffff',
  highlight: '#58b0d8',      // sampled from the delivered cut
  lastBaseline: 1620 - BAND_TOP,
  padRight: 880, ruleX: 912,
  scrimFrom: 1380 - BAND_TOP, scrimTo: 1660 - BAND_TOP, scrimAlpha: parseFloat(process.env.SCRIM_ALPHA || '0.66')
};

const font = fs.readFileSync(path.join(DIR, 'fonts', 'Heebo.ttf')).toString('base64');
const page = (body, css) => `<!doctype html><meta charset="utf-8"><style>
@font-face{font-family:H;src:url(data:font/ttf;base64,${font}) format('truetype');font-weight:100 900}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:${W}px;height:${BAND_H}px;overflow:hidden;background:transparent;
  font-family:H,sans-serif;-webkit-font-smoothing:antialiased}
#scrim{position:absolute;left:0;right:0;top:${SPEC.scrimFrom}px;height:${BAND_H - SPEC.scrimFrom}px;
  background:linear-gradient(to bottom,rgba(11,43,68,0) 0%,
    rgba(11,43,68,${SPEC.scrimAlpha}) ${((SPEC.scrimTo - SPEC.scrimFrom) / (BAND_H - SPEC.scrimFrom) * 100).toFixed(1)}%,
    rgba(11,43,68,${SPEC.scrimAlpha}) 100%)}
${css}</style><div id="scrim"></div>${body}`;

(async () => {
  const total = parseFloat(process.argv[2] || '84.733');
  const caps = JSON.parse(fs.readFileSync(path.join(DIR, 'captions.json'), 'utf8'));
  fs.mkdirSync(OUT, { recursive: true });
  fs.readdirSync(OUT).filter(f => /^w\d+\.png$|^gap\.png$/.test(f))
    .forEach(f => fs.unlinkSync(path.join(OUT, f)));

  const b = await chromium.launch({ args: ['--force-color-profile=srgb', '--disable-lcd-text'] });
  const p = await b.newPage({ viewport: { width: W, height: BAND_H }, deviceScaleFactor: 1 });

  await p.setContent(page('', ''));
  await p.screenshot({ path: path.join(OUT, 'gap.png'), omitBackground: true });

  const esc = s => s.replace(/[&<>]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[ch]));
  const track = [];                       // {file, dur}
  let clock = 0, n = 0;

  for (const c of caps) {
    const st = STYLE[c.style || 'plain'];
    const lines = String(c.text).split('\n').map(l => l.split(' '));
    const flat = lines.flat();
    const lh = st.size * st.lineHeight;
    const top = SPEC.lastBaseline - lh * lines.length + (lh - st.size) / 2;
    const box = st.align === 'right'
      ? `right:${W - SPEC.padRight}px;width:${SPEC.padRight - 90}px;text-align:right`
      : `left:0;right:0;text-align:center`;
    const rule = st.rule
      ? `<div style="position:absolute;left:${SPEC.ruleX}px;top:${Math.round(top) - 8}px;
           width:6px;height:${Math.round(lh * lines.length) + 16}px;background:#fff;border-radius:3px"></div>`
      : '';

    for (let k = 0; k < flat.length; k++) {
      const [ws, we] = c.wt[k];
      if (ws > clock + 0.001) {
        track.push({ file: 'gap.png', dur: +(ws - clock).toFixed(3) });
        clock = ws;
      }
      let i = 0;
      const html = lines.map(ln => '<div class="l">' +
        ln.map(word => {
          const cur = i++ === k;
          return cur ? `<b class="hi">${esc(word)}</b>` : esc(word);
        }).join(' ') + '</div>').join('');

      await p.setContent(page(rule + `<div id="c">${html}</div>`,
        `#c{position:absolute;top:${Math.round(top)}px;${box};direction:rtl}
         .l{font-size:${st.size}px;font-weight:${st.weight};color:${SPEC.color};
            line-height:${st.lineHeight};letter-spacing:-.008em;
            text-shadow:0 2px 14px rgba(11,43,68,.60)}
         .hi{color:${SPEC.highlight};font-weight:inherit}`));
      await p.evaluate(() => document.fonts.ready);
      const f = 'w' + String(n++).padStart(4, '0') + '.png';
      await p.screenshot({ path: path.join(OUT, f), omitBackground: true });
      track.push({ file: f, dur: +(we - ws).toFixed(3) });
      clock = we;
    }
  }
  if (clock < total) track.push({ file: 'gap.png', dur: +(total - clock).toFixed(3) });

  /* the concat demuxer repeats the last entry without a trailing duration,
     so the final plate is listed twice */
  let out = '';
  for (const t of track) out += `file '${t.file}'\nduration ${t.dur}\n`;
  out += `file '${track[track.length - 1].file}'\n`;
  fs.writeFileSync(path.join(OUT, 'track.txt'), out);

  console.log(`${n} word plates, ${track.length} track entries, covering ${clock.toFixed(2)}s`);
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
