from flask import Blueprint

main = Blueprint("main", __name__)

@main.route("/")
def map():
    return "<h1>This page will have the map</h1>"
