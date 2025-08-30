"""
Ben L - 8.29.25
Personal website package for Modern Software Concepts in Python class.

This Flask application creates a personal website with a bio, contact page, and list of projects.  The package utilizes
blueprints and templates to create the pages.

I based the project on https://realpython.com/flask-project/

- Uses create_app() to initialize app
- Uses blueprints from pages.py
- Uses CSS and HTML for static assets
"""
from flask import Flask
from personal_website import pages

def create_app():
    """
    Creates Flask application, registers the pages blueprint, and returns app instance.
    """
    app = Flask(__name__)

    app.register_blueprint(pages.bp)
    return app
app = create_app()