const { test, expect } = require('@playwright/test');

for (const language of ['ar', 'en']) {
  test(`${language}: keyboard controls remain reachable at 2x layout magnification`, async ({ page }) => {
    await page.route('**/*', route => new URL(route.request().url()).origin === 'http://127.0.0.1:8765' ? route.continue() : route.abort());
    await page.addInitScript(language => {
      localStorage.setItem('nmi-preview-language',language);
      localStorage.setItem('nmi-preview-demo-v1',JSON.stringify({version:1,profile:{name:'Demo',country:'Jordan',grade:10,language,avatar:false,subjects:[]},chats:[]}));
    }, language);
    // CSS zoom exercises magnified layout and scrolling, not native browser chrome.
    await page.setViewportSize({width:1280,height:800}); await page.goto('/');
    await page.evaluate(() => { document.documentElement.style.zoom = '2'; });
    await page.locator('#question').focus(); await page.keyboard.type('Sample question'); await page.keyboard.press('Tab'); await expect(page.locator('#send')).toBeFocused();
    const box = await page.locator('#send').boundingBox(); expect(box.x).toBeGreaterThanOrEqual(0); expect(box.y).toBeGreaterThanOrEqual(0); expect(box.x+box.width).toBeLessThanOrEqual(1280); expect(box.y+box.height).toBeLessThanOrEqual(800);
    await page.keyboard.press('Enter'); await expect(page.locator('.assistant-message')).toHaveCount(1);
    await page.screenshot({path:`.cache/screenshots/magnified-${language}.png`});
    await page.evaluate(() => { document.documentElement.style.zoom = ''; });
    await page.locator('.sidebar a[href="#profile"]').click(); await page.locator('#continue-learning').scrollIntoViewIfNeeded(); await page.screenshot({path:`.cache/screenshots/profile-lower-${language}.png`});
    await page.locator('.sidebar a[href="#progress"]').click(); await page.locator('#sample-toggle').click(); await page.locator('#main').evaluate(el => { el.scrollTop = el.scrollHeight; }); await page.screenshot({path:`.cache/screenshots/prerequisite-recovery-${language}.png`});
  });
}
