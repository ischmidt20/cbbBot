#!/Usr/bin/python3
import datetime
import pytz
import cbbBot_data

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

hour, minute = datetime.datetime.now(tz).hour, datetime.datetime.now(tz).minute
if hour == 10 and minute == 7:
    import os
    os.system('python3 cbbBot_newday.py')

import cbbBot_text #Import later so index thread updates appropriately

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

games = cbbBot_data.read_games()

stoppers = ['Ike348', '1hive']
mods = ['Ike348'] + [user.name for user in list(r.subreddit('CollegeBasketball').moderator())]

try:
    print('Checking mail..... ' + str(datetime.datetime.now(tz)))
    for message in r.inbox.unread(): #look for requests
        body = message.body
        subject = message.subject
        if isinstance(message, praw.models.Message):
            if len(body) == 9 and body.isnumeric(): #if message is 9-digit ID
                if cbbBot_data.check_game(body): #if message is valid game
                    if subject.lower() == 'request':
                        # If user has requested too many threads already
                        if ((games['user'] == message.author).sum() >= 2) and (message.author not in mods):
                            message.reply(body = cbbBot_text.msg_spam)
                            message.mark_read()
                            continue
                        # If user does not meet karma or age thresholds
                        author = r.redditor(message.author)
                        if (author.comment_karma < 0) or ((datetime.datetime.utcnow().timestamp() - author.created_utc) < 86400):
                            message.reply(body = cbbBot_text.msg_young)
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
                                message.reply(body = cbbBot_text.msg_success)
                                print('Added game ' + body + ' to queue! ' + str(datetime.datetime.now(tz)))
                            else:
                                message.reply(body = cbbBot_text.msg_duplicate)
                        else:
                            message.reply(body = cbbBot_text.msg_success)
                            print('Added game ' + body + ' to queue! ' + str(datetime.datetime.now(tz)))
                    if subject.lower() == 'pgrequest':
                        games.loc[body, 'pgrequested'] = 1
                        message.reply(body = cbbBot_text.msg_success_pg)
                        print('Added post-game ' + body + ' to queue! ' + str(datetime.datetime.now(tz)))
                else:
                    message.reply(body = bbBot_text.msg_fail)
            elif message.author in stoppers and subject.lower() == 'stop': #if admin wants to prevent game thread from being made
                blacklist.append(body)
                with open('./data/blacklist.txt', 'a') as f:
                    f.write(body + '\n')
                print('Bot will not write game ' + game + '. ' + str(datetime.datetime.now(tz)))
                message.reply(body = cbbBot_text.msg_stopped)
            elif message.author != 'reddit':
                message.reply(body = cbbBot_text.msg_fail)
            message.mark_read()
except:
    print('Could not check messages. Will continue. ' + str(datetime.datetime.now(tz)))

games.loc[[game for game in requested_games if game in games.index], 'requested'] = 1

print('Checking games..... ' + str(datetime.datetime.now(tz)))

for game, row in games.loc[(~games['status'].str.lower().isin(['canceled', 'postponed', 'forfeit'])) & ((games['requested'] + games['pgrequested']) >= 1) & (games['pgthread'] == '')].iterrows():
    if 'FINAL' in row['status']:
        try:
            game_data = cbbBot_data.get_game_data(game)
            print('Obtained game info for ' + game + '! ' + str(datetime.datetime.now(tz)))
            (title, thread_text) = cbbBot_text.make_pg_thread(game, game_data)
            print('Made post-game thread for game ' + game + '! ' + str(datetime.datetime.now(tz)))
            pgthread = r.subreddit('CollegeBasketball').submit(title = title, selftext = thread_text, send_replies = False, flair_id = '323a5f80-872b-11e6-ac0e-0e5318091097')
            games.loc[game, 'pgthread'] = pgthread.permalink
            print('Posted post-game thread ' + game + '! ' + str(datetime.datetime.now(tz)))
            thread = r.submission(id = row['gamethread'].split('/')[4]) #find already posted thread
            comment_stream_link = 'http://www.reddit-stream.com' + thread.permalink
            (title, thread_text) = cbbBot_text.make_game_thread(game, game_data, comment_stream_link) #re-write thread
            print('Made thread for game ' + game + '! ' + str(datetime.datetime.now(tz)))
            thread.edit(body = thread_text) #edit thread
            print('Edited thread ' + game + '! ' + str(datetime.datetime.now(tz)))
        except:
            print('Failed to post post-game ' + game + '. ' + str(datetime.datetime.now(tz)))
    if (row['requested'] == 1) and (row['gamethread'] == '') and ('FINAL' not in row['status']):
        if datetime.datetime.now(tz) > (row['date'] - datetime.timedelta(minutes = 60)) and game not in blacklist: #if time is later than 60 minutes before game time, and game is not over, post thread, write thread_id to file
            print('Posting game ' + game + ' ..... ' + str(datetime.datetime.now(tz)))
            try:
                game_data = cbbBot_data.get_game_data(game)
                print('Obtained game info for ' + game + '! ' + str(datetime.datetime.now(tz)))
                (title, thread_text) = cbbBot_text.make_game_thread(game, game_data)
                print('Made thread for game ' + game + '! ' + str(datetime.datetime.now(tz)))
                thread = r.subreddit('CollegeBasketball').submit(title = title, selftext = thread_text, send_replies = False, flair_id = '2be569e0-872b-11e6-a895-0e2ab20e1f97')
                games.loc[game, 'gamethread'] = thread.permalink
                print('Posted game thread ' + game + '! ' + str(datetime.datetime.now(tz)))
            except:
                print('Failed to post game ' + game + '. ' + str(datetime.datetime.now(tz)))
        else:
            print('Game ' + game + ' will not be posted at this time. ' + str(datetime.datetime.now(tz)))

games = cbbBot_data.update_schedule(games)
games.to_csv('./data/games_today.csv')

r.submission(id = cbbBot_text.index_permalink.split('/')[4]).edit(body = cbbBot_text.index_thread(games))

print('Concluded script without issues. ' + str(datetime.datetime.now(tz)))
