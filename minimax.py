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
               move_ordering=False, eval_method="number",
               print_leaves=False, print_stats=False):
    super().__init__()
    self.depth = depth
    self.prune = prune
    self.alpha = None
    self.beta = None

    self.print_leaves = print_leaves
    self.print_stats = print_stats

    # the method for evaluating a board
    self.evaluate_method = eval_method

    # a set of connected stones
    self.connected_stones = set()

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
    if self.evaluate_method == "number":
      return self.__evaluate_number()
    elif self.evaluate_method == "connected":
      return self.__evaluate_number() * 2 + self.__evaluate_connected()
    else:
      raise Exception("unexpected evaluate method in minimax")

  def __evaluate_number(self):
    score = 0
    for row in self.board:
      for stone in row:
        if stone == PLAYER_BLACK:
          score += 1
        elif stone == PLAYER_WHITE:
          score -= 1
    return score

  def __evaluate_connected(self):
    return len(self.connected_stones)

  def update_connected_stones(self):  
    # update connected stones every time after try_move(), 
    # and before making decision
    self.connected_stones = set()
    for i in range(5):
      for j in range(5):
        if (j < 4 
            and self.board[i][j] == PLAYER_BLACK 
            and self.board[i][j + 1] == PLAYER_BLACK):
          self.connected_stones.add((i, j))
          self.connected_stones.add((i, j + 1))
        if (i < 4 
            and self.board[i][j] == PLAYER_BLACK 
            and self.board[i + 1][j] == PLAYER_BLACK):
          self.connected_stones.add((i, j))
          self.connected_stones.add((i + 1, j))

  def __around_stone(self, x, y, side):
    # decide whether there exists stone with color "side" around (x, y)
    assert x >= 0 and x <= 4 and y >= 0 and y <= 4
    if x > 0:
      if self.board[x - 1][y] == side:
        return True
    if x < 4:
      if self.board[x + 1][y] == side:
        return True
    if y > 0:
      if self.board[x][y - 1] == side:
        return True
    if y < 4:
      if self.board[x][y + 1] == side:
        return True 
    return False
     
  def move_ordering(self, moves):
    if not moves: # no possible moves
      return None

    to_pop = []
    to_pop_connected = []
    for i in range(len(moves)):
      if not moves[i].is_pass:
        x, y = moves[i].x, moves[i].y
        assert x >= 0 and x <= 4 and y >= 0 and y <= 4
        if self.evaluate_method == "number":
          #if self.__around_stone(x, y, self.opponent(self.to_move)):
          if self.__around_stone(x, y, PLAYER_WHITE):
            to_pop.append(i)
        elif self.evaluate_method == "connected":
          #if (self.__around_stone(x, y, self.opponent(self.to_move)) 
          #    and self.__is_connected(moves[i])):
          if (self.__around_stone(x, y, PLAYER_WHITE) 
              and self.__is_connected(moves[i])):
            to_pop_connected.append(i)
          #elif self.__around_stone(x, y, self.opponent(self.to_move)):
          elif self.__around_stone(x, y, PLAYER_WHITE):
            to_pop.append(i)
        else:
          raise Exception("unexpected evaluate methode in minimax")

    new_moves = []

    # add moves that around opponent and preserve connection first
    to_pop = to_pop_connected + to_pop

    for i in to_pop:
      new_moves.append(moves[i])
    for i in sorted(to_pop, reverse=True):
      del moves[i]

    # add rest of the moves
    new_moves += moves

    return new_moves

  def __is_connected(self, move):
    assert (move 
            and move.x >= 0 
            and move.x <= 4 
            and move.y >= 0 
            and move.y <= 4) 
    if move.is_pass:
      return False 
    x, y = move.x, move.y
    for stone in self.connected_stones:
      if ((x - 1 == stone[0] and y == stone[1]) or
          (x + 1 == stone[0] and y == stone[1]) or
          (x == stone[0] and y - 1 == stone[1]) or
          (x == stone[0] and y + 1 == stone[1])):
        return True
    return False

  def decision(self):
    self.update_connected_stones()
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
    b.update_connected_stones()
    return b

  def __terminal_status(self, board):
    if board.game_status == GAME_OVER:
      if board.referee() == PLAYER_BLACK:
        return 999999, None
      else:
        return -999999, None
    else:
      return None, None