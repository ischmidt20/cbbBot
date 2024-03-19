#!/Usr/bin/python3
import cloudscraper
import pytz
import requests

import pandas as pd
import numpy as np

import datetime
import json
import time

tz = pytz.timezone('US/Eastern')

use_reddit_rank = False

def get_game_data(game_id):
    game_data = espn(game_id)
    teams = get_teams()

    if use_reddit_rank:
        game_data['awayRank'], game_data['homeRank'] = '', '' #clear ESPN rank values
    game_data['awayFlair'], game_data['homeFlair'] = game_data['awayTeam'], game_data['homeTeam']

    if game_data['awayTeam'] in teams.index:
        if use_reddit_rank and not np.isnan(teams.loc[game_data['awayTeam'], 'CBBPollRank']):
            game_data['awayRank'] = int(teams.loc[game_data['awayTeam'], 'CBBPollRank'])
        game_data['awayFlair'] = teams.loc[game_data['awayTeam'], 'Flair']
    if game_data['homeTeam'] in teams.index:
        if use_reddit_rank and not np.isnan(teams.loc[game_data['homeTeam'], 'CBBPollRank']):
            game_data['homeRank'] = int(teams.loc[game_data['homeTeam'], 'CBBPollRank'])
        game_data['homeFlair'] = teams.loc[game_data['homeTeam'], 'Flair']
    return game_data

def read_games():
    games = pd.read_csv('./data/games_today.csv', dtype = {'id': str}, parse_dates = ['date']).fillna('').set_index('id')
    for column in ['awayRank', 'awayKenpomRank', 'homeRank', 'homeKenpomRank']:
        games[column] = games[column].fillna('').astype(str).str.replace('.0', '', regex = False)
    return games

def read_teams():
    return pd.read_csv('data/team_list.csv', names = ['Team', 'Flair', 'CBBPollName', 'KenpomName'], encoding = 'utf-8').set_index('Team')

def get_teams():
    teams = read_teams()
    with open('./data/cbbpoll.txt', 'r') as imp_file:
        lines = imp_file.readlines()
    cbbpoll = [line.replace('\n', '') for line in lines]
    teams.loc[cbbpoll, 'CBBPollRank'] = np.arange(1, 25 + 1)
    with open('./data/kenpom.txt', 'r', encoding = 'utf-8') as imp_file:
        lines = imp_file.readlines()
    kenpom = [line.replace('\n', '') for line in lines]
    teams.loc[kenpom, 'KenpomRank'] = np.arange(1, len(teams) + 1)
    return teams

def download_kenpom():
    teams = read_teams()
    url = 'https://kenpom.com/'
    downloaded = False
    while not downloaded:
        lines = cloudscraper.create_scraper().get('https://kenpom.com/').content.decode('utf-8').split('\n')
        if len(lines) > 150:
            downloaded = True
        time.sleep(5)
    ranking = []
    search_str = '<a href="team.php'
    for line in lines:
        if search_str in line:
            begin = line.find('>', line.find(search_str) + len(search_str))
            end = line.find('</a>')
            team = line[(begin + 1):end]
            ranking.append(teams.loc[teams['KenpomName'] == team].index[0])
    with open('./data/kenpom.txt', 'w', encoding = 'utf-8') as f:
        for team in ranking:
            f.write(team + '\n')

def download_rcbb_rank():
    teams = read_teams()
    url = 'http://cbbpoll.net/'
    line = requests.get(url).content.decode('utf-8')
    start_str = 'type="application/json">'
    start_index = line.find(start_str)
    data = json.loads(line[start_index + len(start_str): line.find('</script>', start_index)])
    poll = data['props']['pageProps']['userpoll']

    ranking = []
    for i in range(25):
        team = poll[i]['shortName']
        ranking.append(teams.loc[teams['CBBPollName'] == team].index[0])
    with open('./data/cbbpoll.txt', 'w') as f:
        for team in ranking:
            f.write(team + '\n')

def if_exists(dct, key, value):
    if key in dct:
        return dct[key]
    return value

def check_game(game_id):
    url = 'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/summary?event=' + str(game_id)
    obj = requests.get(url)
    game = json.loads(obj.content)
    if 'code' in game:
        if game['code'] == 404:
            return False
    return True

def get_events(date):
    groups = ['50']
    full_events = []
    for group in groups:
        for offset in [0, 1]:
            url = 'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?dates=' + (date + datetime.timedelta(days = offset)).strftime('%Y%m%d') + '&groups=' + group + '&limit=357'
            obj = requests.get(url)
            schedule = json.loads(obj.content)
            full_events = full_events + schedule['events']
    return full_events

def update_schedule(games):
    events = get_events(datetime.datetime.now(tz) - datetime.timedelta(hours = 10))
    for game in events:
        game_id = game['id']
        status = game['status']['type']['detail'].replace(' - ', ' ').replace(' Half', '').upper()
        if game['status']['type']['id'] != '1':
            if game_id in games.index:
                games.loc[game_id, 'status'] = status
    return games

def espn(game_id):
    url = 'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/summary?event=' + str(game_id)
    obj = requests.get(url)
    game = json.loads(obj.content)
    teams = game['header']['competitions'][0]['competitors']

    return_data = {}

    (return_data['homeRank'], return_data['awayRank']) = [if_exists(team, 'rank', '') for team in teams]
    (return_data['homeTeam'], return_data['awayTeam']) = [team['team']['location'] for team in teams]
    (return_data['homeRecord'], return_data['awayRecord']) = [team['record'][0]['summary'] if team['record'] else '' for team in teams]
    (return_data['homeScore'], return_data['awayScore']) = [int(if_exists(team, 'score', 0)) for team in teams]
    (return_data['homeLinescore'], return_data['awayLinescore']) = [[x['displayValue'] for x in if_exists(team, 'linescores', [])] for team in teams]

    return_data['venue'] = game['gameInfo']['venue']['fullName']
    return_data['city'] = game['gameInfo']['venue']['address']['city']
    return_data['state'] = game['gameInfo']['venue']['address']['state']
    return_data['boxscore'] = game['boxscore']

    return_data['plays'] = []
    if 'plays' in game:
        return_data['plays'] = game['plays'][:-6:-1]

    return_data['network'] = ''
    if len(game['header']['competitions'][0]['broadcasts']) > 0:
        return_data['network']  = game['header']['competitions'][0]['broadcasts'][0]['media']['shortName']

    return_data['startTime'] = pytz.utc.localize(datetime.datetime.strptime(game['header']['competitions'][0]['date'],'%Y-%m-%dT%H:%MZ')).astimezone(tz)
    return_data['gameClock'] = game['header']['competitions'][0]['status']['type']['detail']
    if game['header']['competitions'][0]['status']['type']['id'] == '1':
        return_data['gameClock'] = ''

    return_data['spread'], return_data['overUnder'] = '', ''
    if game['pickcenter']:
        for provider in game['pickcenter']:
            if provider['provider']['name'] == 'consensus':
                return_data['spread'] = provider['details']
                return_data['overUnder'] = provider['overUnder']

    return return_data
