#!/Usr/bin/python3
import urllib.request
import os
import datetime
import cbbBot_func
import pytz

dir='/home/i/is/ischmidt/cbbBot/'
#dir=''

tz=pytz.timezone('US/Eastern')

tv_flairs={'BTN':'[Big Ten Network](#l/btn)','CBS':'[CBS](#l/cbs)','CBSSN':'[CBS Sports Network](#l/cbssn)','ESPN':'[ESPN](#l/espn)','ESPN2':'[ESPN2](#l/espn2)','ESPN3':'[ESPN3](#l/espn3)','ESPNU':'[ESPNU](#l/espnu)','FOX':'[Fox](#l/fox)','FS1':'[Fox Sports 1](#l/fs1)','FSN':'[Fox Sports Network](#l/fsn)','Longhorn Network':'[Longhorn Network](#l/lhn)','NBC':'[NBC](#l/nbc)','NBCSN':'[NBC Sports Network](#l/nbcsn)','PAC12':'[Pac-12 Network](#l/p12n)','SECN':'[SEC Network](#l/secn)','TBS':'[TBS](#l/tbs)','TNT':'[TNT](#l/tnt)','truTV':'[truTV](#l/trutv)','ACCN':'[ACC Network](#l/accn)','ACCNE':'[ACC Network Extra](#l/accne)','ESPNN':'[ESPNews](#l/espnews)','FS2':'[Fox Sports 2](#l/fs2)'}

tv_stream_links={'BTN':'[FOX Sports GO](https://www.foxsportsgo.com/)','CBSSN':'[CBSSN](http://www.cbssports.com/watch/cbssportsnetwork/)','ESPN':'[WatchESPN](http://www.espn.com/watchespn/)','ESPN2':'[WatchESPN](http://www.espn.com/watchespn/)','ESPN3':'[WatchESPN](http://www.espn.com/watchespn/)','ESPNU':'[WatchESPN](http://www.espn.com/watchespn/)','ESPNN':'[WatchESPN](http://www.espn.com/watchespn/)','FOX':'[FOX Sports GO](https://www.foxsportsgo.com/)','FS1':'[FOX Sports GO](https://www.foxsportsgo.com/)','FSN':'[FOX Sports GO](https://www.foxsportsgo.com/)','Longhorn Network':'[WatchESPN](http://www.espn.com/watchespn/)','NBC':'[NBC Sports Live Extra](http://www.nbcsports.com/live)','NBCSN':'[NBC Sports Live Extra](http://www.nbcsports.com/live)','PAC12':'[PAC12](http://pac-12.com/live)','SECN':'[WatchESPN](http://www.espn.com/watchespn/)','ACCN':'[WatchESPN](http://www.espn.com/watchespn/)','ACCNE':'[WatchESPN](http://www.espn.com/watchespn/)','ESPN+':'[ESPN+](https://plus.espn.com/)','FS2':'[FOX Sports GO](https://www.foxsportsgo.com/)'}

try: #import if praw is happy, quit this cycle if not
  import praw
  from praw.models import Message
  print('Imported praw! '+str(datetime.datetime.now(tz)))
except:
  print('Failed to import praw. Shutting down..... '+str(datetime.datetime.now(tz)))
  quit()

def get_info(game_id):
  (away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,time_of_game,game_time,away_score,home_score)=cbbBot_func.espn(game_id)
  with open('cbbBot/ranking.txt','r') as imp_file:
    lines=imp_file.readlines()
  (teams,rank_names)=cbbBot_func.get_teams()
  ranking={}
  for line in lines:
    (team,rank)=line.replace('\n','').split(',')
    team=team.replace('&amp;','&')
    ranking[team]=int(rank)
  away_rank,home_rank='','' #clear ESPN rank values
  away_flair,home_flair='',''
  if away_team in teams.keys():
    if rank_names[away_team] in ranking.keys():
      away_rank='#'+str(ranking[rank_names[away_team]])
    away_flair=teams[away_team]
  if home_team in teams.keys():
    if rank_names[home_team] in ranking.keys():
      home_rank='#'+str(ranking[rank_names[home_team]])
    home_flair=teams[home_team]
  return away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,time_of_game,away_flair,home_flair,game_time,away_score,home_score

def get_stream(game_id):
  with open('cbbBot/streams.txt','r',encoding='utf-8-sig') as imp_file:
    lines=imp_file.readlines()
  streams={}
  for line in lines:
    (espn,ncaa)=line.replace('\n','').split(',')
    streams[espn]=ncaa
  if game_id in streams.keys():
    return '[March Madness Live](https://smart.link/58c2fa27d6415?cid=mml_partner_reddit&game='+streams[game_id]+')'
  return ''

def make_thread(game_id,away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,time_of_game,away_flair,home_flair,game_time,away_score,home_score,comment_stream_link=''):
  #try:
  #  (away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,month,day,hour,minute,away_flair,home_flair,game_time,away_score,home_score)=get_info(game_id)
  #  print('Making thread '+game_id+' ..... '+str(datetime.datetime.now(tz)))
  #except:
  #  print('Failed to make thread for '+game_id+'. '+str(datetime.datetime.now(tz)))
  #  return ''
  if game_time!='':
    away_score,home_score,game_time='**'+str(away_score)+'**','**'+str(home_score)+'**','- **'+game_time+'**'
  if away_flair=='':
    thread=away_team
  else:
    thread=away_flair
  thread=thread+' '+away_score+' @ '+home_score+' '
  if home_flair=='':
    thread=thread+home_team
  else:
    thread=thread+home_flair
  thread=thread+' '+game_time+'\n\n\n###NCAA Basketball\n [**^Click ^here ^to ^request ^a ^Game ^Thread**](https://www.reddit.com/r/CollegeBasketball/comments/5o5at9/introducing_ucbbbot_an_easier_way_of_making_game/)\n\n---\n '
  if away_record=='':
    away_record='--'
  if home_record=='':
    home_record='--'
  if away_rank!='':
    away_rank=away_rank+' '
  if home_rank!='':
    home_rank=home_rank+' '
  thread=thread+away_flair+' **'+away_rank+away_team+'** ('+away_record+') @ '+home_flair+' **'+home_rank+home_team+'** ('+home_record+')\n\nTip-Off: '
  minute=time_of_game.minute
  if time_of_game.minute<10:
    minute='0'+str(minute)
  if time_of_game.hour>12:
    time=str(time_of_game.hour-12)+':'+str(minute)+' PM ET'
  elif time_of_game.hour==12:
    time='12:'+str(minute)+' PM ET'
  else:
    time=str(time_of_game.hour)+':'+str(minute)+' AM ET'
  if network=='':
    network='Check your local listings.'
  network_flair=network
  if network in tv_flairs.keys():
    network_flair=tv_flairs[network]
  thread=thread+time+'\n\nVenue: '+venue+', '+city_state+'\n\n-----------------------------------------------------------------\n\n**[Join us on Discord for more college basketball discussion!](https://discordapp.com/invite/74Bswry)** \n\n-----------------------------------------------------------------\n\n**Television:** \n'+network_flair+'\n\n\n**Streams:**\n'
  if network in tv_stream_links.keys():
    thread=thread+tv_stream_links[network]+'\n'
  espn_link='http://www.espn.com/mens-college-basketball/game?gameId='+game_id
  stream_link=get_stream(game_id)
  thread=thread+stream_link+"\n\n-----------------------------------------------------------------\n\n**Thread Notes:**\n\n- I'm a bot! Don't be afraid to leave feedback!\n\n- Follow the game on [ESPN]("+espn_link+") for preview, play-by-play, more stats, and recap.\n\n- Discuss whatever you wish. You can trash talk, but keep it civil.\n\n- Turning comment sort to 'new' will help you see the newest posts.\n\n- Try [Chrome Refresh](https://chrome.google.com/extensions/detail/aifhnlnghddfdaccgbbpbhjfkmncekmn) or Firefox's [AutoReload](https://addons.mozilla.org/en-US/firefox/addon/auto-reload-tab/) to auto-refresh this tab.\n\n- You may also like [reddit stream]("+comment_stream_link+") to keep up with comments.\n\n- [Follow @redditCBB](https://twitter.com/redditCBB) on twitter for news, updates, and bad attempts at humor.\n\n- Show your team affiliation - get a team logo by clicking 'Select Flair' on the right."
  #thread=thread+"r/ncaaBBallStreams\n\n-----------------------------------------------------------------\n\n**Thread Notes:**\n\n- I'm a bot! Don't be afraid to leave feedback!\n\n- Follow the game on [ESPN]("+espn_link+") for preview, play-by-play, more stats, and recap.\n\n- Discuss whatever you wish. You can trash talk, but keep it civil.\n\n- Turning comment sort to 'new' will help you see the newest posts.\n\n- Try [Chrome Refresh](https://chrome.google.com/extensions/detail/aifhnlnghddfdaccgbbpbhjfkmncekmn) or Firefox's [AutoReload](https://addons.mozilla.org/en-US/firefox/addon/auto-reload-tab/) to auto-refresh this tab.\n\n- You may also like [reddit stream]("+comment_stream_link+") to keep up with comments.\n\n- [Follow @redditCBB](https://twitter.com/redditCBB) on twitter for news, updates, and bad attempts at humor.\n\n- Show your team affiliation - get a team logo by clicking 'Select Flair' on the right."
  #thread=thread+"\n\n\n**Subscribe to these communities** \n\n"
  #away_sub='r/AwayTeam'
  #home_sub='r/HomeTeam'
  #thread=thread+away_sub+' | '+home_sub
  title='[Game Thread] '+away_rank+away_team+' @ '+home_rank+home_team+' ('+time+')'
  print('Made thread for game '+game_id+'! '+str(datetime.datetime.now(tz)))
  return title,thread

with open('client.txt','r') as imp_file:
  lines=imp_file.readlines()
lines=[line.replace('\n','') for line in lines]

try:
  r = praw.Reddit(client_id=lines[0],client_secret=lines[1],username="cbbBot",password=lines[2],user_agent="CBB Bot v3.1") #define praw and user agent, login
  print('Logged in to Reddit! '+str(datetime.datetime.now(tz)))
except:
  print('Failed to login to Reddit. Shutting down..... '+str(datetime.datetime.now(tz)))
  quit()

try:
  thread=r.submission(id='5ctg2v') #get thread to edit
  thread.edit(datetime.datetime.now(tz)) #edit same thread with current timestamp; let's me know that the bot is running
  print('Edited check thread with current time and date! '+str(datetime.datetime.now(tz)))
except:
  print('Failed to edit thread with current time and date. Will continue..... '+str(datetime.datetime.now(tz)))

hour,minute=datetime.datetime.now(tz).hour,datetime.datetime.now(tz).minute

if hour==10 and minute==8: #if 10:02, automatically add top 25 games
  print('Gathering games for new day ..... '+str(datetime.datetime.now(tz)))
  try:
    cbbBot_func.get_rcbb_rank()
    os.system('python3 cbbBot_newday2.py')
    print('Gathered games for new day! '+str(datetime.datetime.now(tz)))
  except:
    print('Failed to gather games for new day. Will continue ..... '+str(datetime.datetime.now(tz)))

requested_games=[]
blacklist=[]

stoppers=['Ike348','1hive']
try:
  print('Checking mail..... '+str(datetime.datetime.now(tz)))
  for message in r.inbox.unread(): #look for requests
    body=message.body
    subject=message.subject
    if isinstance(message, Message):
      if subject.lower()=='request' and len(body)==9: #if message is a game request
        requested_games.append(body) #add game to queue
        message.reply('Thanks for your message. The game you requested has been successfully added to the queue and will be created within an hour of the scheduled game time. If the game has already started, the thread will be created momentarily. If the game is over, no thread will be created.')
        print('Added game '+body+' to queue! '+str(datetime.datetime.now(tz)))
      elif message.author in stoppers and subject.lower()=='stop': #if admin wants to prevent game thread from being made
        blacklist.append(body)
        message.reply('No game thread will be created for '+body+'!')
      else:
        message.reply('Thanks for your message. If you are trying to submit a game thread request, please make sure your title is "request" (case-insensitive) and the body contains only the ESPN game ID. If your request is successful, you will get a confirmation reply. If you have a question/comment about the bot, please send to u/Ike348.')
    message.mark_read()

except:
  print('Could not check messages. Will continue. '+str(datetime.datetime.now(tz)))

with open(dir+'cbbBot/games_to_write.txt','r') as imp_file: #get day's games from newday script
    games=imp_file.readlines()

with open(dir+'cbbBot/blacklist.txt','a') as f: #add blacklisted games to file
  for game in blacklist:
    f.write(game+'\n')
    print('Bot will not write game '+game+'. '+str(datetime.datetime.now(tz)))

with open(dir+'cbbBot/blacklist.txt','r') as imp_file: #get all blacklisted games from file
  lines=imp_file.readlines()
blacklist=[]
for line in lines:
  blacklist.append(line.replace('\n',''))

with open(dir+'cbbBot/games_to_write.txt','a') as f: #add requested games to list of games to make
  for game in requested_games:
    if game+'\n' not in games:
      f.write(game+'\n')
      print('Bot knows to write game '+game+'. '+str(datetime.datetime.now(tz)))

print('Checking which games have already been posted..... '+str(datetime.datetime.now(tz)))
already_posted={}
for post in r.redditor('cbbBot').submissions.new(limit=1000): #see which games already have threads
  if post.subreddit=='CollegeBasketball':
    game_id=post.selftext[post.selftext.find('http://www.espn.com/mens-college-basketball/game?gameId=')+56:post.selftext.find('http://www.espn.com/mens-college-basketball/game?gameId=')+65]
    already_posted[game_id]=post.id

games_over=[]
with open('cbbBot/games_over.txt','r') as imp_file: #see which games are already over
  lines=imp_file.readlines()
for line in lines:
  games_over.append(line.replace('\n',''))

print('Checking games..... '+str(datetime.datetime.now(tz)))

for game in games:
  game=game.replace('\n','')
  if game not in games_over:
    print('Getting game info for '+game+'..... '+str(datetime.datetime.now(tz)))
    try:
      (away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,time_of_game,away_flair,home_flair,game_time,away_score,home_score)=get_info(game)
      print('Obtained game info for '+game+'! '+str(datetime.datetime.now(tz)))
      if game not in already_posted.keys():
        if datetime.datetime.now(tz)>(time_of_game-datetime.timedelta(minutes=60)) and 'FINAL' not in game_time and game not in blacklist: #if time is later than 60 minutes before game time, and game is not over, post thread, write thread_id to file
          print('Posting game '+game+' ..... '+str(datetime.datetime.now(tz)))
          try:
            (title,thread_text)=make_thread(game,away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,time_of_game,away_flair,home_flair,game_time,away_score,home_score)
            thread=r.subreddit('CollegeBasketball').submit(title=title,selftext=thread_text,send_replies=False)
            thread.flair.select('2be569e0-872b-11e6-a895-0e2ab20e1f97')
            print('Posted game thread '+game+'! '+str(datetime.datetime.now(tz)))
          except:
            print('Failed to post game '+game+'. '+str(datetime.datetime.now(tz)))
        else:
          print('Game '+game+' will not be posted at this time. '+str(datetime.datetime.now(tz)))
      else:
        if datetime.datetime.now(tz)>time_of_game+datetime.timedelta(hours=4):
          with open('cbbBot/games_over.txt','a') as f:
            f.write(game+'\n')
        try:
          thread=r.submission(id=already_posted[game]) #find already posted thread
          comment_stream_link='http://www.reddit-stream.com/'+thread.permalink
          (title,thread_text)=make_thread(game,away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,time_of_game,away_flair,home_flair,game_time,away_score,home_score,comment_stream_link) #re-write thread
          thread.edit(thread_text) #edit thread
          print('Edited thread '+game+'! '+str(datetime.datetime.now(tz)))
        except:
          print('Failed to edit thread '+game+'. Will continue..... '+str(datetime.datetime.now(tz)))
    except:
      print('Failed to get game info for '+game+'. '+str(datetime.datetime.now(tz)))
