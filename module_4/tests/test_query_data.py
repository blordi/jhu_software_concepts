import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest
import importlib

@pytest.mark.db
def test_query_data_module_imports_and_runs(mocker):
    """Test that query_data module can be imported and executes all queries."""
    # Mock psycopg_pool before importing
    mock_pool = mocker.MagicMock()
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    
    # Set up the mock chain
    mock_pool.getconn.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.cursor.return_value.__exit__.return_value = None
    
    # Mock fetchall to return sample data for each query
    mock_cursor.fetchall.side_effect = [
        [(150,)],  # Fall 2025 count
        [(25.5,)], # International percentage
        [('GPA', 100, 3.75), ('GRE', 80, 320.5)], # Averages
        [(3.65,)], # American GPA
        [(15.75,)], # Acceptance percentage
        [(3.80,)], # Accepted GPA
        [(45,)],   # JHU count
        [(12,)],   # Georgetown count
        [('University A', 80.0, 75.5, -4.5)], # University rates
        [('Masters', 'Accepted', 50, 3.8)] # GPA by status
    ]
    
    mocker.patch('psycopg_pool.ConnectionPool', return_value=mock_pool)
    mocker.patch('builtins.print')  # Mock print to avoid output during tests
    
    # Remove the module from sys.modules if it exists, then import fresh
    if 'src.query_data' in sys.modules:
        del sys.modules['src.query_data']
    
    # Now import the module - this should execute all the queries
    import src.query_data
    
    # Verify the connection was established
    assert hasattr(src.query_data, 'pool')
    assert hasattr(src.query_data, 'conn')
    
    # Verify all queries were executed (10 execute calls)
    assert mock_cursor.execute.call_count == 10
    
    # Verify all results were fetched (10 fetchall calls)  
    assert mock_cursor.fetchall.call_count == 10

@pytest.mark.db
def test_query_data_sql_queries_content(mocker):
    """Test that the SQL queries contain expected content."""
    # Set up the same mocks
    mock_pool = mocker.MagicMock()
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    
    mock_pool.getconn.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.cursor.return_value.__exit__.return_value = None
    
    mock_cursor.fetchall.return_value = [(1,)]  # Simple return for all queries
    
    mocker.patch('psycopg_pool.ConnectionPool', return_value=mock_pool)
    mocker.patch('builtins.print')
    
    # Remove and re-import to ensure fresh execution
    if 'src.query_data' in sys.modules:
        del sys.modules['src.query_data']
    
    # Import the module
    import src.query_data
    
    # Get all the executed queries
    executed_queries = [call[0][0] for call in mock_cursor.execute.call_args_list]
    
    # Verify we have queries
    assert len(executed_queries) >= 5  # At least some queries
    
    # Verify key content in queries (case insensitive)
    query_text = ' '.join(executed_queries).upper()
    assert "FALL 2025" in query_text or "Fall 2025" in ' '.join(executed_queries)
    assert "INTERNATIONAL" in query_text or "international" in ' '.join(executed_queries)

@pytest.mark.db 
def test_query_data_database_connection_handling(mocker):
    """Test that database connections are properly managed."""
    mock_pool = mocker.MagicMock()
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    
    mock_pool.getconn.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.cursor.return_value.__exit__.return_value = None
    mock_cursor.fetchall.return_value = [(1,)]
    
    mocker.patch('psycopg_pool.ConnectionPool', return_value=mock_pool)
    mocker.patch('builtins.print')
    
    # Remove and re-import
    if 'src.query_data' in sys.modules:
        del sys.modules['src.query_data']
    
    # Import the module
    import src.query_data
    
    # Verify connection was obtained from pool
    mock_pool.getconn.assert_called_once()
    
    # Verify cursor context manager was used
    mock_conn.cursor.assert_called_once()