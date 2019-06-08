"""Retrieves metrics from Treshna phone system database for KPI dashboards
    Written by Tom Morgan on 2019-05-21
"""

import request
import psycopg2
import json
from datetime import date, timedelta
import requests

def read_from_database():
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
    cursor.execute("""  SELECT 
                            AVG(duration)::INT 
                        FROM 
                            cdr 
                        WHERE 
                            disposition = 'ANSWERED' AND 
                            calldate >= TIMESTAMP 'yesterday'  AND
                            calldate <= (TIMESTAMP 'today' - '1 second'::INTERVAL) AND 
                            duration > 60
                    """)
    returned_data = cursor.fetchone()

    if str(returned_data[0]) == 'None':
        main_date = {'avgDuration' : '0'}
    else:
        main_data = {'avgDuration' : str(returned_data[0])}

    # Selecting the count of voicemails from yesterday
    cursor.execute("""  SELECT 
                            COUNT(*) 
                        FROM 
                            cdr 
                        WHERE 
                            char_length(src::text) > 4 AND 
                            lastapp ILIKE '%voicemail%' AND 
                            calldate >= TIMESTAMP 'yesterday' AND 
                            calldate <= (TIMESTAMP 'today' - '1 second'::INTERVAL)
                    """)
    returned_data = cursor.fetchone()
    main_data.update( {'voicemailCount' : str(returned_data[0]) } )

    # Selecting the average queue time on calls from yesterday
    cursor.execute(  """WITH call_times AS (
                            SELECT
                                (MAX(calldate) - MIN(calldate)) AS "queue_time",
                                src,
                                MIN(disposition)
                            FROM
                                cdr
                            WHERE
                                lastapp ILIKE '%queue%' AND
                                calldate::DATE BETWEEN (TIMESTAMP 'yesterday')::DATE AND 
                                (TIMESTAMP 'today' - '1 second'::INTERVAL)::DATE AND
                                clid NOT LIKE '%{D}%'
                            GROUP BY uniqueid, src
                            )
                        SELECT avg(queue_time) FROM call_times;
                    """)
    returned_data = cursor.fetchone()
    returned_data = str(returned_data[0])
    # Subscript off extra digits from milliseconds timestamp as not needed
    main_data.update( {'avgQueuetime' : returned_data[:7]} )

    # Close the connection with the database
    cursor.close()
    conn.close()

    print("PostgreSQL connection is closed")

    if not main_data:
        return null
    return(main_data)


def write_to_database(data_to_write):
    """Writes the returned phone system data to a PostgreSQL database"""

    """ PSQL commands to create the database:
            # CREATE TABLE phonedata (id serial primary key, date TIMESTAMPTZ, data JSONB);
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

    # Connect the cursor
    cursor = conn.cursor()
    
    # INSERT the Google Analytics data with date into the database
    print("INSERTING into the database now")
    cursor.execute("INSERT INTO phonedata ( date, data ) VALUES ( CURRENT_DATE - 1 , %s)",(json.dumps(data_to_write),))
    
    # Make the changes to the database persistent
    conn.commit()

    # Close the connection with the database
    cursor.close()
    conn.close()
    print("PostgreSQL connection is closed")


def main():
    print('Reading data from phone system database')
    phone_data = read_from_database()
    print('Writing data to KPI database')
    write_to_database(phone_data)

if __name__ == '__main__':
  main()
