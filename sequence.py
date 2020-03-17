import numpy as np

from base64 import b64encode, b64decode

from papersoccer_env import get_coord_table

class ThreeBitPacker:
    def __init__(self):
        self.bits = [] 
        self.mult = np.array([128,64,32,16,8,4,2,1]).astype('uint8')

    def add(self, val):
        assert(val>=0 and val<=7)

        self.bits.append(val&1>0)
        self.bits.append(val&2>0)
        self.bits.append(val&4>0)

    def encode(self):
        values = []
        first_val = len(self.bits) % 8
        values.append(first_val&1>0)
        values.append(first_val&2>0)
        values.append(first_val&4>0)

        values += self.bits.copy()
        while len(values)%8 != 0:
            values.append(False)

        values = np.array(values).astype('uint8').reshape(-1,8)
        values = values * self.mult
        values = values.sum(axis=1).astype('uint8')

        return str(b64encode(values))[2:-1]

    def set(self, val):
        values = np.array([int(b) for b in b64decode(val)])
        values = np.expand_dims(values, axis=1)
        values = np.repeat(values, 8, axis=1)
        values = ((values & self.mult)>0).astype('uint8')
        values = values.reshape(-1)
        mod = values[0] + values[1]*2 + values[2]*4

        self.bits = []
        for v in values[3:]:
            self.bits.append(v>0)

        while len(self.bits)%8 != mod:
            self.bits = self.bits[:-1]

    def get_indexes(self):
        data = []
        for off in range(0,len(self.bits),3):
            v = self.bits[off] + self.bits[off+1]*2 + self.bits[off+2]*4
            data.append(v)
        return data

def encode_moves(moves_sequence):
    move_to_coord_index = {}
    for i,k in enumerate(get_coord_table()):
        move_to_coord_index[k]=i

    data = ThreeBitPacker()
    for move in moves_sequence:
        data.add(move_to_coord_index[move])

    return data.encode()

def decode_moves(encoded):
    data = ThreeBitPacker()
    data.set(encoded)
    indexes = data.get_indexes()    
    
    coord_to_move = {}
    for i,k in enumerate(get_coord_table()):
        coord_to_move[i]=k

    return [coord_to_move[i] for i in indexes]
