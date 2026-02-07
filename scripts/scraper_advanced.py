#!/usr/bin/env python3
"""
proweb-advanced: Heavy-duty web scraping with Selenium for JavaScript-heavy sites.
Requires: selenium, playwright (optional)

Usage:
  python3 scraper_advanced.py "url" [--headless] [--wait 5] [--extract all]
  python3 scraper_advanced.py "url" --method playwright  # Use Playwright instead
"""

import sys
import json
import argparse
import time
from typing import Dict, Optional
import subprocess

def scrape_selenium(url: str, wait_secs: int = 5, headless: bool = True) -> Dict:
    """
    Scrape with Selenium (can handle JavaScript).
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from bs4 import BeautifulSoup
        
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        driver = webdriver.Chrome(options=options)
        
        try:
            driver.get(url)
            
            # Wait for page to load
            time.sleep(wait_secs)
            
            # Get rendered HTML
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script/style
            for tag in soup(['script', 'style', 'noscript']):
                tag.decompose()
            
            result = {
                'url': url,
                'method': 'selenium',
                'title': soup.title.string if soup.title else 'No title',
                'rendered': True
            }
            
            # Extract text
            text = soup.get_text(separator='\n', strip=True)
            result['text'] = text[:3000]
            result['text_length'] = len(text)
            
            # Extract headings
            headings = [h.get_text() for h in soup.find_all(['h1', 'h2', 'h3'])[:10]]
            result['headings'] = headings
            
            # Extract forms
            forms = []
            for form in soup.find_all('form')[:3]:
                inputs = []
                for inp in form.find_all(['input', 'textarea', 'select']):
                    inputs.append({
                        'name': inp.get('name', ''),
                        'type': inp.get('type', 'text'),
                        'value': inp.get('value', '')
                    })
                if inputs:
                    forms.append({'inputs': inputs})
            result['forms'] = forms
            
            # Extract metadata
            meta_tags = {}
            for meta in soup.find_all('meta'):
                name = meta.get('name', meta.get('property', ''))
                content = meta.get('content', '')
                if name:
                    meta_tags[name] = content
            result['metadata'] = meta_tags
            
            return result
        
        finally:
            driver.quit()
    
    except ImportError:
        return {'error': 'Selenium not installed'}
    except Exception as e:
        return {'error': f'Selenium scrape failed: {str(e)}'}

def scrape_playwright(url: str, wait_secs: int = 5) -> Dict:
    """
    Scrape with Playwright (faster, more reliable than Selenium).
    """
    try:
        from playwright.sync_api import sync_playwright
        from bs4 import BeautifulSoup
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            page.goto(url, wait_until='load')
            time.sleep(wait_secs)
            
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script/style
            for tag in soup(['script', 'style', 'noscript']):
                tag.decompose()
            
            result = {
                'url': url,
                'method': 'playwright',
                'title': soup.title.string if soup.title else 'No title',
                'rendered': True
            }
            
            # Extract text
            text = soup.get_text(separator='\n', strip=True)
            result['text'] = text[:3000]
            result['text_length'] = len(text)
            
            # Extract headings
            headings = [h.get_text() for h in soup.find_all(['h1', 'h2', 'h3'])[:10]]
            result['headings'] = headings
            
            # Extract interactive elements
            buttons = [b.get_text() for b in soup.find_all('button')[:5]]
            result['buttons'] = buttons
            
            # Screenshot available
            result['screenshot_available'] = True
            
            browser.close()
            return result
    
    except ImportError:
        return {'error': 'Playwright not installed'}
    except Exception as e:
        return {'error': f'Playwright scrape failed: {str(e)}'}

def main():
    parser = argparse.ArgumentParser(description='proweb Advanced Scraper (JavaScript support)')
    parser.add_argument('url', help='URL to scrape')
    parser.add_argument('--method', choices=['selenium', 'playwright'], default='selenium', help='Scraping method')
    parser.add_argument('--headless', action='store_true', default=True, help='Run headless')
    parser.add_argument('--wait', type=int, default=5, help='Seconds to wait for JS to render')
    parser.add_argument('--extract', choices=['text', 'all'], default='all', help='What to extract')
    
    args = parser.parse_args()
    
    if args.method == 'playwright':
        result = scrape_playwright(args.url, args.wait)
    else:
        result = scrape_selenium(args.url, args.wait, args.headless)
    
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
