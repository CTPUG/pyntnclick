'''Game main module.

Contains the entry point used by the run_game.py script.

'''

# Albow looks for stuff in os.path[0], which isn't always where it expects.
# The following horribleness fixes this.
import sys
import os.path
right_path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, right_path)
from optparse import OptionParser

import pygame
from pygame.locals import SWSURFACE

from pyntnclick.engine import Engine
from pyntnclick.gamescreen import DefMenuScreen, DefEndScreen
from pyntnclick.constants import GameConstants, DEBUG_ENVVAR
from pyntnclick.resources import Resources
from pyntnclick.sound import Sound
from pyntnclick import state

from pyntnclick.tools.rect_drawer import RectApp, make_rect_display
from pyntnclick.tools.utils import list_scenes


class GameDescriptionError(Exception):
    """Raised when an GameDescription is invalid."""


class GameDescription(object):

    # initial scene for start of game (unless overridden by debug)
    INITIAL_SCENE = None

    # list of game scenes
    SCENE_LIST = None

    # starting menu
    SPECIAL_SCREENS = {
            'menu': DefMenuScreen,
            'end': DefEndScreen,
            }

    START_SCREEN = 'menu'

    # resource module
    RESOURCE_MODULE = "Resources"

    def __init__(self):
        if self.INITIAL_SCENE is None:
            raise GameDescriptionError("A game must have an initial scene.")
        if not self.SCENE_LIST:
            raise GameDescriptionError("A game must have a non-empty list"
                                       " of scenes.")
        self._initial_scene = self.INITIAL_SCENE
        self._scene_list = self.SCENE_LIST
        self._resource_module = self.RESOURCE_MODULE
        self._debug_rects = False
        self.resource = Resources(self._resource_module)
        self.sound = Sound(self.resource)
        self.constants = self.game_constants()
        self.debug_options = []

    def initial_state(self):
        """Create a copy of the initial game state."""
        initial_state = state.Game(self)
        initial_state.set_debug_rects(self._debug_rects)
        for scene in self._scene_list:
            initial_state.load_scenes(scene)
        initial_state.set_current_scene(self._initial_scene)
        initial_state.set_do_enter_leave()
        return initial_state

    def game_constants(self):
        return GameConstants()

    def option_parser(self):
        parser = OptionParser()
        parser.add_option("--no-sound", action="store_false", default=True,
                dest="sound", help="disable sound")
        # We flag these, so we can warn the user that these require debug mode
        self.debug_options = ['--scene', '--no-rects', '--rect-drawer',
                '--list-scenes', '--details']
        if self.constants.debug:
            parser.add_option("--scene", type="str", default=None,
                dest="scene", help="initial scene")
            parser.add_option("--no-rects", action="store_false", default=True,
                dest="rects", help="disable debugging rects")
            parser.add_option("--rect-drawer", action="store_true",
                    default=False, dest="rect_drawer",
                    help="Launch the rect drawing helper tool. Specify the"
                    " scene with --scene")
            parser.add_option("--list-scenes", action="store_true",
                    default=False, dest='list_scenes', help="List all scenes"
                    " that can be used with --scene and exit.")
            parser.add_option("--detail", type="str", default=None,
                    dest="detail", help="Detailed view for rect_drawer")
        return parser

    def warn_debug(self, option):
        """Warn the user that he needs debug mode"""
        print '%s is only valid in debug mode' % option
        print 'set %s to enable debug mode' % DEBUG_ENVVAR
        print

    def main(self):
        parser = self.option_parser()
        # This is a bit hack'ish, but works
        if not self.constants.debug:
            for option in self.debug_options:
                if option in sys.argv:
                    self.warn_debug(option)
        opts, _ = parser.parse_args(sys.argv)
        pygame.display.init()
        pygame.font.init()
        if opts.sound:
            self.sound.enable_sound(self.constants)
        else:
            self.sound.disable_sound()
        if self.constants.debug:
            if opts.scene is not None:
                # debug the specified scene
                self._initial_scene = opts.scene
            self._debug_rects = opts.rects
        if self.constants.debug and opts.list_scenes:
            # FIXME: Horrible hack to avoid image loading issues for
            # now
            display = pygame.display.set_mode(self.constants.screen,
                                              SWSURFACE)
            list_scenes(self.initial_state)
            sys.exit(0)
        if self.constants.debug and opts.rect_drawer:
            if opts.scene is None:
                print 'Need to supply a scene to use the rect drawer'
                sys.exit(1)
            display = make_rect_display()
            # FIXME: Remove Albow from here
            try:
                self.engine = RectApp(display, self.initial_state, opts.scene,
                        opts.detail)
            except KeyError:
                print 'Invalid scene: %s' % opts.scene
                sys.exit(1)
        else:
            pygame.display.set_mode(self.constants.screen, SWSURFACE)
            pygame.display.set_icon(self.resource.get_image(
                    'suspended_sentence24x24.png', basedir='icons'))
            pygame.display.set_caption("Suspended Sentence")

            self.engine = Engine(self)
            # Initialize the special screens in the engine
            for name, cls in self.SPECIAL_SCREENS.iteritems():
                screen = cls(self)
                self.engine.add_screen(name, screen)
            # Should we allow the menu not to be the opening screen?
            self.engine.set_screen(self.START_SCREEN)
        try:
            self.engine.run()
        except KeyboardInterrupt:
            pass
