import cv2
import numpy as np

class SinlgeBlock:
    def __init__(self, value=0, draw_size = 15):
        self.value = value
        self.draw_size = draw_size

    def copy(self):
        return SinlgeBlock(self.value, self.draw_size)

    def decode(self):
        # 0 is in TL
        # 1 top
        # 2 left
        # 3 /
        # 4 \    
        is_in_tl = (self.value & (2**0)) >0
        top_occupied = (self.value & (2**1)) >0
        left_occupied = (self.value & (2**2)) >0
        slash_occupied = (self.value & (2**3)) >0
        backslash_occupied = (self.value & (2**4)) >0
        
        return is_in_tl,top_occupied, left_occupied, slash_occupied, backslash_occupied
    
    def draw(self):
        board = 240
        can_occupy = (230,232,230)
        occupied = (0,135,0)
        ball = (255,0,0)
        
        img = np.ones((self.draw_size, self.draw_size,3), dtype='uint8')*board
        
        is_in_tl,top_occupied, left_occupied, slash_occupied, backslash_occupied = self.decode()
        
        # TOP Line
        color = can_occupy
        if top_occupied:
            color = occupied
        cv2.line(img,(0,0),(self.draw_size-1, 0), color )
        
        # LEFT Line
        color = can_occupy
        if left_occupied:
            color = occupied
        cv2.line(img,(0,0),(0, self.draw_size-1), color )
        
        # SLASH line
        color = can_occupy
        if slash_occupied:
            color = occupied
        cv2.line(img,(0,self.draw_size),(self.draw_size-1,0), color )
        color = can_occupy
        
        # BACKSLASH Line
        if backslash_occupied:
            color = occupied
        cv2.line(img,(0,0),(self.draw_size-1,self.draw_size-1), color )
        
        # BALL in the TOP LEFT field
        color = can_occupy
        if is_in_tl:
            cv2.rectangle(img,(0,0),(1,1), ball, 1 )
        
        return img  
    
class Board():
    def __init__(self, width=8, height=12,  draw_size = 15):
        self.width = width+2
        self.height = height+2
        self.draw_size = draw_size
        self.ball_pos = (height//2+1, width//2+1)
        self.player_to_move = 0
        self.moves = 0
        self.data = []
        
        # Init start position
        for row in range(self.height):
            for col in range(self.width):
                block = SinlgeBlock(30, draw_size = draw_size)
                self.data.append(block)
                if row >1 and row <self.height-2:
                    if col >0 and col <self.width-1:
                        block.value=0
                if row ==2:
                    block.value=block.value | 2**1
                if col ==1:
                    block.value=block.value | 2**2

        # goal
        self.data[1 * self.width + self.width//2].value = 2
        self.data[1 * self.width + self.width//2-1].value = 6
        self.data[2 * self.width + self.width//2].value = 0
        self.data[2 * self.width + self.width//2-1].value = 0

        self.data[(self.height-2) * self.width + self.width//2].value = 0
        self.data[(self.height-2) * self.width + self.width//2-1].value = 4
        
        # set winning locations
        self.winning_positions = {
            0: [(self.width//2,1),(self.width//2-1,1),(self.width//2+1,1)],
            1: [(self.width//2,self.height-1),(self.width//2-1,self.height-1),(self.width//2+1,self.height-1)]
        }

        # ball
        self.data[(self.ball_pos[0]) * self.width + self.ball_pos[1]].value = 1
        
        # coords table (offset y, offset x, value chenge in terms of power of 2, move dy, move dx)
        self.coords_table = {
            "TL": (-1, -1, 4, -1, -1),
            "T":  (-1,  0, 2, -1,  0),
            "TR": (-1,  0, 3, -1,  1),
            "L":  ( 0, -1, 1,  0, -1),
            "R":  ( 0,  0, 1,  0,  1),
            "BL": ( 0, -1, 3,  1, -1),
            "B":  ( 0,  0, 2,  1,  0),
            "BR": ( 0,  0, 4,  1,  1) 
        }

    def copy(self):
        result = Board(self.width-2, self.height-2, draw_size=self.draw_size)
        result.ball_pos = (self.ball_pos[0],self.ball_pos[1])

        result.player_to_move = self.player_to_move 
        result.moves = self.moves
        result.data = [d.copy() for d in self.data]

        return result
     
    def possible_moves(self):
        result ={}
        
        for key in self.coords_table:
            oy, ox, p,_,_ = self.coords_table[key]
            result[key]=(self.data[(self.ball_pos[0]+oy) * self.width + self.ball_pos[1]+ox].value & 2**p == 0)

        return result
    
    def move(self, move):
        # Check if move is possible
        pm = self.possible_moves()
        if not move in pm or not pm[move]:
            return False, self.player_to_move, None
        
        change_player = True
        move_oy, move_ox, move_p, dy, dx = self.coords_table[move]
        by,bx = self.ball_pos
        
        # Mark path
        self.data[(by+move_oy) * self.width + bx+move_ox].value |= 2**move_p
        
        # Move ball
        self.data[(by) * self.width + bx].value &= 254
        self.data[(by+dy) * self.width + bx+dx].value |= 1
        self.ball_pos = (by+dy,bx+dx)
        
        # Check who should move 
        new_moves = self.possible_moves()
        blocked_ways = 0
        for key in new_moves:
            if not new_moves[key]:
                blocked_ways+=1
        change_player = (blocked_ways==1)       
        
        # Check winner (no move)
        if blocked_ways==8:
            return True, None, 1 - self.player_to_move
        
        # Check winner (goal)
        for potential_winner in self.winning_positions:
            for x,y in self.winning_positions[potential_winner]:
                if x == self.ball_pos[1] and y == self.ball_pos[0]:
                    return True, None, potential_winner
        
        if change_player:
            self.player_to_move = 1 - self.player_to_move
            self.moves += 1
            
        return True, self.player_to_move, None
                
    def draw(self):
        img = np.zeros((self.draw_size*self.height,self.draw_size*self.width,3), dtype='uint8')
        for row in range(self.height):
            for col in range(self.width):  
                block = self.data[row * self.width + col].draw()
                oy = row*self.draw_size
                ox = col*self.draw_size
                img[oy:oy+self.draw_size, ox:ox+self.draw_size] = block
        cv2.rectangle(img,(1,1),(img.shape[1], img.shape[0]), (0,135,0),self.draw_size*2-3)
        font_size = 0.8*self.draw_size/15
        spacing = int(np.ceil(2 *self.draw_size/15))
        cv2.putText(img,f"M:{self.moves} P:{self.player_to_move} ({self.ball_pos[1]},{self.ball_pos[0]})",(self.draw_size-1, self.draw_size-spacing), cv2.FONT_HERSHEY_PLAIN, font_size, (255,255,255))
        cv2.putText(img,f"papersoccer_env",(self.draw_size-1, img.shape[0]-spacing), cv2.FONT_HERSHEY_PLAIN, font_size, (255,255,255))
        return img
    
    @staticmethod
    def merge_images(images, in_row=6):
        h,w,_ = images[0].shape
        l = int(np.ceil(len(images)/in_row))
        index = 0
        
        merged = np.zeros(((h+1)*l-1, (w+1)*in_row-1, 3), dtype='uint8')
        
        for y in range(l):
            for x in range(in_row):
                if index>=len(images):
                    break
                merged[(h+1)*y:(h+1)*y+h,(w+1)*x:(w+1)*x+w] = images[index]
                index+=1

        return merged
    
    @staticmethod
    def play_sequence(sequence, verbose = False):
        sb = Board(draw_size=15)
        states = []
        for si,s in enumerate(sequence):
            valid_move, next_player, winner = sb.move(s)
            if verbose:
                print(f"{si+1}: {s:2s} valid move={valid_move} next_player:{next_player} winner:{winner}")
            states.append(sb.draw())
        if verbose:
            print(sb.possible_moves())
        return sb, states[-1], Board.merge_images(states)