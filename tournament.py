from papersoccer_env import Board

def play_game(playerA, playerB, max_moves, draw_score = 0.5):
    board = Board()
    next_player = 0
    sequence = []
    for i in range(max_moves):
        if next_player == 0:
            move = playerA.move(board)
        else:
            move = playerB.move(board)
            
        valid_move, next_player, winner = board.move(move)
        sequence.append(move)
        if winner is not None:
            return i, winner, sequence, board      
        
    return max_moves, draw_score, sequence, board 

def play_tournament(players, rounds=100, max_moves=1000, draw_score=0.5, progress_lambda=lambda x:x):
    
    points = {p.get_name():0 for p in players}
    
    all_games = len(players)*(len(players)-1)*rounds
    
    history = []
    
    for round in progress_lambda(range(rounds)):
        for pa, playerA in enumerate(players):
            for pb, playerB in enumerate(players):
                if pa<pb:
                    moves, pointsA, sequence, _ = play_game(playerA, playerB, max_moves, draw_score=draw_score)
                    history.append( (playerA.get_name(), playerB.get_name(), pointsA, sequence) )
                    
                    moves, pointsB, sequence, _ = play_game(playerB, playerA, max_moves, draw_score=draw_score)
                    history.append( (playerB.get_name(), playerA.get_name(), pointsB, sequence) )
                    
                    points[playerA.get_name()] += pointsA + (1-pointsB)
                    points[playerB.get_name()] += pointsB + (1-pointsA)               
    return points, history