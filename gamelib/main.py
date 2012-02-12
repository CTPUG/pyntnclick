import scenes

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

    def __init__(self):
        super(SuspendedSentence, self).__init__(SSState)


def main():
    ss = SuspendedSentence()
    return ss.main()
