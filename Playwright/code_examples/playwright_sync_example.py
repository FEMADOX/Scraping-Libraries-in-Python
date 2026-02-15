from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://books.toscrape.com/catalogue/page-1.html")
        html = page.content()
        soup = BeautifulSoup(html, "lxml")

        books = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")

        for item in books:
            title = item.h3.a.attrs["title"]
            print(title)


main()
