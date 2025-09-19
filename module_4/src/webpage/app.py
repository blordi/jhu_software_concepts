"""
Flask web application for graduate admissions analytics dashboard.

This module provides a comprehensive web interface for analyzing graduate school
applicant data from The GradCafe. It connects to a PostgreSQL database using
connection pooling, executes complex analytical queries, and displays interactive
results through a responsive dashboard interface.

The application features:
- Real-time data scraping and processing capabilities
- Comprehensive analytics with multiple statistical views
- Busy-state management to prevent concurrent operations
- Thread-safe operations with proper locking mechanisms
- Responsive web interface with formatted data display

Key Components:
    - Database Analytics: Complex SQL queries for admissions insights
    - Data Pipeline: Integration with scraping and cleaning modules
    - Web Interface: Flask routes for dashboard and data operations
    - Concurrency Control: Thread-safe scraping operations
    - Error Handling: Graceful degradation and user feedback

.. note::
   This application requires PostgreSQL database connectivity and access
   to The GradCafe website for data scraping operations.

.. warning::
   The application includes data scraping functionality. Ensure compliance
   with website terms of service and implement appropriate rate limiting.

Database Schema Requirements:
    The application expects an 'applicants' table with the following fields:
    - term: Application term (e.g., 'Fall 2025')
    - us_or_international: Applicant type ('American', 'International')
    - gpa: Grade Point Average (numeric)
    - gre, gre_v, gre_aw: GRE scores (numeric)
    - status: Application status (contains 'Accepted', 'Rejected', etc.)
    - degree: Degree type ('Masters', 'PhD')
    - llm_generated_university: Standardized university names

Routes:
    - GET /: Main dashboard with analytics
    - POST /rescrape: Trigger data scraping and processing
    - POST /refresh: Refresh dashboard data

Example Usage:
    >>> from app import app
    >>> app.run(debug=True)
    * Running on http://127.0.0.1:5000

.. seealso::
   :mod:`scrape` for data collection functionality
   :mod:`clean` for data processing pipeline
   :mod:`load_data` for database operations
"""

import sys
import os
from flask import Flask, render_template, request, url_for, redirect, jsonify

current_dir = os.path.dirname(os.path.abspath(__file__))  # webpage directory
module_3_dir = os.path.dirname(current_dir)              # module_3 directory
web_scraper_dir = os.path.join(module_3_dir, 'web_scraper')  # web_scraper directory

sys.path.extend([module_3_dir, web_scraper_dir])

import psycopg_pool
import threading
import clean
import scrape
import load_data
import json
    

# global variables for busy state tracking
scrape_lock = threading.Lock()
is_scraping = False

# pool = psycopg_pool.ConnectionPool(
#         "postgresql://postgres:Uphold-Removable-Radiator@localhost:5432/module_3_db"
#     )

def create_app(config=None):
    """
    Flask application factory.
    
    Creates and configures a Flask application instance with database
    connection pooling and route definitions.
    
    :param config: Configuration dictionary for the application
    :type config: dict, optional
    :return: Configured Flask application instance
    :rtype: Flask
    
    Example:
        >>> app = create_app({'TESTING': True, 'DATABASE_URL': 'test_db'})
        >>> client = app.test_client()
    """
    app = Flask(__name__)
    
    # Load configuration
    if config:
        app.config.update(config)
    
    # Set up database connection
    database_url = app.config.get('DATABASE_URL', 
        os.getenv('DATABASE_URL', "postgresql://postgres@localhost:5432/module_3_db"))
    
    global pool
    pool = psycopg_pool.ConnectionPool(database_url)
    @app.route('/')
    def dashboard():
        """
        Render the main analytics dashboard with comprehensive applicant statistics.
        
        This route serves as the primary interface for the application, executing
        multiple complex SQL queries to generate comprehensive analytics about
        graduate school applicant data. It provides insights into application
        trends, acceptance rates, academic metrics, and demographic patterns.
        
        :return: Rendered HTML template with analytics data or error message
        :rtype: str
        :raises Exception: When database queries fail or template rendering fails
        
        .. note::
        All percentage values are formatted to exactly 2 decimal places
        for consistent display across the dashboard interface.
        
        Analytics Provided:
            - Application volume by term (Fall 2025 focus)
            - International vs. domestic applicant percentages
            - Average academic metrics (GPA, GRE scores)
            - Acceptance rate analysis by various dimensions
            - Institution-specific statistics (JHU, Georgetown)
            - Comparative analysis by applicant type and degree
            
        SQL Queries Executed:
            1. Fall 2025 application count
            2. International student percentage
            3. Average GPA/GRE metrics with UNION operations
            4. American student GPA averages for Fall 2025
            5. Fall 2025 acceptance percentage
            6. Johns Hopkins University Masters application count
            7. Georgetown University PhD acceptance count
            8. University acceptance rates by applicant type (CTE query)
            9. GPA analysis by admission status and degree type
            
        Template Variables:
            - fall_2025_apps_count: Total Fall 2025 applications
            - international_percentage_pct: International student percentage (formatted)
            - averages_avg: List of academic metric averages
            - average_gpa_american_fall_25_avg: American student GPA average
            - fall_25_acceptange_percent_pct: Fall 2025 acceptance rate (formatted)
            - jhu_cs_apps_count: JHU Masters application count
            - georgetown_phd_cs_apps_count: Georgetown PhD acceptance count
            - int_domestic_acceptance_rates_rank: University comparison data
            - gpa_accepted_vs_rejected_degree_avg: GPA analysis by status/degree
            
        Error Handling:
            - Catches all database and rendering exceptions
            - Returns user-friendly error message on failure
            - Logs detailed error information for debugging
            
        Example Response:
            Renders dashboard.html with analytics showing:
            - "1,250 Fall 2025 Applications"
            - "34.56% International Students"
            - "Average GPA: 3.75, Average GRE: 320.50"
            - Interactive tables and charts
        """
        # Define SQL queries   
        # Number of Fall 2025 applications
        fall_2025_apps = """
                    SELECT COUNT (*) 
                    FROM applicants
                    WHERE TERM = 'Fall 2025';
                    """
        # Percentage of international students
        international_percentage = """
                SELECT
                    ROUND(
                        (SELECT COUNT(*) FROM applicants WHERE us_or_international = 'International') *100.0 /
                        (SELECT COUNT(*) FROM applicants), 
                        2
                ) AS international_percentage;
                    """
        # Average GPA, GRE, GRE V, GRE AW of applicants who provide these metrics
        averages = """
                SELECT 
                    'GPA' AS metric,
                    ROUND(AVG(gpa::NUMERIC), 2) AS average_value
                FROM applicants 
                WHERE gpa IS NOT NULL 

                UNION ALL

                SELECT 
                    'GRE' AS metric,
                    ROUND(AVG(gre::NUMERIC), 2) AS average_value
                FROM applicants 
                WHERE gre IS NOT NULL 

                UNION ALL

                SELECT 
                    'GRE Verbal' AS metric,
                    ROUND(AVG(gre_v::NUMERIC), 2) AS average_value
                FROM applicants 
                WHERE gre_v IS NOT NULL 

                UNION ALL

                SELECT 
                    'GRE Analytical Writing' AS metric,
                    ROUND(AVG(gre_aw::NUMERIC), 2) AS average_value
                FROM applicants 
                WHERE gre_aw IS NOT NULL;
                    """
        # Average GPA of applicants who applied for Fall 2025 who were accepted
        average_gpa_american_fall_25 = """
                    SELECT 
                    ROUND(AVG(CAST(gpa AS NUMERIC)),2) AS average_value
                    FROM applicants
                    WHERE us_or_international = 'American'
                    AND
                    term = 'Fall 2025'
                    AND
                    gpa <= 5;
                    """
        # What percentage of Fall 2025 applicants were accepted
        fall_25_acceptance_percent = """
                    SELECT
                        ROUND(
                            (COUNT(CASE WHEN status ILIKE '%Accepted%' THEN 1 END) * 100.00) / COUNT(*),
                            2
                        ) AS acceptance_percentage
                    FROM applicants
                    WHERE term = 'Fall 2025';
                    """
        # How many entries are from applicants who applied to JHU for a masters degrees?
        jhu_apps = """
                    SELECT COUNT (*)
                    FROM applicants
                    WHERE
                    llm_generated_university ILIKE '%Johns Hopkins University%'
                    AND
                    degree = 'Masters';                
                    """
        # How many entries from 2025 are acceptances from applicants who applied to Georgetown University for a PhD?
        georgetown_phd_apps = """
                    SELECT COUNT(*)
                    FROM applicants
                    WHERE llm_generated_university ILIKE '%Georgetown%'
                    AND degree ILIKE 'PhD'
                    AND status ILIKE '%accept%'
                    AND term ILIKE '%2025%';
                    """
        # Ranked list of universities with highest acceptance rates for international vs. domestic applicants
        int_domestic_acceptance_rates = """
                    WITH acceptance_by_status AS (
                    SELECT 
                        llm_generated_university,
                        us_or_international,
                        COUNT(*) as total_applications,
                        COUNT(CASE WHEN status ILIKE '%accepted%' THEN 1 END) as acceptances,
                        ROUND(
                            (COUNT(CASE WHEN status ILIKE '%accepted%' THEN 1 END) * 100.0) / COUNT(*), 
                            2
                        ) AS acceptance_rate
                    FROM applicants 
                    WHERE llm_generated_university IS NOT NULL 
                    AND us_or_international IS NOT NULL
                    AND status IS NOT NULL
                    GROUP BY llm_generated_university, us_or_international
                    HAVING COUNT(*) >= 5  -- Only universities with sufficient data
                    )
                    SELECT 
                        llm_generated_university,
                        MAX(CASE WHEN us_or_international = 'American' THEN acceptance_rate END) as us_acceptance_rate,
                        MAX(CASE WHEN us_or_international = 'International' THEN acceptance_rate END) as intl_acceptance_rate,
                        (MAX(CASE WHEN us_or_international = 'International' THEN acceptance_rate END) - 
                        MAX(CASE WHEN us_or_international = 'American' THEN acceptance_rate END)) as rate_difference
                    FROM acceptance_by_status
                    GROUP BY llm_generated_university
                    HAVING COUNT(DISTINCT us_or_international) = 2
                    ORDER BY rate_difference DESC;
                    """
        # Average GPA of accepted students vs. rejected students by degree
        gpa_accepted_vs_rejected_degree = """
                    SELECT 
                    degree,
                    CASE 
                        WHEN status ILIKE '%accepted%' THEN 'Accepted'
                        WHEN status ILIKE '%rejected%' THEN 'Rejected'
                        ELSE 'Other'
                    END as admission_status,
                    ROUND(AVG(CAST(gpa AS NUMERIC)), 2) as average_gpa
                FROM applicants 
                WHERE gpa IS NOT NULL 
                AND gpa <= 5
                AND status IS NOT NULL
                AND degree IS NOT NULL
                GROUP BY 
                    degree,
                    CASE 
                        WHEN status ILIKE '%accepted%' THEN 'Accepted'
                        WHEN status ILIKE '%rejected%' THEN 'Rejected'
                        ELSE 'Other'
                    END
                ORDER BY degree, admission_status;        
                    """
        # Execute queries and fetch results
        try:
            fall_2025_apps_results = execute_query(fall_2025_apps)
            international_percentage_results = execute_query(international_percentage)
            averages_results = execute_query(averages)
            average_gpa_american_fall_25_results = execute_query(average_gpa_american_fall_25)
            fall_25_acceptance_percent_results = execute_query(fall_25_acceptance_percent)
            jhu_apps_results = execute_query(jhu_apps)
            georgetown_phd_apps_results = execute_query(georgetown_phd_apps)
            int_domestic_acceptance_rates_results = execute_query(int_domestic_acceptance_rates)
            gpa_accepted_vs_rejected_degree_results = execute_query(gpa_accepted_vs_rejected_degree)
                # Render results in the dashboard template
            return render_template('dashboard.html',
                                fall_2025_apps_count = fall_2025_apps_results[0][0],
                                international_percentage_pct = f"{international_percentage_results[0][0]:.2f}",
                                averages_avg = averages_results,
                                average_gpa_american_fall_25_avg = average_gpa_american_fall_25_results[0][0],
                                fall_25_acceptange_percent_pct = f"{fall_25_acceptance_percent_results[0][0]:.2f}",
                                jhu_cs_apps_count = jhu_apps_results[0][0],
                                georgetown_phd_cs_apps_count = georgetown_phd_apps_results[0][0],
                                int_domestic_acceptance_rates_rank = int_domestic_acceptance_rates_results,
                                gpa_accepted_vs_rejected_degree_avg = gpa_accepted_vs_rejected_degree_results
                                )
        except Exception as e:
            return f"Error executing queries: {str(e)}"

    @app.route('/rescrape', methods=['POST'])    
    def rescrape():
        """
        Trigger data scraping and processing pipeline with concurrency control.
        
        This route handles requests to collect new data from The GradCafe, process
        it through the cleaning pipeline, and insert it into the database. It
        implements thread-safe busy-state management to prevent concurrent scraping
        operations that could cause data corruption or resource conflicts.
        
        :return: JSON response with busy status or redirect to dashboard
        :rtype: flask.Response
        :raises Exception: When scraping or database operations fail
        
        .. note::
        This route uses global state variables and threading locks to ensure
        only one scraping operation can run at a time across all requests.
        
        .. warning::
        Scraping operations can take several minutes. 
        
        Concurrency Control:
            - Checks global is_scraping flag before starting
            - Uses threading.Lock() for atomic state changes
            - Returns HTTP 409 (Conflict) if operation already in progress
            - Ensures proper cleanup in finally block
            
        Processing Pipeline:
            1. Check if scraping is already in progress
            2. Set busy state and acquire lock
            3. Execute run_rescrape() for data collection
            4. Execute add_to_db() for database insertion
            5. Clear busy state and release lock
            6. Redirect to dashboard for updated results
            
        Response Codes:
            - 409 Conflict: When scraping is already in progress
            - 500 Internal Server Error: When scraping/processing fails
            - 302 Found: Successful completion, redirects to dashboard
            
        JSON Responses:
            - {"busy": True}: When operation is already running
            - {"error": "message"}: When operation fails
            
        Thread Safety:
            - Uses global scrape_lock for atomic operations
            - Ensures is_scraping flag is always properly reset
            - Prevents race conditions between concurrent requests
            
        Example Usage:
            POST /rescrape
            → Returns: {"busy": true} (409) if already running
            → Returns: Redirect to / (302) if successful
            → Returns: {"error": "..."} (500) if failed
        """
        global is_scraping
        
        # Check if already scraping
        if is_scraping:
            return jsonify({"busy": True}), 409
        
        try:
            with scrape_lock:
                is_scraping = True
                run_rescrape()
                add_to_db()
            
            response = jsonify({"ok": True})
            response.headers['Refresh'] = '2; url=' + url_for('dashboard')
            return response, 200
        
        except Exception as e:
            print(f"Error occurred while rescraping: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            is_scraping = False
        
        # return redirect(url_for('dashboard')), 

    @app.route('/refresh', methods=['POST'])
    def refresh_dashboard():
        """
        Refresh the dashboard interface with current data.
        
        This route provides a way to reload the dashboard with the most current
        data from the database. It includes busy-state checking to prevent
        refreshing during active scraping operations, which could display
        incomplete or inconsistent data.
        
        :return: JSON response with busy status or redirect to dashboard
        :rtype: flask.Response
        
        .. note::
        This route checks the scraping state to ensure data consistency.
        If scraping is in progress, it returns a busy status instead of
        potentially showing partial results.
        
        Busy State Handling:
            - Checks global is_scraping flag
            - Returns HTTP 409 if scraping is in progress
            - Prevents displaying inconsistent data during updates
            
        Response Behavior:
            - 409 Conflict: When scraping is in progress
            - 302 Found: Normal refresh, redirects to dashboard
            
        Use Cases:
            - Manual dashboard refresh without data collection
            - Updating display after external data changes
            - Refreshing after configuration changes
            
        Example Usage:
            POST /refresh
            → Returns: {"busy": true} (409) if scraping active
            → Returns: Redirect to / (302) for normal refresh
        """
        global is_scraping
        
        # Check if scraping is in progress
        if is_scraping:
            return jsonify({"busy": True}), 409
        
        response = jsonify({"ok": True})
        response.headers['Refresh'] = '1; url=' + url_for('dashboard')
        return response, 200
    return app

def execute_query(query):
    """
    Execute a SQL query and return the results using connection pooling.
    
    This function provides a centralized interface for database operations,
    managing connections efficiently through the connection pool and ensuring
    proper resource cleanup after query execution.
    
    :param query: The SQL query string to execute
    :type query: str
    :return: List of tuples containing the query results
    :rtype: list[tuple]
    :raises psycopg.Error: When database connection or query execution fails
    :raises psycopg.ProgrammingError: When SQL syntax is invalid
    
    .. note::
       Uses connection pooling for efficient resource management.
       Connections are automatically returned to the pool after use.
       
    .. warning::
       This function does not provide SQL injection protection.
       Ensure queries are properly sanitized before calling.
       
    Connection Management:
        - Acquires connection from pool automatically
        - Creates cursor for query execution
        - Fetches all results into memory
        - Releases connection back to pool
        
    Example:
        >>> results = execute_query("SELECT COUNT(*) FROM applicants")
        >>> print(results[0][0])
        1250
        
        >>> gpa_data = execute_query("SELECT AVG(gpa) FROM applicants WHERE gpa IS NOT NULL")
        >>> print(f"Average GPA: {gpa_data[0][0]:.2f}")
        Average GPA: 3.75
    """
    with pool.connection() as conn:
        cur = conn.cursor()
        cur.execute(query)
        results = cur.fetchall()
        return results
def run_rescrape():
    """
    Execute the complete data scraping and cleaning pipeline.
    
    This function orchestrates the data collection process by calling the
    scraping module to fetch new data from The GradCafe, followed by the
    cleaning module to process and structure the raw HTML data.
    
    :raises Exception: When scraping or cleaning operations fail
    :raises urllib3.exceptions.HTTPError: When network requests fail
    :raises IOError: When file operations fail during processing
    
    .. note::
       This function calls external modules that perform network operations
       and file I/O. Execution time varies based on data volume and network speed.
       
    .. warning::
       This function performs web scraping operations. Ensure appropriate
       rate limiting and compliance with website terms of service.
       
    Processing Pipeline:
        1. scrape.main(): Collects new HTML data from The GradCafe
        2. clean.main(): Processes HTML and extracts structured data
        
    Side Effects:
        - Creates/updates raw HTML data files
        - Creates/updates cleaned JSON data files
        - May take several minutes for large datasets
        
    Example:
        >>> run_rescrape()
        Checking page 1...
        Page 1: 25 new results out of 25 total
        ...
        LLM processing completed successfully
    """
    scrape.main()
    clean.main()

def add_to_db():
    """
    Execute the complete data scraping and cleaning pipeline.
    
    This function orchestrates the data collection process by calling the
    scraping module to fetch new data from The GradCafe, followed by the
    cleaning module to process and structure the raw HTML data.
    
    :raises Exception: When scraping or cleaning operations fail
    :raises urllib3.exceptions.HTTPError: When network requests fail
    :raises IOError: When file operations fail during processing
    
    .. note::
       This function calls external modules that perform network operations
       and file I/O. Execution time varies based on data volume and network speed.
       
    .. warning::
       This function performs web scraping operations. Ensure appropriate
       rate limiting and compliance with website terms of service.
       
    Processing Pipeline:
        1. scrape.main(): Collects new HTML data from The GradCafe
        2. clean.main(): Processes HTML and extracts structured data
        
    Side Effects:
        - Creates/updates raw HTML data files
        - Creates/updates cleaned JSON data files
        - May take several minutes for large datasets
        
    Example:
        >>> run_rescrape()
        Checking page 1...
        Page 1: 25 new results out of 25 total
        ...
        LLM processing completed successfully
    """

    current_dir = os.path.dirname(os.path.abspath(__file__))
    module_3_dir = os.path.dirname(current_dir)
    cleaned_data_path = os.path.join(module_3_dir, 'update_llm_extend_applicant_data.json')
    
    try:
        with open(cleaned_data_path, 'r', encoding='utf-8') as f:
            cleaned_data = json.load(f)
        
        load_data.add_applicant_data(cleaned_data)
        print("Data successfully added to database")
        
    except Exception as e:
        print(f"Error in add_to_db: {e}")
        raise




if __name__ == '__main__': # pragma: no cover
    """
    Main execution block for running the Flask application.
    
    This block handles application startup when the module is executed directly.
    It includes proper cleanup registration and error handling for graceful
    shutdown of database connections and other resources.
    
    .. note::
       The application runs on host 0.0.0.0 and port 8080 with debug mode
       enabled for development purposes.
       
    .. warning::
       Debug mode should be disabled in production environments for security.
       
    Startup Configuration:
        - Host: 0.0.0.0 (accepts connections from any interface)
        - Port: 8080 (non-standard port for development)
        - Debug: True (enables auto-reload and detailed error pages)
        
    Cleanup Handling:
        - Registers cleanup function with atexit
        - Handles KeyboardInterrupt gracefully
        - Ensures database connection pool is properly closed
        - Prevents resource leaks on application shutdown
    """
    app = create_app()
    app.run(host='0.0.0.0', port=8080,debug=True, )

    import atexit
    atexit.register(lambda: pool.close())
    
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        pass
    finally:
        pool.close()   
    

