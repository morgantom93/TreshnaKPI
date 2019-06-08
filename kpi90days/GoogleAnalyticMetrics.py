"""GymMaster Google Analytics Reporting API V4."""
"""Taken from Google Analytics Reporting API v4 tutorial, write_to_databae function written by Tom Morgan on 2019-05-14"""

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import psycopg2
import json
from datetime import date, timedelta

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = '/home/gymmaster/kpi/kpi90days/client_secrets.json'
# VIEW_ID is the view on Google Analytics used to gather data
VIEW_ID = '###'


def initialize_analyticsreporting():
  """Initializes an Analytics Reporting API V4 service object.

  Returns:
    An authorized Analytics Reporting API V4 service object.
  """
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
      KEY_FILE_LOCATION, SCOPES)

  # Build the service object.
  analytics = build('analyticsreporting', 'v4', credentials=credentials)

  return analytics


def get_report(day, analytics):
  """Queries the Analytics Reporting API V4.

  Args:
    analytics: An authorized Analytics Reporting API V4 service object.
  Returns:
    The Analytics Reporting API V4 response.
  """
  timeselect = date.today() - timedelta(days=day)
  timeselect = str(timeselect.strftime('%Y-%m-%d'))

  return analytics.reports().batchGet(
      body={
		"reportRequests": [
			{
				"viewId": "###",
				"dateRanges": [
					{
						"startDate": timeselect,
						"endDate": timeselect
					}
				],
				"metrics": [
					{"expression": "ga:sessions"},
					{"expression": "ga:pageviewsPerSession"},
					{"expression": "ga:avgSessionDuration"},
					{"expression": "ga:users"},
					{"expression": "ga:newUsers"},
					{"expression": "ga:avgTimeOnPage"},
					{"expression": "ga:avgPageLoadTime"},
					{"expression": "ga:avgServerResponseTime"}
				]
				}
			]
		}
  ).execute()


def print_response(response):
  """Parses and prints the Analytics Reporting API V4 response.

  Args:
    response: An Analytics Reporting API V4 response.
  """
  for report in response.get('reports', []):
    columnHeader = report.get('columnHeader', {})
    dimensionHeaders = columnHeader.get('dimensions', [])
    metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])

    for row in report.get('data', {}).get('rows', []):
      dimensions = row.get('dimensions', [])
      dateRangeValues = row.get('metrics', [])
      
      # Dict to store Google Analytics data until writing to database
      googleanalyticsjsondump = {}
      
      for i, values in enumerate(dateRangeValues): 
        for metricHeader, value in zip(metricHeaders, values.get('values')):
		  # strips off leading string of "ga:" from the metric names
          googleanalyticsjsondump.update({metricHeader.get('name')[3:] : value})

      return(googleanalyticsjsondump)

def write_to_database(day, response):
  """Writes the returned Google Analytics data to a PostgreSQL database"""

  """ PSQL commands to create the database:
        # CREATE TABLE googleanalyticsdata (id serial primary key, date DATE, data JSONB);
        # GRANT ALL ON googleanalyticsdata to user;
        # GRANT ALL ON SEQUENCE googleanalyticsdata_id_seq TO user;
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
  cursor.execute("INSERT INTO googleanalyticsdata ( date, data ) VALUES ( CURRENT_DATE - %s , %s)",(day, json.dumps(response),))
  
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
        analytics = initialize_analyticsreporting()
        response = get_report(day, analytics)
        google_response = print_response(response)
        write_to_database(day, google_response)
        day+=1



def main():
  lastmonths()

if __name__ == '__main__':
  main()
