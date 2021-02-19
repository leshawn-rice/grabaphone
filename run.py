from flask import render_template
from app.app import app
from api import views
from app.database import db


@app.route('/')
def index():
    return render_template('index.html')
