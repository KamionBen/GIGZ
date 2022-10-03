import sys
import pygame as pg
from data import control
from data.states import menu, game, pause

app = control.Control()
states_dict = {
    'mainmenu': menu.MainMenu(),
    'game': game.Game(),
    'gamemenu': pause.GameMenu(),
    'pausemenu': pause.PauseMenu()
}
app.setup_states(states_dict, 'mainmenu')
app.main_game_loop()
pg.quit()
sys.exit()
