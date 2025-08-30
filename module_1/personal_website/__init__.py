"""
Ben L - 8.29.25
The init file for the personal_website package. Based off of https://realpython.com/flask-project/
Uses a create_app function to run the app, and blueprints from pages.py
"""
from flask import Flask
from personal_website import pages

def create_app():
    """
    Calls the app function and creates a flask app.  Uses the register_blueprint function and pages.bp from pages.py
    to create the app.
    :return: app
    """
    app = Flask(__name__)

    app.register_blueprint(pages.bp)
    return app
#creates the app so run.py will work
app = create_app()