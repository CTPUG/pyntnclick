"""Cryo room where the prisoner starts out."""

import random

from gamelib.state import Scene, Item, Thing, Result, \
                          InteractImage, InteractNoImage


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
        "unit": InteractNoImage(520, 430, 80, 50),
    }

    INITIAL = "unit"

    INITIAL_DATA = {
        'contains_titanium_leg': True,
        }

    def interact_without(self):
        self.state.add_inventory_item('titanium_leg')
        self.set_data('contains_titanium_leg', False)
        return Result("The corpse in this cryo unit has a prosthetic leg made out of titanium. You take it.")

    def is_interactive(self):
        return self.get_data('contains_titanium_leg')


class CryoRoomDoor(Thing):
    "Door to the cryo room."

    NAME = "cryo.door"

    INTERACTS = {
        "ajar": InteractImage(290, 260, "door_ajar.png"),
        "open": InteractImage(290, 260, "door_open.png"),
        }

    INITIAL = "ajar"

    INITIAL_DATA = {
        'open': False,
        }

    def interact_with_titanium_leg(self, item):
        self.open_door()
        return Result("You wedge the titanium leg into the chain and twist. With a satisfying *snap*, the chain breaks and the door opens.")

    def interact_without(self):
        return Result("It moves slightly and then stops. A chain on the other side is preventing it from opening completely.")

    def interact_default(self, item):
        return Result(random.choice([
                    "Sadly, this isn't that sort of game.",
                    "Your valiant efforts are foiled by the Evil Game Designer.",
                    "The door resists. Try something else, perhaps?",
                    ]))

    def is_interactive(self):
        return not self.get_data('open')

    def open_door(self):
        self.set_data('open', True)
        self.set_interact("open")
        self.state.scenes['bridge'].set_data('accessible', True)
        self.state.remove_inventory_item('titanium_leg')

    def get_description(self):
        if self.get_data('open'):
            return 'An open doorway leads to the rest of the ship'
        return 'A rusty door. It is currently closed'


class CryoComputer(Thing):
    "Computer in the cryo room."

    NAME = "cryo.computer"

    INTERACTS = {
        "info": InteractImage(416, 290, "comp_info.png"),
        "warn": InteractImage(416, 290, "comp_warn.png"),
        "error": InteractImage(416, 290, "comp_error.png"),
        }

    INITIAL = "info"


SCENES = [Cryo]
