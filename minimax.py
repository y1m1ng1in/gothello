import copy

from board import (Board, Move, ILLEGAL_MOVE, CONTINUE, 
  GAME_OVER, PLAYER_BLACK, PLAYER_WHITE)

class Minimax(Board):

  def __init__(self, depth=3, prune=False, print_leaves=False):
    super().__init__()
    self.depth = depth
    self.prune = prune
    self.alpha = None
    self.beta = None
    if self.prune: # set alpha and beta to some unreachable value temporarily
      self.alpha = -999999 
      self.beta = 999999
    self.print_leaves = print_leaves

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
    if self.prune:
      return self.alpha_beta_minimax()
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
      b = self.__board_after_moving(self, m)
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
      b = self.__board_after_moving(board, m)
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
      b = self.__board_after_moving(board, m)
      values.append(self.__min_value(b, depth - 1))
    return max(values)

  def alpha_beta_minimax(self):
    _, m = self.__alpha_beta_max_value(self, self.depth)
    return m

  def __alpha_beta_max_value(self, board, depth):
    if depth <= 0:
      if self.print_leaves:
        print("depth at 0:\n" + str(board))
      return board.evaluate(), None

    v = -999999
    to_move = None

    moves = board.gen_moves()
    if not moves:
      if self.print_leaves:
        print("depth at 0:\n" + str(board))
      return board.evaluate(), None

    for m in moves:
      b = self.__board_after_moving(board, m)
      child_val, _ = self.__alpha_beta_min_value(b, depth - 1)
      if child_val > v:
        to_move = m
        v = child_val
      if v >= self.beta:
        return v, m
      self.alpha = max(self.alpha, v)
    
    assert to_move
    return v, to_move

  def __alpha_beta_min_value(self, board, depth):
    if depth <= 0:
      if self.print_leaves:
        print("depth at 0:\n" + str(board))
      return board.evaluate(), None

    v = 999999
    to_move = None 

    moves = board.gen_moves()
    if not moves:
      if self.print_leaves:
        print("depth at 0:\n" + str(board))
      return board.evaluate(), None

    for m in moves:
      b = self.__board_after_moving(board, m)
      child_val, _ = self.__alpha_beta_max_value(b, depth - 1)
      if child_val < v:
        to_move = m
        v = child_val
      if v <= self.alpha:
        return v, m
      self.beta = min(self.beta, v)
    
    assert to_move
    return v, to_move
  
  def __board_after_moving(self, board, move):
    b = copy.deepcopy(board)
    result = b.try_move(move)
    if result == ILLEGAL_MOVE:
      raise Exception("illegal move in minimax")
    return b
