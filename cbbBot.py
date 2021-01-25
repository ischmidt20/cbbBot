#!/Usr/bin/python3
import datetime
import pytz
import cbbBot_data
import cbbBot_text

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
    game_data['awayRank'], game_data['homeRank'] = '', '' #clear ESPN rank values
    game_data['awayFlair'], game_data['homeFlair'] = game_data['awayTeam'], game_data['homeTeam']
    if game_data['awayTeam'] in teams.keys():
        if rank_names[game_data['awayTeam']] in ranking.keys():
            game_data['awayRank'] = str(ranking[rank_names[game_data['awayTeam']]])
        game_data['awayFlair'] = teams[game_data['awayTeam']]
    if game_data['homeTeam'] in teams.keys():
        if rank_names[game_data['homeTeam']] in ranking.keys():
            game_data['homeRank'] = str(ranking[rank_names[game_data['homeTeam']]])
        game_data['homeFlair'] = teams[game_data['homeTeam']]
    return game_data

with open('./client.txt', 'r') as imp_file:
    lines = imp_file.readlines()
lines = [line.replace('\n', '') for line in lines]

try:
    r = praw.Reddit(client_id = lines[0], client_secret = lines[1], username = "cbbBot", password = lines[2], user_agent="CBB Bot v5") #define praw and user agent, login
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

requested_games = []
blacklist = []

stoppers = ['Ike348', '1hive']
try:
    print('Checking mail..... ' + str(datetime.datetime.now(tz)))
    for message in r.inbox.unread(): #look for requests
        body = message.body
        subject = message.subject
        if isinstance(message, praw.models.Message):
            if subject.lower() == 'request' and len(body) == 9: #if message is a game request
                if cbbBot_data.check_game(body):
                    if body not in requested_games:
                        requested_games.append(body) #add game to queue
                    message.reply('Thanks for your message. The game you requested has been successfully added to the queue and will be created within an hour of the scheduled game time. If the game has already started, the thread will be created momentarily. If the game is over, no thread will be created.')
                    print('Added game ' + body + ' to queue! ' + str(datetime.datetime.now(tz)))
                else:
                    message.reply('Thanks for your message. If you are trying to submit a game thread request, please make sure your title is "request" (case-insensitive) and the body contains only the ESPN game ID. If your request is successful, you will get a confirmation reply. If you have a question or comment about the bot, please send to u/Ike348.')
            elif message.author in stoppers and subject.lower() == 'stop': #if admin wants to prevent game thread from being made
                blacklist.append(body)
                message.reply('No game thread will be created for ' + body + '!')
            else:
                message.reply('Thanks for your message. If you are trying to submit a game thread request, please make sure your title is "request" (case-insensitive) and the body contains only the ESPN game ID. If your request is successful, you will get a confirmation reply. If you have a question or comment about the bot, please send to u/Ike348.')
            message.mark_read()
except:
    print('Could not check messages. Will continue. ' + str(datetime.datetime.now(tz)))

with open('./data/blacklist.txt', 'a') as f: #add blacklisted games to file
    for game in blacklist:
        f.write(game + '\n')
        print('Bot will not write game ' + game + '. ' + str(datetime.datetime.now(tz)))

with open('./data/blacklist.txt', 'r') as imp_file: #get all blacklisted games from file
    lines = imp_file.readlines()
blacklist = []
for line in lines:
    blacklist.append(line.replace('\n', ''))

with open('./data/games_to_write.txt', 'r') as imp_file: #get day's games from newday script
    games = imp_file.readlines()

with open('./data/games_to_write.txt', 'a') as f: #add requested games to list of games to make
    for game in requested_games:
        if game + '\n' not in games:
            f.write(game + '\n')
            print('Bot knows to write game ' + game + '. ' + str(datetime.datetime.now(tz)))

print('Checking which games have already been posted..... ' + str(datetime.datetime.now(tz)))
already_posted = {}
for post in r.redditor('cbbBot').submissions.new(limit = 1000): #see which games already have threads
    if post.subreddit == 'CollegeBasketball':
        game_id = post.selftext[(post.selftext.find('http://www.espn.com/mens-college-basketball/game?gameId=') + 56):(post.selftext.find('http://www.espn.com/mens-college-basketball/game?gameId=') + 65)]
        already_posted[game_id] = post.id

games_over = []
with open('./data/games_over.txt', 'r') as imp_file: #see which games are already over
    lines = imp_file.readlines()
for line in lines:
    games_over.append(line.replace('\n', ''))

print('Checking games..... ' + str(datetime.datetime.now(tz)))

for game in games:
    game = game.replace('\n', '')
    if game not in games_over:
        print('Getting game info for ' + game + '..... ' + str(datetime.datetime.now(tz)))
        if cbbBot_data.check_game(game):
            game_data = get_info(game)
            print('Obtained game info for ' + game + '! ' + str(datetime.datetime.now(tz)))
            if game not in already_posted.keys():
                if any([desc in game_data['gameClock'].lower() for desc in ['canceled', 'postponed', 'final']]):
                    with open('./data/games_over.txt', 'a') as f:
                        f.write(game + '\n')
                    continue
                elif datetime.datetime.now(tz) > (game_data['startTime'] - datetime.timedelta(minutes = 60)) and game not in blacklist: #if time is later than 60 minutes before game time, and game is not over, post thread, write thread_id to file
                    print('Posting game ' + game + ' ..... ' + str(datetime.datetime.now(tz)))
                    try:
                        (title, thread_text) = cbbBot_text.make_thread(game, game_data)
                        print('Made thread for game ' + game_id + '! ' + str(datetime.datetime.now(tz)))
                        thread = r.subreddit('CollegeBasketball').submit(title = title, selftext = thread_text, send_replies = False)
                        thread.flair.select('2be569e0-872b-11e6-a895-0e2ab20e1f97')
                        print('Posted game thread ' + game + '! ' + str(datetime.datetime.now(tz)))
                    except:
                        print('Failed to post game ' + game + '. ' + str(datetime.datetime.now(tz)))
                else:
                    print('Game ' + game + ' will not be posted at this time. ' + str(datetime.datetime.now(tz)))
            else:
                if datetime.datetime.now(tz) > (game_data['startTime'] + datetime.timedelta(hours = 4)) and 'final' in game_data['gameClock'].lower():
                    with open('./data/games_over.txt', 'a') as f:
                        f.write(game + '\n')
                try:
                    thread = r.submission(id = already_posted[game]) #find already posted thread
                    comment_stream_link = 'http://www.reddit-stream.com/' + thread.permalink
                    (title, thread_text) = cbbBot_text.make_thread(game, game_data, comment_stream_link) #re-write thread
                    print('Made thread for game ' + game_id + '! ' + str(datetime.datetime.now(tz)))
                    thread.edit(thread_text) #edit thread
                    print('Edited thread ' + game + '! ' + str(datetime.datetime.now(tz)))
                except:
                    print('Failed to edit thread ' + game + '. Will continue..... ' + str(datetime.datetime.now(tz)))
        else:
            print('Failed to get game info for ' + game + '. ' + str(datetime.datetime.now(tz)))

thread = r.submission(id = '5ctg2v') #get thread to edit
thread.edit(str(datetime.datetime.now(tz)) + '\n\n' + 'bot concluded script') #edit same thread with current timestamp; lets me know that the bot has finished without issues
print('Concluded script without issues. ' + str(datetime.datetime.now(tz)))
