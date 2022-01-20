from sqlalchemy import create_engine, MetaData, Table, \
    Column, Integer, String, Text, DateTime, text, JSON
import os
import dotenv
from datetime import datetime
import pytz
import json

"""
see https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_core_creating_table.htm
"""
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

        # create the engine
        self.create_engine()
        self.create_tables()  # ok to run it since if tables exists it does nothing
        pass

    def test1(self):
        self.check_uat('def','abc')
        self.check_uat('xyz','abc')
        self.check_userid('xyz','newid')

    def create_engine(self):
        self.engine = create_engine(self.url, echo = True, future=True)
    
    def create_tables(self):
        # create the tables
        meta = MetaData()

        accounts = Table(
            'accounts', meta,
            Column('id', Integer, primary_key = True), 
            Column('userid', Text), 
            Column('uat', Text), 
            Column('secret', Text),
            Column('subject_id', Text),
            Column('register',Integer),
            Column('created_at',DateTime),
            Column('updated_at',DateTime)
        )

        garmindata = Table(
            'garmindata', meta, 
            Column('id', Integer, primary_key = True), 
            Column('userid', Text),
            Column('uat', Text), 
            Column('datatype', Text),
            Column('starttime', Integer),
            Column('offsettime', Integer),
            Column('started_at', DateTime),
            Column('d', JSON),
            Column('created_at',DateTime),
            Column('updated_at',DateTime),
        )

        # to add column
        # alter table garmindata add column started_at datetime after offsettime;
        meta.create_all(self.engine)

        pass

    def check_uat(self, uat, secret):
        """
        Checks if a UserAccessToken exists, if it doesn't then creates entry
        """
        conn = self.engine.connect()
        sql = f"select count(*) as count from accounts where uat like '{uat}';"
        result = conn.execute(text(sql))

        for row in result:
            count = row[0]

        if count==0:
            # insert a new row
            now = datetime.now(pytz.timezone(self.tz))

            # dd/mm/YY H:M:S
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

            sql = f"insert into accounts (uat, secret, created_at) \
                value('{uat}','{secret}','{dt_string}');"

            result = conn.execute(text(sql))
            conn.commit()

        pass

    def register_uat(self, uat, register=1):
        """
        Checks if uat exists 
        Then sets register to requested value
        """
        conn = self.engine.connect()
        sql = f"select count(*) as count from accounts where uat like '{uat}';"
        result = conn.execute(text(sql))

        for row in result:
            count = row[0]

        if count==1:
            # update register value
            now = datetime.now(pytz.timezone(self.tz))

            # dd/mm/YY H:M:S
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
            sql = f"update accounts set register = {register}, updated_at='{dt_string}' where uat like '{uat}';"
            result = conn.execute(text(sql))
            conn.commit()

        pass

    def check_userid(self, uat, userid):
        """
        Checks if a userid exists for this uat, if not then update 
        """
        conn = self.engine.connect()
        sql = f"select userid, uat from accounts where uat like '{uat}';"
        result = conn.execute(text(sql))
        olduserid = None

        for row in result:
            olduserid = row.userid

        if olduserid == None:
            # update
            now = datetime.now(pytz.timezone(self.tz))

            # dd/mm/YY H:M:S
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

            sql = f"update accounts set userid = '{userid}', updated_at='{dt_string}' where uat like '{uat}';"

            result = conn.execute(text(sql))
            conn.commit()

        pass

    def record_exists(self, uat, datatype, starttime):
        """
        Checks if a row exists for this uat, datatype and starttime 

        returns
        0 if no match and id of row if exists
        """
        conn = self.engine.connect()
        sql = f"select id, uat, datatype, starttime from garmindata where uat like '{uat}' and \
                datatype like '{datatype}' and starttime = {starttime};"
        result = conn.execute(text(sql))

        # initialize
        oldid = 0

        for row in result:
            oldid = row.id

        if oldid:
            id = oldid  # return the row number of match
        else:
            id = 0 # return 0 

        return id

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
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

        actual_dt_string = datetime.fromtimestamp(actualtime)

        # convert python object back into json
        json_object = json.dumps(jd, indent=4)
        conn = self.engine.connect()

        if idExists:
            # do update 
            sql = f"update garmindata set updated_at ='{dt_string}', d='{json_object}' where id={idExists};"
        else:
            sql = f"insert into garmindata (userid, uat, datatype, starttime, offsettime, started_at, created_at, d) \
                    value('{userid}','{uat}','{datatype}',{starttime},{actualtime},'{actual_dt_string}','{dt_string}','{json_object}');"

        result = conn.execute(text(sql))
        conn.commit()

        pass    
if __name__ == '__main__':
    db = Db()
