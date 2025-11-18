# Welt.de News Scraper

A Python-based web scraper for collecting German news articles from [welt.de](https://www.welt.de/) and storing them in JSON format for AI analysis.

## Features

- Scrapes articles from multiple categories (Politik, Wirtschaft, Sport, Kultur, Wissenschaft)
- Extracts key metadata: title, text, publication date, author, category
- Stores articles as individual JSON files and combined database
- Respectful scraping with rate limiting and proper headers
- UTF-8 encoding support for German characters
- Error handling and retry logic
- Comprehensive logging

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the scraper to collect articles:
```bash
python scraper.py
```

The scraper will:
1. Visit each category page defined in `config.py`
2. Extract article URLs from each category
3. Scrape article content (title, text, date, author, category)
4. Save each article as a JSON file in the `data/` directory
5. Create a combined JSON file with all articles at `data/all_articles.json`

### Configuration

Edit `config.py` to customize the scraper:

- **CATEGORY_URLS**: List of category pages to scrape
- **REQUEST_DELAY**: Delay between requests (default: 2 seconds)
- **MAX_ARTICLES_PER_CATEGORY**: Limit articles per category (default: 50)
- **DATA_DIR**: Directory for storing scraped data

### Output Format

Each article is saved as JSON with the following structure:
```json
{
  "url": "https://www.welt.de/...",
  "scraped_at": "2025-11-18T12:00:00",
  "title": "Article Title",
  "text": "Full article text...",
  "date": "2025-11-18T10:00:00",
  "author": "Author Name",
  "category": "politik"
}
```

## Directory Structure

```
welt_news/
├── scraper.py          # Main scraper script
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── data/              # Scraped articles (JSON files)
│   ├── 2025-11-18_abc123.json
│   ├── 2025-11-18_def456.json
│   └── all_articles.json
└── scraper.log        # Log file
```

## AI Analysis

The scraped articles are ready for AI analysis. You can:

1. **Load all articles:**
```python
import json

with open('data/all_articles.json', 'r', encoding='utf-8') as f:
    articles = json.load(f)
```

2. **Process with AI:**
   - Sentiment analysis
   - Topic modeling
   - Entity extraction
   - Summarization
   - Translation

3. **Example with OpenAI/Anthropic:**
```python
import json
from anthropic import Anthropic

# Load articles
with open('data/all_articles.json', 'r', encoding='utf-8') as f:
    articles = json.load(f)

# Analyze with Claude
client = Anthropic(api_key="your-api-key")
for article in articles[:5]:  # Process first 5 articles
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"Summarize this German article:\n\n{article['text']}"
        }]
    )
    print(f"Title: {article['title']}")
    print(f"Summary: {response.content[0].text}\n")
```

## Ethical Considerations

- **Rate Limiting**: 2-second delay between requests (configurable)
- **User-Agent**: Identifies the scraper properly
- **robots.txt**: Respect site's crawling rules
- **One-time bulk**: Designed for one-time data collection, not continuous scraping
- **Personal Use**: Use responsibly and in accordance with welt.de's terms of service

## Troubleshooting

**No articles found:**
- Check if welt.de HTML structure has changed
- Verify internet connection
- Check `scraper.log` for errors

**Encoding issues:**
- Ensure UTF-8 encoding is used
- All files use `encoding='utf-8'`

**Rate limiting/blocking:**
- Increase `REQUEST_DELAY` in config.py
- Check if IP is blocked (wait and try again later)

## License

For educational and personal use only. Respect welt.de's terms of service.
