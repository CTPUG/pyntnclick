'''Game main module.

Contains the entry point used by the run_game.py script.

'''
from __future__ import print_function

import sys
import gettext
import locale
import os
from optparse import OptionParser

import pygame
from pygame.locals import SWSURFACE

from .i18n import _, get_module_i18n_path
from .engine import Engine
from .gamescreen import DefMenuScreen, DefEndScreen, GameScreen
from .constants import GameConstants, DEBUG_ENVVAR
from .resources import Resources
from .sound import Sound
from . import state

from .tools.rect_drawer import (
    RectEngine, RectDrawerError, make_rect_display)
from .utils import list_scenes


class GameDescriptionError(Exception):
    """Raised when an GameDescription is invalid."""


class GameDescription(object):

    # initial scene for start of game (unless overridden by debug)
    INITIAL_SCENE = None

    # list of game scenes
    SCENE_LIST = None

    # starting menu
    SCREENS = {
        'menu': DefMenuScreen,
        'end': DefEndScreen,
        }

    START_SCREEN = 'menu'

    # Modules
    RESOURCE_MODULE = 'data'
    SCENE_MODULE = 'gamelib.scenes'

    def __init__(self):
        if self.INITIAL_SCENE is None:
            raise GameDescriptionError("A game must have an initial scene.")
        if not self.SCENE_LIST:
            raise GameDescriptionError("A game must have a non-empty list"
                                       " of scenes.")
        if 'game' in self.SCREENS:
            raise GameDescriptionError("The 'game' screen is reserved for the"
                                       " game itself.")
        self._initial_scene = self.INITIAL_SCENE
        self._scene_list = self.SCENE_LIST
        self._resource_module = self.RESOURCE_MODULE
        self._debug_rects = False
        self._screens = self.SCREENS.copy()
        self._screens['game'] = GameScreen
        self.constants = self.game_constants()

        locale.setlocale(locale.LC_ALL, "")
        lang = locale.getdefaultlocale(['LANGUAGE', 'LC_ALL', 'LC_CTYPE',
                                        'LANG'])[0]
        self.resource = Resources(self._resource_module, lang)
        locale_path = self.resource.get_resource_path('locale')
        gettext.bindtextdomain(self.constants.short_name, locale_path)
        gettext.textdomain(self.constants.short_name)

        popath = self.resource.get_resource_path('po')
        self._check_translations(popath, locale_path)

        self.sound = Sound(self.resource)
        self.debug_options = []
        self.running = False

    def _check_translations(self, popath, locale_path):
        """Check for outdated mo files"""
        name = gettext.textdomain()  # only check the current app
        for candidate in os.listdir(popath):
            if candidate.endswith('.po'):
                polang = candidate.split('.', 1)[0]
                pofile = os.path.join(popath, candidate)
                mofile = gettext.find(name, locale_path, (polang,))
                if mofile is None:
                    print('Missing mo file for %s' % pofile)
                    continue
                if os.stat(pofile).st_mtime > os.stat(mofile).st_mtime:
                    print('po file %s is newer than mo file %s'
                          % (pofile, mofile))

    def initial_state(self, game_state=None):
        """Create a copy of the initial game state."""
        initial_state = state.Game(self, self.game_state_class()(game_state))
        initial_state.set_debug_rects(self._debug_rects)
        for scene in self._scene_list:
            initial_state.load_scenes(scene)
        if initial_state.data['current_scene'] is None:
            initial_state.data.set_current_scene(self._initial_scene)
        initial_state.change_scene(initial_state.data['current_scene'])
        return initial_state

    def game_state_class(self):
        return state.GameState

    def game_constants(self):
        return GameConstants()

    def option_parser(self):
        parser = OptionParser()
        parser.add_option(
            "--no-sound", action="store_false", default=True,
            dest="sound", help="disable sound")
        # We flag these, so we can warn the user that these require debug mode
        self.debug_options = [
            '--scene', '--no-rects', '--rect-drawer',
            '--list-scenes', '--details']
        if self.constants.debug:
            parser.add_option(
                "--scene", type="str", default=None,
                dest="scene", help="initial scene")
            parser.add_option(
                "--no-rects", action="store_false", default=True,
                dest="rects", help="disable debugging rects")
            parser.add_option(
                "--rect-drawer", action="store_true",
                default=False, dest="rect_drawer",
                help=(
                    "Launch the rect drawing helper tool. Specify the"
                    " scene with --scene"))
            parser.add_option(
                "--list-scenes", action="store_true",
                default=False, dest='list_scenes',
                help="List all scenes that can be used with --scene and exit.")
            parser.add_option(
                "--detail", type="str", default=None,
                dest="detail", help="Detailed view for rect_drawer")
        return parser

    def warn_debug(self, option):
        """Warn the user that he needs debug mode"""
        print('%s is only valid in debug mode' % option)
        print('set %s to enable debug mode' % DEBUG_ENVVAR)
        print

    def main(self):
        parser = self.option_parser()
        # This is a bit hack'ish, but works
        if not self.constants.debug:
            for option in self.debug_options:
                if option in sys.argv:
                    self.warn_debug(option)
        opts, args = parser.parse_args(sys.argv)
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
            list_scenes(self.SCENE_MODULE, self._scene_list)
            sys.exit(0)
        if self.constants.debug and opts.rect_drawer:
            if opts.scene is None:
                print('Need to supply a scene to use the rect drawer')
                sys.exit(1)
            locale_path = get_module_i18n_path(
                    self.resource.DEFAULT_RESOURCE_MODULE)
            gettext.bindtextdomain('pyntnclick-tools', locale_path)
            gettext.textdomain('pyntnclick-tools')
            popath = get_module_i18n_path(
                    self.resource.DEFAULT_RESOURCE_MODULE, 'po')
            self._check_translations(popath, locale_path)
            make_rect_display()
            try:
                self.engine = RectEngine(self, opts.detail)
            except RectDrawerError as e:
                print('RectDrawer failed with: %s' % e)
                sys.exit(1)
        else:
            pygame.display.set_mode(self.constants.screen, SWSURFACE)
            if self.constants.icon:
                pygame.display.set_icon(self.resource.get_image(
                    self.constants.icon, basedir='icons'))
            if self.constants.title:
                title = _(self.constants.title)
                if sys.version_info.major == 2:
                    title = title.encode('utf-8')
                pygame.display.set_caption(title)

            self.engine = Engine(self)
            # Initialize the special screens in the engine
            for name, cls in self._screens.items():
                screen = cls(self)
                self.engine.add_screen(name, screen)
            # Should we allow the menu not to be the opening screen?
            self.engine.set_screen(self.START_SCREEN)
        try:
            self.engine.run()
        except KeyboardInterrupt:
            pass

    def get_default_save_location(self):
        """Return a default save game location."""
        app = self.constants.short_name
        if sys.platform.startswith("win"):
            if "APPDATA" in os.environ:
                return os.path.join(os.environ["APPDATA"], app)
            return os.path.join(os.path.expanduser("~"), "." + app)
        elif 'XDG_DATA_HOME' in os.environ:
            return os.path.join(os.environ["XDG_DATA_HOME"], app)
        return os.path.join(os.path.expanduser("~"), ".local", "share", app)
