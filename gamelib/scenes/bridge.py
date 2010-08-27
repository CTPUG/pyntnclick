"""Bridge where the final showdown with the AI occurs."""

import random

from albow.music import change_playlist, get_music, PlayList

from gamelib.cursor import CursorSprite
from gamelib.state import Scene, Item, Thing, Result, InteractText, \
                          InteractNoImage, InteractRectUnion, InteractAnimated
from gamelib.statehelpers import GenericDescThing
from gamelib.scenes.scene_widgets import Door

class Bridge(Scene):

    FOLDER = "bridge"
    BACKGROUND = 'bridge.png'

    MUSIC = [
            'beep330.ogg',
            'beep660.ogg',
            'beep880.ogg',
            'beep440.ogg',
            'silent.ogg',
            'creaking.ogg',
            'silent.ogg',
            ]

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
        self.add_thing(BridgeComputer())
        self.add_thing(LeftLights())
        self.add_thing(RightLights())

    def enter(self):
        pieces = [get_music(x, prefix='sounds') for x in self.MUSIC]
        background_playlist = PlayList(pieces, random=True, repeat=True)
        change_playlist(background_playlist)
        return Result("The bridge is in a sorry, shabby state")

    def leave(self):
        change_playlist(None)


class ToMap(Door):

    NAME = "bridge.tomap"

    INTERACTS = {
        "door": InteractNoImage(707, 344, 84, 245),
        }

    INITIAL = "door"


class BridgeComputer(Thing):
    """The bridge computer. Gives status updates"""

    NAME = "bridge.comp"

    INTERACTS = {
        'screen' : InteractNoImage(338, 296, 123, 74),
    }

    INITIAL = 'screen'

    def interact_without(self):
        return Result(detail_view='bridge_comp_detail')

    def interact_with_titanium_leg(self):
        return Result("You can't break the duraplastic screen.")

    def interact_with_machete(self):
        return Result("Scratching the screen won't help you.")

    def get_description(self):
        return "The main bridge computer screen."


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

class BlinkingLights(Thing):

    def get_description(self):
        return random.choice([
            "The lights flash in interesting patterns.",
            "The flashing lights don't mean anything to you",
            "The console lights flash and flicker",
            ])

class LeftLights(BlinkingLights):

    NAME ='bridge.lights.1'

    INTERACTS = {
        "lights": InteractAnimated(176, 337, ["bridge_lights_1_1.png", "bridge_lights_1_2.png", "bridge_lights_1_3.png", "bridge_lights_1_2.png"], 5)
    }

    INITIAL = 'lights'

class RightLights(BlinkingLights):

    NAME ='bridge.lights.2'

    INTERACTS = {
        "lights": InteractAnimated(559, 332, ["bridge_lights_2_1.png", "bridge_lights_2_2.png", "bridge_lights_2_3.png", "bridge_lights_2_2.png"], 5)
    }

    INITIAL = 'lights'



class ChairDetail(Scene):

    FOLDER = 'bridge'
    BACKGROUND = 'chair_detail.png'
    NAME = 'chair_detail'

    SIZE = (300, 300)

    def __init__(self, state):
        super(ChairDetail, self).__init__(state)
        self.add_thing(SuperconductorThing())

class BridgeCompDetail(Scene):

    FOLDER = 'bridge'
    BACKGROUND = 'comp_detail_1.png'
    NAME = 'bridge_comp_detail'

    SIZE = (300, 300)

    def __init__(self, state):
        super(BridgeCompDetail, self).__init__(state)


SCENES = [Bridge]
DETAIL_VIEWS = [ChairDetail, BridgeCompDetail]
