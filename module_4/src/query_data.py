"""
Module to query data from a PostgreSQL database for graduate admissions analysis.

This module connects to a PostgreSQL database and executes a comprehensive set of
analytical queries on graduate school applicant data. The queries provide insights
into application trends, acceptance rates, academic metrics, and demographic patterns.

The module executes automatically when imported, running all predefined queries
and printing results to the console. This provides a complete analytical overview
of the graduate admissions dataset.

.. note::
   This module requires a PostgreSQL database running on localhost:5432
   with database name 'module_3_db' containing an 'applicants' table.

.. warning::
   All queries execute immediately upon module import. Ensure database
   connectivity before importing this module.

Database Requirements:
    The applicants table must contain the following fields:
    - term: Application term (e.g., 'Fall 2025')
    - us_or_international: Applicant type ('American', 'International', 'Other')
    - gpa: Grade Point Average (numeric, typically 0-5 scale)
    - gre: GRE total score (numeric, typically 260-340 scale)
    - gre_v: GRE Verbal score (numeric, typically 130-170 scale)
    - gre_aw: GRE Analytical Writing score (numeric, typically 0-6 scale)
    - status: Application status (contains 'Accepted', 'Rejected', etc.)
    - degree: Degree type ('Masters', 'PhD', etc.)
    - llm_generated_university: University name (processed by LLM)

Queries Executed:
    1. Fall 2025 application count
    2. International student percentage
    3. Average academic metrics (GPA, GRE scores)
    4. American student GPA averages for Fall 2025
    5. Fall 2025 acceptance percentage
    6. Average GPA of accepted Fall 2025 applicants
    7. Johns Hopkins University Masters application count
    8. Georgetown University PhD acceptance count for 2025
    9. University acceptance rates by applicant type
    10. GPA comparison by admission status and degree type

Example Usage:
    >>> import query_data  # Automatically executes all queries
    How many entries do you have in your database who have applied for Fall 2025?
    [(1250,)]
    
    What percentage of entries are from international students...
    [(34.56,)]
    
    ... (additional query results)

.. seealso::
   :mod:`load_data` for database table creation and data insertion
   :mod:`app` for web interface to these analytics
"""

import psycopg_pool

pool = psycopg_pool.ConnectionPool(
        "postgresql://postgres:Uphold-Removable-Radiator@localhost:5432/module_3_db"
    )

conn = pool.getconn()
with conn.cursor() as cur:

    # Query 1: Count of Fall 2025 applications
    """
    Count total number of applications for Fall 2025 term.
    
    This query provides a baseline count of how many applicant records
    exist for the Fall 2025 application cycle.
    
    SQL Logic:
        - Filters applicants table for exact term match 'Fall 2025'
        - Returns single count value
        
    Expected Output: Single integer representing total Fall 2025 applications
    """
    cur.execute("""
        SELECT COUNT (*) 
                FROM applicants
                WHERE TERM = 'Fall 2025';""")
    print("How many entries do you have in your database who have applied for Fall 2025?\n", cur.fetchall(),"\n\n")

    # Query 2: Percentage of international students
    """
    Calculate percentage of international vs. total applicants.
    
    This query computes the proportion of international students in the dataset
    by comparing international applicant count to total applicant count.
    
    SQL Logic:
        - Subquery counts international applicants
        - Divides by total applicant count and multiplies by 100
        - Rounds result to 2 decimal places for readability
        
    Expected Output: Percentage value (e.g., 34.56 for 34.56%)
    """
    cur.execute("""
            SELECT
                ROUND(
                    (SELECT COUNT(*) FROM applicants WHERE us_or_international = 'International') *100.0 /
                    (SELECT COUNT(*) FROM applicants), 
                    2
            ) AS international_percentage;
                """)
    print("What percentage of entries are from international students (not American or Other)\n", cur.fetchall(),"\n\n")

    # Query 3: Average academic metrics (GPA, GRE scores)
    """
    Calculate average values for key academic metrics.
    
    This comprehensive query computes averages for GPA and all GRE components,
    providing a complete academic profile of the applicant pool. Uses UNION ALL
    to combine results for different metrics into a single result set.
    
    SQL Logic:
        - Separate SELECT for each metric (GPA, GRE, GRE Verbal, GRE AW)
        - Filters out NULL values and applies reasonable upper bounds
        - Includes count of records with data for each metric
        - Rounds averages to 2 decimal places
        
    Data Validation:
        - GPA: Filters values <= 5 (assumes 5-point scale)
        - GRE (Quantitative): Filters values <= 170 
        - GRE Verbal: Filters values <= 170 (correct range)
        - GRE AW: Filters values <= 6 (correct range)
        
    Expected Output: Four rows with metric name, count, and average value
    """
    cur.execute("""
            SELECT 
                'GPA' AS metric,
                COUNT(gpa) AS count_with_data,
                ROUND(AVG(CAST(gpa AS NUMERIC)), 2) AS average_value
            FROM applicants 
            WHERE gpa IS NOT NULL AND gpa <= 5

            UNION ALL

            SELECT 
                'GRE' AS metric,
                COUNT(gre) AS count_with_data,
                ROUND(AVG(CAST(gre AS NUMERIC)), 2) AS average_value
            FROM applicants 
            WHERE gre IS NOT NULL AND gre <= 170

            UNION ALL

            SELECT 
                'GRE Verbal' AS metric,
                COUNT(gre_v) AS count_with_data,
                ROUND(AVG(CAST(gre_v AS NUMERIC)), 2) AS average_value
            FROM applicants 
            WHERE gre_v IS NOT NULL AND gre_v <= 170

            UNION ALL

            SELECT 
                'GRE Analytical Writing' AS metric,
                COUNT(gre_aw) AS count_with_data,
                ROUND(AVG(CAST(gre_aw AS NUMERIC)), 2) AS average_value
            FROM applicants 
            WHERE gre_aw IS NOT NULL AND gre_aw <= 6;
                """)
    print("What is the average GPA, GRE, GRE V, GRE AW of applicants who provide these metrics?\n", cur.fetchall(),"\n\n")
    
    # Query 4: Average GPA of American students for Fall 2025
    """
    Calculate average GPA specifically for American students applying to Fall 2025.
    
    This query focuses on domestic applicant academic performance for the
    most recent application cycle, providing targeted demographic insights.
    
    SQL Logic:
        - Filters for American applicants only
        - Restricts to Fall 2025 term
        - Validates GPA values (<=5 for reasonable bounds)
        - Rounds result to 2 decimal places
        
    Expected Output: Single average GPA value for American Fall 2025 applicants
    """
    cur.execute("""
                SELECT 
                ROUND(AVG(CAST(gpa AS NUMERIC)),2) AS average_value
                FROM applicants
                WHERE us_or_international = 'American'
                AND
                term = 'Fall 2025'
                AND
                gpa <= 5;
                """)
    print("What is their average GPA of American students in Fall 2025?\n", cur.fetchall(),"\n\n")

    # Query 5: Fall 2025 acceptance percentage
    """
    Calculate overall acceptance rate for Fall 2025 applications.
    
    This query determines what percentage of Fall 2025 applicants received
    acceptances, providing a key admissions metric for the application cycle.
    
    SQL Logic:
        - Uses CASE WHEN with ILIKE for flexible status matching
        - Counts acceptances and divides by total Fall 2025 applications
        - Multiplies by 100 for percentage and rounds to 2 decimals
        - ILIKE '%Accepted%' catches variations in status text
        
    Expected Output: Percentage of Fall 2025 applicants who were accepted
    """
    cur.execute("""
                SELECT
                    ROUND(
                        (COUNT(CASE WHEN status ILIKE '%Accepted%' THEN 1 END) * 100.00) / COUNT(*),
                        2
                    ) AS acceptance_percentage
                FROM applicants
                WHERE term = 'Fall 2025';
                """)
    print("What percent of entries for Fall 2025 are Acceptances (to two decimal places)?\n", cur.fetchall(),"\n\n")

    # Query 6: Average GPA of accepted Fall 2025 applicants
    """
    Calculate average GPA specifically for accepted Fall 2025 applicants.
    
    This query provides insight into the academic profile of successful
    applicants for the Fall 2025 cycle, useful for prospective applicants
    to understand competitive GPA ranges.
    
    SQL Logic:
        - Filters for Fall 2025 term and accepted status
        - Uses ILIKE for flexible status matching
        - Validates GPA values (<=5 for reasonable bounds)
        - Rounds result to 2 decimal places
        
    Expected Output: Average GPA of students accepted for Fall 2025
    """
    cur.execute("""
                SELECT
                    ROUND(
                        (AVG(CAST(gpa AS NUMERIC))),
                        2
                    ) AS average_gpa
                FROM applicants
                WHERE term = 'Fall 2025'
                AND
                status ILIKE '%accepted%'
                AND gpa <= 5;
                """)
    print("What is the average GPA of applicants who applied for Fall 2025 who are Acceptances?\n", cur.fetchall(),"\n\n")
    
    # Query 7: Johns Hopkins University Masters applications
    """
    Count applications to Johns Hopkins University for Masters programs.
    
    This query provides institution-specific data for JHU Masters programs,
    useful for understanding application volume to a specific prestigious institution.
    
    SQL Logic:
        - Uses ILIKE with wildcards for flexible university name matching
        - Filters for exact degree match 'Masters'
        - LLM-generated university field used for standardized names
        
    Expected Output: Count of JHU Masters applications
    """
    cur.execute("""
                SELECT COUNT (*)
                FROM applicants
                WHERE
                llm_generated_university ILIKE '%Johns Hopkins University%'
                AND
                degree = 'Masters';                
                """)
    print("How many entries are from applicants who applied to JHU for a masters degrees?\n", cur.fetchall(),"\n\n")


    # Query 8: Georgetown PhD acceptances for 2025
    """
    Count Georgetown University PhD acceptances for 2025 application cycles.
    
    This query provides specific institutional and program data, focusing on
    successful PhD applications to Georgetown for recent application cycles.
    
    SQL Logic:
        - Uses ILIKE with wildcards for flexible matching on all text fields
        - Combines university, degree, status, and term filters
        - Flexible matching allows for variations in data entry
        
    Expected Output: Count of Georgetown PhD acceptances in 2025
    """    
    cur.execute("""
                SELECT COUNT (*)
                FROM applicants
                WHERE
                llm_generated_university ILIKE '%Georgetown%'
                AND
                degree = 'PhD'
                AND
                status ILIKE '%accept%'
                AND
                term ILIKE '%2025%';                
                """)
    print("How many entries from 2025 are acceptances from applicants who applied to Georgetown University for a PhD?\n", cur.fetchall(), "\n\n")

    # Query 9: University acceptance rates by applicant type (International vs. Domestic)
    """
    Compare acceptance rates between international and domestic applicants by university.
    
    This complex analytical query uses Common Table Expressions (CTE) to calculate
    and compare acceptance rates across applicant types, providing insights into
    potential admission bias or preferences at different institutions.
    
    SQL Logic:
        - CTE calculates acceptance rates by university and applicant type
        - Filters for universities with sufficient data (>=5 applications)
        - Main query pivots data to compare US vs International rates
        - Calculates rate difference (International - US)
        - Orders by rate difference to show universities favoring international students
        
    Data Quality Filters:
        - Excludes records with NULL university, applicant type, or status
        - Requires minimum 5 applications per university/type combination
        - Only includes universities with both US and International applicants
        
    Expected Output: Universities with US rate, International rate, and difference
    """
    cur.execute("""
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
                    MAX(CASE WHEN us_or_international = 'US' THEN acceptance_rate END) as us_acceptance_rate,
                    MAX(CASE WHEN us_or_international = 'International' THEN acceptance_rate END) as intl_acceptance_rate,
                    (MAX(CASE WHEN us_or_international = 'International' THEN acceptance_rate END) - 
                    MAX(CASE WHEN us_or_international = 'US' THEN acceptance_rate END)) as rate_difference
                FROM acceptance_by_status
                GROUP BY llm_generated_university
                HAVING COUNT(DISTINCT us_or_international) = 2
                ORDER BY rate_difference DESC;
                """)
    print("Which universities have the highest acceptance rates for interational students? How about domestic?\n", cur.fetchall(), "\n\n")
    
    # Query 10: GPA comparison by admission status and degree type
    """
    Analyze average GPA differences between accepted and rejected applicants by degree type.
    
    This query provides crucial insights into academic competitiveness across
    different degree programs, helping prospective applicants understand
    GPA expectations for their target degree type.
    
    SQL Logic:
        - Groups applicants by degree type and admission outcome
        - Uses CASE statement to categorize status into Accepted/Rejected/Other
        - Calculates average GPA and count for each group
        - Filters for valid GPA values and complete records
        - Orders by degree and admission status for easy comparison
        
    Data Validation:
        - Excludes NULL GPA, status, and degree values
        - Filters GPA <= 5 for reasonable bounds
        - Includes count for statistical significance assessment
        
    Expected Output: Degree type, admission status, count, and average GPA
    """
    cur.execute("""
                SELECT 
                degree,
                CASE 
                    WHEN status ILIKE '%accepted%' THEN 'Accepted'
                    WHEN status ILIKE '%rejected%' THEN 'Rejected'
                    ELSE 'Other'
                END as admission_status,
                COUNT(*) as count,
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
                """)
    print("What is the average GPA of accepted students vs. rejected students by degree?\n", cur.fetchall(),"\n\n")