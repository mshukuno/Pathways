import dash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import json
from flask import Flask
from dash_google_auth import GoogleOAuth
import sys
from sty import fg, rs

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
APP_ROOT = os.path.join(os.path.dirname(__file__), '..') 
config_path = os.path.join(APP_ROOT, 'config.json')
with open(config_path, 'r') as f:
    CONFIG = json.load(f)

server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=external_stylesheets)
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['suppress_callback_exceptions']=True
app.title = 'Pathways'

# Check SQLALCHEMY connection to DATABASE
try:
    # Get URI from system
    print(f'{fg.green} ----- Checking ----- {fg.rs}')
    if os.environ.get('SQLALCHEMY_DATABASE_URI'):
        app.server.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    # Get URI from .env
    else:
        dotenv_path = os.path.join(APP_ROOT, '.env')
        load_dotenv(dotenv_path)        
        app.server.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    print(f'SQLALCHEMY_DATABASE_URI ---{fg.green} OK{fg.rs}\n')
    db = SQLAlchemy(app.server)
except Exception as e:
    print(e)
    print(fg.red + ' SQLALCHEMY_DATABASE_URI not set or incorrect URI.' + fg.rs)

# Check Google Auth
if CONFIG['AUTH'].lower() == 'yes':
    app.auth = 'auth'
    app.url_base_pathname = '/'

    try:
        print(f'{fg.green} ----- Google Auth Settings ----- {fg.rs}')
        # Getting values from .env file
        server.secret_key = os.getenv('FLASK_SEACRET_KEY')
        print(f'FLASK_SEACRET_KEY ---{fg.green} OK{fg.rs}')

        server.config['GOOGLE_OAUTH_CLIENT_ID'] = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
        print(f'GOOGLE_OAUTH_CLIENT_ID ---{fg.green} OK{fg.rs}')

        server.config['GOOGLE_OAUTH_CLIENT_SECRET'] = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
        print(f'GOOGLE_OAUTH_CLIENT_SECRET ---{fg.green} OK{fg.rs}')

        # DEV: Remove this for release
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        
    except Exception as e:
        print(e)
        print(fg.red + '''Something went wrong. \n
        Check "FLASK_SEACRET_KEY", GOOGLE_OAUTH_CLIENT_ID", and 
        "GOOGLE_OAUTH_CLIENT_SECRET" values set in .env file.''')
        sys.exit()


# Get authorized users
if CONFIG['AUTH'].lower() == 'yes':
    try:
        tables = db.engine.table_names()
        if len(tables) > 0:
            if 'login' in tables:
                emails = db.session.execute('SELECT email FROM login').fetchall()

                authorized_emails = []
                for e in emails:
                    authorized_emails.append(e[0])

                auth = GoogleOAuth(
                    app,
                    authorized_emails
                )
                print(f'GOOGLE AUTH ---{fg.green} OK{fg.rs}\n\n')

                @server.route('/Pathways')
                def pathways_app():
                    return app.index()

            else:
                print(fg.yellow +' Missing "login" table in DB.' + fg.rs)
                sys.exit()
        else:
            print(fg.yellow + ' No table found in DB. Upload dump file.' + fg.rs)
            sys.exit()
        
    except Exception as e:
        print(e)
        print(fg.red + ' No table found in DB. Upload dump file' + fg.rs)
        sys.exit()






