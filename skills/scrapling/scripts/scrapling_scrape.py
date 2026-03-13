#!/usr/bin/env python3
"""Scrapling CLI helper — scrape a URL with any fetcher type and extract by CSS/XPath.

Usage:
  python scrapling_scrape.py \
    --url https://quotes.toscrape.com/ \
    --css ".quote .text" \
    --output quotes.json

  python scrapling_scrape.py \
    --url https://example.com/spa \
    --fetcher dynamic \
    --css ".product-title" \
    --wait-selector "#app-loaded" \
    --output products.json

  python scrapling_scrape.py \
    --url https://protected-site.com \
    --fetcher stealthy \
    --css "article" \
    --network-idle \
    --output content.json

  python scrapling_scrape.py \
    --url https://blog.example.com/ \
    --xpath "//article//h2/text()" \
    --output headings.json

Output formats:
  .json   → JSON array of extracted strings
  .jsonl  → one JSON string per line
  .txt    → plain text, one result per line
  .html   → full page HTML (when no selector given)
  .md     → page text content
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrapling CLI — fetch and extract from websites."
    )
    parser.add_argument("--url", "-u", required=True, help="URL to scrape.")
    parser.add_argument(
        "--fetcher", "-f", default="static",
        choices=["static", "dynamic", "stealthy"],
        help="Fetcher type: static (default), dynamic (JS), stealthy (anti-bot).",
    )
    parser.add_argument("--css", "-c", help="CSS selector to extract (e.g. '.title').")
    parser.add_argument("--xpath", "-x", help="XPath expression to extract.")
    parser.add_argument(
        "--attribute", "-a", default=None,
        help="Attribute to extract (default: text). E.g. 'href' for links.",
    )
    parser.add_argument(
        "--first", action="store_true",
        help="Return only the first match.",
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Output file (default: print to stdout). Extension determines format: .json, .jsonl, .txt, .html, .md",
    )
    parser.add_argument(
        "--headless", action="store_true", default=True,
        help="Headless browser mode for dynamic/stealthy (default: True).",
    )
    parser.add_argument(
        "--no-headless", action="store_true",
        help="Run browser with visible window (dynamic/stealthy).",
    )
    parser.add_argument(
        "--disable-resources", action="store_true",
        help="Skip loading images/fonts/styles (faster, dynamic/stealthy only).",
    )
    parser.add_argument(
        "--wait-selector", default=None,
        help="CSS selector to wait for before extracting (dynamic/stealthy only).",
    )
    parser.add_argument(
        "--wait-timeout", type=int, default=30000,
        help="Wait timeout in ms (default: 30000).",
    )
    parser.add_argument(
        "--network-idle", action="store_true",
        help="Wait for network to go idle (dynamic/stealthy only).",
    )
    parser.add_argument(
        "--execute-js", default=None,
        help="JavaScript to execute after page load (dynamic/stealthy only).",
    )
    parser.add_argument(
        "--os-randomize", action="store_true",
        help="Randomize OS fingerprint (stealthy only).",
    )
    parser.add_argument(
        "--proxy", default=None,
        help="Proxy URL (e.g. http://user:pass@host:port).",
    )
    parser.add_argument(
        "--auto-save", action="store_true",
        help="Save element fingerprints for adaptive mode.",
    )
    parser.add_argument(
        "--adaptive", action="store_true",
        help="Use adaptive mode to relocate elements after site changes.",
    )
    parser.add_argument(
        "--find-text", default=None,
        help="Find elements by text content instead of CSS/XPath.",
    )
    parser.add_argument(
        "--find-regex", default=None,
        help="Find elements by regex pattern instead of CSS/XPath.",
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Print debug info (HTTP status, URL, element count).",
    )
    return parser.parse_args()


def build_fetcher(args: argparse.Namespace):
    try:
        from scrapling.fetchers import Fetcher, DynamicFetcher, StealthyFetcher
    except ImportError:
        print("ERROR: scrapling is not installed. Run: pip install scrapling", file=sys.stderr)
        sys.exit(1)

    fetcher_kwargs = dict(auto_save=args.auto_save)

    if args.fetcher == "static":
        return Fetcher(**fetcher_kwargs), "static"
    elif args.fetcher == "dynamic":
        return DynamicFetcher(**fetcher_kwargs), "dynamic"
    elif args.fetcher == "stealthy":
        return StealthyFetcher(**fetcher_kwargs), "stealthy"


def fetch_page(fetcher, fetcher_type: str, args: argparse.Namespace):
    headless = not args.no_headless

    if fetcher_type == "static":
        return fetcher.get(args.url)

    fetch_kwargs: dict = dict(
        headless=headless,
        disable_resources=args.disable_resources,
        wait_timeout=args.wait_timeout,
        network_idle=args.network_idle,
    )
    if args.wait_selector:
        fetch_kwargs["wait_selector"] = args.wait_selector
    if args.execute_js:
        fetch_kwargs["execute_js"] = args.execute_js
    if args.proxy:
        fetch_kwargs["proxy"] = args.proxy
    if fetcher_type == "stealthy" and args.os_randomize:
        fetch_kwargs["os_randomize"] = True

    return fetcher.fetch(args.url, **fetch_kwargs)


def extract_results(page, args: argparse.Namespace) -> list[str]:
    select_kwargs = {}
    if args.auto_save:
        select_kwargs["auto_save"] = True
    if args.adaptive:
        select_kwargs["adaptive"] = True
    if args.first:
        select_kwargs["first_match"] = True

    # Determine selector method
    if args.css:
        elements = page.css(args.css, **select_kwargs)
    elif args.xpath:
        elements = page.xpath(args.xpath, **{k: v for k, v in select_kwargs.items() if k not in ("auto_save", "adaptive")})
    elif args.find_text:
        elements = page.find_by_text(args.find_text, first_match=args.first)
    elif args.find_regex:
        elements = page.find_by_regex(args.find_regex, first_match=args.first)
    else:
        # No selector — return full page text or HTML
        return [page.text]

    if elements is None:
        return []

    # Normalize to list
    if not hasattr(elements, "__iter__") or isinstance(elements, str):
        elements = [elements]

    results = []
    for el in elements:
        if el is None:
            continue
        if args.attribute:
            val = el.attrib.get(args.attribute) if hasattr(el, "attrib") else None
            if val is not None:
                results.append(val)
        else:
            text = el.get() if hasattr(el, "get") else str(el)
            if text is not None:
                results.append(text.strip())

    return results


def save_output(results: list[str], output_path: str | None, args: argparse.Namespace, page=None) -> None:
    if output_path is None:
        # Print to stdout
        for r in results:
            print(r)
        return

    p = pathlib.Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    ext = p.suffix.lower()

    if ext == ".json":
        p.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    elif ext == ".jsonl":
        lines = "\n".join(json.dumps(r, ensure_ascii=False) for r in results)
        p.write_text(lines + "\n", encoding="utf-8")
    elif ext == ".txt":
        p.write_text("\n".join(results) + "\n", encoding="utf-8")
    elif ext == ".html" and page is not None:
        p.write_text(page.text, encoding="utf-8")
    elif ext == ".md":
        p.write_text("\n".join(results) + "\n", encoding="utf-8")
    else:
        # Default: JSON
        p.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Saved {len(results)} result(s) → {p}")


def main() -> None:
    args = parse_args()
    fetcher, fetcher_type = build_fetcher(args)

    selector_desc = args.css or args.xpath or args.find_text or args.find_regex or "(full page)"
    print(f"Fetching [{args.fetcher}]: {args.url}", file=sys.stderr)

    page = fetch_page(fetcher, fetcher_type, args)

    if args.debug:
        print(f"  Status: {page.status}", file=sys.stderr)
        print(f"  URL: {page.url}", file=sys.stderr)

    # Full page modes
    if not any([args.css, args.xpath, args.find_text, args.find_regex]):
        ext = pathlib.Path(args.output).suffix.lower() if args.output else ".txt"
        if ext == ".html":
            save_output([page.text], args.output, args, page=page)
        else:
            # Plain text
            text_content = page.css("body").get() or page.text
            save_output([text_content], args.output, args)
        return

    results = extract_results(page, args)

    if args.debug:
        print(f"  Extracted: {len(results)} result(s) for selector: {selector_desc}", file=sys.stderr)

    if not results:
        print(f"WARNING: No results for selector: {selector_desc}", file=sys.stderr)

    save_output(results, args.output, args, page=page)


if __name__ == "__main__":
    main()
