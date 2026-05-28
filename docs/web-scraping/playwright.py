from playwright.async_api import async_playwright


async def redner(url):
    async with async_playwright() as p:
        browser = await p.chromium.lauch(headeless=True)
        page = await browser.new_page()

        await page.goto(url, wait_until="networkidle")
        html = await page.content()

        await browser.close()
        return html
