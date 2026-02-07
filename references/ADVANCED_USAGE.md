# proweb Advanced Usage Guide

## Scripts Included

### 1. `search.py` — Main Search & Scraping Tool

**Features:**
- Multi-source search (DuckDuckGo, Bing, Google, all)
- Scrape first result or any URL
- Extract text, links, images, tables
- Full command-line interface

**Installation:**
```bash
python3 -m pip install beautifulsoup4 lxml --break-system-packages
```

**Usage:**

#### Search Queries

```bash
# Basic search (DuckDuckGo)
python3 search.py "Python programming"

# Bing search (more results)
python3 search.py "web scraping tutorial" --source bing --count 10

# Try all sources
python3 search.py "machine learning" --source all --count 5

# Scrape first result
python3 search.py "OpenClaw documentation" --scrape
```

#### Scrape URLs

```bash
# Scrape any URL for all content
python3 search.py --scrape-url "https://example.com" --extract all

# Extract just text
python3 search.py --scrape-url "https://example.com" --extract text

# Extract just links
python3 search.py --scrape-url "https://github.com/trending" --extract links

# Extract images
python3 search.py --scrape-url "https://unsplash.com" --extract images

# Extract tables
python3 search.py --scrape-url "https://wikipedia.org/wiki/Python" --extract tables
```

**Output:** JSON with results array, each containing title, URL, snippet, source.

**Limitations:**
- Google results often empty (rate limited)
- No JavaScript rendering (use scraper_advanced.py for that)
- HTML pages only (no PDFs, images)

---

### 2. `scraper_advanced.py` — JavaScript-Capable Scraper

**Features:**
- Headless browser automation (Selenium or Playwright)
- Render JavaScript-heavy content
- Extract rendered DOM (not raw HTML)
- Form detection, button extraction
- Metadata extraction

**Installation:**

```bash
# For Selenium (slower, more robust):
pip3 install --break-system-packages selenium

# For Playwright (faster, recommended):
pip3 install --break-system-packages playwright
playwright install

# For Chrome/Chromium to work:
apt-get install chromium-browser chromium-chromedriver  # Or use existing browsers
```

**Usage:**

```bash
# Scrape with Selenium (default)
python3 scraper_advanced.py "https://example.com"

# Scrape with Playwright (faster)
python3 scraper_advanced.py "https://example.com" --method playwright

# Wait longer for JS to render
python3 scraper_advanced.py "https://example.com" --wait 10

# Headless mode (default: enabled)
python3 scraper_advanced.py "https://example.com" --headless
```

**Output:** JSON with:
- `text`: Rendered page text (3000 char limit)
- `headings`: H1-H3 tags
- `buttons`: Interactive buttons
- `forms`: Form fields and inputs
- `metadata`: Meta tags (Open Graph, etc.)
- `rendered`: Boolean (true = JS was executed)

**Use Cases:**
- Single-page applications (React, Vue, Angular)
- Dynamic content (AJAX loading)
- Form extraction
- Content behind payloads
- Rendering validation

---

## Real-World Examples

### Example 1: Research a Framework

```bash
python3 search.py "FastAPI tutorial" --source all --count 5 --scrape
```

This searches for FastAPI tutorials across all sources and scrapes the first result's content inline.

### Example 2: Gather GitHub Links

```bash
python3 search.py --scrape-url "https://github.com/trending" --extract links | jq '.links[] | .href'
```

Extracts all links from GitHub trending page and outputs just the URLs.

### Example 3: Extract Wikipedia Table Data

```bash
python3 search.py --scrape-url "https://en.wikipedia.org/wiki/Python_(programming_language)" --extract tables
```

Gets tables from Wikipedia's Python page (good for factual data extraction).

### Example 4: Monitor a Blog for Updates

```bash
# Find recent posts
python3 search.py "site:example.com/blog" --source duckduckgo --count 10

# Scrape first post for full content
python3 search.py "site:example.com/blog latest" --scrape
```

### Example 5: Extract Form Data

```bash
python3 scraper_advanced.py "https://example.com/contact" --method playwright --wait 3
```

Returns form fields, inputs, buttons from a contact form.

### Example 6: Batch Scraping

```bash
for url in "https://site1.com" "https://site2.com" "https://site3.com"; do
  echo "=== $url ==="
  python3 search.py --scrape-url "$url" --extract text | jq '.text_length'
done
```

Quick check of multiple pages' content size.

---

## Performance Tips

### 1. Use DuckDuckGo First

```bash
python3 search.py "query" --source duckduckgo  # ~2 sec
```

DuckDuckGo is fastest (no scraping, just API), then fallback to Bing.

### 2. Limit Results

```bash
python3 search.py "query" --count 3  # Faster than --count 50
```

Fewer results = faster response.

### 3. Targeted Extraction

```bash
python3 search.py --scrape-url "url" --extract text  # Faster
# Instead of:
python3 search.py --scrape-url "url" --extract all   # Slower (text + links + images + tables)
```

Extract only what you need.

### 4. Parallel Searches (bash)

```bash
python3 search.py "topic1" --count 3 > result1.json &
python3 search.py "topic2" --count 3 > result2.json &
python3 search.py "topic3" --count 3 > result3.json &
wait
cat result*.json | jq -s 'add'  # Combine results
```

Run multiple searches in parallel.

### 5. Cache Results

```bash
# Check if cache exists
[ -f "cache_query.json" ] && cat cache_query.json || {
  python3 search.py "query" --count 5 > cache_query.json
  cat cache_query.json
}
```

Avoid re-scraping the same URLs.

---

## Error Handling

### "Empty results on Google?"

Google aggressively blocks scrapers. Use Bing or DuckDuckGo instead:

```bash
python3 search.py "query" --source bing  # Works
python3 search.py "query" --source all   # DDG + Bing (no Google)
```

### "Timeout errors?"

Increase wait time:

```bash
python3 scraper_advanced.py "url" --wait 10  # Default 5 sec
```

Or increase curl timeout in search.py (edit the code).

### "JavaScript not rendering?"

Use the advanced scraper:

```bash
python3 scraper_advanced.py "url" --method playwright
```

search.py can't render JS — it fetches raw HTML only.

### "Cloudflare/WAF blocking?"

These require special handling. Try:

```bash
# May work with proper headers (search.py uses Mozilla UA)
python3 search.py --scrape-url "url" --extract text

# If blocked, use agent-browser skill instead
```

---

## Integration with OpenClaw

When used as an OpenClaw skill, you can call proweb from agent scripts:

```python
# In an OpenClaw agent script:
import subprocess
import json

def search_web(query, count=5):
    result = subprocess.run(
        ['python3', '/path/to/search.py', query, '--count', str(count)],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

results = search_web("machine learning")
for r in results['results']:
    print(f"{r['title']}: {r['url']}")
```

---

## Security & Ethics

**Please respect:**
- Website Terms of Service
- robots.txt directives
- Rate limits (space out requests)
- Don't scrape paywalled content
- Attribution when using scraped content

**Recommended practices:**
- Add delays between requests: `time.sleep(2)`
- Check `robots.txt` before scraping
- Use Bing/DDG instead of Google when possible
- Rotate user agents for large-scale scraping

---

## Troubleshooting Commands

```bash
# Test DuckDuckGo API directly
curl -s "https://api.duckduckgo.com/?q=python&format=json" | jq .

# Test Bing HTML response
curl -s -L "https://www.bing.com/search?q=python" | head -100

# Check if BeautifulSoup is installed
python3 -c "import bs4; print(bs4.__version__)"

# Run scraper with debugging
python3 search.py "query" 2>&1 | head -50

# Test advanced scraper
python3 scraper_advanced.py "https://example.com" 2>&1
```

---

## File Structure

```
proweb/
├── SKILL.md                    # Main skill documentation
├── scripts/
│   ├── search.py              # Main search + basic scraper (11KB)
│   └── scraper_advanced.py    # JavaScript-capable scraper (6KB)
└── references/
    └── ADVANCED_USAGE.md      # This file
```

---

**proweb v2: From quick searches to deep scraping. No API keys. No restrictions.** 🌀
