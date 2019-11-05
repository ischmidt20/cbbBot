#!/Usr/bin/python3
import urllib.request
import os
import datetime
import pytz

tz=pytz.timezone('US/Eastern')

def get_teams():
  with open('cbbBot/team_list.txt','r') as imp_file:
    lines=imp_file.readlines()
  flairs={}
  rank_names={}
  for line in lines:
    (team,flair,rank_name)=line.replace('\n','').split(',')
    flairs[team]=flair
    rank_names[team]=rank_name
  return flairs,rank_names

def get_rcbb_rank():
  (flairs,rank_names)=get_teams()
  url='http://cbbpoll.com/'
  urllib.request.urlretrieve(url,'cbbBot/ranking.html')
  with open('cbbBot/ranking.html','r') as imp_file:
    lines=imp_file.readlines()
  ranking,first_place_votes=[],[]
  i=1
  while i<125:
    first_place_votes.append('('+str(i)+')')
    i=i+1
  rank_names_inv={}
  for team in list(rank_names.keys()):
    rank_names_inv[team[1]] = team[0]
  for line in lines:
    if "<td><span class='team-name'>" in line:
      team_rank=lines[lines.index(line)-1].replace('<td>','').replace('</td>','')
      line=line.replace('&#39;',"'").replace('&#38;','&')
      begin=line.find('></span>')
      end=line.find('</span></td>')
      team=line[begin+9:end]
      for vote in first_place_votes:
        if vote in team:
          team=team.replace(vote,'')
          break
      ranking.append(rank_names_inv[team.replace('&amp;','&')]+','+str(int(team_rank)))
  os.remove('cbbBot/ranking.html')
  with open('cbbBot/ranking.txt','w') as f:
    for team in ranking:
      f.write(team+'\n')

def espn(game_id):
  url='http://www.espn.com/mens-college-basketball/game?gameId='+game_id
  urllib.request.urlretrieve(url,'cbbBot/'+game_id+'.html')
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

  time_of_game=pytz.utc.localize(datetime.datetime.strptime(time_of_game,'%Y-%m-%dT%H:%MZ')).astimezone(tz)

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

  os.remove('cbbBot/'+game_id+'.html')
  return away_rank,away_team,away_record,home_rank,home_team,home_record,venue,city_state,network,time_of_game,game_time,away_score,home_score
