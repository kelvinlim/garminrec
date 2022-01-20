#! /usr/bin/env python

"""
Code to update the started_at field in the garmindata table.

Test out the ORM sqlalchemy feature to make it easier

Using following as template

https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_orm_declaring_mapping.htm

"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
import dotenv
import pytz
import os
from datetime import datetime

# create the url for sqlalchemy
db_user = os.getenv('db_user')
db_pw = os.getenv('db_pw')
db_host = os.getenv('db_host')
db_name = os.getenv('db_name')
db_dialect = os.getenv('db_dialect')   
db_port = os.getenv('db_port')       
tz = os.getenv('tz')       

# add port for cnc2
url = f"{db_dialect}://{db_user}:{db_pw}@{db_host}:{db_port}/{db_name}"

engine = create_engine(url, echo = True)

Base = declarative_base()

# define the table
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

# create table
# Base.metadata.create_all(engine)

# create a session
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind = engine)
session = Session()


result = session.query(Garmindata).all()

for row in result:
    print(f"id: {row.id} offset:{row.offsettime} started_at: {row.started_at}")
    # only update if row.offsettime > 0
    if row.offsettime > 0:
        dt_string = datetime.fromtimestamp(row.offsettime)
        #r = session.query(Garmindata).get(row.id)
        #r.started_at = dt_string  # update the string
        row.started_at = dt_string  # update the datetime
        session.commit()

result = session.query(Garmindata).all()

print('After Update')
for row in result:
    print(f"id: {row.id} datatype: {row.datatype} offset:{row.offsettime} started_at: {row.started_at}")



pass