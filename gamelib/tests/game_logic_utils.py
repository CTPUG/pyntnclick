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

    def set_game_data(self, key, value, thing=None):
        gizmo = self.state.current_scene
        if thing is not None:
            gizmo = gizmo.things[thing]
        gizmo.set_data(key, value)

    def assert_game_data(self, key, value, thing=None, scene=None):
        gizmo = self.state.current_scene
        if scene is not None:
            gizmo = self.state.scenes[scene]
        if thing is not None:
            gizmo = gizmo.things[thing]
        self.assertEquals(value, gizmo.get_data(key))

    def assert_inventory_item(self, item, in_inventory=True):
        self.assertEquals(in_inventory, self.state.items[item] in self.state.inventory)

    def assert_scene_thing(self, thing, in_scene=True):
        self.assertEquals(in_scene, thing in self.state.current_scene.things)

    def assert_detail_thing(self, thing, in_detail=True):
        self.assertEquals(in_detail, thing in self.state.current_detail.things)

    def assert_item_exists(self, item, exists=True):
        self.assertEquals(exists, item in self.state.items)

    def assert_current_scene(self, scene):
        self.assertEquals(scene, self.state.current_scene.name)

    def interact_thing(self, thing, item=None):
        item_obj = None
        if item is not None:
            item_obj = self.state.items[item]
        thing_container = self.state.current_detail or self.state.current_scene
        result = thing_container.things[thing].interact(item_obj)
        if result and result.detail_view:
            self.state.set_current_detail(result.detail_view)
        return result

