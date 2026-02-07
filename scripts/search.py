#!/usr/bin/env python3
"""
proweb v2: Advanced web search + scraping with multiple sources.
No API key required. Full HTML/content extraction.

Usage:
  python3 search.py "query" [--count 5] [--scrape] [--source duckduckgo|google|bing]
  python3 scrape.py "url" [--extract text|links|images|all]
"""

import sys
import json
import subprocess
import urllib.parse
import argparse
from typing import List, Dict, Optional
import re

def run_curl(url: str, timeout: int = 10) -> Optional[str]:
    """Execute curl with proper headers."""
    try:
        result = subprocess.run(
            ['curl', '-s', '-L', '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', url],
            capture_output=True,
            timeout=timeout,
            text=True
        )
        return result.stdout if result.returncode == 0 else None
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

def search_duckduckgo(query: str, count: int = 5) -> List[Dict]:
    """Search DuckDuckGo instant answers."""
    try:
        params = urllib.parse.urlencode({
            'q': query,
            'format': 'json',
            't': 'proweb'
        })
        url = f"https://api.duckduckgo.com/?{params}"
        
        result = subprocess.run(
            ['curl', '-s', url],
            capture_output=True,
            timeout=10,
            text=True
        )
        
        if result.returncode != 0:
            return []
        
        data = json.loads(result.stdout)
        results = []
        
        # Instant answer
        if data.get('AbstractText'):
            results.append({
                'title': data.get('Heading', query),
                'url': data.get('AbstractURL', ''),
                'snippet': data.get('AbstractText', '')[:400],
                'source': 'duckduckgo-instant'
            })
        
        # Related topics
        for topic in data.get('RelatedTopics', []):
            if len(results) >= count:
                break
            
            if isinstance(topic, dict):
                text = topic.get('Text', '')
                url = topic.get('FirstURL', '')
                
                if text and url and len(text) > 5:
                    results.append({
                        'title': text.split(maxsplit=1)[0] if ' ' in text else text[:50],
                        'url': url,
                        'snippet': text[:400],
                        'source': 'duckduckgo-related'
                    })
        
        return results[:count]
    except Exception as e:
        print(f"DuckDuckGo error: {e}", file=sys.stderr)
        return []

def search_google_raw(query: str, count: int = 5) -> List[Dict]:
    """
    Scrape Google search results directly (no API).
    Warning: May hit rate limits. Use sparingly.
    """
    try:
        from bs4 import BeautifulSoup
        
        search_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={search_query}&num={count}"
        
        html = run_curl(url, timeout=15)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Google search result structure
        for g in soup.find_all('div', class_='g')[:count]:
            try:
                title_elem = g.find('h3')
                link_elem = g.find('a', href=True)
                snippet_elem = g.find('span', {'data-attr': True})
                
                if not snippet_elem:
                    snippet_elem = g.find('div', class_='VwiC3b')
                
                if title_elem and link_elem:
                    title = title_elem.get_text()
                    url = link_elem['href']
                    snippet = snippet_elem.get_text() if snippet_elem else title
                    
                    if url.startswith('/url?q='):
                        url = url.split('&')[0].replace('/url?q=', '')
                    
                    if title and url and len(title) > 3:
                        results.append({
                            'title': title[:100],
                            'url': url[:300],
                            'snippet': snippet[:400],
                            'source': 'google-scrape'
                        })
            except:
                continue
        
        return results
    except ImportError:
        print("BeautifulSoup not available for Google scraping", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Google scrape error: {e}", file=sys.stderr)
        return []

def search_bing(query: str, count: int = 5) -> List[Dict]:
    """
    Scrape Bing search results (more lenient than Google).
    """
    try:
        from bs4 import BeautifulSoup
        
        search_query = urllib.parse.quote(query)
        url = f"https://www.bing.com/search?q={search_query}&count={count}"
        
        html = run_curl(url, timeout=15)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        for li in soup.find_all('li', class_='b_algo')[:count]:
            try:
                h2 = li.find('h2')
                a = li.find('a', href=True)
                p = li.find('p')
                
                if h2 and a:
                    title = h2.get_text().strip()
                    url = a['href']
                    snippet = p.get_text().strip() if p else title
                    
                    results.append({
                        'title': title[:100],
                        'url': url[:300],
                        'snippet': snippet[:400],
                        'source': 'bing-scrape'
                    })
            except:
                continue
        
        return results
    except ImportError:
        print("BeautifulSoup not available for Bing scraping", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Bing scrape error: {e}", file=sys.stderr)
        return []

def scrape_page(url: str, extract: str = 'all') -> Dict:
    """
    Scrape a specific page for content.
    extract: 'text' | 'links' | 'images' | 'tables' | 'all'
    """
    try:
        from bs4 import BeautifulSoup
        
        html = run_curl(url, timeout=15)
        if not html:
            return {'error': 'Failed to fetch URL'}
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script/style tags
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()
        
        result = {
            'url': url,
            'title': soup.title.string if soup.title else 'No title',
            'source': 'proweb-scraper'
        }
        
        if extract in ['text', 'all']:
            # Extract main text content
            text = soup.get_text(separator='\n', strip=True)
            result['text'] = text[:2000]  # Limit to 2000 chars
            result['text_length'] = len(text)
        
        if extract in ['links', 'all']:
            # Extract all links
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                text = a.get_text().strip()
                if href and len(href) > 1:
                    links.append({
                        'text': text[:50] if text else '(no text)',
                        'href': href[:200]
                    })
            result['links'] = links[:20]  # Limit to 20 links
            result['link_count'] = len(links)
        
        if extract in ['images', 'all']:
            # Extract all images
            images = []
            for img in soup.find_all('img'):
                src = img.get('src', '')
                alt = img.get('alt', '')
                if src:
                    images.append({
                        'src': src[:200],
                        'alt': alt[:50] if alt else '(no alt)',
                        'title': img.get('title', '')[:50]
                    })
            result['images'] = images[:10]  # Limit to 10 images
            result['image_count'] = len([i for i in soup.find_all('img')])
        
        if extract in ['tables', 'all']:
            # Extract table data
            tables = []
            for table in soup.find_all('table')[:3]:  # Limit to 3 tables
                rows = []
                for tr in table.find_all('tr')[:10]:  # Limit rows
                    cells = []
                    for td in tr.find_all(['td', 'th']):
                        cells.append(td.get_text().strip()[:50])
                    if cells:
                        rows.append(cells)
                if rows:
                    tables.append(rows)
            result['tables'] = tables
            result['table_count'] = len([t for t in soup.find_all('table')])
        
        return result
    except ImportError:
        return {'error': 'BeautifulSoup not available'}
    except Exception as e:
        return {'error': str(e)}

def search(query: str, count: int = 5, source: str = 'duckduckgo', scrape: bool = False) -> Dict:
    """Main search function."""
    results = []
    
    if source == 'duckduckgo':
        results = search_duckduckgo(query, count)
    elif source == 'google':
        results = search_google_raw(query, count)
    elif source == 'bing':
        results = search_bing(query, count)
    elif source == 'all':
        # Try all sources
        ddg = search_duckduckgo(query, count // 2)
        bing_results = search_bing(query, count // 2)
        results = (ddg + bing_results)[:count]
    
    # Optionally scrape first result
    if scrape and results and results[0].get('url'):
        first_url = results[0]['url']
        scraped = scrape_page(first_url, 'text')
        results[0]['scraped_content'] = scraped.get('text', '')[:500]
    
    return {
        'query': query,
        'count': len(results),
        'source': source,
        'results': results
    }

def main():
    parser = argparse.ArgumentParser(description='proweb - Advanced web search + scraping')
    parser.add_argument('query', nargs='?', help='Search query or URL to scrape')
    parser.add_argument('--count', type=int, default=5, help='Number of results')
    parser.add_argument('--source', choices=['duckduckgo', 'google', 'bing', 'all'], default='duckduckgo', help='Search source')
    parser.add_argument('--scrape', action='store_true', help='Scrape first result content')
    parser.add_argument('--scrape-url', help='Scrape specific URL')
    parser.add_argument('--extract', choices=['text', 'links', 'images', 'tables', 'all'], default='all', help='What to extract when scraping URL')
    
    args = parser.parse_args()
    
    if not args.query and not args.scrape_url:
        parser.print_help()
        sys.exit(1)
    
    # Mode 1: Scrape a specific URL
    if args.scrape_url:
        result = scrape_page(args.scrape_url, args.extract)
        print(json.dumps(result, indent=2))
    
    # Mode 2: Search
    else:
        result = search(args.query, args.count, args.source, args.scrape)
        print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
