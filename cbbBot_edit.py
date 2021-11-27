#!/Usr/bin/python3
import datetime
import pytz
import time
import cbbBot_text
import cbbBot_data

tz = pytz.timezone('US/Eastern')

try: #import if praw is happy, quit this cycle if not
    import praw
    print('Imported praw! ' + str(datetime.datetime.now(tz)))
except:
    print('Failed to import praw. Shutting down..... ' + str(datetime.datetime.now(tz)))
    quit()

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

while True:
    hour, minute = datetime.datetime.now(tz).hour, datetime.datetime.now(tz).minute
    if hour == 10 and minute == 6:
        quit()

    games = cbbBot_data.read_games()
    for game, row in games.iterrows():
        if (row['gamethread'] != '') and not any([desc in row['status'].lower() for desc in ['final', 'canceled', 'postponed']]):
            try:
                game_data = cbbBot_data.get_game_data(game)
                print('Obtained game info for ' + game + '! ' + str(datetime.datetime.now(tz)))
            except:
                print('Failed to get game info for ' + game + '! ' + str(datetime.datetime.now(tz)))
            try:
                thread = r.submission(id = row['gamethread'].split('/')[4]) #find already posted thread
                comment_stream_link = 'http://www.reddit-stream.com' + thread.permalink
                (title, thread_text) = cbbBot_text.make_game_thread(game, game_data, comment_stream_link) #re-write thread
                print('Made thread for game ' + game + '! ' + str(datetime.datetime.now(tz)))
                thread.edit(thread_text) #edit thread
                print('Edited thread ' + game + '! ' + str(datetime.datetime.now(tz)))
            except:
                print('Failed to edit thread ' + game + '. Will continue..... ' + str(datetime.datetime.now(tz)))
            time.sleep(5)
    time.sleep(5)
