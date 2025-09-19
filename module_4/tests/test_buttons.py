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

@pytest.mark.buttons
def test_add_to_db_exception_handling_complete(mocker):
    """Test add_to_db exception handling prints error and re-raises."""
    from src.webpage import app as app_module
    
    # Mock print to capture it
    mock_print = mocker.patch('builtins.print')
    
    # Mock open to raise a specific exception
    test_exception = Exception("Test file error")
    mocker.patch('builtins.open', side_effect=test_exception)
    
    # Call add_to_db and expect it to raise
    with pytest.raises(Exception) as exc_info:
        app_module.add_to_db()
    
    # Verify the exception was re-raised
    assert exc_info.value is test_exception
    
    # Verify the print statement was called (this hits line 45-46)
    mock_print.assert_called_with("Error in add_to_db: Test file error")

@pytest.mark.buttons
def test_rescrape_error_handling(client, mocker):
    """Test rescrape route handles scraper errors gracefully."""
    # Mock run_rescrape to raise an exception
    mocker.patch('src.webpage.app.run_rescrape', side_effect=Exception("Scraper failed"))
    mock_add_to_db = mocker.patch('src.webpage.app.add_to_db')
    
    response = client.post('/rescrape')
    assert response.status_code == 500
    assert response.get_json() == {"error": "Scraper failed"}

@pytest.mark.buttons
def test_add_to_db_error_handling(client, mocker):
    """Test add_to_db function error handling."""
    from src.webpage import app as app_module
    
    # Mock file operations to raise an exception
    mocker.patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    
    with pytest.raises(FileNotFoundError):
        app_module.add_to_db()

@pytest.mark.buttons
def test_run_rescrape_function_calls(mocker):
    """Test that run_rescrape actually calls scrape.main and clean.main."""
    from src.webpage import app as app_module
    
    # Mock the individual functions that run_rescrape calls
    mock_scrape_main = mocker.patch('scrape.main')
    mock_clean_main = mocker.patch('clean.main')
    
    # Call the REAL run_rescrape function (don't mock it)
    app_module.run_rescrape()
    
    # Verify both functions were called (this hits lines 45-46)
    mock_scrape_main.assert_called_once()
    mock_clean_main.assert_called_once()