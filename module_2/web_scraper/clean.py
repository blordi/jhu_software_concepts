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
        
        program_div = tds[1].find('div', class_='tw-text-gray-900')
        program_span = tds[1].find("span") 
        program_name = program_span.get_text(strip=True) if program_span else None

        added_on = tds[2].get_text(strip=True) if len(tds) > 2 else None

        degree_span = program_div.find('span', class_='tw-text-gray-500') if program_div else None
        degree = degree_span.get_text(strip=True) if degree_span else None

        link_tag = tds[4].find('a', href=lambda x: x and "/result/" in x)
        applicant_url = "https://www.thegradcafe.com"+link_tag['href'] if link_tag else None

        print("Program Name:", program_name)
        print("University:", university_text)
        print("Added On:", added_on)
        print("Degree:", degree)
        print("Applicant URL:", applicant_url)


scraped_data = load_data('raw_applicant_data.json')

for entry in scraped_data:
    clean_html(entry['html'])