import pygame as pg
from . import tools


class PlayerProfile:
    pid = 0

    def __init__(self, name=None):
        """ The living player, the one with a controller in his hands """
        PlayerProfile.pid += 1
        if name is None:
            self.name = f"Player {PlayerProfile.pid}"
        else:
            self.name = name

        self.options = tools.Options(Vibrations=[True, False],
                                     Color=[(23, 82, 153), (16, 129, 13), (141, 0, 22)])

        self.buttons = {'touchpad': False,
                        'options': False}

        # Settings
        self.vibration = None
        self.color = None

        self.controller_guid = None
        self.survivor = None

        # Stats
        self.kills = 0
        self.ff_count = 0  # Friendly fire damages
        self.precision = [0, 0]

    def reinit_buttons(self):
        self.buttons = {'touchpad': False,
                        'options': False}

    def update_options(self):
        self.vibration = self.options['Vibrations']
        self.color = self.options['Color']

    def set_name(self, new_name):
        self.name = new_name

    def set_survivor(self, new_survivor):
        self.survivor = new_survivor

    def set_vibration(self, i):
        self.vibration = self.options['Vibrations']

    def set_color(self, value):
        self.color = value

    def set_controller(self, value):
        self.controller_guid = value

    def get_event(self, event):
        if event.type == pg.JOYBUTTONDOWN:
            if event.button == 6:  # PS4 options button
                self.buttons['options'] = self.buttons['options'] is False  # Switches buttons states
            if event.button == 15:  # PS4 touchpad button
                self.buttons['touchpad'] = self.buttons['touchpad'] is False  # Switches buttons states

