import pygame as pg
from pygame.locals import *
import os
from . import tools

VERSION = '0.2.0'
CAPTION = "GIGZ"
RESOLUTION = 1920, 1080
FPS = 60
RATIO = 540 / RESOLUTION[1]


# initialization
pg.init()
pg.event.set_allowed([QUIT, JOYAXISMOTION, JOYDEVICEREMOVED, JOYBUTTONDOWN, JOYBUTTONUP, JOYDEVICEADDED])
SCREEN = pg.display.set_mode(RESOLUTION)
SCREEN_RECT = SCREEN.get_rect()
CLOCK = pg.time.Clock()

# loading resources
FONTS = tools.load_all_fonts(os.path.join('resources', 'fonts'))
IMAGES = tools.load_all_images(os.path.join('resources', 'images'))

WEAPONS = tools.get_weapon_list(os.path.join('data', 'items', 'weapons.csv'))
GEARS = tools.get_gear_list(os.path.join('data', 'items', 'gears.csv'))

SURVIVOR_SPRITESET = tools.load_json(os.path.join('data', 'spritesets', 'character.json'))
ZOMBIE_SPRITESET = tools.load_json(os.path.join('data', 'spritesets', 'zombie.json'))

for weapon, w_dict in SURVIVOR_SPRITESET.items():
    for status, s_dict in w_dict.items():
        for img in s_dict['files']:
            IMAGES[img] = tools.scale_ratio(IMAGES[img], RATIO)

for status, s_dict in ZOMBIE_SPRITESET.items():
    for img in s_dict['files']:
        IMAGES[img] = tools.scale_ratio(IMAGES[img], RATIO)



