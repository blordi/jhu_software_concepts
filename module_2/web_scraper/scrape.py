import urllib3
from bs4 import BeautifulSoup
import json

def save_data(data, filename='data.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
        
def scrape_data(url):
    page = http.request('GET', url)
    return page.data.decode('utf-8')  # Return raw HTML as string

http = urllib3.PoolManager()

# app_number=range(506400, 986412)
app_number = range(986410,986413)
raw_html_list = []
for number in app_number:
    print(f"Scraping application number {number}")
    url = f"https://www.thegradcafe.com/result/{number}"
    raw_html = scrape_data(url)
    raw_html_list.append({'number': number, 'html': raw_html})

save_data(raw_html_list, 'raw_html_data.json')
