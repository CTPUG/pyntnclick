import scenes

from constants import SSConstants
from menu import MenuScreen
from endscreen import EndScreen
from ss_state import SSState

from pyntnclick.main import GameDescription


class SuspendedSentence(GameDescription):

    INITIAL_SCENE = scenes.INITIAL_SCENE
    SCENE_LIST = scenes.SCENE_LIST
    SCREENS = {
            'menu': MenuScreen,
            'end': EndScreen,
            }
    START_SCREEN = 'menu'

    def game_state(self):
        return SSState()

    def game_constants(self):
        return SSConstants()


def main():
    ss = SuspendedSentence()
    return ss.main()
