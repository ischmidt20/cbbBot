#!/Usr/bin/python3
import requests
import datetime
import pytz
import json
import cbbBot_data
import cbbBot_text

import pandas as pd
import numpy as np

tz = pytz.timezone('US/Eastern')
now = datetime.datetime.now(tz)

try:
    import praw
    import praw.models
    print('Imported praw! ' + str(datetime.datetime.now(tz)))
except:
    print('Failed to import praw. Shutting down..... ' + str(datetime.datetime.now(tz)))
    quit()

cbbBot_data.download_rcbb_rank()
cbbBot_data.download_kenpom()
teams = cbbBot_data.get_teams()

full_events = []

full_events = cbbBot_data.get_events(now)

espn_home_ranks, espn_away_ranks = [], []
game_dicts = []

for game in full_events:
    game_id = game['id']
    home_team, away_team = [team['team']['location'] for team in game['competitions'][0]['competitors']]
    date = pytz.utc.localize(datetime.datetime.strptime(game['date'], '%Y-%m-%dT%H:%MZ')).astimezone(tz)
    network = ''
    if len(game['competitions'][0]['broadcasts']) > 0:
        network = game['competitions'][0]['broadcasts'][0]['names'][0]

    espn_ranks = []
    for team in game['competitions'][0]['competitors']:
        rank = ''
        if 'curatedRank' in team:
            if 'current' in team['curatedRank']:
                rank = str(team['curatedRank']['current'])
                if rank == '99':
                    rank = ''
        espn_ranks.append(rank)

    if (date - datetime.timedelta(hours = 10)).day == now.day:
        game_dicts.append({'id': game_id, 'awayTeam': away_team, 'homeTeam': home_team, 'date': date, 'network': network})
        espn_home_ranks.append(espn_ranks[0])
        espn_away_ranks.append(espn_ranks[1])

games = pd.DataFrame(game_dicts)

if len(games) == 0:
    quit()

games = games.merge(teams[['CBBPollRank', 'KenpomRank']], how = 'left', left_on = 'awayTeam', right_index = True).merge(teams[['CBBPollRank', 'KenpomRank']], how = 'left', left_on = 'homeTeam', right_index = True)
games = games.rename(columns = {'CBBPollRank_x': 'awayRank', 'KenpomRank_x': 'awayKenpomRank', 'CBBPollRank_y': 'homeRank', 'KenpomRank_y': 'homeKenpomRank'})

if not cbbBot_data.use_reddit_rank:
    games['awayRank'] = espn_away_ranks
    games['homeRank'] = espn_home_ranks
games['top25'] = (games['awayRank'].replace('', np.nan).notna() | games['homeRank'].replace('', np.nan).notna()).astype(int)
for column in ['awayRank', 'awayKenpomRank', 'homeRank', 'homeKenpomRank']:
    games[column] = games[column].fillna('').astype(str).str.replace('.0', '', regex = False)

games = games.drop_duplicates('id', keep = 'first')

games['requested'] = games['top25']
games['pgrequested'] = games['top25']
games['gamethread'] = [''] * len(games)
games['pgthread'] = [''] * len(games)
games['user'] = [''] * len(games)
games['status'] = games['date'].dt.strftime('%I:%M %p')
games = games.sort_values(['top25', 'date'], ascending = [False, True]).set_index('id')
games.to_csv('./data/games_today.csv')

games_added = []
with open('./data/games_to_write.txt', 'r') as f:
    lines = f.readlines()
for line in lines:
    games_added.append(line.replace('\n', ''))

with open('./data/games_to_write.txt', 'a') as f: #create today's file
    for game, row in games.iterrows():
        if (row['top25']) and game not in games_added:
            f.write(game + '\n')

with open('./client.txt', 'r') as imp_file:
    lines = imp_file.readlines()
lines = [line.replace('\n', '') for line in lines]
try:
    r = praw.Reddit(client_id = lines[0], client_secret = lines[1], username = "cbbBot", password = lines[2], user_agent = "CBB Bot v5") #define praw and user agent, login
    r.validate_on_submit = True
    print('Logged in to Reddit! ' + str(datetime.datetime.now(tz)))
except:
    print('Failed to login to Reddit. Shutting down..... ' + str(datetime.datetime.now(tz)))
    quit()

title = 'Game Thread Index - ' + now.strftime('%B %d, %Y')

thread = r.subreddit('CollegeBasketball').submit(title = title, selftext = cbbBot_text.index_thread(games), send_replies = False, flair_id = '2be569e0-872b-11e6-a895-0e2ab20e1f97')
with open('./data/index_thread.txt', 'w') as f:
    f.write(thread.permalink)
