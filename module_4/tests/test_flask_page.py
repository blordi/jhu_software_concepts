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