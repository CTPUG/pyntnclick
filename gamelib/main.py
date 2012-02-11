import scenes

from pyntnclick.main import GameDescription


class SuspendedSentence(GameDescription):

    INITIAL_SCENE = scenes.INITIAL_SCENE
    SCENE_LIST = scenes.SCENE_LIST


def main():
    ss = SuspendedSentence()
    return ss.main()
