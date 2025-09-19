API Reference
=============

This section provides detailed documentation for all modules in the Graduate Admissions Analytics application.

Web Application (app.py)
-------------------------

The main Flask application that serves the analytics dashboard.

**Key Functions:**

* ``execute_query(query)`` - Execute SQL queries with connection pooling
* ``run_rescrape()`` - Trigger data scraping and cleaning pipeline  
* ``add_to_db()`` - Load processed data into database
* ``dashboard()`` - Main analytics dashboard route
* ``rescrape()`` - Handle data collection requests
* ``refresh_dashboard()`` - Refresh dashboard with current data

Data Loading (load_data.py)
----------------------------

Handles loading cleaned applicant data into the PostgreSQL database.

**Key Functions:**

* ``load_data(filename)`` - Load JSON data with multiple format support
* ``create_applicant_table()`` - Create database table schema
* ``add_applicant_data(data)`` - Insert applicant records into database
* ``drop_table()`` - Remove applicants table

Data Cleaning (clean.py)
-------------------------

Processes raw HTML from The GradCafe into structured data.

**Key Functions:**

* ``clean_html(html)`` - Parse HTML and extract applicant fields
* ``save_data(data, filename)`` - Save processed data to JSON
* ``load_data(filename)`` - Load raw HTML data from files
* ``llm_clean_command()`` - Enhance data using LLM processing
* ``main()`` - Execute complete cleaning pipeline

Web Scraping (scrape.py)
-------------------------

Collects raw HTML data from The GradCafe survey results.

**Key Functions:**

* ``scrape_data(url)`` - Fetch and parse HTML from URL
* ``get_existing_ids()`` - Query database for existing result IDs
* ``new_results(page_number, existing_ids)`` - Check page for new data
* ``save_data(data, filename)`` - Save scraped HTML to file
* ``main()`` - Execute intelligent scraping with duplicate detection

Database Queries (query_data.py)
---------------------------------

Executes analytical queries on applicant data for insights.

**Query Categories:**

* Application volume analysis (Fall 2025 focus)
* International vs domestic student percentages
* Academic metrics averages (GPA, GRE scores)
* Acceptance rate analysis by various dimensions
* Institution-specific statistics
* Comparative analysis by applicant type and degree

**Note:** This module executes automatically when imported and prints results to console.