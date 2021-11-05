import traceback
import pygame

from game import Game

try:
    pygame.init()
    g = Game()

    print()
    print('--', end='')
    print('-'*5*len(g.tile_map[0]))
    for row in g.tile_map:
        print('| ', end='')
        for tile in row:
            print("{:<5}".format(tile.cost()), end='')
        print('|')
    print('-', end='')
    print('-'*5*len(g.tile_map[0]))

    g.run()
except (Exception,):
    traceback.print_exc()
    input()
finally:
    pygame.quit()
