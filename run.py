from flask import render_template
from app.app import app
from api import views
from app.database import db

db.drop_all()
db.create_all()


@app.route('/')
def index():
    return render_template('index.html')
