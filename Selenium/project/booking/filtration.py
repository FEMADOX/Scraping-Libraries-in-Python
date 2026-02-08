from selenium.webdriver.chrome.webdriver import WebDriver

from Selenium.project.booking.booking import By


class BookingFiltration:
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

    def apply_star_rating(
        self,
        *star_values: int,
    ) -> None:
        star_filtration_box = self.driver.find_element(By.ID, "filter_class")
        star_child_elements = star_filtration_box.find_elements(By.CSS_SELECTOR, "*")

        for _ in star_values:
            for star_element in star_child_elements:
                if (
                    str(star_element.get_attribute("innerHTML")).strip()
                    == "f {star_value} stars"
                ):
                    star_element.click()

    def sort_price_lowest_first(self) -> None:
        element = self.driver.find_element(By.CSS_SELECTOR, "")
        element.click()
