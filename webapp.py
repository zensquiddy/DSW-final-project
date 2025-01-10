from flask import Flask, redirect, url_for, session, request, jsonify, render_template, flash
from markupsafe import Markup
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from authlib.integrations.flask_client import OAuth
from bson.objectid import ObjectId
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os.path
import pprint
import os
import time
import pymongo
import sys

app = Flask(__name__)

app.debug = True  # Change this to False for production
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' #Remove once done debugging


app.secret_key = os.environ['SECRET_KEY']  # used to sign session cookies

# Initialize OAuth
oauth = OAuth(app)
load_dotenv()
SCOPES = ["https://www.googleapis.com/auth/documents.readonly"]
DOCUMENT_ID = "195j9eDD3ccgjQRttHhJPymLJUCOUjs-jmwTrekvdjFE"
CLIENT_SECRET_FILE = os.path.join(os.path.dirname(__file__), 'client_secret.json')


# Set up Google as OAuth provider
google = oauth.register(
    name='google',
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET'),
    scopes = ['your_scopes_here'],
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes=['your_scopes_here']),
    client_id=os.environ['GOOGLE_CLIENT_ID'],  # Your Google Client ID
    client_secret=os.environ['GOOGLE_CLIENT_SECRET'],  # Your Google Client Secret
    access_token_url='https://accounts.google.com/o/oauth2/token',
    AUTH_URL = 'https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={
        'scope': 'openid email profile',
    }
)

# Connect to database
url = os.environ["MONGO_CONNECTION_STRING"]
client = pymongo.MongoClient(url)
db = client[os.environ["MONGO_DBNAME"]]
collection = db['posts']

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

@app.context_processor
def inject_logged_in():
    return {"logged_in": ('google_token' in session)}

@app.route('/')
def home():
    return render_template('home.html')

# Redirect to Google's OAuth page and confirm callback URL
@app.route('/login')
def login():
    # Create the OAuth flow object
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('callback', _external=True, _scheme='https')
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='select_account')

    # Save the state so we can verify the request later
    session['state'] = state

    return redirect(authorization_url)



@app.route('/callback')
def callback():
    # Verify the request state
    if request.args.get('state') != session['state']:
        raise Exception('Invalid state')

    # Create the OAuth flow object
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_FILE, scopes=SCOPES, state=session['state'])
    flow.redirect_uri = url_for('callback', _external=True)

    # Exchange the authorization code for an access token
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Save the credentials to the session
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    token = google.authorize_access_token()
    if not token:
        session.clear()
        flash('Access denied or error occurred.', 'error')
        return redirect('/')
    
    try:
        session['google_token'] = token  # Save the token in the session
        user_info = google.get('userinfo').json()
        session['user_data'] = user_info  # Save user data in the session
        message = f"You were successfully logged in as {user_info['email']}."
    except Exception as inst:
        session.clear()
        print(inst)
        message = 'Unable to login, please try again.', 'error'
    
    return render_template('message.html', message=message)

@app.route('/Jobs')
def renderJobs():
    if 'user_data' in session:
        user_data_pprint = pprint.pformat(session['user_data'])  # Format the user data nicely
    else:
        user_data_pprint = ''
    return render_template('page1.html', dump_user_data=user_data_pprint)

@app.route('/Map')
def renderMap():
    return render_template('page2.html')


@app.route('/Info')
def renderInfo():
    return render_template('Info.html')
    
    
@app.route('/SBPL')
def renderSBPL():
    return render_template('SBPL.html')

if __name__ == '__main__':
    app.run(debug=True)

