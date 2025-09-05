from bs4 import BeautifulSoup
import re
import json

def load_data(filename):
    with open(filename, 'r') as f:
        return json.load(f)


def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")

    for tr in soup.find_all('tr'):
        tds = tr.find_all('td')
        if not tds or len(tds) < 5:
            continue

        university = tds[0].find("div", class_="tw-font-medium tw-text-gray-900 tw-text-sm")
        university_text = university.get_text(strip=True) if university else None
        
        program_span = tds[1].find("span") 
        program_name = program_span.get_text(strip=True) if program_span else None

        added_on = tds[2].get_text(strip=True) if len(tds) > 2 else None

        print("Program Name:", program_name)
        print("University:", university_text)
        print("Added On:", added_on)


scraped_data = load_data('raw_applicant_data.json')

for entry in scraped_data:
    clean_html(entry['html'])