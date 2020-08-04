#!/Usr/bin/python3
import requests
import datetime
import pytz
import json

tz = pytz.timezone('US/Eastern')

def get_teams():
    with open('./data/team_list.txt','r') as imp_file:
        lines=imp_file.readlines()
    flairs = {}
    rank_names = {}
    for line in lines:
        (team,flair,rank_name) = line.replace('\n','').split(',')
        flairs[team] = flair
        rank_names[team] = rank_name
    return flairs,rank_names

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

def espn(game_id):
    url = 'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/summary?event=' + str(game_id)
    obj = requests.get(url)
    game = json.loads(obj.content)
    teams = game['header']['competitions'][0]['competitors']

    (home_rank, away_rank) = [if_exists(team, 'rank', '') for team in teams]
    (home_team, away_team) = [team['team']['location'] for team in teams]
    (home_record, away_record) = [team['record'][0]['summary'] for team in teams]
    (home_score, away_score) = [int(team['score']) for team in teams]

    venue = game['gameInfo']['venue']['fullName']
    city = game['gameInfo']['venue']['address']['city']
    state = game['gameInfo']['venue']['address']['state']
    network = ''
    if len(game['header']['competitions'][0]['broadcasts']) > 0:
        network = game['header']['competitions'][0]['broadcasts'][0]['media']['shortName']

    start_time = pytz.utc.localize(datetime.datetime.strptime(game['header']['competitions'][0]['date'],'%Y-%m-%dT%H:%MZ')).astimezone(tz)
    game_clock = game['header']['competitions'][0]['status']['type']['detail']
    if game['header']['competitions'][0]['status']['type']['id'] == '1':
        game_clock = ''

    return [away_rank, away_team, away_record, home_rank, home_team, home_record, venue, city, state, network, start_time, game_clock, away_score, home_score]
