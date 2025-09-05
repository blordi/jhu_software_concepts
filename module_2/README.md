Created by Benjamin Lordi: F83F95  for JHU Modern Software Concepts in Python on 9.5.25

## About
This project was created for Module 2, assignment 2 Webscrape, due on 9.7.25

This project scrapes data from thegradcafe.com using URLLIB3 and BeautifulSoup. It then cleans that data to only include:

o Program Name
o University
o Comments (if available)
o Date of Information Added to Grad Café
o URL link to applicant entry
o Applicant Status
▪ If Accepted: Acceptance Date
▪ If Rejected: Rejection Date
o Semester and Year of Program Start (if available)
o International / American Student (if available)
o GRE Score (if available)
o GRE V Score (if available)
o Masters or PhD (if available)
o GPA (if available)
o GRE AW (if available)

finally it saves the data as a series of dictionary key-value pairs in a json file called applicant_data.json.

Before beginning the project I checked robots.txt for thegradcafe.com (see screenshot).  If you are attempting to use this code, ensure that scraping thegradcafe.com is still allowed.

## Approach

This project consists of 2 files, scrape.py clean.py.  scrape.py.  scrape.py uses urllib3 to connect to thegradcafe.com and pull all the html from the /survey pages to be cleaned later.  It uses BeautifulSoup to parse the html and returns a prettified version.  It then saves the data as raw_applicant_data.json to be used in clean.py.  Clean.py uses a mix of BeautifulSoup string methods and Regex searches to extract the required elements from the raw html and returns a dictionary.  The dictionary is saved in a json file as applicant data.

The final step is to use a locally hosted llm in the llm_hosting file to clean the program name field and return the llm_extend_applicant_data.json file.

## Acknowledgements

The llm_hosting file came directly from Liv d'Aliberti and I did not modify it.  Some of the Regex searches were written by Claude 4 Opus.  The rest of the work is my own.

## Known Bugs

There are no known bugs at this time.