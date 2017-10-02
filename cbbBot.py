#!/Usr/bin/python3
import urllib.request
import shutil
import os
import time
import datetime
import cbbBot_func
import pytz

tz=pytz.timezone('US/Eastern')

tv_flairs={'BTN':'[Big Ten Network](#f/btn)','CBS':'[CBS](#f/cbs)','CBSSN':'[CBS Sports Network](#f/cbssn)','ESPN':'[ESPN](#f/espn)','ESPN2':'[ESPN2](#f/espn2)','ESPN3':'[ESPN3](#f/espn3)','ESPNU':'[ESPNU](#f/espnu)','FOX':'[Fox](#f/fox)','FS1':'[Fox Sports 1](#f/fs1)','FSN':'[Fox Sports Network](#f/fsn)','Longhorn Network':'[Longhorn Network](#f/lhn)','NBC':'[NBC](#f/nbc)','NBCSN':'[NBC Sports Network](#f/nbcsn)','PAC12':'[Pac-12 Network](#f/p12n)','SECN':'[SEC Network](#f/secn)','TBS':'[TBS](#f/tbs)','TNT':'[TNT](#f/tnt)','truTV':'[truTV](#f/trutv)'}

tv_stream_links={'BTN':'[BTN2GO](https://www.btn2go.com/)','CBSSN':'[CBSSN](http://www.cbssports.com/watch/cbssportsnetwork/)','ESPN':'[WatchESPN](http://www.espn.com/watchespn/)','ESPN2':'[WatchESPN](http://www.espn.com/watchespn/)','ESPN3':'[WatchESPN](http://www.espn.com/watchespn/)','ESPNU':'[WatchESPN](http://www.espn.com/watchespn/)','ESPNN':'[WatchESPN](http://www.espn.com/watchespn/)','FOX':'[FOX Sports GO](https://www.foxsportsgo.com/)','FS1':'[FOX Sports GO](https://www.foxsportsgo.com/)','FSN':'[FOX Sports GO](https://www.foxsportsgo.com/)','Longhorn Network':'[WatchESPN](http://www.espn.com/watchespn/)','NBC':'[NBC Sports Live Extra](http://www.nbcsports.com/live)','NBCSN':'[NBC Sports Live Extra](http://www.nbcsports.com/live)','PAC12':'[PAC12](http://pac-12.com/live)','SECN':'[WatchESPN](http://www.espn.com/watchespn/)'}

try: #import if praw is happy, quit this cycle if not
  import praw
  from praw.models import Message
  print('Imported praw! '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
except:
  print('Failed to import praw. Shutting down..... '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
  quit()

def get_info(game_id):
  print('Getting game info for '+game_id+'..... '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
  try:
    (away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,month,day,hour,minute,game_time,away_score,home_score)=cbbBot_func.espn(game_id)
    ranking=cbbBot_func.get_rcbb_rank()
    away_rank,home_rank='','' #clear ESPN rank values
    if away_team in ranking: #see if Reddit ranked
      away_rank='#'+str(ranking.index(away_team)+1)
    if home_team in ranking: #see if Reddit ranked
      home_rank='#'+str(ranking.index(home_team)+1)
    teams=cbbBot_func.get_teams()
    away_flair,home_flair='',''
    if away_team in teams.keys():
      away_flair=teams[away_team]
    if home_team in teams.keys():
      home_flair=teams[home_team]
    print('Obtained game info for '+game_id+'! '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
    return away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,month,day,hour,minute,away_flair,home_flair,game_time,away_score,home_score
  except:
    print('Failed to get game info for '+game_id+'. '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))

def make_thread(away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,month,day,hour,minute,away_flair,home_flair,game_time,away_score,home_score,permalink=''):
  #try:
  #  (away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,month,day,hour,minute,away_flair,home_flair,game_time,away_score,home_score)=get_info(game_id)
  #  print('Making thread '+game_id+' ..... '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
  #except:
  #  print('Failed to make thread for '+game_id+'. '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
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
  if minute<10:
    minute='0'+str(minute)
  if hour>12:
    time=str(hour-12)+':'+str(minute)+' PM ET'
  elif hour==12:
    time='12:'+str(minute)+' PM ET'
  else:
    time=str(hour)+':'+str(minute)+' AM ET'
  if network=='':
    network='Check your local listings.'
  network_flair=network
  if network in tv_flairs.keys():
    network_flair=tv_flairs[network]
  thread=thread+time+'\n\nVenue: '+venue+', '+city_state+'\n\n-----------------------------------------------------------------\n\n**[Join the live IRC chat on freenode, #redditcbb](http://webchat.freenode.net/?channels=#redditcbb)** \n\n-----------------------------------------------------------------\n\n**Television:** \n'+network_flair+'\n\n\n**Streams:**\n'
  if network in tv_stream_links.keys():
    thread=thread+tv_stream_links[network]+'\n'
  espn_link='http://www.espn.com/mens-college-basketball/game?gameId='+game_id
  thread=thread+"r/ncaaBBallStreams\n\n-----------------------------------------------------------------\n\n**Thread Notes:**\n\n- I'm a bot! Don't be afraid to leave feedback!\n\n- Follow the game on [ESPN]("+espn_link+") for preview, play-by-play, more stats, and recap.\n\n- Discuss whatever you wish. You can trash talk, but keep it civil.\n\n- Turning comment sort to 'new' will help you see the newest posts.\n\n- Try [Chrome Refresh](https://chrome.google.com/extensions/detail/aifhnlnghddfdaccgbbpbhjfkmncekmn) or Firefox's [ReloadEvery](https://addons.mozilla.org/en-US/firefox/addon/115/) to auto-refresh this tab.\n\n- You may also like [reddit stream]("+permalink+") to keep up with comments.\n\n- [Follow @redditCBB](https://twitter.com/redditCBB) on twitter for news, updates, and bad attempts at humor.\n\n- Show your team affiliation - get a team logo by clicking 'edit' in the column on the right."
  #thread=thread+"\n\n\n**Subscribe to these communities** \n\n"
  #away_sub='r/AwayTeam'
  #home_sub='r/HomeTeam'
  #thread=thread+away_sub+' | '+home_sub
  title='[Game Thread] '+away_rank+away_team+' @ '+home_rank+home_team+' ('+time+')'
  print('Made thread for game '+game_id+'! '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
  return title,thread

try:
<<<<<<< HEAD
  r = praw.Reddit(client_id="yixQbUFcDcZVSQ",client_secret="-EH4dR9bNu0mJmBSftwWhPrHthU",username="cbbBot",password="ILoveCBB1",user_agent="CBB Bot v3") #define praw and user agent, login
=======
  r = praw.Reddit(client_id="",client_secret="",username="cbbBot",password="",user_agent="CBB Bot v3") #define praw and user agent, login
>>>>>>> 0fb77fbd10eb2b2f3d9a73ae9f62c1f30cffa3e5
  print('Logged in to Reddit! '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
except:
  print('Failed to login to Reddit. Shutting down..... '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
  quit()

try:
  thread=r.submission(id='5ctg2v') #get thread to edit
  thread.edit(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)) #edit same thread with current timestamp; let's me know that the bot is running
  print('Edited check thread with current time and date! '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
except:
  print('Failed to edit thread with current time and date. Will continue..... '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))

hour,minute=pytz.utc.localize(datetime.datetime.now()).astimezone(tz).hour,pytz.utc.localize(datetime.datetime.now()).astimezone(tz).minute

if hour==10 and minute==2: #if 10:02, automatically add top 25 games
  print('Gathering games for new day ..... '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
  try:
    os.system('python3 cbbBot_newday2.py')
    print('Gathered games for new day! '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
  except:
    print('Failed to gather games for new day. Will continue ..... '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))

requested_games=[]
blacklist=[]

stoppers=['Ike348','1hive']
try:
  print('Checking mail..... '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz))) 
  for message in r.inbox.unread(): #look for requests
    body=message.body
    subject=message.subject
    if isinstance(message, Message):
      if subject.lower()=='request' and len(body)==9: #if message is a game request
        requested_games.append(body) #add game to queue
        message.reply('Thanks for your message. The game you requested has been successfully added to the queue and will be created within an hour of the scheduled game time. If the game has already started, the thread will be created momentarily. If the game is over, no thread will be created.')
        print('Added game '+body+' to queue! '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
      elif message.author in stoppers and subject.lower()=='stop': #if admin wants to prevent game thread from being made
        blacklist.append(body)
        message.reply('No game thread will be created for '+body+'!')
      else:
        message.reply('Thanks for your message. If you are trying to submit a game thread request, please make sure your title is "request" (case-insensitive) and the body contains only the ESPN game ID. If your request is successful, you will get a confirmation reply. If you have a question/comment about the bot, please send to u/Ike348.')
    message.mark_read()

except:
  print('Could not check messages. Will continue. '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))

with open('/home/ischmidt/cbbBot/blacklist.txt','a') as f: #add blacklisted games to file
  for game in blacklist:
    f.write(game+'\n')
    print('Bot will not write game '+game+'. '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz))) 
    
with open('/home/ischmidt/cbbBot/blacklist.txt','r') as imp_file: #get all blacklisted games from file
  lines=imp_file.readlines()
blacklist=[]
for line in lines:
  blacklist.append(line.replace('\n',''))

with open('/home/ischmidt/cbbBot/games_to_write.txt','a') as f: #add requested games to list of games to make
  for game in requested_games:
    f.write(game+'\n')
    print('Bot knows to write game '+game+'. '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))

print('Checking which games have already been posted..... '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
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

with open('/home/ischmidt/cbbBot/games_to_write.txt','r') as imp_file: #get day's games from newday script
  games=imp_file.readlines()
  
print('Checking games..... '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
for game in games:
  game=game.replace('\n','')
  if game not in games_over:
    (away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,month,day,hour,minute,away_flair,home_flair,game_time,away_score,home_score)=get_info(game)
    sked_time=pytz.utc.localize(datetime.datetime.now()).astimezone(tz).replace(month=month,day=day,hour=hour,minute=minute)
    if game not in already_posted.keys():
      if pytz.utc.localize(datetime.datetime.now()).astimezone(tz)>(sked_time-datetime.timedelta(minutes=60)) and 'FINAL' not in game_time and game not in blacklist: #if time is later than 60 minutes before game time, and game is not over, post thread, write thread_id to file
        print('Posting game '+game+' ..... '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
        try:
          (title,thread_text)=make_thread(away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,month,day,hour,minute,away_flair,home_flair,game_time,away_score,home_score)
          thread=r.subreddit('CollegeBasketball').submit(title=title,selftext=thread_text,send_replies=False)
          thread.flair.select('2be569e0-872b-11e6-a895-0e2ab20e1f97')
          print('Posted game thread '+game+'! '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
        except:
          print('Failed to post game '+game+'. '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
      else:
        print('Game '+game+' will not be posted at this time. '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))  
    else:
      if pytz.utc.localize(datetime.datetime.now()).astimezone(tz)>sked_time+datetime.timedelta(hours=6):
        with open('cbbBot/games_over.txt','a') as f:
          f.write(game+'\n')
      try:
        thread=r.submission(id=already_posted[game]) #find already posted thread
        permalink='http://www.reddit-stream.com'+thread.permalink
        (title,thread_text)=make_thread(away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,month,day,hour,minute,away_flair,home_flair,game_time,away_score,home_score,permalink) #re-write thread
        thread.edit(thread_text) #edit thread
        print('Edited thread '+game+'! '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
      except:
        print('Failed to edit thread '+game+'. Will continue..... '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
