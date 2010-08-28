"""You WON screen"""

from gamelib.state import Scene, Item, Thing, Result
from gamelib.scenes.game_constants import PLAYER_ID
from gamelib.scenes.scene_widgets import (Door, InteractText, InteractNoImage,
                                          InteractRectUnion, InteractImage,
                                          InteractAnimated, GenericDescThing,
                                          make_jim_dialog)


class Won(Scene):

    FOLDER = "won"
    BACKGROUND = "won.png"

    INITIAL_DATA = {
        'accessible': False,
        }

    def __init__(self, state):
        super(Won, self).__init__(state)

    def enter(self):
        return Result("Congratulations, Prisoner %s. You head off to your chosen "
                "destination, safe in the knowledge that nothing can stop you. "
                "Now you just need to find something to do during the intervening months." % PLAYER_ID)

SCENES = [Won]
