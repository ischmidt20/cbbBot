#!/Usr/bin/python3
import urllib.request
import shutil
import os
import pytz
import datetime
import praw

tz=pytz.timezone('US/Eastern')

r=praw.Reddit(client_id='wa8L2PyY12DSHg',client_secret='yqH47YE8uHow_SpmRXTB5JbaDbo',username='cfbStreamBot',password='FuckESPN1',user_agent='CFB Stream Bot 1.0')

def get_info(game_id):
  #print(game_id)
  url='http://www.espn.com/college-football/game?gameId='+game_id
  with urllib.request.urlopen(url) as response, open (game_id+'.html', 'wb') as out_file:
    shutil.copyfileobj(response, out_file)
  with open(game_id+'.html','r') as imp_file:
    lines=imp_file.readlines()
  for line in lines:
    if '<div id="custom-nav"' in line:
      info=line
      break
  at_begin=info.find('<span class="long-name">')
  at_end=info.find('<',at_begin+1)
  away_team=info[at_begin+24:at_end]

  home_info=info[at_end:]
  ht_begin=home_info.find('<span class="long-name">')
  ht_end=home_info.find('<',ht_begin+1)
  home_team=home_info[ht_begin+24:ht_end]

  #away_team,home_team=similar(away_team),similar(home_team)
  if info.find('<span class="rank">')==-1:
    away_rank,home_rank='',''
  else:
    if info.find('<span class="rank">')>at_begin:
      hrk_begin=info.find('<span class="rank">')
      hrk_end=info.find('<',hrk_begin+1)
      home_rank=info[hrk_begin+19:hrk_end]
      away_rank=''
    if info.find('<span class="rank">')<at_begin:
      ark_begin=info.find('<span class="rank">')
      ark_end=info.find('<',ark_begin+1)
      away_rank=info[ark_begin+19:ark_end]
      home_info=info[ark_end:]
      if home_info.find('<span class="rank">')==-1:
        home_rank=''
      else:
        hrk_begin=home_info.find('<span class="rank">')
        hrk_end=home_info.find('<',hrk_begin+1) 
        home_rank=home_info[hrk_begin+19:hrk_end] 
  if away_rank!='':
    away_rank='#'+away_rank
  if home_rank!='':
    home_rank='#'+home_rank

  arc_begin=info.find('<div class="record">')
  arc_end=info.find('<',arc_begin+1) #fix
  away_record=info[arc_begin+20:arc_end]
  home_info=info[arc_end:]
  hrc_begin=home_info.find('<div class="record">') 
  hrc_end=home_info.find('<',hrc_begin+1) #fix
  home_record=home_info[hrc_begin+20:hrc_end]

  lookup=False
  venue,network='',''
  for line in lines:
    if '<h1>Game Information</h1>' in line:
      lookup=True
    if lookup:
      if '<figure>' in line:
        venue=lines[lines.index(line)+4].replace('\t','').replace('\n','')
      else:
        if '<div class="location-details">' in line and venue=='':
          venue=lines[lines.index(line)+1][9:-8]
      if '<li class="icon-font-before icon-location-solid-before">' in line:
        city_state=lines[lines.index(line)+1].replace('\t','').replace('\n','') 
      if '<div class="game-network">' in line:
        network=lines[lines.index(line)+1].replace('\t','').replace('\n','').replace('Coverage: ','')
      if '<span data-date="' in line:
        time_of_game=line[22:39]
        
    if '</article>' in line:
      lookup=False
  
  time_of_game=datetime.datetime.strptime(time_of_game,'%Y-%m-%dT%H:%MZ')-datetime.timedelta(hours=4)
  
  game_time='' 
  for line in lines:
    if 'class="game-time' in line:
      gt_begin=line.find('>',line.find('<span class="game-time'))
      gt_end=line.find('</span>',gt_begin)
      game_time=line[gt_begin+1:gt_end]
      game_time=game_time.replace('<span class="status-detail">','')
      break
  game_time=game_time.replace(' Half','').replace(' - ',' ').upper()
  
  away_score,home_score='',''
  for line in lines:
    if '<div class="score icon-font-' in line:
      line=line.replace('before','').replace('after','')
      as_begin=line.find('<div class="score icon-font-')
      as_end=line.find('</div>',as_begin)
      away_score=line[as_begin+30:as_end]
      if away_score!='':
        away_score=int(away_score)
      line=line[as_end:]
      hs_begin=line.find('<div class="score icon-font-')
      hs_end=line.find('</div>',hs_begin)
      home_score=line[hs_begin+30:hs_end]
      if home_score!='':
        home_score=int(home_score)
      break
    
  os.remove(game_id+'.html')
  return away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,time_of_game,game_time,away_score,home_score

def make_thread(away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,time_of_game,game_time,away_score,home_score,game_id):
  if away_rank!='':
    away_rank=away_rank+' '
  if home_rank!='':
    home_rank=home_rank+' '
  minute=time_of_game.minute
  if time_of_game.minute<10:
    minute='0'+str(minute)
  if time_of_game.hour>12:
    time=str(time_of_game.hour-12)+':'+str(minute)+' PM ET'
  elif time_of_game.hour==12:
    time='12:'+str(minute)+' PM ET'
  else:
    time=str(time_of_game.hour)+':'+str(minute)+' AM ET'
  title='Game Thread: '+away_rank+away_team+' vs '+home_rank+home_team+' ('+time+')'
  if away_score!='':
    thread_text=away_team+' **'+str(away_score)+'**\n\n'+home_team+' **'+str(home_score)+'**\n\n**'+str(game_time)+'**\n\n'
  else:
    thread_text=away_team+'\n\n'+home_team+'\n\n'
  thread_text=thread_text+'[ESPN](http://www.espn.com/college-football/game?gameId='+game_id+')'
  return title,thread_text


url='http://www.espn.com/college-football/schedule/_/group/80/'
with urllib.request.urlopen(url) as response, open ('schedule.html', 'wb') as out_file:
  shutil.copyfileobj(response, out_file)
with open('schedule.html','r') as imp_file:
  lines=imp_file.readlines()
for line in lines:
  if 'data-behavior="schedule"' in line:
    break
games=[]
while '<tr class' in line:
  at_begin=line.find('<span>',line.find('class="team-name"'))
  at_end=line.find('</span>',at_begin)
  away_team=line[at_begin+6:at_end]
  ht_begin=line.find('<span>',at_end)
  ht_end=line.find('</span>',ht_begin)
  home_team=line[ht_begin+6:ht_end]
  id_begin=line.find('href="/college-football/game/_/')
  id_end=line.find('">',id_begin)
  game_id=line[id_begin+38:id_end]
  games.append((away_team,home_team,game_id))
  line=line[id_end:]
os.remove('schedule.html')


url='http://www.espn.com/college-football/schedule/_/group/81/'
with urllib.request.urlopen(url) as response, open ('schedule.html', 'wb') as out_file:
  shutil.copyfileobj(response, out_file)
with open('schedule.html','r') as imp_file:
  lines=imp_file.readlines()
for line in lines:
  if 'data-behavior="schedule"' in line:
    break
while '<tr class' in line:
  at_begin=line.find('<span>',line.find('class="team-name"'))
  at_end=line.find('</span>',at_begin)
  away_team=line[at_begin+6:at_end]
  ht_begin=line.find('<span>',at_end)
  ht_end=line.find('</span>',ht_begin)
  home_team=line[ht_begin+6:ht_end]
  id_begin=line.find('href="/college-football/game/_/')
  id_end=line.find('">',id_begin)
  game_id=line[id_begin+38:id_end]
  games.append((away_team,home_team,game_id))
  line=line[id_end:]
os.remove('schedule.html')              

#print(games)
print('Checking which games have already been posted..... '+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz)))
already_posted={}
for post in r.redditor('cfbStreamBot').submissions.new(limit=1000): #see which games already have threads
  if post.subreddit=='CFBStreams':
    game_id=post.selftext[post.selftext.find('http://www.espn.com/college-football/game?gameId=')+49:post.selftext.find('http://www.espn.com/college-football/game?gameId=')+58]
    already_posted[game_id]=post.id
print(already_posted)


for game in games:
  (away_team,home_team,game_id)=game
  (away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,time_of_game,game_time,away_score,home_score)=get_info(game_id)
  if game_id not in already_posted.keys():
    if pytz.utc.localize(datetime.datetime.now()).astimezone(tz).replace(tzinfo=None)>(time_of_game-datetime.timedelta(minutes=60)) and 'FINAL' not in game_time:
      (title,thread_text)=make_thread(away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,time_of_game,game_time,away_score,home_score,game_id)
      thread=r.subreddit('CFBStreams').submit(title=title,selftext=thread_text,send_replies=False)
  else:
    thread=r.submission(id=already_posted[game_id])
    (title,thread_text)=make_thread(away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,time_of_game,game_time,away_score,home_score,game_id)
    thread.edit(thread_text)
    if 'FINAL' in game_time:
      thread.delete()
