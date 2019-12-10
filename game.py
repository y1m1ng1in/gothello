#!/usr/bin/python3

import random
import argparse

import gthclient

from board import Board, Move, ILLEGAL_MOVE, CONTINUE, GAME_OVER
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
      except gthclient.ProtocolError as e:
        # python library doesn't handle game draw, so manually 
        # handle it here
        if e.expression == 325 or e.expression == 326:
          print("game drawn")
          break

  def __make_my_move(self):
    if self.client.winner:
      print("winner: ", self.client.winner)
      return True

    move = self.board.decision()
    if not move:
      move = Move(0, 0, is_pass=True)
    result, _ = self.board.try_move(move)
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
    except gthclient.ProtocolError as e:
      # python library doesn't handle game draw, so manually 
      # handle it here
      if e.expression == 325 or e.expression == 326:
        print("game drawn")
        return True

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
    result, _ = self.board.try_move(move)
    if result == ILLEGAL_MOVE:
      raise Exception("illegal move when receiving from server")
    if result == GAME_OVER:
      raise Exception("Game over when receiving from server")

    return False


def main():
  sides = [
    "black",
    "white"
  ]

  eval_methods = [
    "number",
    "eye"
  ]

  parser = argparse.ArgumentParser(description='gothello')

  parser.add_argument('--side',  
                      '-s',
                      type=str,
                      choices=sides, 
                      default=sides[0], 
                      help="choose a side to play")

  parser.add_argument('--depth',
                      '-d',
                      type=int,
                      default=4,
                      help="depth limitation for minimax search \
                            , not applied to iter deepening")

  parser.add_argument('--evaluate',
                      '-e',
                      type=str,
                      choices=eval_methods,
                      default=eval_methods[0],
                      help="choose a static evaluate function: (1)\
                            \"number\" counts number of stones on each side; (2)\
                            \"eye\" counts number of eyes and stones on each side")

  parser.add_argument('--stonescore',
                      '-S',
                      type=int,
                      default=1,
                      help="assign a score for stone")

  parser.add_argument('--blackeyescore',
                      '-b',
                      type=int,
                      default=1,
                      help="assign a score for black eye")

  parser.add_argument('--whiteeyescore',
                      '-w',
                      type=int,
                      default=1,
                      help="assign a score for white eye")

  parser.add_argument('--iterdeepening',
                      '-i',
                      action='store_true',
                      help="enable iterative deepening \
                            default maximum number of states \
                            to visit is 12000")

  parser.add_argument('--moveselection',
                      '-M',
                      action='store_true',
                      help="select move with the largest liberties \
                            when multiple moves with same evalutated\
                            score encountered")

  parser.add_argument('--maxnstate',
                      '-m',
                      type=int,
                      default=10000,
                      help="assign a number for maximum number \
                            of states to visit in iterative deepening")

  parser.add_argument('--stats',
                      action='store_true',
                      help="enable printing states info")

  args = parser.parse_args()

  side = args.side
  depth = args.depth
  eval_function = args.evaluate
  scoring = {
              'stone': args.stonescore,
              'black eye': args.blackeyescore,
              'white eye': args.whiteeyescore
            }
  iterdeepening = args.iterdeepening
  maximum_visit = args.maxnstate
  move_selection = args.moveselection
  print_stats = args.stats

  client = gthclient.GthClient(side, "localhost", 0)

  method = AlphaBetaPruning(side,
                            depth=depth,
                            iterdeepening=iterdeepening,
                            maximum_visited=maximum_visit, 
                            eval_method=eval_function,
                            scoring=scoring,
                            move_selection=move_selection,
                            print_stats=print_stats)

  game = Gothelo(method, client, side=side)
  game.play()
  game.client.closeall()


if __name__ == "__main__":
  main()