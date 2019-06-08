Any sensitive information within the code and README has been replaced with "###"

README file for KPI scripts and running Grafana
Written by Tom Morgan - 28-05-2019
I can be contacted at morgan.tom93@gmail.com if there are any questions. I have commented the code so it should be easy to read.

### KPI SCRIPTS ###

To run the script simply type "python3 [FILENAME]"

The scripts in this folder are used to get the data from the previous day.
They are run at 3am every morning so long as this Pi remains on.
The are run by a cronjob, to view them type "$ crontab -e"
The scripts access the API of the service that the file is named after.
All of these files add to a common local PostgreSQL database.
There are 3 tables in the database, one for each file. They are named:
	googleanalyticsdata
	ladeskdata
	phonedata

The structure of these tables are identical. It is:
	id - serial primary key
	date - DATE
	data - JSONB

This information is also in each script file.

The folder called "kpi90days" is a set of the same scripts just modified to run over and over getting data from the last 90 days.
When run, it will make a request to the relevant API and get the data for each date going back 90 days.
This is used to set up the KPI system so there is data to compare to for previous months.


### GoogleAnalyticMetrics.py ###

This file accesses Google Analytics Reporting API v4 with the client_secrets.json file.
It uses the VIEW_ID of "###" - "###"
To add more metrics to be gathered when running the script, add "expression" in a dict with the value of the ga:metric to be gather.
More of these metrics can be found easily at https://ga-dev-tools.appspot.com/request-composer

### LADeskMetrics.py ###

This is used to access the LADesk API v1 Performance Report.
The URL on line 19 specifies the results to be returned.
"&column=..." add more return fields seperated by commas as shown in the code to have more metrics returned.
Google "LADesk API" and navigate to "Performance Report" for more details.

### PhoneMetrics.py ###

This access the Treshna PostgreSQL database called ### that houses the phone system data.
This database has details on every call made within ###, Who made it, how long it lasted, where it was going, etc.
Only 3 metrics are taken from this database, as the data is messy and difficult to decipher what it all means.
The 3 metrics returned are self explanitory. If you want to add more metrics talk to "###" as he is knowledgable on the phone database.




### GRAFANA OPERATION ###

Grafana is installed on this machine, it is version v5.4.2 (commit: d812109).

To start the Grafana server type into the terminal:

# sudo grafana-server start
