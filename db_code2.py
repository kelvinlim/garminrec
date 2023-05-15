from re import A
from pytz import timezone
from sqlalchemy import create_engine, MetaData, Table, \
    Column, Integer, String, Text, DateTime, text, JSON,BIGINT, \
    Boolean, ForeignKey

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from contextlib import contextmanager

import os
import dotenv
from datetime import datetime
import pytz
import json

"""
db code version that uses the usercode in accounts

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
    account_id = Column(Integer, ForeignKey('accounts.id'))

class Accounts(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    oauth_token = Column(Text)
    entry_code = Column(Text)
    userid = Column(Text)
    uat = Column(Text)
    secret = Column(Text)
    study_info = Column(Text)
    subject_info = Column(Text)
    register = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    garmindata = relationship("Garmindata")
    studi_id = Column(BIGINT, default=1)

    # alter table accounts add column oauth_token text after id;
# class Study(Base):
#     __tablename__ = 'garmin_study'
#     id = Column(Integer, primary_key=True)   
#     label = Column(Text)
#     description = Column(Text)
#     study_active = Column(Boolean)
#     grid_study = Column(Integer)
#     pi_x500 = Column(Text)
#     json_data = Column(JSON)
#     accounts = relationship("Accounts")
#     # users many to many


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
        #self.create_session()

        #self.create_tables()  # ok to run it since if tables exists it does nothing
        #self.test1()
        pass


    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        Session = sessionmaker(bind = self.engine)
        session = Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


    def test1(self):
        # uat exists
        #self.check_uat('37cd115c-b230-4f1a-a38c-7bdd16565ab0','abcd')
        # uat doesn't exist
        self.new_uat('def','abc','xyz')
        # change the register setting to 0
        self.register_uat('def',register=0)
        # check if userid exists
        self.check_userid('def','xyz')
        # check if record exists
        #self.record_exists()
        # delete it
        with self.session_scope() as session:
            session.query(Accounts).filter(Accounts.uat=='def').delete()
            session.commit()
        pass

    def create_engine(self):
        self.engine = create_engine(self.url, echo = True, future=True, pool_pre_ping=True)
        # pool_pre_ping to  deal with disconnection problem
        # https://docs.sqlalchemy.org/en/13/core/pooling.html#disconnect-handling-pessimistic

    '''         
    def create_session(self):
        "Create a session"
        Session = sessionmaker(bind = self.engine)
        self.session = Session()
    '''
    
    def create_tables(self):
        # create the tables
        Base.metadata.create_all(self.engine)
        pass

    def update_oauth_token_id(self, id, oauth_token):
        """
        Update the account specified by id with oauth_token
        """

        with self.session_scope() as session:
            res = session.query(Accounts).filter(Accounts.id==id).first()

            if res != None:
                # update the row
                now = datetime.now(pytz.timezone(self.tz))
                # dd/mm/YY H:M:S
                dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

                # update the fields
                res.oauth_token = oauth_token
                res.updated_at = dt_string
                res.created_at = dt_string
   
                session.commit()

            pass
    def new_uat(self, uat, secret, oauth_token):
        """
        Update the account with oauth_token with the uat and secret
        """

        with self.session_scope() as session:
            res = session.query(Accounts).filter(Accounts.oauth_token==oauth_token).first()

            if res != None:
                # update the row
                now = datetime.now(pytz.timezone(self.tz))
                # dd/mm/YY H:M:S
                dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

                # update the fields
                res.uat = uat
                res.secret = secret
                res.updated_at = dt_string
                #res.register = 1

                session.commit()

            pass
    
    '''
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
    '''

    def register_uat(self, uat, register=1):
        """
        Checks if uat exists 
        Then sets register to requested value
        """

        
        with self.session_scope() as session:

            # not using .first with res[0] gave inconsistent results - would set date but not register
            res = session.query(Accounts).filter(Accounts.uat==uat).first()

            if res != None:
                # update register value
                now = datetime.now(pytz.timezone(self.tz))
                # dd/mm/YY H:M:S
                dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                res.updated_at=dt_string
                res.register=register

                session.commit()

                pass

    def entry_code_exists(self, entry_code):
        """
        Checks if entrycode exists 
        returns id, else 0, register status
        """

        with self.session_scope() as session:

            # not using .first with res[0] gave inconsistent results - would set date but not register
            res = session.query(Accounts).filter(Accounts.entry_code==entry_code).first()
            
            if res:
                id = res.id
                register = res.register
            else:
                id = 0
                register = 0

            return id, register

    def check_userid(self, uat, userid):
        """
        Checks if a userid exists for this uat, if not then update 
        """

        with self.session_scope() as session:
            res = session.query(Accounts).filter(Accounts.uat==uat)

            if res.count()==1 and not res[0].userid:
                # update userid  value
                now = datetime.now(pytz.timezone(self.tz))
                # dd/mm/YY H:M:S
                dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                
                res[0].userid = userid
                res[0].updated_at = dt_string
                session.commit()

            pass

    def record_exists(self, uat, datatype, starttime):
        """
        Checks if a row exists for this uat, datatype and starttime 

        returns
        0 if no match and id of row if exists
        """
        with self.session_scope() as session:
            res = session.query(Garmindata).filter(
                (Garmindata.uat == uat),
                (Garmindata.datatype == datatype),
                (Garmindata.starttime == starttime)
            )

            if res.count() == 1:
                id = res[0].id
            else:
                id = 0
            return id

    def account_exists(self, uat):
        """
        Checks if a row exists for this uat  in Accounts 

        returns
        0 if no match and id of row if exists
        """
        with self.session_scope() as session:
            res = session.query(Accounts).filter(
                (Accounts.uat == uat)
            )

            if res.count() == 1:
                id = res[0].id
            else:
                id = 0
            return id
    
    def test_account_exists(self):
        """
        Test the account_exists method
        """
        uat = '11c5b917-64ab-4276-89e7-6947efd2c6e0'
        userid = '6f568484-0e46-4c74-ba15-72a9dbaea3b1'

        assert self.account_exists(uat) > 0, \
            f"Expect return primary key, got zero"
        
        # change the uat so should return zero
        uat += 'extra'
        assert self.account_exists(uat) == 0, \
            f"No match, so expect zero"        
        pass

    def add_oauth_token(self, oauth_token,study_info, subject_info):
        "Add oauth_token, subject_info and study_info to accounts table as first step"

        with self.session_scope() as session:
            res = session.query(Accounts).filter(Accounts.oauth_token==oauth_token).first()
            if res == None:
                # add record if it doesn't exist previously
                ad = Accounts(
                        oauth_token = oauth_token,
                        study_info = study_info,
                        subject_info = subject_info
                )
                session.add(ad)
                session.commit()

    def add_raw_data_old(self, jd):
        """
        
        # old version assumes same user for all data
        
        add raw data to database
        1. get the type of data from key
        2. need to get the userid and uat for the data
        3. get the foreign key based on userid and uat
        4. get the starttime
        """

        # get datatype
        datatype = list(jd.keys())[0]

        # get the userid and uat from the first row of data
        userid = jd[datatype][0]['userId']
        uat = jd[datatype][0]['userAccessToken']

        account_fk = self.account_exists(uat)

        if datatype in ['epochs','stressDetails','dailies','sleeps','pulseox','activities',
                        'healthSnapshot','allDayRespiration','hrv']:
                         
            starttime = jd[datatype][0]['startTimeInSeconds']
            offset = jd[datatype][0]['startTimeOffsetInSeconds']
            actualtime = starttime + offset
        
        elif datatype in ['activityDetails']:
            starttime = jd[datatype][0]['summary']['startTimeInSeconds']
            offset = jd[datatype][0]['summary']['startTimeOffsetInSeconds']
            actualtime = starttime + offset

        elif datatype in ['bodyComps']:
            starttime = jd[datatype][0]['measurementTimeInSeconds']
            offset = jd[datatype][0]['measurementTimeOffsetInSeconds']
            actualtime = starttime + offset

        elif datatype in ['userMetrics']:
            # just have calendarDate, not TimeInSeconds eg. '2022-02-08'
            cal_date = jd['userMetrics'][0]['calendarDate']
            year,month,day = cal_date.split('-')
            t = datetime(int(year),int(month),int(day))
            starttime = int(t.timestamp())
            offset = 0
            actualtime = starttime + offset
            pass

        elif datatype in ['moveIQActivities']:
            starttime = jd[datatype][0]['startTimeInSeconds']
            # offsetInSeconds is -2160000 instead of -21600 so divide by 100
            offset = jd[datatype][0]['offsetInSeconds']/100
            actualtime = starttime + offset
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
 
        with self.session_scope() as session:
            if idExists:
                # do update of existing record
                res = session.query(Garmindata).filter(Garmindata.id==idExists)
                res[0].updated_at = now_dt_string
                res[0].d = jd
                #sql = f"update garmindata set updated_at ='{now_dt_string}', d='{json_object}' where id={idExists};"                pass
            else:
                gd =Garmindata(
                    userid=userid,
                    uat=uat,
                    datatype=datatype,
                    starttime=starttime,
                    offsettime=actualtime,
                    started_at=actual_dt_string,
                    created_at=now_dt_string,
                    updated_at=now_dt_string,
                    d=jd,
                    account_id=account_fk
                )
                session.add(gd)
                #sql = f"insert into garmindata (userid, uat, datatype, starttime, offsettime, started_at, created_at, d) \
                #        value('{userid}','{uat}','{datatype}',{starttime},{actualtime},'{actual_dt_string}','{nowdt_string}','{json_object}');"
                pass
            
            session.commit()

            pass    


    def add_raw_data(self, jd):
        """
        add raw data to database
        1. loop through each datatype get the type of data from key
            2. loop through each data entry
                need to get the userid and uat for the data
                get the foreign key based on userid and uat
                get the starttime
        """

        # get datatype
        #datatype = list(jd.keys())[0]
        for datatype in jd.keys():

            for jdata in jd[datatype]:
                # get the userid and uat from the first row of data
                userid = jdata['userId']
                uat = jdata['userAccessToken']

                account_fk = self.account_exists(uat)

                if datatype in ['epochs','stressDetails','dailies','sleeps','pulseox','activities',
                                'healthSnapshot','allDayRespiration','hrv']:
                                
                    starttime = jdata['startTimeInSeconds']
                    offset = jdata['startTimeOffsetInSeconds']
                    actualtime = starttime + offset
                
                elif datatype in ['activityDetails']:
                    starttime = jdata['summary']['startTimeInSeconds']
                    offset = jdata['summary']['startTimeOffsetInSeconds']
                    actualtime = starttime + offset

                elif datatype in ['bodyComps']:
                    starttime = jdata['measurementTimeInSeconds']
                    offset = jdata['measurementTimeOffsetInSeconds']
                    actualtime = starttime + offset

                elif datatype in ['userMetrics']:
                    # just have calendarDate, not TimeInSeconds eg. '2022-02-08'
                    cal_date = jd['userMetrics'][0]['calendarDate']
                    year,month,day = cal_date.split('-')
                    t = datetime(int(year),int(month),int(day))
                    starttime = int(t.timestamp())
                    offset = 0
                    actualtime = starttime + offset
                    pass

                elif datatype in ['moveIQActivities']:
                    starttime = jdata['startTimeInSeconds']
                    # offsetInSeconds is -2160000 instead of -21600 so divide by 100
                    offset = jdata['offsetInSeconds']/100
                    actualtime = starttime + offset
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
        
                # create a new data structure with the datatype as key
                # this preserves same data structure that comes from garmin
                newdata = {}
                newdata[datatype] = [ jdata ]
                
                with self.session_scope() as session:
                    if idExists:
                        # do update of existing record
                        res = session.query(Garmindata).filter(Garmindata.id==idExists)
                        res[0].updated_at = now_dt_string
                        res[0].d = newdata
                        #sql = f"update garmindata set updated_at ='{now_dt_string}', d='{json_object}' where id={idExists};"                pass
                    else:
                        gd =Garmindata(
                            userid=userid,
                            uat=uat,
                            datatype=datatype,
                            starttime=starttime,
                            offsettime=actualtime,
                            started_at=actual_dt_string,
                            created_at=now_dt_string,
                            updated_at=now_dt_string,
                            d=newdata,
                            account_id=account_fk
                        )
                        session.add(gd)
                        #sql = f"insert into garmindata (userid, uat, datatype, starttime, offsettime, started_at, created_at, d) \
                        #        value('{userid}','{uat}','{datatype}',{starttime},{actualtime},'{actual_dt_string}','{nowdt_string}','{json_object}');"
                        pass
                    
                    session.commit()

                    pass    
        
if __name__ == '__main__':
    db = Db()
    db.test_account_exists()
    pass