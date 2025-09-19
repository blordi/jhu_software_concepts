Overview & Setup
================

How to Run the App
------------------

1. Install dependencies::

    pip install -r requirements.txt

2. Set up PostgreSQL database and configure connection

3. Set environment variables (optional)::

    # Windows Command Prompt
    set DATABASE_URL=postgresql://postgresd@localhost:5432/module_3_db
    
    # Windows PowerShell
    $env:DATABASE_URL="postgresql://postgres@localhost:5432/module_3_db"

4. Run the Flask application::

    python src/webpage/app.py

Required Environment Variables
------------------------------

* ``DATABASE_URL``: PostgreSQL connection string (optional)
  
  - Default: ``postgresql://postgres@localhost:5432/module_3_db``
  - Format: ``postgresql://username:password@host:port/database``
  - Used by all modules for database connectivity

Application Factory
~~~~~~~~~~~~~~~~~~~

The application uses Flask's factory pattern for better testability::

    from src.webpage.app import create_app
    
    # Create app with default config
    app = create_app()
    
    # Create app with custom config
    app = create_app({'DATABASE_URL': 'custom_db_url', 'TESTING': True})