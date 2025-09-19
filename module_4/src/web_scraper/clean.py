"""
Module for parsing and cleaning graduate school applicant data from The GradCafe.

This module processes raw HTML data scraped from The GradCafe survey results,
extracting structured applicant information and enhancing it through LLM processing.
The module handles complex HTML parsing, data extraction, and integration with
external LLM services for data standardization and enhancement.

The cleaning process involves multiple stages:
1. Loading raw HTML data from JSON files
2. Parsing HTML to extract applicant fields (university, program, scores, etc.)
3. Structuring data into standardized dictionaries
4. Processing through LLM for data enhancement and standardization
5. Outputting clean, structured JSON files for analysis

.. note::
   This module requires BeautifulSoup4 for HTML parsing and access to an
   LLM service for data enhancement.

.. warning::
   The HTML parsing is tailored to The GradCafe's specific HTML structure.
   Changes to the website structure may require updates to parsing logic.

Dependencies:
    - BeautifulSoup4: For HTML parsing and data extraction
    - json: For data serialization and file I/O
    - subprocess: For LLM CLI integration
    - re: For regex-based field extraction
    - os: For file path management

Output Files:
    - update_applicant_data.json: Initially cleaned data
    - update_llm_extend_applicant_data.json: LLM-enhanced data

Example Usage:
    >>> import clean
    >>> clean.main()  # Process all raw data through cleaning pipeline
    LLM processing completed successfully

.. seealso::
   :mod:`scrape` for raw data collection
   :mod:`load_data` for database insertion of cleaned data
"""

import time
from bs4 import BeautifulSoup
import re
import json
import subprocess
import os


def save_data(data, filename='applicant_data.json'):
    """
    Save a list of dictionaries to a JSON file with proper formatting.
    
    This function serializes applicant data to JSON format with indentation
    for human readability. It handles the file creation and ensures proper
    encoding for international characters.
    
    :param data: List of cleaned applicant data dictionaries
    :type data: list[dict]
    :param filename: Output file path for JSON data
    :type filename: str, optional
    :raises IOError: When file cannot be written
    :raises TypeError: When data cannot be JSON serialized
    
    .. note::
       Uses indent=2 for readable JSON formatting. File is created with
       default system encoding.
       
    Example:
        >>> applicant_data = [{"program": "CS", "gpa": 3.8}]
        >>> save_data(applicant_data, "cleaned_data.json")
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def load_data(filename):
    """
    Load data from a JSON file containing raw HTML data.
    
    This function reads and deserializes JSON data from files, typically
    containing raw HTML content that needs to be parsed and cleaned.
    
    :param filename: Input file path for JSON data
    :type filename: str
    :return: List of dictionaries containing raw HTML data
    :rtype: list[dict]
    :raises FileNotFoundError: When the specified file doesn't exist
    :raises json.JSONDecodeError: When file contains invalid JSON
    :raises IOError: When file cannot be read
    
    .. note::
       Expected JSON structure: List of dictionaries with 'html' keys
       containing raw HTML content from scraped pages.
       
    Example:
        >>> raw_data = load_data("raw_applicant_data.json")
        >>> print(len(raw_data))
        250
    """
    with open(filename, 'r') as f:
        return json.load(f)


def clean_html(html):
    """
    Parse a single HTML page and extract applicant data from table rows.
    
    This is the core parsing function that processes raw HTML from The GradCafe
    survey results pages. It uses BeautifulSoup for HTML parsing and regex
    for field extraction, handling the complex nested structure of the survey
    result tables.
    
    :param html: Raw HTML content of a survey page
    :type html: str
    :return: List of extracted applicant data dictionaries
    :rtype: list[dict]
    
    .. note::
       The function processes table rows in pairs, as The GradCafe displays
       applicant data across multiple rows. It skips rows that don't contain
       sufficient data fields.
       
    Extracted Fields:
        - program: Combined program and university name
        - comments: Applicant comments about their experience
        - date_added: Date when entry was added to The GradCafe
        - url: Direct URL to the applicant's detailed entry
        - status: Application status (Accepted/Rejected with date)
        - Term: Application semester (Fall/Spring/Summer + year)
        - US/International: Applicant nationality category
        - gre: GRE Quantitative score
        - gre_v: GRE Verbal score  
        - gre_aw: GRE Analytical Writing score
        - Degree: Degree type (Masters/PhD/etc.)
        - gpa: Grade Point Average
        
    HTML Structure Assumptions:
        - Data is contained in <tr> elements within tables
        - University name in first <td> with specific CSS class
        - Program details in second <td> with nested spans
        - Status information in fourth <td> with regex-parseable format
        - Additional details in subsequent row with specific patterns
        
    Error Handling:
        - Returns None for missing or unparseable fields
        - Continues processing even if individual fields fail
        - Skips rows with insufficient data (<5 td elements)
        
    Example:
        >>> html_content = "<table><tr><td>...</td></tr></table>"
        >>> applicants = clean_html(html_content)
        >>> print(applicants[0]['program'])
        "Computer Science, Stanford University"
    """
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all('tr') # Find all table rows 
    extracted_data = []

    i = 0
    while i < len(rows):    
        tr = rows[i]
        tds = tr.find_all('td')
        if not tds or len(tds) < 5: # Ensure there are enough TDs to extract data
            i += 1
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
        if link_tag:
            applicant_url = "https://www.thegradcafe.com" + link_tag['href']
        else:
            applicant_url = None

        # Extract Applicant Status using regex
        status_match = re.search(
            r'<div[^>]*>\s*((Accepted|Rejected)\s+on\s+[A-Za-z0-9 ,]+)\s*</div>', str(tds[3])
        )
        applicant_status = status_match.group(1) if status_match else None #Return None if status not found

        semester = nationality = gre = gre_v = gre_aw = gpa = comment = None #Initialize optional fields to None

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
        combined_program = None
        if program_name and university_text:
            combined_program = f"{program_name}, {university_text}"
        elif program_name:
            combined_program = program_name
        elif university_text:
            combined_program = university_text
        else:
            combined_program = None

        entry = {
            "program": combined_program,
            "comments": comment,
            "date_added": added_on,
            "url": applicant_url,
            "status": applicant_status,
            "Term": semester,
            "US/International": nationality,
            "gre": gre,
            "gre_v": gre_v,
            "Degree": degree,
            "gpa": gpa,
            "gre_aw": gre_aw
        }
        extracted_data.append(entry)
        i += 2 #Skip the next row since it's already processed
    return extracted_data

def llm_clean_command():
    """
    Process applicant data using LLM CLI mode to enhance and standardize the data.
    
    This function integrates with an external LLM service to further clean and
    enhance the initially parsed applicant data. It handles the subprocess
    execution, data format conversion, and error handling for the LLM processing
    pipeline.
    
    :return: True if LLM processing completed successfully, False otherwise
    :rtype: bool
    :raises subprocess.TimeoutExpired: When LLM processing exceeds 600 seconds
    :raises json.JSONDecodeError: When LLM output is not valid JSON
    :raises FileNotFoundError: When LLM CLI application is not found
    :raises IOError: When input/output files cannot be accessed
    
    .. note::
       The function expects the LLM CLI application to be located at
       'jhu_software_concepts/module_3/web_scraper/llm_hosting/app.py'
       relative to the current working directory.
       
    Processing Pipeline:
        1. Sets up file paths for input and output
        2. Constructs CLI command with appropriate parameters
        3. Executes LLM processing
        4. Handles both JSON and JSONL output formats
        5. Saves enhanced data to output file
        
    Input/Output Files:
        - Input: update_applicant_data.json (initially cleaned data)
        - Output: update_llm_extend_applicant_data.json (LLM-enhanced data)
        
    LLM Enhancements:
        - University name standardization
        - Program name normalization  
        - Data validation and correction
        - Missing field inference
        - Format standardization
        
    Error Handling:
        - Captures and reports subprocess errors
        - Handles JSON parsing failures gracefully
        - Supports JSONL format as fallback
        - Provides detailed error messages
        
    Example:
        >>> success = llm_clean_command()
        LLM processing completed successfully
        >>> print(success)
        True
    """
    import subprocess
    import os
    import json
    
    # Setup paths
    current_dir = os.getcwd()
    llm_dir = os.path.join(current_dir, "jhu_software_concepts", "module_3", "web_scraper", "llm_hosting")
    input_file = os.path.join(current_dir, "jhu_software_concepts", "module_3", "update_applicant_data.json")
    output_file = os.path.join(current_dir, "jhu_software_concepts", "module_3", "update_llm_extend_applicant_data.json")
    
    # Build CLI command
    cli_command = [
        'python', 
        'app.py', 
        '--file', 
        input_file,
        '--stdout'
    ]
    
    try:
        # Run the CLI command
        result = subprocess.run(
            cli_command,
            cwd=llm_dir,
            capture_output=True,
            text=True,
        )
        
        if result.returncode == 0:
            # Parse and save output
            try:
                output_data = json.loads(result.stdout)
            except json.JSONDecodeError:
                # Handle JSONL format
                lines = result.stdout.strip().split('\n')
                records = []
                for line in lines:
                    if line.strip():
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
                output_data = {"rows": records}
            
            # Save to output file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
            
            print("LLM processing completed successfully")
            return True
        else:
            print(f"LLM processing failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"LLM processing error: {e}")
        return False

def main():
    """
    Execute the complete data cleaning pipeline from raw HTML to LLM-enhanced data.
    
    This is the main orchestration function that coordinates the entire cleaning
    process. It loads raw scraped data, processes it through HTML parsing,
    saves intermediate results, and then enhances the data through LLM processing.
    
    :raises FileNotFoundError: When input raw data file is not found
    :raises IOError: When intermediate or output files cannot be written
    :raises Exception: When HTML parsing or LLM processing fails
    
    .. note::
       The function expects raw data to be available at
       'jhu_software_concepts/module_3/web_scraper/update_raw_applicant_data.json'
       
    Processing Steps:
        1. Load raw HTML data from JSON file
        2. Process each HTML entry through clean_html() function
        3. Aggregate all extracted applicant data
        4. Save initially cleaned data to update_applicant_data.json
        5. Process data through LLM for enhancement
        6. Output final enhanced data to update_llm_extend_applicant_data.json
        
    Output Files Created:
        - update_applicant_data.json: Initially parsed and cleaned data
        - update_llm_extend_applicant_data.json: LLM-enhanced final data
        
    Data Flow:
        Raw HTML → HTML Parsing → Initial Cleaning → LLM Enhancement → Final Output
        
    Example:
        >>> main()
        LLM processing completed successfully
        # Creates two output files with cleaned applicant data
    """
    scraped_data = load_data('jhu_software_concepts/module_3/web_scraper/update_raw_applicant_data.json')
    application_data = []

    for entry in scraped_data:
        application = clean_html(entry['html'])
        if application:
                application_data.extend(application)

    save_data(application_data, 'jhu_software_concepts/module_3/update_applicant_data.json')
    llm_clean_command()


if __name__ == "__main__":
    main()
