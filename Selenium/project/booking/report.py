from typing import TYPE_CHECKING

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver


class BookingReport:
    """Collect and parse booking deal information from a Selenium WebDriver.

    Attributes:
        driver: The Selenium WebDriver instance used to query page elements.

    Methods:
        pull_deal_box_attributes: Extract hotel name, price, and score details.

    """

    def __init__(self, driver: WebDriver) -> None:
        """Initialize the report parser with a Selenium WebDriver."""
        self.driver = driver

    def pull_deal_box_attributes(self) -> list[list[str]]:
        """Collect hotel name, price, and score details from the deal cards.

        Returns:
            A list of lists containing hotel name, price, and score for each deal.

        """
        collection = []
        deal_boxes = self.driver.find_elements(
            By.CSS_SELECTOR,
            "div[data-testid='property-card']",
        )

        for deal_box in deal_boxes:
            # Extracting hotel name
            try:
                hotel_name = deal_box.find_element(
                    By.CSS_SELECTOR,
                    "div[data-testid='title']",
                ).text.strip()
            except NoSuchElementException:
                hotel_name = "N/A"

            # Extracting hotel price
            try:
                hotel_price = deal_box.find_element(
                    By.CSS_SELECTOR,
                    "span[data-testid='price-and-discounted-price']",
                ).text.strip()
            except NoSuchElementException:
                hotel_price = "N/A"

            # Extracting hotel score
            try:
                hotel_score = deal_box.find_element(
                    By.CSS_SELECTOR,
                    "div[data-testid='review-score'] div",
                ).text.strip()
            except NoSuchElementException:
                hotel_score = "N/A"

            collection.append([hotel_name, hotel_price, hotel_score])
        return collection
