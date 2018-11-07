# gamescreen.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game
from __future__ import division

import pygame.draw
from pygame import Surface
from pygame.color import Color
from pygame.locals import MOUSEBUTTONDOWN, MOUSEMOTION, KEYDOWN, K_ESCAPE

from .i18n import _
from .cursor import CursorScreen
from .engine import Screen
from .widgets.base import (Container, ModalStackContainer, ModalWrapper)
from .widgets.text import TextButton, WrappedTextLabel
from .widgets.imagebutton import ImageButtonWidget


class InventorySlot(ImageButtonWidget):
    SELECTED_COLOR = Color("yellow")
    SELECTED_WIDTH = 2

    def __init__(self, pos, gd, size):
        self.item = None
        super(InventorySlot, self).__init__(pos, gd, None, size)
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
    def __init__(self, pos, gd, size=None):
        super(UpDownButton, self).__init__(pos, gd, self.TEXT, size=size,
                                           padding=3)


class UpButton(UpDownButton):
    TEXT = u'\N{UPWARDS ARROW}UP'


class DownButton(UpDownButton):
    TEXT = u'\N{DOWNWARDS ARROW}DN'


class InventoryView(Container):
    MIN_UPDOWN_WIDTH = 20

    def __init__(self, pos, gd, size, screen):
        self.bsize = gd.constants.button_size
        super(InventoryView, self).__init__(pos, gd, size)
        self.screen = screen
        self.game = screen.game

        slots = (self.rect.width - self.MIN_UPDOWN_WIDTH) // self.bsize
        self.slots = [self.add(self.make_slot(i)) for i in range(slots)]
        self.inv_offset = 0

        self.updown_width = self.rect.width - slots * self.bsize
        ud_left = self.rect.right - self.updown_width
        self.up_button = self.add(UpButton((ud_left, self.rect.top), gd,
                    (self.updown_width, self.rect.height // 2)))
        self.up_button.add_callback(MOUSEBUTTONDOWN, self.up_callback)
        self.down_button = self.add(DownButton(
                    (ud_left, self.rect.top + self.rect.height // 2), gd,
                    (self.updown_width, self.rect.height // 2)))
        self.down_button.add_callback(MOUSEBUTTONDOWN, self.down_callback)

        self.add_callback(MOUSEBUTTONDOWN, self.mouse_down)
        self.update_slots()

    def make_slot(self, slot):
        pos = (self.rect.left + slot * self.bsize, self.rect.top)
        size = (self.bsize, self.rect.height)
        return InventorySlot(pos, self.gd, size)

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
        if max_slot >= len(self.game.inventory()):
            self.down_button.disable()
        else:
            self.down_button.enable()

    @property
    def slot_items(self):
        item_names = self.game.inventory()[self.inv_offset:][:len(self.slots)]
        return [self.game.get_item(name) for name in item_names]

    def mouse_down(self, event, widget):
        if event.button != 1:
            self.game.set_tool(None)

    def select(self, tool):
        self.game.set_tool(tool)


class SceneWidget(Container):
    DETAIL_BORDER = 4
    DETAIL_BORDER_COLOR = Color("black")

    def __init__(self, pos, gd, size, scene, screen, is_detail=False):
        super(SceneWidget, self).__init__(pos, gd, size)
        self.name = scene.NAME
        self.scene = scene
        self.screen = screen
        self.game = screen.game
        self.add_callback(MOUSEBUTTONDOWN, self.mouse_down)
        self.add_callback(MOUSEMOTION, self.mouse_move)
        self.is_detail = is_detail
        if is_detail:
            self.close_button = TextButton((0, 0), self.gd, _("Close"))
            self.close_button.do_prepare()
            # TODO: Don't muck around with close_button's rect
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
            if self.game.tool:
                self.game.set_tool(None)
            elif self.is_detail:
                self.close(event, widget)
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
    def __init__(self, pos, gd, size, screen):
        self.screen = screen

        super(ToolBar, self).__init__(pos, gd, size)

        self.bg_color = (31, 31, 31)
        self.left = self.rect.left

        self.menu_button = self.add_tool(
            self.rect.height, TextButton, _("Menu"),
            fontname=gd.constants.bold_font,
            color="red", padding=1, border=0, bg_color="black")
        self.menu_button.add_callback(MOUSEBUTTONDOWN, self.menu_callback)

        hand_image = gd.resource.get_image('items', 'hand.png')
        self.hand_button = self.add_tool(
            None, ImageButtonWidget, hand_image)
        self.hand_button.add_callback(MOUSEBUTTONDOWN, self.hand_callback)

        self.inventory = self.add_tool(
            self.rect.width - self.left, InventoryView, screen=screen)

    def add_tool(self, width, cls, *args, **kw):
        pos = (self.left, self.rect.top)
        if width is not None:
            kw['size'] = (width, self.rect.height)
        tool = cls(pos, self.gd, *args, **kw)
        self.add(tool)
        tool.do_prepare()
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
        self.reset_game()

    def get_save_dir(self):
        return self.gd.get_default_save_location()

    def game_event_load(self, data):
        state = self.gd.game_state_class().load_game(
            self.get_save_dir(), 'savegame')
        # TODO: Handle this better.
        if state is not None:
            self.reset_game(state)

    def game_event_save(self, data):
        self.game.data.save_game(self.get_save_dir(), 'savegame')

    def reset_game(self, game_state=None):
        self._clear_all()
        self.game = self.create_initial_state(game_state)

        self.screen_modal = self.container.add(
            ModalStackContainer(self.container.pos, self.gd,
                                self.container.size))
        self.inner_container = self.screen_modal.add(
            Container(self.container.pos, self.gd, self.container.size))

        toolbar_height = self.gd.constants.button_size

        self.scene_modal = self.inner_container.add(
            ModalStackContainer((0, 0), self.gd,
                (self.surface_size[0], self.surface_size[1] - toolbar_height)))
        self.toolbar = self.inner_container.add(
            ToolBar((0, self.surface_size[1] - toolbar_height), self.gd,
                (self.surface_size[0], toolbar_height), self))
        self.inventory = self.toolbar.inventory

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
        self.game.data.set_current_scene(scene_name)
        self._add_scene(self.game.scenes[scene_name])

    def show_detail(self, detail_name):
        detail_scene = self.game.detail_views[detail_name]
        if detail_scene.name == self.scene_modal.top.name:
            # Don't show the scene if we're already showing it
            return
        self._add_scene(detail_scene, True)

    def _add_scene(self, scene, detail=False):
        pos = self.scene_modal.rect.topleft
        size = self.scene_modal.rect.size
        if detail:
            size = scene.get_detail_size()
            pos = ((self.scene_modal.rect.width - size[0]) // 2,
                   (self.scene_modal.rect.height - size[1]) // 2)

        self.scene_modal.add(SceneWidget(pos, self.gd, size, scene, self,
                                         detail))
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
        max_width = self.gd.constants.screen[0] - 100
        widget = WrappedTextLabel((0, 0), self.gd, message,
                                  max_width=max_width)
        widget.do_prepare()
        # TODO: Use the centering API when it exists
        widget.rect.center = self.container.rect.center
        self.queue_widget(widget)

    def handle_result(self, resultset):
        """Handle dealing with result or result sequences"""
        if resultset:
            if hasattr(resultset, 'process'):
                resultset = [resultset]
            for result in resultset:
                if result:
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
