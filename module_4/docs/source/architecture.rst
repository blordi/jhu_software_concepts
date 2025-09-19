Architecture
============

System Overview
---------------

The application follows a three-layer architecture:

Web Layer
~~~~~~~~~
- **Flask Application** (``src/webpage/app.py``)
- Handles HTTP requests and responses
- Renders analytics dashboard
- Manages user interactions and data display

ETL Layer  
~~~~~~~~~
- **Scraping** (``src/scrape.py``): Collects raw data from The GradCafe
- **Cleaning** (``src/clean.py``): Processes and structures raw HTML data
- **Loading** (``src/load_data.py``): Inserts cleaned data into database

Database Layer
~~~~~~~~~~~~~~
- **PostgreSQL Database**: Stores applicant data
- **Query Module** (``src/query_data.py``): Executes analytical queries
- **Connection Pooling**: Efficient database resource management

Data Flow
---------

1. **Collection**: Web scraping gathers raw HTML from The GradCafe
2. **Processing**: HTML parsing extracts structured applicant data  
3. **Enhancement**: LLM processing standardizes and enriches data
4. **Storage**: Cleaned data inserted into PostgreSQL database
5. **Analysis**: Complex SQL queries generate insights
6. **Presentation**: Flask web interface displays interactive analytics