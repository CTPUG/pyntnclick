"""Crew quarters."""

from gamelib.cursor import CursorSprite
from gamelib.state import Scene, Item, Thing, Result
from gamelib.scenes.scene_widgets import (Door, InteractText, InteractNoImage,
                                          InteractRectUnion, InteractImage,
                                          InteractAnimated, GenericDescThing)

class CrewQuarters(Scene):

    FOLDER = "crew_quarters"
    BACKGROUND = "crew_quarters.png"

    OFFSET = (0, -50)

    INITIAL_DATA = {
        'accessible': True,
        }

    def __init__(self, state):
        super(CrewQuarters, self).__init__(state)
        self.add_thing(ToMap())
        self.add_thing(Safe())
        self.add_thing(FishbowlThing())
        self.add_item(Fishbowl('fishbowl'))
        self.add_thing(GenericDescThing('crew.plant', 1,
            "The plant is doing surprisingly well for centuries of neglect",
            ((624, 215, 61, 108),)))
        self.add_thing(GenericDescThing('crew.cat', 2,
            "A picture of a cat labelled 'Clementine'",
            ((722, 382, 66, 72),)))

    def enter(self):
        return Result("The crew were a messy bunch. Or maybe that's just the intervening centuries.")


class ToMap(Door):

    SCENE = "crew"

    INTERACTS = {
        "door": InteractNoImage(233, 252, 125, 181),
        }

    INITIAL = "door"


class Safe(Thing):
    "A safe, for keeping things safe."

    NAME = 'crew.safe'

    INTERACTS = {
        'safe': InteractNoImage(447, 238, 72, 73),
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


class FishbowlThing(Thing):
    "A safe, for keeping things safe."

    NAME = 'crew.fishbowl'

    INTERACTS = {
        'fishbowl': InteractImage(356, 495, 'fishbowl_on_table.png'),
        'fish_no_bowl': InteractImage(372, 517, 'fish_minus_bowl.png'),
    }

    INITIAL = 'fishbowl'

    INITIAL_DATA = {
        'has_bowl': True,
        }

    def interact_without(self):
        if not self.get_data('has_bowl'):
            return Result("What's the point of lugging around a very dead fish "
                          "and a kilogram or so of sand?")
        self.set_interact('fish_no_bowl')
        self.set_data('has_bowl', False)
        self.state.add_inventory_item('fishbowl')
        return Result("The fishbowl is useful, but its contents aren't.")

    def get_description(self):
        return "This fishbowl looks exactly like an old science fiction space helmet."


class Fishbowl(Item):
    "A bowl. Sans fish."

    INVENTORY_IMAGE = 'fishbowl.png'
    CURSOR = CursorSprite('fishbowl.png', 29, 27)


class SafeDetail(Scene):

    FOLDER = 'crew_quarters'
    BACKGROUND = None # TODO
    NAME = 'safe_detail'

    SIZE = (300, 300)

    def __init__(self, state):
        super(SafeDetail, self).__init__(state)


SCENES = [CrewQuarters]
DETAIL_VIEWS = [SafeDetail]
