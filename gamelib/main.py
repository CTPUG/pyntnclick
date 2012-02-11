import scenes

from menu import MenuScreen
from endscreen import EndScreen

from pyntnclick.main import GameDescription


class SuspendedSentence(GameDescription):

    INITIAL_SCENE = scenes.INITIAL_SCENE
    SCENE_LIST = scenes.SCENE_LIST
    SPECIAL_SCENES = {
            'menu': MenuScreen,
            'end': EndScreen,
            }
    START_SCREEN = 'menu'


def main():
    ss = SuspendedSentence()
    return ss.main()
