"""
Module for scraping graduate school applicant data from The GradCafe survey results.

This module provides intelligent web scraping functionality that avoids duplicate
data collection by checking existing database entries before scraping new pages.
It fetches HTML content from The GradCafe survey results pages and saves the raw
HTML data for subsequent cleaning and processing.

The scraping process is designed to be efficient and respectful:
- Checks existing database entries to avoid duplicate scraping
- Stops automatically when no new data is found across multiple pages
- Uses connection pooling for efficient HTTP requests
- Saves raw HTML data in structured JSON format for processing

.. note::
   This module requires network connectivity and access to The GradCafe website.
   It also requires a PostgreSQL database connection to check for existing data.

.. warning::
   Web scraping should be performed responsibly. Ensure compliance with
   The GradCafe's robots.txt and terms of service.

Dependencies:
    - urllib3: For HTTP request handling with connection pooling
    - BeautifulSoup4: For HTML parsing and link extraction
    - psycopg_pool: For PostgreSQL database connectivity
    - json: For data serialization

Database Requirements:
    - PostgreSQL database with 'applicants' table
    - Table must have 'url' field containing result URLs
    - URLs should follow pattern '/result/{id}' for ID extraction

Output:
    - update_raw_applicant_data.json: Raw HTML content with page metadata

Example Usage:
    >>> import scrape
    >>> scrape.main()
    Checking page 1...
    Page 1: 25 new results out of 25 total
    Checking page 2...
    Page 2: 20 new results out of 25 total
    ...

.. seealso::
   :mod:`clean` for processing the scraped HTML data
   :mod:`load_data` for database operations
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
    Save scraped HTML data to a JSON file with proper formatting.
    
    This function serializes the list of scraped page data to JSON format,
    preserving the page numbers and HTML content for subsequent processing.
    The output is formatted with indentation for human readability.
    
    :param data: List of dictionaries containing scraped HTML and page metadata
    :type data: list[dict]
    :param filename: Path to the output JSON file
    :type filename: str, optional
    :raises IOError: When file cannot be written
    :raises TypeError: When data cannot be JSON serialized
    
    .. note::
       Each dictionary in the data list should contain 'page' and 'html' keys
       representing the page number and raw HTML content respectively.
       
    Data Structure:
        [
            {"page": 1, "html": "<html>...</html>"},
            {"page": 2, "html": "<html>...</html>"},
            ...
        ]
        
    Example:
        >>> scraped_pages = [{"page": 1, "html": "<html>content</html>"}]
        >>> save_data(scraped_pages, "raw_data.json")
    """ 
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
   

def scrape_data(url):
    """
    Fetch and return the prettified HTML content of the given URL.
    
    This function performs an HTTP GET request to the specified URL and
    returns the HTML content formatted with proper indentation using
    BeautifulSoup's prettify functionality.
    
    :param url: The URL to scrape
    :type url: str
    :return: Prettified HTML content of the page
    :rtype: str
    :raises urllib3.exceptions.HTTPError: When HTTP request fails
    :raises urllib3.exceptions.TimeoutError: When request times out
    :raises Exception: When HTML parsing fails
    
    .. note::
       This function uses the global urllib3.PoolManager for connection reuse
       and improved performance across multiple requests.
       
    .. warning::
       No rate limiting is implemented. Consider adding delays between
       requests for large-scale scraping operations.
       
    Example:
        >>> html_content = scrape_data("https://www.thegradcafe.com/survey/?page=1")
        >>> print(html_content[:100])
        <!DOCTYPE html>
        <html>
        <head>
        ...
    """
    page = http.request('GET', url)
    soup = BeautifulSoup(page.data, 'html.parser')
    return soup.prettify()

def get_existing_ids():
    """
    Query database and retrieve existing result IDs from the URL field.
    
    This function connects to the PostgreSQL database and extracts result IDs
    from existing applicant URLs. It uses regex pattern matching to extract
    numeric IDs from URLs that follow The GradCafe's '/result/{id}' format.
    The function returns a set of existing IDs for efficient duplicate checking.
    
    :return: Set of existing result IDs, or empty set if query fails
    :rtype: set[int]
    :raises psycopg.Error: When database connection or query fails
    
    .. note::
       The function extracts IDs using SQL SUBSTRING with regex pattern
       '/result/([0-9]+)' and casts results to INTEGER for proper comparison.
       
    .. warning::
       If database connection fails, the function returns an empty set and
       continues execution, which may result in duplicate data scraping.
       
    SQL Query Logic:
        - Filters for URLs containing '/result/' pattern
        - Extracts numeric ID using SUBSTRING with regex
        - Casts extracted strings to INTEGER
        - Returns DISTINCT values to avoid duplicates
        
    Error Handling:
        - Catches all database exceptions
        - Prints error message for debugging
        - Returns empty set to allow scraping to continue
        - Warns about potential duplicate data collection
        
    Example:
        >>> existing_ids = get_existing_ids()
        >>> print(len(existing_ids))
        1250
        >>> print(list(existing_ids)[:5])
        [12345, 12346, 12347, 12348, 12349]
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
    Check a specific page for new results not already in the database.
    
    This function scrapes a single page from The GradCafe survey results,
    extracts all result IDs from the page, compares them against existing
    database entries, and determines if the page contains new data worth
    processing. It returns comprehensive information about the page's content.
    
    :param page_number: Page number to scrape from The GradCafe
    :type page_number: int
    :param existing_ids: Set of result IDs already in database
    :type existing_ids: set[int]
    :return: Tuple containing (has_new_data, total_ids, new_ids_count, html_content)
    :rtype: tuple[bool, int, int, str|None]
    :raises urllib3.exceptions.HTTPError: When HTTP request fails
    :raises Exception: When HTML parsing fails
    
    .. note::
       The function only returns HTML content if new results are found,
       optimizing storage and processing for relevant data only.
       
    Return Values:
        - has_new_data (bool): True if page contains new results
        - total_ids (int): Total number of result IDs found on page
        - new_ids_count (int): Number of new IDs not in database
        - html_content (str|None): Prettified HTML if new data found, None otherwise
        
    Processing Logic:
        1. Constructs URL for specified page number
        2. Fetches page content via HTTP GET request
        3. Parses HTML to find all links containing '/result/'
        4. Extracts numeric IDs from result URLs
        5. Compares page IDs against existing database IDs
        6. Returns HTML content only if new data is present
        
    URL Pattern Matching:
        - Searches for <a> tags with href attributes
        - Filters for hrefs containing '/result/' substring
        - Extracts trailing numeric ID from URL path
        - Handles malformed URLs gracefully with exception catching
        
    Example:
        >>> existing = {12345, 12346, 12347}
        >>> has_new, total, new_count, html = new_results(1, existing)
        >>> print(f"Page 1: {new_count} new out of {total} total")
        Page 1: 22 new out of 25 total
        >>> print(has_new)
        True
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
    Execute the complete scraping pipeline with intelligent stopping criteria.
    
    This is the main orchestration function that manages the entire scraping
    process. It implements an intelligent stopping mechanism that continues
    scraping until multiple consecutive pages contain no new data, indicating
    that all available new results have been collected.
    
    :raises urllib3.exceptions.HTTPError: When HTTP requests fail
    :raises psycopg.Error: When database connection fails
    :raises IOError: When output file cannot be written
    
    .. note::
       The function stops after 5 consecutive pages with no new results,
       balancing thoroughness with efficiency.
       
    Processing Algorithm:
        1. Query database for existing result IDs
        2. Initialize page counter and empty page tracker
        3. For each page:
           a. Check for new results against existing IDs
           b. If new results found: save HTML and reset empty counter
           c. If no new results: increment empty counter
           d. Continue until max empty pages reached
        4. Save all collected HTML data to output file
        
    Stopping Criteria:
        - Stops after 5 consecutive pages with no new results
        - Prevents infinite scraping when reaching end of available data
        - Balances completeness with efficiency
        
    Output Behavior:
        - Creates output file only if new data is found
        - Prints informative messages about scraping progress
        - Reports statistics for each page processed
        
    Performance Considerations:
        - Uses connection pooling for efficient HTTP requests
        - Minimizes database queries by checking existing IDs once
        - Only saves HTML for pages with new data
        
    Example Output:
        >>> main()
        Checking page 1...
        Page 1: 25 new results out of 25 total
        Checking page 2...
        Page 2: 20 new results out of 25 total
        Checking page 3...
        Page 3: No new results
        Checking page 4...
        Page 4: No new results
        ...
        Checking page 8...
        Page 8: No new results
        # Stops after 5 consecutive empty pages
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
