import os
import pygame as pg
from . import tools, prepare
from random import choice


wall_colors = ['pink', 'red', 'green', 'blue', 'grey50', 'purple']

class Wall(pg.sprite.Sprite):
    """ Basically just a grey Rect """
    def __init__(self, pos_x, pos_y, size_x, size_y):
        pg.sprite.Sprite.__init__(self)
        self.position = pos_x, pos_y

        self.image = pg.Surface((size_x, size_y))
        self.image.fill(choice(wall_colors))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos_x, pos_y


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
        tile_size = 32
        chunk_size = 8
        directory = os.path.join('resources', 'levels', self.name)
        layout = pg.image.load(os.path.join(directory, 'layout.png')).convert()
        poi = pg.image.load(os.path.join(directory, 'poi.png')).convert()

        self.width, self.height = tile_size * layout.get_width(), tile_size * layout.get_height()

        self.rect = pg.rect.Rect(0, 0, self.width, self.height)

        wall_color = (0, 0, 0, 255)
        s_spawn_color = (0, 255, 0, 255)
        z_spawn_color = (255, 0, 0, 255)

        road_color = (69, 69, 69, 255)

        for y in range(layout.get_height()):
            for x in range(layout.get_width()):
                # Points of interest
                if poi.get_at((x, y)) == s_spawn_color:
                    self.survivors_spawns.append((x * tile_size, y * tile_size))
                if poi.get_at((x, y)) == z_spawn_color:
                    self.zombies_spawns.append((x * tile_size, y * tile_size))

                # Chunk
                coord = (int(x // chunk_size), int(y // chunk_size))
                key = f"{coord[0]}.{coord[1]}"
                if key not in self.chunks.keys():
                    self.chunks[key] = Chunk(coord)

                # Blit
                tile = pg.Surface((tile_size, tile_size))
                pixel_color = layout.get_at((x, y))
                if pixel_color == road_color:
                    tile.blit(prepare.IMAGES['road.png'], (0, 0))
                else:
                    tile.fill(layout.get_at((x, y)))

                self.chunks[key].blit(tile, (x % chunk_size * tile_size, y % chunk_size * tile_size))

        for key, chunk in self.chunks.items():
            posx, posy = chunk.coord
            horizontal = {}
            vertical = {}
            solo = {}  # Useless for now
            for y in range(chunk_size):
                horizontal[y] = []
                for x in range(chunk_size):
                    current_rect = pg.Rect(posx * 256 + x * tile_size, posy * 256 + y * tile_size, tile_size + 1, tile_size + 1)
                    if chunk.image.get_at((x * tile_size, y * tile_size)) == (0, 0, 0, 255):
                        if len(horizontal[y]) == 0:
                            horizontal[y].append(current_rect)
                        elif current_rect.colliderect(horizontal[y][-1]):
                            horizontal[y][-1].width += tile_size
                        else:
                            horizontal[y].append(current_rect)
            for x in range(chunk_size):
                vertical[x] = []
                for y in range(chunk_size):
                    current_rect = pg.Rect(posx * 256 + x * tile_size, posy * 256 + y * tile_size, tile_size + 1, tile_size + 1)
                    if chunk.image.get_at((x * tile_size, y * tile_size)) == (0, 0, 0, 255):
                        if len(vertical[x]) == 0:
                            vertical[x].append(current_rect)
                        elif current_rect.colliderect(vertical[x][-1]):
                            vertical[x][-1].height += tile_size
                        else:
                            vertical[x].append(current_rect)

            for index, walllist in horizontal.items():
                for rect in walllist:
                    if rect.width > tile_size + 1:
                        chunk.walls.add(Wall(rect.x, rect.y, rect.width, rect.height))
            for walllist in vertical.values():
                for rect in walllist:
                    if rect.height > tile_size + 1:
                        chunk.walls.add(Wall(rect.x, rect.y, rect.width, rect.height))


