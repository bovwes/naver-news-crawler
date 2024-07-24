import os
import csv
import calendar
from functions import *
from concurrent.futures import ThreadPoolExecutor, as_completed

#
#
# Variables.
#

# Search for news articles after given date.
# Possible formats: YYYY, YYYY-MM, YYYY-MM-DD.
AFTER = "" 

# Search for news articles before given date.
# Possible formats: YYYY, YYYY-MM, YYYY-MM-DD.
BEFORE = "" 

# Search for news articles within given category.
# Possible categories: 정치, 경제, 사회, 생활문화, 세계, IT/과학, 오피니언, TV.
CATEGORY = ""

# Provide User-Agent that will appear in every request. (optional)
# Example: "news-crawler/1.0".
USER_AGENT = ""

# Provide the number of threads for multithreading to speed up the parsing
NUM_THREADS = 10

news_urls = []
article_urls = []

#
#
# List all the pages that include news articles within the timeframe for a given category.
#

print(f'Searching for {CATEGORY} articles from {AFTER} to {BEFORE}...')

timeframe = get_timeframe(BEFORE, AFTER) # Transform before and after into timeframe dictionary.
category_idx = get_category_idx(CATEGORY) # Transform category into its respective number used by Naver.

base_url = f'http://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1={category_idx}&date='

for year in range(timeframe['start_year'], timeframe['end_year'] + 1):
    if timeframe['start_year'] == timeframe['end_year']:
        target_start_month = timeframe['start_month']
        target_end_month = timeframe['end_month']
    else:
        if year == timeframe['start_year']:
            target_start_month = timeframe['start_month']
            target_end_month = 12
        elif year == timeframe['end_year']:
            target_start_month = 1
            target_end_month = timeframe['end_month']
        else:
            target_start_month = 1
            target_end_month = 12

    for month in range(target_start_month, target_end_month + 1):
        if timeframe['start_month'] == timeframe['end_month']:
            target_start_day = timeframe['start_day']
            target_end_day = timeframe['end_day']
        else:
            if year == timeframe['start_year'] and month == timeframe['start_month']:
                target_start_day = timeframe['start_day']
                target_end_day = calendar.monthrange(year, month)[1]
            elif year == timeframe['end_year'] and month == timeframe['end_month']:
                target_start_day = 1
                target_end_day = timeframe['end_day']
            else:
                target_start_day = 1
                target_end_day = calendar.monthrange(year, month)[1]

        for day in range(target_start_day, target_end_day + 1):
            if len(str(month)) == 1:
                month = "0" + str(month)
            if len(str(day)) == 1:
                day = "0" + str(day)

            url = base_url + str(year) + str(month) + str(day)
       
            max_page = get_max_page_idx(url, USER_AGENT) # Ensure every news page is parsed, from page 1 until max page.
            for page in range(1, max_page + 1):
                news_urls.append(url + "&page=" + str(page))

#
#
# Extract all articles from the list.
#

for url in news_urls:
    soup = fetch_url(url, USER_AGENT)
    articles = soup.select('.newsflash_body .type06_headline li dl')
    articles.extend(soup.select('.newsflash_body .type06 li dl'))

    for i in articles:
        print(f'Found {len(article_urls)} articles...', end='\r')
        article_urls.append(i.a.get('href'))

print(f'Found {len(article_urls)} articles.')

#
#
# Open each article and write relevant fields to csv file.
#

output_dir = f'out'
os.makedirs(output_dir, exist_ok=True)

output_file_path = f'{output_dir}/{CATEGORY} {AFTER} - {BEFORE}.csv'

with open(output_file_path, 'w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'Category', 'Outlet', 'Headline', 'Content', 'URL'])

    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        future_to_url = {executor.submit(parse_article, url, USER_AGENT, CATEGORY): url for url in article_urls}
        for i, future in enumerate(as_completed(future_to_url), 1):
            url = future_to_url[future]
            try:
                result = future.result()
                if result:
                    writer.writerow(result)
                print(f'Parsed article {i} of {len(article_urls)}', end='\r')
            except Exception as e:
                print(f"Skipped article {i}. Error: {e}. URL: {url}") # Some articles that have a different HTML structure may be skipped. Happens mostly to Sports articles.

print("Finished parsing articles.")
print(f"Saved to {output_file_path}.")
