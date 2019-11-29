import copy

from board import (Board, Move, ILLEGAL_MOVE, CONTINUE, 
  GAME_OVER, PLAYER_BLACK, PLAYER_WHITE)

class Minimax(Board):

  def __init__(self, depth=3):
    super().__init__()
    self.depth = depth

  def evaluate(self):
    score = 0
    for row in self.board:
      for stone in row:
        if stone == PLAYER_BLACK:
          score += 1
        elif stone == PLAYER_WHITE:
          score -= 1
    return score

  def decision(self):
    return self.minimax()

  def minimax(self):
    assert self.to_move == PLAYER_BLACK
    if self.depth < 0:
      raise Exception("depth error at entry point of minimax")
    moves = self.gen_moves()
    if not moves:
      return None # move not available
    values = []
    for m in moves:
      b = copy.deepcopy(self)
      result = b.try_move(m)
      if result == ILLEGAL_MOVE:
        raise Exception("illegal move in minimax")
      values.append(self.__min_value(b, self.depth - 1))
    i = values.index(max(values))
    return moves[i]

  def __min_value(self, board, depth):
    assert board.to_move == PLAYER_WHITE
    if depth <= 0:
      return board.evaluate() # reach upper bound of depth
    moves = board.gen_moves()
    if not moves:
      return board.evaluate() # at leaf node, return eval
    values = []
    for m in moves:
      b = copy.deepcopy(board)
      result = b.try_move(m)
      if result == ILLEGAL_MOVE:
        raise Exception("ilegal move in minimax")
      values.append(self.__max_value(b, depth - 1))
    return min(values)

  def __max_value(self, board, depth):
    assert board.to_move == PLAYER_BLACK
    if depth <= 0:
      return board.evaluate() # reach upper bound of depth
    moves = board.gen_moves()
    if not moves:
      return board.evaluate() # at leaf node, return eval
    values = []
    for m in moves:
      b = copy.deepcopy(board)
      result = b.try_move(m)
      if result == ILLEGAL_MOVE:
        raise Exception("ilegal move in minimax")
      values.append(self.__min_value(b, depth - 1))
    return max(values)

  

