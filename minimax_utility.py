from board import (Board, Move, ILLEGAL_MOVE, CONTINUE, 
  GAME_OVER, PLAYER_BLACK, PLAYER_WHITE)

class MinimaxUtility(Board):

  def __init__(self, 
               eval_method="number", 
               scoring={'stone': 1,
                        'black connection': 1,
                        'white connection': 2,
                        'black eye': 3,
                        'white eye': 3}):
    super().__init__()

    # the method for evaluating a board
    self.evaluate_method = eval_method

    # a set of connected stones
    self.connected_black = set()
    self.connected_white = set()

    # value for scoring board
    self.eval = scoring

  def evaluate(self):
    def number():
      return self.__evaluate_number()
    
    def connected():
      nc_black, nc_white = self.__evaluate_connected()
      return (self.__evaluate_number() * self.eval['stone'] 
              + nc_black * self.eval['black connection'] 
              - nc_white * self.eval['white connection']) 
    
    def eyes():
      ne_black, ne_white = self.__evaluate_eye()
      return (self.__evaluate_number() * self.eval['stone'] 
              + ne_black * self.eval['black eye'] 
              - ne_white * self.eval['white eye'])  

    if self.evaluate_method == "number":
      return number()

    elif self.evaluate_method == "connected":
      return number() + connected()

    elif self.evaluate_method == "eye":
      return number() + eyes()

    elif self.evaluate_method == "connected eye":
      return number() + connected() + eyes()

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
    nblack = self.__count_maximum_connected_group(self.connected_black, PLAYER_BLACK)
    nwhite = self.__count_maximum_connected_group(self.connected_white, PLAYER_WHITE) 
    return nblack, nwhite

  def __count_maximum_connected_group(self, stone_set, side):
    coords = list(stone_set)
    coords.sort(key=lambda x: x[0])
    i = 0
    maximum = 0
    while i < len(coords):
      count = 0
      scratch = self.scratch_board()
      self.flood(scratch, side, coords[i][0], coords[i][1])
      i += 1
      for x in range(5):
        for y in range(5):
          if scratch[x][y]:
            count += 1
      maximum = max(maximum, count)
    return maximum

  def __evaluate_eye(self):
    nblack = self.__count_eye(PLAYER_BLACK)
    nwhite = self.__count_eye(PLAYER_WHITE)
    return len(nblack), len(nwhite)

  def __count_eye(self, side):
    eye_coords = set()

    def check(x, y):
      if x < 0 or x > 4 or y < 0 or y > 4:
        return 0
      if self.board[x][y] == side:
        return 1
      else:
        return -1

    for i in range(5):
      for j in range(5):
        if self.board[i][j] == 0:
          if (check(i - 1, j) != -1
              and check(i + 1, j) != -1
              and check(i, j - 1) != -1
              and check(i, j + 1) != -1):
            eye_coords.add((i, j))
    
    return eye_coords

  def update_connected_stones(self):  
    # update connected stones every time after try_move(), 
    # and before making decision
    self.connected_black = self.__update_connected_stones(PLAYER_BLACK)
    self.connected_white = self.__update_connected_stones(PLAYER_WHITE)

  def __update_connected_stones(self, side):  
    connected = set()
    for i in range(5):
      for j in range(5):
        if (j < 4 
            and self.board[i][j] == side 
            and self.board[i][j + 1] == side):
          connected.add((i, j))
          connected.add((i, j + 1))
        if (i < 4 
            and self.board[i][j] == side 
            and self.board[i + 1][j] == side):
          connected.add((i, j))
          connected.add((i + 1, j))
    return connected
     
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
          if self.__around_stone(x, y, PLAYER_WHITE):
            to_pop.append(i)

        elif (self.evaluate_method == "connected" 
              or self.evaluate_method == "connected eye"):
          if self.__is_connected(moves[i]):
            to_pop_connected.append(i)

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

  def __is_connected(self, move):
    assert (move 
            and move.x >= 0 
            and move.x <= 4 
            and move.y >= 0 
            and move.y <= 4) 
    if move.is_pass:
      return False 
    x, y = move.x, move.y
    for stone in self.connected_black:
      if ((x - 1 == stone[0] and y == stone[1]) or
          (x + 1 == stone[0] and y == stone[1]) or
          (x == stone[0] and y - 1 == stone[1]) or
          (x == stone[0] and y + 1 == stone[1])):
        return True
    return False