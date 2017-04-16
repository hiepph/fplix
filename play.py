Q_TRAINED = {
    (('0', '2', '0', '2', '0', '0', '1', '2'), 0): 14.497635808,
    (('-1', '2', '0', '2', '-1', '2', '-1', '2'), 2): 10,
    (('0', '2', '0', '2', '0', '0', '0', '2'), 1): -10000,
    (('1', '1', '-1', '1', '-1', '-1', '1', '1'), 2): -2008.0,
    (('1', '1', '0', '1', '0', '0', '1', '1'), 0): -10,
    (('1', '1', '1', '1', '1', '1', '1', '1'), 3): -10,
    (('-1', '2', '-1', '2', '-1', '-1', '-1', '2'), 3): -1990.2,
    (('0', '2', '2', '-1', '1', '2', '-1', '-1'), 0): 10,
    (('-1', '2', '2', '2', '-1', '2', '-1', '2'), 0): 10,
    (('0', '2', '1', '-1', '0', '2', '-1', '-1'), 2): 10,
    (('0', '1', '1', '1', '0', '1', '0', '1'), 0): 10,
    (('0', '2', '0', '2', '0', '0', '0', '2'), 0): 10,
    (('1', '1', '0', '1', '0', '0', '1', '1'), 1): -10,
    (('1', '1', '1', '1', '1', '1', '1', '1'), 2): -10,
    (('1', '1', '1', '-1', '1', '1', '-1', '-1'), 3): 10.04,
    (('-1', '2', '0', '2', '-1', '1', '-1', '2'), 0): -10000,
    (('-1', '2', '-1', '2', '-1', '-1', '-1', '2'), 0): -1990.56,
    (('0', '1', '1', '1', '0', '1', '0', '1'), 1): -10,
    (('0', '2', '1', '-1', '1', '1', '-1', '-1'), 3): -1992.0,
    (('1', '1', '-1', '1', '-1', '-1', '1', '1'), 1): -10,
    (('1', '1', '-1', '1', '-1', '-1', '1', '0'), 2): -10,
    (('0', '2', '2', '-1', '1', '2', '-1', '-1'), 2): -10000,
    (('1', '1', '-1', '1', '-1', '-1', '1', '1'), 0): -10,
    (('0', '2', '0', '2', '0', '1', '0', '2'), 2): 16.1448367772,
    (('0', '2', '0', '2', '0', '0', '0', '2'), 3): -10000,
    (('-1', '2', '-1', '2', '-1', '-1', '-1', '2'), 1): -10000,
    (('1', '1', '0', '1', '0', '0', '1', '1'), 2): 10,
    (('-1', '2', '-1', '2', '-1', '-1', '-1', '2'), 2): 10,
    (('0', '2', '-1', '2', '-1', '-1', '0', '2'), 0): 42.072003114,
    (('1', '1', '0', '1', '0', '0', '1', '1'), 3): -10,
    (('0', '2', '1', '-1', '1', '2', '-1', '-1'), 0): 10,
    (('0', '1', '1', '1', '0', '1', '0', '1'), 2): -10,
    (('0', '2', '0', '2', '0', '0', '0', '2'), 2): 36.4436639829,
    (('1', '1', '-1', '1', '-1', '-1', '1', '1'), 3): -10,
    (('1', '-1', '0', '2', '0', '-1', '1', '-1'), 1): 10,
    (('2', '-1', '0', '2', '0', '-1', '2', '-1'), 1): -10000,
    (('-1', '1', '1', '1', '-1', '1', '-1', '1'), 0): 10,
    (('0', '2', '1', '-1', '0', '1', '-1', '-1'), 2): 0,
}

from sys import stdin
import random

# Q implementation
class Q:
    def __init__(self, actions, epsilon=0.1, alpha=0.2, gamma=0.9):
        self.q = {}

        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.actions = actions

    def getQ(self, state, action):
        """Try to get Q value from (state, action)
        If not found return 0.0
        """
        return self.q.get((state, action), 0.0)

    def learnQ(self, state, action, reward, value):
        oldv = self.q.get((state, action), None)
        if oldv is None:
            self.q[(state, action)] = reward
        else:
            self.q[(state, action)] = oldv + self.alpha * (value - oldv)

    def chooseAction(self, state, last_action=None):
        """Lookup corresponding action values for state,
        choose the maximum. If there are serveral with
        same value, randomly choose.

        Exploration: Randomly generate a value, if that value is less
        than epsilon, then randomly add values to Q values for this state.
        In this Q, exploration is added, but still using our learned Q values
        as a basics foor choosing action.
        """

        q = [self.getQ(state, a) for a in self.actions]
        maxQ = max(q)

        # Exploration
        if random.random() < self.epsilon:
            minQ = min(q); mag = max(abs(minQ), abs(maxQ))
            # randomly add values to all the actions
            q = [q[i] + random.random() * mag - .5 * mag for i in range(len(self.actions))]
            # recalculate max of Q
            maxQ = max(q)

        count = q.count(maxQ)
        if count > 1:
            best = [i for i in range(len(self.actions)) if q[i] == maxQ]
            i = random.choice(best)
        else:
            i = q.index(maxQ)

        action = self.actions[i]
        return action

    def learn(self, prev_state, prev_action, reward, curr_state):
        maxqnew = max([self.getQ(curr_state, a) for a in self.actions])
        self.learnQ(prev_state, prev_action, reward, reward + self.gamma * maxqnew)

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
W = 30
H = 20

# CASES
STABLES = ['1', '3', '5', '7']
UNSTABLES = ['2', '4', '6', '8']

# Value points
POINTS = {
    '-1': 1000,
    '2':  100,
    '1':  10,
    '0':  1
}

class Board():
    def __init__(self):
        self.state = [['0' for y in range(W)] for x in range(H)]
        # default
        self.stable = '1'
        self.unstable = '2'

    def view(self):
        for i in range(H):
            print ''.join(self.state[i])

    def update(self, inputs):
        for i in range(H):
            self.state[i] = list(inputs.readline()[:-1])

    def getCell(self, cell):
        """Get specific corresponding to cell
        Also map again into stable/unstable region"""
        x, y = cell
        if x not in range(H):
            return '-1'
        if y not in range(W):
            return '-1'


        value = self.state[x][y]
        if value == '0':
            return '0'
        elif value == self.stable:
            return '1'
        elif value == self.unstable:
            return '2'
        elif value in STABLES:
            return '0'
        elif value in UNSTABLES:
            return '-1'

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

        return tuple([self.getRadar(direction) for direction in [
            left, right, up, down,
            left_up, right_up, left_down, right_down
        ]])


class Bot():
    def __init__(self, index, x=-1, y=-1):
        self.id = index
        self.x = x
        self.y = y

        self.q = None
        self.last_action = None

    def chooseAction(self, board):
        curr_state = board.calcState(self.x, self.y)
        move = self.q.chooseAction(curr_state, self.last_action)

        # Prevent reversing
        #count = 0
        #while count != 10 and [move, self.last_action] in FATAL_MOVES:
            #move = self.q.chooseAction(curr_state, self.last_action)
            #count += 1

        # Update last move
        self.last_action = move

        return MOVES[move]


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

    if bot.id == 1:
        board.stable = '1'
        board.unstable = '2'
    elif bot.id == 2:
        board.stable = '3'
        board.unstable = '4'
    elif bot.id == 3:
        board.stable = '5'
        board.unstable = '6'
    elif bot.id == 4:
        board.stable = '7'
        board.unstable = '8'

    # Initialize q
    bot.q = Q(actions=range(len(MOVES)))
    bot.q.q = Q_TRAINED

    # Update board adapts to world
    board.update(stdin)

    # Read position of bots (corresponding to bot's index)
    for i in range(n_players):
        bots[i].x, bots[i].y = map(int, stdin.readline().split())

    while True:
        # Actuator
        print bot.chooseAction(board)

        # Update new board state from stdin
        board.update(stdin)

        # Update bot position
        for i in range(n_players):
            bots[i].x, bots[i].y = map(int, stdin.readline().split())

if __name__ == '__main__':
    main()
