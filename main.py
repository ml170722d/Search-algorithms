import sys, re
import traceback
import pygame

from game import Game

try:
    pygame.init()
    g = Game()

    print()
    print('--', end='')
    print('-' * 5 * len(g.tile_map[0]))
    for row in g.tile_map:
        print('| ', end='')
        for tile in row:
            print("{:<5}".format(tile.cost()), end='')
        print('|')
    print('-', end='')
    print('-' * 5 * len(g.tile_map[0]))

    g.run()
except (Exception,):
    traceback.print_exc()
    input()
finally:
    # map_arg = re.compile('.*(map\\d).txt').match(sys.argv[1]).group(1)
    # agent_arg = sys.argv[2]
    # pygame.image.save(g.screen.copy(), "./solutions/{agent}-{map}.png".format(agent=agent_arg, map=map_arg))
    pygame.quit()
