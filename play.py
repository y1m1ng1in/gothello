#!/usr/bin/python3

import time
import copy

from game import Gothelo
from board import PLAYER_WHITE, PLAYER_BLACK
from gthclient import GthClient
from minimax import Minimax

class Game:

  def __init__(self, side, method, times=3):
    self.side = side
    self.method = method
    self.times = times
    self.black_win = 0
    self.white_win = 0

  def play(self):
    for i in range(self.times):
      print("\n\ngame", i+1, "\n\n")

      client = GthClient(self.side, "barton.cs.pdx.edu", 0)
      method = copy.deepcopy(self.method)
      game = Gothelo(method, client, side=self.side)

      game.play()
      if client.winner == "black":
        self.black_win += 1
      elif client.winner == "white":
        self.white_win += 1

      client.closeall()
      time.sleep(1)

  def stats(self):
    print("\n\n")
    print("black win rate:", self.black_win / self.times)
    print("white win rate:", self.white_win / self.times)


def main():
  scoring = {
              'stone': 0,
              'black connection': 1,
              'white connection': 1,
              'black eye': 6,
              'white eye': 3
            }

  auto_adjust_scoring = {
                          'stone': 10,
                          'black connection': 0,
                          'white connection': 0,
                          'black eye': 0,
                          'white eye': 0,
                          'serial': 7
                        }

  method = Minimax("black",
                   depth=3,
                   prune=True, 
                   move_ordering=True,
                   selective_search=True,
                   eval_method="connected eye",
                   scoring=scoring,
                   dynamic_eval=True,
                   auto_adjust_scoring=auto_adjust_scoring,
                   iter_deepening=True, 
                   max_visited=3000)

  g = Game("black", method)
  g.play()
  g.stats()


if __name__ == "__main__":
  main()