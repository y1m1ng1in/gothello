from board import (Board, Move, ILLEGAL_MOVE, CONTINUE, 
  GAME_OVER, PLAYER_BLACK, PLAYER_WHITE)

class MinimaxUtility(Board):

  def __init__(self,
               side,
               eval_method="number", 
               scoring={
                 'stone': 1,
                 'black connection': 1,
                 'white connection': 1,
                 'black eye': 1,
                 'white eye': 1
               }):
    super().__init__()

    if side == "black":
      self.side = PLAYER_BLACK
    elif side == "white":
      self.side = PLAYER_WHITE
    else:
      raise Exception("unexpected side")

    # the method for evaluating a board
    self.evaluate_method = eval_method

    # value for scoring board
    self.eval = scoring

  def evaluate(self, adjust=False):
    evaluation = self.eval

    def number():
      score_number = self.__evaluate_number() * evaluation['stone']
      if self.side == PLAYER_WHITE:
        return -score_number
      return score_number

    def eyes():
      ne_black, ne_white = self.__evaluate_eye()
      score_eyes = (ne_black * evaluation['black eye'] 
                    - ne_white * evaluation['white eye']) 
      if self.side == PLAYER_WHITE:
        return -score_eyes
      return score_eyes
              
    if self.evaluate_method == "number":
      return number()

    elif self.evaluate_method == "eye":
      return number() + eyes()

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

  def __evaluate_eye(self):
    nblack = self.__count_eye(PLAYER_BLACK)
    nwhite = self.__count_eye(PLAYER_WHITE)
    return len(nblack), len(nwhite)

  def __check_eye(self, x, y, side):
    def check(x, y):
      if x < 0 or x > 4 or y < 0 or y > 4:
        return 0
      if self.board[x][y] == side:
        return 1
      else:
        return -1
    if (check(x - 1, y) != -1
        and check(x + 1, y) != -1
        and check(x, y - 1) != -1
        and check(x, y + 1) != -1):
      return True 
    return False

  def __count_eye(self, side):
    eye_coords = set()
    for i in range(5):
      for j in range(5):
        if self.board[i][j] == 0:
          if self.__check_eye(i, j, side):
            eye_coords.add((i, j))
    return eye_coords

  def avoid_opponent_eye(self, moves):
    if not moves:
      return [], []

    def check_my_eye(x, y):
      if self.__check_eye(x, y, self.to_move):
        return True
      return False

    result = set()
    remained = set()
    for move in moves:
      added = False
      if self.__detect_opponent_eye(move):
        x, y = move.x, move.y
        self.board[x][y] = self.to_move # move to (x,y) temporarily
        if x > 0 and self.board[x - 1][y] != self.to_move:
          if check_my_eye(x - 1, y):
            result.add(move)
            added = True
        if x < 4 and self.board[x + 1][y] != self.to_move:
          if check_my_eye(x + 1, y):
            result.add(move)
            added = True
        if y > 0 and self.board[x][y - 1] != self.to_move:
          if check_my_eye(x, y - 1):
            result.add(move)
            added = True
        if y < 4 and self.board[x][y + 1] != self.to_move:
          if check_my_eye(x, y + 1):
            result.add(move)
            added = True 
        if not added:
          remained.add(move)
        self.board[x][y] = 0  # recover to original value
      else:
        result.add(move)
    
    return list(result), list(remained)

  def __detect_opponent_eye(self, move):
    assert not move.is_pass

    count = 0
    x, y = move.x, move.y

    assert (self.board[x][y] == 0 
            and x >= 0 
            and x <= 4 
            and y >= 0 
            and y <= 4)
            
    if x == 0 or x == 4:
      count += 1
    if y == 0 or y == 4:
      count += 1
    if x > 0 and self.board[x - 1][y] == self.opponent(self.to_move):
      count += 1
    if x < 4 and self.board[x + 1][y] == self.opponent(self.to_move):
      count += 1
    if y > 0 and self.board[x][y - 1] == self.opponent(self.to_move):
      count += 1
    if y < 4 and self.board[x][y + 1] == self.opponent(self.to_move):
      count += 1

    if count >= 3:
      return True
    return False
