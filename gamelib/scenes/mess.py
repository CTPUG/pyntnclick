"""Mess where crew eat. Fun stuff."""

from random import choice, randint

from gamelib.state import Scene, Item, CloneableItem, Thing, Result
from gamelib.cursor import CursorSprite
from gamelib.scenes.scene_widgets import (Door, InteractText, InteractNoImage,
                                          InteractRectUnion, InteractImage,
                                          InteractImageRect, InteractAnimated,
                                          GenericDescThing)

from gamelib.sound import get_sound
from gamelib import constants
from gamelib.scenes.game_constants import PLAYER_ID


class Mess(Scene):

    FOLDER = "mess"
    BACKGROUND = "mess_hall.png"

    INITIAL_DATA = {
        'accessible': True,
        'life support status': 'broken', # broken, replaced, fixed
        }

    def __init__(self, state):
        super(Mess, self).__init__(state)
        self.add_thing(CansOnShelf())
        self.add_thing(Tubes())
        self.add_thing(ToMap())
        self.add_thing(DetergentThing())
        self.add_thing(Boomslang())
        self.add_item(DetergentBottle('detergent_bottle'))
        # Flavour items
        # extra cans on shelf
        self.add_thing(GenericDescThing('mess.cans', 1,
            "A large collection of rusted, useless cans.",
            (
                (154, 335, 89, 106),
                (152, 435, 63, 66),
                )))
        self.add_thing(GenericDescThing('mess.broccoli', 2,
            "An impressively overgrown broccoli.",
            (
                (503, 89, 245, 282),
                (320, 324, 229, 142),
                )))


class BaseCan(CloneableItem):
    """Base class for the cans"""

    def interact_with_full_can(self, item, state):
        return Result("You bang the cans together. It sounds like two cans being banged together.", soundfile="can_hit.ogg")

    def interact_with_dented_can(self, item, state):
        return self.interact_with_full_can(item, state)

    def interact_with_empty_can(self, item, state):
        return self.interact_with_full_can(item, state)

    def interact_with_machete(self, item, state):
        return Result("You'd mangle it beyond usefulness.")

    def interact_with_canopener(self, item, state):
        empty = EmptyCan('empty_can')
        state.add_item(empty)
        state.replace_inventory_item(self.name, empty.name)
        return Result("You open both ends of the can, discarding the hideous contents.")


class EmptyCan(BaseCan):
    "After emptying the full can."

    INVENTORY_IMAGE = "empty_can.png"
    CURSOR = CursorSprite('empty_can_cursor.png')

    def interact_with_titanium_leg(self, item, state):
        return Result("Flattening the can doesn't look like a useful thing to do.")

    def interact_with_canopener(self, item, state):
        return Result("There's nothing left to open on this can")


class FullCan(BaseCan):
    "Found on the shelf."

    INVENTORY_IMAGE = "full_can.png"
    CURSOR = CursorSprite('full_can_cursor.png')

    def interact_with_titanium_leg(self, item, state):
        dented = DentedCan("dented_can")
        state.add_item(dented)
        state.replace_inventory_item(self.name, dented.name)
        return Result("You club the can with the femur. The can gets dented, but doesn't open.", soundfile="can_hit.ogg")


class DentedCan(BaseCan):
    "A can banged on with the femur"

    INVENTORY_IMAGE = "dented_can.png"
    CURSOR = CursorSprite('dented_can_cursor.png')

    def interact_with_titanium_leg(self, item, state):
        return Result("You club the can with the femur. The dents shift around, but it still doesn't open.", soundfile="can_hit.ogg")


class CansOnShelf(Thing):

    NAME = "mess.cans"

    INTERACTS = {
        '3cans': InteractImage(165, 209, 'shelf_3_cans.png'),
        '2cans': InteractImage(165, 209, 'shelf_2_cans.png'),
        '1cans': InteractImage(165, 209, 'shelf_1_can.png'),
        '0cans': InteractNoImage(165, 209, 50, 50),
    }

    INITIAL = '3cans'

    INITIAL_DATA = {
        'cans_available': 3,
    }

    def interact_without(self):
        starting_cans = self.get_data('cans_available')
        if starting_cans > 0:
            can = FullCan("full_can")
            self.state.add_item(can)
            self.state.add_inventory_item(can.name)
            self.set_data('cans_available', starting_cans - 1)
            self.set_interact('%icans' % (starting_cans - 1))
            if starting_cans == 1:
                self.scene.remove_thing(self)
            return Result({
                    3: "Best before a long time in the past. Better not eat these.",
                    2: "Mmmm. Nutritious bacteria stew.",
                    1: "Candied silkworms. Who stocked this place?!",
                    }[starting_cans])
        else:
            return Result("The rest of the cans are rusted beyond usefulness.")

    def get_description(self):
        return "The contents of these cans look synthetic."


class Tubes(Thing):

    NAME = "mess.tubes"

    INTERACTS = {
        "blocked": InteractImage(250, 130, "blocking_broccoli.png"),
        "broken": InteractImage(250, 183, "broken_tubes.png"),
        "replaced": InteractImage(250, 183, "replaced_tubes.png"),
        "fixed": InteractImage(252, 183, "fixed_tubes.png"),
        }

    INITIAL = "blocked"

    INITIAL_DATA = {
        "status": "blocked",
        }

    def get_description(self):
        if self.get_data('status') == "blocked":
            return "The broccoli seems to have become entangled with something."
        elif self.get_data("status") == "broken":
            return "These broken pipes look important."
        elif self.get_data("status") == "replaced":
            return "The pipes have been repaired but are the repairs aren't airtight, yet"
        else:
            return "Your fix looks like it's holding up well."

    def interact_with_machete(self, item):
        if self.get_data("status") == "blocked":
            self.set_data("status", "broken")
            self.set_interact("broken")
            return Result("With a flurry of disgusting mutant vegetable "
                          "chunks, you clear the overgrown broccoli away from "
                          "the access panel and reveal some broken tubes. "
                          "They look important.",
                          soundfile='chopping.ogg')
        elif self.get_data("status") == "broken":
            return Result("It looks broken enough already.")
        elif self.get_data("status") == "replaced":
            return Result("Cutting holes won't repair the leaks.")
        else:
            return Result("After all that effort fixing it, chopping it to "
                          "bits doesn't seem very smart.")

    def interact_with_cryo_pipes_three(self, item):
        if self.get_data("status") == "blocked":
            return Result("It would get lost in the fronds.")
        else:
            self.state.remove_inventory_item(item.name)
            self.set_data('status', 'replaced')
            self.set_interact("replaced")
            self.scene.set_data('life support status', 'replaced')
            return Result(
                "The pipes slot neatly into place, but don't make an airtight seal. "
                "One of the pipes has cracked slightly as well."
            )

    def interact_with_duct_tape(self, item):
        if self.get_data("status") == "broken":
            return Result("It would get lost in the fronds.")
        elif self.get_data("status") == 'fixed':
            return Result("There's quite enough tape on the ducting already.")
        else:
            self.set_data("fixed", True)
            self.set_data("status", "fixed")
            self.set_interact("fixed")
            self.scene.set_data('life support status', 'fixed')
            # TODO: A less anticlimactic climax?
            return Result("It takes quite a lot of tape, but eventually everything is"
                          " airtight and ready to hold pressure. Who'd've thought duct"
                          " tape could actually be used to tape ducts?")

    def interact_without(self):
        if self.get_data("status") == "blocked":
            return Result("The mutant broccoli resists your best efforts.")
        elif self.get_data("status") == "broken":
            return Result("Shoving the broken pipes around doesn't help much.")
        elif self.get_data("status") == "replaced":
            return Result("Do you really want to hold it together for the "
                          "rest of the voyage?")
        else:
            return Result("You don't find any leaks. Good job, Prisoner %s." % PLAYER_ID)


class Boomslang(Thing):
    NAME = 'mess.boomslang'

    INTERACTS = {
        'snake': InteractAnimated(455, 241, (
            'boomslang_no_tongue.png', 'boomslang_with_tongue.png',
            'boomslang_no_tongue.png', 'boomslang_with_tongue.png',
            'boomslang_no_tongue.png',
            ), 5),
        'no_snake': InteractNoImage(0, 0, 0, 0),
    }

    INITIAL = 'no_snake'

    INITIAL_DATA = {
        'anim_pos': -1,
        }

    HISS = get_sound('boomslang.ogg')

    def is_interactive(self):
        return False

    def animate(self):
        if self.get_data('anim_pos') > -1:
            self.current_interact.animate()
            if self.get_data('anim_pos') > self.current_interact._anim_pos:
                self.set_interact('no_snake')
                self.set_data('anim_pos', -1)
            else:
                self.set_data('anim_pos', self.current_interact._anim_pos)
            return True
        if randint(0, 30 * constants.FRAME_RATE) == 0:
            self.set_interact('snake')
            self.set_data('anim_pos', 0)
            self.HISS.play()
        return False


class DetergentThing(Thing):

    NAME = "mess.detergent"

    INTERACTS = {
        'present': InteractImageRect(581, 424, 'detergent_lid.png', 565, 399, 62, 95),
        'taken': InteractNoImage(565, 399, 62, 95),
    }

    INITIAL = 'present'

    INITIAL_DATA = {
        'taken': False,
    }

    def interact_without(self):
        if self.get_data('taken'):
            return Result("The remaining bottles leak.")
        self.set_data('taken', True)
        self.set_interact('taken')
        self.state.add_inventory_item('detergent_bottle')
        return Result("You pick up an empty dishwashing liquid bottle. You can't find any sponges.")

    def get_description(self):
        return "Empty plastic containers. They used to hold dishwasher soap."


class DetergentBottle(Item):
    INVENTORY_IMAGE = 'bottle_empty.png'
    CURSOR = CursorSprite('bottle_empty_cursor.png', 27, 7)


class ToMap(Door):

    SCENE = "mess"

    INTERACTS = {
        "door": InteractNoImage(20, 390, 85, 150),
        }

    INITIAL = "door"


SCENES = [Mess]
