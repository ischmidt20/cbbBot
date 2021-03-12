#!/Usr/bin/python3
import requests
import datetime
import pytz
import json
import cbbBot_data
import cbbBot_text

import pandas as pd

tz = pytz.timezone('US/Eastern')
now = datetime.datetime.now(tz)

try:
    import praw
    import praw.models
    print('Imported praw! ' + str(datetime.datetime.now(tz)))
except:
    print('Failed to import praw. Shutting down..... ' + str(datetime.datetime.now(tz)))
    quit()

cbbBot_data.get_rcbb_rank()

#year, month, day = '2021', '01', '31'

with open('./data/ranking.txt','r') as imp_file:
    lines = imp_file.readlines()
ranking = []
for line in lines:
    ranking.append(line.replace('\n','').split(',')[0])


url = 'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?dates=' + now.strftime('%Y%m%d') + '&groups=50&limit=357'
obj = requests.get(url)
schedule = json.loads(obj.content)

url2 = 'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?dates=' + (now + datetime.timedelta(days = 1)).strftime('%Y%m%d') + '&groups=50&limit=357'
obj2 = requests.get(url2)
schedule2 = json.loads(obj2.content)

full_events = schedule['events'] + schedule2['events']

games = pd.DataFrame()
for game in full_events:
    game_id = game['id']
    home_team, away_team = [team['team']['location'] for team in game['competitions'][0]['competitors']]
    date = pytz.utc.localize(datetime.datetime.strptime(game['date'], '%Y-%m-%dT%H:%MZ')).astimezone(tz)
    network = ''
    if len(game['competitions'][0]['broadcasts']) > 0:
        network = game['competitions'][0]['broadcasts'][0]['names'][0]

    away_rank = ''
    if away_team in ranking:
        away_rank = '#' + str(ranking.index(away_team) + 1) + ' '
    home_rank = ''
    if home_team in ranking:
        home_rank = '#' + str(ranking.index(home_team) + 1) + ' '
    top25 = (away_rank != '' or home_rank != '')

    if date.day == now.day:
        games = games.append({'id': game_id, 'away': away_team, 'home': home_team, 'date': date, 'network': network, 'top25': top25, 'arank': away_rank, 'hrank': home_rank}, ignore_index = True)

games['requested'] = games['top25']
games['pgrequested'] = games['top25']
games['gamethread'] = [''] * len(games)
games['pgthread'] = [''] * len(games)
games['user'] = [''] * len(games)
games['status'] = games['date'].dt.strftime('%I:%M %p')
games = games.sort_values(['top25', 'date'], ascending = [False, True]).set_index('id')
games.to_csv('./data/games_today.csv')

games_added = []
with open('./data/games_to_write.txt','r') as f:
    lines = f.readlines()
for line in lines:
    games_added.append(line.replace('\n',''))

with open('./data/games_to_write.txt','a') as f: #create today's file
    for game, row in games.iterrows():
        if (row['away'] in ranking or row['home'] in ranking) and game not in games_added:
            f.write(game + '\n')

with open('./client.txt', 'r') as imp_file:
    lines = imp_file.readlines()
lines = [line.replace('\n', '') for line in lines]
try:
    r = praw.Reddit(client_id = lines[0], client_secret = lines[1], username = "cbbBot", password = lines[2], user_agent="CBB Bot v5") #define praw and user agent, login
    r.validate_on_submit = True
    print('Logged in to Reddit! ' + str(datetime.datetime.now(tz)))
except:
    print('Failed to login to Reddit. Shutting down..... ' + str(datetime.datetime.now(tz)))
    quit()

title = 'Game Thread Index - ' + now.strftime('%B %d, %Y')

thread = r.subreddit('CollegeBasketball').submit(title = title, selftext = cbbBot_text.index_thread(games), send_replies = False, flair_id = '2be569e0-872b-11e6-a895-0e2ab20e1f97')
with open('./data/index_thread.txt', 'w') as f:
    f.write(thread.id)
