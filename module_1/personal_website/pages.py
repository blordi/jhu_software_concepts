""""
Ben L - 8.29.25
Sets up the blueprints for each page in the website. designates bp as Blueprint and renders each html template in a
function.
"""
from flask import Blueprint, render_template

bp = Blueprint("pages", __name__)

@bp.route("/")
#default route for home, sometimes called index
def home():
    """ returns the home page """
    return render_template("pages/home.html")

@bp.route("/contact")
def contact():
    """ renders the contact page """
    return render_template("pages/contact.html")

@bp.route("/projects")
def projects():
    """returns the project page"""
    return render_template("pages/projects.html")