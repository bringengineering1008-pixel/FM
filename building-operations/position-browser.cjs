const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1280,height:800}});
  await page.goto(((process.env.ATLAS_TEST_URL||'http://localhost:59483')+'/building-operations/'));
  const initial=await page.evaluate(async()=>{
   const d=(await import('./model.mjs')).demo();
   for(const r of d.records){r.confidence='현장 확인';r.verifiedAt='2026-09-13';r.source='검증용 도면';}
   d.records.find(r=>r.id==='pump').routes=[{targetId:'tank',points:[{floor:0,x:-2,z:2}],confirmed:true}];
   d.records.find(r=>r.id==='valve').routes=[{targetId:'pump',points:[{floor:0,x:2,z:2}],confirmed:true}];
   d.records.find(r=>r.id==='riser2').routes=[{targetId:'riser1',points:[{floor:1,x:5,z:2}],confirmed:true}];
   return {version:2,activeId:'first',items:[{id:'first',data:d}]};
  });
  for(const [field,value] of [['notes','메모만 수정'],['x','1'],['z','3'],['floor','1']]){
   await page.evaluate(p=>localStorage.setItem('bring-building-atlas-portfolio-v2',JSON.stringify(p)),initial);
   await page.reload();
   await page.locator('#editRecord').click();
   await page.locator(`#form [name=${field}]`).fill(value);
   await page.locator('#form button[type=submit]').click();
   await page.waitForFunction(()=>!document.querySelector('#editor').open);
   await page.reload();
   const d=await page.evaluate(()=>JSON.parse(localStorage.getItem('bring-building-atlas-portfolio-v2')).items[0].data);
   const pump=d.records.find(r=>r.id==='pump');
   const moved=field!=='notes';
   assert.equal(pump.confidence,moved?'추정':'현장 확인',`${field}: confidence`);
   assert.equal(pump.verifiedAt,moved?'':'2026-09-13');
   assert.equal(pump.routes[0].confirmed,!moved,'outbound route');
   assert.equal(d.records.find(r=>r.id==='valve').routes[0].confirmed,!moved,'inbound route');
   assert.equal(d.records.find(r=>r.id==='riser2').routes[0].confirmed,true,'unrelated route');
   assert(pump.source.includes('검증용 도면'),'retain original evidence reference');
  }
  console.log('PASS: x/z/floor changes reset verification and attached routes; notes preserve confirmation; unrelated routes and evidence retained after reload');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
