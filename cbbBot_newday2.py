#!/Usr/bin/python3
import urllib.request
import os
import datetime
import pytz

dir='/home/i/is/ischmidt/cbbBot/'
#dir=''

tz=pytz.timezone('US/Eastern')
now=datetime.datetime.now(tz)
year=str(now.year)
month=str(now.month)
if now.month<10:
  month='0'+str(now.month)
day=str(now.day)
if now.day<10:
  day='0'+str(now.day)

year,month,day='2019','11','05'

url='http://www.espn.com/mens-college-basketball/schedule/_/date/'+year+month+day+'/'
urllib.request.urlretrieve(url,dir+'schedule.html')

with open(dir+'schedule.html','r') as imp_file:
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

os.remove(dir+'schedule.html')

with open(dir+'cbbBot/ranking.txt','r') as imp_file:
  lines=imp_file.readlines()
ranking=[]
for line in lines:
  ranking.append(line.replace('\n','').split(',')[0])

games_added=[]
with open(dir+'cbbBot/games_to_write.txt','r') as f:
  lines=f.readlines()

for line in lines:
  games_added.append(line.replace('\n',''))
#print(games_added)

with open(dir+'cbbBot/games_to_write.txt','a') as f: #create today's file
  for game in games:
    #print(game[0],game[1])
    if (game[0] in ranking or game[1] in ranking) and game[2] not in games_added:
        f.write(game[2]+'\n')
