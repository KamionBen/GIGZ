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
                weapon_list.append(weapons.Weapon(name, category, cadence, sprite, img, damages, shooting_speed, magazine,
                                          reload_time, slots, distance))

    return weapon_list


class Options:
    def __init__(self, names=(), options=()):
        self.names = names
        self.options = options

    def __len__(self):
        return len(self.names)

    def __iter__(self):
        return iter(self.names)

    def __getitem__(self, index):
        return self.options[index]

    def select_option(self, index, direction):
        if direction == 1:
            _temp = self.options[index].pop(0)
            self.options[index].append(_temp)
        if direction == -1:
            _temp = self.options[index].pop(-1)
            self.options[index].insert(0, _temp)


class State:
    def __init__(self):
        self.done = False
        self.next = None
        self.quit = False
        self.previous = None

        self.options = {}
        self.selected_index = 0

        self.players = []
        self.joysticks = []

    def startup(self):
        pass

    def cleanup(self):
        pass

    def get_event(self, event):
        pass

    def change_selected_option(self, op=None):
        if op is not None:
            self.selected_index += op
            if self.selected_index < 0:
                self.selected_index = len(self.options) -1
            if self.selected_index >= len(self.options):
                self.selected_index = 0







