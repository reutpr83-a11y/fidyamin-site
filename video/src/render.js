const { chromium } = require('playwright-core');
const path = require('path'), fs = require('fs');
const DIR = process.env.FILM_DIR || path.resolve(__dirname, '..');

(async () => {
  const mode = process.argv[2] || 'probe';
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--no-sandbox','--disable-dev-shm-usage','--font-render-hinting=none','--force-color-profile=srgb','--hide-scrollbars']
  });
  const page = await browser.newPage({ viewport:{width:1920,height:1080}, deviceScaleFactor:1 });
  await page.goto('file://'+path.join(__dirname,'film.html'));
  await page.waitForTimeout(1200);
  const total = await page.evaluate(()=>window.TOTAL);
  console.log('TOTAL =', total.toFixed(2), 's');

  if (mode === 'probe') {
    const times = process.argv.slice(3).map(Number);
    for (const t of times) {
      await page.evaluate(tt=>window.seek(tt), t);
      await page.screenshot({ path: path.join(DIR,'probe_'+t.toFixed(1).replace('.','_')+'.png') });
    }
  } else {
    const FPS = 25;
    const n = Math.ceil(total*FPS);
    const fdir = path.join(DIR,'frames');
    fs.rmSync(fdir,{recursive:true,force:true}); fs.mkdirSync(fdir,{recursive:true});
    const t0 = Date.now();
    for (let i=0;i<n;i++){
      await page.evaluate(tt=>window.seek(tt), i/FPS);
      await page.screenshot({ path: path.join(fdir,'f'+String(i).padStart(6,'0')+'.jpg'), type:'jpeg', quality:95 });
      if (i%250===0) console.log(i+'/'+n+'  '+((Date.now()-t0)/1000).toFixed(0)+'s');
    }
    console.log('done '+n+' frames in '+((Date.now()-t0)/1000).toFixed(0)+'s');
    fs.writeFileSync(path.join(DIR,'total.txt'), String(total));
  }
  await browser.close();
})();
