import copy
import random
import uuid

from board import (Board, Move, ILLEGAL_MOVE, CONTINUE, 
  GAME_OVER, PLAYER_BLACK, PLAYER_WHITE)

from minimax_utility import MinimaxUtility


inf = 999999

iter_deepening_resource_exhausted = 1

print_killer_moves = 1
print_move_paths = 2


class TerminationException(Exception):

  def __init__(self, 
               code, 
               msg="iterative deepening resource exhausted"):
    self.code = code
    self.msg = msg


class AlphaBetaPruning(MinimaxUtility):

  def __init__(self,
               side,
               depth=3,
               iterdeepening=False,
               maximum_visited=3000,
               eval_method="number",
               scoring={
                 'stone': 1,
                 'black connection': 1,
                 'white connection': 2
               },
               move_selection=False,
               print_leaves=False, 
               print_stats=False,
               print_move_lists=False):
          
    super().__init__(side, 
                     eval_method=eval_method, 
                     scoring=scoring)

    self.depth = depth

    self.print_leaves = print_leaves
    self.print_stats = print_stats
    self.print_move_lists = print_move_lists

    # whether select by the number of liberties if values are same
    self.select_by_nlib = move_selection
    
    # test-purpse -- how many states have been visited
    self.nvisited = 0 
    self.npruned = 0
    self.nttablehit = 0

    # recorded best path during searching
    self.move_path = [None, []]
    self.killer_moves = []

    # whether or not iterative deepening search
    self.iterdeepening = iterdeepening
    self.maximum_visited = maximum_visited
    self.stop_deepening = False

    # hash key for transposition table, this will be 
    # manually updated after try_move() being called 
    self.zobrist_key = 0

  def decision(self):
    self.nvisited, self.npruned, self.nttablehit = 0, 0, 0
    self.move_path = [None, []]
    zobrist_table = AlphaBetaPruning.init_zobrist_table()
    transposition = {}
    if not self.iterdeepening:
      _, move = self.__max_value(self, self.depth, -inf, inf, [], 
                                 transposition=transposition,
                                 zobrist_table=zobrist_table)
      self.__print_stats()
      self.__print_moves(print_move_paths)
      self.__generate_killer_moves(self.depth)
      self.__print_moves(print_killer_moves)
      return move
    else:
      self.stop_deepening = False
      return self.__iter_deepening()

  def __max_value(self, board, depth, alpha, beta, path, 
                  transposition=None, zobrist_table=None):
    self.nvisited += 1
    value, moves = self.__terminal_test(board, depth)
    if value != None and not moves: # end recursion
      self.__update_move_path(path, value, is_max=False)
      return value, None 

    assert value == None and moves
 
    if transposition != None:
      if board.zobrist_key in transposition: 
        self.nttablehit += 1
        value = transposition[board.zobrist_key] 
        self.__update_move_path(path, value, is_max=True)
        return value, None

    value = -inf
    move_candidates = []  # my move candidates that have same eval value 
    max_nlib = -1

    for move, nlib in moves:
      b = AlphaBetaPruning.board_after_moving(board, move, 
                                              zobrist_table=zobrist_table)
      
      p = [m for m in path]
      p.append(move)
      
      opp_value, _ = self.__min_value(b, depth - 1, alpha, beta, p, 
                                      transposition=transposition, 
                                      zobrist_table=zobrist_table)

      if transposition != None:
        if b.zobrist_key in transposition:
          assert opp_value == transposition[b.zobrist_key]
        else:
          transposition[b.zobrist_key] = opp_value
      
      # when a greater value is returned
      if opp_value > value:  
        value = opp_value
        move_candidates = [move]
        max_nlib = nlib
      
      # when the returned value is same as current largest
      elif opp_value == value:    
        if self.select_by_nlib:
          # candidate selection by number of liberties is enabled
          if nlib > max_nlib:
            # reset candidate list if new maximum nlib arrives
            move_candidates = [move]
            max_nlib = nlib
          elif nlib == max_nlib:
            # nlib is same as current maximum, append move to candidate list
            move_candidates.append(move)
        else:
          # candidate selection by number of liberties is disabled, append
          # move to candidate list directly
          move_candidates.append(move)

      if value >= beta:
        self.npruned += 1
        return value, AlphaBetaPruning.random_pick_move(move_candidates)

      alpha = max(alpha, value)

    return value, AlphaBetaPruning.random_pick_move(move_candidates)

  def __min_value(self, board, depth, alpha, beta, path, 
                  transposition=None, zobrist_table=None):
    self.nvisited += 1
    value, moves = self.__terminal_test(board, depth)
    if value != None and not moves: # end recursion
      self.__update_move_path(path, value, is_max=True)
      return value, None 
    
    assert value == None and moves

    if transposition != None:
      if board.zobrist_key in transposition:
        self.nttablehit += 1
        value = transposition[board.zobrist_key] 
        self.__update_move_path(path, value, is_max=False)
        return value, None

    value = inf
    move_candidates = []
    max_nlib = -1

    for move, nlib in moves:
      b = AlphaBetaPruning.board_after_moving(board, move, 
                                              zobrist_table=zobrist_table)

      p = [m for m in path]
      p.append(move)

      my_value, _ = self.__max_value(b, depth - 1, alpha, beta, p,
                                     transposition=transposition, 
                                     zobrist_table=zobrist_table)

      if transposition != None:
        if b.zobrist_key in transposition:
          assert my_value == transposition[b.zobrist_key]
        else:
          transposition[b.zobrist_key] = my_value

      if my_value < value:
        value = my_value
        move_candidates = [move]
        max_nlib = nlib

      elif my_value == value:
        if self.select_by_nlib:
          if nlib > max_nlib:
            max_nlib = nlib
            move_candidates = [move]
          elif nlib == max_nlib:
            move_candidates.append(move)
        else:
          move_candidates.append(move)

      if value <= alpha:
        self.npruned += 1
        return value, AlphaBetaPruning.random_pick_move(move_candidates)

      beta = min(beta, value)

    return value, AlphaBetaPruning.random_pick_move(move_candidates)

  def __terminal_test(self, board, depth):
    """ 
    Decide whether maximum depth is reached, and there is no possible move 
    at current state. And indicate whether we should continue searching 
    by returning a list of moves or returning None
    :return: evaluated value, None    if there is at terminal state
             None, a list of (move, nlib)   if there isn't at terminal state
    """
    if depth <= 0:
      return self.__eval(board), None
    
    if self.iterdeepening:
      if self.nvisited >= self.maximum_visited:
        raise TerminationException(iter_deepening_resource_exhausted)
      moves = self.__generate_moves(board, depth=depth)
    else:
      moves = self.__generate_moves(board)
    
    if not moves:
      if self.iterdeepening:
        self.stop_deepening = True
      return self.__eval(board), None
    
    return None, moves

  def __update_move_path(self, path, value, is_max=True):
    if is_max:
      if self.move_path[0] == None or value > self.move_path[0]:
        self.move_path[0] = value
        self.move_path[1] = [path]
      elif value == self.move_path[0]:
        self.move_path[1].append(path)
    else:
      if self.move_path[0] == None or value < self.move_path[0]:
        self.move_path[0] = value
        self.move_path[1] = [path]
      elif value == self.move_path[0]:
        self.move_path[1].append(path)

  def __eval(self, board):
    """
    Evaluate a board based on serial number of server side, and whether 
    dynamic_eval flag is enabled. 
    """
    return board.evaluate()

  def __generate_moves(self, board, depth=None):
    """
    Generate a list of possible moves based on board. If current_depth
    is provided, it will reorder the killer moves at current depth
    to the beginning of returned move list.
    """
    moves = board.gen_moves() # [(move1, nlib1), (move2, nlib2), ...]
    tmp = list(zip(*moves)) # [(move1, move2, ...), (nlib1, nlib2, ...)]

    if not moves:
      return []

    if depth != None and depth < len(self.killer_moves):
      assert depth <= len(self.killer_moves)
      index = len(self.killer_moves) - depth 
      for killer_move in self.killer_moves[index]:
        if killer_move in tmp[0]:
          i = tmp[0].index(killer_move) # index of (killer_move, nlib) in moves
          removed = moves.pop(i)  # remove it from its original position
          moves.insert(0, removed)  # re-add it to the beginning of moves
    
    return moves

  def __generate_killer_moves(self, d):
    """
    Based on move path, generate a list of killer moves at each 
    depth, the list is indexed by the depth number
    """
    self.killer_moves = [set() for _ in range(d)]
    for path in self.move_path[1]:
      for i in range(len(path)):
        self.killer_moves[i].add(path[i])

  @staticmethod
  def random_pick_move(moves):
    assert moves
    pick_move = random.randint(0, len(moves) - 1) 
    return moves[pick_move]

  @staticmethod
  def board_after_moving(board, move, zobrist_table=None):
    """
    Deepcopy a board(i.e. AlphaBetaPruning object), and try move,
    and manually update Zobrist hash value for new board
    :param board: AlphaBetaPruning object
    :param move: Move object
    :param zobrist_table: a zobrist table with initialized value, 
                          or None if not specified 
    :return: AlphaBetaPruning object after trying move, with new 
             zobrist hash key
    """
    # deep copy current state
    b = copy.deepcopy(board)
    
    # save original to_move, since try_move will change to_move to 
    # opponent side
    orig_to_move, orig_opp = b.to_move, b.opponent(b.to_move) 
    
    result, captured = b.try_move(move)
    if result == ILLEGAL_MOVE:
      raise Exception("illegal move in minimax")
    
    # now update Zobrist hash key manually
    if zobrist_table:
      for x, y in captured:
        # xor OUT original opponent side stone
        b.zobrist_key ^= zobrist_table[x][y][orig_opp - 1]
        # xor IN original to_move side stone
        b.zobrist_key ^= zobrist_table[x][y][orig_to_move - 1]
      # xor IN original new stone (original to_move side)
      b.zobrist_key ^= zobrist_table[move.x][move.y][orig_to_move - 1]
    
    return b

  @staticmethod
  def init_zobrist_table():
    table = [[[0 for _ in range(2)] for _ in range(5)] for _ in range(5)]
    for x in range(5):
      for y in range(5):
        for side in range(2):
          table[x][y][side] = uuid.uuid4().int 
    return table

  def __iter_deepening(self):
    """
    First, search 1 ply deep and record the best path of moves.
    Then search 1 ply deeper, but use the recorded path to inform 
    move ordering.
    """
    depth = 1
    stored_move = None
    zobrist_table = AlphaBetaPruning.init_zobrist_table()
    
    while self.nvisited < self.maximum_visited and depth <= 25:
      try:
        transposition = {}
        self.move_path = [None, []]
        v, move = self.__max_value(self, depth, -inf, inf, [], 
                                   transposition=transposition, 
                                   zobrist_table=zobrist_table)
        stored_move = move
        self.__print_moves(print_move_paths)
        self.__generate_killer_moves(depth)
        if self.stop_deepening:
          break
        if self.print_stats:
          print("at depth: ", depth, "value: ", v)
        self.__print_stats()
        self.__print_moves(print_killer_moves)
        depth += 1
      except TerminationException as e:
        if e.code == iter_deepening_resource_exhausted:
          if self.print_stats:
            print("resource exhausted ..")
          return stored_move

    return stored_move

  def __print_stats(self):
    if self.print_stats:
      print("number of states visited: ", self.nvisited - 1)
      print("number of returned by pruning: ", self.npruned)
      print("number of states hit ttable: ", self.nttablehit)

  def __print_moves(self, which):
    if self.print_stats and self.print_move_lists:
      if which == print_killer_moves:
        print("killer moves: ", 
              [[str(m) for m in ms] for ms in self.killer_moves]) 
      elif which == print_move_paths:
        print("move path: ", 
              self.move_path[0], 
              [[str(s) for s in ms] for ms in self.move_path[1]])