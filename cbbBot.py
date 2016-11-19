#!/Usr/bin/python3
import urllib.request
import shutil
import os
import time
import re
import datetime
import praw
import cbbBot_espn

def get_info(game_id):
  (away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,hour,minute)=cbbBot_espn.get_info(game_id)
  return away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,hour,minute

def make_thread(game_id):
  (away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,hour,minute)=get_info(game_id)
  thread='###NCAA Basketball\n [**^Click ^here ^to ^create ^a ^Game ^Thread**](http://www.reddit.com/r/CollegeBasketball/comments/1pnabg/updated_game_thread_format/)\n\n---\n '
  away_flair,home_flair='[](/AwayTeamFlair)','[](/HomeTeamFlair)'
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
  thread=thread+time+'\n\nVenue: '+venue+', '+city_state+'\n\n-----------------------------------------------------------------\n\n**[Join the live IRC chat on freenode, #redditcbb](http://webchat.freenode.net/?channels=#redditcbb)** \n\n-----------------------------------------------------------------\n\n**Television:** \n'+network+'\n\n\n**Streams:**\nr/ncaaBBallStreams\n\n\n**Preview:** \n[ESPN]('
  link='http://www.espn.com/mens-college-basketball/game?gameId='+game_id
  thread=thread+link+")\n\n-----------------------------------------------------------------\n\n\n**Thread Notes:**\n\n- I'm a bot! Don't be afraid to leave feedback!\n\n- Discuss whatever you wish. You can trash talk, but keep it civil.\n\n- Turning comment sort to 'new' will help you see the newest posts.\n\n- Try [Chrome Refresh](https://chrome.google.com/extensions/detail/aifhnlnghddfdaccgbbpbhjfkmncekmn) or Firefox's [ReloadEvery](https://addons.mozilla.org/en-US/firefox/addon/115/) to auto-refresh this tab.\n\n- You may also like [reddit stream](http://www.reddit.com/r/CFB/comments/wn9uj/lets_discuss_game_threads_come_fall/c5esw1u) to keep up with comments.\n\n- [Follow @redditCBB](https://twitter.com/redditCBB) on twitter for news, updates, and bad attempts at humor.\n\n- Show your team affiliation - get a team logo by clicking 'edit' in the column on the right.\n\n\n**Subscribe to these communities** \n\n"
  away_sub='r/AwayTeam'
  home_sub='r/HomeTeam'
  thread=thread+away_sub+' | '+home_sub
  title='[Game Thread] '+away_rank+away_team+' @ '+home_rank+home_team+' ('+time+')'
  return title,thread

user_agent = ("CBB Bot v1.0")
r = praw.Reddit(user_agent = user_agent) #define praw and user agent

with open('/home/ischmidt/cbbLogin.txt','r') as imp_file:
  (username,password)=imp_file.readlines()[0].replace('\n','').split(',') #get bot username and password from file

r.login(username,password,disable_warning=True) #login to bot account
url="http://www.espn.com/ncb/bottomline/scores" #url for espn bottom line scores
#with urllib.request.urlopen(url) as response, open ('game_list.html','wb') as out_file:
 # shutil.copyfileobj(response, out_file)
#thread=r.submit("cbbBotTest","Can this bot post?",text="damn right it can",send_replies="False")
#thread_id=thread.short_link[15:]
thread=r.get_submission(submission_id='5ctg2v') #get thread to edit
thread.edit(datetime.datetime.now()) #edit same thread with current timestamp; let's me know that the bot is running

hour,minute=datetime.datetime.now().hour,datetime.datetime.now().minute
print(hour,minute)
if hour==11 and minute==4: #if certain time, get the games for that day
  try:
    os.remove('/home/ischmidt/games_to_write.txt')
  except:
    pass
  os.system('cd /home/ischmidt; python3 cbbBot_newday.py')


inbox=r.get_unread() #open mail
with open('/home/ischmidt/games_to_write.txt','r') as imp_file:
  games=imp_file.readlines() #get all games from today

game_ids=[]
requested_games=[]
for game in games:
  game_ids.append(game.split(',')[0]) #get list of ESPN game IDs

#print(game_ids)
for message in inbox: #look for requests
  body=message.body
  subject=message.subject
  if subject.lower()=='request' and body in game_ids: #if message is a game request
    requested_games.append(body) #add game to queue
  message.mark_as_read()

os.remove('/home/ischmidt/games_to_write.txt') #delete file, will be re-written
with open('/home/ischmidt/games_to_write.txt','w') as f:
  for game in games:
    if (game.split(',')[0]) not in requested_games or game.split(',')[1]=='True': #if game hasn't been newly requested, write same line
      f.write(game)
    if (game.split(',')[0]) in requested_games and game.split(',')[1]=='False': #if game has been newly requested, change request to True
      f.write(game.split(',')[0]+',True,False,0\n')


with open('/home/ischmidt/games_to_write.txt','r') as imp_file: #get day's games from newday script
  games=imp_file.readlines()

os.remove('/home/ischmidt/games_to_write.txt') #delete file, will be re-written

with open('/home/ischmidt/games_to_write.txt','w') as f:
  for game in games:
    game=game.replace('\n','').split(',') #turn line into list (espn_game_id,posted,thread_id)
    if game[1]=='False':
      f.write(game[0]+',False,False,0\n') #if the game won't be posted, write same thing
    if game[1]=='True':
      if game[2]=='True': #if already posted, just write same info to file, this is where threads will be edited later
        f.write(game[0]+',True,True,'+game[3]+'\n')
      if game[2]=='False': #if game not yet posted
        (away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,hour,minute)=get_info(game[0])

        if hour<11: #if game is early in the morning, make sure game time is next day
          game_time=(datetime.datime.now+datetime.timedelta(1)).replace(hour=hour,minute=minute)
        else:
          game_time=datetime.datetime.now().replace(hour=hour,minute=minute)
        if datetime.datetime.now()>(game_time-datetime.timedelta(minutes=15)): #if time is later than 15 minutes before game time, post thread, write thread_id to file
          sub='cbbBotTest'
          (title,thread_text)=make_thread(game[0])
          try:
            game_thread=r.submit(sub,title,text=thread_text,send_replies=False)
            thread_id=game_thread.short_link[15:]
            f.write(game[0]+',True,True,'+thread_id+'\n')
          except:
            f.write(game[0]+',True,False,0\n')
        else: #if we have to wait, write old same to file
          f.write(game[0]+',True,False,0\n')
