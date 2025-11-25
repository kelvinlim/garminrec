#! /usr/bin/env python

from flask import Flask, render_template, url_for, redirect, send_file, request, Response
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

import requests_oauthlib
from dotenv import load_dotenv
import os
import json
import logging
import traceback

# Configure logging
logging.basicConfig(
    filename='app_errors.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
    force=True
)


version = "1.05"

# database code
#from db_cm import Db
# switch to new database structure with Study
from db_study import Db

#import requests

# Using OAuth1Session
from requests_oauthlib import OAuth1Session

load_dotenv()  # take environment variables from .env.

request_token_url = 'https://connectapi.garmin.com/oauth-service/oauth/request_token'
base_authorization_url = 'https://connect.garmin.com/oauthConfirm'
access_token_url = 'https://connectapi.garmin.com/oauth-service/oauth/access_token'

callback_uri = 'https://lnpitask.umn.edu/garminrec/callback'

client_key = os.getenv('client_key')
client_secret = os.getenv('client_secret')
callback_uri = os.getenv('callback_uri')

# setup the db
db = Db()

app = Flask(__name__)

# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] =client_secret

# Flask-Bootstrap requires this line
Bootstrap(app)

class InfoForm(FlaskForm):
    studyinfo = StringField('Please enter study information provided by staff: ', validators=[DataRequired()])
    submit = SubmitField('Submit')

# initialize globals
resource_owner_key = ''
resource_owner_secret = ''

# do oauth initialization

@app.route("/")
def index():

   global resource_owner_key, resource_owner_secret, request_token_url, \
      base_authorization_url, callback_uri

   oauth = OAuth1Session(client_key, client_secret=client_secret)
   fetch_response = oauth.fetch_request_token(request_token_url)

   resource_owner_key = fetch_response.get('oauth_token')
   resource_owner_secret = fetch_response.get('oauth_token_secret')

  
   #Save the oauth_token in a new row in the accounts table, along with subject_id and study_id
   db.add_oauth_token(resource_owner_key, '1234', '56789')

   if callback_uri:
      # use the callback_uri
      # how to use explicit callback: https://requests-oauthlib.readthedocs.io/en/latest/api.html?highlight=oauth_callback#requests_oauthlib.OAuth1Session.authorization_url
      authorization_url = oauth.authorization_url(base_authorization_url, 
         callback_uri=callback_uri)
   else:
      # don't use callback_uri
      authorization_url = oauth.authorization_url(base_authorization_url)

   #print('Please go here and authorize,', authorization_url)

   form = InfoForm()
   message = ""
   if form.validate_on_submit():
      studyinfo = form.studyinfo.data
      return redirect( url_for('authorize', studyinfo=studyinfo) )
 

   """
   return (
      "<h2>Thank you for participating in research at the University of Minnesota!</h2>  \
      <p>Please click on the Authorize link below to give <b>Garmin Connect</b> permission to share your data with UMN Psychiatry.</p>"
      '<a class="button" href="{}">Click here to Authorize</a>'.format(authorization_url) 
      )
   """
   return render_template("index.html", authorization_url=authorization_url)

@app.route("/authorize")
def authorize():
   pass

@app.route("/privacy")
def privacy():
   return render_template("privacy.html")

@app.route("/callback")
def callback():

   global resource_owner_key, resource_owner_secret, access_token_url

   """
   This gets returned
   for callback
   https://lnpitest.northcentralus.cloudapp.azure.com/garminrec/callback?oauth_token=c320eef5-cd50-4baa-8c3a-adf129b71ede&oauth_verifier=qDrm812Aa7

   """
   pass
   #oauth = OAuth1Session(client_key, client_secret=client_secret)
   
   #oauth_response = oauth.parse_authorization_response(redirect_response)

   #get the verifier  
   # do this as part of the callback
   verifier =request.args.get('oauth_verifier')
   oauth_token = request.args.get('oauth_token')
   """

   3. Obtain an access token from the OAuth provider. 
   Save this token as it can be re-used later. 
   In this step we will re-use most of the credentials obtained 
   up til this point.
   """
   
   # Using OAuth1Session
   # do with callback
   oauth = OAuth1Session(  client_key,
                           client_secret=client_secret,
                           resource_owner_key=resource_owner_key,
                           resource_owner_secret=resource_owner_secret,
                           verifier=verifier)
   
   oauth_tokens = oauth.fetch_access_token(access_token_url)
   
   # user access token is oauth_tokens['oauth_token']

   # load this info into the accounts table if it doesn't already exist
   db.new_uat(oauth_tokens['oauth_token'],oauth_tokens['oauth_token_secret'], oauth_token)

   # set register flag 1 (True)
   db.register_uat(oauth_tokens['oauth_token'], register=1)

   """
   return(
   '<p>  Verifier {}</p>'.format(
         verifier
   ))
   """
   return render_template("callback.html")

@app.route("/icon")
def icon():
   #return send_file(url_for('static', filename='z_150_icon.png'))
   #return send_file('static/z_150_icon.png')
   mnfile = 'static/goldy_150.png'
   return send_file(mnfile)

###
### routes for each of the data endpoints
###

@app.route('/activities', methods=['POST'])
def activities():
   # receive data from garmin 
   try:
      req = request.get_json()
      db.add_raw_data(req)
      return Response("OK", status=200, mimetype='application/json' )
   except Exception as e:
      logging.error(f"Error in activities: {str(e)}")
      logging.error(traceback.format_exc())
      return Response("OK", status=200, mimetype='application/json' )

@app.route('/activitydetails', methods=['POST'])
def activitydetails():
   # receive data from garmin 
   try:
      req = request.get_json()
      db.add_raw_data(req)
      return Response("OK", status=200, mimetype='application/json' )
   except Exception as e:
      logging.error(f"Error in activitydetails: {str(e)}")
      logging.error(traceback.format_exc())
      return Response("OK", status=200, mimetype='application/json' )

@app.route('/bodycomp', methods=['POST'])
def bodycomp():
   # receive data from garmin 
   try:
      req = request.get_json()
      db.add_raw_data(req)
      return Response("OK", status=200, mimetype='application/json' )
   except Exception as e:
      logging.error(f"Error in bodycomp: {str(e)}")
      logging.error(traceback.format_exc())
      return Response("OK", status=200, mimetype='application/json' )

@app.route('/dailies', methods=['POST'])
def dailies():
   # receive data from garmin 
   try:
      req = request.get_json()
      db.add_raw_data(req)
      return Response("OK", status=200, mimetype='application/json' )
   except Exception as e:
      logging.error(f"Error in dailies: {str(e)}")
      logging.error(traceback.format_exc())
      return Response("OK", status=200, mimetype='application/json' )

@app.route('/deregistrations', methods=['POST'])
def deregistrations():
   # receive data from garmin 
   try:
      req = request.get_json()
      db.add_raw_data(req)
      # set register flag 0 (False) in accounts
      uat = req['deregistrations'][0]['userAccessToken']
      db.register_uat(uat, register=0)
      return Response("OK", status=200, mimetype='application/json' )
   except Exception as e:
      logging.error(f"Error in deregistrations: {str(e)}")
      logging.error(traceback.format_exc())
      return Response("OK", status=200, mimetype='application/json' )

@app.route('/epochs', methods=['POST'])
def epochs():
   # receive data from garmin 
   try:
      req = request.get_json()
      db.add_raw_data(req)
      return Response("OK", status=200, mimetype='application/json' )
   except Exception as e:
      logging.error(f"Error in epochs: {str(e)}")
      logging.error(traceback.format_exc())
      return Response("OK", status=200, mimetype='application/json' )

@app.route('/healthsnapshot', methods=['POST'])
def healthsnapshot():
   # receive data from garmin 
   try:
      req = request.get_json()
      db.add_raw_data(req)
      return Response("OK", status=200, mimetype='application/json' )
   except Exception as e:
      logging.error(f"Error in healthsnapshot: {str(e)}")
      logging.error(traceback.format_exc())
      return Response("OK", status=200, mimetype='application/json' )

@app.route('/manactivities', methods=['POST'])
def manactivities():
   # receive data from garmin 
   try:
      req = request.get_json()
      db.add_raw_data(req)
      return Response("OK", status=200, mimetype='application/json' )
   except Exception as e:
      logging.error(f"Error in manactivities: {str(e)}")
      logging.error(traceback.format_exc())
      return Response("OK", status=200, mimetype='application/json' )

@app.route('/moveiq', methods=['POST'])
def moveiq():
   # receive data from garmin 
   try:
      req = request.get_json()
      db.add_raw_data(req)
      return Response("OK", status=200, mimetype='application/json' )
   except Exception as e:
      logging.error(f"Error in moveiq: {str(e)}")
      logging.error(traceback.format_exc())
      return Response("OK", status=200, mimetype='application/json' )

@app.route('/pulseox', methods=['POST'])
def pulseox():
   # receive data from garmin 
   try:
      req = request.get_json()
      db.add_raw_data(req)
      return Response("OK", status=200, mimetype='application/json' )
   except Exception as e:
      logging.error(f"Error in pulseox: {str(e)}")
      logging.error(traceback.format_exc())
      return Response("OK", status=200, mimetype='application/json' )

@app.route('/respiration', methods=['POST'])
def respiration():
   # receive data from garmin 
   try:
      req = request.get_json()
      db.add_raw_data(req)
      return Response("OK", status=200, mimetype='application/json' )
   except Exception as e:
      logging.error(f"Error in respiration: {str(e)}")
      logging.error(traceback.format_exc())
      return Response("OK", status=200, mimetype='application/json' )

@app.route('/sleeps', methods=['POST'])
def sleeps():
   # receive data from garmin 
   try:
      req = request.get_json()
      db.add_raw_data(req)
      return Response("OK", status=200, mimetype='application/json' )
   except Exception as e:
      logging.error(f"Error in sleeps: {str(e)}")
      logging.error(traceback.format_exc())
      return Response("OK", status=200, mimetype='application/json' )

@app.route('/stress', methods=['POST'])
def stress():
   # receive data from garmin 
   try:
      req = request.get_json()
      db.add_raw_data(req)
      return Response("OK", status=200, mimetype='application/json' )
   except Exception as e:
      logging.error(f"Error in stress: {str(e)}")
      logging.error(traceback.format_exc())
      return Response("OK", status=200, mimetype='application/json' )

@app.route('/thirddailies', methods=['POST'])
def thirddailies():
   # receive data from garmin 
   try:
      req = request.get_json()
      db.add_raw_data(req)
      return Response("OK", status=200, mimetype='application/json' )
   except Exception as e:
      logging.error(f"Error in thirddailies: {str(e)}")
      logging.error(traceback.format_exc())
      return Response("OK", status=200, mimetype='application/json' )

@app.route('/usermetrics', methods=['POST'])
def usermetrics():
   # receive data from garmin 
   try:
      req = request.get_json()
      db.add_raw_data(req)
      return Response("OK", status=200, mimetype='application/json' )
   except Exception as e:
      logging.error(f"Error in usermetrics: {str(e)}")
      logging.error(traceback.format_exc())
      return Response("OK", status=200, mimetype='application/json' )

# change port
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5005)
    
    
    


