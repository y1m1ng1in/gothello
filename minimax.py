import copy
import random

from board import (Board, Move, ILLEGAL_MOVE, CONTINUE, 
  GAME_OVER, PLAYER_BLACK, PLAYER_WHITE)

ITER_DEEPENING_EXCEPTION = 1

class TerminationException(Exception):

  def __init__(self, 
               code=ITER_DEEPENING_EXCEPTION, 
               msg="iterative deepening resource exhausted"):
    self.code = code
    self.msg = msg


class Minimax(Board):

  def __init__(self, depth=3, prune=False, 
               max_visited=10000, iter_deepening=False, 
               move_ordering=False,
               print_leaves=False, print_stats=False):
    super().__init__()
    self.depth = depth
    self.prune = prune
    self.alpha = None
    self.beta = None

    self.print_leaves = print_leaves
    self.print_stats = print_stats

    # set alpha and beta to some unreachable value temporarily
    if self.prune: 
      self.alpha = -999999 
      self.beta = 999999
    
    # test-purpse -- how many states have been visited
    self.nvisited = 0 

    self.reorder_move = move_ordering
  
    # whether search by iterative deepening
    self.iter_deepening = iter_deepening  
  
    # upper bound of visiting node for iterative deepening
    self.max_visited = max_visited  

  def evaluate(self):
    score = 0
    for row in self.board:
      for stone in row:
        if stone == PLAYER_BLACK:
          score += 1
        elif stone == PLAYER_WHITE:
          score -= 1
    return score

  def move_ordering(self, moves):
    if not moves: # no possible moves
      return None

    to_pop = []
    for i in range(len(moves)):
      if not moves[i].is_pass:
        x, y = moves[i].x, moves[i].y
        assert x >= 0 and x <= 4 and y >= 0 and y <= 4
        if x > 0:
          if self.board[x - 1][y] == self.opponent(self.to_move):
            to_pop.append(i)
            continue 
        if x < 4:
          if self.board[x + 1][y] == self.opponent(self.to_move):
            to_pop.append(i)
            continue
        if y > 0:
          if self.board[x][y - 1] == self.opponent(self.to_move):
            to_pop.append(i)
            continue
        if y < 4:
          if self.board[x][y + 1] == self.opponent(self.to_move):
            to_pop.append(i)
            continue

    new_moves = []
    for i in to_pop:
      new_moves.append(moves[i])
    for i in sorted(to_pop, reverse=True):
      del moves[i]
    new_moves += moves
    return new_moves

  def decision(self):
    if self.prune and self.iter_deepening:
      return self.alpha_beta_minimax_iter_deepening()
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
    val, _ = self.__terminal_status(board)
    if val:
      return val
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
    val, _ = self.__terminal_status(board)
    if val:
      return val
    moves = board.gen_moves()
    if not moves:
      return board.evaluate() # at leaf node, return eval
    values = []
    for m in moves:
      b = self.__board_after_moving(board, m)
      values.append(self.__min_value(b, depth - 1))
    return max(values)

  def alpha_beta_minimax(self, depth=None):
    if depth:
      _, move = self.__alpha_beta_max_value(self, depth)
    else:
      _, move = self.__alpha_beta_max_value(self, self.depth)
    return move

  def alpha_beta_minimax_iter_deepening(self):
    self.nvisited = 0
    depth = 1
    last_depth_move = None

    # at most 25 depth, since there are only 25 stones on board
    while self.nvisited < self.max_visited and depth <= 25:
      try:
        move = self.alpha_beta_minimax(depth=depth)
        last_depth_move = move
        depth += 1
        if not move:
          break
      except TerminationException as e:
        if e.code == ITER_DEEPENING_EXCEPTION:
          assert last_depth_move
          depth += 1  # adjust for output message below
          move = last_depth_move
          
      if self.print_stats:
        print("current depth:", depth-1, " visited:", self.nvisited)

    if self.print_stats:
      print("visited ", self.nvisited)

    return move

  def __alpha_beta_max_value(self, board, depth):
    self.nvisited += 1  # increment visisted node
    if self.nvisited >= self.max_visited:
      # terminate searching when maximum number of node visited has been reached
      if self.iter_deepening:
        raise TerminationException(
          code=ITER_DEEPENING_EXCEPTION, 
          msg="iterative deepening resource exhausted")

    if depth <= 0:
      if self.print_leaves:
        print("depth at 0:\n" + str(board))
      return board.evaluate(), None

    val, move = self.__terminal_status(board)
    if val:
      return (val, move)

    # generate all possible moves
    moves = board.gen_moves()
    if self.reorder_move:
      moves = board.move_ordering(moves)

    if not moves: # no possible move currently, return board's evaluated value
      if self.print_leaves:
        print("depth at 0:\n" + str(board))
      return board.evaluate(), None

    v = -999999
    move_candidates = []

    for m in moves:
      b = self.__board_after_moving(board, m) # generate new board after move -- m
      v_child, _ = self.__alpha_beta_min_value(b, depth - 1)  # search recursively
      
      if v_child > v:
        # update maximum value, when child's value is larger
        v = v_child
        move_candidates = [m]
      elif v_child == v:  
        # if child's value is same as current maximum value, append it to the move candidate list
        move_candidates.append(m)
      
      if v >= self.beta:
        if move_candidates:
          pick_move = random.randint(0, len(move_candidates) - 1)
          return v, move_candidates[pick_move]
        else:
          return v, m
      
      self.alpha = max(self.alpha, v)
    
    assert move_candidates

    # randomly pick a move from all possible move candidates
    pick_move = random.randint(0, len(move_candidates) - 1) 
    return v, move_candidates[pick_move]

  def __alpha_beta_min_value(self, board, depth):
    self.nvisited += 1  # increment visisted node
    if self.nvisited >= self.max_visited:
      # terminate searching when maximum number of node visited has been reached
      if self.iter_deepening:
        raise TerminationException(
          code=ITER_DEEPENING_EXCEPTION,
          msg="iterative deepening resource exhausted")

    if depth <= 0:
      if self.print_leaves:
        print("depth at 0:\n" + str(board))
      return board.evaluate(), None

    val, move = self.__terminal_status(board)
    if val:
      return (val, move)

    moves = board.gen_moves()
    if self.reorder_move:
      moves = board.move_ordering(moves)

    if not moves:
      if self.print_leaves:
        print("depth at 0:\n" + str(board))
      return board.evaluate(), None

    v = 999999
    move_candidates = []

    for m in moves:
      b = self.__board_after_moving(board, m)
      v_child, _ = self.__alpha_beta_max_value(b, depth - 1)

      if v_child < v:
        v = v_child
        move_candidates = [m]
      elif v_child == v:
        move_candidates.append(m)

      if v <= self.alpha: 
        if move_candidates:
          pick_move = random.randint(0, len(move_candidates) - 1)
          assert pick_move < len(move_candidates) and pick_move >= 0
          return v, move_candidates[pick_move]
        else:
          return v, m

      self.beta = min(self.beta, v)
    
    assert move_candidates
    pick_move = random.randint(0, len(move_candidates) - 1)
    return v, move_candidates[pick_move]
  
  def __board_after_moving(self, board, move):
    b = copy.deepcopy(board)
    result = b.try_move(move)
    if result == ILLEGAL_MOVE:
      raise Exception("illegal move in minimax")
    return b

  def __terminal_status(self, board):
    if board.game_status == GAME_OVER:
      if board.referee() == PLAYER_BLACK:
        return 999999, None
      else:
        return -999999, None
    else:
      return None, None