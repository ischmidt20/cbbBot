#!/Usr/bin/python3
import requests
import datetime
import pytz
import json

tz = pytz.timezone('US/Eastern')

def get_teams():
    with open('./data/team_list.csv','r') as imp_file:
        lines=imp_file.readlines()
    flairs = {}
    rank_names = {}
    for line in lines:
        (team,flair,rank_name) = line.replace('\n','').split(',')
        flairs[team] = flair
        rank_names[team] = rank_name
    return flairs, rank_names

def get_rcbb_rank():
    (flairs,rank_names) = get_teams()
    url = 'http://cbbpoll.com/'
    lines = requests.get(url).content.decode('utf-8').split('\n')
    ranking, first_place_votes = [], []
    i = 1
    while i < 125:
        first_place_votes.append('('+str(i)+')')
        i = i + 1
    rank_names_inv={}
    for team in list(rank_names.items()):
        rank_names_inv[team[1]] = team[0]
    for line in lines:
        if "<td><span class='team-name'>" in line:
            team_rank = lines[lines.index(line)-1].replace('<td>','').replace('</td>','')
            line = line.replace('&#39;',"'").replace('&#38;','&')
            begin = line.find('></span>')
            end = line.find('</span></td>')
            team = line[(begin+9):end]
            for vote in first_place_votes:
                if vote in team:
                    team = team.replace(vote,'')
                    break
            ranking.append(rank_names_inv[team.replace('&amp;','&')] + ',' + str(int(team_rank)))
    with open('./data/ranking.txt','w') as f:
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

def espn(game_id):
    url = 'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/summary?event=' + str(game_id)
    obj = requests.get(url)
    game = json.loads(obj.content)
    teams = game['header']['competitions'][0]['competitors']

    return_data = {}

    (return_data['homeRank'], return_data['awayRank']) = [if_exists(team, 'rank', '') for team in teams]
    (return_data['homeTeam'], return_data['awayTeam']) = [team['team']['location'] for team in teams]
    (return_data['homeRecord'], return_data['awayRecord']) = [team['record'][0]['summary'] if team['record'] else '--' for team in teams]
    (return_data['homeScore'], return_data['awayScore']) = [int(if_exists(team, 'score', 0)) for team in teams]

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

    return return_data

def create_boxscore(game_data):
    is_pregame = False
    boxscore = {}

    for team in game_data['boxscore']['teams']:
        name = team['team']['location']
        boxscore[name] = {}
        for data_point in team['statistics']:
            if 'label' in data_point:
                boxscore[name][data_point['label']] = data_point['displayValue']
            if 'abbreviation' in data_point:
                boxscore[name][data_point['abbreviation']] = data_point['displayValue']

        # Not sure if there's a better way to check if this is pre-game or not, but it definitely works!
        is_pregame = 'Streak' in boxscore[name].keys()

    if is_pregame:
        game_stats = ['STRK', 'PTS', 'PA', 'FG%', '3P%', 'REB', 'AST', 'BLK', 'STL', 'ToTO']
    else:
        game_stats = ['FG%', '3P%', 'FT%', 'REB', 'OR', 'AST', 'STL', 'BLK', 'TO', 'PF']

    boxscore_string = '\n\n'
    # Add 'Team' column to beginning of list
    boxscore_string = boxscore_string + 'Team | ' + ' | '.join(game_stats) + '\n'
    # Add the reddit table separator, length of stats + 1 due to manually adding 'Team'
    boxscore_string = boxscore_string + '----|' * (len(game_stats) + 1)

    # Doing it this way allows us to keep home/away in order
    boxscore_string = boxscore_string + '\n'

    boxscore_line = [game_data['awayFlair']]
    for stat in game_stats:
        value = if_exists(boxscore[game_data['awayTeam']], stat, '')
        boxscore_line.append(value)
    boxscore_string = boxscore_string + ' | '.join(boxscore_line) + '\n'

    boxscore_line = [game_data['homeFlair']]
    for stat in game_stats:
        value = if_exists(boxscore[game_data['homeTeam']], stat, '')
        boxscore_line.append(value)
    boxscore_string = boxscore_string + ' | '.join(boxscore_line)

    return boxscore_string
