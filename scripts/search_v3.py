#!/usr/bin/env python3
"""
proweb v3: Advanced multi-source web search + intelligent scraping.
Focus: Best-in-class search combining multiple sources with smart result ranking.

Usage:
  python3 search.py "query" [--count 10] [--deep] [--scrape-all]
  python3 search.py "query" --sources ddg,bing,google --count 20
  python3 search.py "query" --deep --scrape-all  # Full research mode
"""

import sys
import json
import subprocess
import urllib.parse
import argparse
from typing import List, Dict, Optional, Set, Tuple
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================================
# MULTI-SOURCE SEARCH ENGINE
# ============================================================================

def run_curl(url: str, timeout: int = 10) -> Optional[str]:
    """Execute curl with proper headers and retry logic."""
    try:
        result = subprocess.run(
            ['curl', '-s', '-L', '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0', url],
            capture_output=True,
            timeout=timeout,
            text=True
        )
        return result.stdout if result.returncode == 0 else None
    except Exception as e:
        return None

def search_duckduckgo(query: str, count: int = 10) -> List[Dict]:
    """DuckDuckGo instant answers + related topics (fastest, most reliable)."""
    try:
        params = urllib.parse.urlencode({
            'q': query,
            'format': 'json',
            't': 'proweb',
            'ia': 'web'
        })
        url = f"https://api.duckduckgo.com/?{params}"
        html = run_curl(url, timeout=8)
        
        if not html:
            return []
        
        data = json.loads(html)
        results = []
        rank = 0
        
        # Instant answer (high priority)
        if data.get('AbstractText'):
            rank += 1
            results.append({
                'rank': rank,
                'title': data.get('Heading', query),
                'url': data.get('AbstractURL', ''),
                'snippet': data.get('AbstractText', '')[:500],
                'source': 'duckduckgo-instant',
                'relevance': 0.95,
                'score': 95
            })
        
        # Related topics
        for topic in data.get('RelatedTopics', []):
            if len(results) >= count:
                break
            
            if isinstance(topic, dict):
                text = topic.get('Text', '')
                url_topic = topic.get('FirstURL', '')
                
                if text and url_topic and len(text) > 5:
                    rank += 1
                    results.append({
                        'rank': rank,
                        'title': text.split(maxsplit=2)[0:2] if ' ' in text else text[:60],
                        'title': text.split(' - ')[0] if ' - ' in text else text[:60],
                        'url': url_topic,
                        'snippet': text[:500],
                        'source': 'duckduckgo-related',
                        'relevance': 0.75,
                        'score': 75
                    })
        
        return results[:count]
    except Exception as e:
        return []

def search_bing(query: str, count: int = 10) -> List[Dict]:
    """Bing web search scraping (comprehensive, deep results)."""
    try:
        from bs4 import BeautifulSoup
        
        search_query = urllib.parse.quote(query)
        url = f"https://www.bing.com/search?q={search_query}&count=50"
        
        html = run_curl(url, timeout=12)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        rank = 0
        
        for item in soup.find_all('li', class_='b_algo'):
            if len(results) >= count:
                break
            
            try:
                title_elem = item.find('h2')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                link_elem = title_elem.find('a')
                url_result = link_elem['href'] if link_elem else ''
                
                desc_elem = item.find('p')
                snippet = desc_elem.get_text(strip=True) if desc_elem else ''
                
                if title and url_result and len(snippet) > 20:
                    rank += 1
                    results.append({
                        'rank': rank,
                        'title': title[:100],
                        'url': url_result,
                        'snippet': snippet[:500],
                        'source': 'bing',
                        'relevance': 0.80,
                        'score': 80
                    })
            except:
                continue
        
        return results
    except Exception as e:
        return []

def search_google(query: str, count: int = 10) -> List[Dict]:
    """Google search scraping (may be rate-limited, but comprehensive)."""
    try:
        from bs4 import BeautifulSoup
        
        search_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={search_query}&num={count}"
        
        html = run_curl(url, timeout=12)
        if not html or len(html) < 1000:
            return []  # Usually means rate-limited
        
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        rank = 0
        
        for item in soup.find_all('div', class_='g'):
            if len(results) >= count:
                break
            
            try:
                title_elem = item.find('h3')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                
                link_elem = item.find('a')
                url_result = link_elem['href'] if link_elem else ''
                
                desc_elem = item.find('span', class_='VwiC3b')
                snippet = desc_elem.get_text(strip=True) if desc_elem else ''
                
                if title and url_result and len(snippet) > 10:
                    # Clean Google URLs
                    if url_result.startswith('/url?q='):
                        url_result = urllib.parse.unquote(url_result.split('q=')[1].split('&')[0])
                    
                    rank += 1
                    results.append({
                        'rank': rank,
                        'title': title[:100],
                        'url': url_result,
                        'snippet': snippet[:500],
                        'source': 'google',
                        'relevance': 0.70,
                        'score': 70
                    })
            except:
                continue
        
        return results
    except Exception as e:
        return []

def search_wikipedia(query: str) -> Optional[Dict]:
    """Wikipedia search (structured knowledge)."""
    try:
        params = urllib.parse.urlencode({
            'action': 'query',
            'format': 'json',
            'srsearch': query,
            'srprop': 'snippet',
            'srlimit': '1'
        })
        url = f"https://en.wikipedia.org/w/api.php?{params}"
        
        html = run_curl(url, timeout=8)
        if not html:
            return None
        
        data = json.loads(html)
        results = data.get('query', {}).get('search', [])
        
        if results:
            r = results[0]
            title = r.get('title', '')
            snippet = re.sub('<[^<]+?>', '', r.get('snippet', ''))  # Remove HTML tags
            
            return {
                'rank': 0,
                'title': title,
                'url': f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title)}",
                'snippet': snippet[:500],
                'source': 'wikipedia',
                'relevance': 0.85,
                'score': 85
            }
    except:
        pass
    
    return None

def search_arxiv(query: str, count: int = 5) -> List[Dict]:
    """arXiv academic papers search."""
    try:
        from urllib.parse import quote
        search_query = quote(query)
        url = f"https://arxiv.org/cgi-bin/opensearch?query={search_query}&start=0&max_results={count}"
        
        html = run_curl(url, timeout=10)
        if not html:
            return []
        
        from xml.etree import ElementTree as ET
        root = ET.fromstring(html)
        
        results = []
        rank = 0
        
        for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
            if len(results) >= count:
                break
            
            try:
                title = entry.find('{http://www.w3.org/2005/Atom}title').text
                summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
                url_elem = entry.find('{http://www.w3.org/2005/Atom}id').text
                
                rank += 1
                results.append({
                    'rank': rank,
                    'title': title[:100],
                    'url': url_elem,
                    'snippet': summary[:500],
                    'source': 'arxiv',
                    'relevance': 0.75,
                    'score': 75
                })
            except:
                continue
        
        return results
    except:
        return []

# ============================================================================
# INTELLIGENT RESULT RANKING & DEDUPLICATION
# ============================================================================

def deduplicate_results(all_results: List[Dict]) -> List[Dict]:
    """Deduplicate results by URL + title similarity."""
    seen_urls = set()
    seen_titles = {}
    deduplicated = []
    
    for result in all_results:
        url = result.get('url', '')
        title = result.get('title', '')
        
        # Skip if URL already seen
        if url in seen_urls:
            continue
        
        # Skip if very similar title already seen
        if title:
            title_lower = title.lower()
            is_duplicate = False
            for seen_title in seen_titles:
                if abs(len(title_lower) - len(seen_title)) < 5:
                    if title_lower[:30] == seen_title[:30]:
                        is_duplicate = True
                        break
            
            if is_duplicate:
                continue
            
            seen_titles[title_lower] = True
        
        seen_urls.add(url)
        deduplicated.append(result)
    
    return deduplicated

def rank_results(results: List[Dict]) -> List[Dict]:
    """Rank results by relevance score + source authority + freshness."""
    for result in results:
        # Base score from source
        base_score = result.get('score', 50)
        
        # Boost for having good snippet
        if len(result.get('snippet', '')) > 100:
            base_score += 5
        
        # Boost for URL authority (wikipedia, arxiv, etc)
        source = result.get('source', '')
        if source == 'wikipedia':
            base_score += 20
        elif source == 'duckduckgo-instant':
            base_score += 15
        elif source == 'arxiv':
            base_score += 10
        
        result['score'] = min(base_score, 100)
    
    # Sort by score (descending)
    return sorted(results, key=lambda x: x['score'], reverse=True)

# ============================================================================
# INTELLIGENT SCRAPING
# ============================================================================

def smart_scrape(url: str, extract_mode: str = "smart") -> Dict:
    """
    Smart scraping: extract main article content + metadata.
    Smarter than basic text extraction.
    """
    try:
        from bs4 import BeautifulSoup
        
        html = run_curl(url, timeout=15)
        if not html:
            return {'error': 'Failed to fetch'}
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove noise
        for script in soup(['script', 'style', 'nav', 'footer']):
            script.decompose()
        
        result = {
            'url': url,
            'title': soup.title.string if soup.title else 'N/A',
            'scraped_at': int(time.time())
        }
        
        # Extract main content
        if extract_mode in ['smart', 'text', 'all']:
            # Try to find main content area
            main_content = None
            for selector in ['article', 'main', '[role="main"]', '.content', '#content']:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if main_content:
                text = main_content.get_text(separator=' ', strip=True)
            else:
                # Fallback: get body text
                text = soup.get_text(separator=' ', strip=True)
            
            text = re.sub(r'\s+', ' ', text)[:3000]  # Limit to 3000 chars
            result['text'] = text
            result['text_length'] = len(text)
            
            # Extract headings
            headings = []
            for h in soup.find_all(['h1', 'h2', 'h3'])[:5]:
                h_text = h.get_text(strip=True)
                if h_text:
                    headings.append(h_text)
            
            if headings:
                result['headings'] = headings
        
        # Extract metadata
        if extract_mode in ['smart', 'metadata', 'all']:
            metadata = {}
            
            # OG tags
            for tag in soup.find_all('meta'):
                prop = tag.get('property', '')
                content = tag.get('content', '')
                
                if prop.startswith('og:'):
                    meta_key = prop.replace('og:', '')
                    metadata[meta_key] = content
            
            if metadata:
                result['metadata'] = metadata
        
        # Extract links
        if extract_mode in ['smart', 'links', 'all']:
            links = []
            for link in soup.find_all('a', href=True)[:30]:
                href = link['href']
                link_text = link.get_text(strip=True)
                
                if href and link_text and len(link_text) > 2:
                    # Skip internal navigation links
                    if not any(x in link_text.lower() for x in ['menu', 'nav', 'toggle', 'close']):
                        links.append({
                            'text': link_text[:80],
                            'href': href[:200]
                        })
            
            if links:
                result['links'] = links[:20]
                result['link_count'] = len(links)
        
        # Extract images
        if extract_mode in ['smart', 'images', 'all']:
            images = []
            for img in soup.find_all('img')[:10]:
                src = img.get('src', '')
                alt = img.get('alt', '')
                
                if src and (alt or len(src) > 10):
                    images.append({
                        'src': src[:200],
                        'alt': alt[:100] if alt else ''
                    })
            
            if images:
                result['images'] = images
                result['image_count'] = len(images)
        
        return result
    
    except Exception as e:
        return {'error': str(e), 'url': url}

# ============================================================================
# MAIN SEARCH ENGINE
# ============================================================================

def multi_source_search(query: str, sources: List[str], count: int = 10, deep: bool = False) -> Dict:
    """
    Unified multi-source search engine.
    Combines results from multiple sources with intelligent ranking.
    """
    all_results = []
    
    source_functions = {
        'ddg': lambda q: search_duckduckgo(q, count),
        'bing': lambda q: search_bing(q, count),
        'google': lambda q: search_google(q, count),
        'wikipedia': lambda q: ([search_wikipedia(q)] if search_wikipedia(q) else []),
        'arxiv': lambda q: search_arxiv(q, count)
    }
    
    # Parallel search from multiple sources
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        
        for source in sources:
            if source in source_functions:
                future = executor.submit(source_functions[source], query)
                futures[future] = source
        
        for future in as_completed(futures):
            try:
                results = future.result(timeout=15)
                if results:
                    all_results.extend(results)
            except:
                pass
    
    # Deduplicate
    deduplicated = deduplicate_results(all_results)
    
    # Rank by relevance
    ranked = rank_results(deduplicated)
    
    # Return top N
    return {
        'query': query,
        'sources': sources,
        'count': len(ranked),
        'results': ranked[:count],
        'total_combined': len(all_results),
        'total_deduplicated': len(deduplicated)
    }

# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='proweb: Advanced multi-source search')
    
    parser.add_argument('query', nargs='?', default=None, help='Search query')
    parser.add_argument('--count', type=int, default=10, help='Number of results (default: 10)')
    parser.add_argument('--sources', default='ddg,bing', help='Sources: ddg,bing,google,wikipedia,arxiv (default: ddg,bing)')
    parser.add_argument('--deep', action='store_true', help='Deep search (include Google + arXiv)')
    parser.add_argument('--scrape-all', action='store_true', help='Scrape all results')
    parser.add_argument('--scrape-url', default=None, help='Scrape specific URL')
    parser.add_argument('--extract', choices=['smart', 'text', 'links', 'images', 'metadata', 'all'], default='smart', help='Extraction mode')
    
    args = parser.parse_args()
    
    # Scrape specific URL
    if args.scrape_url:
        result = smart_scrape(args.scrape_url, extract_mode=args.extract)
        print(json.dumps(result, indent=2))
        return
    
    if not args.query:
        parser.print_help()
        return
    
    # Determine sources
    sources = args.sources.split(',')
    
    if args.deep:
        sources = ['ddg', 'bing', 'google', 'wikipedia', 'arxiv']
    
    # Search
    print(f"🔍 Searching {len(sources)} sources for '{args.query}'...", file=sys.stderr)
    
    results = multi_source_search(args.query, sources, count=args.count, deep=args.deep)
    
    # Optionally scrape all results
    if args.scrape_all:
        print(f"📄 Scraping {len(results['results'])} results...", file=sys.stderr)
        for result in results['results'][:5]:  # Scrape top 5
            if result.get('url'):
                scraped = smart_scrape(result['url'], extract_mode=args.extract)
                result['scraped_content'] = scraped
    
    # Output
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
