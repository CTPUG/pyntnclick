"""Utilities and base classes for dealing with scenes."""

import copy

from widgets.text import LabelWidget
from pygame.color import Color

from pyntnclick.engine import ScreenEvent
from pyntnclick.tools.utils import draw_rect_image


class Result(object):
    """Result of interacting with a thing"""

    def __init__(self, message=None, soundfile=None, detail_view=None,
                 widget=None, end_game=False):
        self.message = message
        self.soundfile = soundfile
        self.detail_view = detail_view
        self.widget = widget
        self.end_game = end_game

    def play_sound(self, screen):
        if self.soundfile:
            sound = screen.gd.sound.get_sound(self.soundfile)
            sound.play()

    def process(self, screen):
        """Helper function to do the right thing with a result object"""
        self.play_sound(screen)
        if self.widget:
            screen.queue_widget(self.widget)
        if self.message:
            screen.show_message(self.message)
        if self.detail_view:
            screen.game.show_detail(self.detail_view)
        if self.end_game:
            screen.end_game()


class GameState(object):
    """This holds the serializable game state.

       Games wanting to do fancier stuff with the state should
       sub-class this and feed the subclass into
       GameDescription via the custom_data parameter."""

    def __init__(self):
        self._game_state = {'inventories': {'main': []}}

    def __getitem__(self, key):
        return self._game_state[key]

    def get_all_gizmo_data(self, state_key):
        """Get all state for a gizmo - returns a dict"""
        return self[state_key]

    def get_data(self, state_key, data_key):
        """Get a single entry"""
        return self[state_key].get(data_key, None)

    def set_data(self, state_key, data_key, value):
        """Set a single value"""
        self[state_key][data_key] = value

    def initialize_state(self, state_key, initial_data):
        """Initialize a gizmo entry"""
        if state_key not in self._game_state:
            self._game_state[state_key] = {}
            if initial_data:
                # deep copy of INITIAL_DATA allows lists, sets and
                # other mutable types to safely be used in INITIAL_DATA
                self._game_state[state_key].update(copy.deepcopy(initial_data))

    def inventory(self, name='main'):
        return self['inventories'][name]


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
        self.current_inventory = 'main'
        # currently selected tool (item)
        self.tool = None
        # Global game data
        self.data = self.gd.game_state()
        # current scene
        self.current_scene = None
        # debug rects
        self.debug_rects = False

    def inventory(self, name=None):
        if name is None:
            name = self.current_inventory
        return self.data.inventory(name)

    def set_custom_data(self, data_object):
        self.data = data_object

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
        mod = __import__('%s.%s' % (self.gd.SCENE_MODULE, modname),
                         fromlist=[modname])
        for scene_cls in mod.SCENES:
            scene = scene_cls(self)
            self.add_scene(scene)
        if hasattr(mod, 'DETAIL_VIEWS'):
            for scene_cls in mod.DETAIL_VIEWS:
                scene = scene_cls(self)
                self.add_detail_view(scene)

    def change_scene(self, name):
        ScreenEvent.post('game', 'change_scene',
                         {'name': name, 'detail': False})

    def show_detail(self, name):
        ScreenEvent.post('game', 'change_scene',
                         {'name': name, 'detail': True})

    def _update_inventory(self):
        ScreenEvent.post('game', 'inventory', None)

    def add_inventory_item(self, name):
        self.inventory().append(self.items[name])
        self._update_inventory()

    def is_in_inventory(self, name):
        if name in self.items:
            return self.items[name] in self.inventory()
        return False

    def remove_inventory_item(self, name):
        self.inventory().remove(self.items[name])
        # Unselect tool if it's removed
        if self.tool == self.items[name]:
            self.set_tool(None)
        self._update_inventory()

    def replace_inventory_item(self, old_item_name, new_item_name):
        """Try to replace an item in the inventory with a new one"""
        try:
            index = self.inventory().index(self.items[old_item_name])
            self.inventory()[index] = self.items[new_item_name]
            if self.tool == self.items[old_item_name]:
                self.set_tool(self.items[new_item_name])
        except ValueError:
            return False
        self._update_inventory()
        return True

    def set_tool(self, item):
        self.tool = item


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
        self.state.initialize_state(self.state_key, self.INITIAL_DATA)

    def set_data(self, key, value):
        if self.state:
            self.state.set_data(self.state_key, key, value)

    def get_data(self, key):
        if self.state:
            return self.state.get_data(self.state_key, key)


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
        self.current_thing = None
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
        if thing is self.current_thing:
            self.current_thing.leave()
            self.current_thing = None

    def _get_description(self, dest_rect):
        text = (self.current_thing and
                self.current_thing.get_description())
        if text is None:
            return None
        label = LabelWidget((0, 10), self.gd, text)
        label.do_prepare()
        label.rect.left += (dest_rect.width - label.rect.width) / 2
        return label

    def draw_description(self, surface):
        description = self._get_description(surface.get_rect())
        if description is not None:
            description.draw(surface)

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

    def draw(self, surface):
        self.draw_background(surface)
        self.draw_things(surface)

    def interact(self, item, pos):
        """Interact with a particular position.

        Item may be an item in the list of items or None for the hand.

        Returns a Result object to provide feedback to the player.
        """
        if self.current_thing is not None:
            return self.current_thing.interact(item)

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
        if self.current_thing is not None:
            if not self.current_thing.contains(pos):
                self.current_thing.leave()
                self.current_thing = None
        for thing in self.things.itervalues():
            if thing.contains(pos):
                thing.enter(self.game.tool)
                self.current_thing = thing
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
                draw_rect_image(surface, self._interact_hilight_color,
                        self.rect.inflate(1, 1), 1)
            else:
                for rect in self.rect:
                    draw_rect_image(surface, self._interact_hilight_color,
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
