import asyncio

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


async def main() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://books.toscrape.com/catalogue/page-1.html")
        html = await page.content()
        soup = BeautifulSoup(html, "lxml")

        books = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")

        for item in books:
            title = item.h3.a.attrs["title"]
            print(title)


asyncio.run(main())
