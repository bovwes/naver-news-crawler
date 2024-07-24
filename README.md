# naver-news-crawler

This script is designed to crawl news articles from Naver News within a specified date range and category.

## Dependencies

The `BeautifulSoup` and `requests` libraries are required. You can install these libraries using pip:

```
pip install beautifulsoup4 requests
```

## Setup

Modify the following variables in the `crawler.py` to define the date range and category of news articles you want to retrieve:

- `AFTER` and `BEFORE` should be in the format `YYYY-MM-DD`, `YYYY-MM`, or `YYYY`.
- `CATEGORY` can be any of following available categories: `정치` (Politics), `경제` (Economy), `사회` (Society), `생활문화` (Culture), `세계` (World), `IT/과학` (Science), `연예` (Entertainment), `오피니언` (Opinion), `TV` (TV)
- `USER_AGENT` will be included in the header of ever request. No headers are included if left empty.

Then, run the script using the following command:

```
python crawler.py
```

## Output

The script will output a single CSV file with every crawled news article. Depending on the size of the date range, it may take a while to parse all articles. Each parsed article contains the following attributes:

- Timestamp
- Category
- Outlet
- Headline
- Content
- URL
