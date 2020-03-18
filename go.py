import numpy as np
import zlib

from papersoccer_env import Board
from actors import Actor, RandomActor, GreedyActor, TryOnlyBestActor
from tournament import play_game, play_tournament
from sequence import encode_moves, decode_moves

from tqdm import tqdm

class MonteCarloActor(Actor):
    def __init__(self, name):
        super(MonteCarloActor, self).__init__("MonteCarlo_"+name)

        self.gamma=0.99

        # global knowledge
        self.V = {}
        self.returns = {}

    def policy(self, board, is_first_move): # TODO is_first_move
        actions_dict = board.possible_moves()
        actions = []
        for key in actions_dict:
            if actions_dict[key]:
                actions.append(key)

        # pick random
        action = actions[np.random.randint(0,len(actions))]
        return action
    
    def move(self, board):
        is_first_move = (len(self.states_actions_rewards)==0)
        action = self.policy(board, is_first_move)

        #if is_first_move:
        #    state = board.get_b64_state()
        #    self.states_actions_rewards.append((state, action, 0))

        return action

    def new_game(self):
        print("New game")
        self.states_actions_rewards = []

    def state_hash(self, state):
        return zlib.crc32(state.encode())

    def end_game(self):
        print("End game")

        G = 0
        states_actions_returns = []
        first = True
        for s, a, r in reversed(self.states_actions_rewards):
            if first:
                first = False
            else:
                states_actions_returns.append((s, a, G))
            G = r + self.gamma * G
        states_actions_returns.reverse() 

        return states_actions_returns

    def save_reward(self, state, action, reward):
        self.states_actions_rewards.append((state, action, reward))
        print("Save reward. Number = ", len(self.states_actions_rewards), action, reward)

# Single game
max_moves, draw_score, sequence, board, (states_actions_returns,_) = play_game(MonteCarloActor("1"), RandomActor("2"), max_moves=1000)

for s,a,G in states_actions_returns:
    print(f"{a:<3} {G:-2.5f}")

# Tournament
#actors = []
#actors.append(RandomActor("1"))
#actors.append(TryOnlyBestActor("2"))
#actors.append(GreedyActor("3"))
#points, history = play_tournament(actors, rounds=100, progress_lambda=tqdm)
#print(points)