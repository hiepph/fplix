from sys import stdin, stdout
import random

# Hard-code values
MOVES = [
    'LEFT',
    'RIGHT',
    'UP',
    'DOWN',
]
TURN = 1000
TIMEOUT = 1000 # ms
W = 30
H = 20


class Board():
    def __init__(self):
        self.state = [[0 for y in range(W)] for x in range(H)]

    # Pretty print state
    def view(self):
        for i in range(H):
            print ''.join(self.state[i])

    # inputs: Raw stdin input -> 'h' lines of ('w' characters) (just take this part)
    def update(self, inputs):
        for i in range(H):
            self.state[i] = list(inputs.readline()[:-1])

    def getPosition(self, x, y):
        return self.state[x][y]


class Bot():
    def __init__(self, index, x=-1, y=-1):
        self.id = index
        self.x = x
        self.y = y

        self.last_move = None

    # state: Board' state format a.k.a 2-d array
    def chooseAction(self, state):
        # magic here

        ## random for now
        move = random.choice(MOVES)
        while move == self.last_move:
            move = random.choice(MOVES)

        # Prevent last move duplicated
        self.last_move = move

        return move


def main():
    board = Board()

    ## Get initial values from stdin

    # Number of players
    n_players = int(stdin.readline())
    # Create a list of bots with index 1->n_players
    bots = []
    for i in range(n_players):
        bots.append(Bot(i + 1))

    # Choose my bot from my bot's index
    bot = bots[int(stdin.readline()) - 1]

    # Update board adapts to world
    board.update(stdin)

    # Read position of bots (corresponding to bot's index)
    for i in range(n_players):
        bots[i].x, bots[i].y = map(int, stdin.readline().split())

    while True:
        # Actuator
        print bot.chooseAction(board.state)

        # Update new board state from stdin
        board.update(stdin)

        # Update bot position
        #for i in range(n_players):
        #    bots[i].x, bots[i].y = map(int, stdin.readline().split())


if __name__ == '__main__':
    main()
