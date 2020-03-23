from papersoccer_env import Board

def play_game(playerA, playerB, max_moves, draw_score = 0.5, reward_nowin_move=-1e-5, reward_win=1, reward_loss=-1):
    board = Board()
    playerA.new_game()
    playerB.new_game()
    next_player = 0
    sequence = []
    for i in range(max_moves):
        if next_player == 0:
            move = playerA.move(board)
            moveTrace = (playerA,0, playerB)
        else:
            move = playerB.move(board)
            moveTrace = (playerB,1, playerA)

        board_state = board.get_b64_state()
        valid_move, next_player, winner = board.move(move)

        if not valid_move:
            raise Exception('Move is not valid')

        if winner is None:
            moveTrace[0].save_reward(board_state, move, reward_nowin_move)
        elif winner == moveTrace[1]:
            moveTrace[0].save_reward(board_state, move, reward_win)
            moveTrace[2].save_reward(board_state, None, reward_loss)
        else:
            moveTrace[2].save_reward(board_state, move, reward_win)
            moveTrace[0].save_reward(board_state, None, reward_loss)

        sequence.append(move)
        if winner is not None:
            endGameA = playerA.end_game()
            endGameB = playerB.end_game()
            return i, winner, sequence, board, (endGameA, endGameB)    

    endGameA = playerA.end_game() # TODO add reward?
    endGameB = playerB.end_game()  # TODO add reward?     
    return max_moves, draw_score, sequence, board, (endGameA, endGameB)

def play_tournament(players, rounds=100, max_moves=1000, draw_score=0.5, progress_lambda=lambda x:x):
    
    points = {p.get_name():0 for p in players}
    
    all_games = len(players)*(len(players)-1)*rounds
    
    history = []
    
    for round in progress_lambda(range(rounds)):
        for pa, playerA in enumerate(players):
            for pb, playerB in enumerate(players):
                if pa<pb:
                    moves, pointsA, sequence, _, _ = play_game(playerA, playerB, max_moves, draw_score=draw_score)
                    history.append( (playerA.get_name(), playerB.get_name(), pointsA, sequence) )
                    
                    moves, pointsB, sequence, _, _ = play_game(playerB, playerA, max_moves, draw_score=draw_score)
                    history.append( (playerB.get_name(), playerA.get_name(), pointsB, sequence) )
                    
                    points[playerA.get_name()] += pointsA + (1-pointsB)
                    points[playerB.get_name()] += pointsB + (1-pointsA)               
    return points, history