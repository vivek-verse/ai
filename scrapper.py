import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

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


async def fetch_all_links_async(url: str) -> list[str]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(url, timeout=30000)
        await page.wait_for_load_state("networkidle")

        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "lxml")

    links = set()
    base_domain = urlparse(url).netloc

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()

        # Skip junk links
        if href.startswith(("javascript:", "mailto:", "tel:", "#")):
            continue

        full_url = urljoin(url, href)
        parsed = urlparse(full_url)

        # Optional: keep only same-domain links
        if parsed.netloc == base_domain:
            links.add(full_url)

    return sorted(links)


def fetch_website_content(url: str, max_chars: int = 2000) -> str:
    """
    Sync wrapper so main.py doesn't need async code
    """
    return asyncio.run(scrape_clean_text_async(url, max_chars))


def fetch_all_links(url: str) -> list[str]:
    """
    Sync wrapper to fetch all links from a webpage
    """
    return asyncio.run(fetch_all_links_async(url))
