"""Bridge where the final showdown with the AI occurs."""

from gamelib.cursor import CursorSprite
from gamelib.state import Scene, Item, Thing, Result, InteractText, \
                          InteractNoImage, InteractRectUnion

class Bridge(Scene):

    FOLDER = "bridge"
    BACKGROUND = 'bridge.png'

    INITIAL_DATA = {
        'accessible': True,
        }

    def __init__(self, state):
        super(Bridge, self).__init__(state)
        self.add_item(Superconductor('superconductor'))
        self.add_item(Stethoscope('stethoscope'))
        self.add_thing(ToMap())
        self.add_thing(MassageChair())
        self.add_thing(StethoscopeThing())

    def enter(self):
        return Result("The bridge is in a sorry, shabby state")


class ToMap(Thing):
    "Way to map."

    NAME = "bridge.tomap"
    DEST = "map"

    INTERACTS = {
        "door": InteractNoImage(707, 344, 84, 245),
        }

    INITIAL = "door"

    def interact_without(self):
        """Go to map."""
        self.state.set_current_scene("map")


class MassageChair(Thing):
    "The captain's massage chair, contains superconductor"

    NAME = 'bridge.massagechair'

    INTERACTS = {
        'chair': InteractRectUnion((
            (76, 365, 72, 216),
            (148, 486, 160, 97),
            (148, 418, 77, 68),
        )),
    }

    INITIAL = 'chair'

    INITIAL_DATA = {
            'contains_superconductor': True,
    }

    def interact_without(self):
        return Result(detail_view='chair_detail')

    def get_description(self):
        if self.get_data('contains_superconductor'):
            return "A top of the line Massage-o-Matic Captain's Executive Command Chair."
        return "The chair won't work any more, it has no power."


class Stethoscope(Item):
    "Used for cracking safes. Found on the doctor on the chair"

    INVENTORY_IMAGE = 'triangle.png'
    CURSOR = CursorSprite('triangle.png', 20, 30)


class StethoscopeThing(Thing):
    "Stehoscope on the doctor"

    NAME ='bridge.stethoscope'

    INTERACTS = {
        'stethoscope': InteractNoImage(643, 177, 57, 87),
    }

    INITIAL = 'stethoscope'

    def interact_without(self):
        self.state.add_inventory_item('stethoscope')
        self.scene.remove_thing(self)
        return Result("You pick up the stethoscope and verify that the doctor's "
                      "heart has stoped. Probably a while ago.")


class Superconductor(Item):
    "Used for connecting high-powered parts of the ship up"

    INVENTORY_IMAGE = 'triangle.png'
    CURSOR = CursorSprite('triangle.png', 20, 30)


class SuperconductorThing(Thing):
    "Superconductor from the massage chair."

    NAME ='bridge.superconductor'

    INTERACTS = {
        'superconductor': InteractText(100, 200, 'Superconductor'),
    }

    INITIAL = 'superconductor'

    def interact_without(self):
        self.state.add_inventory_item('superconductor')
        self.state.current_scene.things['bridge.massagechair'] \
                          .set_data('contains_superconductor', False)
        self.scene.remove_thing(self)
        return Result("You pick up the stethoscope and verify that the doctor's "
                      "heart has stoped. Probably a while ago.")

class ChairDetail(Scene):

    FOLDER = 'bridge'
    BACKGROUND = 'chair_detail.png'
    NAME = 'chair_detail'

    SIZE = (300, 300)

    def __init__(self, state):
        super(ChairDetail, self).__init__(state)
        self.add_thing(SuperconductorThing())


SCENES = [Bridge]
DETAIL_VIEWS = [ChairDetail]
