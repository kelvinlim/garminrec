from sqlalchemy import create_engine, MetaData, Table, \
    Column, Integer, String, Text, DateTime, text
import os
import dotenv
from datetime import datetime

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

        self.url = f"{db_dialect}://{db_user}:{db_pw}@{db_host}/{db_name}"

        # create the engine
        self.create_engine()
        self.create_tables()

        pass

    def test1(self):
        self.check_uat('def','abc')
        self.check_uat('xyz','abc')

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
            Column('creation',DateTime)
        )

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
            now = datetime.now()

            # dd/mm/YY H:M:S
            dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

            sql = f"insert into accounts (uat, secret, creation) \
                value('{uat}','{secret}','{dt_string}');"

            result = conn.execute(text(sql))
            conn.commit()

        pass

if __name__ == '__main__':
    db = Db()
