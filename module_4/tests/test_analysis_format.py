import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest
import re

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

@pytest.mark.analysis
def test_answer_labels_present(client, mocker):
    """Test that your page includes 'Answer' labels for rendered analysis."""
    # Use default mock data
    mock_data = {'fall_2025_count': 150, 'international_pct': 25.5}
    mocker.patch('src.webpage.app.execute_query', side_effect=create_mock_query(mock_data))
    
    response = client.get('/')
    assert response.status_code == 200
    
    page_content = response.data.decode('utf-8')
    assert 'Answer:' in page_content, "Page should contain 'Answer:' labels for analysis results"
    
    answer_count = page_content.count('Answer:')
    assert answer_count >= 3, f"Should have at least 3 'Answer:' labels, found {answer_count}"

@pytest.mark.analysis
@pytest.mark.parametrize("test_data,expected_format", [
    ({'international_pct': 25.5}, "25.50%"),      # Single decimal should become 25.50%
    ({'international_pct': 30.0}, "30.00%"),      # Whole number should become 30.00%
    ({'acceptance_pct': 15.789}, "15.79%"),       # Should round to 15.79%
    ({'international_pct': 33.33}, "33.33%"),     # Already 2 decimals
])
def test_percentage_formatting_scenarios(client, mocker, test_data, expected_format):
    """Test percentage formatting with various input scenarios."""
    mocker.patch('src.webpage.app.execute_query', side_effect=create_mock_query(test_data))
    
    response = client.get('/')
    assert response.status_code == 200
    
    page_content = response.data.decode('utf-8')
    assert expected_format in page_content, f"Should contain {expected_format} in rendered page"

@pytest.mark.analysis
@pytest.mark.parametrize("invalid_pattern,description", [
    (r'(\d+\.\d)%', "single decimal percentages"),
    (r'(\d+\.\d{3,})%', "more than 2 decimal percentages"),
    (r'(\d+\.\d{1})%', "exactly 1 decimal percentages"),
])
def test_no_invalid_percentage_formats(client, mocker, invalid_pattern, description):
    """Test that invalid percentage formats are not present."""
    # Use data that might cause formatting issues
    mock_data = {
        'international_pct': 25.5,
        'acceptance_pct': 15.789,
        'avg_gpa': 3.6543
    }
    mocker.patch('src.webpage.app.execute_query', side_effect=create_mock_query(mock_data))
    
    response = client.get('/')
    assert response.status_code == 200
    
    page_content = response.data.decode('utf-8')
    
    invalid_matches = re.findall(invalid_pattern, page_content)
    assert len(invalid_matches) == 0, f"Found {description}: {invalid_matches}"

@pytest.mark.analysis
@pytest.mark.parametrize("mock_averages,expected_count", [
    ([('GPA', 3.75), ('GRE', 320.5)], 2),
    ([('GPA', 3.789), ('GRE', 320.1), ('GRE Verbal', 155.67)], 3),
    ([('GPA', 3.0), ('GRE', 320.0), ('GRE Verbal', 155.0), ('GRE AW', 4.0)], 4),
])
def test_answer_labels_count_varies_with_data(client, mocker, mock_averages, expected_count):
    """Test that Answer: label count adjusts based on available data."""
    mock_data = {'averages': mock_averages}
    mocker.patch('src.webpage.app.execute_query', side_effect=create_mock_query(mock_data))
    
    response = client.get('/')
    assert response.status_code == 200
    
    page_content = response.data.decode('utf-8')
    
    # Count Answer: labels in the averages section
    answer_count = page_content.count('Answer:')
    assert answer_count >= expected_count, f"Should have at least {expected_count} Answer: labels for averages data"