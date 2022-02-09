# garminrec

This is python flask app to receive data from Garmin Connect 
using their push notification.

This app also serves the information required by garmin.
1. callback
2. privacy
3. icon

## excellent oauth python library with interactive code

from https://requests-oauthlib.readthedocs.io/en/latest/oauth1_workflow.html


## docker stuff
```
# build the container
sudo docker build -t garminrec:1.05 .

# to run on production network on lnpitask.umn.edu
sudo docker run -d -p 5005:5005 --network=production --restart unless-stopped garminrec:1.05

# run the container at port 5005  azure
sudo docker run -d -p 5005:5005 --network=host --restart unless-stopped garminrec:1.02

# to run without detached mode for testing with db running on localhost
sudo docker run --network=host -p 5005:5005 garminrec:1.05
```

## developing using a docker container
https://code.visualstudio.com/docs/containers/debug-python

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

## reference materials for using mysql with json

https://www.digitalocean.com/community/tutorials/working-with-json-in-mysql

sqlalchemy

https://pypi.org/project/sqlalchemy-json/

Links for different resources on garmin
https://www.programmableweb.com/api/garmin-connect-rest-api

link for garmin instructions on how to remove third-party site access from garmin
connect account

https://support.garmin.com/en-US/?faq=J1LFILJV3z7SGvwIIb95X6



## using environment variables when building docker containers
https://stackoverflow.com/questions/19537645/get-environment-variable-value-in-dockerfile

In dockerfile

ARG requestdomain

Access it

ENV requestdomain=$requestdomain

pass it during build

docker build --build-arg request_domain=mydomain Dockerfile

## how to use .env to set env variable in shell

Entries in the .env file have to be like this:

db_name=garmindb

https://stackoverflow.com/questions/43267413/shell-how-to-set-environment-variables-from-env-file

https://stackoverflow.com/questions/61693804/dockerfile-is-there-any-way-to-read-variables-from-env-file

set -a # automatically export all variables
source .env
set +a

## accessing mysql on localhost from container
https://www.cloudsavvyit.com/14114/how-to-connect-to-localhost-within-a-docker-container/

This allows access to localhost from container
*** docker run -d --network=host my-container:latest

## how to add form in Flask - use this for callback in order to add a subject_id
https://python-adv-web-apps.readthedocs.io/en/latest/flask_forms.html

## sqlalchemy info
https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/#

## to enable python38 on rhel7
https://developers.redhat.com/blog/2018/08/13/install-python3-rhel#tl_dr

1. subscription-manager repos --enable rhel-7-server-optional-rpms \
  --enable rhel-server-rhscl-7-rpms
2. yum -y install @development
3. yum -y install rh-python38
4. # to enable
   1. scl enable rh-python36 bash  # got error 
   2.  (28, 'Operation too slow. Less than 1000 bytes/sec transferred the last 30 seconds')
Trying other mirror.

## trying direct install of python38
https://tecadmin.net/install-python-3-8-centos/

Got error
 wget https://www.python.org/ftp/python/3.8.12/Python-3.8.12.tgz
--2022-01-03 06:07:00--  https://www.python.org/ftp/python/3.8.12/Python-3.8.12.tgz
Resolving www.python.org (www.python.org)... 199.232.28.223, 2a04:4e42:44::223
Connecting to www.python.org (www.python.org)|199.232.28.223|:443...

Had to download on another machine and transfer the tgz file

Then did install

## to resize the umn logo to 150x150

https://onlinepngtools.com/resize-png

## garmin tools for testing endpoints

https://apis.garmin.com/tools/login

## problem with losing connection and needing rollback error

potential solution

https://stackoverflow.com/questions/29755228/sqlalchemy-mysql-lost-connection-to-mysql-server-during-query

https://docs.sqlalchemy.org/en/13/core/pooling.html#disconnect-handling-pessimistic

Use of ping
engine = create_engine("mysql+pymysql://user:pw@host/db", pool_pre_ping=True)

Can also use contextmanager
https://docs.sqlalchemy.org/en/13/orm/session_basics.html#when-do-i-construct-a-session-when-do-i-commit-it-and-when-do-i-close-it

```python

from contextlib import contextmanager

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def run_my_program():
    with session_scope() as session:
        ThingOne().go(session)
        ThingTwo().go(session)
        
```

