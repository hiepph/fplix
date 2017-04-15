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
FATAL_COUPLES = [
    [0, 1],
    [1, 0],
    [2, 3],
    [3, 2]
]
EPOCH = int(os.environ['EPOCH'])
if EPOCH is None:
    EPOCH = 1000
W = 30
H = 20


class Board():
    def __init__(self, world=None):
        if world is None:
            self.state = [['0' for y in range(W)] for x in range(H)]
        else:
            self.state = world
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

    def getCell(self, x, y):
        if x not in range(H):
            return '-1'
        if y not in range(W):
            return '-1'

        return self.state[x][y]

    def calcState(self, x, y, sight=2):
        """Make an overview of surrounded environment
        """

        radar = []
        # left-right, up-down, diagon
        for h in range(x-sight, x+sight+1):
            for w in range(y-sight, y+sight+1):
                radar.append([h, w])

        radar = filter(lambda pos: pos != [x, y], radar)
        state = [self.getCell(cell[0], cell[1]) for cell in radar]

        return tuple(state)

    def reward(self, x, y):
        if self.done:
            # Fatal
            return -1000

        cell = self.state[x][y]
        if cell == '1':
            reward = -10
        elif cell == '0':
            reward = -1
        elif cell == '2':
            reward = -1000

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
        reward = board.reward(self.x, self.y)

        if self.last_state is not None:
            self.q.learn(self.last_state, self.last_action, reward, curr_state)

    # state: Board' state format a.k.a 2-d array
    def chooseAction(self, board, auto=True):
        if not auto:
            move = int(stdin.readline())
        else:
            curr_state = board.calcState(self.x, self.y)
            move = self.q.chooseAction(curr_state)

            # update last state
            self.last_state = curr_state

        if [move, self.last_action] in FATAL_COUPLES:
            board.done = True
            return MOVES[move]

        # Update (x,y) of bot
        if move == 0:
            self.y -= 1
        elif move == 1:
            self.y += 1
        elif move == 2:
            self.x -= 1
        else:
            self.x += 1

        # Update last move
        self.last_action = move

        return MOVES[move]


def main():
    ## WORLD MAKING
    world = [['0' for y in range(W)] for x in range(H)]
    for i in range(H):
        world[i] = list(stdin.readline()[:-1])
    world_x, world_y = map(int, stdin.readline().split())

    ## Agent
    bot = Bot(1)

    ## TRAINING
    for e in range(EPOCH):
        # Restart
        board = Board(copy.deepcopy(world))
        bot.restart(world_x, world_y)

        done = False
        turn = 1

        while not board.done:
            # Actuator
            print bot.chooseAction(board)

            # Update world
            board.update(bot.x, bot.y)
            #board.view()

            # Bot learn
            bot.learn(board)

            if board.done:
                board.view()
                print "GAME %d - %d turn(s)" % (e+1, turn)
                #print "Q {%d KB}" % (sys.getsizeof(bot.q.q)/1024)
                #print bot.q.q

            turn += 1

if __name__ == '__main__':
    main()
