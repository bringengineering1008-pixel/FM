const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const base=process.env.ATLAS_TEST_URL||'http://localhost:59483';
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true,args:['--enable-webgl','--use-angle=swiftshader']});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},acceptDownloads:true});
  await page.route('**/*',route=>new URL(route.request().url()).origin===new URL(base).origin?route.continue():route.abort());
  await page.goto(base+'/index.html');
  await page.waitForFunction(()=>document.querySelector('#fmExportClose'));
  await page.evaluate(()=>{auth=null;document.querySelector('#exportAtlasBasics').click();});
  assert((await page.locator('#fmExportError').innerText()).includes('로그인'));
  assert(await page.locator('#fmExportDownload').isDisabled());await page.locator('#fmExportClose').click();
  await page.evaluate(()=>{
   auth={currentUser:{uid:'synthetic-test'}};
   settings={paymentBuildings:{b:{name:'테스트 건물',address:'테스트 주소',ownerName:'SECRET_OWNER',amount:99999}}};
   cases={};document.querySelector('#exportAtlasBasics').click();
  });
  assert((await page.locator('#fmExportPreview').innerText()).includes('테스트 건물'));
  const [download]=await Promise.all([page.waitForEvent('download'),page.locator('#fmExportDownload').click()]);
  const payload=JSON.parse(await fs.readFile(await download.path(),'utf8'));
  assert.deepEqual(payload,{kind:'bring-building-basics',version:1,building:{name:'테스트 건물',address:'테스트 주소'}});
  await page.evaluate(()=>{auth=null;});await page.locator('#fmExportDownload').click();
  assert((await page.locator('#fmExportError').innerText()).includes('만료'));
  await page.goto(base+'/building-operations/');await page.locator('#viewport canvas').waitFor();
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(let i=0;i<2;i++){
   await page.locator('#importFMBasics').click();
   await page.locator('#fmBasicsFile').setInputFiles({name:'building.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(payload))});
   await page.waitForFunction(()=>!document.querySelector('#fmImportConfirm').disabled);
   await page.locator('#fmImportConfirm').click();
   assert.equal(await page.locator('#title').innerText(),'테스트 건물');
   assert.equal(await page.locator('#buildingSelect option').count(),2);
  }
  assert(await page.locator('#fmGeometryWarning').isVisible());
  const before=await page.evaluate(()=>localStorage.getItem('bring-building-atlas-portfolio-v2'));
  await page.locator('#importFMBasics').click();
  await page.locator('#fmBasicsFile').setInputFiles({name:'bad.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({...payload,phone:'SECRET'}))});
  await page.waitForFunction(()=>document.querySelector('#fmImportError').textContent);
  assert(await page.locator('#fmImportConfirm').isDisabled());
  assert.equal(await page.evaluate(()=>localStorage.getItem('bring-building-atlas-portfolio-v2')),before);
  await page.locator('#fmImportClose').click();await page.reload();
  assert.equal(await page.locator('#title').innerText(),'테스트 건물');
  await page.screenshot({path:'building-atlas-fm-import.png'});
  assert.deepEqual(errors,[]);
  console.log('PASS: login/expired session guarded, export contains only name/address, preview/import persists, duplicates preserve existing map, sensitive extra fields rejected');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
