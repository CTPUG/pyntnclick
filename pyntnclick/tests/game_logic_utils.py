import unittest

import pygame.display
import pygame.event

from .. import resources


class GameLogicTestCase(unittest.TestCase):
    CURRENT_SCENE = None
    GAME_DESCRIPTION_CLASS = None

    def setUp(self):
        # Events require us to initialize the display
        pygame.display.init()
        # Disable alpha conversion which requires a screen
        resources.Resources.CONVERT_ALPHA = False

        self.game_description = self.GAME_DESCRIPTION_CLASS()
        self.state = self.game_description.initial_state()
        self.scene_stack = []

        # We aren't handling events, monkey patch change_scene and show_detail
        def change_scene(name):
            self.state.data.set_current_scene(name)
            self.scene_stack = [self.state.get_current_scene()]
        self.state.change_scene = change_scene

        def show_detail(name):
            self.scene_stack.append(self.state.detail_views[name])
        self.state.show_detail = show_detail

        self.state.change_scene(self.CURRENT_SCENE)

    def close_detail(self):
        self.scene_stack.pop()
        self.assertTrue(len(self.scene_stack) > 0)

    def clear_event_queue(self):
        # Since we aren't handling events, we may overflow the pygame
        # event buffer if we're generating a lot of events
        pygame.event.clear()

    def clear_inventory(self):
        # Remove all items from the inventory, ensuring tool is set to None
        self.state.set_tool(None)
        self.state.inventory()[:] = []

    def set_game_data(self, key, value, thing=None):
        gizmo = self.state.get_current_scene()
        if thing is not None:
            gizmo = gizmo.things[thing]
        gizmo.set_data(key, value)

    def assert_game_data(
            self, key, value, thing=None, scene=None, detail=None):
        gizmo = self.state.get_current_scene()
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
        self.assertEquals(
            in_scene, thing in self.state.get_current_scene().things)

    def assert_detail_thing(self, thing, in_detail=True):
        self.assertEquals(in_detail, thing in self.scene_stack[-1].things)

    def assert_item_exists(self, item, exists=True):
        try:
            self.state.get_item(item)
            self.assertTrue(exists)
        except Exception:
            self.assertFalse(exists)

    def assert_current_scene(self, scene):
        self.assertEquals(scene, self.state.get_current_scene().name)

    def handle_result(self, result):
        self.clear_event_queue()
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
            item_obj = self.state.get_item(item)
        thing_container = self.scene_stack[-1]
        if detail is not None:
            self.assertEqual(detail, thing_container.name)
        result = thing_container.things[thing].interact(item_obj)
        return self.handle_result(result)

    def interact_item(self, target_item, item):
        self.assert_inventory_item(target_item)
        item_obj = self.state.get_item(item)
        target_obj = self.state.get_item(target_item)
        result = target_obj.interact(item_obj)
        return self.handle_result(result)
