import random
import sys

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

    def chooseAction(self, state):
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

            # NOTE: Debug
            sys.stdout.write("EXPLORE - ")

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
