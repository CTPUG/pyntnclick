"""Crew quarters."""

from gamelib.cursor import CursorSprite
from gamelib.state import Scene, Item, Thing, Result
from gamelib.scenes.scene_widgets import (Door, InteractText, InteractNoImage,
                                          InteractRectUnion, InteractImage,
                                          InteractAnimated, GenericDescThing)

class CrewQuarters(Scene):

    FOLDER = "crew_quarters"
    BACKGROUND = None # TODO

    INITIAL_DATA = {
        'accessible': True,
        }

    def __init__(self, state):
        super(CrewQuarters, self).__init__(state)
        self.add_thing(ToMap())

    def enter(self):
        return Result("The crew were a messy bunch. Or maybe that's just the intervening centuries.")


class ToMap(Door):

    SCENE = "crew"

    INTERACTS = {
        "door": InteractText(100, 200, "To Map"),
        }

    INITIAL = "door"


class Safe(Thing):
    "A safe, for keeping things safe."

    NAME = 'crew.safe'

    INTERACTS = {
        'safe': InteractText(200, 200, 'Safe'),
    }

    INITIAL = 'safe'

    INITIAL_DATA = {
        'is_cracked': False,
        }

    def interact_without(self):
        if self.get_data('is_cracked'):
            return Result(detail_view='safe_detail')
        return Result("The safe is locked. This might be an interesting"
                      " challenge, if suitable equipment can be found.")

    def interact_with_stethoscope(self, item):
        if self.get_data('is_cracked'):
            return Result("It's already unlocked. There's no more challenge.")
        # TODO: Add years to the sentence for safecracking.
        # TODO: Wax lyrical some more about safecracking.
        return Result("Even after centuries of neglect, the tumblers slide"
                      " almost silently into place. Turns out the combination"
                      " was '1 2 3 4 5'. An idiot must keep his luggage in"
                      " here.")

    def get_description(self):
        return "Ah, a vintage Knoxx & Co. model QR3. Quaint, but reasonably secure."


class SafeDetail(Scene):

    FOLDER = 'crew_quarters'
    BACKGROUND = None # TODO
    NAME = 'safe_detail'

    SIZE = (300, 300)

    def __init__(self, state):
        super(SafeDetail, self).__init__(state)


SCENES = [CrewQuarters]
DETAIL_VIEWS = [SafeDetail]
