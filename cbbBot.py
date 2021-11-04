#!/Usr/bin/python3
import datetime
import pytz
import cbbBot_data
import cbbBot_text

import pandas as pd
import numpy as np

tz = pytz.timezone('US/Eastern')

try: #import if praw is happy, quit this cycle if not
    import praw
    import praw.models
    print('Imported praw! ' + str(datetime.datetime.now(tz)))
except:
    print('Failed to import praw. Shutting down..... ' + str(datetime.datetime.now(tz)))
    quit()

def get_info(game_id):
    game_data = cbbBot_data.espn(game_id)
    with open('./data/ranking.txt', 'r') as imp_file:
        lines = imp_file.readlines()
    (teams, rank_names) = cbbBot_data.get_teams()
    ranking = {}
    for line in lines:
        (team, rank) = line.replace('\n', '').split(',')
        team = team.replace('&amp;', '&')
        ranking[team] = int(rank)
    #game_data['awayRank'], game_data['homeRank'] = '', '' #clear ESPN rank values
    game_data['awayFlair'], game_data['homeFlair'] = game_data['awayTeam'], game_data['homeTeam']
    if game_data['awayTeam'] in teams.keys():
        #if rank_names[game_data['awayTeam']] in ranking.keys():
        #    game_data['awayRank'] = str(ranking[rank_names[game_data['awayTeam']]])
        game_data['awayFlair'] = teams[game_data['awayTeam']]
    if game_data['homeTeam'] in teams.keys():
        #if rank_names[game_data['homeTeam']] in ranking.keys():
    #        game_data['homeRank'] = str(ranking[rank_names[game_data['homeTeam']]])
        game_data['homeFlair'] = teams[game_data['homeTeam']]
    return game_data

with open('./client.txt', 'r') as imp_file:
    lines = imp_file.readlines()
lines = [line.replace('\n', '') for line in lines]

try:
    r = praw.Reddit(client_id = lines[0], client_secret = lines[1], username = "cbbBot", password = lines[2], user_agent = "CBB Bot v5", timeout = 2) #define praw and user agent, login
    r.validate_on_submit = True
    print('Logged in to Reddit! ' + str(datetime.datetime.now(tz)))
except:
    print('Failed to login to Reddit. Shutting down..... ' + str(datetime.datetime.now(tz)))
    quit()

try:
    thread = r.submission(id = '5ctg2v') #get thread to edit
    thread.edit(datetime.datetime.now(tz)) #edit same thread with current timestamp; lets me know that the bot is running
    print('Edited check thread with current time and date! ' + str(datetime.datetime.now(tz)))
except:
    print('Failed to edit thread with current time and date. Will continue..... ' + str(datetime.datetime.now(tz)))

hour, minute = datetime.datetime.now(tz).hour, datetime.datetime.now(tz).minute

with open('./data/games_to_write.txt', 'r') as imp_file: #get games already requested
    lines = imp_file.readlines()
requested_games = []
for line in lines:
    requested_games.append(line.replace('\n', ''))

with open('./data/blacklist.txt', 'r') as imp_file: #get all blacklisted games from file
    lines = imp_file.readlines()
blacklist = []
for line in lines:
    blacklist.append(line.replace('\n', ''))

games = pd.read_csv('./data/games_today.csv', dtype = {'id': str}, parse_dates = ['date']).fillna('').set_index('id')

stoppers = ['Ike348', '1hive']
mods = ['Ike348', 'peanutsfan1995', 'Kllian', 'Concision', 'homemade_mayo', 'ztrobin5', 'AutoModerator', 'rCBB_Mod', 'Forestl', 'cbbflairwizard', '1hive', 'cinciforthewin', 'glass_bottle', 'OutlawsHeels', 'IrishBall', 'Nebraska_Actually', 'AlekRivard', 'cbbscorebot', 'Wicked_UMD', 'ouguy2017', 'DEP61', 'grubberbeb', 'cbbpollbot', 'NowWithVitamin_R', '44TheKid', 'SleveMcDichael4', 'jjstatman', 'jloose128', 'tldRAWR', 'BurrShotFirst1804', 's-sea', 'yakovgolyadkin', 'SnareShot', 'Purdue49OSU20']

try:
    print('Checking mail..... ' + str(datetime.datetime.now(tz)))
    for message in r.inbox.unread(): #look for requests
        body = message.body
        subject = message.subject
        if isinstance(message, praw.models.Message):
            if len(body) == 9 and body.isnumeric(): #if message is 9-digit ID
                if cbbBot_data.check_game(body): #if message is valid game
                    if subject.lower() == 'request':
                        if ((games['user'] == message.author).sum() >= 2) and (message.author not in mods):
                            message.reply(cbbBot_text.msg_spam)
                            message.mark_read()
                            continue
                        if body not in requested_games:
                            requested_games.append(body)
                            with open('./data/games_to_write.txt', 'a') as f:
                                f.write(body + '\n') #add game to queue
                        if body in games.index:
                            if games.loc[body, 'requested'] == 0:
                                games.loc[body, 'requested'] = 1
                                games.loc[body, 'user'] = message.author
                                message.reply(cbbBot_text.msg_success)
                                print('Added game ' + body + ' to queue! ' + str(datetime.datetime.now(tz)))
                            else:
                                message.reply(cbbBot_text.msg_duplicate)
                        else:
                            message.reply(cbbBot_text.msg_success)
                            print('Added game ' + body + ' to queue! ' + str(datetime.datetime.now(tz)))
                    if subject.lower() == 'pgrequest':
                        message.reply(cbbBot_text.msg_success_pg)
                        games.loc[body, 'pgrequest'] = 1
                else:
                    message.reply(cbbBot_text.msg_fail)
            elif message.author in stoppers and subject.lower() == 'stop': #if admin wants to prevent game thread from being made
                blacklist.append(body)
                with open('./data/blacklist.txt', 'a') as f:
                    f.write(body + '\n')
                print('Bot will not write game ' + game + '. ' + str(datetime.datetime.now(tz)))
                message.reply(cbbBot_text.msg_stopped)
            elif message.author != 'reddit':
                message.reply(cbbBot_text.msg_fail)
            message.mark_read()
except:
    print('Could not check messages. Will continue. ' + str(datetime.datetime.now(tz)))

#games = pd.read_csv('./data/games_today.csv', dtype = {'id': str}, parse_dates = ['date']).fillna('').set_index('id')

games.loc[[game for game in requested_games if game in games.index], 'requested'] = 1

print('Checking games..... ' + str(datetime.datetime.now(tz)))

for game, row in games.iterrows():
    if not any([desc in row['status'].lower() for desc in ['canceled', 'postponed']]) and row['requested'] == 1 and row['pgthread'] == '':
        if 'FINAL' in row['status']:
            try:
                game_data = get_info(game)
                (title, thread_text) = cbbBot_text.make_pg_thread(game, game_data, row)
                print('Made post-game thread for game ' + game + '! ' + str(datetime.datetime.now(tz)))
                pgthread = r.subreddit('CollegeBasketball').submit(title = title, selftext = thread_text, send_replies = False, flair_id = '323a5f80-872b-11e6-ac0e-0e5318091097')
                games.loc[game, 'pgthread'] = pgthread.permalink
                print('Posted post-game thread ' + game + '! ' + str(datetime.datetime.now(tz)))
            except:
                print('Failed to post post-game ' + game + '. ' + str(datetime.datetime.now(tz)))
        game_data = get_info(game)
        print('Obtained game info for ' + game + '! ' + str(datetime.datetime.now(tz)))
        if row['gamethread'] == '':
            if datetime.datetime.now(tz) > (game_data['startTime'] - datetime.timedelta(minutes = 60)) and game not in blacklist: #if time is later than 60 minutes before game time, and game is not over, post thread, write thread_id to file
                print('Posting game ' + game + ' ..... ' + str(datetime.datetime.now(tz)))
                try:
                    (title, thread_text) = cbbBot_text.make_game_thread(game, game_data)
                    print('Made thread for game ' + game + '! ' + str(datetime.datetime.now(tz)))
                    thread = r.subreddit('CollegeBasketball').submit(title = title, selftext = thread_text, send_replies = False, flair_id = '2be569e0-872b-11e6-a895-0e2ab20e1f97')
                    thread.flair.select('2be569e0-872b-11e6-a895-0e2ab20e1f97')
                    games.loc[game, 'gamethread'] = thread.permalink
                    print('Posted game thread ' + game + '! ' + str(datetime.datetime.now(tz)))
                except:
                    print('Failed to post game ' + game + '. ' + str(datetime.datetime.now(tz)))
            else:
                print('Game ' + game + ' will not be posted at this time. ' + str(datetime.datetime.now(tz)))
        else:
            try:
                thread = r.submission(id = row['gamethread'].split('/')[4]) #find already posted thread
                comment_stream_link = 'http://www.reddit-stream.com' + thread.permalink
                (title, thread_text) = cbbBot_text.make_game_thread(game, game_data, comment_stream_link) #re-write thread
                print('Made thread for game ' + game + '! ' + str(datetime.datetime.now(tz)))
                thread.edit(thread_text) #edit thread
                print('Edited thread ' + game + '! ' + str(datetime.datetime.now(tz)))
            except:
                print('Failed to edit thread ' + game + '. Will continue..... ' + str(datetime.datetime.now(tz)))

games = cbbBot_data.update_schedule(games)
games.to_csv('./data/games_today.csv')

r.submission(id = cbbBot_text.index_id).edit(cbbBot_text.index_thread(games))

thread = r.submission(id = '5ctg2v') #get thread to edit
thread.edit(str(datetime.datetime.now(tz)) + '\n\n' + 'bot concluded script') #edit same thread with current timestamp; lets me know that the bot has finished without issues
print('Concluded script without issues. ' + str(datetime.datetime.now(tz)))
