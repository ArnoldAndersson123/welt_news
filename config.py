"""
Configuration settings for Welt.de news scraper
"""

# Base URL
BASE_URL = "https://www.welt.de"

# Category pages to scrape (add more as needed)
CATEGORY_URLS = [
    "https://www.welt.de/politik/",
    "https://www.welt.de/wirtschaft/",
    "https://www.welt.de/sport/",
    "https://www.welt.de/kultur/",
    "https://www.welt.de/wissenschaft/",
    "https://www.welt.de/",  # Homepage
]

# Scraping settings
REQUEST_DELAY = 2  # Seconds between requests (be respectful)
REQUEST_TIMEOUT = 10  # Seconds
MAX_RETRIES = 3
MAX_ARTICLES_PER_CATEGORY = 50  # Limit for one-time bulk scraping

# Headers
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

# Storage settings
DATA_DIR = "data"
ARTICLE_FILENAME_FORMAT = "{date}_{id}.json"  # Format: 2024-01-15_abc123.json
COMBINED_OUTPUT = "data/all_articles.json"  # Optional: all articles in one file

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "scraper.log"
