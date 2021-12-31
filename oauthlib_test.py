# from https://requests-oauthlib.readthedocs.io/en/latest/oauth1_workflow.html

import requests_oauthlib

from dotenv import load_dotenv

# Using OAuth1Session
from requests_oauthlib import OAuth1Session

load_dotenv()  # take environment variables from .env.

request_token_url = 'https://connectapi.garmin.com/oauth-service/oauth/request_token'
base_authorization_url = 'https://connect.garmin.com/oauthConfirm'
access_token_url = 'https://connectapi.garmin.com/oauth-service/oauth/access_token'

# TODO switch to using dot_env
client_key = 'c118028e-05f9-4ee6-bea0-e054d4e98cac'
client_secret = '6uUOIxYkaVCfzqjvR4mbWwjf398yQy7qRhP'

"""
1. Obtain a request token which will identify you (the client) 
in the next step. At this stage you will only need your 
client key and secret.
"""
# obtain request token
oauth = OAuth1Session(client_key, client_secret=client_secret)
fetch_response = oauth.fetch_request_token(request_token_url)

resource_owner_key = fetch_response.get('oauth_token')
resource_owner_secret = fetch_response.get('oauth_token_secret')

"""
2. Obtain authorization from the user (resource owner) to access 
their protected resources (images, tweets, etc.). This is commonly 
done by redirecting the user to a specific url to which you add 
the request token as a query parameter. 
Note that not all services will give you a verifier even if 
they should. Also the oauth_token given here will be the same 
as the one in the previous step.
"""
# obtain authorization
authorization_url = oauth.authorization_url(base_authorization_url)

print('Please go here and authorize,', authorization_url)

redirect_response = input('Paste the full redirect URL here: ')
oauth_response = oauth.parse_authorization_response(redirect_response)

"""
This gets returned
for callback
https://lnpitest.northcentralus.cloudapp.azure.com/garminrec/callback?oauth_token=c320eef5-cd50-4baa-8c3a-adf129b71ede&oauth_verifier=qDrm812Aa7

"""

#get the verifier  
# do this as part of the callback
verifier = oauth_response.get('oauth_verifier')

"""

3. Obtain an access token from the OAuth provider. 
Save this token as it can be re-used later. 
In this step we will re-use most of the credentials obtained 
up til this point.
"""

# Using OAuth1Session
# do with callback
oauth = OAuth1Session(client_key,
                          client_secret=client_secret,
                          resource_owner_key=resource_owner_key,
                          resource_owner_secret=resource_owner_secret,
                          verifier=verifier)
oauth_tokens = oauth.fetch_access_token(access_token_url)
"""
{
    "oauth_token": "6253282-eWudHldSbIaelX7swmsiHImEL4KinwaGloHANdrY",
    "oauth_token_secret": "2EEfA6BG3ly3sR3RjE0IBSnlQu4ZrUzPiYKmrkVU"
}
"""

resource_owner_key = oauth_tokens.get('oauth_token')
resource_owner_secret = oauth_tokens.get('oauth_token_secret')



pass
