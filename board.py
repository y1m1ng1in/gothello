PLAYER_BLACK = 1  
PLAYER_WHITE = 2
OBSERVER = 3
  
GAME_OVER = 1
CONTINUE = 0
ILLEGAL_MOVE = -1

class Move:

  def __init__(self, x, y, is_pass=False):
    self.x = x
    self.y = y
    self.is_pass = is_pass

  @staticmethod
  def letter(index):
    if index == 0:
      return 'a'
    elif index == 1:
      return 'b'
    elif index == 2:
      return 'c'
    elif index == 3:
      return 'd'
    elif index == 4:
      return 'e'
    else:
      raise Exception("bad index in Move")

  @staticmethod
  def digit(letter):
    if letter == 'a':
      return 0
    elif letter == 'b':
      return 1
    elif letter == 'c':
      return 2
    elif letter == 'd':
      return 3
    elif letter == 'e':
      return 4
    else:
      raise Exception("bad letter in Move")

  @staticmethod
  def parse_string(s):
    if s == "pass":
      return Move(0, 0, is_pass=True)
    else:
      if len(s) != 2:
        raise Exception("bad argument for parsing string in Move")
      else:
        x = Move.digit(s[0])
        y = int(s[1]) - 1
        if x < 0 or x > 4 or y < 0 or y > 4:
          raise Exception("bad index in parse_string() in Move")
        return Move(x, y)

  def __str__(self):
    if not self.is_pass:
      return Move.letter(self.x) + str(self.y + 1)
    else:
      return "pass"

  def __eq__(self, other):
    if (self.x == other.x 
        and self.y == other.y 
        and self.is_pass == other.is_pass):
      return True
    return False

  def __hash__(self):
    return hash(tuple([self.x, self.y, self.is_pass]))


class Board:

  def __init__(self):
    self.to_move = PLAYER_BLACK
    self.board = [[0 for _ in range(5)] for _ in range(5)]
    self.game_status = CONTINUE
    self.previous_move = None
    self.serial = 1

  def __str__(self):
    ret = ""
    for row in self.board:
      for item in row:
        if item == PLAYER_WHITE:
          piece = "O "
        elif item == PLAYER_BLACK:
          piece = "* "
        else:
          piece = ". "
        #print(piece, end="")
        ret += piece
      ret += "\n"
    return ret
  
  def opponent(self, player):
    if player == PLAYER_BLACK:
      return PLAYER_WHITE
    if player == PLAYER_WHITE:
      return PLAYER_BLACK
    raise Exception("internal error: bad player")

  def scratch_board(self):
    return [[False for _ in range(5)] for _ in range(5)]

  def flood(self, scratch, color, x, y):
    if not (x >= 0 and x <= 4 and y >= 0 and y <= 4):
      return
    if scratch[x][y]:
      return
    if self.board[x][y] != color:
      return 
    scratch[x][y] = True
    self.flood(scratch, color, x - 1, y)
    self.flood(scratch, color, x + 1, y)
    self.flood(scratch, color, x, y - 1)
    self.flood(scratch, color, x, y + 1)

  def group_border(self, scratch, x, y):
    if scratch[x][y]:
	    return False
    if x > 0 and scratch[x - 1][y]:
      return True
    if x < 4 and scratch[x + 1][y]:
      return True
    if y > 0 and scratch[x][y - 1]:
      return True
    if y < 4 and scratch[x][y + 1]:
      return True
    return False

  def liberties(self, x, y):
    scratch = self.scratch_board()
    self.flood(scratch, self.board[x][y], x, y)
    n = 0
    for i in range(5):
      for j in range(5):
        if self.board[i][j] == 0 and self.group_border(scratch, i, j):
          n += 1
    return n

  def move_ok(self, move):
    """
    Check whether a move is valid based on current board.
    :return: a tuple (boolean, integer)
             1st element indicates whether move is valid
             2nd element indicates the number of liberties 
             if it is valid and not pass; otherwise it is -1
             or 0.
    """
    if move.is_pass:
      return (True, -1)
    if self.board[move.x][move.y] != 0:
      return (False, -1)
    self.board[move.x][move.y] = self.to_move    
    n = self.liberties(move.x, move.y)
    self.board[move.x][move.y] = 0
    if n == 0:
      return (False, n)
    return (True, n)
    
  def gen_moves(self):
    """
    Generate all possible moves and store them into a list named 
    result. Each element of result is a tuple (move, nliberties)
    :return: a list of tuple
    """
    result = []
    for i in range(5):
      for j in range(5):
        if self.board[i][j] == 0:
          m = Move(i, j)
          is_valid, nlib = self.move_ok(m)
          if is_valid:
            result.append((m, nlib))
    return result

  def has_moves(self):
    ms = self.gen_moves()
    if ms:
      return True
    return False
    
  def capture(self, x, y):
    """
    Attempt to capture opponent stones.
    :return: a set of stone coords captured
    """
    if self.liberties(x, y) > 0:
      return set() 
    captured = set()
    scratch = self.scratch_board()
    self.flood(scratch, self.board[x][y], x, y)
    for i in range(5):
      for j in range(5):
        if scratch[i][j]:
          self.board[i][j] = self.to_move
          captured.add((x, y))
    return captured

  def do_captures(self, move):
    """
    Captures opponent stones based on move argument
    :return: a set of stone coords captured
    """
    captured = set()
    if move.x > 0 and self.board[move.x - 1][move.y] == self.opponent(self.to_move):
      captured |= self.capture(move.x - 1, move.y)
    if move.x < 4 and self.board[move.x + 1][move.y] == self.opponent(self.to_move):
      captured |= self.capture(move.x + 1, move.y)
    if move.y > 0 and self.board[move.x][move.y - 1] == self.opponent(self.to_move):
      captured |= self.capture(move.x, move.y - 1)
    if move.y < 4 and self.board[move.x][move.y + 1] == self.opponent(self.to_move):
      captured |= self.capture(move.x, move.y + 1)
    return captured

  def make_move(self, move):
    """
    Make a move on the current board based on the argument move,
    and do captures
    :param move: a Move object
    :return: a set of stone coords captured
    """
    self.previous_move = move
    if move.is_pass:
      return 
    self.board[move.x][move.y] = self.to_move
    captured = self.do_captures(move)
    if (move.x, move.y) in captured:
      captured.remove((move.x, move.y))
    return captured

  def try_move(self, move, debug=False):
    """
    Try move based on argument move.
    :return: a flag indicates whether game should continue,
             and a set of stone coords captured if any
    """
    if debug:
      print("entering try_move()")

    if self.game_status != CONTINUE:
      if debug:
        print("leaving try_move(): move after game over")
      return ILLEGAL_MOVE, None
    if move.is_pass and self.previous_move and self.previous_move.is_pass:
      self.game_status = GAME_OVER
      if debug:
        print("leaving try_move(): game over")
      return GAME_OVER, None
    if not self.move_ok(move)[0]:
      if debug:
        print("leaving try_move(): illegal move")
      return ILLEGAL_MOVE, None
    if debug:
      print("move ok")

    captured = self.make_move(move)

    self.to_move = self.opponent(self.to_move)
    if self.to_move == PLAYER_BLACK:
      self.serial += 1
    
    if debug:
      print("leaving try_move(): continue game")
    return CONTINUE, captured

  def referee(self):
    #if self.game_status != GAME_OVER:
    #  raise Exception("internal error: referee unfinished game")
    
    nblack, nwhite = 0, 0
    for i in range(5):
      for j in range(5):
        if self.board[i][j] == PLAYER_BLACK:
          nblack += 1
        elif self.board[i][j] == PLAYER_WHITE:
          nwhite += 1
    
    if nblack > nwhite:
      return PLAYER_BLACK
    if nwhite > nblack:
      return PLAYER_WHITE
    return OBSERVER
