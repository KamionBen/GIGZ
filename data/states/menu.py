from time import time
import pygame as pg
from pygame.locals import *
from .. import tools, prepare, player, level


class MainMenu(tools.State):
    def __init__(self):
        tools.State.__init__(self)
        self.done = False
        self.next = 'game'

        # Joysticks

        self.joysticks = tools.update_joysticks()
        self.rumble = [joy.rumble(.1, 0, 1) for joy in self.joysticks]
        self.ready = [False for _ in self.joysticks]

        # Players
        self.players = [player.PlayerProfile() for _ in self.joysticks]
        self.player_options = prepare.player_options
        # TODO : Separate ready controllers

        # Level
        self.options = prepare.level_options

        self.timer = None

        self.menu_screen = None
        self._update_menu_screen()

    def update(self):
        self.draw(prepare.SCREEN)
        if all(self.ready) and len(self.ready) > 0:
            if self.timer is None:
                self.timer = time()
            elif time() - self.timer >= 3:  # 3 seconds
                self.done = True
                if len(self.joysticks) == 1:
                    self.player_options[1] = None
        elif self.timer is not None:
            self.timer = None
        self._update_menu_screen()

    def _update_menu_screen(self):
        # Sugar
        blood_red = (183, 15, 15)
        grass_green = (39, 148, 15)
        base_font = prepare.FONTS['Biometric Joe'][56]
        small_font = prepare.FONTS['Biometric Joe'][32]
        center = prepare.RESOLUTION[0] / 2

        # Background
        self.menu_screen = pg.Surface(prepare.RESOLUTION, SRCALPHA, 32)
        self.menu_screen.blit(prepare.IMAGES['menu_bg.png'], (0, 0))

        # Logo + Version
        logo = prepare.IMAGES['gigz_logo.png']
        self.menu_screen.blit(logo, (center - logo.get_width() / 2, 50),
                              (0, 0, logo.get_width(), logo.get_height() - 60))
        version = small_font.render(f"Version {prepare.VERSION}", True, 'grey50')
        self.menu_screen.blit(version, (center - version.get_width() / 2, 300))

        # Level options
        for index, name in enumerate(self.options):
            if index == self.selected_index:
                brush = tools.scale_ratio(prepare.IMAGES['brush.png'], .3)

                self.menu_screen.blit(brush, (center - brush.get_width() / 2, 340 + index * 70))

            txt = base_font.render(f"{name} : {self.options[index][0]}", True, 'white')
            self.menu_screen.blit(txt, (center - txt.get_width() / 2, 350 + index * 70))

        # Timer
        if self.timer is not None:
            timer_txt = small_font.render(f"Starting in {3 - int(time() - self.timer)} seconds ...", True, 'white')
            self.menu_screen.blit(timer_txt, (center - timer_txt.get_width() / 2, 950))

        # Players
        if len(self.joysticks) == 0:
            no_control = base_font.render("No controller detected", True, blood_red)
            self.menu_screen.blit(no_control, (center - no_control.get_width() / 2, 700))
        else:
            for i, joy in enumerate(self.joysticks):
                player_surf = pg.Surface((600, 300), SRCALPHA, 32)
                #current_player = self.players[i]
                # Name
                player_txt = base_font.render(f"Player {i + 1}", True, 'white')
                player_surf.blit(player_txt, (300 - (player_txt.get_width() / 2), 0))
                # Joystick name
                controller = small_font.render(self.joysticks[i].get_name(), True, 'grey70')
                player_surf.blit(controller, (300 - controller.get_width() / 2, 70))

                # Player settings
                for index, name in enumerate(self.player_options[i]):
                    param = self.player_options[i][index][0]
                    if name == 'Color':
                        txt = small_font.render(f"{name} : ", True, 'white')
                        pg.draw.rect(player_surf, param, (310, 100 + index * 35, 70, 30))
                        player_surf.blit(txt, (260 - txt.get_width() / 2, 100 + index * 35))
                    else:
                        txt = small_font.render(f"{name} : {param}", True, 'white')
                        player_surf.blit(txt, (300 - txt.get_width() / 2, 100 + index * 35))

                # Ready
                if self.ready[i]:
                    ready_txt = "READY"
                    color = grass_green
                else:
                    ready_txt = "NOT READY"
                    color = blood_red
                ready = base_font.render(ready_txt, True, color)
                player_surf.blit(ready, (300 - ready.get_width() / 2, 200))

                # Final blit
                self.menu_screen.blit(player_surf, (prepare.RESOLUTION[0] / (len(self.joysticks) + 1) - 300, 700))

    def draw(self, screen):
        screen.blit(self.menu_screen, (0, 0))

    def update_joysticks(self):
        self.joysticks = tools.update_joysticks()[:2]  # You can't plug more than 2 controllers
        self.rumble = [joy.rumble(.1, 0, 1) for joy in self.joysticks]
        self.ready = [False for _ in self.joysticks]

        if len(self.joysticks) > 0:
            pass
            #self.players[0].set_controller(self.joysticks[0].get_guid())

    def get_event(self, event):
        if event.type == QUIT:
            self.quit = True
        if event.type == JOYBUTTONDOWN:
            buttons = tools.ps4controller_map['button']

            # Options selection
            if event.button == buttons['up']:
                self.change_selected_option(-1)
            if event.button == buttons['down']:
                self.change_selected_option(1)
            if event.button == buttons['right']:
                self.options.select_option(self.selected_index, 1)
            if event.button == buttons['left']:
                self.options.select_option(self.selected_index, -1)

            # Player events
            if event.button == buttons['options']:
                self.ready[event.joy] = self.ready[event.joy] is False
            if event.button == buttons['square']:
                self.player_options[event.joy].select_option(0, 1)
            if event.button == buttons['triangle']:
                self.player_options[event.joy].select_option(1, 1)

        # Joysticks events
        if event.type in (JOYDEVICEADDED, JOYDEVICEREMOVED):
            self.update_joysticks()
