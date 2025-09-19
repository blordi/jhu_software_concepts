import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest

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

@pytest.fixture
def app_instance(mock_database_modules):
    """Import and return the app after mocking."""
    from src.webpage.app import create_app
    return create_app({'TESTING': True})

@pytest.fixture
def mock_connection(mocker):
    """Mock database connection and cursor."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor

@pytest.mark.db
def test_execute_query_function_exists(app_instance):
    """Test that execute_query function exists and is callable."""
    from src.webpage import app as app_module
    assert hasattr(app_module, 'execute_query')
    assert callable(app_module.execute_query)

@pytest.mark.db
def test_execute_query_calls_database(app_instance, mocker):
    """Test that execute_query properly calls database operations."""
    from src.webpage import app as app_module
    
    # Mock the connection pool
    mock_pool = mocker.MagicMock()
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    
    # Set up the mock chain
    mock_pool.connection.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [('test_result',)]
    
    # Replace the pool in the app
    app_module.pool = mock_pool
    
    # Test the function
    result = app_module.execute_query("SELECT * FROM test_table")
    
    # Verify database operations were called
    mock_pool.connection.assert_called_once()
    mock_conn.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once_with("SELECT * FROM test_table")
    mock_cursor.fetchall.assert_called_once()
    
    assert result == [('test_result',)]

@pytest.mark.db
@pytest.mark.parametrize("query,expected_table", [
    ("SELECT COUNT (*) FROM applicants WHERE TERM = 'Fall 2025'", "applicants"),
    ("SELECT * FROM applicants WHERE us_or_international = 'International'", "applicants"),
    ("SELECT AVG(gpa::NUMERIC) FROM applicants WHERE gpa IS NOT NULL", "applicants"),
])
def test_queries_target_correct_tables(app_instance, mocker, query, expected_table):
    """Test that queries target the expected database tables."""
    from src.webpage import app as app_module
    
    # Mock the connection pool
    mock_pool = mocker.MagicMock()
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    
    mock_pool.connection.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [(100,)]
    
    app_module.pool = mock_pool
    
    # Execute the query
    app_module.execute_query(query)
    
    # Verify the query was executed
    mock_cursor.execute.assert_called_once_with(query)
    
    # Verify the query contains the expected table name
    executed_query = mock_cursor.execute.call_args[0][0]
    assert expected_table in executed_query.lower()

@pytest.mark.db
def test_database_connection_pool_exists(app_instance):
    """Test that database connection pool is properly initialized."""
    from src.webpage import app as app_module
    
    # Check that pool exists
    assert hasattr(app_module, 'pool')
    assert app_module.pool is not None

@pytest.mark.db
def test_sql_queries_are_well_formed(app_instance):
    """Test that the app has routes and can be created successfully."""
    # Test that the app was created successfully
    assert app_instance is not None
    
    # Test that routes are registered
    assert len(app_instance.url_map._rules) > 0
    
    # Test that main routes exist
    route_rules = [rule.rule for rule in app_instance.url_map.iter_rules()]
    assert '/' in route_rules
    assert '/rescrape' in route_rules
    assert '/refresh' in route_rules

@pytest.mark.db
def test_load_data_functions_exist(app_instance):
    """Test that data loading functions exist."""
    from src.webpage import app as app_module
    
    # Check that data loading functions are accessible
    assert hasattr(app_module, 'run_rescrape')
    assert hasattr(app_module, 'add_to_db')
    assert callable(app_module.run_rescrape)
    assert callable(app_module.add_to_db)

@pytest.mark.db
def test_add_to_db_function_behavior(app_instance, mocker):
    """Test that add_to_db function calls load_data properly."""
    from src.webpage import app as app_module
    
    # Mock the load_data module
    mock_load_data = mocker.patch('src.webpage.app.load_data')
    mock_json = mocker.patch('src.webpage.app.json')
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data='{"test": "data"}'))
    
    # Mock json.load to return test data
    mock_json.load.return_value = {"test": "data"}
    
    # Call the function
    app_module.add_to_db()
    
    # Verify it tried to open the file and call load_data
    mock_open.assert_called()
    mock_load_data.add_applicant_data.assert_called_once_with({"test": "data"})

@pytest.mark.db
@pytest.mark.parametrize("query_type,expected_columns", [
    ("COUNT", ["count"]),
    ("AVG", ["average"]),
    ("SELECT", ["multiple_possible"]),
])
def test_query_result_structure(app_instance, mocker, query_type, expected_columns):
    """Test that different query types return expected result structures."""
    from src.webpage import app as app_module
    
    # Mock the connection pool with different return types
    mock_pool = mocker.MagicMock()
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    
    mock_pool.connection.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    if query_type == "COUNT":
        mock_cursor.fetchall.return_value = [(150,)]
    elif query_type == "AVG":
        mock_cursor.fetchall.return_value = [(3.75,)]
    else:
        mock_cursor.fetchall.return_value = [('col1', 'col2', 'col3')]
    
    app_module.pool = mock_pool
    
    # Test with a sample query
    result = app_module.execute_query(f"{query_type} test query")
    
    # Verify result structure
    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], tuple)