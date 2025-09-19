import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest
import json

@pytest.fixture(autouse=True)
def mock_database_modules(mocker):
    """Mock database modules before importing load_data."""
    mock_pool = mocker.MagicMock()
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    
    # Set up the mock chain
    mock_pool.getconn.return_value.__enter__.return_value = mock_conn
    mock_pool.getconn.return_value.__exit__.return_value = None
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.cursor.return_value.__exit__.return_value = None
    
    mocker.patch('psycopg_pool.ConnectionPool', return_value=mock_pool)
    
    return mock_pool, mock_conn, mock_cursor

@pytest.mark.db
def test_load_data_valid_json(mocker):
    """Test load_data with valid JSON file."""
    from src import load_data
    
    test_data = {"rows": [{"name": "test", "value": 123}]}
    mock_open = mocker.mock_open(read_data=json.dumps(test_data))
    mocker.patch('builtins.open', mock_open)
    
    result = load_data.load_data('test.json')
    
    assert result == test_data
    mock_open.assert_called_once_with('test.json', 'r', encoding='utf-8')

@pytest.mark.db
def test_load_data_jsonl_format(mocker):
    """Test load_data with JSONL format (one JSON per line)."""
    from src import load_data
    
    jsonl_content = '{"name": "test1", "value": 1}\n{"name": "test2", "value": 2}\n'
    
    # First call raises JSONDecodeError, second call succeeds
    mock_open = mocker.mock_open(read_data=jsonl_content)
    mocker.patch('builtins.open', mock_open)
    mocker.patch('json.load', side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
    
    result = load_data.load_data('test.jsonl')
    
    expected = {"rows": [{"name": "test1", "value": 1}, {"name": "test2", "value": 2}]}
    assert result == expected

@pytest.mark.db
def test_load_data_unicode_decode_error(mocker):
    """Test load_data handles UnicodeDecodeError."""
    from src import load_data
    
    test_data = {"rows": [{"name": "test"}]}
    
    # First call raises UnicodeDecodeError, second succeeds
    mock_open_calls = [
        mocker.mock_open().return_value,  # First call fails
        mocker.mock_open(read_data=json.dumps(test_data)).return_value  # Second succeeds
    ]
    
    mocker.patch('builtins.open', side_effect=[
        UnicodeDecodeError("utf-8", b"", 0, 1, "invalid"),
        mock_open_calls[1]
    ])
    
    result = load_data.load_data('test.json')
    assert result == test_data

@pytest.mark.db
def test_create_applicant_table(mock_database_modules):
    """Test create_applicant_table function."""
    from src import load_data
    
    mock_pool, mock_conn, mock_cursor = mock_database_modules
    
    load_data.create_applicant_table()
    
    # Verify connection and cursor usage
    mock_pool.getconn.assert_called_once()
    mock_conn.cursor.assert_called_once()
    
    # Verify SQL commands were executed
    assert mock_cursor.execute.call_count == 2
    
    # Check that DROP and CREATE commands were called
    executed_sql = [call[0][0] for call in mock_cursor.execute.call_args_list]
    assert any("DROP TABLE IF EXISTS applicants" in sql for sql in executed_sql)
    assert any("CREATE TABLE IF NOT EXISTS applicants" in sql for sql in executed_sql)
    
    # Verify commit was called
    mock_conn.commit.assert_called_once()
    
    # Verify pool was closed
    mock_pool.close.assert_called_once()

@pytest.mark.db
def test_add_applicant_data(mock_database_modules):
    """Test add_applicant_data function."""
    from src import load_data
    
    mock_pool, mock_conn, mock_cursor = mock_database_modules
    
    test_data = {
        "rows": [
            {
                'program': 'CS', 'comments': 'Good', 'date_added': '2024-01-01',
                'url': 'http://test.com', 'status': 'Accepted', 'Term': 'Fall 2025',
                'US/International': 'US', 'gpa': 3.8, 'gre': 320, 'gre_v': 160,
                'gre_aw': 4.5, 'Degree': 'Masters', 'llm-generated-program': 'Computer Science',
                'llm-generated-university': 'Test University'
            }
        ]
    }
    
    load_data.add_applicant_data(test_data)
    
    # Verify database operations
    mock_pool.getconn.assert_called_once()
    mock_conn.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_pool.close.assert_called_once()
    
    # Verify INSERT SQL was executed
    executed_sql = mock_cursor.execute.call_args[0][0]
    assert "INSERT INTO applicants" in executed_sql

@pytest.mark.db
def test_add_applicant_data_master_copy(mock_database_modules):
    """Test add_applicant_data_master_copy function."""
    from src import load_data
    
    mock_pool, mock_conn, mock_cursor = mock_database_modules
    
    test_data = {
        "rows": [
            {
                'program': 'CS', 'comments': 'Good', 'date_added': '2024-01-01',
                'url': 'http://test.com', 'status': 'Accepted', 'semester': 'Fall 2025',
                'applicant_type': 'US', 'gpa': 3.8, 'gre_total': 320, 'gre_verbal': 160,
                'gre_aw': 4.5, 'degree': 'Masters', 'llm-generated-program': 'Computer Science',
                'llm-generated-university': 'Test University'
            }
        ]
    }
    
    load_data.add_applicant_data_master_copy(test_data)
    
    # Verify database operations
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_pool.close.assert_called_once()

@pytest.mark.db
def test_drop_table(mock_database_modules):
    """Test drop_table function."""
    from src import load_data
    
    mock_pool, mock_conn, mock_cursor = mock_database_modules
    
    load_data.drop_table()
    
    # Verify database operations
    mock_pool.getconn.assert_called_once()
    mock_conn.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once_with("DROP TABLE IF EXISTS applicants;")
    mock_conn.commit.assert_called_once()
    mock_pool.close.assert_called_once()

@pytest.mark.db
def test_main_block_exists():
    """Test that main block exists and contains expected code."""
    from src import load_data
    import inspect
    
    source = inspect.getsource(load_data)
    assert 'if __name__ == "__main__":' in source
    assert 'load_data(' in source

@pytest.mark.db
def test_load_data_jsonl_with_invalid_lines(mocker):
    """Test load_data JSONL format with some invalid JSON lines."""
    from src import load_data
    
    # JSONL with one valid line and one invalid line
    jsonl_content = '{"name": "test1", "value": 1}\ninvalid json line\n{"name": "test2", "value": 2}\n'
    
    mock_open = mocker.mock_open(read_data=jsonl_content)
    mocker.patch('builtins.open', mock_open)
    mocker.patch('json.load', side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
    
    result = load_data.load_data('test.jsonl')
    
    # Should skip the invalid line and continue
    expected = {"rows": [{"name": "test1", "value": 1}, {"name": "test2", "value": 2}]}
    assert result == expected
