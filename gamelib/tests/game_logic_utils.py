import unittest

import pygame
from pygame.locals import SWSURFACE

from gamelib import state
from gamelib.constants import SCREEN


# We need this stuff set up so we can load images and whatnot.
pygame.display.init()
pygame.font.init()
pygame.display.set_mode(SCREEN, SWSURFACE)


class GameLogicTestCase(unittest.TestCase):
    CURRENT_SCENE = None

    def setUp(self):
        self.state = state.initial_state()
        self.state.set_current_scene(self.CURRENT_SCENE)

    def tearDown(self):
        for item in self.state.items.values():
            if isinstance(item, state.CloneableItem):
                type(item)._counter = 0

    def set_game_data(self, key, value, thing=None):
        gizmo = self.state.current_scene
        if thing is not None:
            gizmo = gizmo.things[thing]
        gizmo.set_data(key, value)

    def assert_game_data(self, key, value, thing=None, scene=None):
        gizmo = self.state.current_scene
        if self.state.current_detail is not None:
            gizmo = self.state.current_detail
        if scene is not None:
            gizmo = self.state.scenes[scene]
        if thing is not None:
            gizmo = gizmo.things[thing]
        self.assertEquals(value, gizmo.get_data(key))

    def assert_inventory_item(self, item, in_inventory=True):
        self.assertEquals(in_inventory, self.state.is_in_inventory(item))

    def assert_scene_thing(self, thing, in_scene=True):
        self.assertEquals(in_scene, thing in self.state.current_scene.things)

    def assert_detail_thing(self, thing, in_detail=True):
        self.assertEquals(in_detail, thing in self.state.current_detail.things)

    def assert_item_exists(self, item, exists=True):
        self.assertEquals(exists, item in self.state.items)

    def assert_current_scene(self, scene):
        self.assertEquals(scene, self.state.current_scene.name)

    def assert_current_detail(self, scene):
        self.assertEquals(scene, self.state.current_detail.name)

    def handle_result(self, result):
        if result is None:
            return None
        if hasattr(result, 'process'):
            if result.detail_view:
                self.state.set_current_detail(result.detail_view)
            return result
        return [self.handle_result(r) for r in result]

    def interact_thing(self, thing, item=None):
        item_obj = None
        if item is not None:
            self.assert_inventory_item(item)
            item_obj = self.state.items[item]
        thing_container = self.state.current_detail or self.state.current_scene
        result = thing_container.things[thing].interact(item_obj)
        return self.handle_result(result)

    def interact_item(self, target_item, item):
        self.assert_inventory_item(target_item)
        item_obj = self.state.items[item]
        target_obj = self.state.items[target_item]
        result = target_obj.interact(item_obj, self.state)
        return self.handle_result(result)

    def close_detail(self):
        self.state.set_current_detail(None)

