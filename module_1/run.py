"""
Ben L - 8.29.25
This script imports a Flask app from personal_website and runs it.
Usage:
    python run.py
"""
from personal_website import app

if __name__ == '__main__':
    #Running with debug on, host = 0.0.0.0 and port = 8080
    app.run(debug=True, host= '0.0.0.0', port=8080)