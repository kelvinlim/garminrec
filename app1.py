from flask import Flask, render_template, url_for, send_file

import requests_oauthlib
from dotenv import load_dotenv
import os

# Using OAuth1Session
from requests_oauthlib import OAuth1Session

load_dotenv()  # take environment variables from .env.

request_token_url = 'https://connectapi.garmin.com/oauth-service/oauth/request_token'
base_authorization_url = 'https://connect.garmin.com/oauthConfirm'
access_token_url = 'https://connectapi.garmin.com/oauth-service/oauth/access_token'

# TODO switch to using dot_env
client_key = 'c118028e-05f9-4ee6-bea0-e054d4e98cac'
client_secret = '6uUOIxYkaVCfzqjvR4mbWwjf398yQy7qRhP'

client_key = os.getenv('client_key')
client_secret = os.getenv('client_secret')

oauth = OAuth1Session(client_key, client_secret=client_secret)

app = Flask(__name__)

# do oauth initialization

@app.route("/")
def index():
   fetch_response = oauth.fetch_request_token(request_token_url)

   resource_owner_key = fetch_response.get('oauth_token')
   resource_owner_secret = fetch_response.get('oauth_token_secret')

   authorization_url = oauth.authorization_url(base_authorization_url)

   print('Please go here and authorize,', authorization_url)

   return(
      "<p>Hello, please go here to authorize Garmin to share your data with lnpitest.</p>"
      '<a class="button" href="{}">Logout</a>'.format(
            authorization_url
      ))

@app.route("/privacy")
def privacy():
   return render_template("privacy.html")

@app.route("/callback")
def callback():
   return render_template("callback.html")

@app.route("/icon")
def icon():
   #return send_file(url_for('static', filename='z_150_icon.png'))
   return send_file('static/z_150_icon.png')

# change port
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5005)
    
    
    


