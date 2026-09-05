/* Deterministic frame renderer.
   node render.js sheet          -> one still per scene into out/sheet/
   node render.js frames         -> pipes every frame straight into ffmpeg -> out/harish-budget.mp4
*/
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const DIR = __dirname;
const OUT = path.join(DIR, 'out');
const FPS = 30;
const FF = process.env.FFMPEG || '/tmp/ffdl/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2';

(async () => {
  const mode = process.argv[2] || 'sheet';
  fs.mkdirSync(OUT, { recursive: true });

  const browser = await chromium.launch({
    args: ['--force-color-profile=srgb', '--font-render-hinting=none',
           '--disable-lcd-text', '--hide-scrollbars', '--disable-gpu']
  });
  const page = await browser.newPage({
    viewport: { width: 1080, height: 1920 },
    deviceScaleFactor: 1
  });
  await page.goto('file://' + path.join(DIR, 'video.html'));
  await page.waitForFunction('window.ready === true', null, { timeout: 30000 });

  const total = await page.evaluate('window.TOTAL');
  const scenes = await page.evaluate('window.SCENES.map(s=>s.id)');
  const durs = await page.evaluate('window.SCENES.map(s=>s.dur)');
  console.log('total duration', total.toFixed(2), 's ·', scenes.length, 'scenes ·',
              Math.round(total * FPS), 'frames');

  if (mode === 'sheet') {
    const sheet = path.join(OUT, 'sheet');
    fs.mkdirSync(sheet, { recursive: true });
    let acc = 0;
    for (let i = 0; i < scenes.length; i++) {
      const t = acc + durs[i] * 0.72;         // after the reveal has settled
      acc += durs[i];
      await page.evaluate(tt => window.setTime(tt), t);
      await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
      const f = path.join(sheet, String(i).padStart(2, '0') + '-' + scenes[i] + '.png');
      await page.screenshot({ path: f });
      console.log('·', scenes[i], t.toFixed(2) + 's');
    }
    await browser.close();
    return;
  }

  // full render
  const outFile = path.join(OUT, 'harish-budget-reels-1080x1920.mp4');
  const args = [
    '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', 'pipe:0',
    '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=48000',
    '-shortest',
    '-c:v', 'libx264', '-profile:v', 'high', '-level', '4.1',
    '-preset', 'slow', '-crf', '18',
    '-pix_fmt', 'yuv420p', '-r', String(FPS),
    '-x264-params', 'keyint=60:min-keyint=30:scenecut=0',
    '-c:a', 'aac', '-b:a', '128k',
    '-movflags', '+faststart',
    outFile
  ];
  const ff = spawn(FF, args, { stdio: ['pipe', 'inherit', 'pipe'] });
  let ffErr = '';
  ff.stderr.on('data', d => { ffErr += d.toString(); if (ffErr.length > 40000) ffErr = ffErr.slice(-20000); });
  const done = new Promise((res, rej) =>
    ff.on('close', c => c === 0 ? res() : rej(new Error('ffmpeg ' + c + '\n' + ffErr.slice(-3000)))));

  const nFrames = Math.round(total * FPS);
  const t0 = Date.now();
  for (let i = 0; i < nFrames; i++) {
    const t = i / FPS;
    await page.evaluate(tt => window.setTime(tt), t);
    const buf = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) {
      const el = (Date.now() - t0) / 1000;
      console.log(`frame ${i}/${nFrames}  ${(i / nFrames * 100).toFixed(1)}%  ${el.toFixed(0)}s elapsed`);
    }
  }
  ff.stdin.end();
  await done;
  console.log('wrote', outFile);
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
