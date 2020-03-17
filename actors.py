import numpy as np


class Actor():
    def __init__(self, name):
        self.name = name
        
    def get_name(self):
        return self.name
    
    def move(self, board):
        raise Exception("move(...): Not implemented")


class RandomActor(Actor):
    def __init__(self, name):
        super(RandomActor, self).__init__("Random_"+name)
    
    def move(self, board):
        moves_dict = board.possible_moves()
        moves = []
        for key in moves_dict:
            if moves_dict[key]:
                moves.append(key)

        index = np.random.randint(0,len(moves))
        return moves[index]

class TryOnlyBestActor(Actor):
    def __init__(self, name):
        super(TryOnlyBestActor, self).__init__("TryBest_"+name)
    
    def move(self, board):
        moves_dict = board.possible_moves()
        target = board.winning_positions[board.player_to_move][0]
        
        y,x = board.ball_pos
        ty,tx = target
        
        # Calculate preference
        vert_preference = ""
        horiz_preference = ""
        
        if tx<x:
            horiz_preference="L"
        elif tx>x:
            horiz_preference="R"
            
        if ty<y:
            vert_preference="T"
        elif ty>y:
            vert_preference="B"
            
        shortest_move = vert_preference+horiz_preference

        # Possible moves
        moves = []
        for key in moves_dict:
            if moves_dict[key]:
                moves.append(key)
                
        # Try best     
        if shortest_move in moves:
            return shortest_move

        index = np.random.randint(0,len(moves))
        return moves[index]


class GreedyActor(Actor):
    def __init__(self, name):
        super(GreedyActor, self).__init__("Greedy_"+name)
    
    def move(self, board):
        moves_dict = board.possible_moves()
        target = board.winning_positions[board.player_to_move][0]
        
        y,x = board.ball_pos
        ty,tx = target
        
        # Calculate preference
        vert_preference = ""
        horiz_preference = ""
        
        if tx<x:
            horiz_preference="L"
        elif tx>x:
            horiz_preference="R"
            
        if ty<y:
            vert_preference="T"
        elif ty>y:
            vert_preference="B"
            
        shortest_move = vert_preference+horiz_preference

        # Possible moves
        moves = []
        for key in moves_dict:
            if moves_dict[key]:
                moves.append(key)
         
         # Try best    
        if shortest_move in moves:
            return shortest_move
        
         # Try horiz direction
        for m in moves:
            if horiz_preference in m:
                return m
            
         # Try vert direction
        for m in moves:
            if vert_preference in m:
                return m

        index = np.random.randint(0,len(moves))
        return moves[index]