"""The inside of the maintenance manual."""

import random

from albow.music import change_playlist, get_music, PlayList
from albow.resource import get_image

from gamelib.cursor import CursorSprite
from gamelib.state import Scene, Item, Thing, Result
from gamelib.sound import get_current_playlist

from gamelib.scenes.game_constants import PLAYER_ID
from gamelib.scenes.scene_widgets import (Door, InteractText, InteractNoImage,
                                          InteractRectUnion, InteractImage,
                                          InteractAnimated, GenericDescThing,
                                          BaseCamera, make_jim_dialog)


# classes related the computer detail


class PageBase(Thing):
    "Displays manual pages"

    def get_page_thing(self):
        return self.state.current_detail.things['manual.page']

    def get_page(self):
        return self.get_page_thing().get_data('page')

    def set_page(self, page):
        self.get_page_thing().set_page(page)


class PagePrior(PageBase):
    """Prior page in the manual"""

    NAME = 'manual.page_prior'

    INTERACTS = {
            'up' : InteractNoImage(0, 350, 80, 25)
            }
    INITIAL = 'up'

    def is_interactive(self):
        return self.get_page() > 0

    def interact_without(self):
        self.set_page(self.get_page() - 1)


class PageNext(PageBase):
    """Next page in the manual"""

    NAME = 'manual.page_next'

    INTERACTS = {
            'down' : InteractNoImage(170, 350, 80, 25)
            }
    INITIAL = 'down'

    def is_interactive(self):
        return self.get_page() < len(self.get_page_thing().INTERACTS) - 1

    def interact_without(self):
        self.set_page(self.get_page() + 1)


class ManualPage(Thing):
    """Page in the manual"""

    NAME = 'manual.page'

    INTERACTS = {
            0 : InteractImage(0, 0, 'manual_p1.png'),
            1 : InteractImage(0, 0, 'manual_p2.png'),
            2 : InteractImage(0, 0, 'manual_p3.png'),
            3 : InteractImage(0, 0, 'manual_p4.png'),
            }
    INITIAL = 0

    INITIAL_DATA = {
        'page': 0,
        }

    def is_interactive(self):
        return False

    def set_page(self, page):
        self.set_data('page', page)
        self.set_interact(page)


class ManualDetail(Scene):

    FOLDER = 'manual'
    NAME = 'manual_detail'

    BACKGROUND = 'manual_detail.png'

    def __init__(self, state):
        super(ManualDetail, self).__init__(state)

        self.add_thing(ManualPage())
        self.add_thing(PagePrior())
        self.add_thing(PageNext())
        self._scene_playlist = None

    def enter(self):
        self._scene_playlist = get_current_playlist()
        change_playlist(None)

    def leave(self):
        change_playlist(self._scene_playlist)


SCENES = []
DETAIL_VIEWS = [ManualDetail]
