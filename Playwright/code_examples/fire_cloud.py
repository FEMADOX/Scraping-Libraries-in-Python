import asyncio

from playwright.async_api import Browser, Page, Playwright, async_playwright


class FireCloudScraper:
    """A class to scrape data from FireCloud using Playwright.

    Attributes:
        headless (bool): Whether to run the browser in headless mode.
        url (str): The target URL to scrape.
        browser (Browser | None): The Playwright browser instance.
        playwright (Playwright | None): The Playwright instance.

    """

    def __init__(self, headless: bool = False) -> None:
        """Initialize the FireCloudScraper instance.

        Args:
            headless (bool): If True, runs the browser without a UI. Defaults to False.

        """
        self.url = "https://fyrecloud.ultraplus.click/"
        self.browser: Browser | None = None
        self.playwright: Playwright | None = None
        self.headless = headless

    async def set_up(self) -> Page:
        """Init Playwright, launch the browser, create a context, and open a new page.

        Returns:
            Page: The newly created Playwright page object.

        """
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        context = await self.browser.new_context()

        return await context.new_page()

    async def close(self) -> None:
        """Close the browser instance and stop the Playwright driver."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def run(self) -> None:
        """Execute the scraping process."""
        page = await self.set_up()
        await page.goto(self.url)

        # Login Process
        username_input = await page.wait_for_selector("#login-username")
        password_input = await page.wait_for_selector("#login-password")
        submit_input = await page.wait_for_selector(".btn.btn-primary")

        if not username_input or not password_input or not submit_input:
            print("Login fields not found.")
            await self.close()
            return

        await username_input.type("Saul Sondon", delay=100)
        await password_input.type("Estudia*", delay=100)
        await submit_input.click()

        await asyncio.sleep(5)


if __name__ == "__main__":
    scraper = FireCloudScraper()
    asyncio.run(scraper.run())
