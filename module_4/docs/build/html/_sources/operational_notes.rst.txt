Operational Notes
=================

Busy-State Policy
-----------------

The application prevents concurrent operations using thread-safe busy-state management.

**Implementation:**
- Global ``is_scraping`` flag with ``threading.Lock()``
- Returns HTTP 409 ``{"busy": True}`` when operations conflict
- Automatic cleanup in ``finally`` blocks prevents permanent locks

**Behavior:**
- Only one scraping operation allowed at a time
- Dashboard refresh blocked during scraping for data consistency
- Client should handle 409 responses and retry appropriately

Duplicate Strategy
--------------------

**Duplicate Prevention:**
- Queries existing result IDs before scraping new pages
- Extracts IDs from GradCafe URLs (``/result/{id}`` pattern)
- Uses set comparison: ``new_ids = page_ids - existing_ids``
- Stops after 5 consecutive pages with no new data

**Data Processing:**
- New runs overwrite previous temporary files
- Database transactions ensure atomic operations
- LLM reprocesses all data for consistency

Uniqueness Keys
---------------

**Database Schema:**
- Primary key: ``p_id`` (auto-incrementing)
- Natural uniqueness: URL field contains unique GradCafe result URLs

**Data Integrity:**
- URL validation ensures GradCafe pattern compliance
- Field validation: GPA (0-5), GRE (130-170) ranges
- LLM processing standardizes university/program names

Troubleshooting
---------------

Common Local Issues
~~~~~~~~~~~~~~~~~~~

**Database Connection Errors:**
.. code-block:: bash

    # Check PostgreSQL service
    net start postgresql-x64-16
    
    # Test connection
    psql -U postgres -h localhost -d module_3_db

**Module Import Errors:**
.. code-block:: bash

    # Install dependencies
    pip install -r requirements.txt
    pip install psycopg[binary]
    
    # Activate virtual environment
    .venv\Scripts\activate

**Web Scraping Issues:**
- Check network connectivity to thegradcafe.com
- Add delays between requests if rate-limited
- Debug HTML parsing if structure changes

**Flask Application Issues:**
- Verify templates in correct folder
- Check port 8080 availability: ``netstat -an | findstr :8080``
- Enable debug mode: ``app.run(debug=True)``

Common CI Issues
~~~~~~~~~~~~~~~~

**GitHub Actions Failures:**
.. code-block:: yaml

    # Set environment variables
    env:
      DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
    
    # Add PostgreSQL service
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres

**Coverage Issues:**
.. code-block:: bash

    # Ensure all test files committed
    git add tests/
    
    # Use absolute paths
    pytest --cov=./src --cov-report=term-missing

**Deployment Issues:**
- Use environment variables for production config
- Ensure static files properly served
- Run database setup: ``create_applicant_table()``

**Performance Tips:**
- Monitor connection pool usage
- Consider pagination for large datasets
- Implement exponential backoff for retries
- Add health check endpoint: ``GET /health``