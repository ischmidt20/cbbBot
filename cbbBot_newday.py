#!/Usr/bin/python3
import requests
import datetime
import pytz
import json
import cbbBot_func

cbbBot_func.get_rcbb_rank()

tz = pytz.timezone('US/Eastern')
now = datetime.datetime.now(tz)

#year,month,day='2020','03','10'

url = 'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?dates=' + now.strftime('%Y%m%d') + '&groups=50&limit=353'
obj = requests.get(url)
schedule = json.loads(obj.content)

games = []

for game in schedule['events']:
    game_id = game['id']
    away_team, home_team = [team['team']['location'] for team in game['competitions'][0]['competitors']]
    games.append((game_id,away_team,home_team))

with open('./data/ranking.txt','r') as imp_file:
    lines = imp_file.readlines()
ranking = []
for line in lines:
    ranking.append(line.replace('\n','').split(',')[0])

games_added = []
with open('./data/games_to_write.txt','r') as f:
    lines = f.readlines()

for line in lines:
    games_added.append(line.replace('\n',''))

with open('./data/games_to_write.txt','a') as f: #create today's file
    for game in games:
        if (game[1] in ranking or game[2] in ranking) and game[0] not in games_added:
            f.write(game[0]+'\n')
