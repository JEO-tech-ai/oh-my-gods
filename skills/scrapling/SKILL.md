---
name: scrapling
description: >
  Adaptive web scraping framework with multiple fetcher types (static HTTP,
  dynamic Playwright, stealth anti-bot bypass), Scrapy-like spiders, and
  adaptive CSS/XPath selectors that auto-relocate elements after site changes.
  Use when scraping websites, bypassing anti-bot protection, running Scrapy-like
  crawls, or needing MCP-based browser automation tools.
  Triggers on: "scrapling", "web scraping", "adaptive scraping", "bypass cloudflare",
  "scrape website", "crawl site", "web crawler", "fetch page", "stealthy fetch",
  "dynamic scraping", "playwright scraping", "anti-bot bypass", "web extraction",
  "html parsing", "css selector scraping", "xpath scraping".
allowed-tools: Bash Read Write Edit Glob Grep
compatibility: Python 3.10+. Dynamic/Stealthy fetchers require browser install via `scrapling install`. Stealth requires cairosvg (`pip install cairosvg`).
license: BSD-3-Clause
metadata:
  tags: web-scraping, crawling, adaptive, playwright, anti-bot, mcp, python
  version: "1.0"
  source: https://github.com/D4Vinci/Scrapling
---

# Scrapling — Adaptive Web Scraping

> Python web scraping framework (D4Vinci) with adaptive element tracking,
> 4 fetcher types (static → dynamic → stealth), Scrapy-like spiders,
> MCP server, and CLI. Adapts to site changes — CSS selectors that worked
> yesterday still work today even if the site restructured.

## When to use this skill

- Scrape websites that change layout or restructure HTML over time (adaptive mode)
- Bypass anti-bot protection and Cloudflare Turnstile (StealthyFetcher)
- Run concurrent crawls with pause/resume across thousands of pages (Spider)
- Fetch rendered JavaScript-heavy pages (DynamicFetcher)
- Connect via MCP to provide browser automation tools to AI agents
- Quick one-off scraping from CLI (`scrapling shell`, `scrapling extract`)

---

## Instructions

### Step 1: Install

```bash
# Parser only (no browser bindings) — lightest
pip install scrapling

# Static + dynamic + stealthy fetchers
pip install "scrapling[fetchers]"
scrapling install   # downloads browser binaries (Playwright Chromium)

# All dependencies
pip install "scrapling[all]"
scrapling install

# MCP server support
pip install "scrapling[ai]"

# IPython shell support
pip install "scrapling[shell]"

# Docker (pre-built with all dependencies)
docker pull pyd4vinci/scrapling
# or
docker pull ghcr.io/d4vinci/scrapling:latest
```

### Step 2: Choose the right fetcher

| Fetcher | Best for | Anti-bot | JS rendering | Speed |
|---------|----------|----------|--------------|-------|
| `Fetcher` / `AsyncFetcher` | Static sites, APIs | Basic TLS | No | Fastest |
| `DynamicFetcher` / `DynamicSession` | JS-heavy pages | Basic | Yes (Playwright) | Medium |
| `StealthyFetcher` / `StealthySession` | Cloudflare, bot detection | Strong | Yes + stealth patches | Slowest |
| `ProxyRotator` | Proxy rotation helper | — | — | — |

### Step 3: Static fetching (Fetcher / AsyncFetcher)

```python
from scrapling.fetchers import Fetcher, AsyncFetcher

# Synchronous
page = Fetcher().get("https://quotes.toscrape.com/")
print(page.status)  # HTTP status code
print(page.url)     # final URL (after redirects)

# Navigate the HTML
quotes = page.css(".quote .text")     # CSS selector → list of elements
texts = page.css(".quote .text").getall()  # → list of strings
first = page.css(".quote .text").get()     # → first string

# xpath
authors = page.xpath("//small[@class='author']/text()").getall()

# Find by text content
link = page.find_by_text("Next", first_match=True)

# Find similar elements to a reference
header = page.css("h1").get()
similar_headers = page.find_similar(header)  # finds other h1/h2-like elements

# Async
import asyncio
async def main():
    page = await AsyncFetcher().get("https://quotes.toscrape.com/")
    print(page.css("h1").get())

asyncio.run(main())
```

### Step 4: Session-based fetching (cookies / auth)

```python
from scrapling.fetchers import FetcherSession

with FetcherSession() as session:
    session.get("https://example.com/login", data={"user": "...", "pass": "..."})
    page = session.get("https://example.com/protected")
    print(page.css(".content").get())
```

### Step 5: Dynamic fetching with JavaScript rendering

```python
from scrapling.fetchers import DynamicFetcher, AsyncDynamicFetcher

# Synchronous — headless Playwright Chromium
page = DynamicFetcher().fetch("https://example.com/spa")

# Wait for a specific element to appear
page = DynamicFetcher().fetch(
    "https://example.com",
    wait_selector=".loaded-content",
    wait_timeout=10000,     # ms
    headless=True,
    disable_resources=True,  # skip images/fonts for speed
)

# Session (shared cookies/browser state)
from scrapling.fetchers import DynamicSession
with DynamicSession() as session:
    session.fetch("https://example.com/login", execute_js="document.querySelector('#btn').click()")
    page = session.fetch("https://example.com/dashboard")

# Async
async def main():
    page = await AsyncDynamicFetcher().fetch("https://example.com/spa")
```

### Step 6: Stealthy fetching (anti-bot bypass)

```python
from scrapling.fetchers import StealthyFetcher, StealthySession

# Bypass Cloudflare Turnstile and advanced bot detection
page = StealthyFetcher().fetch(
    "https://protected-site.com",
    headless=True,
    network_idle=True,      # wait for network to go idle
    disable_resources=True,
    os_randomize=True,      # randomize OS fingerprint
)

# With session (persistent browser context)
with StealthySession() as session:
    page = session.fetch("https://protected-site.com")
    data = page.css(".protected-content").getall()
```

> **Prerequisite**: `pip install cairosvg` for canvas fingerprint patching (required for stealth mode)

### Step 7: Adaptive scraping (handle site changes)

Adaptive mode remembers how elements were found and auto-relocates them after site restructuring.

```python
from scrapling.fetchers import Fetcher

f = Fetcher(auto_save=True)  # save element fingerprints on first scrape

# First scrape — saves element fingerprints to local database
page = f.get("https://example.com/")
titles = page.css(".product-title", auto_save=True)
print(titles.getall())

# After site changes, use adaptive=True to relocate elements
page = f.get("https://example.com/")
titles = page.css(".product-title", adaptive=True)  # auto-relocates
print(titles.getall())
```

### Step 8: Spider (concurrent multi-page crawling)

```python
from scrapling.spiders import Spider, Request, Response

class QuotesSpider(Spider):
    start_urls = ["https://quotes.toscrape.com/"]
    concurrent_requests = 5
    download_delay = 1.0  # seconds between requests

    async def configure_sessions(self, session):
        # Called once per session — set headers, login, etc.
        session.headers.update({"User-Agent": "MyBot/1.0"})

    async def parse(self, response: Response):
        # Called for each fetched page
        quotes = response.css(".quote .text").getall()
        authors = response.css(".quote .author").getall()

        for quote, author in zip(quotes, authors):
            yield {"quote": quote, "author": author}

        # Follow pagination
        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield Request(url=response.urljoin(next_page), callback=self.parse)

# Run the spider
import asyncio
results = asyncio.run(QuotesSpider().start())
for item in results:
    print(item)

# Stream results as they arrive
async for result in QuotesSpider().stream():
    print(result)
```

### Step 9: Pause and resume crawls

```python
# Pass crawldir to checkpoint progress — Ctrl+C saves, restart resumes
spider = QuotesSpider(crawldir="./crawl_data")
asyncio.run(spider.start())
# If interrupted: re-run the same line — automatically resumes from checkpoint
```

### Step 10: CLI usage

```bash
# IPython shell with a pre-fetched page
scrapling shell https://quotes.toscrape.com/
# Provides `page` variable — try: page.css(".quote").getall()

# Extract page content and save
scrapling extract get https://quotes.toscrape.com/ output.md
scrapling extract fetch https://example.com/spa output.md       # DynamicFetcher
scrapling extract stealthy-fetch https://cf-site.com output.md  # StealthyFetcher
```

### Step 11: MCP server (for AI agents)

```python
# Start MCP server
pip install "scrapling[ai]"
python -m scrapling.mcp
```

Add to Claude Code MCP config:
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

MCP tools available:
| Tool | Description |
|------|-------------|
| `get` | Static HTTP GET (Fetcher) |
| `bulk_get` | Concurrent static GET for multiple URLs |
| `fetch` | Dynamic fetch with JS rendering (DynamicFetcher) |
| `bulk_fetch` | Concurrent dynamic fetch |
| `stealthy_fetch` | Anti-bot bypass fetch (StealthyFetcher) |
| `bulk_stealthy_fetch` | Concurrent stealthy fetch |

All MCP tools accept an optional `css_selector` to pre-filter the page and return only matching content — reduces tokens sent to the LLM.

---

## Key parameters

### Fetcher constructor params

| Parameter | Default | Description |
|-----------|---------|-------------|
| `auto_save` | `False` | Save element fingerprints for adaptive mode |
| `huge_tree` | `False` | Enable lxml huge tree for very large pages |
| `keep_components` | `False` | Keep CSS/JS/media tags in parsed output |
| `storage` | `'default'` | SQLite storage path for adaptive fingerprints |

### DynamicFetcher / StealthyFetcher fetch params

| Parameter | Default | Description |
|-----------|---------|-------------|
| `headless` | `True` | Headless browser mode |
| `disable_resources` | `False` | Skip images/fonts/styles (faster) |
| `wait_selector` | `None` | CSS selector to wait for before returning |
| `wait_timeout` | `30000` | Milliseconds to wait for selector |
| `network_idle` | `False` | Wait for network to go idle |
| `execute_js` | `None` | JavaScript to execute on page load |
| `os_randomize` | `False` | Randomize OS fingerprint (StealthyFetcher only) |

### Spider class attrs

| Attribute | Default | Description |
|-----------|---------|-------------|
| `start_urls` | `[]` | Initial URLs to crawl |
| `concurrent_requests` | `10` | Max parallel requests |
| `download_delay` | `0` | Seconds between requests per domain |
| `crawldir` | `None` | Directory to checkpoint crawl state |
| `fetcher_class` | `Fetcher` | Override with DynamicFetcher or StealthyFetcher |

---

## Element selection API

```python
# CSS and XPath
elements = page.css(".quote")              # all matches
element = page.css(".quote", first_match=True)  # first only
texts = page.css(".quote::text").getall() # text via ::text pseudo
hrefs = page.css("a::attr(href)").getall() # attribute via ::attr()
page.xpath("//h1/text()").get()

# Text search
el = page.find_by_text("Next", first_match=True)  # exact text match
els = page.find_by_regex(r"\d{4}-\d{2}-\d{2}")   # regex text match

# Similar elements (find elements similar to a reference)
ref = page.css("h1").get_element()
page.find_similar(ref)

# Navigation
el.parent
el.next_sibling
el.previous_sibling
el.children

# Attribute access
el.attrib["href"]
el.text
el.get()      # text content
el.getall()   # all text contents
```

---

## Examples

### Example 1: Scrape static page

```python
from scrapling.fetchers import Fetcher

page = Fetcher().get("https://quotes.toscrape.com/")
for quote in page.css(".quote"):
    text = quote.css(".text").get()
    author = quote.css(".author").get()
    print(f"{author}: {text}")
```

### Example 2: JS-rendered SPA

```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher().fetch(
    "https://example.com/spa",
    wait_selector="#app-loaded",
    disable_resources=True,
)
data = page.css(".item-title").getall()
```

### Example 3: Bypass Cloudflare

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher().fetch(
    "https://cloudflare-protected.com",
    headless=True,
    network_idle=True,
    os_randomize=True,
)
content = page.css("main").get()
```

### Example 4: Multi-page spider with checkpoint

```python
import asyncio
from scrapling.spiders import Spider, Request, Response

class BlogSpider(Spider):
    start_urls = ["https://blog.example.com/"]
    concurrent_requests = 3
    download_delay = 2.0

    async def parse(self, response: Response):
        for post in response.css("article.post"):
            yield {
                "title": post.css("h2").get(),
                "date": post.css("time").get(),
                "url": post.css("a::attr(href)").get(),
            }
        next_url = response.css(".pagination .next::attr(href)").get()
        if next_url:
            yield Request(url=response.urljoin(next_url), callback=self.parse)

results = asyncio.run(BlogSpider(crawldir="./blog_crawl").start())
```

---

## Best practices

1. **Start with `Fetcher`** — use `DynamicFetcher` only when JavaScript rendering is needed, `StealthyFetcher` only for anti-bot sites
2. **`disable_resources=True`** — skip images/fonts/styles for 2–5× faster dynamic fetching
3. **`auto_save=True` → `adaptive=True`** — save fingerprints first, then use adaptive on subsequent scrapes to handle site changes
4. **`crawldir` for large crawls** — always set a checkpoint directory so large jobs survive interruption
5. **`download_delay`** — add respectful delays between requests on the same domain
6. **CSS selector with MCP** — pass `css_selector` to MCP tools to pre-filter pages; reduces tokens by 80–90%
7. **Proxy rotation** — use `ProxyRotator` or set `proxies` param on fetchers for distributed scraping

---

## Scripts

- **`scripts/scrapling_scrape.py`** — CLI wrapper: scrape a URL with any fetcher type, extract by CSS/XPath, save output

```bash
# Static scrape, extract CSS
python scripts/scrapling_scrape.py \
  --url https://quotes.toscrape.com/ \
  --css ".quote .text" \
  --output quotes.json

# Dynamic (JS rendering)
python scripts/scrapling_scrape.py \
  --url https://example.com/spa \
  --fetcher dynamic \
  --css ".product-title" \
  --output products.json

# Stealthy (Cloudflare bypass)
python scripts/scrapling_scrape.py \
  --url https://protected-site.com \
  --fetcher stealthy \
  --css "main article" \
  --output content.json
```

---

## References

- [GitHub: D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling)
- [PyPI: scrapling](https://pypi.org/project/scrapling/)
- [Docker Hub: pyd4vinci/scrapling](https://hub.docker.com/r/pyd4vinci/scrapling)
- [MCP Server Documentation](https://github.com/D4Vinci/Scrapling/blob/main/docs/ai/mcp-server.md)
- [Fetchers Documentation](https://github.com/D4Vinci/Scrapling/blob/main/docs/fetchers)
- [Spiders Documentation](https://github.com/D4Vinci/Scrapling/blob/main/docs/spiders)
- [Adaptive Scraping Guide](https://github.com/D4Vinci/Scrapling/blob/main/docs/adaptive-scraping.md)
