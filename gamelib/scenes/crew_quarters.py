"""Crew quarters."""

from pyntnclick.i18n import _
from pyntnclick.cursor import CursorSprite
from pyntnclick.state import Scene, Item, Thing, Result
from pyntnclick.scenewidgets import (
    InteractNoImage, InteractImage, InteractAnimated, GenericDescThing,
    TakeableThing)

from gamelib.scenes.game_constants import PLAYER_ID
from gamelib.scenes.game_widgets import Door, BaseCamera, make_jim_dialog


class CrewQuarters(Scene):

    FOLDER = "crew_quarters"
    BACKGROUND = "crew_quarters.png"

    OFFSET = (0, -50)

    def setup(self):
        self.add_thing(ToMap())
        self.add_thing(Safe())
        self.add_thing(FishbowlThing())
        self.add_item_factory(Fishbowl)
        self.add_item_factory(DuctTape)
        self.add_item_factory(EscherPoster)
        self.add_item_factory(FishbowlHelmet)
        self.add_thing(PosterThing())
        self.add_thing(MonitorCamera())
        self.add_thing(GenericDescThing('crew.plant', 1,
            _("The plant is doing surprisingly well for centuries of neglect"),
            ((624, 215, 61, 108),)))
        self.add_thing(GenericDescThing('crew.cat', 2,
            _("A picture of a cat labelled 'Clementine'"),
            ((722, 382, 66, 72),)))


class ToMap(Door):

    SCENE = "crew_quarters"

    INTERACTS = {
        "door": InteractNoImage(233, 252, 125, 181),
        }

    INITIAL = "door"


class Safe(Thing):
    "A safe, for keeping things safe."

    NAME = 'crew.safe'

    INTERACTS = {
        'safe': InteractNoImage(447, 238, 72, 73),
        'full_safe': InteractImage(445, 227, 'open_safe_full.png'),
        'empty_safe': InteractImage(445, 227, 'open_safe_empty.png'),
    }

    INITIAL = 'safe'

    INITIAL_DATA = {
        'is_cracked': False,
        'has_tape': True,
        }

    def select_interact(self):
        if self.get_data('is_cracked'):
            if self.get_data('has_tape'):
                return 'full_safe'
            return 'empty_safe'
        return self.INITIAL

    def interact_without(self):
        if self.get_data('is_cracked'):
            if self.get_data('has_tape'):
                self.set_data('has_tape', False)
                self.game.add_inventory_item('duct_tape')
                self.set_interact()
                return Result(_("Duct tape. It'll stick to everything except "
                                "ducts, apparently."))
            return Result(_("The perfectly balanced door swings "
                            "frictionlessly to and fro. What craftsmanship!"))
        return Result(_("The safe is locked. This might be an interesting "
                        "challenge, if suitable equipment can be found."))

    def interact_with_stethoscope(self, item):
        if self.get_data('is_cracked'):
            return Result(_("It's already unlocked. "
                            "There's no more challenge."))
        # TODO: Add years to the sentence for safecracking.
        # TODO: Wax lyrical some more about safecracking.
        self.set_data('is_cracked', True)
        self.set_interact()
        return (Result(_("Even after centuries of neglect, the tumblers slide"
                         " almost silently into place. Turns out the"
                         " combination was '1 2 3 4 5'. An idiot must keep his"
                         " luggage in here.")),
                make_jim_dialog(_("Prisoner %s, you have been observed"
                                  " committing a felony violation. This will"
                                  " go onto your permanent record, and your"
                                  " sentence may be extended by up to twenty"
                                  " years.") % PLAYER_ID, self.game))

    def get_description(self):
        return _("Ah, a vintage Knoxx & Co. model QR3. Quaint, but"
                 " reasonably secure.")


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

    def select_interact(self):
        if not self.get_data('has_bowl'):
            return 'fish_no_bowl'
        return self.INITIAL

    def interact_without(self):
        if not self.get_data('has_bowl'):
            return Result(_("What's the point of lugging around a very dead"
                            " fish and a kilogram or so of sand?"))
        self.set_data('has_bowl', False)
        self.set_interact()
        self.game.add_inventory_item('fishbowl')
        return Result(_("The fishbowl is useful, but its contents aren't."))

    def get_description(self):
        if self.get_data('has_bowl'):
            return _("This fishbowl looks exactly like an old science fiction"
                     " space helmet.")
        else:
            return _("An evicted dead fish and some sand lie forlornly on the"
                     " table")


class Fishbowl(Item):
    "A bowl. Sans fish."

    INVENTORY_IMAGE = 'fishbowl.png'
    CURSOR = CursorSprite('fishbowl.png')
    NAME = "fishbowl"

    def interact_with_duct_tape(self, item):
        self.game.replace_inventory_item(self.name, 'helmet')
        return Result(_("You duct tape the edges of the helmet. The seal is"
                        " crude, but it will serve as a workable helmet if"
                        " needed."))


class FishbowlHelmet(Item):
    "A bowl with duct-tape"

    INVENTORY_IMAGE = "fishbowl_helmet.png"
    CURSOR = CursorSprite('fishbowl_helmet.png')
    NAME = "helmet"


class DuctTape(Item):
    "A bowl. Sans fish."

    NAME = 'duct_tape'
    INVENTORY_IMAGE = 'duct_tape.png'
    CURSOR = CursorSprite('duct_tape.png')


class MonitorCamera(BaseCamera):
    "A Camera pointing to JIM"

    NAME = 'crew.camera'

    INTERACTS = {
        'online': InteractImage(85, 97, 'camera_medium.png'),
        'dead': InteractImage(85, 97, 'camera_medium_gray.png'),
        'looping': InteractAnimated(85, 97, ('camera_medium.png',
                                             'camera_medium_gray.png'),
                                    15),
    }


class PosterThing(TakeableThing):
    "A innocent poster on the wall"

    NAME = 'crew.poster'

    INTERACTS = {
        'poster': InteractImage(29, 166, 'triangle_poster.png'),
    }

    INITIAL = 'poster'
    ITEM = 'escher_poster'

    def interact_without(self):
        self.take()
        return Result(_("This poster will go nicely on your bedroom wall."))

    def get_description(self):
        return _("A paradoxical poster hangs below the security camera.")


class EscherPoster(Item):
    "A confusing poster to disable JIM"

    INVENTORY_IMAGE = "triangle_poster.png"
    CURSOR = CursorSprite('triangle_poster.png')
    NAME = "escher_poster"


SCENES = [CrewQuarters]
