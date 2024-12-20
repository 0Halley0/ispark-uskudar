from flask import Blueprint, render_template
from app.services import fetch_ispark_data

main = Blueprint("main", __name__)

@main.route("/")
def map():
    ispark_data = fetch_ispark_data()
    return render_template("index.html", ispark_data=ispark_data)
