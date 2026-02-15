# Playwright Methods

In this section, we will look at the different methods when using `p.chromium`.

## Launch Chromium instance or create browser

This method allows us to create a browser:

```python
browser = p.chromium.launch()
```

### Launch Parameters

- **Headless Mode:** To make the browser visible and interactable (DOM), we use `headless=True` or `False`.

    ```python
    p.chromium.launch(headless=True)
    ```

- **Channel:** The channel or browser type (Chrome, Firefox, etc.). Options include `chrome`, `msedge`, etc.

    ```python
    p.chromium.launch(channel='chrome')
    ```

- **DevTools:** To see DevTools in real-time use the following parameter:

    ```python
    p.chromium.launch(devtools=True)
    ```

- **Downloads Path:** To create a directory to save downloads:

    ```python
    p.chromium.launch(downloads_path='./downloads')
    ```

- **Executable Path:** Path to the browser binary:

    ```python
    p.chromium.launch(executable_path=r'[executable path]')
    ```

- **Environment Variables:** Access environment variables for the browser:

    ```python
    p.chromium.launch(env={'data': 1})
    ```

- **Ignore Default Args:** Remove all arguments Playwright passes by default. We can set `True` or `False` or pass a list of arguments we don't want activated:

    ```python
    p.chromium.launch(ignore_default_args=True)
    ```

- **Ignore All Default Args:** Removes ALL default arguments:

    ```python
    p.chromium.launch(ignore_all_default_args=True)
    ```

- **Proxy:** Configure a proxy/connect from another server or IP to avoid blocks:

    ```python
    p.chromium.launch(proxy={'server': 'http://myproxy:3128'})
    ```

- **Timeout:** Wait time to launch the browser. The value will be a float:

    ```python
    p.chromium.launch(timeout=1.0)
    ```

## Create context

A context allows us to create an isolated 'virtual' browser within a browser instance to simulate independent users with their own cookies, local storage, and session.

For example, suppose we want to create a browser where each page has its own cookies independently. We should create two distinct contexts and a page for each context.

It would be as follows:

```python
browser = p.chromium.launch(headless=False)
context1 = browser.new_context()
context2 = browser.new_context()

page1 = context1.new_page()
page2 = context2.new_page()

page1.goto("https://example.com")
page2.goto("https://example.org")
browser.close()
```

### Get cookies

To get cookies use the following code:

```python
browser = p.chromium.launch()
cookies = browser.new_context().cookies()
```

### Add cookies

To add cookies use the following code:

```python
browser = p.chromium.launch()
browser.new_context().add_cookies()
```

## Create page

To create a page after creating a browser use the following code:

```python
browser = p.chromium.launch()
page = browser.new_page()
```

### Go to URL

To go to the address after creating the page use `goto()`:

```python
page.goto("https://books.toscrape.com/catalogue/page-1.html")
```

## Select an object and selection methods

To select an object (be it a radio button, a button, a form, etc.) we have three ways:

1. Use `locator()`
2. Use `query_selector` / `query_selector_all`
3. Use role, text, or XPath

### Selection methods

When selecting an object we must consider what we can select:

#### CSS Selector

- **By ID:**

    ```python
    field = page.locator("#username")
    ```

- **By Class:**

    ```python
    button = page.locator(".btn-primary")
    ```

- **By Tag:**

    ```python
    title = page.locator("h1")
    ```

- **Composite Selector:**

    ```python
    input_login = page.locator("form.login input[type='password']")
    ```

Apparently with `locator` if we use the `all()` method we can get all objects:

```python
page.locator().all()
```

#### XPath

- **By attribute:**

    ```python
    field = page.locator("//input[@id='username']")
    ```

- **By text inside the element:**

    ```python
    button = page.locator("//button[contains(text(), 'Submit')]")
    ```

- **By hierarchy:**

    ```python
    link = page.locator("//div[@class='menu']//a[@href='/home']")
    ```

#### By text

- **By internal text:**

    ```python
    button = page.locator("text=Log In")
    ```

### Use locator()

One way to interact is using locator():

```python
element = page.locator("input#email")
```

### Use query_selector / query_selector_all

- If you want only one object:

    ```python
    element = page.query_selector("div.card")
    ```

- If you want to get multiple elements:

    ```python
    elements = page.query_selector_all("div.item")
    for el in elements:
        print(el.inner_text())
    ```

### Use role, text or XPath

- **By text:**

    ```python
    button = page.get_by_text("Accept")
    ```

- **By XPath:**

    ```python
    title = page.locator("//h1")
    ```

## Actions

### Click an object

To click an object select it using one of the previous ways followed by the `click()` method:

```python
title = page.locator("//h1")
title.click()
```

### Extract text

To get the text of a selected object do it as follows:

| Method | Returns | Get text | Get attribute | Observations |
| :--- | :--- | :--- | :--- | :--- |
| `locator()` | Reusable Locator | `.text_content()` | `.get_attribute()` | Can chain actions, implicit wait. |
| `query_selector()` | Single ElementHandle | `.inner_text()` | `.get_attribute()` | Only one element, no automatic wait. |
| `get_by_text()` | Locator | `.text_content()` | `.get_attribute()` | Selection based on visible text. |

### Write text

Sometimes it is necessary to simulate `human behavior` and a good way is to type manually in the form.

To do this use the `keyboard` propiety + `type` method:

```python
form = page.locator('#mi-input')
form.keyboard.type('Hello world')
```

If we want to do it quickly we can do it with `fill()`:

```python
form = page.locator()
form.fill('Hello world')
```

### Execute Javascript code

To execute Javascript code do it as follows:

```python
title = page.evaluate("() => document.title")
```

## Page load or DOM check

Wait for the page to reach a specific load state.
Can be: `"load"` (document loaded), `"domcontentloaded"` (DOM ready), `"networkidle"` (no network requests).

```python
page.goto("https://example.com")
page.wait_for_load_state("networkidle")
```

Or directly with the parameter in `wait_until`:

```python
page.goto("https://example.com", wait_until="networkidle")
```

### Reload page

To reload the page do it as follows:

```python
page.reload(wait_until="domcontentloaded")
```

## Get listeners, events, Javascript functions

Sometimes Javascript code executes not just as a result of selecting a button or manipulating forms but seconds after page start, scrolling, selecting classes, etc.

We have roughly three ways to do this:

1. **Get all events starting with `on`:**

    ```python
    events = page.evaluate("""
            () => {
                const e = document.body
                return Object.keys(e).filter(k => k.startsWith('on') && e[k] !== null)
            }
        """)
    print(events)
    ```

2. **Get all listeners (DOM events) by adding a listener with `addEventListener`:**

    ```python
    page.evaluate("""
        (() => {
            const oldAddEventListener = Element.prototype.addEventListener
            window._eventListeners = []

            Element.prototype.addEventListener = function(type, listener, options) {
                window._eventListeners.push({
                    element: this.tagName + (this.id ? '#' + this.id : '') + (this.className ? '.' + this.className.replace(/\\s+/g, '.') : ''),
                    type: type,
                    listener: listener.toString()
                })
                oldAddEventListener.call(this, type, listener, options)
            }
        })
        """)
    events = page.evaluate("() => window._eventListeners")
    
    for e in events:
        print(f"Element: {e['element']}, Event: {e['type']}")
    ```

    In the previous case:
    1. Overwrite `Element.prototype.addEventListener` to capture all listeners added.
    2. Store info in `window._eventListeners`:
        - `element`: tag + id + classes of the element
        - `type`: event type (click, keydown, etc.)
        - `listener`: function code (as string)
    3. Use `page.evaluate()` to bring the list to Python.

3. **Finally with the following function get all listeners except those starting with `on`:**

    ```python
    elements = page.query_selector_all("*")

    all_events = []

    for el in elements:
        events = el.evaluate("""
            element => {
                // getEventListeners works only in DevTools
                if (typeof getEventListeners === "function") {
                    const listeners = getEventListeners(element)
                    const result = []
                    for (const [type, funcs] of Object.entries(listeners)) {
                        funcs.forEach(f => result.push({type: type, listener: f.listener.toString()}))
                    }
                    return result
                }
                return []
            }
        """)
        if events:
            tag = el.evaluate("el => el.tagName")
            all_events.append({"element": tag, "events": events})

    # Print results
    for item in all_events:
        print(f"Element: {item['element']}")
        for e in item["events"]:
            print(f"  Event: {e['type']}, Function: {e['listener'][:50]}...")
    ```

### Identify events

For example, to identify an event that executes when scrolling, consider the function can execute in various ways:

- **Inline in HTML:**

    ```html
    <body onscroll="loadMore()">
    ```

    The `loadMore()` function executes when you scroll. Obtain like this:

    ```javascript
    document.body.getAttribute("onscroll")
    ```

- **Assigned via JS property:**

    ```javascript
    window.onscroll = function() { console.log('scroll!') }
    window.onscroll.toString()
    ```

- **Added with `addEventListener`:**
    Return registered functions:

    ```javascript
    getEventListeners(window).scroll
    ```

Finally in Python to get scroll functions:

```python
scroll_listeners = page.evaluate("""
        () => {
            if (typeof getEventListeners === 'function') {
                return getEventListeners(window).scroll.map(f => f.listener.toString())
            }
            return []
        }
    """)
print("addEventListener scroll:", scroll_listeners)
```

## Create page and connect to Bright Data API and proxy

Here you start Playwright locally and route it through the Bright Data proxy. If you encounter a captcha, the example shows how to detect it and a pattern to use an external service (Bright Data Captcha Solver / Web Unlocker) to return the response and inject it:

```python
import asyncio
import time
import requests
from playwright.async_api import async_playwright

# Bright Data Proxy (example). Fill with your host/port/zone credentials.
BD_PROXY_HOST = "zproxy.lum-superproxy.io:22225"   # or the host/port indicated by Bright Data
BD_PROXY_USER = "your_proxy_user"
BD_PROXY_PASS = "your_proxy_password"

TARGET_URL = "https://example.com"

# Conceptual ENDPOINT for Bright Data Captcha Solver (placeholder).
# Check your dashboard / docs for real URL and parameters.
BD_CAPTCHA_SOLVER_API = "https://api.brightdata.com/captcha-solver/solve"  # placeholder


async def solve_captcha_with_brightdata(captcha_info):
    """
    Conceptual example: send captcha info to Bright Data service
    and receive a response to apply on page (e.g., token).
    IMPORTANTE: replace URL/params with what your dashboard/documentation indicates.
    """
    payload = {
        "site": captcha_info.get("site"),
        "type": captcha_info.get("type"),
        # other fields the API requires: sitekey, page_url, etc.
    }
    # Authentication: use what Bright Data indicates (API key or basic auth)
    # Here uses basic auth just as an example.
    resp = requests.post(BD_CAPTCHA_SOLVER_API, json=payload, auth=(BD_PROXY_USER, BD_PROXY_PASS), timeout=120)
    resp.raise_for_status()
    return resp.json()  # expects something like {'solution': 'token_string'}


async def main():
    proxy = {
        "server": f"http://{BD_PROXY_HOST}",
        "username": BD_PROXY_USER,
        "password": BD_PROXY_PASS
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, proxy=proxy)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(TARGET_URL, wait_until="load", timeout=60000)

        # Detect captcha (simple example: look for reCAPTCHA or hcaptcha iframe)
        iframe = await page.query_selector("iframe[src*='recaptcha'], iframe[src*='hcaptcha']")
        if iframe:
            print("Captcha detected — collecting info to solve...")
            # Extract sitekey or site info: example for reCAPTCHA
            sitekey = await page.evaluate("""
                () => {
                    const el = document.querySelector('[data-sitekey], div.g-recaptcha, textarea#g-recaptcha-response')
                    return el ? (el.getAttribute ? el.getAttribute('data-sitekey') : null) : null
                }
            """)
            captcha_info = {"site": TARGET_URL, "type": "recaptcha", "sitekey": sitekey}
            # Call external solver (placeholder): blocking in this example
            solution = await asyncio.get_event_loop().run_in_executor(None, solve_captcha_with_brightdata, captcha_info)
            token = solution.get("solution")
            if token:
                # Inject token and submit form (common pattern for reCAPTCHA)
                await page.evaluate("""(token) => {
                    // set g-recaptcha-response and submit forms that expect it
                    const ta = document.querySelector('textarea#g-recaptcha-response') || document.createElement('textarea')
                    ta.style.display = 'none'
                    ta.id = 'g-recaptcha-response'
                    ta.name = 'g-recaptcha-response'
                    ta.value = token
                    document.body.appendChild(ta)
                    // some sites require event dispatch or explicit submit:
                    const evt = new Event('change', {bubbles:true})
                    ta.dispatchEvent(evt)
                    // attempt form submit:
                    const f = document.querySelector('form')
                    if (f) f.submit()
                }""", token)
                print("Token injected, waiting for navigation...")
                await page.wait_for_load_state("networkidle", timeout=30000)
            else:
                print("Solver did not return token. Check response.")
        else:
            print("No captcha detected on initial load.")

        print("Final title:", await page.title())
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
```

## Create a custom browser

This method is the same as the previous one, the difference is that here we have a series of tools available to customize the bot more:

```python
p.chromium.launch_persistent_context(user_data_dir, **kwargs)
```

### Persistent Context Parameters

- **User Data Directory:** The folder where all user data will be saved:

    ```python
    p.chromium.launch_persistent_context(user_data_dir=r'C:\Users\Cash\Documents\pruebaspython')
    ```

    Arguments from `p.chromium.launch()` are used here too.

- **Accept Downloads:** Accept downloads. If `True` accepts automatic downloads:

    ```python
    p.chromium.launch_persistent_context(accept_downloads=True)
    ```

- **Geolocation:** To modify geolocation (latitude, longitude) we can use:

    ```python
    p.chromium.launch_persistent_context({"latitude": 52.5, "longitude": 13.4, "accuracy": 100})
    ```

- **HTTP Credentials:** For auth authentication use the following (user and password). Remember key names may vary:

    ```python
    p.chromium.launch_persistent_context(http_credentials={'user': '', 'password': ''})
    ```

- **Locale:** Change language:

    ```python
    p.chromium.launch_persistent_context(locale='es-ES')
    ```

- **Permissions:** Activate desired permissions. Pass a list:

    ```python
    p.chromium.launch_persistent_context(permissions=['geolocation','microphone'])
    ```

- **User Agent:** Define user/agent. This could be done in headers but can also be done here:

    ```python
    p.chromium.launch_persistent_context(user_agent='Arian')
    ```

- **Viewport:** To increase window resolution pass a dictionary with width or height keys or pass `None`. With `None` it sets to full screen.

    ```python
    p.chromium.launch_persistent_context(viewport={"width":1280, "height":720})
    p.chromium.launch_persistent_context(viewport=None)
    ```

- **Websocket Endpoint:** Pass the url, likely with user and password within, to connect:

    ```python
    p.chromium.connect(ws_endpoint='https://www.brightdata.arian.comida123.com:8080')
    ```

- **Timeout:** Set maximum connection time:

    ```python
    p.chromium.connect(ws_endpoint=url, timeout=3.0)
    ```

- **Headers:** Set headers:

    ```python
    p.chromium.connect(ws_endpoint=url, headers={})
    ```

## Connect to an existing browser

The `ws_endpoint` MUST always be present.
In this case we are not creating a browser but connecting to an existing one:

```python
p.chromium.connect(ws_endpoint, **kwargs)
```

### Connect to an existing browser via Chrome DevTools

With this method we connect to another browser using DevTools. Quite useful.

## Create session in Bright Data browsers

Now we will create a session on Bright Data servers to solve the captcha. The Captcha Solver is integrated and runs automatically when a challenge appears. Replace `BD_USERNAME`, `BD_PASSWORD` and `TARGET_URL` with your values.

Use the following code:

```python
import asyncio
from playwright.async_api import async_playwright

BD_USERNAME = "your_bd_user"     # from your Browser API zone (Overview)
BD_PASSWORD = "your_bd_password"    # from your Browser API zone (Overview)
TARGET_URL = "https://example.com"

# Bright Data FAQ indicates host brd.superproxy.io and port 9222 for CDP (wss://).
WS_ENDPOINT = f"wss://{BD_USERNAME}:{BD_PASSWORD}@brd.superproxy.io:9222"


async def main():
    async with async_playwright() as p:
        # Connect over CDP to endpoint provided by Bright Data
        browser = await p.chromium.connect_over_cdp(WS_ENDPOINT)
        # usually a context / page is already available in the session
        if browser.contexts:
            ctx = browser.contexts[0]
        else:
            ctx = await browser.new_context()
        # create/use a page
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        # Navigate: Browser API handles unlocking + CAPTCHA solving automatically.
        await page.goto(TARGET_URL, wait_until="load", timeout=60000)
        print("Title:", await page.title())

        # example: check for captcha selector (informational only)
        has_captcha = await page.query_selector("iframe[src*='recaptcha'], div.h-captcha")
        print("Captcha iframe detected on page?", bool(has_captcha))

        # interact normally (e.g. extract content)
        body = await page.content()
        print("HTML Length:", len(body))

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
```

- Use credentials from Browser API zone in your Bright Data panel.
- Bright Data solver resolves most CAPTCHAs automatically when using Browser API / Scraping Browser; plus you can use custom CDP functions to monitor the process (see docs).

## Login

If we need to login we can use the following command:

```python
page.fill("object_name", text)
```

When setting the object name we can do it as an XPath or class name like a CSS Selector. Remember in CSS Selectors spaces are filled with dots and start with a dot.

```python
await page.fill('.aui-field-input.aui-field-input-text.aui-form-validator-error', 'your_text_to_insert')
```

Or with XPath:

```python
await page.fill('input[name="_58_login"]', 'your_username')
```

And to go to the page use for the button:

```python
page.click('button[type="submit"]')
```

Followed by:

```python
page.wait_for_navigation() # This code allows us to wait until reaching the page
```

## Playwright code generator

Unlike Selenium, with Playwright we can generate Python code as we navigate pages as if recording a macro.

![playwright code generator](../assets/img/image6.png)

As we interact with the web page everything is recorded in this window and we can use this code for web scraping.

To use this tool open any terminal and press:

```bash
python -m playwright codegen
```

### Example

```python
async def open_and_download_multiple_browser(self,context, url):
    """
    DO NOT USE ALONE-------------------

    This function works with loop_browser()
    This function is managed to fetch the content of every tab tab openend
    
    """
    page = await context.new_page()
    await page.goto(url)
    await page.wait_for_timeout(1300)
    content = await page.content()
    await page.close()
    
    return content

async def loop_browser(self,urls):
    """
    This function opens a browser and asynchronly opens multiple pages inheriting 'context' created object and executes the function
    open_and_download_multiple_browser().
    It returns a list with all the json/html content of every page opened
    
    """
    self.urls = urls
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        tasks = [self.open_and_download_multiple_browser(context, url) for url in self.urls]
        contents = await asyncio.gather(*tasks)
        await browser.close()
        return contents
```
