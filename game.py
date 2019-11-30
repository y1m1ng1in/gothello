#!/usr/bin/python3

import random

import gthclient

from board import Board, Move, ILLEGAL_MOVE, CONTINUE, GAME_OVER
from minimax import Minimax

class Gothelo:

  def __init__(self, method, client, side="black"):
    self.board = method
    self.client = client
    self.side = side
    
  def play(self):
    print("*** game start ***\n" + str(self.board))
    while(True):
      if self.side == "black":
        self.__make_my_move()
        print(self.board)
        if self.__get_move():
          break
        print(self.board)
      elif self.side == "white":
        if self.__get_move():
          break
        print(self.board)
        self.__make_my_move()
        print(self.board)
      else:
        raise Exception("error side")

  def __make_my_move(self):
    move = self.board.decision()
    if not move:
      move = Move(0, 0, is_pass=True)
    result = self.board.try_move(move)
    if result == ILLEGAL_MOVE:
      raise Exception("illegal move")
    
    print("me: ", move)

    try:
      if move.is_pass:
        self.client.make_move("pass")
      else:
        self.client.make_move(str(move))
    except gthclient.MoveError as e:
      if e.cause == e.ILLEGAL:
        print("me: made illegal move, passing")
        self.client.make_move("pass")

  def __get_move(self):
    cont, move = self.client.get_move()
    print("opp: ", move)

    if not cont:
      print("winner: ", self.client.winner)
      return True

    move = Move.parse_string(move)
    result = self.board.try_move(move)
    if result == ILLEGAL_MOVE:
      raise Exception("illegal move when receiving from server")
    if result == GAME_OVER:
      raise Exception("Game over when receiving from server")

    return False


client = client = gthclient.GthClient("black", "barton.cs.pdx.edu", 0)

method = Minimax(depth=6, prune=True)

game = Gothelo(method, client, side="black")
game.play()