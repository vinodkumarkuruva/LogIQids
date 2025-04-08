import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = '!1234$567*90'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir+'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app,db)

from Log import views