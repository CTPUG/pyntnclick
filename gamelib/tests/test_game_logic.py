import unittest

import pygame

from gamelib import state

from pygame.locals import SWSURFACE
from gamelib.constants import SCREEN


# We need this stuff set up so we can load images and whatnot.
pygame.display.init()
pygame.display.set_mode(SCREEN, SWSURFACE)


class TestGameLogic(unittest.TestCase):
    def setUp(self):
        self.state = state.initial_state()

    def set_game_data(self, key, value, scene, thing=None):
        gizmo = self.state.scenes[scene]
        if thing is not None:
            gizmo = gizmo.things[thing]
        gizmo.set_data(key, value)

    def assert_game_data(self, key, value, scene, thing=None):
        gizmo = self.state.scenes[scene]
        if thing is not None:
            gizmo = gizmo.things[thing]
        self.assertEquals(value, gizmo.get_data(key))

    def interact_thing(self, scene_name, thing_name, item_name=None):
        item = None
        if item_name is not None:
            item = self.state.items[item_name]
        self.state.scenes[scene_name].things[thing_name].interact(item)

    def test_cryo_door_closed_hand(self):
        "The door is closed and we touch it with the hand. No change."

        self.assert_game_data('accessible', True, 'cryo')
        self.assert_game_data('accessible', False, 'bridge')
        self.assert_game_data('open', False, 'cryo', 'cryo.door')

        self.interact_thing('cryo', 'cryo.door')

        self.assert_game_data('accessible', True, 'cryo')
        self.assert_game_data('accessible', False, 'bridge')
        self.assert_game_data('open', False, 'cryo', 'cryo.door')

    def test_cryo_door_closed_titanium_leg(self):
        "The door is closed and we touch it with the titanium leg. It opens."

        self.assert_game_data('accessible', True, 'cryo')
        self.assert_game_data('accessible', False, 'bridge')
        self.assert_game_data('open', False, 'cryo', 'cryo.door')

        self.interact_thing('cryo', 'cryo.door', 'titanium_leg')

        self.assert_game_data('accessible', True, 'cryo')
        self.assert_game_data('accessible', True, 'bridge')
        self.assert_game_data('open', True, 'cryo', 'cryo.door')

    def test_cryo_door_open_hand(self):
        "The door is open and we touch it with the hand. No change."

        self.set_game_data('accessible', True, 'bridge')
        self.set_game_data('open', True, 'cryo', 'cryo.door')

        self.interact_thing('cryo', 'cryo.door')

        self.assert_game_data('accessible', True, 'cryo')
        self.assert_game_data('accessible', True, 'bridge')
        self.assert_game_data('open', True, 'cryo', 'cryo.door')

    def test_cryo_door_open_titanium_leg(self):
        "The door is open and we touch it with the titanium leg. No change."

        self.set_game_data('accessible', True, 'bridge')
        self.set_game_data('open', True, 'cryo', 'cryo.door')

        self.interact_thing('cryo', 'cryo.door', 'titanium_leg')

        self.assert_game_data('accessible', True, 'cryo')
        self.assert_game_data('accessible', True, 'bridge')
        self.assert_game_data('open', True, 'cryo', 'cryo.door')
