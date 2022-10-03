import pygame as pg
from .. import tools, prepare


class PauseMenu(tools.State):
    def __init__(self):
        """ Display the game options, settings, quit, etc ..."""
        tools.State.__init__(self)
        self.next = 'game'

        self.base_font = prepare.FONTS['Biometric Joe'][56]
        self.small_font = prepare.FONTS['Biometric Joe'][32]
        # TODO : Set the fonts global

        self.options = tools.Options(game=['Resume game'],
                                     mainmenu=['Return to main menu'])

        self.action = False

    def draw(self, screen):
        screen.fill((0, 0, 0, 128))  # TODO : Display game screen as background (or the GameMenu)
        center_x = 1920 / 2
        pause_txt = self.base_font.render("Pause", True, 'white')
        screen.blit(pause_txt, (center_x - pause_txt.get_width() / 2, 50))

        i = 0
        for name, option in self.options.items():
            if self.options.is_selected(name):
                brush = tools.scale_ratio(prepare.IMAGES['brush.png'], .3)
                screen.blit(brush, (center_x - brush.get_width() / 2, 400 + i * 60))
            txt = self.base_font.render(option, True, 'white')
            screen.blit(txt, (center_x - txt.get_width() / 2, 400 + i * 60))
            i += 1

    def update(self):
        if self.action:
            self.next = self.options.selected()
            self.done = True
            # TODO : Return to main menu doesn't work yet

    def get_event(self, event):
        if event.type == pg.JOYBUTTONDOWN:
            buttons = tools.ps4controller_map['button']
            # Options selection
            if event.button == buttons['up']:
                self.options.change_cursor(-1)
            if event.button == buttons['down']:
                self.options.change_cursor(1)
            if event.button == buttons['cross']:
                self.action = True

    def startup(self):
        for s_player in tools.State.players:
            s_player.reinit_buttons()

    def cleanup(self):
        for s_player in tools.State.players:
            s_player.reinit_buttons()
        self.action = False


class GameMenu(tools.State):
    def __init__(self):
        """ Display the survivors options, choosing weapons etc ..."""
        tools.State.__init__(self)
        self.next = 'game'

        self.base_font = prepare.FONTS['Biometric Joe'][56]
        self.small_font = prepare.FONTS['Biometric Joe'][32]

        self.ready = [False for _ in tools.State.players]

    def update(self):
        if all(self.ready):
            self.done = True

    def draw(self, screen):
        self._draw_header(screen)
        self._draw_players(screen)

    def _draw_header(self, screen):
        screen.blit(prepare.IMAGES['menu_bg.png'], (0, 0))
        center_x = 1920 / 2
        pause_txt = self.base_font.render("Pause", True, 'white')
        screen.blit(pause_txt, (center_x - pause_txt.get_width() / 2, 50))

    def _draw_players(self, screen):
        # Player screens
        for i, player in enumerate(tools.State.players):
            p_screen = pg.Surface((800, 800), pg.SRCALPHA, 32)
            p_screen.fill((0, 0, 0, 64))
            name_txt = self.base_font.render(player.name, True, 'white')
            p_screen.blit(name_txt, (400 - name_txt.get_width() / 2, 20))
            pg.draw.rect(p_screen, 'white', (0,0, 800, 800), 1)

            # TODO : Replace players rect correctly
            screen.blit(p_screen, (1920 / (len(tools.State.players) + 1) - 400 + i * 800, 200))

    def get_event(self, event):
        if event.type == pg.JOYBUTTONDOWN:
            if event.button == 15:  # Touchpad button
                self.ready[event.joy] = True

    def startup(self):
        for s_player in tools.State.players:
            s_player.reinit_buttons()

    def cleanup(self):
        for s_player in tools.State.players:
            s_player.reinit_buttons()
        self.ready = [False for _ in tools.State.players]
