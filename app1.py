from flask import Flask, render_template, url_for, send_file, request

import requests_oauthlib
from dotenv import load_dotenv
import os
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
   return send_file('static/UMN_M-wdmk-stack-D2D-maroon-blk.png')
# change port
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5005)
    
    
    


