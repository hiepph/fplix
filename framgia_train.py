from sys import stdin
import sys
import random
import time
import copy
import os

try:
    EPOCH = int(os.getenv('EPOCH'))
except:
    EPOCH = 10462

# Board
W = 30
H = 20

# Bot
ACTIONS = {
    'L': 0,
    'R': 1,
    'U': 2,
    'D': 3
}

# Value points
POINTS = {
    '-2': 1000, # Oppo
    '-1': 100,  # Out of board
    '0' : 10,   # Empty
    '1' : 10,   # Stable
    '2' : 50,   # Unstable
    '3' : 15,   # Oppo's stable
    '4' : 50    # Oppo's unstable
}

# Reward points
# Board
FATAL_POINT = -100
BOOST_POINT = 10
STABLE_POINT = -10
EMPTY_POINT = 10
# Oppo
OPPO_STABLE_POINT = 15
KILL_POINT = 50
KILLED_POINT = -50

# Take risk (Higher value means more risk)
EPSILON = 0.2

# Vision
SIGHT = 5

from q import Q

def dump_q(q, n):
    f = open('q_%d' % n, 'wb')
    for k, v in q.iteritems():
        f.write('    ')
        f.write(str(k))
        f.write(': ')
        f.write(str(v))
        f.write(',\n')
    f.close()


class Board():
    def __init__(self):
        self.state = [['0' for y in range(W)] for x in range(H)]
        self.done = False

        # Out of board
        self.out = '-1'

        # Default bot id 1 for framgia
        self.stable = '1'
        self.unstable = '2'

        # Other bots
        self.oppo = '-2' # Head of bot
        self.oppo_stable = '3'
        self.oppo_unstable = '4'

    def view(self):
        if self.state is not None:
            for i in range(H):
                print ''.join(self.state[i])
        else:
            print 'None'

    def updateState(self, inputs):
        if not self.done:
            for i in range(H):
                line = inputs.readline()
                if line == '':
                    # end game
                    self.state = None
                    self.done = True
                else:
                    self.state[i] = list(line[:-1])

    def getCell(self, cell):
        """Get specific corresponding to cell
        Map value if necessary into keys of POINTS"""
        x, y = cell

        # Out of board
        if x not in range(H):
            return self.out
        if y not in range(W):
            return self.out

        # Map value
        value = self.state[x][y]
        if value in ['0', '1', '2']:
            return value
        elif value in ['3', '5', '7']:
            return '3'
        elif value in ['4', '6', '8']:
            return '4'
        else:
            # opponents
            return '-2'

    def getRadar(self, cells):
        points = {}
        max_val = None
        max_point = None
        for cell in cells:
            value = self.getCell(cell)

            if value not in points:
                points[value] = POINTS[value]
            else:
                points[value] += POINTS[value]

            if max_val is None:
                max_val = value
            if max_point is None:
                max_point = points[value]

            if points[value] > max_point:
                max_val = value
                max_point = points[value]

        return max_val

    def calcState(self, x, y, sight=5):
        """Make an overview of surrounded environment
        """

        left = [[x, w] for w in range(y-sight, y)]
        right = [[x, w] for w in range(y, y+sight+1)]
        up = [[h, y] for h in range(x-sight, x)]
        down = [[h, y] for h in range(x, x+sight+1)]

        left_up = []
        for h in range(x-sight, x):
            for w in range(y-sight, y):
                left_up.append([h, w])

        right_up = []
        for h in range(x-sight, x):
            for w in range(y, y+sight+1):
                right_up.append([h, w])

        left_down = []
        for h in range(x, x+sight+1):
            for w in range(y-sight, y):
                left_down.append([h, w])

        right_down = []
        for h in range(x, x+sight+1):
            for w in range(y, y+sight+1):
                right_down.append([h, w])

        return tuple([self.getRadar(direction) for direction in [left, right, up, down, left_up, right_up, left_down, right_down]])

    def reward(self, bot):
        if self.done:
            # Fatal
            return FATAL_POINT

        if not (bot.x in range(H) and bot.y in range(W)):
            self.done = True
            return FATAL_POINT


        cell = self.state[bot.x][bot.y]
        # empty
        if cell == '2':
            return EXPAND_POINT

        elif cell == '1':
            new_score = 0
            for h in range(H):
                line = ''.join(self.state[h])
                if '1' in line:
                    start = line.index('1')
                    end = line.rindex('1')
                    for w in range(start, end+1):
                        new_score += 1

            # Too dumb to expand the area
            if new_score == bot.score:
                return STABLE_POINT
            else:
                bot.score = new_score
                reward = (new_score - bot.score) * BOOST_POINT
                return reward

class Bot():
    def __init__(self, idx, x=-1, y=-1, trained_q=None, epsilon=EPSILON):
        self.id = idx
        self.x = x
        self.y = y
        self.score = 9

        # Q
        self.ai = Q(actions=range(4), epsilon=epsilon)
        if trained_q is not None:
            self.ai.q = trained_q

        # History for learning
        self.last_action = None
        self.last_state = None
        self.last_score = None

    def learn(self, board):
        curr_state = board.calcState(self.x, self.y)
        print curr_state
        #reward = board.reward(self)

        #if self.last_state is not None:
            #self.ai.learn(self.last_state, self.last_action, reward, curr_state)

        # update last state
        self.last_state = curr_state


def main():
    games = os.listdir('crawl')
    for e, game in enumerate(games[:EPOCH]):
        f = open('crawl/' + game, 'r')

        # Initalize process
        board = Board()

        n_players = int(f.readline())
        bot = Bot(1)

        # First state of board
        board.updateState(f)

        # First position of my bot
        bot.x, bot.y = map(int, f.readline().split())

        # First position of other bots (skip)
        for _ in range(n_players-1):
            f.readline()

        # First score, already initialized -> just skip
        f.readline()

        turn = 1
        # Loop for game playing
        while True:
            # Update last action of bot in previous game
            try:
                last_move = f.readline().split()[0]
                if last_move == '-':
                    board.done = True
                else:
                    bot.last_action = ACTIONS[last_move]
            except IndexError:
                print '>>> ERROR: Game wrong. Skip!'
                break

            # Update board state
            board.updateState(f)
            # Check if game were done
            if board.done:
                board.view()
                print 'EPOCH %d: %s - %d turn(s)' % (e+1, game, turn)
                break

            # Update position of my bot
            bot.x, bot.y = map(int, f.readline().split())
            # Update positions of other bots (skip)
            for _ in range(n_players-1):
                f.readline()

            # Update score
            bot.last_score = bot.score
            bot.score = int(f.readline().split()[0])


            ## LEARN
            bot.learn(board)

            turn += 1

    f.close()

if __name__ == '__main__':
    main()
