# 🕷️ Mastering Web Scraping with Python

This repository serves as a practical guide and a collection of examples designed to master web data extraction (Web Scraping) using the most powerful libraries in the Python ecosystem.

From simple HTTP requests to modern browser automation, this project documents the learning process through various approaches and techniques.

## 📚 Technologies & Libraries

The project covers the following key tools:

- **Requests & Requests-HTML**: For direct HTTP requests and basic session management.
- **Beautiful Soup 4**: For parsing and extracting data from HTML and XML documents.
- **Selenium**: For web browser automation, ideal for sites with heavy dynamic content (JavaScript).
- **Playwright**: The modern tool for automation, faster and more robust for complex web apps.
- **Aiohttp & Asyncio**: Advanced techniques for high-performance asynchronous and concurrent scraping.
- **Lxml**: Ultra-fast HTML processing.

## 📂 Project Structure

The repository is organized by technology and script type:

- `Beautiful Soup/`: Examples focused on cleaning and extracting static data.
- `Selenium/`: Scripts requiring browser interaction (clicks, scrolling, forms).
- `Playwright Project/`: Implementations using Microsoft's modern browser automation engine.
- `Code_Examples_spiders/`: A collection of "spiders" demonstrating the difference between synchronous and asynchronous approaches:
  - Asynchronous scripts: `async_spider.py`
  - Synchronous scripts: `sync_spider*.py`
- `main.ipynb`: Jupyter Notebook for interactive testing, data visualization, and rapid prototyping.

## 🚀 Installation

This project manages its dependencies using modern tooling.

```zsh
# Install dependencies using uv
uv sync
```

---
*Educational project for mastering data extraction techniques in Python.*
