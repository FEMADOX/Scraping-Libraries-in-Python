import logging
from typing import TYPE_CHECKING, Self

from selenium.webdriver.common.by import By

from selenium import webdriver
from Selenium.project.booking.constants import BASE_URL
from Selenium.project.booking.filtration import BookingFiltration
from Selenium.project.booking.report import BookingReport

if TYPE_CHECKING:
    from types import TracebackType

    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class Booking(webdriver.Chrome):
    """A class to automate interactions with the Booking.com website using Selenium.

    This class extends webdriver.Chrome to provide specific methods for navigating
    and interacting with booking.com features like currency selection, location search,
    date selection, and guest configuration. It supports context manager usage.
    """

    def __init__(
        self,
        teardown: bool = False,
        options: Options | None = None,
        service: Service | None = None,
        keep_alive: bool = True,
    ) -> None:
        """Initialize the Booking automation driver.

        Args:
            teardown (bool, optional): Whether to close the browser upon exiting the
                context. Defaults to False.
            options (Options | None, optional): Chrome options. Defaults to None.
            service (Service | None, optional): Service object for managing the browser
                driver. Defaults to None.
            keep_alive (bool, optional): Whether to keep the connection alive.
                Defaults to True.

        """
        self.teardown = teardown
        super().__init__(options, service, keep_alive)
        self.implicitly_wait(15)
        self.maximize_window()

    def __enter__(self) -> Self:
        """Enter the runtime context related to this object.

        Returns:
            Booking: The instance of the Booking class.

        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Exit the runtime context, optionally quitting the driver.

        Args:
            exc_type (type[BaseException] | None): The exception type, if an
                exception occurred.
            exc (BaseException | None): The exception instance, if an exception
                occurred.
            traceback (TracebackType | None): The traceback object, if an
                exception occurred.

        """
        if self.teardown:
            self.quit()

    def land_first_page(self) -> None:
        """Navigate to the base URL of Booking.com defined in constants."""
        self.get(BASE_URL)

    def change_currency(self, currency: str | None = None) -> None:
        """Change the currency on the website.

        Args:
            currency (str | None, optional): The currency code or identifier to select.
                Defaults to None.

        """
        currency_element = self.find_element(By.CSS_SELECTOR, "")
        currency_element.click()
        selected_currency_element = self.find_element(By.CSS_SELECTOR, "")
        selected_currency_element.click()

    def select_place_to_go(self, place_to_go: str | None = None) -> None:
        """Enter the destination into the search field and select the first result.

        Args:
            place_to_go (str | None, optional): The name of the place to go.
                Defaults to None.

        """
        search_field = self.find_element("")
        search_field.clear()
        search_field.send_keys(place_to_go) if place_to_go else None
        first_result = self.find_element(By.CSS_SELECTOR, "")
        first_result.click()

    def select_check_dates(
        self,
        check_in_date: str | None = None,
        check_out_date: str | None = None,
    ) -> None:
        """Select the check-in and check-out dates from the calendar.

        Args:
            check_in_date (str | None, optional): The check-in date string.
                Defaults to None.
            check_out_date (str | None, optional): The check-out date string.
                Defaults to None.

        """
        check_in_element = self.find_element(
            By.CSS_SELECTOR,
            f"td[data-date='{check_in_date}']",
        )
        check_in_element.click()
        check_out_element = self.find_element(
            By.CSS_SELECTOR,
            f"td[data-date='{check_out_date}']",
        )
        check_out_element.click()

    def select_adults(
        self,
        count: int = 1,
    ) -> None:
        """Adjust the number of adults in the search criteria.

        Decreases the number of adults to 1 before optionally increasing it.

        Args:
            count (int, optional): The target number of adults. Defaults to 1.

        """
        selection_element = self.find_element(By.CSS_SELECTOR)
        selection_element.click()

        while True:
            decrease_adults_element = self.find_element(
                By.CSS_SELECTOR,
                "button[arial_black='Decrease number of adults']",
            )

            decrease_adults_element.click()
            adults_value_element = self.find_element(By.CSS_SELECTOR, "")
            adults_value = adults_value_element.get_attribute(
                "value",
            )
            if not adults_value:
                break
            if int(adults_value) == 1:
                break

    def click_search(self) -> None:
        """Click the main search button to retrieve results."""
        search_button = self.find_element(By.CSS_SELECTOR, "")
        search_button.click()

    def apply_filtration(self) -> None:
        """Apply filtration options to the search results."""
        filtration = BookingFiltration(driver=self)
        filtration.apply_star_rating(3, 4, 5)
        filtration.sort_price_lowest_first()

    def report(self) -> None:
        """Generate a report of the scraped results to the terminal."""
        booking_report = BookingReport(self)
        table = booking_report.pull_deal_box_attributes()

        logger.info(f"{'Name':<50} {'Price':<20} {'Score':<10}")
        logger.info(f"{'-':<50} {'-':<20} {'-':<10}")
        for name, price, score in table:
            logger.info(f"{name:<50} {price:<20} {score:<10}")
