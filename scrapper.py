import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def scrape_clean_text_async(url: str, max_chars: int = 2000) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(url, timeout=30000)
        await page.wait_for_load_state("networkidle")

        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "lxml")

    # Title
    title = soup.title.string.strip() if soup.title else ""

    # Remove unwanted tags
    for tag in soup(["script", "style", "img", "input", "noscript", "svg"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    combined = f"{title}\n\n{text}".strip()

    return combined[:max_chars]


def fetch_website_content(url: str, max_chars: int = 2000) -> str:
    """
    Sync wrapper so main.py doesn't need async code
    """
    return asyncio.run(scrape_clean_text_async(url, max_chars))
