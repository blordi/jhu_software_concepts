from bs4 import BeautifulSoup
import re
import json
"""
    Parses and cleans applicant data from raw HTML files scraped from The GradCafe survey results.

    - Loads raw HTML data from JSON.
    - Extracts relevant fields (university, program, status, scores, etc.) from each table row.
    - Saves cleaned data as a list of dictionaries to a new JSON file for further analysis.
"""

def save_data(data, filename='applicant_data.json'):
    """
    Save a list of dictionaries to a JSON file.
    Args:
        data (list): List of cleaned applicant data dictionaries.
        filename (str): Output file path for JSON data.
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def load_data(filename):
    """
    Load data from a JSON file.
    Args:
        filename (str): Input file path for JSON data.
    Returns:
        list: List of dictionaries containing raw HTML data.
    """
    with open(filename, 'r') as f:
        return json.load(f)


def clean_html(html):
    """
    Parse a single HTML page and extract applicant data from table rows.
    Args:
        html (str): Raw HTML content of a survey page.
    Returns:
        dict: Dictionary of extracted applicant data fields, or None if not found.
    """
    soup = BeautifulSoup(html, "html.parser")
    
    rows = soup.find_all('tr') # Find all table rows 

    for i in range(len(rows)): # Iterate through each row and extract TD elements
        tr = rows[i]
        tds = tr.find_all('td')
        if not tds or len(tds) < 5: # Ensure there are enough TDs to extract data
            continue
        
        # Extract University name using BeautifulSoup string methods
        university = tds[0].find("div", class_="tw-font-medium tw-text-gray-900 tw-text-sm")
        university_text = university.get_text(strip=True) if university else None #Return None if university not found

        # Extract Program name
        program_div = tds[1].find('div', class_='tw-text-gray-900')
        program_span = tds[1].find("span") 
        program_name = program_span.get_text(strip=True) if program_span else None #Return None if program name not found

        # Extract date added to The Grad Cafe
        added_on = tds[2].get_text(strip=True) if len(tds) > 2 else None #Return None if added_on not found

        # Extract Degree type
        degree_span = program_div.find('span', class_='tw-text-gray-500') if program_div else None 
        degree = degree_span.get_text(strip=True) if degree_span else None #Return None if degree not found

        # Extract Applicant URL
        link_tag = tds[4].find('a', href=lambda x: x and "/result/" in x)
        applicant_url = "https://www.thegradcafe.com"+link_tag['href'] if link_tag else None #Return None if link_tag not found

        # Extract Application Number from href
        app_number_tag = tds[4].find('a', href=lambda x: x in x)
        app_number = app_number_tag['href'] if app_number_tag else None #Return None if app_number_tag not found
        app_number = app_number.replace("/result/", "") #remove prefix to get just the number

        # Extract Applicant Status using regex
        status_match = re.search(
            r'<div[^>]*>\s*((Accepted|Rejected)\s+on\s+[A-Za-z0-9 ,]+)\s*</div>', str(tds[3])
        )
        applicant_status = status_match.group(1) if status_match else None #Return None if status not found

        semester = nationality = gre = gre_v = gre_aw = gpa = None #Initialize optional fields to None

        # Extract additional details from the next row if it exists
        if i+1 < len(rows):
            next_tr = rows[i+1]
            next_tds = next_tr.find_all('td')
            if next_tds:
                tds_html = str(next_tds)
                
                # Extract Semester using regex
                semester_match = re.search(r'(Spring|Summer|Fall|Winter)\s+\d{4}', tds_html)
                semester = semester_match.group(0) if semester_match else None #Return None if semester not found

                # Extract International/American status using regex
                nationality_match = re.search(r'<div[^>]*>\s*(International|American)\s*</div>', tds_html)
                nationality = nationality_match.group(1) if nationality_match else None #Return None if nationality not found

                # Extract GRE scores using regex
                gre_match = re.search(r'<div[^>]*>\s*GRE (\d+)\s*</div>', tds_html)
                gre = gre_match.group(1) if gre_match else None #Return None if gre not found   

                # Extract GRE V score using regex
                gre_v_match = re.search(r'<div[^>]*>\s*GRE V (\d+)\s*</div>', tds_html)
                gre_v = gre_v_match.group(1) if gre_v_match else None #Return None if gre_v not found

                # Extract GRE AW score using regex
                gre_aw_match = re.search(r'<div[^>]*>\s*GRE AW ([\d.]+)\s*</div>', tds_html)
                gre_aw = gre_aw_match.group(1) if gre_aw_match else None #Return None if gre_aw not found
                
                # Extract GPA using regex
                gpa_match = re.search(r'<div[^>]*>\s*GPA ([\d.]+)\s*</div>', tds_html)
                gpa = gpa_match.group(1) if gpa_match else None #Return None if gpa not found

                # Extract Comment using regex
                comment_match = re.search(
                    r'<p class="tw-text-gray-500 tw-text-sm tw-my-0">([^<]+)</p>', str(rows[i + 2]) if i + 2 < len(rows) else ""
                    )
                comment = comment_match.group(1).strip() if comment_match else None
        
        # Return dictionary of extracted fields
        return {
            "app_number": app_number,
            "program_name": program_name,
            "university": university_text,
            "comment": comment,
            "added_on": added_on,
            "semester": semester,
            "applicant_url": applicant_url,
            "applicant_status": applicant_status,
            "nationality": nationality,
            "gre": gre,
            "gre_v": gre_v,
            "degree": degree,
            "gpa": gpa,
            "gre_aw": gre_aw
        } 


scraped_data = load_data('jhu_software_concepts/module_2/web_scraper/raw_applicant_data.json')
application_data = []

for entry in scraped_data:
   application = clean_html(entry['html'])
   if application:
         application_data.append(application)

save_data(application_data, 'jhu_software_concepts/module_2/web_scraper/applicant_data.json')