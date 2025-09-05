from bs4 import BeautifulSoup
import re
import json

def load_data(filename):
    with open(filename, 'r') as f:
        return json.load(f)


def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all('tr')

    for i in range(len(rows)):
        tr = rows[i]
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

        status_match = re.search(
            r'<div[^>]*>\s*((Accepted|Rejected)\s+on\s+[A-Za-z0-9 ,]+)\s*</div>', str(tds[3])
        )
        applicant_status = status_match.group(1) if status_match else None

        semester = nationality = gre = gre_v = gre_aw = gpa = None

        if i+1 < len(rows):
            next_tr = rows[i+1]
            next_tds = next_tr.find_all('td')
            
            if next_tds:
                tds_html = str(next_tds)
                
                semester_match = re.search(r'(Spring|Summer|Fall|Winter)\s+\d{4}', tds_html)
                semester = semester_match.group(0) if semester_match else None

                nationality_match = re.search(r'<div[^>]*>\s*(International|American)\s*</div>', tds_html)
                nationality = nationality_match.group(1) if nationality_match else None

                gre_match = re.search(r'<div[^>]*>\s*GRE (\d+)\s*</div>', tds_html)
                gre = gre_match.group(1) if gre_match else None

                gre_v_match = re.search(r'<div[^>]*>\s*GRE V (\d+)\s*</div>', tds_html)
                gre_v = gre_v_match.group(1) if gre_v_match else None

                gre_aw_match = re.search(r'<div[^>]*>\s*GRE AW ([\d.]+)\s*</div>', tds_html)
                gre_aw = gre_aw_match.group(1) if gre_aw_match else None

                gpa_match = re.search(r'<div[^>]*>\s*GPA ([\d.]+)\s*</div>', tds_html)
                gpa = gpa_match.group(1) if gpa_match else None

                comment_match = re.search(
                    r'<p class="tw-text-gray-500 tw-text-sm tw-my-0">([^<]+)</p>', str(rows[i + 2]) if i + 2 < len(rows) else ""
                    )
                comment = comment_match.group(1) if comment_match else None

        print("Program Name:", program_name)
        print("University:", university_text)
        print("Comment:", comment)
        print("Added On:", added_on)
        print("Semester:", semester)
        print("Applicant URL:", applicant_url)
        print("Applicant Status:", applicant_status)   
        print("Semester:", semester)
        print("Nationality", nationality)
        print("GRE:", gre)  
        print("GRE V:", gre_v)  
        print("Degree:", degree)
        print("GPA:", gpa) 
        print("GRE AW:", gre_aw)    
        print("-" * 40)
        


scraped_data = load_data('raw_applicant_data.json')

for entry in scraped_data:
    clean_html(entry['html'])