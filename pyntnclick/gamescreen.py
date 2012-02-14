# gamescreen.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game

import pygame.draw
from pygame import Rect, Surface
from pygame.color import Color
from pygame.locals import MOUSEBUTTONDOWN, MOUSEMOTION, KEYDOWN, K_ESCAPE

from pyntnclick.cursor import CursorScreen
from pyntnclick.engine import Screen
from pyntnclick.widgets.base import (
    Container, ModalStackContainer, ModalWrapper)
from pyntnclick.widgets.text import TextButton, WrappedTextLabel
from pyntnclick.widgets.imagebutton import ImageButtonWidget

# XXX: Need a way to get at the constants.
from pyntnclick.constants import GameConstants
constants = GameConstants()
SCREEN = constants.screen
LEAVE = constants.leave


class InventorySlot(ImageButtonWidget):
    SELECTED_COLOR = Color("yellow")
    SELECTED_WIDTH = 2

    def __init__(self, rect, gd):
        self.item = None
        super(InventorySlot, self).__init__(rect, gd, None)
        self.add_callback(MOUSEBUTTONDOWN, self.mouse_down)

    def set_item(self, item):
        self.item = item

    def draw(self, surface):
        if self.item:
            surface.blit(self.item.get_inventory_image(), self.rect)
            if self.selected:
                pygame.draw.rect(surface, self.SELECTED_COLOR,
                                 self.rect, self.SELECTED_WIDTH)

    @property
    def selected(self):
        return self.parent.game.tool is self.item

    def mouse_down(self, event, widget):
        if event.button != 1 or not self.item:
            return
        if self.selected:
            self.parent.select(None)
        elif self.item.is_interactive(self.parent.game.tool):
            result = self.item.interact(self.parent.game.tool)
            self.parent.screen.handle_result(result)
        else:
            self.parent.select(self.item)


class UpDownButton(TextButton):
    # TextButton for now.
    def __init__(self, rect, gd):
        super(UpDownButton, self).__init__(rect, gd, self.TEXT, padding=3)


class UpButton(UpDownButton):
    TEXT = 'UP'


class DownButton(UpDownButton):
    TEXT = 'DN'


class InventoryView(Container):
    MIN_UPDOWN_WIDTH = 16

    def __init__(self, rect, gd, screen):
        self.bsize = gd.constants.button_size
        super(InventoryView, self).__init__(rect, gd)
        self.screen = screen
        self.game = screen.game

        slots = (self.rect.width - self.MIN_UPDOWN_WIDTH) / self.bsize
        self.slots = [self.add(self.make_slot(i)) for i in range(slots)]
        self.inv_offset = 0

        self.updown_width = self.rect.width - slots * self.bsize
        ud_left = self.rect.right - self.updown_width
        self.up_button = self.add(UpButton(Rect(
                    (ud_left, self.rect.top),
                    (self.updown_width, self.rect.height / 2)), gd))
        self.up_button.add_callback(MOUSEBUTTONDOWN, self.up_callback)
        self.down_button = self.add(DownButton(Rect(
                    (ud_left, self.rect.top + self.rect.height / 2),
                    (self.updown_width, self.rect.height / 2)), gd))
        self.down_button.add_callback(MOUSEBUTTONDOWN, self.down_callback)

        self.add_callback(MOUSEBUTTONDOWN, self.mouse_down)
        self.update_slots()

    def make_slot(self, slot):
        rect = Rect((self.rect.left + slot * self.bsize, self.rect.top),
                    (self.bsize, self.rect.height))
        return InventorySlot(rect, self.gd)

    def up_callback(self, event, widget):
        self.inv_offset = max(self.inv_offset - len(self.slots), 0)
        self.update_slots()

    def down_callback(self, event, widget):
        self.inv_offset += len(self.slots)
        self.update_slots()

    def update_slots(self):
        items = (self.slot_items + [None] * len(self.slots))[:len(self.slots)]
        for item, slot in zip(items, self.slots):
            slot.set_item(item)

        if self.inv_offset <= 0:
            self.up_button.disable()
        else:
            self.up_button.enable()

        max_slot = (self.inv_offset + len(self.slots))
        if max_slot >= len(self.game.inventory):
            self.down_button.disable()
        else:
            self.down_button.enable()

    @property
    def slot_items(self):
        return self.game.inventory[self.inv_offset:][:len(self.slots)]

    def mouse_down(self, event, widget):
        if event.button != 1:
            self.game.cancel_doodah(self.screen)

    def select(self, tool):
        self.game.set_tool(tool)


class SceneWidget(Container):
    DETAIL_BORDER = 4
    DETAIL_BORDER_COLOR = Color("black")

    def __init__(self, rect, gd, scene, screen, is_detail=False):
        super(SceneWidget, self).__init__(rect, gd)
        self.name = scene.NAME
        self.scene = scene
        self.screen = screen
        self.game = screen.game
        self.add_callback(MOUSEBUTTONDOWN, self.mouse_down)
        self.add_callback(MOUSEMOTION, self.mouse_move)
        self.is_detail = is_detail
        if is_detail:
            self.close_button = TextButton((0, 0), self.gd, "Close")
            self.close_button.rect.midbottom = self.rect.midbottom
            self.close_button.add_callback('clicked', self.close)
            self.add(self.close_button)

    def draw(self, surface):
        self.scene.draw(surface.subsurface(self.rect))
        if self.is_detail:
            border = self.rect.inflate(self.DETAIL_BORDER, self.DETAIL_BORDER)
            pygame.draw.rect(
                surface, self.DETAIL_BORDER_COLOR, border, self.DETAIL_BORDER)
        if self.parent.is_top(self):
            self.scene.draw_description(surface)
        super(SceneWidget, self).draw(surface)

    @property
    def highlight_cursor(self):
        return (self.scene.current_thing
                and self.scene.current_thing.is_interactive())

    def mouse_down(self, event, widget):
        self.mouse_move(event, widget)
        if event.button != 1:  # We have a right/middle click
            self.game.cancel_doodah(self.screen)
        else:
            pos = self.global_to_local(event.pos)
            result = self.scene.interact(self.game.tool, pos)
            self.screen.handle_result(result)

    def animate(self):
        self.scene.animate()

    def mouse_move(self, event, widget):
        pos = self.global_to_local(event.pos)
        self.scene.mouse_move(pos)
        self.game.old_pos = event.pos

    def close(self, event, widget):
        self.screen.close_detail(self)


class ToolBar(Container):
    def __init__(self, rect, gd, screen):
        self.screen = screen
        button_size = gd.constants.button_size

        if not isinstance(rect, Rect):
            rect = Rect(rect, (gd.constants.scene_size[0], button_size))
        super(ToolBar, self).__init__(rect, gd)

        self.bg_color = (31, 31, 31)
        self.left = self.rect.left

        self.menu_button = self.add_tool(
            0, TextButton, gd, "Menu", fontname=gd.constants.bold_font,
            color="red", padding=1, border=0, bg_color="black")
        self.menu_button.add_callback(MOUSEBUTTONDOWN, self.menu_callback)

        hand_image = gd.resource.get_image('items', 'hand.png')
        self.hand_button = self.add_tool(
            None, ImageButtonWidget, gd, hand_image)
        self.hand_button.add_callback(MOUSEBUTTONDOWN, self.hand_callback)

        self.inventory = self.add_tool(
            self.rect.width - self.left, InventoryView, gd, screen)

    def add_tool(self, width, cls, *args, **kw):
        rect = (self.left, self.rect.top)
        if width is not None:
            rect = Rect(rect, (width, self.rect.height))
        tool = cls(rect, *args, **kw)
        self.add(tool)
        self.left += tool.rect.width
        return tool

    def draw(self, surface):
        bg = Surface(self.rect.size)
        bg.fill(self.bg_color)
        surface.blit(bg, self.rect)
        super(ToolBar, self).draw(surface)

    def hand_callback(self, event, widget):
        self.inventory.select(None)

    def menu_callback(self, event, widget):
        self.screen.change_screen('menu')


class GameScreen(CursorScreen):

    def setup(self):
        super(GameScreen, self).setup()
        self.gd.running = False
        self.create_initial_state = self.gd.initial_state
        self.container.add_callback(KEYDOWN, self.key_pressed)

    def _clear_all(self):
        self._message_queue = []
        for widget in self.container.children[:]:
            self.container.remove(widget)

    def process_event(self, event_name, data):
        getattr(self, 'game_event_%s' % event_name, lambda d: None)(data)

    def game_event_restart(self, data):
        self._clear_all()
        self.game = self.create_initial_state()

        self.screen_modal = self.container.add(
            ModalStackContainer(self.container.rect.copy(), self.gd))
        self.inner_container = self.screen_modal.add(
            Container(self.container.rect.copy(), self.gd))

        toolbar_height = self.gd.constants.button_size
        rect = Rect(0, 0, self.surface_size[0],
                    self.surface_size[1] - toolbar_height)

        self.scene_modal = self.inner_container.add(
            ModalStackContainer(rect, self.gd))
        self.toolbar = self.inner_container.add(
            ToolBar((0, rect.height), self.gd, self))
        self.inventory = self.toolbar.inventory

        self.game.change_scene
        self.gd.running = True

    def game_event_inventory(self, data):
        self.inventory.update_slots()

    def game_event_change_scene(self, data):
        scene_name = data['name']
        if data['detail']:
            self.show_detail(scene_name)
        else:
            self.change_scene(scene_name)

    def change_scene(self, scene_name):
        for scene_widget in reversed(self.scene_modal.children[:]):
            self.scene_modal.remove(scene_widget)
            scene_widget.scene.leave()
        scene = self.game.scenes[scene_name]
        self.game.current_scene = scene
        self._add_scene(scene)

    def show_detail(self, detail_name):
        self._add_scene(self.game.detail_views[detail_name], True)

    def _add_scene(self, scene, detail=False):
        rect = self.scene_modal.rect.copy()
        if detail:
            rect = Rect((0, 0), scene.get_detail_size())
            rect.center = self.scene_modal.rect.center

        self.scene_modal.add(SceneWidget(rect, self.gd, scene, self, detail))
        self.handle_result(scene.enter())

    def close_detail(self, detail=None):
        if detail is None:
            detail = self.scene_modal.top
        self.scene_modal.remove(detail)
        self.handle_result(detail.scene.leave())

    def animate(self):
        """Animate the scene widgets"""
        for scene_widget in self.scene_modal.children:
            scene_widget.animate()

    def key_pressed(self, event, widget):
        if event.key == K_ESCAPE:
            self.change_screen('menu')

    def end_game(self):
        self.change_screen('end')

    def show_queued_widget(self):
        if self._message_queue:
            # Only add a message if there isn't already one up
            if self.screen_modal.is_top(self.inner_container):
                widget = self._message_queue.pop(0)
                self.screen_modal.add(
                    ModalWrapper(widget, self.show_queued_widget))

    def queue_widget(self, widget):
        self._message_queue.append(widget)
        self.show_queued_widget()

    def show_message(self, message):
        rect = Rect((0, 0), (1, 1))
        max_width = self.gd.constants.screen[0] - 100
        widget = WrappedTextLabel(rect, self.gd, message, max_width=max_width)
        widget.rect.center = self.container.rect.center
        self.queue_widget(widget)

    def handle_result(self, resultset):
        """Handle dealing with result or result sequences"""
        if resultset:
            if hasattr(resultset, 'process'):
                resultset = [resultset]
            for result in resultset:
                result.process(self)


class DefEndScreen(Screen):
    """A placeholder 'Game Over' screen so people can get started easily"""

    def setup(self):
        self.background = self.resource.get_image('pyntnclick/end.png')

    def draw(self, surface):
        surface.blit(self.background, (0, 0))


class DefMenuScreen(Screen):
    """A placeholder Start screen so people can get started easily"""

    def setup(self):
        self.background = self.resource.get_image('pyntnclick/start.png')

    def draw(self, surface):
        surface.blit(self.background, (0, 0))
