import sys
import pygame as pg
from data import control
from data.states import menu, game, pause

app = control.Control()
states_dict = {
    'menu': menu.MainMenu(),
    'game': game.Game(),
    'pause': pause.Pause()
}
app.setup_states(states_dict, 'menu')
app.main_game_loop()
pg.quit()
sys.exit()
