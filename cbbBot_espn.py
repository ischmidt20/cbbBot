#!/Usr/bin/python3
import urllib.request
import shutil
import os
import re

def get_info(game_id):
  url='http://www.espn.com/mens-college-basketball/game?gameId='+game_id
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

  os.remove(game_id+'.html')
  return away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,hour,minute
