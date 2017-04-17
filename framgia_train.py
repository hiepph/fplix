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
        # Fatal
        self.done = False

        # Default bot id 1 for framgia
        self.stable = '1'
        self.unstable = '2'

        # Other bots
        self.oppo = '-2' # Head of bot
        self.oppo_stable = '3'
        self.oppo_unstable = '4'

        # History
        self.last_state = None

    def view(self):
        for i in range(H):
            print ''.join(self.state[i])

    def review(self, epoch, game, turn):
        print 'EPOCH %d (%s) - %d turn(s)' % (epoch, game, turn)

    def updateState(self, inputs):
        for i in range(H):
            self.state[i] = list(inputs.readline()[:-1])

    def getCell(self, cell, past=False):
        """Get specific corresponding to cell
        Map value if necessary into keys of POINTS"""
        x, y = cell

        # Out of board
        if x not in range(H):
            return '-1'
        if y not in range(W):
            return '-1'

        # Map value
        if past:
            value = self.last_state[x][y]
        else:
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
            # Fatal/Killed
            return FATAL_POINT

        value = self.getCell([bot.x, bot.y])
        if value == '-1':
            board.done = True
            return FATAL_POINT
        elif value == '1':
            return (bot.score - bot.last_score) * BOOST_POINT
        elif value == '2':
            last_value = self.getCell([bot.x, bot.y], past=True)
            # Expand region (empty)
            if last_value == '0':
                return EMPTY_POINT
            # Expand region (oppo)
            elif last_value == '3':
                return OPPO_STABLE_POINT
            # Kill
            elif last_value == '4' or last_value == '-2':
                return KILL_POINT


class Bot():
    def __init__(self, idx, x=-1, y=-1, epsilon=EPSILON):
        self.id = idx
        self.x = x
        self.y = y
        self.score = 9

        # Q
        self.ai = Q(actions=range(4), epsilon=epsilon)

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

        if self.last_state is not None:
            self.ai.learn(self.last_state, self.last_action, reward, curr_state)

        # update last state
        self.last_state = curr_state


def main():
    # Release the kraken
    bot = Bot(1)

    games = os.listdir('crawl')
    for e, game in enumerate(games[:EPOCH]):
        print '---> %s' % game
        f = open('crawl/' + game, 'r')

        # Initalize process
        board = Board()

        n_players = int(f.readline())
        bot.restart()

        # First state of board
        board.updateState(f)

        # First position of my bot
        bot.x, bot.y = map(int, f.readline().split())

        # First position of other bots (skip)
        for _ in range(n_players-1):
            f.readline()

        # First score, already initialized -> just skip
        f.readline()

        # First time update last move
        try:
            last_move = f.readline().split()[0]
        except IndexError:
            # Prevent case like 4832
            f.close()
            continue

        turn = 1
        # Loop for game playing
        while True:
            # Output fail move, bot won't learn anymore -> end the game
            if last_move == '-':
                board.review(epoch=e, game=game, turn=turn)
                break
            else:
                bot.last_action = ACTIONS[last_move]

                # Update board state
                board.last_state = copy.deepcopy(board.state)
                board.updateState(f)
                if board.state == [[] for _ in range(H)]:
                    board.review(epoch=e, game=game, turn=turn)
                    break

                # Update position of my bot
                bot.x, bot.y = map(int, f.readline().split())
                if bot.x == -1 and bot.y == -1:
                    board.done = True

                # Update positions of other bots (skip)
                for _ in range(n_players-1):
                    f.readline()

                # Update score
                bot.last_score = bot.score
                bot.score = int(f.readline().split()[0])

                ## LEARN
                bot.learn(board)

                # Update last action of bot in previous game
                last_move = f.readline().split()[0]

                # Prepare for next turn
                turn += 1

                # Check if game were done or max 1000 turns
                if turn == 1000 or board.done:
                    board.review(epoch=e, game=game, turn=turn)
                    break

    f.close()

    if (e+1) % 1000 == 0:
        dump_q(bot.ai.q, e+1)

if __name__ == '__main__':
    main()
