Gothello

```bash
usage: game.py [-h] [--side {black,white}] [--depth DEPTH]
               [--evaluate {number,eye}] [--stonescore STONESCORE]
               [--blackeyescore BLACKEYESCORE] [--whiteeyescore WHITEEYESCORE]
               [--iterdeepening] [--moveselection] [--maxnstate MAXNSTATE]
               [--stats]

gothello

optional arguments:
  -h, --help            show this help message and exit
  --side {black,white}, -s {black,white}
                        choose a side to play
  --depth DEPTH, -d DEPTH
                        depth limitation for minimax search , not applied to
                        iter deepening
  --evaluate {number,eye}, -e {number,eye}
                        choose a static evaluate function: (1) "number" counts
                        number of stones on each side; (2) "eye" counts number
                        of eyes and stones on each side
  --stonescore STONESCORE, -S STONESCORE
                        assign a score for stone
  --blackeyescore BLACKEYESCORE, -b BLACKEYESCORE
                        assign a score for black eye
  --whiteeyescore WHITEEYESCORE, -w WHITEEYESCORE
                        assign a score for white eye
  --iterdeepening, -i   enable iterative deepening default maximum number of
                        states to visit is 12000
  --moveselection, -M   select move with the largest liberties when multiple
                        moves with same evalutated score encountered
  --maxnstate MAXNSTATE, -m MAXNSTATE
                        assign a number for maximum number of states to visit
                        in iterative deepening
  --stats               enable printing states info
```