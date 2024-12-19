from flask import Flask

app = Flask(__name__)

@app.route('/')
def map():
    return '<h1>This page will have the map</h1>'