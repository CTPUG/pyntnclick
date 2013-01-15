import unittest

import pygame.display

import pyntnclick.resources
import pyntnclick.state


class GameLogicTestCase(unittest.TestCase):
    CURRENT_SCENE = None
    GAME_DESCRIPTION_CLASS = None

    def setUp(self):
        # Events require us to initialize the display
        pygame.display.init()
        # Disable alpha conversion which requires a screen
        pyntnclick.resources.Resources.CONVERT_ALPHA = False

        self.game_description = self.GAME_DESCRIPTION_CLASS()
        self.state = self.game_description.initial_state()
        self.state.current_scene = self.state.scenes[self.CURRENT_SCENE]

        # We aren't handling events, monkey patch change_scene
        def change_scene(name):
            self.state.current_scene = self.state.scenes[name]
        self.state.change_scene = change_scene

    def tearDown(self):
        for item in self.state.items.values():
            if isinstance(item, pyntnclick.state.CloneableItem):
                type(item)._counter = 0

    def set_game_data(self, key, value, thing=None):
        gizmo = self.state.current_scene
        if thing is not None:
            gizmo = gizmo.things[thing]
        gizmo.set_data(key, value)

    def assert_game_data(self, key, value, thing=None, scene=None,
            detail=None):
        gizmo = self.state.current_scene
        if scene is not None:
            gizmo = self.state.scenes[scene]
        if detail is not None:
            gizmo = self.state.detail_views[detail]
        if thing is not None:
            gizmo = gizmo.things[thing]
        self.assertEquals(value, gizmo.get_data(key))

    def assert_inventory_item(self, item, in_inventory=True):
        self.assertEquals(in_inventory, self.state.is_in_inventory(item))

    def assert_scene_thing(self, thing, in_scene=True):
        self.assertEquals(in_scene, thing in self.state.current_scene.things)

    def assert_detail_thing(self, thing, in_detail=True):
        return
        self.assertEquals(in_detail, thing in self.state.current_detail.things)

    def assert_item_exists(self, item, exists=True):
        self.assertEquals(exists, item in self.state.items)

    def assert_current_scene(self, scene):
        self.assertEquals(scene, self.state.current_scene.name)

    def handle_result(self, result):
        if result is None:
            return None
        if hasattr(result, 'process'):
            if result.detail_view:
                self.state.show_detail(result.detail_view)
            return result
        return [self.handle_result(r) for r in result]

    def interact_thing(self, thing, item=None, detail=None):
        item_obj = None
        if item is not None:
            self.assert_inventory_item(item)
            item_obj = self.state.items[item]
        thing_container = self.state.current_scene
        if detail is not None:
            thing_container = self.state.detail_views[detail]
        result = thing_container.things[thing].interact(item_obj)
        return self.handle_result(result)

    def interact_item(self, target_item, item):
        self.assert_inventory_item(target_item)
        item_obj = self.state.items[item]
        target_obj = self.state.items[target_item]
        result = target_obj.interact(item_obj)
        return self.handle_result(result)
