#!/Usr/bin/python3
import urllib.request
import shutil
import os
import time
import re
import datetime

url='http://espn.go.com/ncb/bottomline/scores'
with urllib.request.urlopen(url) as response, open ('/home/ischmidt/ncb_scores.txt', 'wb') as out_file:
  shutil.copyfileobj(response, out_file)
with open('/home/ischmidt/ncb_scores.txt','r') as in_file:
  games=in_file.read().replace('%20',' ').replace('&ncb','\n&ncb').replace('%26','&')
g_list=games.split('\n')

games=[]
look_for_url=False
for line in g_list:
  if '&ncb_s_left' in line:
    game=line
    look_for_url=True
  if look_for_url:
    if 'ncb_s_url' in line:
      url=line[-9:]
      look_for_url=False
      games.append((url,game))

with open('/home/ischmidt/cbbBot/games_to_write.txt','w') as f: #create today's file
  for game in games:
    i=0
    top_25='False'
    while i<25:
      i=i+1
      if '('+str(i)+')' in game[1]: #top 25
        top_25='True'
        break
    f.write(game[0]+','+top_25+',False,0\n')

os.remove('/home/ischmidt/ncb_scores.txt')
