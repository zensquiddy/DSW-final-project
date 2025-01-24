from flask import Flask, redirect, url_for, session, request, jsonify, render_template, flash
from markupsafe import Markup
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from flask_oauthlib.client import OAuth
from bson.objectid import ObjectId
from dotenv import load_dotenv

import pprint
import os
import time
import pymongo
import sys
 
app = Flask(__name__)
load_dotenv()

app.debug = False #Change this to False for production
#os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' #Remove once done debugging


app.secret_key = os.environ['SECRET_KEY'] #used to sign session cookies
oauth = OAuth(app)
oauth.init_app(app) #initialize the app to be able to make requests for user information

#Set up GitHub as OAuth provider
github = oauth.remote_app(
    'github',
    consumer_key=os.environ['GITHUB_CLIENT_ID'], #your web app's "username" for github's OAuth
    consumer_secret=os.environ['GITHUB_CLIENT_SECRET'],#your web app's "password" for github's OAuth
    request_token_params={'scope': 'user:email'}, #request read-only access to the user's email.  For a list of possible scopes, see developer.github.com/apps/building-oauth-apps/scopes-for-oauth-apps
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',  
    authorize_url='https://github.com/login/oauth/authorize' #URL for github's OAuth login
)

#Connect to database
connection_string = os.environ.get("MONGO_CONNECTION_STRING")
client = pymongo.MongoClient(connection_string)
db_name = os.environ["MONGO_DBNAME"]

db = client[db_name]
collection1 = db['Santa Barbara Public Library']
collection2 = db['Unity Shoppe']


for Colors in collection1.find():
        print(Colors)

for doc in collection1.find({"Name":"Santa Barbara Public Library"}):
   print(doc)

# List all databases to test connection


#https://cloud.mongodb.com/v2/675b58a6db24f835738e3230#/metrics/replicaSet/675b5b9698f11f497345b560/explorer/Organizations/Santa%20Barbara%20Public%20Library%20/find
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
    return {"logged_in":('github_token' in session)}


#redirect to GitHub's OAuth page and confirm callback URL
@app.route('/login')
def login():   
    return github.authorize(callback=url_for('authorized', _external=True, _scheme='https')) #callback URL must match the pre-configured callback URL

@app.route('/logout')
def logout():
    session.clear()
    flash('You were logged out.')
    return redirect('/')

@app.route('/login/authorized')
def authorized():
    resp = github.authorized_response()
    if resp is None:
        session.clear()
        flash('Access denied: reason=' + request.args['error'] + ' error=' + request.args['error_description'] + ' full=' + pprint.pformat(request.args), 'error')      
    else:
        try:
            session['github_token'] = (resp['access_token'], '') #save the token to prove that the user logged in
            session['user_data']=github.get('user').data
            message = 'You were successfully logged in as ' + session['user_data']['login'] + '.'
        except Exception as inst:
            session.clear()
            print(inst)
            message = 'Unable to login, please try again.', 'error'
    return render_template('message.html', message=message)


@app.route('/Jobs')
def renderJobs():
    if 'user_data' in session:
        user_data_pprint = pprint.pformat(session['user_data'])#format the user data nicely
    else:
        user_data_pprint = '';
    return render_template('page1.html',dump_user_data=user_data_pprint)

@app.route('/Map')
def renderMap():
    return render_template('page2.html')
    
@app.route('/Info')
def renderInfo():
    return render_template('Info.html')


@app.route('/document/<document_id>')
def view_document(document_id):
    document = collection1.find_one({'_id': ObjectId(document_id)})
    if not document:
        document = collection2.find_one({'_id': ObjectId(document_id)})
    if not document:
        flash('Document not found', 'error')
        return redirect(url_for('home'))
    return render_template('view_document.html', document=document)


@app.route('/create', methods=['GET', 'POST'])
def create_document():
    if request.method == 'POST':
        new_document = {
            'title': request.form['title'],
            'content': request.form['content'],
            'collection': request.form['collection']
        }
        if new_document['collection'] == 'santa_barbara_library':
            collection1.insert_one(new_document)
        elif new_document['collection'] == 'unity_shoppe':
            collection2.insert_one(new_document)
        flash('Document created successfully', 'success')
        return redirect(url_for('home'))
    return render_template('create_document.html')

print("Documents in Santa Barbara Public Library collection:")
for doc in collection1.find():
    print(doc)

print("\nDocuments in Unity Shoppe collection:")
for doc in collection2.find():
    print(doc)
    

@app.route('/santa_barbara_library')
def santa_barbara_library():
    documents = collection1.find()
    return render_template('documents.html', documents=documents, title="Santa Barbara Public Library")

@app.route('/unity_shoppe')
def unity_shoppe():
    documents = collection2.find()
    return render_template('documents.html', documents=documents, title="Unity Shoppe")

@app.route('/')
def home():
    return render_template('home.html')
    
@app.route('/SBPL')
def SBPL():
    return render_template('SBPL.html')
    
@app.route('/UnityS')
def UnityS():
    return render_template('UnityS.html')

@app.route('/CNWH')
def CNWH():
    return render_template('CNWH.html')
    
@app.route('/WSBG')
def WSBG():
    return render_template('WSBG.html')
    
    
@app.route('/CSW')
def CSW():
    return render_template('CSW.html')

@app.route('/HTEC')
def HTEC():
    return render_template('HTEC.html')


@app.route('/SBZ')
def SBZ():
    return render_template('SBZ.html')
    
@app.route('/FNC')
def FNC():
    return render_template('FNC.html')
#the tokengetter is automatically called to check who is logged in.
@github.tokengetter
def get_github_oauth_token():
    return session['github_token']

if __name__ == '__main__':
    app.run(debug=True)


#https://www.perplexity.ai/search/127-0-0-1-21-jan-2025-13-20-12-lAALaZgYSYOiURpy1jaPgQ



