""""
Ben L - 8.29.25
Blueprints for website pages.
Contains route for each page and each rout renders its HTML template.
"""
from flask import Blueprint, render_template

bp = Blueprint("pages", __name__)

@bp.route("/")
#default route for home
def home():
    """ renders the home page """
    return render_template("pages/home.html")

@bp.route("/contact")
def contact():
    """ renders the contact page """
    return render_template("pages/contact.html")

@bp.route("/projects")
def projects():
    """renders the project page"""
    return render_template("pages/projects.html")