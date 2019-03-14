import dash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import json
from flask import Flask
from dash_google_auth import GoogleOAuth

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

APP_ROOT = os.path.join(os.path.dirname(__file__), '..') 
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

config_path = os.path.join(APP_ROOT, 'config.json')
with open(config_path, 'r') as f:
    CONFIG = json.load(f)

server = Flask(__name__)
app = dash.Dash(
    __name__, 
    server=server,
    url_base_pathname='/',
    auth='auth',
    external_stylesheets=external_stylesheets
)
app.server.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['supress_callback_exceptions'] = True
app.title = 'Pathways'
db = SQLAlchemy(app.server)

server.secret_key = os.environ.get('FLASK_SEACRET_KEY', 'supersekrit')
server.config['GOOGLE_OAUTH_CLIENT_ID'] = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
server.config['GOOGLE_OAUTH_CLIENT_SECRET'] = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')

# DEV: Remove this for release
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Get authorized users
emails = db.session.execute('SELECT email FROM login').fetchall()

authorized_emails = []
for e in emails:
    authorized_emails.append(e[0])
   
auth = GoogleOAuth(
    app,
    authorized_emails
)

@server.route('/Pathways')
def pathways_app():
    return app.index()




