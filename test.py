import unittest
import json
from cbbBot_func import create_boxscore

class TestStringMethods(unittest.TestCase):
    def test_pregame(self):
        boxscore_string = '\n\nTeam | Streak | Points Per Game | Field Goal % | Three Point % | Rebounds Per Game | Assists Per Game | Blocks Per Game | Steals Per Game | Total Turnovers Per Game | Points Against\n----|----|----|----|----|----|----|----|----|----|----|\nBellarmine | L1 | 68.7 | 47.6 | 39.0 | 32.0 | 16.3 | 0.7 | 5.0 | 14.7 | 72.0\nNotre Dame | L2 | 73.3 | 43.6 | 41.1 | 33.5 | 14.8 | 3.8 | 3.7 | 11.8 | 77.7'
        with open('data/unplayed_boxscore.json') as f:
            data = json.load(f)
            self.assertEqual(create_boxscore('Bellarmine', 'Notre Dame', data), boxscore_string)

    def test_ingame(self):
        boxscore_string = '\n\nTeam | FG | Field Goal % | 3PT | Three Point % | FT | Free Throw % | Rebounds | Offensive Rebounds | Defensive Rebounds | Assists | Steals | Blocks | Turnovers | Technical Fouls | Flagrant Fouls | Fouls | Largest Lead\n----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|----|\nUCF | 26-57 | 45.6 | 9-21 | 42.9 | 14-24 | 58.3 | 27 | 6 | 21 | 8 | 6 | 4 | 8 | 4 | 0 | 22 | 13\nCincinnati | 23-52 | 44.2 | 5-17 | 29.4 | 19-24 | 79.2 | 41 | 11 | 30 | 15 | 3 | 1 | 19 | 5 | 0 | 25 | 7'
        with open('data/completed_boxscore.json') as f:
            data = json.load(f)
            self.assertEqual(create_boxscore('UCF', 'Cincinnati', data), boxscore_string)

if __name__ == '__main__':
    unittest.main()
