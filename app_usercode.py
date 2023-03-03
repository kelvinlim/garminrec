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

from werkzeug.middleware.proxy_fix import ProxyFix

version = "2.0"

# database code
from db_code import Db

#import requests

# Using OAuth1Session
from requests_oauthlib import OAuth1Session

load_dotenv()  # take environment variables from .env.

request_token_url = 'https://connectapi.garmin.com/oauth-service/oauth/request_token'
base_authorization_url = 'https://connect.garmin.com/oauthConfirm'
access_token_url = 'https://connectapi.garmin.com/oauth-service/oauth/access_token'

callback_uri = 'https://lnpitask.umn.edu/garminrec/callback'

##TODO use python_dotenv to set these
client_key = os.getenv('client_key')
client_secret = os.getenv('client_secret')
callback_uri = os.getenv('callback_uri')

# setup the db
db = Db()

app = Flask(__name__)

# for dealing with reverse proxy
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)

# Flask-WTF requires an encryption key - the string can be anything
app.config['SECRET_KEY'] =client_secret

# Flask-Bootstrap requires this line
Bootstrap(app)

class UserCodeForm(FlaskForm):
    usercode = StringField('Please enter the User Code provided by the study staff:', validators=[DataRequired()])
    submit = SubmitField('Submit')

# initialize globals
resource_owner_key = ''
resource_owner_secret = ''

@app.route("/", methods=['GET', 'POST'])
def index():

   global resource_owner_key, resource_owner_secret, request_token_url, \
      base_authorization_url, callback_uri

   form = UserCodeForm()
   message = ""
   if form.validate_on_submit():
      usercode = form.usercode.data
      id, register = db.entry_code_exists(usercode)
      if id and not register:
         # This is good entry code so get setup to go to garmin site
         # the token exists and register=0
         # empty the form field
         form.usercode.data = ""
      
         # redirect the browser to another route and template
         # return redirect( url_for('/garminrec/goto_garmin', usercode=usercode) )
         return redirect( url_for('goto_garmin', usercode=usercode, _external=True) )
      else:
         if id and register:
            message = f"usercode {usercode} exists but has already been registered."
         elif  id == 0:
            message = f"usercode {usercode} is not valid. Please recheck entry."


   return render_template('index_usercode.html', form=form, message=message)
   

"""
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
 
   return render_template("index.html", authorization_url=authorization_url)
"""
@app.route("/goto_garmin/<usercode>")
def goto_garmin(usercode):

   global resource_owner_key, resource_owner_secret, request_token_url, \
   base_authorization_url, callback_uri
   
   # returns a tuple so select first element
   account_id, register = db.entry_code_exists(usercode)

   oauth = OAuth1Session(client_key, client_secret=client_secret)
   fetch_response = oauth.fetch_request_token(request_token_url)

   resource_owner_key = fetch_response.get('oauth_token')
   resource_owner_secret = fetch_response.get('oauth_token_secret')

   #Save the oauth_token in the account with id=res
   db.update_oauth_token_id(account_id, resource_owner_key)

   if callback_uri:
      # use the callback_uri
      # how to use explicit callback: https://requests-oauthlib.readthedocs.io/en/latest/api.html?highlight=oauth_callback#requests_oauthlib.OAuth1Session.authorization_url
      authorization_url = oauth.authorization_url(base_authorization_url, 
         callback_uri=callback_uri)
   else:
      # don't use callback_uri
      authorization_url = oauth.authorization_url(base_authorization_url)

   return redirect(authorization_url,code=302)


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
   req = request.get_json()
   db.add_raw_data(req)
   return Response("OK", status=200, mimetype='application/json' )

@app.route('/activitydetails', methods=['POST'])
def activitydetails():
   # receive data from garmin 
   req = request.get_json()
   db.add_raw_data(req)
   return Response("OK", status=200, mimetype='application/json' )

@app.route('/bodycomp', methods=['POST'])
def bodycomp():
   # receive data from garmin 
   req = request.get_json()
   db.add_raw_data(req)
   return Response("OK", status=200, mimetype='application/json' )

@app.route('/dailies', methods=['POST'])
def dailies():
   # receive data from garmin 
   req = request.get_json()
   db.add_raw_data(req)
   return Response("OK", status=200, mimetype='application/json' )

@app.route('/deregistrations', methods=['POST'])
def deregistrations():
   # receive data from garmin 
   req = request.get_json()
   db.add_raw_data(req)
   # set register flag 0 (False) in accounts
   uat = req['deregistrations'][0]['userAccessToken']
   db.register_uat(uat, register=0)
   return Response("OK", status=200, mimetype='application/json' )

@app.route('/epochs', methods=['POST'])
def epochs():
   # receive data from garmin 
   req = request.get_json()
   db.add_raw_data(req)
   return Response("OK", status=200, mimetype='application/json' )

@app.route('/healthsnapshot', methods=['POST'])
def healthsnapshot():
   # receive data from garmin 
   req = request.get_json()
   db.add_raw_data(req)
   return Response("OK", status=200, mimetype='application/json' )

@app.route('/hrvsummary', methods=['POST'])
def hrvsummary():
   # receive data from garmin 
   req = request.get_json()
   db.add_raw_data(req)
   return Response("OK", status=200, mimetype='application/json' )

@app.route('/manactivities', methods=['POST'])
def manactivities():
   # receive data from garmin 
   req = request.get_json()
   db.add_raw_data(req)
   return Response("OK", status=200, mimetype='application/json' )

@app.route('/moveiq', methods=['POST'])
def moveiq():
   # receive data from garmin 
   req = request.get_json()
   db.add_raw_data(req)
   return Response("OK", status=200, mimetype='application/json' )

@app.route('/pulseox', methods=['POST'])
def pulseox():
   # receive data from garmin 
   req = request.get_json()
   db.add_raw_data(req)
   return Response("OK", status=200, mimetype='application/json' )

@app.route('/respiration', methods=['POST'])
def respiration():
   # receive data from garmin 
   req = request.get_json()
   db.add_raw_data(req)
   return Response("OK", status=200, mimetype='application/json' )

@app.route('/sleeps', methods=['POST'])
def sleeps():
   # receive data from garmin 
   req = request.get_json()
   db.add_raw_data(req)
   return Response("OK", status=200, mimetype='application/json' )

@app.route('/stress', methods=['POST'])
def stress():
   # receive data from garmin 
   req = request.get_json()
   db.add_raw_data(req)
   return Response("OK", status=200, mimetype='application/json' )

@app.route('/thirddailies', methods=['POST'])
def thirddailies():
   # receive data from garmin 
   req = request.get_json()
   db.add_raw_data(req)
   return Response("OK", status=200, mimetype='application/json' )

@app.route('/usermetrics', methods=['POST'])
def usermetrics():
   # receive data from garmin 
   req = request.get_json()
   db.add_raw_data(req)
   return Response("OK", status=200, mimetype='application/json' )

# change port
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5005)
    #app.run(debug=True, host="localhost", port=5005)
    
    
    


