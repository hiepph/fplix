from sys import stdin
import random
import time

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
EPOCH = 1000
W = 30
H = 20


class Board():
    def __init__(self):
        self.state = [[0 for y in range(W)] for x in range(H)]

    # Pretty print state
    def view(self):
        for i in range(H):
            print ''.join(self.state[i])

    # Update state from (x, y) of bot
    def update(self, x, y):
        if not (x in range(H) and y in range(W)):
            # game end
            return True

        print "(%d, %d)" % (x, y)
        cell = self.state[x][y]

        # empty
        if cell == '0':
            # Add unstable state
            cell = '2'
            self.state[x][y] = cell

        elif cell == '1':
            # Update stable cells
            for x in range(H):
                line = ''.join(self.state[x])
                if '2' in line:
                    if '1' in line:
                        start = min([line.index('1'), line.index('2')])
                        end = max([line.rindex('1'), line.rindex('2')])
                    else:
                        start = line.index('2')
                        end = line.rindex('2')

                    for y in range(start, end+1):
                        self.state[x][y] = '1'

        elif cell == '2':
            return True

        return False

    def getPosition(self, x, y):
        return self.state[x][y]


class Bot():
    def __init__(self, index, x=-1, y=-1):
        self.id = index
        self.x = x
        self.y = y
        self.score = 9
        self.last_move = None

    # state: Board' state format a.k.a 2-d array
    def chooseAction(self, state, auto=True):
        if auto:
            move = random.choice(list(range(len(MOVES))))

            # Prevent reversing
            while [move, self.last_move] in FATAL_COUPLES:
                move = random.choice(list(range(len(MOVES))))

            # Update last move
            self.last_move = move
        else:
            move = int(stdin.readline())

        # Update (x,y) of bot
        if move == 0:
            self.y -= 1
        elif move == 1:
            self.y += 1
        elif move == 2:
            self.x -= 1
        else:
            self.x += 1

        return MOVES[move]


def main():
    board = Board()

    ## WORLD MAKING
    for i in range(H):
        board.state[i] = list(stdin.readline()[:-1])
    board.view()

    ## RELEASE THE KRAKEN
    bot = Bot(1)
    bot.x, bot.y = map(int, stdin.readline().split())

    ## TRAINING
    for i in range(EPOCH):
        # Actuator
        print bot.chooseAction(board.state)
        #print bot.chooseAction(board.state, False)

        # Update world
        done = board.update(bot.x, bot.y)
        board.view()
        if done:
            break

    print "END"

if __name__ == '__main__':
    main()
