const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
  const browser=await chromium.launch({channel:'chrome',headless:true});
  try {
    const page=await browser.newPage();
    await page.goto(((process.env.ATLAS_TEST_URL||'http://localhost:59483')+'/building-operations/'));
    for(const width of [1440,1280,1110,768,390]) {
      await page.setViewportSize({width,height:720});
      assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`horizontal overflow at ${width}`);
      await page.locator('#add').click();
      const visible=()=>page.evaluate(()=>{
        const dialog=document.querySelector('#editor').getBoundingClientRect();
        return ['#close','#form button[type=submit]'].every(selector=>{
          const r=document.querySelector(selector).getBoundingClientRect();
          return r.top>=dialog.top && r.bottom<=dialog.bottom && r.bottom<=innerHeight;
        });
      });
      assert(await visible(),`Save and Close must remain visible at ${width}`);
      await page.locator('#form [name=notes]').fill('화면 검증용 메모');
      assert(await visible(),`controls remain visible after scrolling at ${width}`);
      await page.locator('#close').click();
    }
    console.log('PASS: no horizontal overflow; Save and Close visible before/after field scrolling at five widths');
  } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exitCode=1;});
