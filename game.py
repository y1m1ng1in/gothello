#!/usr/bin/python3

import random

import gthclient

from board import Board, Move, ILLEGAL_MOVE, CONTINUE, GAME_OVER
#from minimax import Minimax
from alphabetapruning import AlphaBetaPruning

class Gothelo:

  def __init__(self, method, client, side="black"):
    self.board = method
    self.client = client
    self.side = side
    
  def play(self):
    print("*** game start ***\n" + str(self.board))
    while(True):
      try:
        if self.side == "black":
          if self.__make_my_move():
            break
          print(self.board)
          if self.__get_move():
            break
          print(self.board)
        elif self.side == "white":
          if self.__get_move():
            break
          print(self.board)
          if self.__make_my_move():
            break
          print(self.board)
        else:
          raise Exception("error side")
      except gthclient.MoveError as e:
        # current python client library didn't offer a way to 
        # handle game drawn, thus manually print out result
        if e.cause == 3 and e.message == 'game terminated early':
          print("game drawn")
          break

  def __make_my_move(self):
    if self.client.winner:
      print("winner: ", self.client.winner)
      return True

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

    return False

  def __get_move(self):
    if self.client.winner:
      print("winner: ", self.client.winner)
      return False

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


def main():
  client = gthclient.GthClient("black", "localhost", 0)

  scoring = {
              'stone': 1,
              'black connection': 0,
              'white connection': 0,
              'black eye': 4,
              'white eye': 4
            }

  method = AlphaBetaPruning("black",
                            depth=4,
                            iterdeepening=True,
                            maximum_visited=4000, 
                            move_ordering=False,
                            selective_search=False,
                            eval_method="number",
                            scoring=scoring,
                            print_stats=True)

  game = Gothelo(method, client, side="black")
  game.play()
  game.client.closeall()


if __name__ == "__main__":
  main()