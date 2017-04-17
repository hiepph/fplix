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
EXPAND_POINT = 15
# Oppo
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
        # Fatal
        self.done = False

        # Default bot id 1 for framgia
        self.stable = '1'
        self.unstable = '2'

        # Other bots
        self.oppo = '-2' # Head of bot
        self.oppo_stable = '3'
        self.oppo_unstable = '4'

    def view(self):
        for i in range(H):
            print ''.join(self.state[i])

    def review(self, epoch, game, turn):
        self.view()
        print 'EPOCH %d (%s) - %d turn(s)' % (epoch, game, turn)

    def updateState(self, inputs):
        for i in range(H):
            self.state[i] = list(inputs.readline()[:-1])

    def getCell(self, cell):
        """Get specific corresponding to cell
        Map value if necessary into keys of POINTS"""
        x, y = cell

        # Out of board
        if x not in range(H):
            return '-1'
        if y not in range(W):
            return '-1'

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

        value = self.getCell([self.x, self.y])
        if value == '-1':
            board.done = True
            return FATAL_POINT
        elif value == '1':
            return (self.score - self.last_score) * BOOST_POINT
        elif value == '2':
            return EXPAND_POINT

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

    def restart(self):
        """Reset everything except id & Q (important)"""
        self.x = -1
        self.y = -1
        self.score = 9

        self.last_action = None
        self.last_state = None
        self.last_score = None


    def learn(self, board):
        curr_state = board.calcState(self.x, self.y)
        reward = board.reward(self)

        #if self.last_state is not None:
            #self.ai.learn(self.last_state, self.last_action, reward, curr_state)

        # update last state
        self.last_state = curr_state


def main():
    # Release the kraken
    bot = Bot(1)

    games = os.listdir('crawl')
    for e, game in enumerate(games[:EPOCH]):
        f = open('crawl/' + game, 'r')

        # Initalize process
        board = Board()

        n_players = int(f.readline())
        bot.restart()

        # First state of board
        board.updateState(f)

        # First position of my bot
        bot.x, bot.y = map(int, f.readline().split())

        # First position of other bots (just check of -1,-1 only)
        qualified = True
        for _ in range(n_players-1):
            try:
                x, y = map(int, f.readline().split())
                if x == -1 and y == -1:
                    qualified = False
            except:
                qualified = False

        if not qualified:
            print 'ERROR: Game (%s) skip!' % game
            f.close()
            continue

        # First score, already initialized -> just skip
        f.readline()

        turn = 1
        # Loop for game playing
        while True:
            # Update last action of bot in previous game
            try:
                last_move = f.readline().split()[0]

                # Output fail move, bot won't learn anymore -> end the game
                if last_move == '-':
                    board.review(epoch=e, game=game, turn=turn)
                    break
                else:
                    bot.last_action = ACTIONS[last_move]

                    # Update board state
                    board.updateState(f)

                    # Update position of my bot
                    bot.x, bot.y = map(int, f.readline().split())
                    if bot.x == -1 and bot.y == -1:
                        board.done = True

                    # Update positions of other bots (check for -1, -1 only)
                    for _ in range(n_players-1):
                        x, y = map(int, f.readline().split())
                        if x == -1 and y == -1:
                            board.done = True

                    # Update score
                    bot.last_score = bot.score
                    bot.score = int(f.readline().split()[0])

                    ## LEARN
                    #bot.learn(board)

                    # Prepare for next turn
                    turn += 1

                    # Check if game were done or max 1000 turns
                    if turn == 1000 or board.done:
                        board.review(epoch=e, game=game, turn=turn)
                        break

            except:
                print '>>> ERROR: Game (%s) wrong. Skip!'
                break

    f.close()

if __name__ == '__main__':
    main()
