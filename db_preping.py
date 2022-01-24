from re import A
from pytz import timezone
from sqlalchemy import create_engine, MetaData, Table, \
    Column, Integer, String, Text, DateTime, text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
import dotenv
from datetime import datetime
import pytz
import json

"""
see https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_core_creating_table.htm
"""

Base = declarative_base()

# define the tables
class Garmindata(Base):
    __tablename__ = 'garmindata'
    id = Column(Integer, primary_key=True)
    userid = Column(Text)
    uat = Column(Text)
    datatype = Column(Text)
    starttime = Column(Integer)
    offsettime = Column(Integer)
    started_at = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    d = Column(JSON)

class Accounts(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    oauth_token = Column(Text)
    userid = Column(Text)
    uat = Column(Text)
    secret = Column(Text)
    study_id = Column(Text)
    subject_id = Column(Text)
    register = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    # alter table accounts add column oauth_token text after id;

class Db:

    def __init__(self):

        # create the url for sqlalchemy
        db_user = os.getenv('db_user')
        db_pw = os.getenv('db_pw')
        db_host = os.getenv('db_host')
        db_name = os.getenv('db_name')
        db_dialect = os.getenv('db_dialect')   
        db_port = os.getenv('db_port')       
        self.tz = os.getenv('tz')       

        # add port for cnc2
        self.url = f"{db_dialect}://{db_user}:{db_pw}@{db_host}:{db_port}/{db_name}"

        # create the engine and session
        self.create_engine()
        self.create_session()

        #self.create_tables()  # ok to run it since if tables exists it does nothing
        #self.test1()
        pass

    def test1(self):
        # uat exists
        self.check_uat('37cd115c-b230-4f1a-a38c-7bdd16565ab0','abcd')
        # uat doesn't exist
        self.check_uat('def','abc')
        # change the register setting to 0
        self.register_uat('def',register=0)
        # check if userid exists
        self.check_userid('def','xyz')
        # check if record exists
        #self.record_exists()
        # delete it
        self.session.query(Accounts).filter(Accounts.uat=='def').delete()
        self.session.commit()
        pass

    def create_engine(self):
        self.engine = create_engine(self.url, echo = True, future=True, pool_pre_ping=True)
        # pool_pre_ping to  deal with disconnection problem
        # https://docs.sqlalchemy.org/en/13/core/pooling.html#disconnect-handling-pessimistic
             
    def create_session(self):
        "Create a session"
        Session = sessionmaker(bind = self.engine)
        self.session = Session()
    
    def create_tables(self):
        # create the tables
        Base.metadata.create_all(self.engine)
        pass

    def new_uat(self, uat, secret, oauth_token):
        """
        Update the account with oauth_token with the uat and secret
        """
        res = self.session.query(Accounts).filter(Accounts.oauth_token==oauth_token).first()

        if res != None:
            # update the row
            now = datetime.now(pytz.timezone(self.tz))
            # dd/mm/YY H:M:S
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

            # update the fields
            res.uat = uat
            res.secret = secret
            res.updated_at = dt_string
            res.register = 1

            self.session.commit()

        pass
    
    def check_uat_pre_study_id(self, uat, secret):
        """
        Checks if a UserAccessToken exists, if it doesn't then creates entry
        """
        count = self.session.query(Accounts).filter(Accounts.uat==uat).count()

        if count==0:
            # insert a new row
            now = datetime.now(pytz.timezone(self.tz))
            # dd/mm/YY H:M:S
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

            new_uat = Accounts( uat=uat,
                                secret=secret,
                                register=1,
                                created_at=dt_string
                                )
            
            self.session.add(new_uat)
            self.session.commit()

        pass

    def register_uat(self, uat, register=1):
        """
        Checks if uat exists 
        Then sets register to requested value
        """

        res = self.session.query(Accounts).filter(Accounts.uat==uat)

        if res.count==1:
            # update register value
            now = datetime.now(pytz.timezone(self.tz))
            # dd/mm/YY H:M:S
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            res[0].register=register
            res[0].updated_at=dt_string
            self.session.commit()

        pass

    def check_userid(self, uat, userid):
        """
        Checks if a userid exists for this uat, if not then update 
        """
        res = self.session.query(Accounts).filter(Accounts.uat==uat)

        if res.count()==1 and res[0].userid == None:
            # update userid  value
            now = datetime.now(pytz.timezone(self.tz))
            # dd/mm/YY H:M:S
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            
            res[0].userid = userid
            res[0].updated_at = dt_string
            self.session.commit()

        pass

    def record_exists(self, uat, datatype, starttime):
        """
        Checks if a row exists for this uat, datatype and starttime 

        returns
        0 if no match and id of row if exists
        """

        res = self.session.query(Garmindata).filter(
            (Garmindata.uat == uat),
            (Garmindata.datatype == datatype),
            (Garmindata.starttime == starttime)
        )

        if res.count() == 1:
            id = res[0].id
        else:
            id = 0
        return id

    def add_oauth_token(self, oauth_token,study_id, subject_id):
        "Add oauth_token, subject_id and study_id to accounts table as first step"

        res = self.session.query(Accounts).filter(Accounts.oauth_token==oauth_token).first()
        if res == None:
            # add record if it doesn't exist previously
            ad = Accounts(
                    oauth_token = oauth_token,
                    study_id = study_id,
                    subject_id = subject_id
            )
            self.session.add(ad)
            self.session.commit()

    def add_raw_data(self, jd):
        """
        add raw data to database
        1. get the type of data from key
        2. need to get the userid and uat for the data
        3. get the startime
        """

        # get datatype
        datatype = list(jd.keys())[0]

        # get the userid and uat from the first row of data
        userid = jd[datatype][0]['userId']
        uat = jd[datatype][0]['userAccessToken']

        if datatype in ['epochs','stressDetails','dailies','sleeps','pulseox','activities',
                        'healthSnapshot','allDayRespiration']:
                         
            starttime = jd[datatype][0]['startTimeInSeconds']
            offset = jd[datatype][0]['startTimeOffsetInSeconds']
            actualtime = starttime + offset
        
        elif datatype in ['activityDetails']:
            starttime = jd[datatype][0]['summary']['startTimeInSeconds']
            offset = jd[datatype][0]['summary']['startTimeOffsetInSeconds']
            actualtime = starttime + offset

            pass
        else:
            starttime = 0
            actualtime = 0

        # update account info with userid
        self.check_userid( uat, userid)


        # check if row exists
        idExists = self.record_exists(uat, datatype, starttime)

        now = datetime.now(pytz.timezone(self.tz))
        now_dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

        # just give raw time without timezone
        # pytz.timezone('US/Central')
        actual_dt_string = datetime.fromtimestamp(actualtime, timezone(self.tz) ).strftime("%Y-%m-%d %H:%M:%S")

        # convert python object back into json
        json_object = json.dumps(jd, indent=4)

        if idExists:
            # do update of existing record
            res = self.session.query(Garmindata).filter(Garmindata.id==idExists)
            res[0].updated_at = now_dt_string
            res[0].d = json_object
            #sql = f"update garmindata set updated_at ='{now_dt_string}', d='{json_object}' where id={idExists};"
        else:
            gd =Garmindata(
                userid=userid,
                uat=uat,
                datatype=datatype,
                starttime=starttime,
                offsettime=actualtime,
                started_at=actual_dt_string,
                created_at=now_dt_string,
                d=json_object
            )
            self.session.add(gd)
            #sql = f"insert into garmindata (userid, uat, datatype, starttime, offsettime, started_at, created_at, d) \
            #        value('{userid}','{uat}','{datatype}',{starttime},{actualtime},'{actual_dt_string}','{nowdt_string}','{json_object}');"
            
        self.session.commit()

        pass    
if __name__ == '__main__':
    db = Db()
