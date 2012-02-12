# gamescreen.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game

import pygame.draw
from pygame import Rect, Surface
from pygame.color import Color
from pygame.locals import MOUSEBUTTONDOWN, MOUSEMOTION, KEYDOWN, K_ESCAPE

from pyntnclick.cursor import CursorScreen
from pyntnclick.engine import Screen
from pyntnclick.state import handle_result
from pyntnclick.widgets.base import Container, ModalStackContainer
from pyntnclick.widgets.text import TextButton, ModalWrappedTextLabel
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
            handle_result(result, self.parent.scene_widget)
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
        self.scene_widget = screen.scene_widget

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

    def draw(self, surface):
        super(InventoryView, self).draw(surface)

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
        self.scene = scene
        self.screen = screen
        self.game = screen.game
        self.add_callback(MOUSEBUTTONDOWN, self.mouse_down)
        self.add_callback(MOUSEMOTION, self.mouse_move)
        self._message_queue = []
        self.is_detail = is_detail
        if is_detail:
            self.close_button = TextButton((0, 0), self.gd, "Close")
            self.close_button.rect.midbottom = self.rect.midbottom
            self.close_button.add_callback('clicked', self.close)
            self.add(self.close_button)

    def draw(self, surface):
        self.scene.draw(surface.subsurface(self.rect))
        self.scene.draw_description(surface)
        super(SceneWidget, self).draw(surface)
        if self.is_detail:
            border = self.rect.inflate(self.DETAIL_BORDER, self.DETAIL_BORDER)
            pygame.draw.rect(
                surface, self.DETAIL_BORDER_COLOR, border, self.DETAIL_BORDER)

    def queue_widget(self, widget):
        self._message_queue.append(widget)

    def mouse_down(self, event, widget):
        self.mouse_move(event, widget)
        if event.button != 1:  # We have a right/middle click
            self.game.cancel_doodah(self.screen)
        else:
            pos = self.global_to_local(event.pos)
            result = self.game.interact(pos)
            handle_result(result, self)

    def animate(self):
        # XXX: if self.game.animate():
            # queue a redraw
        #    self.invalidate()
        # We do this here so we can get enter and leave events regardless
        # of what happens
        result = self.game.check_enter_leave(self.screen)
        handle_result(result, self)
        if self._message_queue:
            # Only add a message if we're at the top
            if self.screen.screen_modal.is_top(self.screen.inner_container):
                widget = self._message_queue.pop(0)
                self.screen.screen_modal.add(widget)
        self.scene.animate()

    def mouse_move(self, event, widget):
        pos = self.global_to_local(event.pos)
        self.scene.mouse_move(pos)
        self.game.old_pos = event.pos

    def show_message(self, message):
        # Display the message as a modal dialog
        # XXX: MessageDialog(self.screen, message, 60, style=style).present()
        # queue a redraw to show updated state
        # XXX: self.invalidate()
        # The cursor could have gone anywhere
        # XXX: if self.subwidgets:
        #    self.subwidgets[0]._mouse_move(mouse.get_pos())
        # else:
        #    self._mouse_move(mouse.get_pos())
        rect = Rect((0, 0), (1, 1))
        widget = ModalWrappedTextLabel(rect, self.gd, message,
                max_width=self.gd.constants.screen[0] - 100)
        widget.rect.center = self.rect.center
        # We abuse animate so we can queue multiple results
        # according
        self.queue_widget(widget)

    def show_detail(self, detail):
        self.screen.show_detail(detail)

    def close(self, event, widget):
        self.screen.close_detail(self)

    def end_game(self):
        self.screen.change_screen('end')


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
        self.scene_widget = None

    def _clear_all(self):
        for widget in self.container.children[:]:
            self.container.remove(widget)

    def process_event(self, event_name, data):
        if event_name == 'restart':
            self.start_game()
        elif event_name == 'inventory':
            self.inventory.update_slots()
        elif event_name == 'change_scene':
            self.change_scene(data)

    def start_game(self):
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
        self.change_scene(None)

        self.toolbar = self.inner_container.add(
            ToolBar((0, rect.height), self.gd, self))
        self.inventory = self.toolbar.inventory

        self.gd.running = True

    def change_scene(self, scene_name):
        self.scene_modal.remove_all()
        self.scene_widget = self.scene_modal.add(
            SceneWidget(self.scene_modal.rect.copy(), self.gd,
                        self.game.current_scene, self))

    def show_detail(self, detail_name):
        detail = self.game.set_current_detail(detail_name)
        detail_rect = Rect((0, 0), detail.get_detail_size())
        detail_rect.center = self.scene_modal.rect.center
        self.scene_modal.add(
            SceneWidget(detail_rect, self.gd, detail, self, is_detail=True))

    def close_detail(self, detail):
        self.scene_modal.remove(detail)

    def animate(self):
        """Animate the scene widgets"""
        for scene_widget in self.scene_modal.children:
            scene_widget.animate()

    def key_pressed(self, event, widget):
        if event.key == K_ESCAPE:
            self.change_screen('menu')


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
