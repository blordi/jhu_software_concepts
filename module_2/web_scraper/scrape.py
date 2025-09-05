import urllib3
from bs4 import BeautifulSoup   
import json

def save_data(data, filename='data.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def scrape_data(url):
    page = http.request('GET', url)
    soup = BeautifulSoup(page.data, 'html.parser')
    return soup.prettify()

http = urllib3.PoolManager()

html_list = []
page_number = range(0, 3)
for number in page_number:
    url = f"https://www.thegradcafe.com/survey/?page={number}"
    html = scrape_data(url)
    html_list.append({'page': number, 'html': html})


save_data(html_list, 'raw_applicant_data.json')
