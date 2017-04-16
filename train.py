from sys import stdin
import sys
import random
import time
import copy
import os

from q import Q

# Hard-code values
MOVES = [
    'LEFT',     # 0
    'RIGHT',    # 1
    'UP',       # 2
    'DOWN'      # 3
]
FATAL_MOVES = [
    [0, 1],
    [1, 0],
    [2, 3],
    [3, 2]
]
try:
    EPOCH = int(os.environ['EPOCH'])
except KeyError:
    EPOCH = 1000
W = 30
H = 20

# Radar point
POINTS = {
    '-1': 1000,
    '2':  100,
    '1':  10,
    '0':  1
}


FATAL_POINT = -10000
BOOST_POINT = 1000
STABLE_POINT = -10
EXPAND_POINT = 10

class Board():
    def __init__(self):
        self.state = [['0' for y in range(W)] for x in range(H)]
        x = random.randint(0, H-3)
        y = random.randint(0, W-3)
        for h in range(x, x+3):
            for w in range(y, y+3):
                self.state[h][w] = '1'

        self.random_x = random.choice(range(x, x+3))
        self.random_y = random.choice(range(y, y+3))

        self.done = False

    # Pretty print state
    def view(self):
        for i in range(H):
            print ''.join(self.state[i])

    # Update state from (x, y) of bot
    def update(self, x, y):
        if self.done:
            return

        if not (x in range(H) and y in range(W)):
            # game end
            self.done = True
            return

        cell = self.state[x][y]

        # empty
        if cell == '0':
            # Add unstable state
            cell = '2'
            self.state[x][y] = cell

        elif cell == '1':
            # Update stable cells
            for h in range(H):
                line = ''.join(self.state[h])
                if '2' in line:
                    if '1' in line:
                        start = min([line.index('1'), line.index('2')])
                        end = max([line.rindex('1'), line.rindex('2')])
                    else:
                        start = line.index('2')
                        end = line.rindex('2')

                    for w in range(start, end+1):
                        self.state[h][w] = '1'

        elif cell == '2':
            self.done = True
            return

        self.done = False

    def getCell(self, cell):
        if cell[0] not in range(H):
            return '-1'
        if cell[1] not in range(W):
            return '-1'

        return self.state[cell[0]][cell[1]]

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

    def calcState(self, x, y, sight=3):
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
    def __init__(self, index, x=-1, y=-1):
        self.id = index
        if self.id == 1:
            self.stable = 1
            self.unstable = 2
        elif self.id == 2:
            self.stable = 3
            self.unstable = 4
        elif self.id == 3:
            self.stable = 5
            self.unstable = 6
        elif self.id == 4:
            self.stable = 7
            self.unstable = 8
        self.x = x
        self.y = y
        self.score = 9

        # Q
        self.q = Q(actions=range(len(MOVES)))
        self.last_action = None
        self.last_state = None

    def restart(self, x=-1, y=-1):
        self.x = x
        self.y = y
        self.score = 9

        self.last_action = None
        self.last_state = None

    def learn(self, board):
        curr_state = board.calcState(self.x, self.y)
        reward = board.reward(self)

        if self.last_state is not None:
            self.q.learn(self.last_state, self.last_action, reward, curr_state)

        # update last state
        self.last_state = curr_state

    # state: Board' state format a.k.a 2-d array
    def chooseAction(self, board, auto=True):
        if not auto:
            move = int(stdin.readline())
        else:
            curr_state = board.calcState(self.x, self.y)
            move = self.q.chooseAction(curr_state, self.last_action)

            # Prevent reversing
            #count = 0
            #while count != 10 and [move, self.last_action] in FATAL_MOVES:
                #move = self.q.chooseAction(curr_state, self.last_action)
                #count += 1

        # Update (x,y) of bot
        if move == 0:
            self.y -= 1
        elif move == 1:
            self.y += 1
        elif move == 2:
            self.x -= 1
        else:
            self.x += 1

        #if [move, self.last_action] in FATAL_MOVES:
            #board.done = True

        # Update last move
        self.last_action = move

        return MOVES[move]


def main():
    ## Agent
    bot = Bot(1)

    total_point = 0
    total_turn = 0
    ## TRAINING
    for e in range(EPOCH):
        # Restart
        board = Board()
        bot.restart(board.random_x, board.random_y)

        done = False
        turn = 1

        while not board.done:
            # Actuator
            action = bot.chooseAction(board)
            #print action

            # Update world
            board.update(bot.x, bot.y)
            #board.view()

            # Bot learn
            bot.learn(board)

            if board.done:
                board.view()
                print "GAME %d - %d turn(s) - %d points" % (e+1, turn, bot.score)
                print "Q {%d KB}" % (sys.getsizeof(bot.q.q)/1024)

                #q = bot.q.q
                #for k, v in q.iteritems():
                    #print k, v

                # Statistics
                total_point += bot.score
                total_turn  += turn

            turn += 1

    print "Average: %f points - %f turns" % (float(total_point/EPOCH), float(total_turn/EPOCH))
    #for k, v in bot.q.q.iteritems():
        #print k, v

if __name__ == '__main__':
    main()
