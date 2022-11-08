# Importing needed modules.
from config import standings_name, rapid_api, project_id
from google.cloud import bigquery
import pandas as pd
import numpy as np
import requests
import json

# Headers used for RapidAPI.
headers = {
	"X-RapidAPI-Key": rapid_api,
	"X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# Standings endpoint from RapidAPI.
url = "https://api-football-v1.p.rapidapi.com/v3/standings"

# Building query to retrieve data.
query = {"season":"2022","league":"39"}
response = requests.request("GET", url, headers=headers, params=query)
json_res = response.json()

# Empty lists that will be filled and then used to create a dataframe.
rank_list = []
team_list = []
wins_list = []
draws_list = []
loses_list = []
points_list = []
goals_for = []
goals_against = []
goals_diff = []

# Filling in empty lists.
count = 0
while count < 20:
    # Team postion data.
    rank_list.append(int(json.dumps(json_res
        ["response"][0]["league"]["standings"][0][count]["rank"])))

    # Team names.
    team_list.append(str(json.dumps(json_res
        ["response"][0]["league"]["standings"][0][count]["team"]["name"])).strip('"'))

    # Number of wins.
    wins_list.append(int(json.dumps(json_res
        ["response"][0]["league"]["standings"][0][count]["all"]["win"])))

    # Number of draws.
    draws_list.append(int(json.dumps(json_res
        ["response"][0]["league"]["standings"][0][count]["all"]["draw"])))

    # Number of loses.
    loses_list.append(int(json.dumps(json_res
        ["response"][0]["league"]["standings"][0][count]["all"]["lose"])))

    # Number of points.
    points_list.append(int(json.dumps(json_res
        ["response"][0]["league"]["standings"][0][count]["points"])))

    # Number of goals for.
    goals_for.append(int(json.dumps(json_res
        ["response"][0]["league"]["standings"][0][count]["all"]["goals"]["for"])))

    # Number of goals against.
    goals_against.append(int(json.dumps(json_res
        ["response"][0]["league"]["standings"][0][count]["all"]["goals"]["against"])))

    # Number of goal differential.
    goals_diff.append(int(json.dumps(json_res
        ["response"][0]["league"]["standings"][0][count]["goalsDiff"])))
    count += 1

class Standings:

    # Dropping BigQuery table.
    def drop(self):
        client = bigquery.Client()
        query = """
            DROP TABLE 
            {}.premier_league.standings
        """.format(project_id)

        query_job = client.query(query)

        print("Standings table dropped...")

    def load(self):
        # Setting the headers then zipping the lists to create a dataframe.
        headers = ['Rank', 'Team', 'Wins', 'Draws', 'Loses', 'Points', 'GF', 'GA', 'GD']
        zipped = list(zip(rank_list, team_list, wins_list, draws_list, loses_list, points_list, goals_for, goals_against, goals_diff))

        df = pd.DataFrame(zipped, columns=headers)

        # Construct a BigQuery client object.
        client = bigquery.Client(project=project_id)

        table_id = standings_name

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