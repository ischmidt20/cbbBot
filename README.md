# cbbBot
Automatically creates game threads for r/CollegeBasketball.
Requires directory (see 'home/ischmidt/cbbBot' in files) to download files to as bot does its work.

Overview of files:
- cbbBot.py: The actual bot. Logs into Reddit, checks messages, creates, edits, and submits threads, etc.
- cbbBot_func.py: Contains various functions used by cbbBot. Gets r/CollegeBasketball ranking, gets game info from ESPN, and matches different names for the same team.
- cbbBot_get_teams.py: Basic script to collect ESPN team codes.
- cbbBot_newday.py: Automatically schedules Top 25 games for the day.
- cbbBot/team_list.txt: List of teams with their ESPN team code, the corresponding logo flair, and the team code for cbbpoll.com.
- cbbBot/games_to_write.txt and cbbBot/games_over.txt: Files that keep track of the games that the bot will create threads for, and keep track of which games are over and no longer need to be edited, respectively.
- cbbBot/blacklist.txt: List of games for which games threads will not be made, as requested by select "blacklister."
