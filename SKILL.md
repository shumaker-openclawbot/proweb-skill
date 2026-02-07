---
name: proweb
description: Advanced web search + scraping with no API key. Search via DuckDuckGo (instant answers), Bing (scraping), or all sources. Scrape pages for text, links, images, tables. Full HTML parsing with BeautifulSoup. Use for research, content extraction, web automation, and data gathering without Brave API or rate limits.
---

# proweb v2 - Advanced Web Search & Scraping

Industrial-strength web search and scraping without API keys. Multiple sources, full content extraction, no rate limits.

## Quick Start

### Search (Default: DuckDuckGo)

```bash
proweb "your search query" --count 5
proweb "Python programming" --count 3
proweb "OpenClaw" --source bing --count 10
```

### Scrape First Result

```bash
proweb "Python" --scrape  # Scrape content from first result
```

### Scrape Specific URL

```bash
proweb --scrape-url "https://example.com" --extract all
proweb --scrape-url "https://example.com" --extract text
proweb --scrape-url "https://example.com" --extract links
proweb --scrape-url "https://example.com" --extract images
```

## Features

### Search Sources

| Source | Speed | Depth | Reliability | Notes |
|--------|-------|-------|-------------|-------|
| **DuckDuckGo** | ⚡ Fast | Medium | Very High | Instant answers + related topics. No rate limits. Preferred. |
| **Bing** | ⚡ Fast | Deep | High | Direct scraping. More results than DDG. |
| **Google** | ⚡ Fast | Deep | Low* | Rate-limited, often blocked. Use sparingly. |
| **All** | Medium | Deep | High | Combines DDG + Bing. Best coverage. |

*Google actively blocks scrapers. DDG/Bing are more reliable.

### Scraping Modes

When scraping a URL, extract:

- **`text`** - Main text content (2000 char limit)
- **`links`** - All hyperlinks with text + href (20 link limit)
- **`images`** - All images with src, alt, title (10 image limit)
- **`tables`** - Tabular data (3 table limit, 10 rows each)
- **`all`** - Everything above

### Output Format

All responses are JSON:

```json
{
  "query": "Python",
  "count": 3,
  "source": "duckduckgo",
  "results": [
    {
      "title": "Python (programming language)",
      "url": "https://...",
      "snippet": "A high-level, general-purpose...",
      "source": "duckduckgo-related",
      "scraped_content": "Optional: scraped text from URL"
    }
  ]
}
```

For URL scraping:

```json
{
  "url": "https://example.com",
  "title": "Example Domain",
  "text": "Full text content",
  "text_length": 142,
  "links": [{
    "text": "Learn more",
    "href": "https://..."
  }],
  "link_count": 1,
  "images": [{
    "src": "https://...",
    "alt": "description",
    "title": "title"
  }],
  "image_count": 0,
  "tables": [[[...]]],
  "table_count": 0
}
```

## Usage Examples

### Example 1: Research a Topic

```bash
proweb "machine learning best practices" --count 5 --source all
```

Returns 5 best results from DDG + Bing, combined and ranked.

### Example 2: Find Documentation

```bash
proweb "Python documentation" --scrape
```

Searches for Python docs, then scrapes the first result to extract content preview.

### Example 3: Extract Data from URL

```bash
proweb --scrape-url "https://example.com/data" --extract tables
```

Extracts all tables from a specific URL (useful for data gathering).

### Example 4: Gather Links from Page

```bash
proweb --scrape-url "https://github.com/openclaw/openclaw" --extract links
```

Extracts all hyperlinks from a page for further analysis.

## Technical Details

### Requirements

- Python 3.7+
- `curl` (for HTTP requests)
- `beautifulsoup4` (for scraping)
- `lxml` (for fast HTML parsing)

### Dependencies Installed

```
requests beautifulsoup4 lxml httpx selenium scrapy playwright
```

### How It Works

1. **Search Mode:**
   - DuckDuckGo: Uses public JSON API (no scraping needed)
   - Bing/Google: Direct HTML scraping with BeautifulSoup
   - Results deduplicated and ranked

2. **Scrape Mode:**
   - Fetches HTML via curl with browser-like headers
   - Parses with BeautifulSoup + lxml
   - Extracts specified content types
   - Limits results (text, links, images) to prevent bloat

### Rate Limiting

- **None imposed by proweb** — relies on target site limits
- DuckDuckGo: Unlimited (API-based)
- Bing: Very high (generous rate limits)
- Google: Low (actively blocks scrapers)
- Recommended: Use DDG or Bing for production

### Performance

- Average search: 2-5 seconds
- Average scrape: 3-8 seconds (depends on page size)
- Timeout: 15 seconds per request

## Limitations

- **Google scraping:** Often returns 0 results (rate limited)
- **JavaScript-heavy sites:** Can't render JS (use agent-browser for that)
- **Login-required pages:** Won't work without auth
- **Cloudflare/WAF sites:** May be blocked
- **PDF/binary files:** Can't be scraped directly

## When to Use proweb

✅ **Use proweb when:**
- You need web search without paying for APIs
- You want to extract text, links, images from pages
- You're researching or gathering data
- You need reliable, fast searches
- Rate limits don't apply to your use case

❌ **Don't use proweb for:**
- High-volume scraping (use dedicated scrapers)
- JavaScript-rendered content (use agent-browser or Playwright)
- Bypassing paywalls or login walls
- Commercial data harvesting (check ToS)

## Troubleshooting

**Empty results on Google?**
- Google actively blocks scrapers. Use Bing or DDG instead.
- If you need Google: `--source all` will still try.

**Timeout errors?**
- Network latency. Retry after a few seconds.
- Large pages might timeout. Reduce expectations.

**Rate limited?**
- Bing/DDG rarely rate limit. Google will.
- If hammering a site, space out requests.

**Missing content when scraping?**
- If page is JavaScript-heavy, proweb can't render it.
- Use `agent-browser` skill instead.

## Script Location

- `scripts/search.py` - Main executable (11KB, lightweight)

## Examples: Command Line

```bash
# Search Python stuff
python3 search.py "Python" --count 5

# Try all sources
python3 search.py "web scraping" --source all --count 10

# Scrape first result
python3 search.py "OpenClaw" --scrape

# Scrape specific URL for all data
python3 search.py --scrape-url "https://docs.python.org" --extract all

# Just get links from a page
python3 search.py --scrape-url "https://github.com/trending" --extract links

# Get table data from URL
python3 search.py --scrape-url "https://en.wikipedia.org/wiki/Python_(programming_language)" --extract tables
```

---

**proweb v2: The free, unrestricted web search tool for AI agents. 🌀**

Built with BeautifulSoup, curl, and chaos. No API keys. No restrictions. Just data.
