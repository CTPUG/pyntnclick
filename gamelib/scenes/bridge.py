"""Bridge where the final showdown with the AI occurs."""

from gamelib.state import Scene, Item, Thing, Result


class Bridge(Scene):

    # FOLDER = "bridge"
    # BACKGROUND = None # TODO

    # TODO: This is for testing.
    FOLDER = "cryo"
    BACKGROUND = "cryo_room.png"
    NAME = "bridge"

    INITIAL_DATA = {
        'accessible': False,
        }

    def enter(self):
        return Result("The bridge is in a sorry, shabby state")



SCENES = [Bridge]
