from time import time
import pygame as pg
from pygame.locals import *
from .. import tools, prepare, player, level, survivor


class MainMenu(tools.State):
    def __init__(self):
        tools.State.__init__(self)
        self.done = False
        self.next = 'game'

        # Joysticks
        tools.State.joysticks = tools.update_joysticks()
        self.rumble = [joy.rumble(.1, 0, 1) for joy in self.joysticks]
        self.ready = [False for _ in self.joysticks]

        # Players
        tools.State.players = [player.PlayerProfile() for _ in self.joysticks]
        # TODO : Separate ready controllers

        # Level
        self.level_options = tools.Options(Level=['HVStreet'],
                                           Difficulty=['Godmode', 'Easy'],
                                           Zombies=[100, 50, 10, None],
                                           Friendly_fire=[False, True])

        self.timer = None

        self.base_font = prepare.FONTS['Biometric Joe'][56]
        self.small_font = prepare.FONTS['Biometric Joe'][32]

    def start_game(self):
        """ Initiate the game """
        # Create level
        tools.State.level = level.Level(name=self.level_options['Level'],
                                        difficulty=self.level_options['Difficulty'],
                                        zombie_number=self.level_options['Zombies'],
                                        friendly_fire=self.level_options['Friendly_fire'])

        for i, u_player in enumerate(tools.State.players):
            u_player.update_options()
            new_survivor = survivor.SurvivorControl(self.level.survivors_spawns[i])
            u_player.set_survivor(new_survivor)

    def update(self):
        if all(self.ready) and len(self.ready) > 0:
            if self.timer is None:
                self.timer = time()
            elif time() - self.timer >= 3:  # 3 seconds
                self.start_game()
                self.done = True
        elif self.timer is not None:
            self.timer = None

    def draw(self, screen):
        self._draw_tile(screen)
        self._draw_options(screen)
        self._draw_players(screen)

    def _draw_players(self, screen):
        # Sugar
        blood_red = (183, 15, 15)
        grass_green = (39, 148, 15)

        center_x = 1920 / 2

        # Timer
        if self.timer is not None:
            timer_txt = self.small_font.render(f"Starting in {3 - int(time() - self.timer)} seconds ...", True, 'white')
            screen.blit(timer_txt, (center_x - timer_txt.get_width() / 2, 950))

        # Players
        if len(self.joysticks) == 0:
            no_control = self.base_font.render("No controller detected", True, blood_red)
            screen.blit(no_control, (center_x - no_control.get_width() / 2, 700))
        else:
            for i, i_player in enumerate(tools.State.players):
                player_surf = pg.Surface((600, 300), SRCALPHA, 32)
                # current_player = self.players[i]
                # Name
                player_txt = self.base_font.render(i_player.name, True, 'white')
                player_surf.blit(player_txt, (300 - (player_txt.get_width() / 2), 0))
                # Joystick name
                controller = self.small_font.render(self.joysticks[i].get_name(), True, 'grey70')
                player_surf.blit(controller, (300 - controller.get_width() / 2, 70))

                # Player settings
                n = 0
                for name, parameter in i_player.options.items():
                    if name == 'Color':
                        txt = self.small_font.render(f"{name} : ", True, 'white')
                        pg.draw.rect(player_surf, parameter, (310, 100 + n * 35, 70, 30))
                        player_surf.blit(txt, (260 - txt.get_width() / 2, 100 + n * 35))
                    else:
                        txt = self.small_font.render(f"{name} : {parameter}", True, 'white')
                        player_surf.blit(txt, (300 - txt.get_width() / 2, 100 + n * 35))
                    n += 1
                # Ready
                if self.ready[i]:
                    ready_txt = "READY"
                    color = grass_green
                else:
                    ready_txt = "NOT READY"
                    color = blood_red
                ready = self.base_font.render(ready_txt, True, color)
                player_surf.blit(ready, (300 - ready.get_width() / 2, 200))

                # Final blit
                screen.blit(player_surf, (1920 / (len(self.joysticks) + 1) - 300 + i * 600, 700))

    def _draw_options(self, screen):
        center_x = 1920/2
        # Level options
        i = 0
        for option, parameter in self.level_options.items():
            if self.level_options.is_selected(option):
                brush = tools.scale_ratio(prepare.IMAGES['brush.png'], .3)
                screen.blit(brush, (center_x - brush.get_width() / 2, 340 + i * 70))

            txt = self.base_font.render(f"{option.replace('_', ' ')} : {parameter}", True, 'white')
            screen.blit(txt, (center_x - txt.get_width() / 2, 350 + i * 70))
            i += 1

    def _draw_tile(self, screen):
        center_x = 1920/2
        # Background
        screen.blit(prepare.IMAGES['menu_bg.png'], (0, 0))

        # Logo + Version
        logo = prepare.IMAGES['gigz_logo.png']
        screen.blit(logo, (center_x - logo.get_width() / 2, 50))
        version = self.small_font.render(f"Version {prepare.VERSION}", True, 'grey50')
        screen.blit(version, (center_x - version.get_width() / 2, 300))

    def update_joysticks(self):
        self.joysticks = tools.update_joysticks()[:2]  # You can't plug more than 2 controllers
        self.rumble = [joy.rumble(.1, 0, 1) for joy in self.joysticks]
        self.ready = [False for _ in self.joysticks]

        while len(self.joysticks) > len(self.players):
            self.players.append(player.PlayerProfile())

    def get_event(self, event):
        if event.type == QUIT:
            self.quit = True
        if event.type == JOYBUTTONDOWN:
            buttons = tools.ps4controller_map['button']

            # Options selection
            if event.button == buttons['up']:
                self.level_options.change_cursor(-1)
            if event.button == buttons['down']:
                self.level_options.change_cursor(1)
            if event.button == buttons['right']:
                self.level_options.change_parameter(1)
            if event.button == buttons['left']:
                self.level_options.change_parameter(-1)

            # Player events
            if event.button == buttons['options']:
                self.ready[event.joy] = self.ready[event.joy] is False
            if event.button == buttons['square']:
                self.players[event.joy].options.change_parameter(1, 0)
            if event.button == buttons['triangle']:
                self.players[event.joy].options.change_parameter(1, 1)

        # Joysticks events
        if event.type in (JOYDEVICEADDED, JOYDEVICEREMOVED):
            self.update_joysticks()
