
"""
Scrapes HTML pages from The GradCafe survey results and saves each page's HTML to a JSON file.

- Checks if page has entries that already exist in Database.
- For each new page, fetches the HTML and stores it in a list with its page number.
- Saves the list of page HTMLs to 'raw_applicant_data.json' for later cleaning.
"""
import urllib3
from bs4 import BeautifulSoup   
import json
import psycopg_pool
db_pool = psycopg_pool.ConnectionPool(
    "postgresql://postgres:Uphold-Removable-Radiator@localhost:5432/module_3_db"
)

http = urllib3.PoolManager()

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
    """
    Queries database and gets existing ids from the url field.  returns a set of the existing ids
    Args:
        None
    Returns:
        A set of existing ids, or an empty set
    """
    try:

        with db_pool.connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                        SELECT DISTINCT 
                        CAST(
                            SUBSTRING(url FROM '/result/([0-9]+)') AS INTEGER
                        ) as result_id
                    FROM applicants 
                    WHERE url LIKE '%/result/%'
                        """)
            results = cur.fetchall()
            existing_ids = set(row[0] for row in results)
            return existing_ids
    except Exception as e:
        print(f"Error getting existing IDs: {e}")
        print("Continuing with empty set - may scrape duplicate data")
        return set()

def new_results(page_number, existing_ids):
    """
    Scrapes new results from a page. 
    Args:
        Page number to scrape
        Existing ids in database
    Returns:
        has_new if there are new results on the page
        the number of page result ids
        the number of new ids
        the html content if there are new results
    """
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
    has_new = len(new_ids) > 0

    html_content = soup.prettify() if has_new else None 

    return has_new, len(page_result_ids), len(new_ids), html_content

def main():
    """
    Scrapes thegradcafe.com and only returns new results. Stops if there are 5 pages without new results in a row.
    Args:
        None
    Returns: 
        Saves data to a file update_raw_applicant_data.json
    """
    html_list = []

    existing_ids = get_existing_ids()

    page_number = 1
    empty_page_count = 0
    max_empty_pages = 5  # Stop after 5 consecutive empty pages

    while empty_page_count < max_empty_pages:
        print(f"Checking page {page_number}...")

        has_new, total_ids, new_ids, html_content = new_results(page_number, existing_ids)
        
        if has_new:
            print(f"Page {page_number}: {new_ids} new results out of {total_ids} total")
            html_list.append({"page": page_number, "html": html_content})
            empty_page_count = 0  # Reset counter if new data is found
        else:
            print(f"Page {page_number}: No new results")
            empty_page_count += 1

        page_number +=1
    if html_list:
        save_data(html_list, 'jhu_software_concepts/module_3/web_scraper/update_raw_applicant_data.json')
    else:
        print("No new data to scrape.")

if __name__ == "__main__":
    main()
