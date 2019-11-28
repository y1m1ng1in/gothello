#!/usr/bin/python3

# Random-move Gothello player.

import random

import gthclient
from board import Board, Move, ILLEGAL_MOVE, CONTINUE, GAME_OVER

client = gthclient.GthClient("black", "barton.cs.pdx.edu", 0)

b = Board()

while True:
  print(b)

  ms = b.gen_moves()
  if len(ms) == 0:
    move = Move(0, 0, is_pass=True)
  else:
    move = random.choice(ms)

  result = b.try_move(move)
  if result == ILLEGAL_MOVE:
    raise Exception("illegal move")
  
  print("me:", move)

  try:
    if move.is_pass:
      client.make_move("pass")
    else:
      client.make_move(str(move))
  except gthclient.MoveError as e:
    if e.cause == e.ILLEGAL:
      print("me: made illegal move, passing")
      client.make_move("pass")

  print(b)

  if client.winner:
    print("winner: ", client.winner)
    break

  cont, move = client.get_move()
  print("opp:", move)

  if not cont:
    print("winner: ", client.winner)
    break
  move = Move.parse_string(move)
  b.try_move(move)
  if result == ILLEGAL_MOVE:
    raise Exception("illegal move when receiving from server")
  if result == GAME_OVER:
    raise Exception("Game over when receiving from server")

