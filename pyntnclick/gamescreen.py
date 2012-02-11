# gamescreen.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game

from pygame import Rect, mouse
from pygame.color import Color

from pyntnclick.cursor import CursorWidget
from pyntnclick.engine import Screen
from pyntnclick.state import handle_result
from pyntnclick.widgets.base import Widget
from pyntnclick.widgets import (
    MessageDialog, BoomButton, HandButton, PopupMenu, PopupMenuButton)

# XXX: Need a way to get at the constants.
from pyntnclick.constants import GameConstants
constants = GameConstants()
SCREEN = constants.screen
BUTTON_SIZE = constants.button_size
SCENE_SIZE = constants.scene_size
LEAVE = constants.leave


class InventoryView(Widget):
    # TODO: Make this work again

    sel_color = Color("yellow")
    sel_width = 2

    def __init__(self, rect):
        self.screen = screen
        self.game = screen.game
        self.state_widget = screen.state_widget

    def num_items(self):
        return len(self.game.inventory)

    def draw_item(self, surface, item_no, rect):
        item_image = self.game.inventory[item_no].get_inventory_image()
        surface.blit(item_image, rect, None)

    def click_item(self, item_no, event):
        item = self.game.inventory[item_no]
        if self.item_is_selected(item_no):
            self.unselect()
        elif item.is_interactive(self.game.tool):
            result = item.interact(self.game.tool)
            handle_result(result, self.state_widget)
        else:
            self.game.set_tool(self.game.inventory[item_no])

    def mouse_down(self, event):
        if event.button != 1:
            self.game.cancel_doodah(self.screen)
        else:
            PaletteView.mouse_down(self, event)

    def item_is_selected(self, item_no):
        return self.game.tool is self.game.inventory[item_no]

    def unselect(self):
        self.game.set_tool(None)


class StateWidget(Widget):

    def __init__(self, screen):
        Widget.__init__(self, Rect(0, 0, SCENE_SIZE[0], SCENE_SIZE[1]))
        self.screen = screen
        self.game = screen.game
        self.detail = DetailWindow(screen)

    def draw(self, surface):
        self.animate()
        if self.game.previous_scene and self.game.do_check == LEAVE:
            # We still need to handle leave events, so still display the scene
            self.game.previous_scene.draw(surface, self)
        else:
            self.game.current_scene.draw(surface, self)

    def mouse_down(self, event):
        self.mouse_move(event)
        if event.button != 1:  # We have a right/middle click
            self.game.cancel_doodah(self.screen)
        elif self.subwidgets:
            self.clear_detail()
            self._mouse_move(event.pos)
        else:
            result = self.game.interact(event.pos)
            handle_result(result, self)

    def animate(self):
        if self.game.animate():
            # queue a redraw
            self.invalidate()
        # We do this here so we can get enter and leave events regardless
        # of what happens
        result = self.game.check_enter_leave(self.screen)
        handle_result(result, self)

    def mouse_move(self, event):
        self.game.highlight_override = False
        if not self.subwidgets:
            self._mouse_move(event.pos)

    def _mouse_move(self, pos):
        self.game.highlight_override = False
        self.game.current_scene.mouse_move(pos)
        self.game.old_pos = pos

    def show_message(self, message, style=None):
        # Display the message as a modal dialog
        MessageDialog(self.screen, message, 60, style=style).present()
        # queue a redraw to show updated state
        self.invalidate()
        # The cursor could have gone anywhere
        if self.subwidgets:
            self.subwidgets[0]._mouse_move(mouse.get_pos())
        else:
            self._mouse_move(mouse.get_pos())

    def show_detail(self, detail):
        self.clear_detail()
        detail_obj = self.game.set_current_detail(detail)
        self.detail.set_image_rect(Rect((0, 0), detail_obj.get_detail_size()))
        self.add_centered(self.detail)
        self.game.do_enter_detail()

    def clear_detail(self):
        """Hide the detail view"""
        if self.game.current_detail is not None:
            self.remove(self.detail)
            self.game.do_leave_detail()
            self.game.set_current_detail(None)
            self._mouse_move(mouse.get_pos())

    def end_game(self):
        self.screen.running = False
        self.screen.shell.show_screen(self.screen.shell.end_screen)


class DetailWindow(Widget):
    def __init__(self, screen):
        Widget.__init__(self)
        self.image_rect = None
        self.screen = screen
        self.game = screen.game
        self.border_width = 5
        self.border_color = (0, 0, 0)
        # parent only gets set when we get added to the scene
        self.close = BoomButton('Close', self.close_but, screen)
        self.add(self.close)

    def close_but(self):
        self.parent.clear_detail()

    def end_game(self):
        self.parent.end_game()

    def set_image_rect(self, rect):
        bw = self.border_width
        self.image_rect = rect
        self.image_rect.topleft = (bw, bw)
        self.set_rect(rect.inflate(bw * 2, bw * 2))
        self.close.rect.midbottom = rect.midbottom

    def draw(self, surface):
        scene_surface = self.get_root().surface.subsurface(self.parent.rect)
        overlay = scene_surface.convert_alpha()
        overlay.fill(Color(0, 0, 0, 191))
        scene_surface.blit(overlay, (0, 0))
        self.game.current_detail.draw(
            surface.subsurface(self.image_rect), self)

    def mouse_down(self, event):
        self.mouse_move(event)
        if event.button != 1:  # We have a right/middle click
            self.game.cancel_doodah(self.screen)
        else:
            result = self.game.interact_detail(
                self.global_to_local(event.pos))
            handle_result(result, self)

    def mouse_move(self, event):
        self._mouse_move(event.pos)

    def _mouse_move(self, pos):
        self.game.highlight_override = False
        self.game.current_detail.mouse_move(self.global_to_local(pos))

    def show_message(self, message, style=None):
        self.parent.show_message(message, style)
        self.invalidate()


class ToolBar(Widget):
    def __init__(self, items):
        for item in items:
            item.height = BUTTON_SIZE
        self.bg_color = (31, 31, 31)

    def draw(self, surface):
        surface.fill(self.bg_color)
        Row.draw(self, surface)


class GameScreen(Screen):

    def setup(self):
        self.running = False
        self.create_initial_state = self.game_description.initial_state

    def _clear_all(self):
        for widget in self.container.children[:]:
            self.container.remove(widget)

    def process_event(self, event_name, data):
        if event_name == 'restart':
            self.start_game()

    def start_game(self):
        self._clear_all()
        self.game = self.create_initial_state()
        self.state_widget = StateWidget(self)
        self.add(self.state_widget)

        self.popup_menu = PopupMenu(self)
        self.menubutton = PopupMenuButton('Menu',
                action=self.popup_menu.show_menu)

        self.handbutton = HandButton(action=self.hand_pressed)

        self.inventory = InventoryView(self)

        self.toolbar = ToolBar([
                self.menubutton,
                self.handbutton,
                self.inventory,
                ])
        self.toolbar.bottomleft = self.bottomleft
        self.add(self.toolbar)

        self.running = True

    def enter_screen(self):
        CursorWidget.enter_screen(self)

    def leave_screen(self):
        CursorWidget.leave_screen(self)

    # albow callback:
    def main_menu_cmd(self):
        self.shell.show_screen(self.shell.menu_screen)

    # albow callback:
    def quit_cmd(self):
        self.shell.quit()

    def hand_pressed(self):
        self.inventory.unselect()


class DefEndScreen(Screen):
    """A placeholder 'Game Over' screen so people can get started easily"""

    def setup(self):
        self.background = self.resource.get_image(('pyntnclick', 'end.png'))

    def draw(self, surface):
        surface.blit(self.background, (0, 0))


class DefMenuScreen(Screen):
    """A placeholder Start screen so people can get started easily"""

    def setup(self):
        self.background = self.resource.get_image(('pyntnclick', 'start.png'))

    def draw(self, surface):
        surface.blit(self.background, (0, 0))
