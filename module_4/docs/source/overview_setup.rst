Overview & Setup
================

How to Run the App
------------------

1. Install dependencies::

    pip install -r requirements.txt

2. Set up PostgreSQL database with connection string
3. Run the Flask application::

    python src/webpage/app.py

Required Environment Variables
------------------------------

None

How to Run Tests
----------------

Run all tests::

    pytest
    
    or

    pytest -m "web or buttons or analysis or db or integration"

Run specific test markers::

    pytest -m web
    pytest -m buttons
    pytest -m integration