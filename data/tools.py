import os
import csv
import pygame as pg
import pygame.time
from . import weapons
import json

# Controller data
ps4controller_map = {'button': {"cross": 0, "circle": 1, "square": 2, "triangle": 3,
                                "share": 4, "PS": 5, "options": 6,
                                "L3": 7, "R3": 8, "L1": 9, "R1": 10,
                                "up": 11, "down": 12, "left": 13, "right": 14,
                                "touchpad": 15},
                     'analog': {"leftstick": [0, 1], "rightstick": [2, 3],
                                "lefttrigger": 4, "righttrigger": 5}}


def create_grid(grid_size=(2000, 2000), tile_size=32, bg_color=(0,0,0,0), fg_color='black', thickness=1):
    """ Return a pygame Surface with a grid texture """
    width, height = grid_size[0], grid_size[1]

    grid = pygame.surface.Surface([width, height], pg.SRCALPHA, 32)
    grid.fill(bg_color)

    for y in range(int(height // tile_size)):
        pygame.draw.line(grid, fg_color, [0, y * tile_size], [width, y * tile_size], thickness)

    for x in range(int(width // tile_size)):
        pygame.draw.line(grid, fg_color, [x * tile_size, 0], [x * tile_size, height], thickness)

    return grid


def load_all_fonts(directory, accept=(".otf", ".ttf")):
    """ Create a dict per font with multiple sizes already imported """
    """ usage : fonts['Biometetric Joe'][28].render() """
    fonts = {}
    for font in os.listdir(directory):
        name, ext = os.path.splitext(font)
        if ext.lower() in accept:
            fonts[name] = {size: pg.font.Font(os.path.join(directory, font), size) for size in range(2, 66, 2)}
    return fonts


def load_all_images(directory, accept=(".png", ".jpg", ".bmp")):
    """ Load all graphics in a directory and his subdirs with extensions in the accept argument. """
    graphics = {}
    for (imgdir, subdir, files) in os.walk(directory):
        for pic in files:
            name, ext = os.path.splitext(pic)
            if ext.lower() in accept:
                img = pygame.image.load(os.path.join(imgdir, pic))
                if img.get_alpha():
                    img = img.convert_alpha()
                else:
                    img = img.convert()
                graphics[name+ext] = img
    return graphics


def load_json(file):
    with open(file, 'r') as file:
        data = json.load(file)
    return data


def scale_ratio(image, ratio):
    """ Return the image scaled to the given ratio """
    width, height = image.get_width(), image.get_height()
    return pg.transform.scale(image, (width * ratio, height * ratio))


def update_joysticks(init=True):
    """ Return a list of all the connected joysticks """
    joysticks = []
    for i in range(pygame.joystick.get_count()):
        joy = pygame.joystick.Joystick(i)
        if init:
            joy.init()
        joysticks.append(joy)

    return joysticks


def get_gear_list(csv_file):
    gear_list = []
    with open(csv_file, 'r') as file:
        line_list = csv.reader(file, delimiter=';')
        for i, row in enumerate(line_list):
            if i > 0:
                name = row[0]
                effect = row[1]
                slot = row[2]
                gear_list.append(weapons.Gear(name, effect, slot))
    return gear_list


def get_weapon_list(csv_file):
    weapon_list = []
    with open(csv_file, 'r') as file:
        line_list = csv.reader(file, delimiter=';')
        for i, row in enumerate(line_list):
            if i > 0:

                name = row[0]
                category = row[1]
                cadence = row[2]
                sprite = row[3]
                if row[4] == 'None':
                    img = None
                else:
                    img = row[4]
                damages = int(row[5])
                shooting_speed = int(row[6])
                magazine = int(row[7])
                reload_time = int(row[8])
                if row[9] == 'None':
                    slots = None
                else:
                    slots = [i for i in row[9].split(',')]
                if row[10] == 'True':
                    distance = True
                else:
                    distance = False
                meleeattack = int(row[11])
                weapon_list.append(weapons.Weapon(name, category, cadence, sprite, img, damages, shooting_speed, magazine,
                                          reload_time, slots, distance, meleeattack))

    return weapon_list


class Options:
    def __init__(self, **options):
        self.names = []
        self.options = []
        for name, option in options.items():
            self.names.append(name)
            self.options.append(option)

        self.cursor = 0  # The option that is currently selected
        self.parameter = [0 for _ in range(len(self))]  # For each parameter, a new selector is created

    def __getitem__(self, item):
        if item not in self.names:
            raise KeyError(f"Key '{item}' not found")
        else:
            ind = self.names.index(item)
            return self.options[ind][self.parameter[ind]]

    def is_selected(self, name):
        return name == self.names[self.cursor]

    def change_cursor(self, incr, loop=True):
        """ Change the selected option """
        self.cursor += incr
        if self.cursor < 0:
            if loop:
                self.cursor = len(self) - 1
            else:
                self.cursor = 0
        if self.cursor >= len(self):
            if loop:
                self.cursor = 0
            else:
                self.cursor = len(self) - 1

    def change_parameter(self, incr, cursor=None, loop=True):
        """ Change the parameter of the currently selected option """
        if cursor is None:
            cursor = self.cursor
        self.parameter[cursor] += incr
        if self.parameter[cursor] < 0:
            if loop:
                self.parameter[cursor] = len(self.options[cursor]) - 1
            else:
                self.parameter[cursor] = 0
        if self.parameter[cursor] >= len(self.options[cursor]):
            if loop:
                self.parameter[cursor] = 0
            else:
                self.parameter[cursor] = len(self.options[cursor]) - 1

    def items(self):
        for i, name in enumerate(self.names):
            current_parameter = self.parameter[i]
            parameter = self.options[i][current_parameter]
            yield name, parameter

    def __len__(self):
        return len(self.names)

    def __iter__(self):
        return iter(self.names)


class State:
    players = []
    joysticks = []
    level = None
    trigger_list = []  # Handle custom events

    def __init__(self):
        self.done = False
        self.next = None
        self.quit = False
        self.previous = None

    def draw(self, screen):
        pass

    def startup(self):
        pass

    def cleanup(self):
        pass

    def get_event(self, event):
        pass


class Trigger:
    def __init__(self, genre, **kwargs):
        self.genre = genre
        self.dict = {key: value for key, value in kwargs.items()}

    def __getitem__(self, item):
        return self.dict[item]

class Projection(pg.sprite.Sprite):
    def __init__(self, position, radius, offset):
        """ A throwaway class to check for collision """
        pg.sprite.Sprite.__init__(self)
        self.position = position

        self.image = pg.Surface((radius * 2, radius * 2), pg.SRCALPHA, 32)
        pg.draw.circle(self.image, 'white', (radius, radius), radius)
        self.rect = self.image.get_rect()
        self.rect.center = position + offset
        self.mask = pg.mask.from_surface(self.image)

    def update(self, position, offset):
        self.position = position
        self.rect.center = position + offset
