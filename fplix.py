from sys import stdin, stdout
import random
import math

# Hard-code values
MOVES = [
    'LEFT',
    'RIGHT',
    'UP',
    'DOWN',
]

ACTIONS = {
    'LEFT': ['LEFT', 'UP', 'DOWN'],
    'RIGHT': ['RIGHT', 'UP', 'DOWN'],
    'UP': ['UP', 'RIGHT', 'LEFT'],
    'DOWN': ['DOWN', 'RIGHT', 'LEFT'],
}


NEXT_ACTIONS = {
    'LEFT': (0, -1),
    'RIGHT': (0, 1),
    'UP': (-1, 0),
    'DOWN': (1, 0),
}

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
            self.state[i] = map(int, list(inputs.readline()[:-1]))

    def getPosition(self, x, y):
        return self.state[x][y]

    def mahattanDistance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def setBots(self, bots):
        self.bots = bots


class Bot():
    def __init__(self, index, board, x=-1, y=-1):
        self.id = index * 2 - 1
        self.x = x
        self.y = y
        self.board = board
        self.prev = None

    # state: Board' state format a.k.a 2-d array
    def distFromEnemies(self):
        unstable = []
        for x in range(0, H):
            for y in range(0, W):
                if self.board.getPosition(x, y) == self.id + 1:
                    unstable.append((x, y))

        squares = unstable + [(self.x, self.y)]
        distances = []
        for bot in self.board.bots:
            if bot.id == self.id: continue
            if bot.x == -1 or bot.y == -1: continue
            dist = [self.board.mahattanDistance((bot.x, bot.y), (x, y)) for (x, y) in squares]
            distances.append(min(dist))

        return distances


    def possibleActions(self, square, prev=None):
        if prev is None:
            return [action for action in MOVES if self.canMove(square, action)]
        return [action for action in ACTIONS[prev] if self.canMove(square, action)]

    def canMove(self, square, action):
        x, y = square
        actionX, actionY = NEXT_ACTIONS[action]
        newX, newY = x + actionX, y + actionY

        if newX < 0 or newX >= H: return False
        if newY < 0 or newY >= W: return False
        if self.board.getPosition(newX, newY) == self.id + 1: return False

        for bot in self.board.bots:
            if bot.id == self.id: continue
            if abs(bot.x - newX) <= 1 and abs(bot.y - newY) <= 1:
                return False

        return True

    def shortestDistToHome(self, square, prev=None):
        # BFS
        visited = [[False for y in range(0, W)] for x in range(0, H)]

        x, y = square
        queue = [(x, y, prev, 0, [])]   

        while len(queue) > 0:
            curX, curY, curPrev, length, history = queue.pop(0)
            visited[curX][curY] = True

            if self.board.getPosition(curX, curY) == self.id:
                return length, history
            actions = self.possibleActions((curX, curY), prev=curPrev)
            for action in actions:
                nextX, nextY = NEXT_ACTIONS[action]
                newX, newY = curX + nextX, curY + nextY
                if not visited[newX][newY]:
                    queue.append((newX, newY, action, length + 1, history + [action]))
        return -1, []

    def shortestDistToBeOut(self):
        # BFS
        visited = [[False for y in range(0, W)] for x in range(0, H)]
        queue = [(self.x, self.y, self.prev, 0, [])]
        while len(queue) > 0:
            curX, curY, curPrev, length, history = queue.pop(0)
            visited[curX][curY]
            if self.board.getPosition(curX, curY) != self.id:
                return length, history
            actions = self.possibleActions((curX, curY), prev=curPrev)
            for action in actions:
                nextX, nextY = NEXT_ACTIONS[action]
                newX, newY = curX + nextX, curY + nextY
                if not visited[newX][newY]:
                    queue.append((newX, newY, action, length + 1, history + [action]))
        return -1, []

    def chooseAction(self):
        # self.prev = 'LEFT'
        distFromEnemies = self.distFromEnemies()
        minDistToEnemy = min(distFromEnemies)

        length, history = self.shortestDistToHome((self.x, self.y), prev=self.prev)
        actions = self.possibleActions((self.x, self.y), self.prev)
        
        if len(actions) == 0:
            move = 'LEFT'
            self.prev = move
            return move

        move = random.choice(actions)
        if length == -1:
            self.prev = move
            return move

        if length == 0:
            l, hist = self.shortestDistToBeOut()
            move = hist[0]
            self.prev = move
            return move

        if length >= minDistToEnemy - 3:
            move = history[0]
            self.prev = move
            return move

        if lenght <= 3:
            if history[0] == self.prev:
                move = history[0]

        if length < minDistToEnemy - 3:
            for action in actions:
                if action != history[0]:
                    move = action
                    break

            self.prev = move
            return move

        self.prev = move
        return move


def main():
    board = Board()

    ## Get initial values from stdin

    # Number of players
    n_players = int(stdin.readline())
    # Create a list of bots with index 1->n_players
    bots = []
    for i in range(n_players):
        bots.append(Bot(i + 1, board))

    board.setBots(bots)

    # Choose my bot from my bot's index
    bot = bots[int(stdin.readline()) - 1]

    # Update board adapts to world
    board.update(stdin)

    # Read position of bots (corresponding to bot's index)
    for i in range(n_players):
        bots[i].x, bots[i].y = map(int, stdin.readline().split())

    while True:
        print bot.chooseAction()

        # Update new board state from stdin
        board.update(stdin)

        # Update bot position
        for i in range(n_players):
            bots[i].x, bots[i].y = map(int, stdin.readline().split())


if __name__ == '__main__':
    main()
