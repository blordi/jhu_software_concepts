import urllib3
from bs4 import BeautifulSoup   
"""
Scrapes HTML pages from The GradCafe survey results and saves each page's HTML to a JSON file.

- Iterates over all survey pages (0 to 9057).
- For each page, fetches the HTML and stores it in a list with its page number.
- Saves the list of page HTMLs to 'raw_applicant_data.json' for later cleaning.
"""
import json

def save_data(data, filename='raw_applicant_data.json'):
     """
    Saves the provided data to a JSON file.
    Args:
        data (list): List of dictionaries containing scraped HTML and page numbers.
        filename (str): Path to the output JSON file.
    """
     with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
   


def scrape_data(url):
    """
    Fetches and returns the prettified HTML content of the given URL.
    Args:
        url (str): The URL to scrape.
    Returns:
        str: Prettified HTML content of the page.
    """
    page = http.request('GET', url)
    soup = BeautifulSoup(page.data, 'html.parser')
    return soup.prettify()

http = urllib3.PoolManager()

html_list = []
page_number = range(0, 9058)
for number in page_number:
    url = f"https://www.thegradcafe.com/survey/?page={number}"
    html = scrape_data(url)
    html_list.append({'page': number, 'html': html})


save_data(html_list, 'jhu_software_concepts/module_2/web_scraper/raw_applicant_data.json')
