#!/Usr/bin/python3
import urllib.request
import os
import datetime
import pytz

dir='/home/ischmidt/'
dir=''
tz=pytz.timezone('US/Eastern')
date=pytz.utc.localize(datetime.datetime.now()).astimezone(tz)
teams={}
while date.replace(tzinfo=None)<datetime.datetime(year=2018,month=12,day=1):
  year=str(date.year)
  month=str(date.month)
  if date.month<10:
    month='0'+str(date.month)
  day=str(date.day)
  if date.day<10:
    day='0'+str(date.day)

  #year,month,day='2018','11','06'

  url='http://www.espn.com/mens-college-basketball/schedule/_/date/'+year+month+day+'/'
  urllib.request.urlretrieve(url,dir+'schedule.html')

  with open(dir+'schedule.html','r') as imp_file:
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
    id_begin=line.find('href="/mens-college-basketball/game?gameId=')
    id_end=line.find('">',id_begin)
    game_id=line[id_begin+43:id_end]
    if away_team not in teams.keys():
      teams[away_team]=0
    if home_team not in teams.keys():
      teams[home_team]=0
    teams[away_team],teams[home_team]=teams[away_team]+1,teams[home_team]+1
    line=line[id_end:]

  os.remove(dir+'schedule.html')

  date=date+datetime.timedelta(days=1)

for team in sorted(teams.items(), key=lambda x: x[1],reverse=True):
  print(team[0]+','+str(team[1]))
