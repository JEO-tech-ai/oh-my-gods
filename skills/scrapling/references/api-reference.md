# Scrapling API Reference

> Source: https://github.com/D4Vinci/Scrapling | License: BSD-3-Clause

---

## Installation

```bash
pip install scrapling                     # parser only
pip install "scrapling[fetchers]"         # + all fetchers
pip install "scrapling[all]"              # + all extras
pip install "scrapling[ai]"               # + MCP server
pip install "scrapling[shell]"            # + IPython shell
scrapling install                         # install browser binaries (Playwright)
```

---

## Fetcher classes

### `Fetcher` / `AsyncFetcher`

Static HTTP fetcher using curl_cffi for TLS fingerprint spoofing. No browser required.

```python
from scrapling.fetchers import Fetcher, AsyncFetcher

# Constructor
Fetcher(
    auto_save=False,        # bool — save element fingerprints for adaptive mode
    huge_tree=False,        # bool — enable lxml huge tree parsing
    keep_components=False,  # bool — keep CSS/JS/media in output
    storage="default",      # str — SQLite path for adaptive fingerprints
)

# Methods
page = Fetcher().get(url, **kwargs)         # GET request → Adaptor
page = Fetcher().post(url, data={}, **kwargs)  # POST request → Adaptor
page = await AsyncFetcher().get(url)        # async GET
page = await AsyncFetcher().post(url)       # async POST
```

### `FetcherSession`

Session wrapper around `Fetcher` that shares cookies and headers across requests.

```python
from scrapling.fetchers import FetcherSession

with FetcherSession(auto_save=False) as session:
    session.get(url)
    session.post(url, data={})
    page = session.get(protected_url)
```

### `DynamicFetcher` / `DynamicSession` / `AsyncDynamicFetcher` / `AsyncDynamicSession`

Playwright Chromium-based fetcher for JavaScript-rendered pages.

```python
from scrapling.fetchers import DynamicFetcher, DynamicSession, AsyncDynamicFetcher

DynamicFetcher(
    auto_save=False,
    huge_tree=False,
    keep_components=False,
    storage="default",
)

# .fetch() params
page = DynamicFetcher().fetch(
    url,
    headless=True,              # bool
    disable_resources=False,    # bool — skip images/fonts for speed
    wait_selector=None,         # str | None — CSS selector to wait for
    wait_timeout=30000,         # int — ms to wait for selector
    network_idle=False,         # bool — wait for network to go idle
    execute_js=None,            # str | None — JS to run after load
    scroll_to_bottom=False,     # bool — scroll to load lazy elements
)

# Session
with DynamicSession() as session:
    session.fetch(url)

# Async
page = await AsyncDynamicFetcher().fetch(url)
```

### `StealthyFetcher` / `StealthySession` / `AsyncStealthySession`

Anti-bot bypass fetcher with Cloudflare Turnstile support. Patches canvas, audio, WebGL fingerprints.

```python
from scrapling.fetchers import StealthyFetcher, StealthySession

StealthyFetcher(
    auto_save=False,
    huge_tree=False,
    keep_components=False,
    storage="default",
)

# .fetch() params (superset of DynamicFetcher + extras)
page = StealthyFetcher().fetch(
    url,
    headless=True,
    disable_resources=False,
    wait_selector=None,
    wait_timeout=30000,
    network_idle=False,
    execute_js=None,
    scroll_to_bottom=False,
    os_randomize=False,         # bool — randomize OS fingerprint (StealthyFetcher only)
    block_images=False,         # bool — block image loading
    # ... proxy params
    proxy=None,                 # str | None — proxy URL
)

# Prerequisite for full stealth mode
# pip install cairosvg
```

### `ProxyRotator`

Rotates through a list of proxies across requests.

```python
from scrapling.fetchers import ProxyRotator

rotator = ProxyRotator(proxies=["http://proxy1:port", "http://proxy2:port"])
rotator.rotate()  # returns next proxy URL
```

---

## Spider classes

### `Spider` (Abstract Base Class)

Scrapy-like concurrent crawler with adaptive fetching support.

```python
from scrapling.spiders import Spider, Request, Response

class MySpider(Spider):
    # Class attributes
    start_urls: list[str] = []
    concurrent_requests: int = 10
    download_delay: float = 0        # seconds between requests per domain
    crawldir: str | None = None      # checkpoint directory for pause/resume
    fetcher_class = Fetcher          # override with DynamicFetcher | StealthyFetcher

    async def configure_sessions(self, session) -> None:
        """Called once to configure session (set headers, login, etc.)."""
        pass

    async def parse(self, response: Response):
        """Default callback for start_urls. Must be overridden."""
        raise NotImplementedError

# Run
import asyncio
results = asyncio.run(MySpider().start())      # list[dict]
async for item in MySpider().stream():         # AsyncIterator[dict]
    ...
```

### `Request`

Represents a URL to fetch with a custom callback.

```python
from scrapling.spiders import Request

Request(
    url: str,
    callback = None,           # async callable(response: Response) → AsyncGenerator
    method: str = "GET",
    headers: dict = {},
    data: dict = {},
    meta: dict = {},           # arbitrary data passed to response
)
```

### `Response`

Response object passed to spider callbacks. Extends `Adaptor` (see below).

```python
response.url          # str — final URL
response.status       # int — HTTP status code
response.headers      # dict
response.meta         # dict — data from Request.meta
response.urljoin(path)  # build absolute URL from relative

# All Adaptor parsing methods available:
response.css(".title").getall()
response.xpath("//h1/text()").get()
```

### `CrawlResult`

Return type from `Spider.start()`.

```python
result.items    # list[dict] — all yielded items
result.stats    # dict — crawl statistics
```

---

## Adaptor (page / response object)

Returned by all fetcher calls. Wraps lxml parsing with CSS, XPath, and adaptive selection.

### Properties

```python
page.url        # str — final URL (after redirects)
page.status     # int — HTTP status code
page.headers    # dict — response headers
page.content    # bytes — raw response body
page.text       # str — decoded response body
page.encoding   # str — detected encoding
```

### Selection methods

```python
# CSS selector
page.css(selector, first_match=False, auto_save=False, adaptive=False)
# → SelectorList | Selector | None

# XPath
page.xpath(expr, first_match=False)
# → SelectorList | Selector | None

# Find all matching
page.find_all(selector, **kwargs)

# Find by exact text
page.find_by_text(text, first_match=False, case_sensitive=True)
# → Selector | SelectorList | None

# Find by regex pattern
page.find_by_regex(pattern, first_match=False)
# → Selector | SelectorList | None

# Find elements similar to a reference
page.find_similar(reference_element)
# → SelectorList
```

### Selector / SelectorList

```python
# Single result
selector.get()          # str — text content (or None)
selector.getall()       # list[str] — all text contents
selector.attrib         # dict — all attributes
selector.attrib["href"] # str — specific attribute value

# Navigation
selector.parent
selector.next_sibling
selector.previous_sibling
selector.children       # list[Selector]

# Further selection
selector.css(".child")
selector.xpath(".//span")

# CSS pseudo-elements
page.css(".item::text")         # → text node selector
page.css("a::attr(href)")       # → attribute selector
```

---

## MCP Server

```bash
pip install "scrapling[ai]"
python -m scrapling.mcp    # starts MCP server
```

### MCP tools

| Tool | Signature | Description |
|------|-----------|-------------|
| `get` | `url, css_selector=None` | Static HTTP GET |
| `bulk_get` | `urls: list[str], css_selector=None` | Concurrent static GET |
| `fetch` | `url, css_selector=None, headless=True, ...` | Dynamic fetch (JS rendering) |
| `bulk_fetch` | `urls: list[str], css_selector=None, ...` | Concurrent dynamic fetch |
| `stealthy_fetch` | `url, css_selector=None, headless=True, ...` | Anti-bot bypass fetch |
| `bulk_stealthy_fetch` | `urls: list[str], css_selector=None, ...` | Concurrent stealthy fetch |

`css_selector` pre-filters the page before returning content — dramatically reduces tokens.

### Claude Code MCP config

```json
{
  "mcpServers": {
    "scrapling": {
      "command": "python",
      "args": ["-m", "scrapling.mcp"]
    }
  }
}
```

---

## CLI

```bash
# IPython shell with pre-fetched page (provides `page` variable)
scrapling shell <url>

# Extract content and save
scrapling extract get <url> <output.md|txt|html>          # static
scrapling extract fetch <url> <output.md|txt|html>        # dynamic
scrapling extract stealthy-fetch <url> <output.md|txt|html>  # stealthy

# Install browser binaries
scrapling install
```

---

## Adaptive mode (element fingerprinting)

Scrapling saves element fingerprints (text content, tag, ancestors, siblings) in a local SQLite database. When enabled with `adaptive=True`, the selector engine tries the original CSS/XPath first, then falls back to fingerprint matching if the element has moved.

```python
# Step 1: First scrape — save fingerprints
f = Fetcher(auto_save=True, storage="./my_fingerprints.db")
page = f.get("https://example.com/")
titles = page.css(".product-title", auto_save=True)

# Step 2: Subsequent scrapes — relocate even if CSS path changed
page = f.get("https://example.com/")
titles = page.css(".product-title", adaptive=True)
```

---

## Pause / Resume crawls

```python
# crawldir stores checkpoint files (JSON per domain)
spider = MySpider(crawldir="./crawl_data/")
asyncio.run(spider.start())
# Ctrl+C → saves checkpoint
# Re-run → resumes from checkpoint
```

---

## Docker

```bash
docker pull pyd4vinci/scrapling
# or
docker pull ghcr.io/d4vinci/scrapling:latest

docker run -v $(pwd):/app pyd4vinci/scrapling python /app/my_scraper.py
```
