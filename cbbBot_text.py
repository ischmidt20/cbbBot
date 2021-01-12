#!/Usr/bin/python3
import datetime

#tz = pytz.timezone('US/Eastern')

tv_flairs = {'BTN':'[Big Ten Network](#l/btn)', 'CBS':'[CBS](#l/cbs)', 'CBSSN':'[CBS Sports Network](#l/cbssn)', 'ESPN':'[ESPN](#l/espn)', 'ESPN2':'[ESPN2](#l/espn2)', 'ESPN3':'[ESPN3](#l/espn3)', 'ESPNU':'[ESPNU](#l/espnu)', 'FOX':'[Fox](#l/fox)', 'FS1':'[Fox Sports 1](#l/fs1)', 'FSN':'[Fox Sports Network](#l/fsn)', 'LHN':'[Longhorn Network](#l/lhn)', 'NBC':'[NBC](#l/nbc)', 'NBCSN':'[NBC Sports Network](#l/nbcsn)', 'PAC12':'[Pac-12 Network](#l/p12n)', 'SECN':'[SEC Network](#l/secn)', 'TBS':'[TBS](#l/tbs)', 'TNT':'[TNT](#l/tnt)', 'truTV':'[truTV](#l/trutv)', 'ACCN':'[ACC Network](#l/accn)', 'ACCNE':'[ACC Network Extra](#l/accne)', 'ACCNX':'[ACC Network Extra](#l/accne)', 'ESPNN':'[ESPNews](#l/espnews)', 'FS2':'[Fox Sports 2](#l/fs2)'}

tv_stream_links = {'BTN':'[BTN](https://www.fox.com/live/channel/BTN/)', 'CBS':'[CBS](https://www.cbssports.com/college-basketball/cbk-live/)', 'CBSSN':'[CBSSN](https://www.cbssports.com/cbs-sports-network/)', 'ESPN':'[WatchESPN](https://www.espn.com/watch/)', 'ESPN2':'[WatchESPN](https://www.espn.com/watch/)', 'ESPN3':'[WatchESPN](https://www.espn.com/watch/)', 'ESPNU':'[WatchESPN](https://www.espn.com/watch/)', 'ESPNN':'[WatchESPN](https://www.espn.com/watch/)', 'FOX':'[FOX](https://www.fox.com/live/)', 'FS1':'[FS1](https://www.fox.com/live/channel/FS1/)', 'FSN':'[FOX Sports](https://www.foxsports.com/live)', 'LHN':'[WatchESPN](https://www.espn.com/watch/)', 'NBC':'[NBC Sports](http://www.nbcsports.com/live)', 'NBCSN':'[NBC Sports](http://www.nbcsports.com/live)', 'PAC12':'[PAC12](http://pac-12.com/live)', 'SECN':'[WatchESPN](https://www.espn.com/watch/)', 'ACCN':'[WatchESPN](https://www.espn.com/watch/)', 'ACCNE':'[WatchESPN](https://www.espn.com/watch/)', 'ACCNX':'[WatchESPN](https://www.espn.com/watch/)', 'ESPN+':'[ESPN+](https://plus.espn.com/)', 'FS2':'[FS2](https://www.fox.com/live/channel/fs2/)'}

def if_exists(dct, key, value):
    if key in dct:
        return dct[key]
    return value

def make_thread(game_id, game_data, comment_stream_link = ''):
    if game_data['awayFlair'] == '':
        thread = game_data['awayTeam']
    else:
        thread = game_data['awayFlair']

    if game_data['gameClock'] != '':
        thread = thread + ' ' + '**' + str(game_data['awayScore']) + '**' + ' @ **' + str(game_data['homeScore']) + '** '
    else:
        thread = thread + ' @ '

    if game_data['homeFlair'] == '':
        thread = thread + game_data['homeTeam']
    else:
        thread = thread + game_data['homeFlair']

    if game_data['gameClock'] != '':
        thread = thread + ' - **' + game_data['gameClock'].upper() + '**'

    thread = thread + '\n\n\n###NCAA Basketball\n [**^Click ^here ^to ^request ^a ^Game ^Thread**](https://www.reddit.com/r/CollegeBasketball/comments/5o5at9/introducing_ucbbbot_an_easier_way_of_making_game/)\n\n---\n '
    if game_data['awayRecord'] == '':
        game_data['awayRecord'] = '--'
    if game_data['homeRecord'] == '':
        game_data['homeRecord'] = '--'
    if game_data['awayRank'] != '':
        game_data['awayRank'] = '#' + game_data['awayRank'] + ' '
    if game_data['homeRank'] != '':
        game_data['homeRank'] = '#' + game_data['homeRank'] + ' '
    thread = thread + game_data['awayFlair'] + ' **' + game_data['awayRank'] + game_data['awayTeam'] + '** (' + game_data['awayRecord'] + ') @ ' + game_data['homeFlair'] + ' **' + game_data['homeRank'] + game_data['homeTeam'] + '** (' + game_data['homeRecord'] + ')\n\nTip-Off: '
    time = game_data['startTime'].strftime('%I:%M %p') + ' ET'
    if game_data['network'] == '':
        game_data['network'] = 'Check your local listings.'
    network_flair = game_data['network']
    if game_data['network'] in tv_flairs.keys():
        network_flair = tv_flairs[game_data['network']]
    thread = thread + time + '\n\nVenue: ' + game_data['venue'] + ', ' + game_data['city'] + ', ' + game_data['state'] + '\n\n-----------------------------------------------------------------\n\n###[](#l/discord) [Join Our Discord](https://discord.gg/redditcbb)\n\n###[](#l/twitter) [Follow Our Twitter](https://twitter.com/redditcbb) \n\n-----------------------------------------------------------------\n\n**Television:** \n' + network_flair + '\n\n\n**Streams:**\n'
    if game_data['network'] in tv_stream_links.keys():
        thread = thread + tv_stream_links[game_data['network']] + '\n'
    thread = thread + "\n\n-----------------------------------------------------------------" + create_boxscore(game_data)
    espn_link = 'http://www.espn.com/mens-college-basketball/game?gameId=' + game_id
    thread = thread + "\n\n-----------------------------------------------------------------\n\n**Thread Notes:**\n\n- I'm a bot! Don't be afraid to leave feedback!\n\n- Follow the game on [ESPN](" + espn_link + ") for preview, play-by-play, more stats, and recap.\n\n- Discuss whatever you wish. You can trash talk, but keep it civil.\n\n- Try [Chrome Refresh](https://chrome.google.com/extensions/detail/aifhnlnghddfdaccgbbpbhjfkmncekmn) or Firefox's [AutoReload](https://addons.mozilla.org/en-US/firefox/addon/auto-reload-tab/) to auto-refresh this tab.\n\n- You may also like [reddit stream](" + comment_stream_link + ") to keep up with comments.\n\n- Show your team affiliation - get a team logo by clicking 'Select Flair' on the right."

    title = '[Game Thread] ' + game_data['awayRank'] + game_data['awayTeam'] + ' @ ' + game_data['homeRank'] + game_data['homeTeam'] + ' (' + time + ')'
    return title, thread

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
