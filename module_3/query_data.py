import psycopg_pool

pool = psycopg_pool.ConnectionPool(
        "postgresql://postgres:Uphold-Removable-Radiator@localhost:5432/module_3_db"
    )

conn = pool.getconn()
with conn.cursor() as cur:

    cur.execute("""
        SELECT COUNT (*) 
                FROM applicants
                WHERE TERM = 'Fall 2025';""")
    print("How many entries do you have in your database who have applied for Fall 2025?\n", cur.fetchall(),"\n\n")

    cur.execute("""
            SELECT
                ROUND(
                    (SELECT COUNT(*) FROM applicants WHERE us_or_international = 'International') *100.0 /
                    (SELECT COUNT(*) FROM applicants), 
                    2
            ) AS international_percentage;
                """)
    print("What percentage of entries are from international students (not American or Other)\n", cur.fetchall(),"\n\n")

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

    cur.execute("""
                SELECT COUNT (*)
                FROM applicants
                WHERE
                llm_generated_university ILIKE '%Johns Hopkins University%'
                AND
                degree = 'Masters';                
                """)
    print("How many entries are from applicants who applied to JHU for a masters degrees in Computer Science?\n", cur.fetchall(),"\n\n")

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
    print("How many entries from 2025 are acceptances from applicants who applied to Georgetown University for a PhD in Computer Science?\n", cur.fetchall(), "\n\n")

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