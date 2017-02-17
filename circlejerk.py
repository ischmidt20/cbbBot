#!/Usr/bin/python3
import random

teams_beaten_test={'A':['B','E','G'],'B':['C','D','E','G'],'C':['A','D'],'D':['A','E','F','G'],'E':['C','F'],'F':['A','B','C','G'],'G':['C','E']}

with open('circle_list.txt','r') as imp_file:
  lines=imp_file.readlines()
best_circle=[]
for line in lines:
  best_circle.append(line.replace('\n',''))

def get_scores():
  with open('ncaa_scores.txt','r') as imp_file:
    games=imp_file.readlines()
  scores=[]
  for game in games:
    (date,winner,w_score,loser,l_score)=game.replace('@','').replace('\n','').split(',')
    scores.append((date,winner,w_score,loser,l_score))
  for team in best_circle:
    for score in scores:
      (date,winner,w_score,loser,l_score)=score
      try:
        if winner==team and loser==best_circle[best_circle.index(team)+1]:
          print(winner+' def. '+loser+' - '+w_score+'-'+l_score+', '+date)
          break
      except:
        if winner==team and loser==best_circle[0]:
          print(winner+' def. '+loser+' - '+w_score+'-'+l_score+', '+date)
          break

def add_team():
  (teams_beaten,losses)=ncaa_dict()
  circle=best_circle.copy()
  bad_lists=[]
  max_size=340
  while len(circle) <= len(teams_beaten.keys()):
    if 'TAM C. Christi' in circle and len(circle)>max_size:
      max_size=len(circle)
      print(len(circle),circle)
    beaten_teams=teams_beaten[circle[-1]].copy() #2
    beaten_2,picked=[],False
    beaten_teams=teams_beaten[circle[-1]].copy()
    while not picked and len(beaten_teams)>0:
      picked_team=random.choice(beaten_teams)
      if picked_team in circle:
        beaten_teams.pop(beaten_teams.index(picked_team))
      if picked_team not in circle:
        circle.append(picked_team)
        if circle in bad_lists:
          circle=circle[:-1]
          beaten_teams.pop(beaten_teams.index(picked_team))
        else:
          picked=True
    if not picked: #3
      bad_lists.append(circle)
    if circle in bad_lists: #5
      if len(circle)<=1:
        circle=list(circle_o)
      else:
        circle=circle[:-1]

def get_teams(best_circle):
  all_teams=ncaa_dict()[0].keys()
  for team in all_teams:
    if team not in best_circle:
      print(team)
  
def circle1():
  (teams_beaten,losses)=ncaa_dict()
  circle=[random.choice(list(teams_beaten.keys()))] #1
  circle_o=['Chicago St','W Illinois']
  circle=['Chicago St','W Illinois']
  max_size=0
  #circle=[random.choice(list(teams_beaten.keys()))]
  bad_lists=[]
  while len(circle) <= len(teams_beaten.keys()):
    #print(len(circle))
    if len(circle)>max_size:
      max_size=len(circle)
      print(max_size,circle)
    beaten_teams=teams_beaten[circle[-1]].copy() #2
    beaten_2,picked=[],False
    for team in teams_beaten[circle[-1]].copy():
      if team not in circle and (team not in beaten_2):
        beaten_2.append(team)
    while not picked and len(beaten_2)>0:
      probs=[]
      summ=0
      for team in beaten_2:
        summ=summ+1/losses[team]
        probs.append(summ)
      k=1/summ
      for prob in probs:
        probs[probs.index(prob)]=prob*k
      rand=random.random()
      for prob in probs:
        if rand>prob:
          continue
        if rand<prob:
          picked_team=beaten_2[probs.index(prob)]
          picked=True
          break
      circle.append(picked_team)
      if circle in bad_lists:
        circle=circle[:-1]
        beaten_2.pop(beaten_2.index(picked_team))
        picked=False
    if len(beaten_2)==0:
      bad_lists.append(circle)

    if len(circle)==len(teams_beaten.keys()): #4
      if circle[0] in teams_beaten[circle[-1]]:
        return circle
      else:
        bad_lists.append(circle)
    if circle in bad_lists: #5
      if len(circle)<=1:
        #circle=[random.choice(list(teams_beaten.keys()))]
        circle=list(circle_o)
      else:
        circle=circle[:-1]

def circle2():
  (teams_beaten,losses)=ncaa_dict()
  circle=[random.choice(list(teams_beaten.keys()))] #1
  circle_o=['Chicago St','W Illinois']
  circle=['Chicago St','W Illinois']
  max_size=0
  #circle=[random.choice(list(teams_beaten.keys()))]
  bad_lists=[]
  while len(circle) <= len(teams_beaten.keys()):
    #print(len(circle))
    if len(circle)>max_size:
      max_size=len(circle)
      print(max_size,circle)
    beaten_teams=teams_beaten[circle[-1]].copy() #2
    beaten_2,picked=[],False
    beaten_teams=teams_beaten[circle[-1]].copy()
    while not picked and len(beaten_teams)>0:
      picked_team=random.choice(beaten_teams)                                                                                    
      if picked_team in circle:                                                                                                  
        beaten_teams.pop(beaten_teams.index(picked_team))                                                                        
      if picked_team not in circle:                                                                                              
        circle.append(picked_team)                                                                                               
        if circle in bad_lists:                                                                                                  
          circle=circle[:-1]                                                                                                     
          beaten_teams.pop(beaten_teams.index(picked_team))                                                                      
        else:                                                                                                                    
          picked=True                                                                                                            
    if not picked: #3                                                                                                            
      bad_lists.append(circle)
    if len(circle)==len(teams_beaten.keys()): #4
      if circle[0] in teams_beaten[circle[-1]]:
        return circle
      else:
        bad_lists.append(circle)
    if circle in bad_lists: #5
      if len(circle)<=1:
        #circle=[random.choice(list(teams_beaten.keys()))]
        circle=list(circle_o)
      else:
        circle=circle[:-1]

def circle3():
  (teams_beaten,losses)=ncaa_dict()
  circle=[random.choice(list(teams_beaten.keys()))] #1
  circle_o=['Chicago St','W Illinois']
  circle=['Chicago St','W Illinois']
  max_size=0
  #circle=[random.choice(list(teams_beaten.keys()))]
  bad_lists=[]
  while len(circle) <= len(teams_beaten.keys()):
    #print(len(circle))
    if len(circle)>max_size:
      max_size=len(circle)
      print(max_size,circle)
    beaten_teams=teams_beaten[circle[-1]].copy() #2
    beaten_2,picked=[],False
    beaten_teams=teams_beaten[circle[-1]].copy()
    while not picked and len(beaten_teams)>0:
      l=[]
      for team in beaten_teams:
        l.append(losses[team])
      picked_team=beaten_teams[l.index(min(l))]
      if picked_team in circle:
        beaten_teams.pop(beaten_teams.index(picked_team))
      if picked_team not in circle:
        circle.append(picked_team)
        if circle in bad_lists:
          circle=circle[:-1]
          beaten_teams.pop(beaten_teams.index(picked_team))
        else:
          picked=True
    if not picked: #3  
      bad_lists.append(circle)

    if len(circle)==len(teams_beaten.keys()): #4
      if circle[0] in teams_beaten[circle[-1]]:
        return circle
      else:
        bad_lists.append(circle)
    if circle in bad_lists: #5
      if len(circle)<=1:
        #circle=[random.choice(list(teams_beaten.keys()))]
        circle=list(circle_o)
      else:
        circle=circle[:-1]

def ncaa_dict():
  with open('ncaa_scores.txt','r') as imp_file:
    games=imp_file.readlines()
  teams_beaten,losses={},{}
  for game in games:
    (date,winner,w_score,loser,l_score)=game.replace('@','').replace('\n','').split(',')
    if winner not in teams_beaten.keys():
      teams_beaten[winner]=[]
    if loser not in losses.keys():
      losses[loser]=0
    if loser not in teams_beaten[winner]:
      losses[loser]=losses[loser]+1
    teams_beaten[winner].append(loser)
  return teams_beaten,losses

def epl_dict():
  with open('epl_scores.txt','r') as imp_file:
    games=imp_file.readlines()
  teams_beaten={}
  for game in games:
    (home,away,score)=game.replace('@','').replace('\n','').split(',')
    (h_score,a_score)=score.split(':')
    if away not in teams_beaten:
      teams_beaten[away]=[]
    if home not in teams_beaten:
      teams_beaten[home]=[]
    if a_score==h_score:
      teams_beaten[away].append(home)
    if h_score==a_score:
      teams_beaten[home].append(away)
  return teams_beaten
