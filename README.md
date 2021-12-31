# garminrec

This is python flask app to receive data from Garmin Connect 
using their push notification.

This app also serves the information required by garmin.
1. callback
2. privacy
3. icon

## docker stuff
```
# build the container
sudo docker build -t garminrec .

# run the container at port 5005
sudo docker run -d -p 5005:5005 --restart unless-stopped garminrec
```
## software installation of authlib
```
pip install --upgrade pip
pip install Authlib Flask
```

## for oauthlib
```
pip install requests_oauthlib
pip install flask_oauthlib

```