import sys
import pygame as pg
from pygame.locals import *
from . import prepare
from .states import menu, game


class Control:
    def __init__(self):
        # Init
        self.done = False

        # States
        self.state_dict, self.state_name, self.state = None, None, None

    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

    def main_game_loop(self):
        while not self.done:
            self.event_loop()
            self.update()
            pg.display.flip()

    def event_loop(self):
        for event in pg.event.get():
            if event.type == QUIT:
                self.done = True
            self.state.get_event(event)

    def update(self):
        self.state.update()
        if self.state.done:
            self.flip_state()

    def flip_state(self):
        self.state.done = False
        previous, self.state_name = self.state_name, self.state.next
        self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup()
        self.state.previous = previous
