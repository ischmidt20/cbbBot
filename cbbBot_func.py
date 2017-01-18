#!/Usr/bin/python3
import urllib.request
import shutil
import os
import re

def similar(team):
  teams=get_teams()
  for name in teams.keys():
    if name==team:
      return name
  for name in teams.keys():
    if name.replace('State','St.')==team or name.replace('State','St')==team or team.replace('State','St.')==name or team.replace('State','St')==name or team.replace('St.','St')==name or name.replace('St.','')==team:
      return name
  for name in teams.keys():
    if name.replace('-',' ')==team or team.replace(' ','-')==name:
      return name
  for name in teams.keys():
    if name.replace('Saint','St.')==team or name.replace('Saint','St')==team or team.replace('Saint','St.')==name or team.replace('Saint','St')==name or team.replace('St.','St')==name or name.replace('St.','')==team:
      return name
  for name in teams.keys():
    if name in team or team in name:
      return name

def get_teams():
  with open('cbbBot/team_list.txt','r') as imp_file:
    lines=imp_file.readlines()
  teams={}
  for line in lines:
    (team,flair)=line.replace('\n','').split(',')
    teams[team]=flair
  return teams

def get_rcbb_rank():
  url='http://cbbpoll.com/'
  with urllib.request.urlopen(url) as response, open ('cbbBot/ranking.html', 'wb') as out_file:
    shutil.copyfileobj(response, out_file)
  with open('cbbBot/ranking.html','r') as imp_file:
    lines=imp_file.readlines()
  ranking,first_place_votes=[],[]
  i=1
  while i<125:
    first_place_votes.append('('+str(i)+')')
    i=i+1

  for line in lines:
    if "<td><span class='team-name'>" in line:
      line=line.replace('&#39;',"'").replace('&#38;','&')
      begin=line.find('></span>')
      end=line.find('</span></td>')
      team=line[begin+9:end]
      for vote in first_place_votes:
        if vote in team:
          team=team.replace(vote,'')
          break
      ranking.append(team)
  os.remove('cbbBot/ranking.html')
  teams_similar=[]
  for team in ranking:
    teams_similar.append(similar(team))
  return teams_similar

def espn(game_id):
  url='http://www.espn.com/mens-college-basketball/game?gameId='+game_id
  with urllib.request.urlopen(url) as response, open ('cbbBot/'+game_id+'.html', 'wb') as out_file:
    shutil.copyfileobj(response, out_file)
  with open('cbbBot/'+game_id+'.html','r') as imp_file:
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


  hour=(int(time_of_game[11:13])+19)%24
  minute=int(time_of_game[14:16])

  game_time='' 
  for line in lines:
    if 'class="game-time">' in line:
      gt_begin=line.find('class="game-time">')
      gt_end=line.find('</span>',gt_begin)
      game_time=line[gt_begin+18:gt_end]
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
    
  os.remove('cbbBot/'+game_id+'.html')
  return away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,hour,minute,game_time,away_score,home_score
