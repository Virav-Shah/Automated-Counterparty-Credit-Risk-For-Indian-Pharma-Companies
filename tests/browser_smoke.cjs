/** Optional local browser regression test; requires Playwright and Chrome/Chromium.
 * Run after generating outputs/dashboard.html. Screenshots go to the OS temp dir.
 */
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const os=require('node:os');
const {pathToFileURL}=require('node:url');
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{})});
 try {
  const page=await browser.newPage({viewport:{width:1440,height:1100}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.resolve(__dirname,'../outputs/dashboard.html')).href);
  await page.waitForSelector('#v2-table tr[data-company]');
  assert.equal(await page.locator('#v2-table tr[data-company]').count(),19);
  await page.fill('#v2-search','JB Chemicals');
  assert.equal(await page.locator('#v2-table tr[data-company]').count(),0);
  assert.equal(await page.locator('#v2-watchlist th').count(),4);
  assert.doesNotMatch(await page.locator('main').innerText(),/qualitative/i);
  await page.screenshot({path:path.join(os.tmpdir(),'crm-v2-desktop.png'),fullPage:true});
  await page.fill('#v2-search','');
  await page.selectOption('#v2-priority','CREDIT REVIEW');
  assert.equal(await page.locator('#v2-table tr[data-company]').count(),1);
  await page.selectOption('#v2-priority','');
  await page.fill('#v2-search','Biocon');
  assert.equal(await page.locator('#v2-table tr[data-company]').count(),1);
  assert.match(await page.locator('#v2-detail').innerText(),/25/);
  assert.match(await page.locator('#v2-detail').innerText(),/45/);
  const [watchDownload]=await Promise.all([page.waitForEvent('download'),page.click('#v2-export')]);
  assert.match(watchDownload.suggestedFilename(),/^credit_watchlist_/);
  assert.equal(fs.readFileSync(await watchDownload.path(),'utf8').split('\r\n').length,2);
  await page.click('#v2-history');
  assert.equal(await page.locator('#financial-view').isVisible(),true);
  assert.match(await page.locator('#detail').innerText(),/Biocon/);
  await page.selectOption('#year','FY21');
  assert.match(await page.locator('#detail').innerText(),/NOT SCORED/);
  await page.click('#tab-watch');
  await page.fill('#v2-search','no company matches');
  assert.equal(await page.locator('#v2-table tr[data-company]').count(),0);
  await page.fill('#v2-search','');
  await page.selectOption('#v2-sort','name');
  assert.match(await page.locator('#v2-table tr').first().innerText(),/Abbott India/);
  await page.selectOption('#v2-group','API / CDMO / Contract Manufacturing');
  assert.equal(await page.locator('#v2-table tr[data-company]').count(),3);
  await page.selectOption('#v2-group','');
  await page.fill('#v2-search','Sun Pharma');
  assert.equal(await page.locator('#v2-detail .v2-layer').count(),2);
  for(const width of [390,768]) {
   await page.setViewportSize({width,height:844});
   await page.screenshot({path:path.join(os.tmpdir(),`crm-v2-mobile-${width}.png`),fullPage:true});
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true);
  }
  assert.deepEqual(errors,[]);
  console.log('PASS: watchlist, company details, filters/sort, watchlist CSV export, financial history, 390/768px layout; no JavaScript errors.');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
