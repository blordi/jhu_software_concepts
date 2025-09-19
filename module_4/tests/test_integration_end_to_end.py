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
def client(app_instance):
    """Create a test client for the Flask application."""
    app_instance.config['TESTING'] = True
    return app_instance.test_client()

def create_mock_query(mock_data):
    """Factory function to create mock query function with specific data."""
    def mock_query(query):
        if "COUNT (*)" in query and "Fall 2025" in query:
            return [(mock_data.get('fall_2025_count', 150),)]
        elif "international_percentage" in query:
            return [(mock_data.get('international_pct', 25.5),)]
        elif "acceptance_percentage" in query:
            return [(mock_data.get('acceptance_pct', 15.75),)]
        elif "average_gpa_american_fall_25" in query:
            return [(mock_data.get('avg_gpa', 3.65),)]
        elif "averages" in query or "UNION ALL" in query:
            return mock_data.get('averages', [('GPA', 3.75), ('GRE', 320.5)])
        elif "Johns Hopkins University" in query:
            return [(mock_data.get('jhu_count', 45),)]
        elif "Georgetown" in query:
            return [(mock_data.get('georgetown_count', 12),)]
        else:
            return [(100,)]
    return mock_query

@pytest.mark.integration
def test_end_to_end(client, mocker):
    mock_run_rescrape = mocker.patch('src.webpage.app.run_rescrape')
    mock_add_to_db = mocker.patch('src.webpage.app.add_to_db')

    before_data = {
    'fall_2025_count': 150,
    'international_pct': 25.5
    }
    after_data = {
    'fall_2025_count': 999,  # Obviously different!
    'international_pct': 42.7  # Obviously different!
    }

    mocker.patch('src.webpage.app.execute_query', side_effect=create_mock_query(before_data))
    response = client.get('/')
    page_content = response.data.decode('utf-8')
    assert '150' in page_content
   
    response = client.post('/rescrape')
    mock_run_rescrape.assert_called_once()
    mock_add_to_db.assert_called_once()
    assert response.status_code == 200
    mocker.patch('src.webpage.app.execute_query', side_effect=create_mock_query(after_data))
    
    response = client.post('/refresh')

    response = client.get('/')
    page_content = response.data.decode('utf-8')
    assert '999' in page_content
    assert '42.70%' in page_content

@pytest.mark.integration
def test_multiple_pulls_uniqueness(client, mocker):
    mock_run_rescrape = mocker.patch('src.webpage.app.run_rescrape')
    mock_add_to_db = mocker.patch('src.webpage.app.add_to_db')

    before_data = {
    'fall_2025_count': 150,
    'international_pct': 25.5
    }
    after_data = {
    'fall_2025_count': 999,  
    'international_pct': 42.7  
    }

    mocker.patch('src.webpage.app.execute_query', side_effect=create_mock_query(before_data))
    response = client.get('/')
    page_content = response.data.decode('utf-8')
    assert '150' in page_content
   
    response = client.post('/rescrape')
    assert mock_run_rescrape.call_count == 1
    assert mock_add_to_db.call_count == 1
    assert response.status_code == 200

    mocker.patch('src.webpage.app.execute_query', side_effect=create_mock_query(after_data))
    
    response = client.post('/rescrape')
    assert mock_run_rescrape.call_count == 2  
    assert mock_add_to_db.call_count == 2     
    assert response.status_code == 200
    
    mocker.patch('src.webpage.app.execute_query', side_effect=create_mock_query(after_data))

    response = client.post('/refresh')
    response = client.get('/')
    page_content = response.data.decode('utf-8')
    
    assert '999' in page_content
    assert '42.70%' in page_content