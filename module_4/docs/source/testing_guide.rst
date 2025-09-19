Testing Guide
=============

This guide covers how to run tests, understand test markers, and work with the test fixtures and doubles provided in the test suite.

Overview
--------

The test suite provides comprehensive coverage of all application components with 95% code coverage. Tests are organized by functionality and use pytest markers for selective execution.

Test Structure
--------------

The test suite is organized into the following files:

* ``tests/test_flask_page.py`` - Flask route and page rendering tests
* ``tests/test_buttons.py`` - Button functionality and busy-state tests  
* ``tests/test_analysis_format.py`` - Data formatting and display tests
* ``tests/test_db.py`` - Database operation tests
* ``tests/test_integration.py`` - End-to-end workflow tests
* ``tests/test_load_data.py`` - Data loading function tests
* ``tests/test_query_data.py`` - Query module tests

Running Tests
-------------

Basic Test Execution
~~~~~~~~~~~~~~~~~~~~

Run all tests::

    pytest
    
    or

    pytest -m "web or buttons or analysis or db or integration"

Run with verbose output::

    pytest -vv


Run specific test file::

    pytest tests/test_flask_page.py -v

Run specific test function::

    pytest tests/test_flask_page.py::test_app_factory_config -v

Marked Test Execution
~~~~~~~~~~~~~~~~~~~~~

The test suite uses pytest markers to categorize tests by functionality:

Available Markers:
    * ``web`` - Flask route and page tests
    * ``buttons`` - Button behavior and POST route tests
    * ``analysis`` - Data formatting and analysis output tests
    * ``db`` - Database schema, inserts, and selects
    * ``integration`` - End-to-end workflow tests

Run tests by marker::

    # Run only web-related tests
    pytest -m web -v
    
    # Run only button-related tests
    pytest -m button -v

    # Run only database tests
    pytest -m db -v

    # Run integration tests only
    pytest -m integration -v

    # Run multiple markers
    pytest -m "web or buttons" -v

Expected Test Selectors
-----------------------

The application provides stable test selectors for UI testing:


Test Fixtures and Doubles
--------------------------

Mock Database Modules
~~~~~~~~~~~~~~~~~~~~~

All test files use automatic database module mocking:

.. code-block:: python

    @pytest.fixture(autouse=True)
    def mock_database_modules(mocker):
        """Automatically mock database modules for all tests."""
        mock_psycopg_pool = mocker.MagicMock()
        mock_psycopg_pool.ConnectionPool = mocker.MagicMock()
        
        mocker.patch.dict('sys.modules', {
            'psycopg_pool': mock_psycopg_pool,
            'psycopg': mocker.MagicMock(),
            'clean': mocker.MagicMock(),
            'scrape': mocker.MagicMock(),
            'load_data': mocker.MagicMock()
        })

Flask Application Fixtures
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**app_instance fixture:**
    Provides access to the Flask application after database mocking:
    
    .. code-block:: python
    
        @pytest.fixture
        def app_instance(mock_database_modules):
            """Import and return the app after mocking."""
            from src.webpage import app as app_module
            return app_module.app

**client fixture:**
    Provides a test client for making HTTP requests:
    
    .. code-block:: python
    
        @pytest.fixture
        def client(app_instance):
            """Create a test client for the Flask application."""
            app_instance.config['TESTING'] = True
            return app_instance.test_client()

Data Mocking Utilities
~~~~~~~~~~~~~~~~~~~~~~

**create_mock_query function:**
    Factory function for creating mock database query responses:
    
    .. code-block:: python
    
        def create_mock_query(mock_data):
            """Factory function to create mock query function with specific data."""
            def mock_query(query):
                if "COUNT (*)" in query and "Fall 2025" in query:
                    return [(mock_data.get('fall_2025_count', 150),)]
                elif "international_percentage" in query:
                    return [(mock_data.get('international_pct', 25.5),)]
                # ... additional query patterns
            return mock_query

    Usage example:
    
    .. code-block:: python
    
        test_data = {'fall_2025_count': 999, 'international_pct': 42.7}
        mocker.patch('src.webpage.app.execute_query', 
                    side_effect=create_mock_query(test_data))

Integration Test Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~

**End-to-end workflow testing:**
    
    .. code-block:: python
    
        def test_end_to_end_flow(client, mocker):
            # Mock scraper functions
            mock_run_rescrape = mocker.patch('src.webpage.app.run_rescrape')
            mock_add_to_db = mocker.patch('src.webpage.app.add_to_db')
            
            # Set up before/after data scenarios
            before_data = {'fall_2025_count': 150}
            after_data = {'fall_2025_count': 999}
            
            # Test complete workflow
            # 1. Initial state
            # 2. Trigger scraping
            # 3. Verify data changes
            # 4. Confirm final state

Test Data Patterns
------------------

Parametrized Testing
~~~~~~~~~~~~~~~~~~~~

The test suite uses ``@pytest.mark.parametrize`` for testing multiple scenarios:

.. code-block:: python

    @pytest.mark.parametrize("test_data,expected_format", [
        ({'international_pct': 25.5}, "25.50%"),
        ({'international_pct': 30.0}, "30.00%"),
        ({'acceptance_pct': 15.789}, "15.79%"),
    ])
    def test_percentage_formatting_scenarios(client, mocker, test_data, expected_format):
        # Test implementation

Mock Data Structures
~~~~~~~~~~~~~~~~~~~~~

Standard test data format for database responses:

.. code-block:: python

    mock_data = {
        'fall_2025_count': 150,           # Integer count
        'international_pct': 25.5,        # Percentage (will be formatted)
        'acceptance_pct': 15.75,          # Percentage (will be formatted)
        'avg_gpa': 3.65,                  # Decimal average
        'jhu_count': 45,                  # Integer count
        'averages': [                     # List of tuples
            ('GPA', 3.75),
            ('GRE', 320.5),
            ('GRE Verbal', 155.2),
            ('GRE AW', 4.1)
        ]
    }

Debugging Tests
---------------

Common Debugging Techniques
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Print debugging in tests:**

.. code-block:: python

    def test_debug_example(client, mocker):
        response = client.get('/')
        page_content = response.data.decode('utf-8')
        
        # Debug: Print actual content
        print("=== PAGE CONTENT ===")
        print(page_content[:500])  # First 500 characters
        
        # Debug: Find specific patterns
        import re
        matches = re.findall(r'Answer:[^<]*', page_content)
        print("Answer matches:", matches)

**Running tests with output:**

.. code-block:: bash

    # Show print statements
    pytest tests/test_file.py -s -v
    
    # Stop on first failure
    pytest tests/test_file.py -x
    
    # Run specific test with debugging
    pytest tests/test_file.py::test_function -s -v --tb=long


Test Configuration
------------------

pytest.ini Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

The project uses the following pytest configuration:

.. code-block:: ini

    [pytest]
    addopts = -q --cov=src --cov-report=term-missing --cov-fail-under=100
    markers =
        web: Flask route/page tests
        buttons: "Pull Data" and "Update Analysis" behavior
        analysis: formatting/rounding of analysis output
        db: database schema/inserts/selects
        integration: end-to-end flows

Dependencies
~~~~~~~~~~~~

Required testing packages::

    pytest>=7.0.0
    pytest-mock>=3.10.0
    pytest-cov>=4.0.0
    beautifulsoup4>=4.11.0

Best Practices
--------------

Test Independence
~~~~~~~~~~~~~~~~~

* Each test is completely independent
* Tests can run in any order
* No shared state between tests
* Fresh fixtures for each test

Mock Strategy
~~~~~~~~~~~~~

* Mock external dependencies (database, network)
* Use dependency injection where possible
* Test behavior, not implementation details
* Provide realistic test data

Error Testing
~~~~~~~~~~~~~

* Test both success and failure paths
* Verify error messages and status codes
* Test edge cases and boundary conditions
* Ensure graceful degradation

Performance
~~~~~~~~~~~

* Keep tests fast (seconds, not minutes)
* Use mocks to avoid slow operations
* Minimize database and network calls
* Run tests in parallel when possible

Example Test Session
--------------------

Complete test workflow example::

    # Run all tests with coverage
    pytest --cov=src --cov-report=term-missing -v

    # Run specific functionality
    pytest -m web -v

    # Debug failing test
    pytest tests/test_flask_page.py::test_get_analysis_page_load -s -v --tb=long

    # Generate HTML coverage report
    pytest --cov=src --cov-report=html

    # Run integration tests only
    pytest -m integration -v

Expected output::

    ========================= test session starts =========================
    tests/test_flask_page.py::test_app_factory_config PASSED      [ 10%]
    tests/test_flask_page.py::test_get_analysis_page_load PASSED   [ 20%]
    tests/test_buttons.py::test_post_pull_data_route PASSED        [ 30%]
    tests/test_buttons.py::test_busy_state_refresh_during_scrape PASSED [ 40%]
    tests/test_analysis_format.py::test_answer_labels_present PASSED [ 50%]
    tests/test_db.py::test_execute_query_function_exists PASSED    [ 60%]
    tests/test_integration.py::test_end_to_end_flow PASSED         [ 70%]
    tests/test_load_data.py::test_load_data_valid_json PASSED      [ 80%]
    tests/test_query_data.py::test_query_data_module_imports PASSED [ 90%]
    ========================= 95% coverage achieved =========================

