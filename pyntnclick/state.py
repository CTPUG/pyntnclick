"""Utilities and base classes for dealing with scenes."""
from __future__ import division

import os
import json
import copy

from collections import OrderedDict

from pygame.color import Color

from .engine import ScreenEvent
from .utils import draw_rect_image
from .widgets.text import LabelWidget


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

    def __init__(self, state_dict=None):
        if state_dict is None:
            state_dict = {
                'inventories': {'main': []},
                'item_factories': {},
                'current_scene': None,
                }
        self._game_state = copy.deepcopy(state_dict)

    def __getitem__(self, key):
        return self._game_state[key]

    def __contains__(self, key):
        return key in self._game_state

    def export_data(self):
        return copy.deepcopy(self._game_state)

    def get_data(self, state_key, data_key):
        """Get a single entry"""
        return self[state_key].get(data_key, None)

    def set_data(self, state_key, data_key, value):
        """Set a single value"""
        self[state_key][data_key] = value

    def _initialize_state(self, state_dict, state_key, initial_data):
        if state_key not in self._game_state:
            state_dict[state_key] = copy.deepcopy(initial_data)

    def initialize_state(self, state_key, initial_data):
        """Initialize a gizmo entry"""
        self._initialize_state(self._game_state, state_key, initial_data)

    def initialize_item_factory_state(self, state_key, initial_data):
        """Initialize an item factory entry"""
        self._initialize_state(
            self._game_state['item_factories'], state_key, initial_data)

    def inventory(self, name='main'):
        return self['inventories'][name]

    def set_current_scene(self, scene_name):
        self._game_state['current_scene'] = scene_name

    @classmethod
    def get_save_fn(cls, save_dir, save_name):
        return os.path.join(save_dir, '%s.json' % (save_name,))

    @classmethod
    def load_game(cls, save_dir, save_name):
        fn = cls.get_save_fn(save_dir, save_name)
        if os.access(fn, os.R_OK):
            f = open(fn, 'r')
            state = json.load(f)
            f.close()
            return state

    def save_game(self, save_dir, save_name):
        fn = self.get_save_fn(save_dir, save_name)
        if not os.path.isdir(save_dir):
            os.makedirs(save_dir)
        f = open(fn, 'w')
        json.dump(self.export_data(), f)
        f.close()


class Game(object):
    """Complete game state.

    Game state consists of:

    * items
    * scenes
    """
    def __init__(self, gd, game_state):
        # game description
        self.gd = gd
        # map of scene name -> Scene object
        self.scenes = {}
        # map of detail view name -> DetailView object
        self.detail_views = {}
        # map of item prefix -> ItemFactory object
        self.item_factories = {}
        # list of item objects in inventory
        self.current_inventory = 'main'
        # currently selected tool (item)
        self.tool = None
        # Global game data
        self.data = game_state
        # debug rects
        self.debug_rects = False

    def get_current_scene(self):
        scene_name = self.data['current_scene']
        if scene_name is not None:
            return self.scenes[scene_name]
        return None

    def get_item(self, item_name):
        base_name, _, _suffix = item_name.partition(':')
        factory = self.item_factories[base_name]
        return factory.get_item(item_name)

    def create_item(self, base_name):
        assert ":" not in base_name
        factory = self.item_factories[base_name]
        return factory.create_item()

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

    def add_item_factory(self, item_class):
        name = item_class.NAME
        assert name not in self.item_factories, (
           "Factory for %s already added." % (name,))
        factory = item_class.ITEM_FACTORY(item_class)
        factory.set_game(self)
        self.item_factories[name] = factory

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

    def add_inventory_item(self, item_name):
        item = self.create_item(item_name)
        self.inventory().append(item.name)
        self._update_inventory()

    def is_in_inventory(self, name):
        return name in self.inventory()

    def remove_inventory_item(self, name):
        self.inventory().remove(name)
        # Unselect tool if it's removed
        if self.tool == self.get_item(name):
            self.set_tool(None)
        self._update_inventory()

    def replace_inventory_item(self, old_item_name, new_item_name):
        """Try to replace an item in the inventory with a new one"""
        try:
            index = self.inventory().index(old_item_name)
            new_item = self.create_item(new_item_name)
            self.inventory()[index] = new_item.name
            if self.tool == self.get_item(old_item_name):
                self.set_tool(new_item)
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
        self.set_state(self.game.data)
        self.setup()

    def set_state(self, state):
        """Hack to allow set_state() to be called before setup()."""
        pass

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
        if self.state_key is None:
            assert self.INITIAL_DATA is None, (
                "Can't provide self.INITIAL_DATA without self.state_key.")
        if self.INITIAL_DATA is not None:
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
        # We use an OrderedDict, so we can control the order we compare
        # objects for interact checks
        # FIXME: We should replace this some system of priority or layers,
        # since relying just on the order of objects is fragile and not
        # very flexible.
        self.things = OrderedDict()
        self.current_thing = None
        self._background = None

    def add_item_factory(self, item_factory):
        self.game.add_item_factory(item_factory)

    def add_thing(self, thing):
        thing.set_game(self.game)
        if not thing.should_add():
            return
        self.things[thing.name] = thing
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
        # TODO: Centre more cleanly
        label.rect.left += (dest_rect.width - label.rect.width) // 2
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
        for thing in self.things.values():
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
        for thing in self.things.values():
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
        for thing in self.things.values():
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

    def set_state(self, state):
        return super(Scene, self).set_state(state)


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

    def should_add(self):
        return True

    def set_scene(self, scene):
        assert self.scene is None
        self.scene = scene
        if self.folder is None:
            self.folder = scene.FOLDER
        self.game = scene.game
        for interact in self.interacts.values():
            interact.set_thing(self)
        self.set_interact()

    def set_interact(self):
        return self._set_interact(self.select_interact())

    def _set_interact(self, name):
        self.current_interact = self.interacts[name]
        self.rect = self.current_interact.interact_rect
        if self.scene:
            self._fix_rect()
        assert self.rect is not None, name

    def select_interact(self):
        return self.INITIAL

    def contains(self, pos):
        if hasattr(self.rect, 'collidepoint'):
            return self.rect.collidepoint(pos)
        else:
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
        """Called when the cursor leaves the Thing."""
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
                draw_rect_image(
                    surface, self._interact_hilight_color,
                    self.rect.inflate(1, 1), 1)
            else:
                for rect in self.rect:
                    draw_rect_image(
                        surface, self._interact_hilight_color,
                        rect.inflate(1, 1), 1)


class ItemFactory(StatefulGizmo):
    INITIAL_DATA = {
        'created': [],
        }

    def __init__(self, item_class):
        super(ItemFactory, self).__init__()
        self.item_class = item_class
        assert self.item_class.NAME is not None, (
            "%s has no NAME set" % (self.item_class,))
        self.state_key = self.item_class.NAME + '_factory'
        self.items = {}

    def get_item(self, item_name):
        assert item_name in self.get_data('created'), (
            "Object %s has not been created" % (item_name,))
        if item_name not in self.items:
            item = self.item_class(item_name)
            item.set_game(self.game)
            self.items[item_name] = item
        return self.items[item_name]

    def get_item_suffix(self):
        return ''

    def create_item(self):
        item_name = '%s:%s' % (self.item_class.NAME, self.get_item_suffix())
        created_list = self.get_data('created')
        assert item_name not in created_list, (
            "Already created object %s" % (item_name,))
        created_list.append(item_name)
        self.set_data('created', created_list)
        return self.get_item(item_name)


class Item(GameDeveloperGizmo, InteractiveMixin):
    """Base class for inventory items."""

    # image for inventory
    INVENTORY_IMAGE = None

    # Base name of item
    NAME = None

    # name for interactions (i.e. def interact_with_<TOOL_NAME>)
    TOOL_NAME = None

    # set to instance of CursorSprite
    CURSOR = None

    ITEM_FACTORY = ItemFactory

    def __init__(self, name=None):
        GameDeveloperGizmo.__init__(self)
        self.name = self.NAME
        if name is not None:
            self.name = name
        self.tool_name = self.NAME
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


class ClonableItemFactory(ItemFactory):
    def get_item_suffix(self):
        # Works as long as we never remove anything from our 'created' list.
        count = len(self.get_data('created'))
        assert self.item_class.MAX_COUNT is not None
        assert count <= self.item_class.MAX_COUNT
        return str(count)


class CloneableItem(Item):
    ITEM_FACTORY = ClonableItemFactory
    MAX_COUNT = None
