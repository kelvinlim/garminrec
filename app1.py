from flask import Flask, render_template, url_for, send_file, request, Response

import requests_oauthlib
from dotenv import load_dotenv
import os
import json
#import requests

# Using OAuth1Session
from requests_oauthlib import OAuth1Session

load_dotenv()  # take environment variables from .env.

request_token_url = 'https://connectapi.garmin.com/oauth-service/oauth/request_token'
base_authorization_url = 'https://connect.garmin.com/oauthConfirm'
access_token_url = 'https://connectapi.garmin.com/oauth-service/oauth/access_token'


client_key = os.getenv('client_key')
client_secret = os.getenv('client_secret')

oauth = OAuth1Session(client_key, client_secret=client_secret)

# setup the db
from db import Db
db = Db()

app = Flask(__name__)

# initialize globals
resource_owner_key = ''
resource_owner_secret = ''

# do oauth initialization

@app.route("/")
def index():

   global resource_owner_key, resource_owner_secret

   fetch_response = oauth.fetch_request_token(request_token_url)

   resource_owner_key = fetch_response.get('oauth_token')
   resource_owner_secret = fetch_response.get('oauth_token_secret')

   authorization_url = oauth.authorization_url(base_authorization_url)

   #print('Please go here and authorize,', authorization_url)

   return(
      "<p>Hello, please go here to authorize Garmin to share your data with lnpitest.</p>"
      '<a class="button" href="{}">Authorize</a>'.format(
            authorization_url
      ))

@app.route("/privacy")
def privacy():
   return render_template("privacy.html")

@app.route("/callback")
def callback():

   global resource_owner_key, resource_owner_secret

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
   token = request.args.get('oauth_token')
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
   db.check_uat(oauth_tokens['oauth_token'],oauth_tokens['oauth_token_secret'])

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
   mnfile = 'static/UMN_M-wdmk-stack-D2D-maroon-blk.png'
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
   # set register flag 0 (False)
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


# change port
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5005)
    
    
    


