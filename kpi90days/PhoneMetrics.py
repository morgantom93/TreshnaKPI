"""Retrieves metrics from Treshna phone system database for KPI dashboards
    Written by Tom Morgan on 2019-05-21
"""

import request
import psycopg2
import psycopg2.extras
import json
from datetime import date, timedelta
import requests

def read_from_database(day):
    """Reads data from the phone system database for the KPI dashboards"""

    # Parameters used to connect to the database 
    params = {"host":"###",
                "port":"###",
                "database":"###", 
                "user":"###", 
                "password":"###"}

    # Connect to the database with the parameters above
    conn = psycopg2.connect(**params)
    print("PostgreSQL connection is open")

    # Connect the cursor
    cursor = conn.cursor()

    # SELECTING data from the database
    print("SELECTING from the database now")

    # Selecting the average duration of answered calls longer than a minute from yesterday
    query = """  SELECT 
                            AVG(duration)::INT 
                        FROM 
                            cdr     
                        WHERE 
                            disposition = 'ANSWERED' AND 
                            calldate >= ( CURRENT_DATE - {0} )  AND
                            calldate <= ((CURRENT_DATE - {0}) + '23 hours, 59 minutes, 59 seconds'::INTERVAL) AND 
                            duration > 60
                    """.format(day)
    cursor.execute(query)
    returned_data = cursor.fetchone()

    if str(returned_data[0]) == 'None':
        main_data = {'avgDuration':'0'}
    else:
        main_data = {'avgDuration' : str(returned_data[0])}

    # Selecting the count of voicemails from yesterday
    query = """  SELECT 
                            COUNT(*) 
                        FROM 
                            cdr 
                        WHERE 
                            char_length(src::text) > 4 AND 
                            lastapp ILIKE '%voicemail%' AND 
                            calldate >= ( CURRENT_DATE - {0} )  AND
                            calldate <= ((CURRENT_DATE - {0}) + '23 hours, 59 minutes, 59 seconds'::INTERVAL)
                    """.format(day)
    cursor.execute(query)
    returned_data = cursor.fetchone()
    main_data.update( {'voicemailCount' : str(returned_data[0]) } )

    # Selecting the average queue time on calls from yesterday
    clid='{D}'
    query =  """WITH call_times AS (
                            SELECT
                                (MAX(calldate) - MIN(calldate)) AS "queue_time",
                                src,
                                MIN(disposition)
                            FROM
                                cdr
                            WHERE
                                lastapp ILIKE '%queue%' AND
                                calldate >= ( CURRENT_DATE - {0} )  AND
                                calldate <= ((CURRENT_DATE - {0}) + '23 hours, 59 minutes, 59 seconds'::INTERVAL) AND
                                clid NOT LIKE '%{1}%'
                            GROUP BY uniqueid, src
                            )
                        SELECT avg(queue_time) FROM call_times;
                    """.format(day,clid)
    cursor.execute(query)
    returned_data = cursor.fetchone()
    returned_data = str(returned_data[0])

    if returned_data == 'None':
        main_data.update( {'avgQueuetime' : '0' })
    else:
        # Subscript off extra digits from millisecond timstamp as not needed
        returned_data = str(returned_data[:7])
		# Convert str of time in total count of seconds
        h, m, s = returned_data.split(':')
        returned_data = int(h) * 3600 + int(m) * 60 + int(s)
        main_data.update( {'avgQueuetime' : str(returned_data)} )


    # Close the connection with the database
    cursor.close()
    conn.close()
    print("PostgreSQL connection is closed")

    if not main_data:
        return null
    return(main_data)


def write_to_database(day, data_to_write):
    """Writes the returned phone system data to a PostgreSQL database"""

    """ PSQL commands to create the database:
            # CREATE TABLE phonedata (id serial primary key, date DATE, data JSONB);
            # GRANT ALL ON phonedata TO user;
            # GRANT ALL ON SEQUENCE phonedata_id_seq TO user;
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

    # enable json handling
    psycopg2.extras.register_json(conn)

    # Connect the cursor
    cursor = conn.cursor()
    
    # INSERT the Google Analytics data with date into the database
    print("INSERTING into the database now")

    query = "INSERT INTO phonedata ( date, data ) VALUES ( (CURRENT_DATE - %s)::DATE, %s)"

    cursor.execute(query, (day, psycopg2.extras.Json(data_to_write)))
    
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
        phone_data = read_from_database(day)
        write_to_database(day, phone_data)
        day+=1



def main():
    lastmonths()

if __name__ == '__main__':
  main()
