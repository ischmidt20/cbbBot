#!/Usr/bin/python3
import requests
import datetime
import pytz
import json

tz = pytz.timezone('US/Eastern')

def get_teams():
    with open('./data/team_list.csv', 'r') as imp_file:
        lines = imp_file.readlines()
    flairs = {}
    rank_names = {}
    for line in lines:
        (team, flair, rank_name) = line.replace('\n', '').split(',')
        flairs[team] = flair
        rank_names[team] = rank_name
    return flairs, rank_names

def get_rcbb_rank():
    (flairs, rank_names) = get_teams()
    url = 'http://cbbpoll.com/'
    lines = requests.get(url).content.decode('utf-8').split('\n')
    ranking, first_place_votes = [], []
    i = 1
    while i < 125:
        first_place_votes.append('(' + str(i) + ')')
        i = i + 1
    rank_names_inv = {}
    for team in list(rank_names.items()):
        rank_names_inv[team[1]] = team[0]
    for line in lines:
        if "<td><span class='team-name'>" in line:
            team_rank = lines[lines.index(line) - 1].replace('<td>', '').replace('</td>', '')
            line = line.replace('&#39;', "'").replace('&#38;', '&')
            begin = line.find('></span>')
            end = line.find('</span></td>')
            team = line[(begin + 9):end]
            for vote in first_place_votes:
                if vote in team:
                    team = team.replace(vote, '')
                    break
            ranking.append(rank_names_inv[team.replace('&amp;', '&')] + ',' + str(int(team_rank)))
    with open('./data/ranking.txt', 'w') as f:
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

def get_events():
    now = datetime.datetime.now(tz) - datetime.timedelta(hours = 10)
    groups = ['50', '100', '98', '55', '56']
    full_events = []
    for group in groups:
        url = 'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?dates=' + now.strftime('%Y%m%d') + '&groups=' + group + '&limit=357'
        obj = requests.get(url)
        schedule = json.loads(obj.content)
        full_events = full_events + schedule['events']
    return full_events

def update_schedule(games):
    events = get_events()
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
