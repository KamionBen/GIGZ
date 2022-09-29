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
        self.main_screen = pg.Surface((1920, 1080), SRCALPHA, 32).convert_alpha()
        self.true_size = prepare.RESOLUTION == (1920, 1080)

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

    def draw(self):
        prepare.SCREEN.fill('black')
        if self.true_size is False:
            game_screen = pg.transform.scale(self.main_screen, prepare.RESOLUTION)
        else:
            game_screen = self.main_screen
        prepare.SCREEN.blit(game_screen, (0, 0))

    def update(self):
        self.state.update()
        self.state.draw(self.main_screen)
        self.draw()
        if self.state.done:
            self.flip_state()

    def flip_state(self):
        self.state.done = False
        previous, self.state_name = self.state_name, self.state.next
        self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup()
        self.state.previous = previous
