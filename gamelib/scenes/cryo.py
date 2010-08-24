"""Cryo room where the prisoner starts out."""

import random

from gamelib.state import Scene, Item, Thing, Result, \
                          InteractImage, InteractNoImage, InteractRectUnion, \
                          InteractAnimated
from gamelib import speech


class Cryo(Scene):

    FOLDER = "cryo"
    BACKGROUND = "cryo_room.png"

    INITIAL_DATA = {
        'accessible': True,
        }

    def __init__(self, state):
        super(Cryo, self).__init__(state)
        self.add_item(Triangle("triangle"))
        self.add_item(TitaniumLeg("titanium_leg"))
        self.add_thing(CryoUnitAlpha())
        self.add_thing(CryoRoomDoor())
        self.add_thing(CryoComputer())


class Triangle(Item):
    "Test item. Needs to go away at some point."

    INVENTORY_IMAGE = "triangle.png"


class TitaniumLeg(Item):
    "Titanium leg, found on a piratical corpse."

    INVENTORY_IMAGE = "titanium_femur.png"


class CryoUnitAlpha(Thing):
    "Cryo unit containing titanium leg."

    NAME = "cryo.unit.1"

    INTERACTS = {
        "unit": InteractRectUnion(((520, 430, 80, 50), (550, 470, 90, 60),
            (600, 510, 60, 40)))
    }

    INITIAL = "unit"

    INITIAL_DATA = {
        'contains_titanium_leg': True,
        }

    def interact_without(self):
        self.state.add_inventory_item('titanium_leg')
        self.set_data('contains_titanium_leg', False)
        return Result("The skeletal occupant of this cryo unit has an artificial femur made of titanium. You take it.")

    def is_interactive(self):
        return self.get_data('contains_titanium_leg')

    def get_description(self):
        if self.get_data('contains_titanium_leg'):
            return "A broken cryo chamber, with an poor unfortunate corpse inside"
        return "A broken cryo chamber. The corpse inside is missing a leg"


class CryoRoomDoor(Thing):
    "Door to the cryo room."

    NAME = "cryo.door"

    INTERACTS = {
        "shut": InteractNoImage(290, 260, 99, 152),
        "ajar": InteractImage(290, 260, "door_ajar.png"),
        "open": InteractImage(290, 260, "door_open.png"),
        }

    INITIAL = "shut"

    INITIAL_DATA = {
        'door': "shut",
        }

    SPEECH = [
        "Sadly, this isn't that sort of game.",
        "Your valiant efforts are foiled by the Evil Game Designer.",
        "The door resists. Try something else, perhaps?",
        "You bang on the door with the titanium femur. It makes a clanging sound.",
    ]

    def interact_with_titanium_leg(self, item):
        if self.get_data('door') == "ajar":
            self.open_door()
            return Result("You wedge the titanium femur into the chain and twist. With a satisfying *snap*, the chain breaks and the door opens.")
        elif self.get_data('door') == "shut":
            text = "You bang on the door with the titanium femur. It makes a clanging sound."
            speech.say(self.name, text)
            return Result(text)
        else:
            return Result("You wave the femur in the doorway. Nothing happens.")

    def interact_without(self):
        if self.get_data('door') == "shut":
            self.half_open_door()
        if self.get_data('door') != "open":
            return Result("It moves slightly and then stops. A chain on the other side is preventing it from opening completely.")
        else:
            self.state.set_current_scene('bridge')
            return Result("you leave the room, hoping to never return.")

    def interact_default(self, item):
        return Result(random.choice([
                    "Sadly, this isn't that sort of game.",
                    "Your valiant efforts are foiled by the Evil Game Designer.",
                    "The door resists. Try something else, perhaps?",
                    ]))

    def is_interactive(self):
        return True

    def half_open_door(self):
        self.set_data('door', "ajar")
        self.set_interact("ajar")

    def open_door(self):
        self.set_data('door', "open")
        self.set_interact("open")
        self.state.scenes['bridge'].set_data('accessible', True)
        self.state.remove_inventory_item('titanium_leg')

    def get_description(self):
        if self.get_data('door') == "open":
            return 'An open doorway leads to the rest of the ship.'
        elif self.get_data('door') == "ajar":
            return "A rusty door.  It can't open all the way because of a chain on the other side."
        return 'A rusty door. It is currently closed.'


class CryoComputer(Thing):
    "Computer in the cryo room."

    NAME = "cryo.computer"

    INTERACTS = {
        "info": InteractAnimated(416, 290, ["comp_info.png", "comp_warn.png"],
            10),
        "warn": InteractImage(416, 290, "comp_warn.png"),
        "error": InteractImage(416, 290, "comp_error.png"),
        }

    INITIAL = "info"


SCENES = [Cryo]
