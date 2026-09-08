/* Caption renderer.
   Hebrew must never be drawn by ffmpeg's drawtext: that filter has no bidi
   support, so it emits the glyphs in logical order and every line comes out
   reversed. Chromium does full bidi and Hebrew shaping correctly, and it is
   already the engine that renders the rest of this project, so captions are
   rendered there as transparent PNGs and simply overlaid.

   Reads captions.json:
     [ { "start": 0.0, "end": 2.4, "text": "שורה ראשונה\nשורה שנייה" },
       { "start": 2.4, "end": 5.0, "text": "משפט נושא", "style": "emphasis" },
       { "start": 5.0, "end": 7.2, "text": "ועוד *1.3 מיליון* בשורה" } ]

   style is "plain" by default. Asterisks mark the one word or figure that
   carries the point, and that word alone is tinted in the campaign light
   blue. One highlight per caption at most.

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

   Spec comes from BRAND.md and is enforced below. The run fails with a list
   of offending captions rather than quietly producing wrong output. */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const DIR = __dirname;
const OUT = path.join(DIR, 'out', 'caps');
const W = 1080, H = 1920;

/* Two treatments, deliberately unequal.
   Most captions are quiet and functional. A handful carry the argument and
   get the film's own right aligned block with the gold rule beside it, the
   same shape as every data screen. That contrast is what makes the cut read
   as designed rather than auto generated: not everything is a hero. */
const STYLE = {
  /* one weight for every caption in the film: 800. a body at 600 sitting
     next to an emphasis at 800 reads as two different typefaces to anyone
     who is not a designer, and that is the report we actually got. the
     approved look is the heavy one, so the heavy one is now everywhere and
     the two treatments differ only in size and in the accent. */
  plain: {
    size: 72, weight: 800, align: 'center',
    maxChars: 22, lineHeight: 1.18
  },
  emphasis: {
    size: 88, weight: 800, align: 'center',
    maxChars: 17, lineHeight: 1.14
  }
};

const SPEC = {
  color: '#ffffff',
  /* The campaign gold is #f5b04a and it is right on flat navy. Over this
     footage, against warm skin and a warm shirt, the identical value reads
     orange and cheap, so gold never appears over picture. The accent over
     picture is the campaign light blue, which is a cool colour against warm
     footage and therefore separates instead of blending. It was measured
     off the youth cut, checked against a lighter and a deeper variant on a
     real graded frame, and this value held: lighter goes pastel, deeper
     starts to sink into the navy scrim.

     It tints one word or one figure per caption and nothing else. The body
     stays white and the rule stays white, so the colour still means
     something when it appears. */
  accent: '#63cbea',
  accentMaxChars: 16,
  /* the accent word is tinted and underlined, both in the same value. the
     underline is what makes it read as marked rather than merely coloured,
     and it survives a bright background where colour alone can wash out. */
  accentUnderline: 8,
  accentUnderlineGap: 14,
  /* every caption is white type with a dark outline drawn behind the fill.
     that outline is what holds the type over sky, grass and skin without a
     heavy band across the picture. */
  stroke: '#0b2b44',
  strokeWidth: 4,
  ruleColor: '#ffffff',
  lastBaseline: 1620,     // every caption shares this, so the block never jumps
  maxLines: 2,
  padRight: 880,          // right edge of the RTL column, as everywhere else
  ruleX: 912,
  scrimFrom: 1380,        // gradient starts here, fully transparent
  scrimTo: 1660,          // and reaches its darkest here
  scrimAlpha: 0.66,
  maxEmphasis: 5          // more than this and emphasis stops meaning anything
};

const DASHES = /[-־‐‑‒–—―]/;

/* *word* marks the highlight. plain() strips the markers for measuring and
   linting, markup() turns them into the tinted span. */
const MARK = /\*([^*]+)\*/g;
const plain = t => t.replace(MARK, '$1');

function lint(caps) {
  const bad = [];
  let emph = 0;
  caps.forEach((c, i) => {
    const st = STYLE[c.style || 'plain'];
    if (!st) { bad.push(`#${i} unknown style ${c.style}`); return; }
    if (c.style === 'emphasis') emph++;
    const lines = plain(String(c.text)).split('\n');
    if (DASHES.test(c.text)) bad.push(`#${i} contains a dash: ${c.text}`);
    if (lines.length > SPEC.maxLines) bad.push(`#${i} has ${lines.length} lines`);
    lines.forEach(l => {
      if (l.length > st.maxChars)
        bad.push(`#${i} line of ${l.length} chars, ${c.style || 'plain'} allows ${st.maxChars}: ${l}`);
    });
    const marks = String(c.text).match(MARK) || [];
    if ((String(c.text).match(/\*/g) || []).length % 2)
      bad.push(`#${i} has an unclosed highlight marker`);
    if (marks.length > 1)
      bad.push(`#${i} has ${marks.length} highlights, one per caption at most`);
    marks.forEach(m => {
      const w = m.slice(1, -1);
      if (w.length > SPEC.accentMaxChars)
        bad.push(`#${i} highlights ${w.length} chars, at most ${SPEC.accentMaxChars}: ${w}`);
      if (lines.some(l => l.trim() === w.trim()))
        bad.push(`#${i} highlights a whole line. the accent marks a word, not a sentence`);
    });
    if (!(c.end > c.start)) bad.push(`#${i} bad timing`);
    if (c.end - c.start < 0.8) bad.push(`#${i} on screen only ${(c.end - c.start).toFixed(2)}s`);
  });
  if (emph > SPEC.maxEmphasis)
    bad.push(`${emph} emphasis captions, at most ${SPEC.maxEmphasis} or it stops meaning anything`);
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

  const esc = s => s.replace(/[&<>]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[ch]));
  const markup = l => esc(l).replace(MARK, '<em>$1</em>');

  for (let i = 0; i < caps.length; i++) {
    const c = caps[i];
    const st = STYLE[c.style || 'plain'];
    const lines = String(c.text).split('\n');
    const lh = st.size * st.lineHeight;
    /* every caption shares one last baseline, so the block never jumps */
    const top = SPEC.lastBaseline - lh * lines.length + (lh - st.size) / 2;
    const h = Math.round(lh * lines.length);

    const box = st.align === 'right'
      ? `right:${W - SPEC.padRight}px;width:${SPEC.padRight - 90}px;text-align:right`
      : `left:0;right:0;text-align:center`;

    /* no vertical rule any more. the accent underline carries the mark, and
       a rule beside centred type has nothing to align to. */
    const rule = '';

    await p.setContent(page(
      rule + `<div id="c">${lines.map(() => '<div class="l"></div>').join('')}</div>`,
      `#c{position:absolute;top:${Math.round(top)}px;${box};direction:rtl}
       .l{font-size:${st.size}px;font-weight:${st.weight};color:${SPEC.color};
          line-height:${st.lineHeight};letter-spacing:-.012em;
          -webkit-text-stroke:${SPEC.strokeWidth}px ${SPEC.stroke};paint-order:stroke fill;
          text-shadow:0 2px 14px rgba(11,43,68,.55)}
       .l em{font-style:normal;color:${SPEC.accent};
          text-decoration:underline;text-decoration-color:${SPEC.accent};
          text-decoration-thickness:${SPEC.accentUnderline}px;
          text-underline-offset:${SPEC.accentUnderlineGap}px}`));
    await p.evaluate(ls => {
      document.querySelectorAll('.l').forEach((el, k) => { el.innerHTML = ls[k]; });
    }, lines.map(markup));
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
