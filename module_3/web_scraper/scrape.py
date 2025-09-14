
"""
Scrapes HTML pages from The GradCafe survey results and saves each page's HTML to a JSON file.

- Iterates over all survey pages (0 to 9057).
- For each page, fetches the HTML and stores it in a list with its page number.
- Saves the list of page HTMLs to 'raw_applicant_data.json' for later cleaning.
"""
import urllib3
from bs4 import BeautifulSoup   
import json
import psycopg_pool

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

def get_existing_ids():
    pool = psycopg_pool.ConnectionPool(
        "postgresql://postgres:Uphold-Removable-Radiator@localhost:5432/module_3_db"
    )
    with pool.connection() as conn:
        cur = conn.cursor()
        cur.execute("""
                    SELECT id FROM applicants;SELECT DISTINCT 
                    CAST(
                        SUBSTRING(url FROM '/result/([0-9]+)') AS INTEGER
                    ) as result_id
                FROM applicants 
                WHERE url LIKE '%/result/%'
                    """)
        results = cur.fetchall()
        return set(row[0] for row in results)

def new_results(page_number, existing_ids):
    http = urllib3.PoolManager()
    url = f"https://www.thegradcafe.com/survey/?page={page_number}"
    page = http.request('GET', url)
    soup = BeautifulSoup(page.data, 'html.parser')

    links = soup.find_all('a', href=True)
    page_result_ids = set()

    for link in links:
        href = link['href']
        if '/result/' in href:
            try:
                result_id = int(href.split('/result/')[-1])
                page_result_ids.add(result_id)
            except (IndexError, ValueError):
                continue

    new_ids = page_result_ids - existing_ids
    return len(new_ids) > 0, len(page_result_ids), len(new_ids)

def main():
    html_list = []

    existing_ids = get_existing_ids()

    page_number = 1
    empty_page_count = 0
    max_empty_pages = 5  # Stop after 5 consecutive empty pages

    while empty_page_count < max_empty_pages:

        has_new, total_ids, new_ids = new_results(page_number, existing_ids)
        if has_new:
            url = f"https://www.thegradcafe.com/survey/?page={page_number}"
            html_content = scrape_data(url)
            html_list.append({"page": page_number, "html": html_content})
            consecutive_empty_pages = 0
        else:
            empty_page_count += 1
    if html_list:
        save_data(html_list, 'jhu_software_concepts/module_3/web_scraper/update_raw_applicant_data.json')
    else:
        print("No new data to scrape.")

if __name__ == "__main__":
    main()
