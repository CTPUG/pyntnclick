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


class PagePrior(Thing):
    """Prior page in the manual"""

    NAME = 'manual.page_prior'

    INTERACTS = {
            'up' : InteractNoImage(594, 82, 30, 58)
            }
    INITIAL = 'up'

    def is_interactive(self):
        page = self.state.current_detail.get_data('page')
        return page > 0

    def interact_without(self):
        page = self.state.current_detail.get_data('page')
        self.state.current_detail.set_data('page', page - 1)


class PageNext(Thing):
    """Next page in the manual"""

    NAME = 'manual.page_next'

    INTERACTS = {
            'down' : InteractNoImage(594, 293, 30, 58)
            }
    INITIAL = 'down'

    def is_interactive(self):
        page = self.state.current_detail.get_data('page')
        return (page + 1) < self.current_detail.get_data('max page')

    def interact_without(self):
        page = self.state.current_detail.get_data('page')
        self.state.current_detail.set_data('page', page + 1)


class ManualDetail(Scene):

    FOLDER = 'manual'
    NAME = 'manual_detail'

    SIZE = (640, 400)

    PAGES = ['manual_p1.png', 'manual_p2.png',
             'manual_p3.png', 'manual_p4.png']

    BACKGROUND = PAGES[0]

    INITIAL_DATA = {
            'page' : 0,
            'max page' : len(PAGES),
    }

    def __init__(self, state):
        super(ManualDetail, self).__init__(state)

        self.add_thing(PagePrior())
        self.add_thing(PageNext())
        self._scene_playlist = None
        self._pages = [get_image(self.FOLDER, x) for x in self.PAGES]

    def enter(self):
        self._scene_playlist = get_current_playlist()
        change_playlist(None)

    def leave(self):
        change_playlist(self._scene_playlist)

    def draw_background(self, surface):
        self._background = self._pages[self.get_data('page')]
        super(ManualDetail, self).draw_background(surface)


SCENES = []
DETAIL_VIEWS = [ManualDetail]
