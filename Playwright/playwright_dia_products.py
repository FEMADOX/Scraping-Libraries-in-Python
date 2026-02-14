import asyncio
import logging
from typing import TYPE_CHECKING, cast

import pandas as pd
from bs4 import BeautifulSoup, Tag
from playwright.async_api import Playwright, async_playwright

if TYPE_CHECKING:
    from playwright.async_api import Browser, Page

# Config logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

URL = "https://www.dia.es/freidora-de-aire-airfryer/c/L125"


class DiaScraper:
    """A class to scrape product information from the DIA supermarket website.

    This class provides methods to set up a browser page, extract category URLs from the
    sidebar, and scrape product details such as name, price, and price per unit. It
    handles dynamic content loading by scrolling through the page until all products are
    loaded.

    Methods:
        set_up: Initializes a new browser page and navigates to the specified URL.
        get_full_urls_from_sidebar: Extracts full URLs of product categories from
            the sidebar.
        extract_products_from_page: Scrapes product information from a given page.
        iter_through_urls: Iterates through a list of URLs to extract product data.

    """

    def __init__(self, url: str = URL, headless: bool = False) -> None:
        """Initialize the scraper with a target URL and headless mode setting."""
        self.url = url
        self.headless = headless
        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.results: list[dict[str, str]] = []

    async def start(self) -> None:
        """Inicialize Playwright and launch the browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        logger.info("Browser Launched.")

    async def close(self) -> None:
        """Close the browser and stop Playwright."""
        if self.browser:
            await self.browser.close()
            logger.info("Browser Closed.")
        if self.playwright:
            await self.playwright.stop()
            logger.info("Playwright Stopped.")

    async def _create_page(self, url: str) -> Page:
        """Create and set up a new browser page.

        This asynchronous method creates a new browser context with a predefined
        viewport size (1920x1080), opens a new page, and attempts to handle cookie

        Returns:
            Page: The initialized Playwright Page object ready for interaction.

        Raises:
            RuntimeError: If the browser is not initialized before calling this method.

        """
        if not self.browser:
            msg = "Browser is not initialized. Call start() first."
            raise RuntimeError(msg)

        context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
        )
        page = await context.new_page()

        cookie_button = page.locator("button:has-text('Rechazar todas')")

        async def handle_cookie_overlay() -> None:
            logger.info("Cookie banner detected by handler. Handling cookies...")
            await cookie_button.click()

        await page.add_locator_handler(cookie_button, handle_cookie_overlay)
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        return page

    async def get_category_urls(self) -> list[str]:
        """Extract full URLs of product categories from the sidebar.

        This method creates a new page, navigates to the specified URL, and iterates
        through the sidebar category elements. It simulates clicks to reveal hidden
        sub-categories and parses the HTML content to find specific links within those
        sub-categories that match defined criteria (excluding "Todo" items).

        Returns:
            list[str]: A list of full URLs for the product categories.

        """
        page = await self._create_page(self.url)
        full_urls = []

        try:
            sidebar = page.locator("div.categories-layout__left-content__list")
            categories = sidebar.locator("li[data-test-id='categories-list-element']")
            count = await categories.count()

            for i in range(count):
                element = categories.nth(i)
                await element.scroll_into_view_if_needed()

                # Intentar expandir categoría
                try:
                    await element.hover()
                    expand_btn = element.locator(
                        "span.dia-icon-plus.category-item__symbol-icon",
                    )
                    expand_btn_visible = element.locator(
                        "span.category-item__symbol-icon.dia-icon-minus.category-item__symbol-icon--visible",
                    )
                    if await expand_btn.is_visible():
                        await expand_btn.click(timeout=1500)
                    elif await expand_btn_visible.is_visible():
                        logger.info(f"Element {i} already expanded.")
                except Exception:
                    logger.exception(f"Could not click expand button for element {i}")

                # Parsear HTML
                element_html = await element.inner_html()
                soup = BeautifulSoup(element_html, "lxml")
                sub_category_list = cast(
                    "Tag",
                    soup.find("ul", {"data-test-id": "sub-categories-list"}),
                )

                if sub_category_list:
                    links = sub_category_list.find_all(
                        lambda tag: (
                            tag.name == "a"
                            and "sub-category-item__link" in tag.get("class", [])
                            and not tag
                            .find_all("span")[1]
                            .text.strip()
                            .startswith("Todo")
                        ),
                    )
                    full_urls.extend([
                        f"https://www.dia.es{link.get('href')}" for link in links
                    ])
        finally:
            await page.close()

        return full_urls

    async def scrape_products(self, url: str) -> list[dict]:
        """Extract full URLs from the sidebar of a DIA supermarket page.

        This method iterates through the sidebar category elements, simulating clicks to
        reveal hidden sub-categories. It then parses the HTML content to find specific
        links within those sub-categories that match defined criteria
        (excluding "Todo" items).

        Args:
            url (str): The url of the page to scrape products from.

        Returns:
            list[str]: A list of full URLs valid for scraping or further processing.
                Note: Based on the implementation, this might return a nested list
                structure (list[list[str]]) depending on how the `hrefs` are appended

        """
        page = await self._create_page(url)
        products = []
        seen_products = set()

        try:
            last_height = await page.evaluate("document.body.scrollHeight")
            while True:
                content = await page.content()
                soup = BeautifulSoup(content, "lxml")
                items = soup.find_all("li", class_="product-card-list__item-container")

                for item in items:
                    name_tag = item.find(
                        "p",
                        class_="search-product-card__product-name",
                    )
                    if not name_tag:
                        continue

                    name = name_tag.text.strip()
                    if name in seen_products:
                        continue
                    seen_products.add(name)

                    price_tag = item.find(
                        "p",
                        class_="search-product-card__active-price",
                    )
                    unit_tag = item.find(
                        "p",
                        class_="search-product-card__price-per-unit",
                    )

                    price = price_tag.text.replace("\xa0", "") if price_tag else "N/A"
                    unit = (
                        unit_tag.text.replace("\xa0", "").strip("() ")
                        if unit_tag
                        else "N/A"
                    )

                    products.append({
                        "#": len(products) + 1,
                        "name": name,
                        "price": price,
                        "price_per_unit": unit,
                    })

                # Scroll logic
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                await asyncio.sleep(2)

                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

        except Exception:
            logger.exception(f"Error scraping {url}")
        finally:
            await page.close()

        return products

    async def run(self, workers: int = 3) -> list[dict]:
        """Orchestrate the scraping process.

            This method initializes the scraping process by starting the browser,
            fetching category URLs, and iterating through those URLs
            to extract product data. It ensures that the browser is properly
            closed after the operation, even if errors occur.

        Args:
            workers (int, optional): The number of concurrent tasks to run.

        Returns:
            list[dict]: A list of dictionaries containing the scraped product data.

        """
        await self.start()
        try:
            logger.info("Fetching categories...")
            urls = await self.get_category_urls()
            logger.info(f"Check: found {len(urls)} category URLs.")

            # Controled concurrency
            semaphore = asyncio.Semaphore(workers)

            async def worker(url: str) -> list[dict] | None:
                async with semaphore:
                    logger.info(f"Scraping: {url}...")
                    return await self.scrape_products(url)

            tasks = [worker(url) for url in urls]
            results = await asyncio.gather(*tasks)

            flat_results = [item for sublist in results if sublist for item in sublist]
            self.results = flat_results
            return flat_results

        finally:
            await self.close()

    def save_to_csv(self, filename: str = "dia_products.csv") -> None:
        """Save the scraped product results to a CSV file.

        This method converts the stored results into a pandas DataFrame and saves it
        to a CSV file with a custom index starting at 1.

        Args:
            filename (str, optional): The output filename for the CSV file.
                Defaults to "dia_products.csv".

        """
        if not self.results:
            logger.warning("No results to save.")
            return

        df = pd.DataFrame(self.results, index=[item["#"] for item in self.results])
        df.to_csv(filename, index_label="#")
        logger.info(f"Saved {len(df)} products to {filename}")


if __name__ == "__main__":
    scraper = DiaScraper(
        url=URL,
        headless=False,
    )
    asyncio.run(scraper.run())
    scraper.save_to_csv()
