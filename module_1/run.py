from flask import Flask
from module_1 import pages

def create_app(test_config=None):
    app = Flask(__name__)

    app.register_blueprint(pages)(pages.bp)
    return app
