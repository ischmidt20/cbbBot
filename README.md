# cbbBot
Automatically creates game threads for r/CollegeBasketball.
Requires directory (see 'home/ischmidt/cbbBot' in files) to download files to as bot does its work.

Overview of files:
- cbbBot.py: The actual bot. Logs into Reddit, checks messages, creates, edits, and submits threads, etc.
- cbbBot_func.py: Contains various functions used by cbbBot. Gets r/CollegeBasketball ranking, gets game info from ESPN, and matches different names for the same team.
- cbbBot_newday.py: Antiquated process to get a list of games for each day, replaced by cbbBot_newday2.py.
- cbbBot_newday2.py: Contains two "new day" processes. The first gets a list of games each day, and the second schedules games involving Top 25 teams.
- cbbBot/team_list.txt: List of teams with their ESPN team name, and the corresponding logo flair.
