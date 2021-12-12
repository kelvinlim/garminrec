# from https://requests-oauthlib.readthedocs.io/en/latest/oauth1_workflow.html

import requests_oauthlib

# Using OAuth1Session
from requests_oauthlib import OAuth1Session

request_token_url = 'https://connectapi.garmin.com/oauth-service/oauth/request_token'
base_authorization_url = 'https://connect.garmin.com/oauthConfirm'
access_token_url = 'https://connectapi.garmin.com/oauth-service/oauth/access_token'

client_key = 'c118028e-05f9-4ee6-bea0-e054d4e98cac'
client_secret = '6uUOIxYkaVCfzqjvR4mbWwjf398yQy7qRhP'

# obtain request token
oauth = OAuth1Session(client_key, client_secret=client_secret)
fetch_response = oauth.fetch_request_token(request_token_url)

resource_owner_key = fetch_response.get('oauth_token')
resource_owner_secret = fetch_response.get('oauth_token_secret')

# obtain authorization
authorization_url = oauth.authorization_url(base_authorization_url)

pass
