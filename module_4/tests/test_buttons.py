import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import pytest
import threading

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
    from src.webpage import app as app_module
    return app_module.app

@pytest.fixture
def client(app_instance):
    """Create a test client for the Flask application."""
    app_instance.config['TESTING'] = True
    return app_instance.test_client()

@pytest.mark.buttons
def test_post_pull_data_route(client, mocker):
    """Test POST /rescrape (pull data button) - Returns redirect and triggers scraper"""
    # Mock the scraper functions
    mock_run_rescrape = mocker.patch('src.webpage.app.run_rescrape')
    mock_add_to_db = mocker.patch('src.webpage.app.add_to_db')
    
    # Test the POST request
    response = client.post('/rescrape')
    
    # Should redirect (302) back to dashboard
    assert response.status_code == 302
    assert response.location.endswith('/')
    
    # Should have called the scraper functions
    mock_run_rescrape.assert_called_once()
    mock_add_to_db.assert_called_once()

@pytest.mark.buttons  
def test_post_update_analysis_route(client):
    """Test POST /refresh (update analysis button) - Returns redirect"""
    response = client.post('/refresh')
    
    # Should redirect (302) back to dashboard 
    assert response.status_code == 302
    assert response.location.endswith('/')
    
@pytest.mark.buttons
def test_busy_state_refresh_during_scrape(client, mocker):
    """Test that refresh returns 409 busy when scrape is in progress"""
    import threading
    
    # Create an event to control when scrape finishes
    scrape_event = threading.Event()
    
    def controlled_scrape():
        # Wait for test to signal completion
        scrape_event.wait()
    
    # Mock scraper to use our controlled function
    mock_run_rescrape = mocker.patch('src.webpage.app.run_rescrape', side_effect=controlled_scrape)
    mock_add_to_db = mocker.patch('src.webpage.app.add_to_db')
    
    # Start scrape in background thread
    scrape_thread = threading.Thread(target=lambda: client.post('/rescrape'))
    scrape_thread.start()
    
    # Now try refresh while scrape is "running" (waiting on event)
    response = client.post('/refresh')
    
    # Should return 409 with busy status
    assert response.status_code == 409
    assert response.get_json() == {"busy": True}
    
    # Signal scrape to complete and wait for thread
    scrape_event.set()
    scrape_thread.join()

@pytest.mark.buttons
def test_busy_state_concurrent_scrapes(client, mocker):
    """Test that second scrape returns 409 busy when first scrape is in progress"""
    import threading
    
    # Create an event to control when scrape finishes
    scrape_event = threading.Event()
    
    def controlled_scrape():
        # Wait for test to signal completion
        scrape_event.wait()
    
    # Mock scraper to use our controlled function
    mock_run_rescrape = mocker.patch('src.webpage.app.run_rescrape', side_effect=controlled_scrape)
    mock_add_to_db = mocker.patch('src.webpage.app.add_to_db')
    
    # Start first scrape in background thread
    scrape_thread = threading.Thread(target=lambda: client.post('/rescrape'))
    scrape_thread.start()
    
    # Try second scrape while first is "running" (waiting on event)
    response = client.post('/rescrape')
    
    # Should return 409 with busy status
    assert response.status_code == 409
    assert response.get_json() == {"busy": True}
    
    # Signal first scrape to complete and wait for thread
    scrape_event.set()
    scrape_thread.join()

@pytest.mark.buttons
def test_busy_state_injectable_control(client, mocker):
    """Test busy state is observable/injectable without arbitrary waits"""
    # Directly set the busy state (injectable)
    from src.webpage import app as app_module
    
    # Set busy state directly
    app_module.is_scraping = True
    
    # Test that refresh returns busy
    response = client.post('/refresh')
    assert response.status_code == 409
    assert response.get_json() == {"busy": True}
    
    # Reset busy state
    app_module.is_scraping = False
    
    # Test that refresh works normally
    response = client.post('/refresh')
    assert response.status_code == 302