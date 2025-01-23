from flask import Flask, redirect, url_for, session, request, jsonify, render_template, flash
from markupsafe import Markup
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from authlib.integrations.flask_client import OAuth
from bson.objectid import ObjectId
from dotenv import load_dotenv

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
oauth.register(
    name='github',
    client_id=os.environ['GITHUB_CLIENT_ID'],
    client_secret=os.environ['GITHUB_CLIENT_SECRET'],
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

# https://www.perplexity.ai/search/error-traceback-most-recent-ca-k2rRbvIcTViNSHBWFV2i_w

#https://www.perplexity.ai/search/127-0-0-1-21-jan-2025-13-20-12-lAALaZgYSYOiURpy1jaPgQS
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


#context processors run before templates are rendered and add variable(s) to the template's context
#context processors must return a dictionary 
#this context processor adds the variable logged_in to the conext for all template

@app.context_processor
def inject_logged_in():
    return {"logged_in": ('github_token' in session)}


@app.route('/')
def home():
    return render_template('home.html')

# Redirect to OAuth page and confirm callback URL
@app.route('/login')
def login():
    github = oauth.create_client('github')
    redirect_uri = url_for('callback', _external=True)
    return github.authorize_redirect(redirect_uri)





@app.route('/callback')
def callback():
    token = oauth.github.authorize_access_token()
    resp = oauth.github.get('user', token=token)
    user_info = resp.json()
    # Do something with the token and profile
    session['github_token'] = token
    session['user_data'] = user_info
    return redirect(url_for('home'))



@app.route('/logout')
def logout():
    session.pop('github_token', None)
    session.pop('user_data', None)
    return redirect(url_for('home'))


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
    
@app.route('/UnityS')
def renderUnityS():
    return render_template('UnityS.html')
    
@app.route('/WSBG')
def renderWSBG():
   return render_template('WSBG.html')
   
@app.route('/SBZ')
def renderSBZ():
    return render_template('SBZ.html')
    
@app.route('/FNC')
def renderFNC():
    return render_template('FNC.html')
    
@app.route('/CSW')
def renderCSW():
    return render_template('CSW.html')
    
    
@app.route('/CNWH')
def renderCNWH():
    return render_template('CNWH.html')
    
@app.route('/HTEC')
def renderHTEC():
    return render_template('HTEC.html')

if __name__ == '__main__':
    app.run(debug=True)

