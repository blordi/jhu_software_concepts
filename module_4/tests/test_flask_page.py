import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest

@pytest.fixture(autouse=True)
def mock_database_modules(mocker):
    """Automatically mock database modules for all tests."""
    mocker.patch.dict('sys.modules', {
        'psycopg_pool': mocker.MagicMock(),
        'psycopg': mocker.MagicMock(),
        'clean': mocker.MagicMock(),
        'scrape': mocker.MagicMock(),
        'load_data': mocker.MagicMock()
    })

@pytest.fixture
def app_instance(mock_database_modules):
    """Import and return the app after mocking."""
    from src.webpage.app import app
    return app

@pytest.fixture
def client(app_instance):
    """Create a test client for the Flask application."""
    app_instance.config['TESTING'] = True
    return app_instance.test_client()

@pytest.mark.web
def test_app_factory_config(app_instance):
    """Test app factory / Config: Assert a testable Flask app is created with required routes."""
    from flask import Flask
    
    # Test that app is a Flask instance
    assert isinstance(app_instance, Flask)
    
    # Test that required routes exist
    with app_instance.app_context():
        routes = [rule.rule for rule in app_instance.url_map.iter_rules()]
        
        # Check for your actual routes
        assert '/' in routes  # dashboard route
        assert '/rescrape' in routes  # pull data route
        assert '/refresh' in routes  # update analysis route 


@pytest.mark.web
def test_get_analysis_page_load(client, mocker):
    """Test GET /analysis (page load) - Status 200, contains buttons, contains analysis content"""
    # Mock the execute_query function to return realistic test data
    def mock_execute_query(query):
        if "COUNT (*)" in query and "Fall 2025" in query:
            return [(150,)]
        elif "international_percentage" in query:
            return [(25.50,)]
        elif "averages" in query or "UNION ALL" in query:
            return [('GPA', 3.75), ('GRE', 320.50), ('GRE Verbal', 155.20), ('GRE Analytical Writing', 4.10)]
        elif "average_gpa_american_fall_25" in query:
            return [(3.65,)]
        elif "acceptance_percentage" in query:
            return [(15.75,)]
        elif "Johns Hopkins University" in query:
            return [(45,)]
        elif "Georgetown" in query:
            return [(12,)]
        elif "acceptance_by_status" in query:
            return [('University A', 80.00, 75.50, 4.50)]
        elif "gpa_accepted_vs_rejected_degree" in query:
            return [('Masters', 'Accepted', 3.80)]
        else:
            return [(100,)]
    
    mocker.patch('src.webpage.app.execute_query', side_effect=mock_execute_query)
    
    # Make the GET request
    response = client.get('/')
    
    # i. Status 200
    assert response.status_code == 200
    
    page_content = response.data.decode('utf-8')
    
    # ii. Page Contains both "Pull Data" and "Update Analysis" buttons
    assert 'Pull Data' in page_content, "Page should contain 'Pull Data' button"
    assert 'Update Analysis' in page_content, "Page should contain 'Update Analysis' button"
    
    # iii. Page text includes "Analysis" and at least one "Answer:"
    assert 'Graduate Admissions Analytics Dashboard' in page_content, "Page should contain dashboard title"
    assert 'Answer:' in page_content, "Page should contain at least one 'Answer:' label"
    
    # Verify mock data appears with Answer: labels (flexible for now)
    assert 'Answer: 150' in page_content, "Should show Fall 2025 count with Answer: label"
    
    # Use flexible matching until we see what's rendered
    assert ('Answer: 25.50' in page_content), "Should show international percentage with Answer: label"

@pytest.mark.web
def test_dashboard_error_handling(client, mocker):
    """Test dashboard route handles database errors gracefully."""
    # Mock execute_query to raise an exception
    mocker.patch('src.webpage.app.execute_query', side_effect=Exception("Database connection failed"))
    
    response = client.get('/')
    assert response.status_code == 200
    assert b"Error executing queries: Database connection failed" in response.data

