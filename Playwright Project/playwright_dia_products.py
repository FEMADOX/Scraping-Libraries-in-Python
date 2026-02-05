import asyncio
import logging
from typing import TYPE_CHECKING, cast

import pandas as pd
from bs4 import BeautifulSoup, Tag
from playwright.async_api import async_playwright

if TYPE_CHECKING:
    from typing import Any

    from playwright.async_api import Browser, Page

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

URL = "https://www.dia.es/freidora-de-aire-airfryer/c/L125"


async def set_up(browser: Browser, url: str) -> Page:
    """Set up a new browser page with specific configurations and navigates to url.

    This asynchronous function creates a new browser context with a predefined viewport
    size (1920x1080), opens a new page, and navigates to the specified URL. It attempts
    to handle cookie consent dialogs by clicking a 'Rechazar todas' button
    if one appears within a short timeout.

    Args:
        browser (Browser): The Playwright Browser instance.
        url (str): The target URL to navigate to.

    Returns:
        Page: The initialized Playwright Page object ready for interaction.

    """
    context = await browser.new_context(
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


async def get_full_urls_from_sidebar(page: Page) -> list[str]:
    """Extract full URLs from the sidebar of a DIA supermarket page.

    This function iterates through the sidebar category elements, simulating clicks to
    reveal hidden sub-categories. It then parses the HTML content to find specific
    links within those sub-categories that match defined criteria
    (excluding "Todo" items).

    Args:
        page (Page): The Playwright Page object representing the current browser tab.

    Returns:
        list[str]: A list of full URLs valid for scraping or further processing.
                   Note: Based on the implementation, this might return a nested list
                   structure (list[list[str]]) depending on how the `hrefs` are appended

    """
    # Iter through sidebar to get categories links
    sidebar = page.locator("div.categories-layout__left-content__list")
    categories_list_elements = sidebar.locator(
        "li[data-test-id='categories-list-element']",
    )

    count = await categories_list_elements.count()

    full_urls = []

    for number in range(count):
        element = categories_list_elements.nth(number)
        await element.scroll_into_view_if_needed()

        try:
            await element.hover()
            expand_button = element.locator(
                "span.dia-icon-plus.category-item__symbol-icon",
            )
            expand_button_visible = element.locator(
                "span.category-item__symbol-icon.dia-icon-minus.category-item__symbol-icon--visible",
            )

            if await expand_button.is_visible():
                await expand_button.click(timeout=1500)
            elif expand_button_visible.is_visible():
                logger.info(f"Element {number} already expanded.")
        except Exception:
            logger.exception(f"Could not click button for element {number}")

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
                    and tag.find("span")
                    and not tag.find_all("span")[1].text.strip().startswith("Todo")
                ),  # pyright: ignore[reportArgumentType]
            )

            hrefs = [link.get("href") for link in links]
            current_urls = [f"https://www.dia.es{href}" for href in hrefs if href]
            full_urls.extend(current_urls)

    await page.close()

    return full_urls


async def extract_products_from_page(page: Page) -> list[dict[str, Any]]:
    """Extract product info from a Playwright page object by scrolling to load content.

    This function continuously scrolls down the page until no new content is loaded,
    scraping product details (name, price, unit price) from HTML list items using
    BeautifulSoup. It handles duplicate products based on their names.

    Args:
        page (Page): The Playwright Page object representing the current browser tab.

    Returns:
        list[dict[str, Any]]: A list of dictionaries, where each dictionary represents
                            a unique product and contains keys for '#', 'name', 'price'
                            and 'price_per_unit'.

    """
    products = []
    added_products = set()
    reached_end = False

    # for _ in range(3):
    while not reached_end:
        content = await page.content()
        soup = BeautifulSoup(content, "lxml")
        containers = soup.find_all("li", class_="product-card-list__item-container")

        for container in containers:
            name = container.find("p", class_="search-product-card__product-name")
            price = container.find("p", class_="search-product-card__active-price")
            price_per_unit = container.find(
                "p",
                class_="search-product-card__price-per-unit",
            )

            if not name and not price and not price_per_unit:
                continue

            name = name.text.strip()

            if name in added_products:
                continue

            price = price.text.replace("\xa0", "")
            price_per_unit = price_per_unit.text.replace("\xa0", "").strip("() ")

            products.append({
                "#": len(products) + 1,
                "name": name,
                "price": price,
                "price_per_unit": price_per_unit,
            })

        previous_height = await page.evaluate("document.body.scrollHeight")

        await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
        await asyncio.sleep(2)

        new_height = await page.evaluate("document.body.scrollHeight")

        reached_end = new_height == previous_height

    return products


async def iter_through_urls(
    urls: list[str],
    browser: Browser,
) -> list[dict[str, Any]] | list[None]:
    """Iterate through all the urls inside a list to extract the info.

    This function uses Playwright to open each URL in a new browser page,
    extracts product information by calling the `extract_products_from_page` function
    and return the number of products found on each page.

    Args:
        urls (list[str]): List of URLs to iterate through.
        browser (Browser): The Playwright Browser instance to use for opening pages.

    Returns:
        list: A combined list of products extracted from all the URLs.

    """
    total_products = []

    semaphore = asyncio.Semaphore(1)

    async def worker(url: str) -> list[dict[str, Any]] | None:
        """Process each URL with concurrency control.

        Args:
            url (str): The URL to process.

        Returns:
            list[dict[str, Any]] | None: A list of products extracted from the page

        """
        async with semaphore:
            logger.info(f"Processing URL: {url}")

            try:
                page = await set_up(browser, url)

                products = await extract_products_from_page(page)
                logger.info(f"Found {len(products)} products on the page.")

                await page.close()
                return products
            except Exception:
                logger.exception(f"Error processing URL: {url}")
                return []

    tasks = [worker(url) for url in urls]
    results = await asyncio.gather(*tasks)

    for product_list in results:
        total_products.extend(product_list or [])

    return total_products


async def main() -> list[Any]:
    """Orchestrate the scraping process.

    This function initializes the Playwright browser, sets up the initial page context,
    extracts category URLs from the sidebar, iterates through these URLs to collect
    product data, and finally cleans up by closing the browser.

    Returns:
        list[Any]: A list containing the scraped product data.

    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        logger.info("Setting up page...")
        page = await set_up(browser, URL)

        logger.info("Extracting urls from sidebar...")
        full_urls = await get_full_urls_from_sidebar(page)

        logger.info("Iterating through urls and extracting products data...")
        products = await iter_through_urls(full_urls, browser)

        await browser.close()

        return products


if __name__ == "__main__":
    products = asyncio.run(main())
    df = pd.DataFrame(products, index=[product["#"] for product in products])

    df = df.drop(columns=["#"])
    df = df.rename(
        columns={
            "name": "Product Name",
            "price": "Price",
            "price_per_unit": "Price per Unit",
        },
    )

    df.to_csv("dia_products.csv", index_label="#")
