import numpy as np
import zlib

from papersoccer_env import Board
from actors import Actor, RandomActor, GreedyActor, TryOnlyBestActor
from tournament import play_game, play_tournament
from sequence import encode_moves, decode_moves
from helpers import max_dict

from tqdm import tqdm

class MonteCarloActor(Actor):
    def __init__(self, name):
        super(MonteCarloActor, self).__init__("MonteCarlo_"+name)

        self.gamma=0.9

        # global knowledge
        self.Q = {}
        self.deltas = []
        self.returns = {}
        self.saved_policy = {}

    def policy(self, board, is_first_move): # TODO is_first_move
        actions_dict = board.possible_moves()
        state = board.get_b64_state()
        actions = []
        for key in actions_dict:
            if actions_dict[key]:
                actions.append(key)

        if state in self.saved_policy:
            action = self.saved_policy[state]
            if action in actions:
                return action
            else:
                print("Policy returned invalid move.")

        # pick random
        action = actions[np.random.randint(0,len(actions))]
        return action
    
    def move(self, board):
        is_first_move = (len(self.states_actions_rewards)==0)
        action = self.policy(board, is_first_move)
        return action

    def new_game(self):
        self.states_actions_rewards = []

    def state_hash(self, state):
        return zlib.crc32(state.encode())
    
    def __getQ(self, Q,s,a):
        if s in self.Q:
            if a in self.Q[s]:
                return self.Q[s][a]
            self.Q[s][a] = 0
            return self.Q[s][a]
        else:
            self.Q[s] = {}
            self.Q[s][a] = 0
            return self.Q[s][a]

    def end_game(self):
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

        seen_state_action_pairs = set()
        biggest_change = 0
        for s, a, G in states_actions_returns:
            sa = (s, a)
            #if sa not in seen_state_action_pairs:
            if (s,a) not in self.returns:
                self.returns[(s,a)] = []
            old_q = self.__getQ(self.Q,s,a)
            self.returns[sa].append(G)
            new_q = np.mean(self.returns[sa])
            self.Q[s][a] = new_q
            biggest_change = max(biggest_change, np.abs(old_q - new_q))
            seen_state_action_pairs.add(sa)

        self.deltas.append(biggest_change)

        # update policy
        all_states = set([s for s,_ in seen_state_action_pairs])
        for s in all_states:
            old = None
            if s in self.saved_policy:
                old = self.saved_policy[s] 

            self.saved_policy[s] = max_dict(self.Q[s])[0]

            if old is not None and old != self.saved_policy[s]:
                print(old,"==>", self.saved_policy[s] )

    def save_reward(self, state, action, reward):
        self.states_actions_rewards.append((state, action, reward))

# Single game
games = 100000
player_a = MonteCarloActor("A")
player_b = RandomActor("B")
progress = tqdm(range(games),desc="Gathering experience...")
for game in progress:
    play_game(player_a, player_b, max_moves=1000)
    progress.set_description(f"{np.mean(player_a.deltas[-1000:]):.5f} {len(player_a.returns)} {len(player_a.Q)}")

# Tournament
actors = []
actors.append(RandomActor("1"))
#actors.append(TryOnlyBestActor("2"))
#actors.append(GreedyActor("3"))
actors.append(player_a)
points, history = play_tournament(actors, rounds=100, progress_lambda=tqdm)
print(points)