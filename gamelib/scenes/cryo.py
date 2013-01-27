"""Cryo room where the prisoner starts out."""

import random

from pyntnclick.i18n import _
from pyntnclick.cursor import CursorSprite
from pyntnclick.state import Scene, Item, CloneableItem, Thing, Result
from pyntnclick.scenewidgets import (
    InteractNoImage, InteractRectUnion, InteractImage, InteractAnimated,
    GenericDescThing, TakeableThing)

from gamelib.scenes.game_constants import PLAYER_ID
from gamelib.scenes.game_widgets import Door, make_jim_dialog


class Cryo(Scene):

    FOLDER = "cryo"
    BACKGROUND = "cryo_room.png"

    INITIAL_DATA = {
        'greet': True,
        'vandalism_warn': True,
        }

    # sounds that will be played randomly as background noise
    MUSIC = [
            'drip1.ogg',
            'drip2.ogg',
            'drip3.ogg',
            'creaking.ogg',
            'silent.ogg',
            'silent.ogg',
            ]

    def setup(self):
        self.add_item_factory(TitaniumLeg)
        self.add_item_factory(TubeFragment)
        self.add_item_factory(FullBottle)
        self.add_thing(CryoUnitAlpha())
        self.add_thing(CryoRoomDoor())
        self.add_thing(CryoComputer())
        self.add_thing(CryoPipeLeft())
        self.add_thing(CryoPipeRightTop())
        self.add_thing(CryoPipeRightBottom())
        self.add_thing(CryoPools())

        # Flavour items
        # pipes
        self.add_thing(GenericDescThing('cryo.pipes', 1,
            _("These pipes carry cooling fluid to the cryo units."),
            (
                (552, 145, 129, 66),
                (636, 82, 165, 60),
                (140, 135, 112, 73),
                (11, 63, 140, 67),
                )))
        self.add_thing(UncuttableCryoPipes())

        # cryo units
        self.add_thing(GenericCryoUnit(2,
            _("An empty cryo chamber."),
            _("Prisoner 81E4-C8900480E635. Embezzlement. 20 years."),
            (
                (155, 430, 50, 35),
                (125, 450, 60, 35),
                (95, 470, 60, 35),
                (55, 490, 60, 55),
                )))

        self.add_thing(GenericCryoUnit(3,
            _("A working cryo chamber. The frosted glass obscures the details"
              " of the occupant."),
            _("Prisoner 9334-CE1EB0243BAB. Murder. 40 years."),
            (
                (215, 430, 50, 35),
                (205, 450, 50, 35),
                (185, 470, 50, 35),
                (125, 505, 80, 40),
                )))

        self.add_thing(GenericCryoUnit(4,
            _("A broken cryo chamber. The skeleton inside has been picked"
              " clean."),
            _("Prisoner BFBC-8BF4C6B7492B. Importing illegal alien biomatter."
              " 15 years."),
            (
                (275, 430, 50, 70),
                (255, 460, 50, 70),
                (235, 490, 50, 60),
                )))

        self.add_thing(GenericCryoUnit(5,
            _("A working cryo chamber. The frosted glass obscures the details "
              "of the occupant."),
            _("Prisoner B520-99495B8C41CE. Copyright infringement. 60 years."),
            (
                (340, 430, 50, 70),
                (330, 500, 60, 50),
                )))

        self.add_thing(GenericCryoUnit(6,
            _("An empty cryo unit. Recently filled by you."),
            _("Prisoner %s. Safecracking, grand larceny. 30 years.")
            % PLAYER_ID,
            (
                (399, 426, 70, 56),
                (404, 455, 69, 120),
                )))

        self.add_thing(GenericCryoUnit(7,
            _("An empty cryo unit."),
            _("Prisoner 83F1-CE32D3234749. Spamming. 5 years."),
            (
                (472, 432, 58, 51),
                (488, 455, 41, 134),
                (517, 487, 42, 93),
                )))

        self.add_thing(GenericCryoUnit(8,
            _("An empty cryo unit."),
            _("Prisoner A455-9DF9F43C43E5. Medical malpractice. 10 years."),
            (
                (596, 419, 69, 39),
                (616, 442, 82, 40),
                (648, 467, 84, 37),
                (681, 491, 97, 60),
                )))

    def enter(self):
        # Setup music
        pieces = [self.sound.get_music(x) for x in self.MUSIC]
        background_playlist = self.sound.get_playlist(pieces, random=True,
                                                      repeat=True)
        self.sound.change_playlist(background_playlist)
        if self.get_data('greet'):
            self.set_data('greet', False)
            return make_jim_dialog(
                    _("Greetings, Prisoner %s. I am the Judicial "
                      "Incarceration Monitor. "
                      "You have been woken early under the terms of the "
                      "emergency conscription act to assist with repairs to "
                      "the ship. Your behaviour during this time will "
                      "be noted on your record and will be relayed to "
                      "prison officials when we reach the destination. "
                      "Please report to the bridge.") % PLAYER_ID, self.game)

    def leave(self):
        # Stop music
        self.sound.change_playlist(None)


class CryoPipeBase(Thing):
    "Base class for cryo pipes that need to be stolen."

    INITIAL = "fixed"

    INITIAL_DATA = {
        'fixed': True,
    }

    def select_interact(self):
        if not self.get_data('fixed'):
            return 'chopped'
        return self.INITIAL

    def interact_with_machete(self, item):
        if self.get_data('fixed'):
            self.set_data('fixed', False)
            self.game.add_inventory_item('tube_fragment')
            self.set_interact()
            responses = [Result(_("It takes more effort than one would expect,"
                                  " but eventually the pipe is separated from"
                                  " the wall."), soundfile="chop-chop.ogg")]
            if self.game.get_current_scene().get_data('vandalism_warn'):
                self.game.get_current_scene().set_data('vandalism_warn', False)
                responses.append(make_jim_dialog(
                    _("Prisoner %s. Vandalism is an offence punishable by a "
                      "minimum of an additional 6 months to your sentence."
                      ) % PLAYER_ID, self.game))
            return responses

    def is_interactive(self, tool=None):
        return self.get_data('fixed')

    def interact_without(self):
        if self.get_data('fixed'):
            return Result(_("These pipes aren't attached to the wall very"
                            " solidly."))
        return None

    def get_description(self):
        if self.get_data('fixed'):
            return _("These pipes carry cooling fluid to empty cryo units.")
        return _("There used to be a pipe carrying cooling fluid here.")


class UncuttableCryoPipes(Thing):
    "Base class for cryo pipes that can't be cut down."

    NAME = "cryo.pipes.2"

    INTERACTS = {
        "fixed": InteractRectUnion((
                (2, 130, 44, 394),
                (756, 127, 52, 393),))
        }

    INITIAL = "fixed"

    def interact_with_machete(self, item):
        return Result(_("These pipes carry fluid to the working cryo units."
                        " Chopping them down doesn't seem sensible."))

    def is_interactive(self, tool=None):
        return True

    def interact_without(self):
        return Result(
          _("These pipes aren't attached to the wall very solidly."))

    def get_description(self):
        return _("These pipes carry cooling fluid to the working cryo units.")


class TubeFragment(CloneableItem):
    "Obtained after cutting down a cryo room pipe."

    NAME = "tube_fragment"
    INVENTORY_IMAGE = "tube_fragment.png"
    CURSOR = CursorSprite('tube_fragment_cursor.png')
    TOOL_NAME = "tube_fragment"
    MAX_COUNT = 3


class CryoPipeLeft(CryoPipeBase):
    "Left cryo pipe."

    NAME = "cryo.pipe.left"
    INTERACTS = {
        "fixed": InteractImage(117, 226, "intact_cryo_pipe_left.png"),
        "chopped": InteractNoImage(125, 192, 27, 258),
        }


class CryoPipeRightTop(CryoPipeBase):
    "Right cryo pipe, top."

    NAME = "cryo.pipe.right.top"
    INTERACTS = {
        "fixed": InteractImage(645, 212, "intact_cryo_pipe_right_top.png"),
        "chopped": InteractNoImage(643, 199, 31, 111),
        }


class CryoPipeRightBottom(CryoPipeBase):
    "Right cryo pipe, bottom."

    NAME = "cryo.pipe.right.bottom"
    INTERACTS = {
        "fixed": InteractImage(644, 333, "intact_cryo_pipe_right_bottom.png"),
        "chopped": InteractNoImage(644, 333, 31, 107),
        }


class TitaniumLeg(Item):
    "Titanium leg, found on a piratical corpse."

    NAME = 'titanium_leg'
    INVENTORY_IMAGE = "titanium_femur.png"
    CURSOR = CursorSprite('titanium_femur_cursor.png', 13, 5)


class CryoUnitAlpha(Thing):
    "Cryo unit containing titanium leg."

    NAME = "cryo.unit.1"

    INTERACTS = {
        "unit": InteractRectUnion((
            (531, 430, 64, 49),
            (560, 460, 57, 47),
            (583, 482, 65, 69),
            (600, 508, 71, 48),
            ))
    }

    INITIAL = "unit"

    INITIAL_DATA = {
        'contains_titanium_leg': True,
        }

    def interact_without(self):
        return Result(detail_view='cryo_detail')

    def interact_with_titanium_leg(self, item):
        return Result(_("You hit the chamber that used to hold this very leg."
                        " Nothing happens as a result."),
                      soundfile="clang2.ogg")

    def get_description(self):
        if self.get_data('contains_titanium_leg'):
            return _("A broken cryo chamber, with a poor unfortunate corpse"
                     " inside.")
        return _("A broken cryo chamber. The corpse inside is missing a leg.")


class GenericCryoUnit(GenericDescThing):
    "Generic Cryo unit"

    def __init__(self, number, description, detailed_description, areas):
        super(GenericCryoUnit, self).__init__('cryo.unit', number,
                description, areas)
        self.detailed_description = detailed_description

    def is_interactive(self, tool=None):
        return True

    def interact_without(self):
        return Result(self.detailed_description)

    def get_description(self):
        return self.description

    def interact_with_titanium_leg(self, item):
        return Result(random.choice([
                _("You bang on the chamber with the titanium femur. Nothing"
                  " much happens."),
                _("Hitting the cryo unit with the femur doesn't achieve"
                  " anything."),
                _("You hit the chamber with the femur. Nothing happens."),
                ]), soundfile="clang2.ogg")


class CryoRoomDoor(Door):
    "Door to the cryo room."

    SCENE = "cryo"

    INTERACTS = {
        "shut": InteractNoImage(290, 260, 99, 152),
        "ajar": InteractImage(290, 260, "door_ajar.png"),
        "open": InteractImage(290, 260, "door_open.png"),
        }

    INITIAL = "shut"

    INITIAL_DATA = {
        'door': "shut",
        }

    def interact_with_titanium_leg(self, item):
        if self.get_data('door') == "ajar":
            self.open_door()
            return Result(_("You wedge the titanium femur into the chain and"
                            " twist. With a satisfying *snap*, the chain"
                            " breaks and the door opens."),
                          soundfile='break.ogg')
        elif self.get_data('door') == "shut":
            text = _("You bang on the door with the titanium femur. It makes a"
                     " clanging sound.")
            return Result(text, soundfile='clang.ogg')
        else:
            return Result(_("You wave the femur in the doorway. Nothing"
                            " happens."))

    def interact_without(self):
        if self.get_data('door') == "shut":
            self.half_open_door()
        if self.get_data('door') != "open":
            return Result(_("It moves slightly and then stops. A chain on the"
                            " other side is preventing it from opening"
                            " completely."), soundfile='chain.ogg')
        else:
            self.game.change_scene('map')
            return None

    def interact_default(self, item):
        return self.interact_without()

    def select_interact(self):
        return self.get_data('door') or self.INITIAL

    def half_open_door(self):
        self.set_data('door', "ajar")
        self.set_interact()

    def open_door(self):
        self.set_data('door', "open")
        self.set_interact()

    def get_description(self):
        if self.get_data('door') == "open":
            return _('An open doorway leads to the rest of the ship.')
        elif self.get_data('door') == "ajar":
            return _("A rusty door. It can't open all the way because of a "
                     "chain on the other side.")
        return _('A rusty door. It is currently closed.')


class CryoComputer(Thing):
    "Computer in the cryo room."

    NAME = "cryo.computer"

    INTERACTS = {
        "info": InteractAnimated(416, 290, ["comp_info.png", "comp_info2.png"],
            10),
        "warn": InteractImage(416, 290, "comp_warn.png"),
        "error": InteractImage(416, 290, "comp_error.png"),
        }

    INITIAL = "info"

    def interact_without(self):
        return Result(detail_view='cryo_comp_detail')

    def interact_with_titanium_leg(self, item):
        return Result(_("Hitting it with the leg accomplishes nothing."))

    def get_description(self):
        return _("A computer terminal, with some text on it.")


class TitaniumLegThing(TakeableThing):
    "Triangle in the cryo room."

    NAME = "cryo.titanium_leg"

    INTERACTS = {
        "leg": InteractImage(180, 132, "leg.png"),
        }

    INITIAL = "leg"
    ITEM = 'titanium_leg'

    def interact_without(self):
        self.game.scenes['cryo'].things['cryo.unit.1'].set_data(
                'contains_titanium_leg', False)
        self.take()
        return Result(_("The skeletal occupant of this cryo unit has an"
                        " artificial femur made of titanium. You take it."))

    def get_description(self):
        return _("This femur looks synthetic.")


class PlaqueThing(Thing):
    "Plaque on the detailed cryo chamber"

    NAME = "cryo.plaque"

    INTERACTS = {
        "plaque": InteractNoImage(60, 40, 35, 24),
        }

    INITIAL = "plaque"

    def interact_without(self):
        return Result(
          _("The plaque is welded to the unit. You can't shift it."))

    def get_description(self):
        return _("'Prisoner 98CC-764E646391EE. War crimes. 45 years.")


class FullBottle(Item):
    NAME = 'full_detergent_bottle'
    INVENTORY_IMAGE = 'bottle_full.png'
    CURSOR = CursorSprite('bottle_full_cursor.png', 27, 7)


class CryoPools(Thing):
    "Handy for cooling engines"

    NAME = 'cryo.pool'

    INTERACTS = {
        'pools': InteractRectUnion((
                (444, 216, 125, 67),
                (44, 133, 74, 107),
                (485, 396, 97, 34),
        )),
    }

    INITIAL = 'pools'

    def get_description(self):
        return _("Coolant leaks disturbingly from the bulkheads.")

    def interact_without(self):
        return Result(_("It's gooey"))

    def interact_with_detergent_bottle(self, item):
        self.game.replace_inventory_item(item.name, 'full_detergent_bottle')
        return Result(_("You scoop up some coolant and fill the bottle."))


class CryoCompDetail(Scene):

    FOLDER = "cryo"
    BACKGROUND = "comp_info_detail.png"
    BACKGROUND_FIXED = "comp_info_detail_fixed.png"
    NAME = "cryo_comp_detail"

    def setup(self):
        self._background_fixed = self.get_image(
            self.FOLDER, self.BACKGROUND_FIXED)

    def draw_background(self, surface):
        if self.game.scenes['engine'].get_data('engine online'):
            surface.blit(self._background_fixed, self.OFFSET, None)
        else:
            surface.blit(self._background, self.OFFSET, None)


class CryoUnitWithCorpse(Scene):

    FOLDER = "cryo"
    BACKGROUND = "cryo_unit_detail.png"
    NAME = "cryo_detail"

    def setup(self):
        self.add_thing(TitaniumLegThing())
        self.add_thing(PlaqueThing())


SCENES = [Cryo]
DETAIL_VIEWS = [CryoUnitWithCorpse, CryoCompDetail]
