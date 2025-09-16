Created by Benjamin Lordi: F83F95  for JHU Modern Software Concepts in Python on 9.14.25

## About
This project was created for Module 3, assignment 3 SQL Data Analysis, due on 9.14.25

This project uses the collected data from the GradCafe that was scraped in assignment 2, and loads it into a PostgreSQL database.  It uses the load_data.py program to connect to a database, create a table called applicants, and load data into the table.  query_data.py uses SQL queries sent through psycopg to the database to answer a serises of questions about the data.  The analysis is then shown on a dynamic dashboard hosted through a flask webpage with update buttons to refresh the data and the analysis.  Finally a pdf title limitations.pdf explains some of the drawbacks to using the GradCafe data for analysis.

## Approach

This project consists of load_data.py and query_data.py to manage the database and query using SQL.  The webpage is created using app.py and the dashboard.html template.  app.py uses scrape.py and clean.py to rescrape thegradcafe.com and clean the new data before it is added to the database.  app.py uses load_data.py to add the new data into the database before refreshing to show the new results.

clean.py utilizes beautifulsoup, regex, and a locally hosted llm to clean the data.

## Acknowledgements

The llm_hosting file came directly from Liv d'Aliberti and I did not modify it.  Some of the Regex searches were written by Claude 4 Opus.  Claude 4 Opus also helped write the html and css code as well as debug some of the SQL queries. I also relied on Claude 4 Opus to help with debuging code and fixing server issues. 

## Known Bugs

There are no known bugs at this time.