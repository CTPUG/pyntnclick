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
from albow.shell import Shell

from pyntnclick.menu import MenuScreen
from pyntnclick.gamescreen import GameScreen
from pyntnclick.endscreen import EndScreen
from pyntnclick.constants import (
    SCREEN, FRAME_RATE)
from pyntnclick.sound import Sound
from pyntnclick import state, data


class MainShell(Shell):
    def __init__(self, display, initial_state):
        Shell.__init__(self, display)
        self.menu_screen = MenuScreen(self)
        self.game_screen = GameScreen(self, initial_state)
        self.end_screen = EndScreen(self)
        self.set_timer(FRAME_RATE)
        self.show_screen(self.menu_screen)


class GameDescriptionError(Exception):
    """Raised when an GameDescription is invalid."""


class GameDescription(object):

    # initial scene for start of game (unless overridden by debug)
    INITIAL_SCENE = None

    # list of game scenes
    SCENE_LIST = None

    def __init__(self):
        if self.INITIAL_SCENE is None:
            raise GameDescriptionError("A game must have an initial scene.")
        if not self.SCENE_LIST:
            raise GameDescriptionError("A game must have a non-empty list"
                                       " of scenes.")
        self._initial_scene = self.INITIAL_SCENE
        self._scene_list = self.SCENE_LIST
        self._debug_rects = False
        # TODO: make these real objects
        self.resource = object()
        self.sound = Sound(self.resource)

    def initial_state(self):
        """Create a copy of the initial game state."""
        initial_state = state.GameState(self)
        initial_state.set_debug_rects(self._debug_rects)
        for scene in self._scene_list:
            initial_state.load_scenes(scene)
        initial_state.set_current_scene(self._initial_scene)
        initial_state.set_do_enter_leave()
        return initial_state

    def option_parser(self):
        parser = OptionParser()
        parser.add_option("--no-sound", action="store_false", default=True,
                dest="sound", help="disable sound")
        if DEBUG:
            parser.add_option("--scene", type="str", default=None,
                dest="scene", help="initial scene")
            parser.add_option("--no-rects", action="store_false", default=True,
                dest="rects", help="disable debugging rects")
        return parser

    def main(self):
        parser = self.option_parser()
        opts, _ = parser.parse_args(sys.argv)
        pygame.display.init()
        pygame.font.init()
        if opts.sound:
            self.sound.enable_sound()
        else:
            self.sound.disable_sound()
        if DEBUG:
            if opts.scene is not None:
                # debug the specified scene
                self._initial_scene = opts.scene
            self._debug_rects = opts.rects
        display = pygame.display.set_mode(SCREEN, SWSURFACE)
        pygame.display.set_icon(pygame.image.load(
            data.filepath('icons/suspended_sentence24x24.png')))
        pygame.display.set_caption("Suspended Sentence")
        shell = MainShell(display, self.initial_state)
        try:
            shell.run()
        except KeyboardInterrupt:
            pass
