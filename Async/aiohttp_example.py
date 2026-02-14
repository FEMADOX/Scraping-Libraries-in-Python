import asyncio

import aiohttp
from bs4 import BeautifulSoup

urls = [
    "https://books.toscrape.com/",
    "https://books.toscrape.com/catalogue/page-2.html",
    "https://books.toscrape.com/catalogue/page-3.html",
    "https://books.toscrape.com/catalogue/page-4.html",
    "https://books.toscrape.com/catalogue/page-5.html",
    "https://books.toscrape.com/catalogue/page-6.html",
    "https://books.toscrape.com/catalogue/page-7.html",
    "https://books.toscrape.com/catalogue/page-8.html",
    "https://books.toscrape.com/catalogue/page-9.html",
    "https://books.toscrape.com/catalogue/page-10.html",
    "https://books.toscrape.com/catalogue/page-11.html",
    "https://books.toscrape.com/catalogue/page-12.html",
    "https://books.toscrape.com/catalogue/page-13.html",
    "https://books.toscrape.com/catalogue/page-14.html",
    "https://books.toscrape.com/catalogue/page-15.html",
    "https://books.toscrape.com/catalogue/page-16.html",
    "https://books.toscrape.com/catalogue/page-17.html",
    "https://books.toscrape.com/catalogue/page-18.html",
    "https://books.toscrape.com/catalogue/page-19.html",
    "https://books.toscrape.com/catalogue/page-20.html",
    "https://books.toscrape.com/catalogue/page-21.html",
    "https://books.toscrape.com/catalogue/page-22.html",
    "https://books.toscrape.com/catalogue/page-23.html",
    "https://books.toscrape.com/catalogue/page-24.html",
    "https://books.toscrape.com/catalogue/page-25.html",
    "https://books.toscrape.com/catalogue/page-26.html",
    "https://books.toscrape.com/catalogue/page-27.html",
    "https://books.toscrape.com/catalogue/page-28.html",
    "https://books.toscrape.com/catalogue/page-29.html",
    "https://books.toscrape.com/catalogue/page-30.html",
    "https://books.toscrape.com/catalogue/page-31.html",
    "https://books.toscrape.com/catalogue/page-32.html",
    "https://books.toscrape.com/catalogue/page-33.html",
    "https://books.toscrape.com/catalogue/page-34.html",
    "https://books.toscrape.com/catalogue/page-35.html",
    "https://books.toscrape.com/catalogue/page-36.html",
    "https://books.toscrape.com/catalogue/page-37.html",
    "https://books.toscrape.com/catalogue/page-38.html",
    "https://books.toscrape.com/catalogue/page-39.html",
    "https://books.toscrape.com/catalogue/page-40.html",
    "https://books.toscrape.com/catalogue/page-41.html",
    "https://books.toscrape.com/catalogue/page-42.html",
    "https://books.toscrape.com/catalogue/page-43.html",
    "https://books.toscrape.com/catalogue/page-44.html",
    "https://books.toscrape.com/catalogue/page-45.html",
    "https://books.toscrape.com/catalogue/page-46.html",
    "https://books.toscrape.com/catalogue/page-47.html",
    "https://books.toscrape.com/catalogue/page-48.html",
    "https://books.toscrape.com/catalogue/page-49.html",
    "https://books.toscrape.com/catalogue/page-50.html",
]


class Spider:
    def __init__(self, urls: list[str]):
        self.urls = urls
        self.semaphore = asyncio.Semaphore(10)

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> tuple[str, str]:
        async with self.semaphore, session.get(url) as response:
            return await response.text(), url

    async def aiohttp_http(self) -> list[tuple[str, str]]:
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch(session, url) for url in self.urls]
            return await asyncio.gather(*tasks)

    async def scrape(self) -> None:
        for title, url in await self.aiohttp_http():
            soup = BeautifulSoup(title, "html.parser")
            data = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")

            for tag_p in data:
                book_title = tag_p.h3.a.text
                price = tag_p.find("p", class_="price_color").text
                print(f"Title: {book_title}, Price: {price}, URL: {url}")


if __name__ == "__main__":
    spider = Spider(urls)
    asyncio.run(spider.scrape())
