
from datetime import datetime


"""
https://www.programiz.com/python-programming/datetime/timestamp-datetime

timestamp = datetime.timestamp(datetime.now())
dt_object = datetime.fromtimestamp(timestamp)
# convert dt_object to string with strftime()
date_time = dt_object.strftime("%Y-%m-%d, %H:%M:%S")

"""
timestamp = 1641271080 -21600

def ts_to_dt(timestamp, offset=-21600, format="%Y-%m-%d %H:%M:%S"):
    ts = timestamp + offset
    dt_object = datetime.fromtimestamp(ts)
    dt_string = dt_object.strftime(format)
    return dt_string, dt_object



pass