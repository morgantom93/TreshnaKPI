"""GET request to Live Agent Desk REST API for Performance Report for KPI Dashboard
    Written by Tom Morgan on 2019-05-16
"""

import request
import psycopg2
import json
from datetime import date, timedelta
import requests

def get_report(day):

    # Setup variables for correct API call
    yesterday = date.today() - timedelta(days=day)
    yesterday = str(yesterday.strftime('%Y-%m-%d'))
    # LADesk API v1 key
    apikey = '###'

    url = 'https://###/api/reports/performance?date_from={0}&date_to={0}&apikey={1}&columns=answers,newAnswerAvgTime,nextAnswerAvgTime,i_messages,created_tickets,resolved_tickets'.format(yesterday,apikey)

    response = requests.get(url)

    if not response.json():                    
        return null
    return(response.json().get("response", {} ).get("performance", [{}] ) [0])




def write_to_database(day, response):
  """Writes the returned Google Analytics data to a PostgreSQL database"""

  """ PSQL commands to create the database:
        # CREATE TABLE ladeskdata (id serial primary key, date DATE, data JSONB);
        # GRANT ALL ON ladeskdata to user;
        # GRANT ALL ON SEQUENCE ladeskdata_id_seq TO user;
  """

  # Parameters used to connect to the database 
  params = {"host":"localhost",
            "port":"5432",
            "database":"postgres", 
            "user":"###", 
            "password":"###"}

  # Connect to the database with the parameters above
  conn = psycopg2.connect(**params)
  print("PostgreSQL connection is open")

  # Connect the cursor
  cursor = conn.cursor()
  
  # INSERT the Google Analytics data with date into the database
  print("INSERTING into the database now")
  cursor.execute("INSERT INTO ladeskdata ( date, data ) VALUES ( (CURRENT_DATE - %s)::DATE , %s)",(day, json.dumps(response),))
  
  # Make the changes to the database persistent
  conn.commit()

  # Close the connection with the database
  cursor.close()
  conn.close()
  print("PostgreSQL connection is closed")


def lastmonths():
    day = 1

    while day != 91:
        print(day)
        ladesk_data = get_report(day)
        write_to_database(day, ladesk_data)
        day+=1




def main():
  lastmonths()

if __name__ == '__main__':
  main()
