#!/usr/bin/env python3
"""
Welt.de News Scraper
Scrapes German news articles from welt.de and stores them in JSON format
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import logging
import hashlib
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse
from dateutil import parser as date_parser
import config


# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WeltScraper:
    """Scraper for welt.de news articles"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)
        self.articles = []
        self.scraped_urls = set()

    def get_page(self, url, retries=0):
        """Fetch a page with error handling and retries"""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(
                url,
                timeout=config.REQUEST_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            if retries < config.MAX_RETRIES:
                logger.info(f"Retrying... (attempt {retries + 1}/{config.MAX_RETRIES})")
                time.sleep(config.REQUEST_DELAY * 2)
                return self.get_page(url, retries + 1)
            return None

    def extract_article_links(self, soup, base_url):
        """Extract article URLs from a page"""
        article_links = set()

        # Look for article links (welt.de typically uses /article/ or /a[0-9]+ patterns)
        for link in soup.find_all('a', href=True):
            href = link['href']

            # Convert relative URLs to absolute
            full_url = urljoin(base_url, href)

            # Filter for article URLs (common patterns on welt.de)
            if any(pattern in full_url for pattern in ['/article/', '/politik/', '/wirtschaft/',
                                                        '/sport/', '/kultur/', '/wissenschaft/']):
                # Check if it looks like an article (contains article ID pattern)
                if full_url.startswith(config.BASE_URL) and full_url not in self.scraped_urls:
                    # Avoid category pages, look for actual articles
                    path = urlparse(full_url).path
                    if len(path.split('/')) >= 3 and not full_url.endswith('/'):
                        article_links.add(full_url)

        return article_links

    def extract_article_content(self, url):
        """Extract article content from a single article page"""
        response = self.get_page(url)
        if not response:
            return None

        soup = BeautifulSoup(response.text, 'lxml')

        article_data = {
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'title': None,
            'text': None,
            'date': None,
            'author': None,
            'category': None,
        }

        try:
            # Extract title
            title_tag = soup.find('h1') or soup.find('title')
            if title_tag:
                article_data['title'] = title_tag.get_text(strip=True)

            # Extract author
            author_tag = soup.find('meta', {'name': 'author'}) or \
                        soup.find('span', class_=lambda x: x and 'author' in x.lower()) or \
                        soup.find('a', {'rel': 'author'})
            if author_tag:
                article_data['author'] = author_tag.get('content') if author_tag.name == 'meta' else author_tag.get_text(strip=True)

            # Extract publication date
            date_tag = soup.find('meta', {'property': 'article:published_time'}) or \
                      soup.find('meta', {'name': 'date'}) or \
                      soup.find('time')
            if date_tag:
                date_str = date_tag.get('content') or date_tag.get('datetime') or date_tag.get_text(strip=True)
                try:
                    article_data['date'] = date_parser.parse(date_str).isoformat()
                except:
                    article_data['date'] = date_str

            # Extract category
            category_tag = soup.find('meta', {'property': 'article:section'}) or \
                          soup.find('meta', {'name': 'category'})
            if category_tag:
                article_data['category'] = category_tag.get('content')
            else:
                # Try to extract from URL
                path_parts = urlparse(url).path.split('/')
                if len(path_parts) > 1:
                    article_data['category'] = path_parts[1]

            # Extract article text
            # Look for article body (common patterns on news sites)
            article_body = soup.find('article') or \
                          soup.find('div', class_=lambda x: x and any(term in str(x).lower() for term in ['article', 'content', 'body', 'text']))

            if article_body:
                # Extract all paragraphs
                paragraphs = article_body.find_all('p')
                text_parts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
                article_data['text'] = '\n\n'.join(text_parts)

            # Validate we got essential data
            if not article_data['title'] or not article_data['text']:
                logger.warning(f"Missing essential data for {url}")
                return None

            logger.info(f"Successfully extracted: {article_data['title'][:50]}...")
            return article_data

        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None

    def generate_article_id(self, url):
        """Generate a unique ID for an article based on URL"""
        return hashlib.md5(url.encode()).hexdigest()[:12]

    def save_article(self, article_data):
        """Save article to individual JSON file"""
        if not article_data:
            return

        # Create filename
        article_id = self.generate_article_id(article_data['url'])
        date_str = article_data.get('date', 'unknown')[:10] if article_data.get('date') else 'unknown'
        filename = config.ARTICLE_FILENAME_FORMAT.format(date=date_str, id=article_id)
        filepath = os.path.join(config.DATA_DIR, filename)

        # Save to file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved article to {filepath}")
            self.articles.append(article_data)
        except Exception as e:
            logger.error(f"Error saving article to {filepath}: {e}")

    def save_all_articles(self):
        """Save all articles to a combined JSON file"""
        try:
            with open(config.COMBINED_OUTPUT, 'w', encoding='utf-8') as f:
                json.dump(self.articles, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(self.articles)} articles to {config.COMBINED_OUTPUT}")
        except Exception as e:
            logger.error(f"Error saving combined articles: {e}")

    def scrape_category(self, category_url, max_articles):
        """Scrape articles from a category page"""
        logger.info(f"Scraping category: {category_url}")

        response = self.get_page(category_url)
        if not response:
            return

        soup = BeautifulSoup(response.text, 'lxml')

        # Extract article links
        article_links = self.extract_article_links(soup, category_url)
        logger.info(f"Found {len(article_links)} article links in {category_url}")

        # Scrape each article
        count = 0
        for article_url in article_links:
            if count >= max_articles:
                break

            if article_url in self.scraped_urls:
                continue

            self.scraped_urls.add(article_url)

            # Extract and save article
            article_data = self.extract_article_content(article_url)
            if article_data:
                self.save_article(article_data)
                count += 1

            # Respectful delay
            time.sleep(config.REQUEST_DELAY)

    def scrape_all(self):
        """Main scraping function"""
        logger.info("Starting Welt.de scraper...")

        # Ensure data directory exists
        os.makedirs(config.DATA_DIR, exist_ok=True)

        total_articles = 0
        for category_url in config.CATEGORY_URLS:
            articles_before = len(self.articles)
            self.scrape_category(category_url, config.MAX_ARTICLES_PER_CATEGORY)
            articles_scraped = len(self.articles) - articles_before
            total_articles += articles_scraped
            logger.info(f"Scraped {articles_scraped} articles from {category_url}")

        # Save combined output
        self.save_all_articles()

        logger.info(f"Scraping complete! Total articles: {total_articles}")
        return total_articles


def main():
    """Main entry point"""
    scraper = WeltScraper()
    scraper.scrape_all()


if __name__ == "__main__":
    main()
