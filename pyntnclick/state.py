"""Utilities and base classes for dealing with scenes."""

import copy

from albow.utils import frame_rect
from widgets import BoomLabel
from pygame.rect import Rect
from pygame.color import Color


class Result(object):
    """Result of interacting with a thing"""

    def __init__(self, message=None, soundfile=None, detail_view=None,
                 style=None, close_detail=False, end_game=False):
        self.message = message
        self.soundfile = soundfile
        self.detail_view = detail_view
        self.style = style
        self.close_detail = close_detail
        self.end_game = end_game

    def play_sound(self, scene_widget):
        if self.soundfile:
            sound = scene_widget.game.gd.sound.get_sound(self.soundfile)
            sound.play()

    def process(self, scene_widget):
        """Helper function to do the right thing with a result object"""
        self.play_sound(scene_widget)
        if self.message:
            scene_widget.show_message(self.message, self.style)
        if self.detail_view:
            scene_widget.show_detail(self.detail_view)
        if (self.close_detail
            and hasattr(scene_widget, 'parent')
            and hasattr(scene_widget.parent, 'clear_detail')):
            scene_widget.parent.clear_detail()
        if self.end_game:
            scene_widget.end_game()


def handle_result(result, scene_widget):
    """Handle dealing with result or result sequences"""
    if result:
        if hasattr(result, 'process'):
            result.process(scene_widget)
        else:
            for res in result:
                if res:
                    # List may contain None's
                    res.process(scene_widget)


class Game(object):
    """Complete game state.

    Game state consists of:

    * items
    * scenes
    """
    def __init__(self, gd):
        # game description
        self.gd = gd
        # map of scene name -> Scene object
        self.scenes = {}
        # map of detail view name -> DetailView object
        self.detail_views = {}
        # map of item name -> Item object
        self.items = {}
        # list of item objects in inventory
        self.inventory = []
        # currently selected tool (item)
        self.tool = None
        # Global game data
        self.data = {}
        # current scene
        self.current_scene = None
        # current detail view
        self.current_detail = None
        # scene we came from, for enter and leave processing
        self.previous_scene = None
        # scene transion helpers
        self.do_check = None
        self.old_pos = None
        # current thing
        self.current_thing = None
        self.highlight_override = False
        # debug rects
        self.debug_rects = False

    def set_debug_rects(self, value=True):
        self.debug_rects = value

    def add_scene(self, scene):
        scene.set_game(self)
        self.scenes[scene.name] = scene

    def add_detail_view(self, detail_view):
        detail_view.set_game(self)
        self.detail_views[detail_view.name] = detail_view

    def add_item(self, item):
        item.set_game(self)
        self.items[item.name] = item

    def load_scenes(self, modname):
        mod = __import__("gamelib.scenes.%s" % (modname,), fromlist=[modname])
        for scene_cls in mod.SCENES:
            scene = scene_cls(self)
            self.add_scene(scene)
        if hasattr(mod, 'DETAIL_VIEWS'):
            for scene_cls in mod.DETAIL_VIEWS:
                scene = scene_cls(self)
                self.add_detail_view(scene)

    def set_current_scene(self, name):
        old_scene = self.current_scene
        self.current_scene = self.scenes[name]
        self.current_thing = None
        if old_scene and old_scene != self.current_scene:
            self.previous_scene = old_scene
            self.set_do_enter_leave()

    def set_current_detail(self, name):
        self.current_thing = None
        if name is None:
            self.current_detail = None
        else:
            self.current_detail = self.detail_views[name]
            return self.current_detail

    def add_inventory_item(self, name):
        self.inventory.append(self.items[name])

    def is_in_inventory(self, name):
        if name in self.items:
            return self.items[name] in self.inventory
        return False

    def remove_inventory_item(self, name):
        self.inventory.remove(self.items[name])
        # Unselect tool if it's removed
        if self.tool == self.items[name]:
            self.set_tool(None)

    def replace_inventory_item(self, old_item_name, new_item_name):
        """Try to replace an item in the inventory with a new one"""
        try:
            index = self.inventory.index(self.items[old_item_name])
            self.inventory[index] = self.items[new_item_name]
            if self.tool == self.items[old_item_name]:
                self.set_tool(self.items[new_item_name])
        except ValueError:
            return False
        return True

    def set_tool(self, item):
        self.tool = item

    def interact(self, pos):
        return self.current_scene.interact(self.tool, pos)

    def interact_detail(self, pos):
        return self.current_detail.interact(self.tool, pos)

    def cancel_doodah(self, screen):
        if self.tool:
            self.set_tool(None)
        elif self.current_detail:
            screen.state_widget.clear_detail()

    def do_enter_detail(self):
        if self.current_detail:
            self.current_detail.enter()

    def do_leave_detail(self):
        if self.current_detail:
            self.current_detail.leave()

    def animate(self):
        if not self.do_check:
            return self.current_scene.animate()

    def check_enter_leave(self, screen):
        if not self.do_check:
            return None
        if self.do_check == self.gd.constants.leave:
            self.do_check = self.gd.constants.enter
            if self.previous_scene:
                return self.previous_scene.leave()
            return None
        elif self.do_check == self.gd.constants.enter:
            self.do_check = None
            # Fix descriptions, etc.
            if self.old_pos:
                self.current_scene.update_current_thing(self.old_pos)
            return self.current_scene.enter()
        raise RuntimeError('invalid do_check value %s' % self.do_check)

    def set_do_enter_leave(self):
        """Flag that we need to run the enter loop"""
        self.do_check = self.gd.constants.leave


class GameDeveloperGizmo(object):
    """Base class for objects game developers see."""

    def __init__(self):
        """Set """
        self.game = None
        self.gd = None
        self.resource = None
        self.sound = None

    def set_game(self, game):
        self.game = game
        self.gd = game.gd
        self.resource = self.gd.resource
        self.sound = self.gd.sound
        self.setup()

    def setup(self):
        """Game developers should override this to do their setup.

        It will be called after all the useful state functions have been
        set.
        """
        pass


class StatefulGizmo(GameDeveloperGizmo):

    # initial data (optional, defaults to none)
    INITIAL_DATA = None
    STATE_KEY = None

    def __init__(self):
        GameDeveloperGizmo.__init__(self)
        self.state_key = self.STATE_KEY
        self.state = None  # set this with set_state if required

    def set_state(self, state):
        """Set the state object and initialize if needed"""
        self.state = state
        if self.state_key not in self.state:
            self.state[self.state_key] = {}
            if self.INITIAL_DATA:
                # deep copy of INITIAL_DATA allows lists, sets and
                # other mutable types to safely be used in INITIAL_DATA
                self.state[self.state_key].update(
                        copy.deepcopy(self.INITIAL_DATA))

    def set_data(self, key, value):
        if self.state:
            self.state[self.state_key][key] = value

    def get_data(self, key):
        if self.state:
            return self.state[self.state_key].get(key, None)


class Scene(StatefulGizmo):
    """Base class for scenes."""

    # sub-folder to look for resources in
    FOLDER = None

    # name of background image resource
    BACKGROUND = None

    # name of scene (optional, defaults to folder)
    NAME = None

    # Offset of the background image
    OFFSET = (0, 0)

    def __init__(self, state):
        StatefulGizmo.__init__(self)
        # scene name
        self.name = self.NAME if self.NAME is not None else self.FOLDER
        self.state_key = self.name
        # map of thing names -> Thing objects
        self.things = {}
        self._background = None

    def set_game(self, game):
        super(Scene, self).set_game(game)
        self.set_state(game.data)

    def add_item(self, item):
        self.game.add_item(item)

    def add_thing(self, thing):
        self.things[thing.name] = thing
        thing.set_game(self.game)
        thing.set_scene(self)

    def remove_thing(self, thing):
        del self.things[thing.name]
        if thing is self.game.current_thing:
            self.game.current_thing.leave()
            self.game.current_thing = None

    def _get_description(self):
        text = (self.game.current_thing and
                self.game.current_thing.get_description())
        if text is None:
            return None
        label = BoomLabel(text)
        label.set_margin(5)
        label.border_width = 1
        label.border_color = (0, 0, 0)
        label.bg_color = Color(210, 210, 210, 255)
        label.fg_color = (0, 0, 0)
        return label

    def draw_description(self, surface, screen):
        description = self._get_description()
        if description is not None:
            w, h = description.size
            sub = screen.get_root().surface.subsurface(
                Rect(400 - w / 2, 5, w, h))
            description.draw_all(sub)

    def _cache_background(self):
        if self.BACKGROUND and not self._background:
            self._background = self.resource.get_image(
                self.FOLDER, self.BACKGROUND)

    def draw_background(self, surface):
        self._cache_background()
        if self._background is not None:
            surface.blit(self._background, self.OFFSET, None)
        else:
            surface.fill((200, 200, 200))

    def draw_things(self, surface):
        for thing in self.things.itervalues():
            thing.draw(surface)

    def draw(self, surface, screen):
        self.draw_background(surface)
        self.draw_things(surface)
        self.draw_description(surface, screen)

    def interact(self, item, pos):
        """Interact with a particular position.

        Item may be an item in the list of items or None for the hand.

        Returns a Result object to provide feedback to the player.
        """
        if self.game.current_thing is not None:
            return self.game.current_thing.interact(item)

    def animate(self):
        """Animate all the things in the scene.

           Return true if any of them need to queue a redraw"""
        result = False
        for thing in self.things.itervalues():
            if thing.animate():
                result = True
        return result

    def enter(self):
        return None

    def leave(self):
        return None

    def update_current_thing(self, pos):
        if self.game.current_thing is not None:
            if not self.game.current_thing.contains(pos):
                self.game.current_thing.leave()
                self.game.current_thing = None
        for thing in self.things.itervalues():
            if thing.contains(pos):
                thing.enter(self.game.tool)
                self.game.current_thing = thing
                break

    def mouse_move(self, pos):
        """Call to check whether the cursor has entered / exited a thing.

        Item may be an item in the list of items or None for the hand.
        """
        self.update_current_thing(pos)

    def get_detail_size(self):
        self._cache_background()
        return self._background.get_size()

    def get_image(self, *image_name_fragments, **kw):
        return self.resource.get_image(*image_name_fragments, **kw)


class InteractiveMixin(object):
    def is_interactive(self, tool=None):
        return True

    def interact(self, tool):
        if not self.is_interactive(tool):
            return None
        if tool is None:
            return self.interact_without()
        handler = getattr(self, 'interact_with_' + tool.tool_name, None)
        inverse_handler = self.get_inverse_interact(tool)
        if handler is not None:
            return handler(tool)
        elif inverse_handler is not None:
            return inverse_handler(self)
        else:
            return self.interact_default(tool)

    def get_inverse_interact(self, tool):
        return None

    def interact_without(self):
        return self.interact_default(None)

    def interact_default(self, item=None):
        return None


class Thing(StatefulGizmo, InteractiveMixin):
    """Base class for things in a scene that you can interact with."""

    # name of thing
    NAME = None

    # sub-folder to look for resources in (defaults to scenes folder)
    FOLDER = None

    # list of Interact objects
    INTERACTS = {}

    # name first interact
    INITIAL = None

    # Interact rectangle hi-light color (for debugging)
    # (set to None to turn off)
    _interact_hilight_color = Color('red')

    def __init__(self):
        StatefulGizmo.__init__(self)
        # name of the thing
        self.name = self.NAME
        # folder for resource (None is overridden by scene folder)
        self.folder = self.FOLDER
        self.state_key = self.NAME
        # interacts
        self.interacts = self.INTERACTS
        # these are set by set_scene
        self.scene = None
        self.current_interact = None
        self.rect = None
        self.orig_rect = None

    def _fix_rect(self):
        """Fix rects to compensate for scene offset"""
        # Offset logic is to always work with copies, to avoid
        # flying effects from multiple calls to _fix_rect
        # See footwork in draw
        if hasattr(self.rect, 'collidepoint'):
            self.rect = self.rect.move(self.scene.OFFSET)
        else:
            self.rect = [x.move(self.scene.OFFSET) for x in self.rect]

    def set_scene(self, scene):
        assert self.scene is None
        self.scene = scene
        if self.folder is None:
            self.folder = scene.FOLDER
        self.game = scene.game
        self.set_state(self.game.data)
        for interact in self.interacts.itervalues():
            interact.set_thing(self)
        self.set_interact(self.INITIAL)

    def set_interact(self, name):
        self.current_interact = self.interacts[name]
        self.rect = self.current_interact.interact_rect
        if self.scene:
            self._fix_rect()
        assert self.rect is not None, name

    def contains(self, pos):
        if hasattr(self.rect, 'collidepoint'):
            return self.rect.collidepoint(pos)
        else:
            # FIXME: add sanity check
            for rect in list(self.rect):
                if rect.collidepoint(pos):
                    return True
        return False

    def get_description(self):
        return None

    def enter(self, item):
        """Called when the cursor enters the Thing."""
        pass

    def leave(self):
        """Called when the cursr leaves the Thing."""
        pass

    def animate(self):
        return self.current_interact.animate()

    def draw(self, surface):
        old_rect = self.current_interact.rect
        if old_rect:
            self.current_interact.rect = old_rect.move(self.scene.OFFSET)
        self.current_interact.draw(surface)
        self.current_interact.rect = old_rect
        if self.game.debug_rects and self._interact_hilight_color:
            if hasattr(self.rect, 'collidepoint'):
                frame_rect(surface, self._interact_hilight_color,
                        self.rect.inflate(1, 1), 1)
            else:
                for rect in self.rect:
                    frame_rect(surface, self._interact_hilight_color,
                            rect.inflate(1, 1), 1)


class Item(GameDeveloperGizmo, InteractiveMixin):
    """Base class for inventory items."""

    # image for inventory
    INVENTORY_IMAGE = None

    # name of item
    NAME = None

    # name for interactions (i.e. def interact_with_<TOOL_NAME>)
    TOOL_NAME = None

    # set to instance of CursorSprite
    CURSOR = None

    def __init__(self, name=None):
        GameDeveloperGizmo.__init__(self)
        self.name = self.NAME
        if name is not None:
            self.name = name
        self.tool_name = name
        if self.TOOL_NAME is not None:
            self.tool_name = self.TOOL_NAME
        self.inventory_image = None

    def _cache_inventory_image(self):
        if not self.inventory_image:
            self.inventory_image = self.resource.get_image(
                    'items', self.INVENTORY_IMAGE)

    def get_inventory_image(self):
        self._cache_inventory_image()
        return self.inventory_image

    def get_inverse_interact(self, tool):
        return getattr(tool, 'interact_with_' + self.tool_name, None)

    def is_interactive(self, tool=None):
        if tool:
            return True
        return False


class CloneableItem(Item):
    _counter = 0

    @classmethod
    def _get_new_id(cls):
        cls._counter += 1
        return cls._counter - 1

    def __init__(self, name=None):
        super(CloneableItem, self).__init__(name)
        my_count = self._get_new_id()
        self.name = "%s.%s" % (self.name, my_count)
