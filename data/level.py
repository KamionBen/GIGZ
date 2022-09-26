import os
import pygame as pg
from . import tools, prepare


class Wall(pg.sprite.Sprite):
    """ Basically just a grey Rect """
    def __init__(self, size, position):
        pg.sprite.Sprite.__init__(self)

        self.size = size
        self.position = position

        self.image = pg.Surface(size)
        self.image.fill('pink')
        self.rect = self.image.get_rect()
        self.rect.topleft = position


class Chunk(pg.sprite.Sprite):
    def __init__(self, coord):
        pg.sprite.Sprite.__init__(self)
        self.coord = coord  # ! Not in pixels
        self.position = pg.math.Vector2(coord[0] * 256, coord[1] * 256)

        self.image = pg.Surface((32 * 8, 32 * 8))
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.coord[0] * 256, self.coord[1] * 256)

        self.walls = pg.sprite.Group()

    def __repr__(self):
        return self.get_key()

    def get_key(self):
        return f"{self.coord[0]}.{self.coord[1]}"

    def blit(self, image, position):
        self.image.blit(image, position)


class Level:
    def __init__(self, name, difficulty, zombie_number, friendly_fire):

        # Settings
        self.name = name
        self.difficulty = difficulty
        self.zombie_number = zombie_number
        self.friendly_fire = friendly_fire

        # Images
        self.width, self.height = None, None
        self.rect = None
        self.chunks = {}

        # Walls
        self.walls = pg.sprite.Group()

        # Spawns
        self.survivors_spawns = []
        self.zombies_spawns = []

        self.parse_layout()

    def parse_layout(self):
        directory = os.path.join('resources', 'levels', self.name)
        layout = pg.image.load(os.path.join(directory, 'layout.png')).convert()
        poi = pg.image.load(os.path.join(directory, 'poi.png')).convert()

        self.width, self.height = 32 * layout.get_width(), 32 * layout.get_height()

        self.rect = pg.rect.Rect(0, 0, self.width, self.height)

        wall_color = (0, 0, 0, 255)
        s_spawn_color = (0, 255, 0, 255)
        z_spawn_color = (255, 0, 0, 255)

        road_color = (69, 69, 69, 255)

        for y in range(layout.get_height()):
            for x in range(layout.get_width()):
                # Points of interest
                if poi.get_at((x, y)) == s_spawn_color:
                    self.survivors_spawns.append((x * 32, y * 32))
                if poi.get_at((x, y)) == z_spawn_color:
                    self.zombies_spawns.append((x * 32, y * 32))

                coord = (int(x // 8), int(y // 8))
                key = f"{coord[0]}.{coord[1]}"
                if key not in self.chunks.keys():
                    self.chunks[key] = Chunk(coord)

                tile = pg.Surface((32, 32))
                pixel_color = layout.get_at((x, y))
                if pixel_color == road_color:
                    tile.blit(prepare.IMAGES['road.png'], (0, 0))
                else:
                    tile.fill(layout.get_at((x, y)))

                self.chunks[key].blit(tile, (x % 8 * 32, y % 8 * 32))

        # WALLS
        horizontal = {}
        vertical = {}
        solo = {}  # TODO : Check for non-connected walls

        tile = 32

        # Horizontal check
        for y in range(layout.get_height()):
            y_index = y * tile
            horizontal[y_index] = []
            for x in range(layout.get_width()):
                color = layout.get_at([x, y])
                # WALLS
                if color == wall_color:
                    current_rect = pg.Rect(x * tile, y * tile, tile + 1, tile + 1)
                    if len(horizontal[y_index]) == 0:
                        # Liste vide, on rajoute le premier qu'on trouve
                        horizontal[y_index].append(current_rect)
                    elif current_rect.colliderect(horizontal[y_index][-1]):
                        # Les rect sont contigus
                        horizontal[y_index][-1].width += tile
                    else:
                        # Les rect ne sont pas contigus
                        horizontal[y_index].append(current_rect)

        # Vertical check
        for x in range(layout.get_width()):
            x_index = x * tile
            vertical[x_index] = []
            for y in range(layout.get_height()):
                color = layout.get_at([x, y])
                if color == wall_color:
                    current_rect = pg.Rect(x * tile, y * tile, tile + 1, tile + 1)
                    if len(vertical[x_index]) == 0:
                        # Liste vide, on rajoute le premier qu'on trouve
                        vertical[x_index].append(current_rect)
                    elif current_rect.colliderect(vertical[x_index][-1]):
                        # Les rect sont contigus
                        vertical[x_index][-1].height += tile
                    else:
                        # Les rect ne sont pas contigus
                        vertical[x_index].append(current_rect)

        wall_rect_list = []  # TODO : Maybe not a necessary variable

        for y, rect_list in horizontal.items():
            for rect in rect_list:
                if rect.width > tile + 1:
                    wall_rect_list.append(rect)
        for x, rect_list in vertical.items():
            for rect in rect_list:
                if rect.height > tile + 1:
                    wall_rect_list.append(rect)

        for elt in wall_rect_list:
            self.walls.add(Wall([elt.width, elt.height], [elt.left, elt.top]))
