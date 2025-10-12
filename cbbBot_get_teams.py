#!/Usr/bin/python3
import datetime
import json
import time

import requests

year = 2025

teams = {}
date = datetime.datetime(year = year, month = 11, day = 1)
while date < datetime.datetime(year = year + 1, month = 3, day = 1):
    url = 'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?dates=' + date.strftime('%Y%m%d') + '&groups=50&limit=357'
    downloaded = False
    while not downloaded:
        obj = requests.get(url)
        schedule = json.loads(obj.content)
        downloaded = 'events' in schedule
        time.sleep(1)

    for game in schedule['events']:
        game_id = game['id']
        away_team, home_team = [team['team']['location'] for team in game['competitions'][0]['competitors']]
        if away_team not in teams.keys():
            teams[away_team] = 0
        if home_team not in teams.keys():
            teams[home_team] = 0
        teams[away_team], teams[home_team] = teams[away_team] + 1, teams[home_team] + 1
    date = date + datetime.timedelta(days = 1)

for team in sorted(teams.items(), key = lambda x: x[1], reverse = True):
    print(team[0] + ',' + str(team[1]))
