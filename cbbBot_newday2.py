#!/Usr/bin/python3
import urllib.request
import shutil
import os
import time
import re
import datetime
import cbbBot_func
import pytz

tz=pytz.timezone('US/Eastern')
year=str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz).year)
month=str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz).month)
if pytz.utc.localize(datetime.datetime.now()).astimezone(tz).month<10:
  month='0'+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz).month)
day=str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz).day)
if pytz.utc.localize(datetime.datetime.now()).astimezone(tz).day<10:
  day='0'+str(pytz.utc.localize(datetime.datetime.now()).astimezone(tz).day)
  
def game_list():
  url='http://www.espn.com/mens-college-basketball/schedule/_/date/'+year+month+day+'/'
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
    id_begin=line.find('href="/mens-college-basketball/game?gameId=')
    id_end=line.find('">',id_begin)
    game_id=line[id_begin+43:id_end]
    games.append((away_team,home_team,game_id))
    line=line[id_end:]  

  os.remove('schedule.html')
  return games

def part1():
  games=game_list()
  with open('/home/ischmidt/cbbBot/games_to_write.txt','w') as f: #create today's file
    for game in games:
      f.write(game[2]+',False,False,0\n')

def part2():
  games=game_list()
  ranking=cbbBot_func.get_rcbb_rank()
  with open('/home/ischmidt/cbbBot/games_to_write.txt','r') as imp_file:
    lines=imp_file.readlines()
  with open('/home/ischmidt/cbbBot/games_to_write.txt','w') as f:
    for line in lines:
      (game_id,scheduled,made,thread_id)=line.replace('/n','').split(',')
      top_25=False
      if games[lines.index(line)][0] in ranking or games[lines.index(line)][1] in ranking:
        top_25=True
        f.write(games[lines.index(line)][2]+',True,False,0\n')
      else:
        f.write(line)
