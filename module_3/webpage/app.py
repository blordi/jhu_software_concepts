"""
A Flask web application that connects to a PostgreSQL database using connection pooling.
Executes various SQL queries to analyze applicant data and displays the results on a dashboard.
"""

from flask import Flask, render_template, request, url_for, redirect
import psycopg_pool

app = Flask(__name__)
pool = psycopg_pool.ConnectionPool(
        "postgresql://postgres:Uphold-Removable-Radiator@localhost:5432/module_3_db"
    )

def execute_query(query):
        """
        Execute a SQL query and return the results.
        Args:
            query (str): The SQL query to execute.
        Returns:
            list: List of tuples containing the query results.
        """
    with pool.connection() as conn:
        cur = conn.cursor()
        cur.execute(query)
        results = cur.fetchall()
        return results

@app.route('/')
def dashboard():
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
    all_25_acceptange_percent = """
                SELECT
                    ROUND(
                        (COUNT(CASE WHEN status ILIKE '%Accepted%' THEN 1 END) * 100.00) / COUNT(*),
                        2
                    ) AS acceptance_percentage
                FROM applicants
                WHERE term = 'Fall 2025';
                """
    # How many entries are from applicants who applied to JHU for a masters degrees?
    jhu_cs_apps = """
                SELECT COUNT (*)
                FROM applicants
                WHERE
                llm_generated_university ILIKE '%Johns Hopkins University%'
                AND
                degree = 'Masters';                
                """
    # How many entries from 2025 are acceptances from applicants who applied to Georgetown University for a PhD?
    georgetown_phd_cs_apps = """
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
        fall_25_acceptange_percent_results = execute_query(fall_25_acceptange_percent)
        jhu_cs_apps_results = execute_query(jhu_cs_apps)
        georgetown_phd_cs_apps_results = execute_query(georgetown_phd_cs_apps)
        int_domestic_acceptance_rates_results = execute_query(int_domestic_acceptance_rates)
        gpa_accepted_vs_rejected_degree_results = execute_query(gpa_accepted_vs_rejected_degree)
            # Render results in the dashboard template
        return render_template('dashboard.html',
                               fall_2025_apps_count = fall_2025_apps_results[0][0],
                               international_percentage_pct = international_percentage_results[0][0],
                               averages_avg = averages_results,
                               average_gpa_american_fall_25_avg = average_gpa_american_fall_25_results[0][0],
                               fall_25_acceptange_percent_pct = fall_25_acceptange_percent_results[0][0],
                               jhu_cs_apps_count = jhu_cs_apps_results[0][0],
                               georgetown_phd_cs_apps_count = georgetown_phd_cs_apps_results[0][0],
                               int_domestic_acceptance_rates_rank = int_domestic_acceptance_rates_results,
                               gpa_accepted_vs_rejected_degree_avg = gpa_accepted_vs_rejected_degree_results
                               )
    except Exception as e:
        return f"Error executing queries: {str(e)}"
    
if __name__ == '__main__':
    app.run(debug=True)
    

