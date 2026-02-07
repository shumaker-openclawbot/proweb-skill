---
name: proweb
description: Advanced multi-source web search engine with intelligent scraping. Combines DuckDuckGo, Bing, Google, Wikipedia, and arXiv with automatic ranking and deduplication.
metadata:
  clawdbot:
    emoji: "🌐"
    homepage: "https://clawhub.com/proweb"
    os: ["darwin", "linux", "win32"]
    requires:
      bins: ["python", "curl"]
      libs: ["beautifulsoup4", "lxml"]
    install:
      - type: "script"
        run: "install.sh"
        description: "Install Python dependencies"
---

# proweb v3 - Advanced Multi-Source Search Engine

Professional-grade web search combining 5+ sources with intelligent ranking, deduplication, and smart scraping. No API keys. No rate limits.

## Quick Start

### Multi-Source Search (Best)

```bash
python3 search_v3.py "your query" --count 10
python3 search_v3.py "bitcoin prediction" --sources ddg,bing --count 5
python3 search_v3.py "machine learning" --deep --count 20
```

### Deep Research (All Sources)

```bash
python3 search_v3.py "AI advances 2026" --deep
# Searches: DuckDuckGo + Bing + Google + Wikipedia + arXiv
```

### Scrape with Intelligence

```bash
python3 search_v3.py --scrape-url "https://example.com" --extract smart
python3 search_v3.py --scrape-url "https://example.com" --extract all
```

### Scrape All Results

```bash
python3 search_v3.py "topic" --scrape-all
# Searches, then scrapes top 5 results automatically
```

---

## 🆕 Key Features

### 1. **Multi-Source Search Engine**
Combines multiple sources intelligently:
- **DuckDuckGo** - Instant answers, related topics (fastest)
- **Bing** - Web scraping, comprehensive results
- **Google** - Deep results (when not rate-limited)
- **Wikipedia** - Structured knowledge
- **arXiv** - Academic papers & research

```bash
# Default: DDG + Bing (fastest, most reliable)
python3 search_v3.py "query"

# Add Google: DDG + Bing + Google
python3 search_v3.py "query" --sources ddg,bing,google

# All sources: Everything (slow but comprehensive)
python3 search_v3.py "query" --deep
```

### 2. **Intelligent Result Ranking**
Automatic ranking by:
- **Relevance score** (based on source + content quality)
- **Source authority** (Wikipedia/arXiv boost)
- **Instant answers** (DDG instant answers ranked highest)
- **Snippet quality** (longer, better snippets rank higher)

Results are automatically scored 0-100 and sorted by relevance.

### 3. **Smart Deduplication**
- Removes duplicate URLs
- Removes near-duplicate titles
- Combines results from multiple sources without overlap

### 4. **Intelligent Scraping**
Smart content extraction:
- **Smart mode** - Extracts main article content + metadata + links
- **Text mode** - Just article text
- **All mode** - Everything (text, links, images, metadata, headings)

```bash
# Smart extraction (recommended)
python3 search_v3.py --scrape-url "https://..." --extract smart

# All data
python3 search_v3.py --scrape-url "https://..." --extract all
```

### 5. **Parallel Searching**
Uses threading for 5x faster searches:
- All sources fetched in parallel
- Combined results sorted by relevance
- Total time: ~2-3 seconds for multiple sources

---

## Usage Examples

### Example 1: Bitcoin Market Research

```bash
python3 search_v3.py "bitcoin price prediction 2026" --count 10 --sources ddg,bing
```

Returns top 10 results about Bitcoin from DuckDuckGo + Bing, sorted by relevance.

### Example 2: Deep Academic Research

```bash
python3 search_v3.py "quantum computing applications" --deep
```

Searches all 5 sources:
- Wikipedia for overview
- arXiv for research papers
- Bing for latest news
- Google for comprehensive coverage
- DuckDuckGo for quick facts

### Example 3: News Research + Scraping

```bash
python3 search_v3.py "Fed rate decision" --scrape-all --count 5
```

Finds top 5 results AND automatically scrapes all of them for full content.

### Example 4: Wikipedia + Academic

```bash
python3 search_v3.py "machine learning algorithms" --sources ddg,wikipedia,arxiv
```

Combines instant answers + encyclopedia knowledge + research papers.

### Example 5: Article Content Extraction

```bash
python3 search_v3.py --scrape-url "https://news.example.com/article" --extract smart
```

Extracts:
- Main article text (3000 char limit)
- Headings (h1-h3, top 5)
- Metadata (OG tags)
- Links (top 20)
- Images (top 10)

---

## API Reference

### Search Command

```bash
python3 search_v3.py "query" [OPTIONS]
```

**Options:**
- `--count N` - Number of results (default: 10, max: 50)
- `--sources ddg,bing,google,wikipedia,arxiv` - Which sources to use (default: ddg,bing)
- `--deep` - Use all sources (DDG + Bing + Google + Wikipedia + arXiv)
- `--scrape-all` - Automatically scrape all results (top 5)

### Scrape Command

```bash
python3 search_v3.py --scrape-url "https://..." [OPTIONS]
```

**Options:**
- `--extract smart|text|links|images|metadata|all` - What to extract (default: smart)

### Output Format

Search output:
```json
{
  "query": "search query",
  "sources": ["ddg", "bing"],
  "count": 5,
  "results": [
    {
      "rank": 1,
      "title": "Result Title",
      "url": "https://...",
      "snippet": "Short description...",
      "source": "duckduckgo-instant",
      "relevance": 0.95,
      "score": 95
    }
  ],
  "total_combined": 12,
  "total_deduplicated": 10
}
```

Scrape output:
```json
{
  "url": "https://...",
  "title": "Page Title",
  "text": "Main article content...",
  "text_length": 2500,
  "headings": ["Title", "Section 1", "Section 2"],
  "metadata": {"og:title": "...", "og:description": "..."},
  "links": [{"text": "Link", "href": "https://..."}],
  "link_count": 20,
  "images": [{"src": "https://...", "alt": "description"}],
  "image_count": 5
}
```

---

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| DuckDuckGo search | 0.5-1s | Instant answers API |
| Bing scraping | 1-2s | HTML scraping |
| Google scraping | 1-2s | May be rate-limited |
| Wikipedia search | 0.5-1s | API-based |
| arXiv search | 1-2s | API-based |
| **Multi-source (DDG+Bing)** | **1.5-2s** | Parallel execution |
| **All sources (--deep)** | **2-3s** | All 5 sources parallel |
| URL scraping | 2-5s | Depends on page size |
| Smart scrape | 2-5s | Includes extraction |

---

## Sources Explained

### DuckDuckGo (Fastest ⚡)
- **Type:** API-based instant answers
- **Speed:** <1 second
- **Coverage:** Good for quick facts
- **Reliability:** Very high, no rate limits
- **Best for:** Quick lookups, definitions, facts

### Bing (Comprehensive 📊)
- **Type:** HTML scraping
- **Speed:** 1-2 seconds
- **Coverage:** Comprehensive web results
- **Reliability:** Very high, generous rate limits
- **Best for:** News, general searches, in-depth results

### Google (Deep 🔍)
- **Type:** HTML scraping
- **Speed:** 1-2 seconds
- **Coverage:** Deep, comprehensive
- **Reliability:** Medium (actively blocks scrapers)
- **Best for:** Research when available

### Wikipedia (Knowledge 📚)
- **Type:** API-based
- **Speed:** 0.5-1 second
- **Coverage:** Encyclopedic
- **Reliability:** Very high
- **Best for:** Understanding topics, definitions, context

### arXiv (Research 🎓)
- **Type:** API-based
- **Speed:** 1-2 seconds
- **Coverage:** Research papers, academic work
- **Reliability:** Very high
- **Best for:** Academic research, technical papers

---

## When to Use Which Source

### Quick Fact Lookup
```bash
python3 search_v3.py "What is X?" --sources ddg
```

### News & Recent Events
```bash
python3 search_v3.py "latest news about..." --sources bing,google
```

### Learning a Topic
```bash
python3 search_v3.py "how to learn X" --sources ddg,wikipedia
```

### Academic Research
```bash
python3 search_v3.py "research on X" --deep  # Includes arXiv
```

### Comprehensive Research (Slow)
```bash
python3 search_v3.py "topic" --deep  # All 5 sources
```

### Local Search (Most Relevant)
```bash
python3 search_v3.py "query" --sources ddg,bing  # Default, fastest
```

---

## Smart Scraping Modes

### Smart Mode (Recommended)
```bash
python3 search_v3.py --scrape-url "https://..." --extract smart
```

Extracts:
- Main article text
- Page headings
- Metadata (OG tags)
- Links

**Use this for:** News articles, blog posts, research

### Text Mode
```bash
python3 search_v3.py --scrape-url "https://..." --extract text
```

Just the article text. Minimum processing.

### All Mode
```bash
python3 search_v3.py --scrape-url "https://..." --extract all
```

Everything:
- Text + headings + metadata + links + images

**Use this for:** Complete content preservation

---

## Integration with Polymarket

Perfect for market research:

```bash
# Find market opportunities
python3 search_v3.py "Bitcoin price predictions 2026" --count 10

# Deep research on topic
python3 search_v3.py "Fed interest rate decision" --deep

# Scrape news article for context
python3 search_v3.py --scrape-url "https://news.com/article" --extract smart
```

---

## Technical Details

### Parallel Processing
Uses ThreadPoolExecutor for concurrent fetching:
- All sources queried in parallel
- Results combined and deduplicated
- Sorted by relevance score
- Typical speedup: 3-5x vs sequential

### Deduplication Algorithm
1. Remove identical URLs
2. Remove near-duplicate titles (same first 30 chars)
3. Keep results in relevance order

### Ranking Algorithm
Each result scored 0-100 based on:
- Source authority (+5 to +20 depending on source)
- Snippet quality (+5 for >100 chars)
- Source type (+15 for Wikipedia/instant answers)
- Result position (first results in source ranked higher)

### Error Handling
- Graceful timeouts (15 seconds per source)
- Partial results returned if one source fails
- Network errors don't stop other sources

---

## Limitations

- **Google scraping:** Often rate-limited or returns 0 results
- **JavaScript sites:** Can't render JS (use agent-browser for that)
- **Paywalls:** Won't work with login-required pages
- **WAF/Cloudflare:** Some sites may block
- **Scraping limits:** 3000 chars for text, 20 links, 10 images

---

## Troubleshooting

**No results from Google?**
- Google actively blocks scrapers. Use DDG/Bing instead.
- Try: `--sources ddg,bing` for better reliability

**Slow searches?**
- Use fewer sources: `--sources ddg,bing` instead of `--deep`
- First source: 0.5s, each additional: +0.5-1s

**Scraping returns empty?**
- Page may have JS content. Use agent-browser skill instead.
- Try different extract mode: `--extract smart`

**Rate limited?**
- Rare on DDG/Bing. Google rate-limits frequently.
- Space out requests if hammering same site.

---

## Examples: Real-World Usage

### Polymarket Research

```bash
# Research crypto markets
python3 search_v3.py "Bitcoin 2026 price prediction" --count 10 --sources ddg,bing

# Research Fed decision
python3 search_v3.py "Federal Reserve interest rate decision" --sources bing,google

# Get academic perspective
python3 search_v3.py "cryptocurrency market analysis" --deep
```

### News Analysis

```bash
# Find news + scrape articles
python3 search_v3.py "AI safety concerns" --scrape-all --count 5

# Deep news research
python3 search_v3.py "latest tech news" --deep
```

### Learning

```bash
# Quick definition
python3 search_v3.py "What is blockchain?" --sources ddg

# Deep learning
python3 search_v3.py "how blockchain works" --deep
```

---

## Script Location

- `scripts/search_v3.py` - Main search engine (19.4 KB, feature-rich)

---

**proweb v3: Professional-grade multi-source search for AI agents. 🌐**

Built with BeautifulSoup, curl, and intelligence. Zero API keys. Zero rate limits. Maximum search power.
