/* Caption renderer.
   Hebrew must never be drawn by ffmpeg's drawtext: that filter has no bidi
   support, so it emits the glyphs in logical order and every line comes out
   reversed. Chromium does full bidi and Hebrew shaping correctly, and it is
   already the engine that renders the rest of this project, so captions are
   rendered there as transparent PNGs and simply overlaid.

   Reads captions.json:
     [ { "start": 0.0, "end": 2.4, "text": "שורה ראשונה\nשורה שנייה" }, ... ]

   Writes:
     out/caps/scrim.png        the permanent gradient under the caption area
     out/caps/cap0000.png ...  one transparent 1080x1920 plate per caption
     out/caps/filter.txt       an ffmpeg filter script, ready to use

   Run:
     node captions.js
     ffmpeg -i picture.mp4 -i out/caps/scrim.png -i out/caps/cap0000.png ... \
            -filter_complex_script out/caps/filter.txt -map "[v]" -map 0:a ...

   The filter script form matters on Windows, where a long -filter_complex
   would blow past the command line length limit.

   Spec comes from BRAND.md and is enforced below: 60px, weight 700, white,
   at most two lines of at most 32 characters, last baseline at 1620, and
   no dashes anywhere. */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const DIR = __dirname;
const OUT = path.join(DIR, 'out', 'caps');
const W = 1080, H = 1920;

const SPEC = {
  size: 60,
  weight: 700,
  color: '#ffffff',
  lineHeight: 1.25,
  lastBaseline: 1620,     // px from the top of the frame
  maxLines: 2,
  maxChars: 32,
  scrimFrom: 1400,        // gradient starts here, fully transparent
  scrimTo: 1700,          // and reaches its darkest here
  scrimAlpha: 0.62
};

const DASHES = /[-־‐‑‒–—―]/;

function lint(caps) {
  const bad = [];
  caps.forEach((c, i) => {
    const lines = String(c.text).split('\n');
    if (DASHES.test(c.text)) bad.push(`#${i} contains a dash: ${c.text}`);
    if (lines.length > SPEC.maxLines) bad.push(`#${i} has ${lines.length} lines`);
    lines.forEach(l => {
      if (l.length > SPEC.maxChars) bad.push(`#${i} line of ${l.length} chars: ${l}`);
    });
    if (!(c.end > c.start)) bad.push(`#${i} bad timing`);
    if (c.end - c.start < 0.8) bad.push(`#${i} on screen only ${(c.end - c.start).toFixed(2)}s`);
  });
  return bad;
}

const page = (body, extra = '') => `<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">
<style>
@font-face{font-family:HeeboV;src:url('file://${path.join(DIR, 'fonts', 'Heebo.ttf')}') format('truetype');font-weight:100 900}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:${W}px;height:${H}px;background:transparent;overflow:hidden;
  font-family:HeeboV,sans-serif;-webkit-font-smoothing:antialiased}
${extra}
</style></head><body>${body}</body></html>`;

(async () => {
  const src = path.join(DIR, 'captions.json');
  if (!fs.existsSync(src)) {
    console.error('missing captions.json next to this script'); process.exit(1);
  }
  const caps = JSON.parse(fs.readFileSync(src, 'utf8'));
  const problems = lint(caps);
  if (problems.length) {
    console.error('captions.json fails the BRAND.md rules:\n  ' + problems.join('\n  '));
    process.exit(1);
  }

  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const p = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });

  /* the scrim is one always on plate, so it never pops between captions */
  await p.setContent(page(`<div id="s"></div>`, `#s{position:absolute;left:0;right:0;
    top:${SPEC.scrimFrom}px;height:${H - SPEC.scrimFrom}px;
    background:linear-gradient(to bottom,rgba(11,43,68,0) 0%,
      rgba(11,43,68,${SPEC.scrimAlpha}) ${((SPEC.scrimTo - SPEC.scrimFrom) / (H - SPEC.scrimFrom) * 100).toFixed(1)}%,
      rgba(11,43,68,${SPEC.scrimAlpha}) 100%)}`));
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: path.join(OUT, 'scrim.png'), omitBackground: true });

  const lh = SPEC.size * SPEC.lineHeight;
  for (let i = 0; i < caps.length; i++) {
    const lines = String(caps[i].text).split('\n');
    /* anchor the block so the last line always sits on the same baseline */
    const top = SPEC.lastBaseline - lh * lines.length + (lh - SPEC.size) / 2;
    await p.setContent(page(
      `<div id="c">${lines.map(l => `<div class="l"></div>`).join('')}</div>`,
      `#c{position:absolute;left:0;right:0;top:${Math.round(top)}px;text-align:center;direction:rtl}
       .l{font-size:${SPEC.size}px;font-weight:${SPEC.weight};color:${SPEC.color};
          line-height:${SPEC.lineHeight};text-shadow:0 2px 12px rgba(11,43,68,.55)}`));
    await p.evaluate(ls => {
      document.querySelectorAll('.l').forEach((el, k) => { el.textContent = ls[k]; });
    }, lines);
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({
      path: path.join(OUT, 'cap' + String(i).padStart(4, '0') + '.png'),
      omitBackground: true
    });
  }
  await browser.close();

  /* ffmpeg filter script. input 0 is the picture, 1 is the scrim,
     2 and onward are the caption plates in order. */
  const parts = [`[0:v][1:v]overlay=0:0[b0]`];
  caps.forEach((c, i) => {
    const from = `[b${i}]`, to = i === caps.length - 1 ? '[v]' : `[b${i + 1}]`;
    parts.push(`${from}[${i + 2}:v]overlay=0:0:enable='between(t,${c.start},${c.end})'${to}`);
  });
  fs.writeFileSync(path.join(OUT, 'filter.txt'), parts.join(';\n'));

  const inputs = ['-i out/caps/scrim.png']
    .concat(caps.map((_, i) => `-loop 1 -i out/caps/cap${String(i).padStart(4, '0')}.png`))
    .join(' ');
  fs.writeFileSync(path.join(OUT, 'command.txt'),
    `ffmpeg -i PICTURE.mp4 ${inputs} \\\n  -filter_complex_script out/caps/filter.txt \\\n` +
    `  -map "[v]" -map 0:a -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p \\\n` +
    `  -c:a copy -movflags +faststart OUTPUT.mp4\n`);

  console.log(`rendered ${caps.length} captions plus the scrim into out/caps`);
  console.log('filter script: out/caps/filter.txt');
  console.log('example command: out/caps/command.txt');
})();
