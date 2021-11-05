import pygame
import os
import config


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, row, col, file_name, transparent_color=None):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (config.TILE_SIZE, config.TILE_SIZE))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (col * config.TILE_SIZE, row * config.TILE_SIZE)
        self.row = row
        self.col = col


class Agent(BaseSprite):
    def __init__(self, row, col, file_name):
        super(Agent, self).__init__(row, col, file_name, config.DARK_GREEN)

    def move_towards(self, row, col):
        row = row - self.row
        col = col - self.col
        self.rect.x += col
        self.rect.y += row

    def place_to(self, row, col):
        self.row = row
        self.col = col
        self.rect.x = col * config.TILE_SIZE
        self.rect.y = row * config.TILE_SIZE

    # game_map - list of lists of elements of type Tile
    # goal - (row, col)
    # return value - list of elements of type Tile
    def get_agent_path(self, game_map, goal):
        pass


class ExampleAgent(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        path = [game_map[self.row][self.col]]

        row = self.row
        col = self.col
        while True:
            if row != goal[0]:
                row = row + 1 if row < goal[0] else row - 1
            elif col != goal[1]:
                col = col + 1 if col < goal[1] else col - 1
            else:
                break
            path.append(game_map[row][col])
        return path


class Tile(BaseSprite):
    def __init__(self, row, col, file_name):
        super(Tile, self).__init__(row, col, file_name)

    def position(self):
        return self.row, self.col

    def cost(self):
        pass

    def kind(self):
        pass


class Stone(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'stone.png')

    def cost(self):
        return 1000

    def kind(self):
        return 's'


class Water(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'water.png')

    def cost(self):
        return 500

    def kind(self):
        return 'w'


class Road(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'road.png')

    def cost(self):
        return 2

    def kind(self):
        return 'r'


class Grass(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'grass.png')

    def cost(self):
        return 3

    def kind(self):
        return 'g'


class Mud(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'mud.png')

    def cost(self):
        return 5

    def kind(self):
        return 'm'


class Dune(Tile):
    def __init__(self, row, col):
        super().__init__(row, col, 'dune.png')

    def cost(self):
        return 7

    def kind(self):
        return 's'


class Goal(BaseSprite):
    def __init__(self, row, col):
        super().__init__(row, col, 'x.png', config.DARK_GREEN)


class Trail(BaseSprite):
    def __init__(self, row, col, num):
        super().__init__(row, col, 'trail.png', config.DARK_GREEN)
        self.num = num

    def draw(self, screen):
        text = config.GAME_FONT.render(f'{self.num}', True, config.WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


# Custom util classes

# Custom agents

class Assistant(Agent):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_options(self, node, game_map):
        """

        :param node: current position of agent
        :param game_map: game map
        :return: list of options and index of first None element
        """
        options = [None] * 4

        row, col = node.position()

        # go north
        if row > 0:
            options[0] = (game_map[row - 1][col])

        # go east
        if col < len(game_map[row]) - 1:
            options[1] = (game_map[row][col + 1])

        # go south
        if row < len(game_map) - 1:
            options[2] = (game_map[row + 1][col])

        # go west
        if col > 0:
            options[3] = (game_map[row][col - 1])

        # move all None values to end of array
        # and prepare for quicksort
        cnt = 0
        high = len(options) - 1
        for i in range(len(options)):
            if options[i] is not None:
                options[cnt] = options[i]
                cnt += 1

        high = cnt

        while cnt < len(options):
            options[cnt] = None
            cnt += 1

        return options, high

    def partition(self, arr, low, high):
        """

        :param arr: array that is used to find pivot point
        :param low: index of fist element
        :param high: index of last element
        :return: pivot index
        """
        i = (low - 1)
        pivot = arr[high].cost()

        for j in range(low, high):
            if arr[j].cost() <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]

        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1

    def quicksort(self, arr, low, high):
        """

        :param arr: array that is being sorted (by tile)
        :param low: index of fist element
        :param high: index of last element
        :return: sorted array
        """
        if len(arr) == 1:
            return arr

        if low < high:
            pi = self.partition(arr, low, high)

            self.quicksort(arr, low, pi - 1)
            self.quicksort(arr, pi + 1, high)
            return arr

    def sort_priorities(self, arr: list[Tile], low, high, node):
        """

        :param arr: array that is being sorted (by direction)
        :param low: index of fist element
        :param high: index of last element
        :param node: current location of agent
        :return: sorted array
        """
        i = low
        while i <= high and arr[low].cost() == arr[i].cost():
            i += 1

        if i == low:
            return

        for p in range(low, i - 1):
            for q in range(p + 1, i):
                if Assistant.priority(arr[p], node) < Assistant.priority(arr[q], node):
                    arr[p], arr[q] = arr[q], arr[p]

        self.sort_priorities(arr, i, high, node)
        return

    @staticmethod
    def priority(tile: Tile, node: Tile) -> int:
        """

        :param tile: tile to check
        :param node: current tile of agent
        :return: priority
        """
        if node.row - 1 == tile.row:
            return 3  # north
        elif node.col + 1 == tile.col:
            return 2  # east
        elif node.row + 1 == tile.row:
            return 1  # south
        elif node.col - 1 == tile.col:
            return 0  # west
        else:
            raise Exception('Invalid tile provided')


class Aki(Assistant):
    def __init__(self, row, col, file_name):
        super().__init__(row, col, file_name)

    def get_agent_path(self, game_map, goal):
        visited = set()
        goal_tile = game_map[goal[0]][goal[1]]
        start_tile = game_map[self.row][self.col]

        return self.dfs(visited, game_map, start_tile, goal_tile)

    def dfs(self, visited, game_map, node, goal):
        path = []
        if node not in visited and node is not None:
            visited.add(node)
            path.append(node)
            if node == goal:
                return path
            else:
                opt, index = self.get_options(node, game_map)
                # sort direction weight
                opt = self.quicksort(opt, 0, index - 1)

                self.sort_priorities(opt, 0, index - 1, node)

                for neighbour in opt:
                    tmp = self.dfs(visited, game_map, neighbour, goal)
                    if (len(tmp) > 0) and (goal in tmp):
                        for i in tmp:
                            path.append(i)
                        break

        return path
