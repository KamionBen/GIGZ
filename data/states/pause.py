import pygame as pg
from .. import tools, prepare


class Pause(tools.State):
    def __init__(self):
        tools.State.__init__(self)
        self.next = 'game'

        self.base_font = prepare.FONTS['Biometric Joe'][56]
        self.small_font = prepare.FONTS['Biometric Joe'][32]

    def update(self):
        self.draw(prepare.SCREEN)

    def draw(self, screen):
        screen.blit(prepare.IMAGES['menu_bg.png'], (0, 0))
        center_x = prepare.RESOLUTION[0] / 2
        pause_txt = self.base_font.render("Pause", True, 'white')
        screen.blit(pause_txt, (center_x - pause_txt.get_width() / 2, 50))

        # Player screens
        for player in tools.State.players:
            p_screen = pg.Surface((800, 800), pg.SRCALPHA, 32)
            p_screen.fill((0, 0, 0, 64))
            name_txt = self.base_font.render(player.name, True, 'white')
            p_screen.blit(name_txt, (400 - name_txt.get_width() / 2, 20))

            screen.blit(p_screen, (prepare.RESOLUTION[0] / (len(tools.State.players) + 1) - 400, 200))

    def get_event(self, event):
        if event.type == pg.JOYBUTTONDOWN:
            if event.button == 6:  # Options button
                self.done = True
