# Importing needed libraries.
from config import location_name, rapid_api, project_id
from google.cloud import bigquery
import pandas as pd
import requests
import json

# Headers used for RapidAPI.
headers = {
	"X-RapidAPI-Key": rapid_api,
	"X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# Creating URL variables.
url= "https://api-football-v1.p.rapidapi.com/v3/"
url_s = url + "standings"
url_t = url + "teams"

# Empty lists that will be filled and then used to create a dataframe.
id_list = []
team_list = []
city_list = []

# Building query for id_list.
querystring_s = {"season":"2022","league":"39"}
response_s = requests.request("GET", url_s, headers=headers, params=querystring_s)
json_res_s = response_s.json()

# Filling in id_list.
count = 0
while count < 20:
	id_list.append(str(json.dumps(json_res_s
	["response"][0]["league"]["standings"][0][count]["team"]["id"])))

	count += 1

# Filling in team_list and city_list. 
for id in id_list:
	querystring_t = {"id":id}
	response = requests.request("GET", url_t, headers=headers, params=querystring_t)
	json_res = response.json()

	team_list.append(str(json.dumps(json_res["response"][0]["team"]["name"])).strip('"'))
	city_list.append(str(json.dumps(json_res["response"][0]["venue"]["city"])).strip('"'))

class Location:

	def drop(self):
		client = bigquery.Client()
		query = """
            DROP TABLE 
            {}.premier_league.location
        """.format(project_id)

		query_job = client.query(query)

		print("Location table dropped...")

	def load(self):
		# Setting the headers then zipping the lists to create a dataframe.
		headers = ['Team', 'City']
		zipped = list(zip(team_list, city_list))

		df = pd.DataFrame(zipped, columns=headers)
		
		client = bigquery.Client(project=project_id)

		table_id = location_name

		job = client.load_table_from_dataframe(
            df, table_id
        )  # Make an API request.
		job.result()  # Wait for the job to complete.

		table = client.get_table(table_id)  # Make an API request.
		print(
            "Loaded {} rows and {} columns".format(
                table.num_rows, len(table.schema)
            )
        )