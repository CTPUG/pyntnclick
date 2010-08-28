# gamescreen.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game

from albow.controls import Widget
from albow.layout import Row
from albow.palette_view import PaletteView
from albow.screen import Screen
from pygame import Rect, mouse
from pygame.color import Color
from pygame.locals import BLEND_ADD

from constants import SCREEN, BUTTON_SIZE, SCENE_SIZE
from cursor import CursorWidget
from state import initial_state, handle_result
from widgets import (MessageDialog, BoomButton, HandButton, PopupMenu,
                     PopupMenuButton)


class InventoryView(PaletteView):

    sel_color = Color("yellow")
    sel_width = 2

    def __init__(self, screen):
        PaletteView.__init__(self, (BUTTON_SIZE, BUTTON_SIZE), 1, 6, scrolling=True)
        self.state = screen.state
        self.state_widget = screen.state_widget

    def num_items(self):
        return len(self.state.inventory)

    def draw_item(self, surface, item_no, rect):
        item_image = self.state.inventory[item_no].get_inventory_image()
        surface.blit(item_image, rect, None, BLEND_ADD)

    def click_item(self, item_no, event):
        item = self.state.inventory[item_no]
        if self.item_is_selected(item_no):
            self.unselect()
        elif self.state.tool or hasattr(item, 'interact_without'):
            result = item.interact(self.state.tool, self.state)
            handle_result(result, self.state_widget)
        else:
            self.state.set_tool(self.state.inventory[item_no])

    def item_is_selected(self, item_no):
        return self.state.tool is self.state.inventory[item_no]

    def unselect(self):
        self.state.set_tool(None)


class StateWidget(Widget):

    def __init__(self, screen):
        Widget.__init__(self, Rect(0, 0, SCENE_SIZE[0], SCENE_SIZE[1]))
        self.screen = screen
        self.state = screen.state
        self.detail = DetailWindow(screen)

    def draw(self, surface):
        self.state.draw(surface, self.screen)

    def mouse_down(self, event):
        self.mouse_move(event)
        if event.button != 1: # We have a right/middle click
            self.state.cancel_doodah(self.screen)
        elif self.subwidgets:
            self.clear_detail()
            self._mouse_move(event.pos)
        else:
            result = self.state.interact(event.pos)
            handle_result(result, self)

    def animate(self):
        if self.state.animate():
            # queue a redraw
            self.invalidate()
        # We do this here so we can get enter and leave events regardless
        # of what happens
        result = self.state.check_enter_leave(self.screen)
        handle_result(result, self)

    def mouse_move(self, event):
        self.state.highlight_override = False
        if not self.subwidgets:
            self._mouse_move(event.pos)

    def _mouse_move(self, pos):
        self.state.highlight_override = False
        self.state.mouse_move(pos)

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
        w, h = self.state.set_current_detail(detail)
        self.detail.set_image_rect(Rect(0, 0, w, h))
        self.add_centered(self.detail)
        self.state.do_enter_detail()

    def clear_detail(self):
        """Hide the detail view"""
        if self.state.current_detail is not None:
            self.remove(self.detail)
            self.state.do_leave_detail()
            self.state.set_current_detail(None)
            self._mouse_move(mouse.get_pos())


class DetailWindow(Widget):
    def __init__(self, screen):
        Widget.__init__(self)
        self.screen = screen
        self.state = screen.state
        self.border_width = 5
        self.border_color = (0, 0, 0)
        # parent only gets set when we get added to the scene
        self.close = BoomButton('Close', self.close_but, screen)
        self.add(self.close)

    def close_but(self):
        self.parent.clear_detail()

    def set_image_rect(self, rect):
        bw = self.border_width
        self.image_rect = rect
        self.image_rect.topleft = (bw, bw)
        self.set_rect(rect.inflate(bw*2, bw*2))
        self.close.rect.midbottom = rect.midbottom

    def draw(self, surface):
        scene_surface = self.get_root().surface.subsurface(self.parent.rect)
        overlay = scene_surface.convert_alpha()
        overlay.fill(Color(0, 0, 0, 191))
        scene_surface.blit(overlay, (0, 0))
        self.state.draw_detail(surface.subsurface(self.image_rect), self.screen)

    def mouse_down(self, event):
        self.mouse_move(event)
        if event.button != 1: # We have a right/middle click
            self.state.cancel_doodah(self.screen)
        else:
            result = self.state.interact_detail(self.global_to_local(event.pos))
            handle_result(result, self)

    def mouse_move(self, event):
        self._mouse_move(event.pos)

    def _mouse_move(self, pos):
        self.state.highlight_override = False
        self.state.mouse_move_detail(self.global_to_local(pos))

    def show_message(self, message, style=None):
        self.parent.show_message(message, style)
        self.invalidate()


class ToolBar(Row):
    def __init__(self, items):
        for item in items:
            item.height = BUTTON_SIZE
        Row.__init__(self, items, spacing=0, width=SCREEN[0])
        self.bg_color = (127, 127, 127)


class GameScreen(Screen, CursorWidget):
    def __init__(self, shell):
        CursorWidget.__init__(self, self)
        Screen.__init__(self, shell)
        self.running = False

    def _clear_all(self):
        for widget in self.subwidgets[:]:
            self.remove(widget)

    def start_game(self):
        self._clear_all()
        self.state = initial_state()
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

    # Albow uses magic method names (command + '_cmd'). Yay.
    # Albow's search order means they need to be defined here, not in
    # PopMenu, which is annoying.
    def hide_cmd(self):
        # This option does nothing, but the method needs to exist for albow
        return

    def main_menu_cmd(self):
        self.shell.show_screen(self.shell.menu_screen)

    def quit_cmd(self):
        self.shell.quit()

    def hand_pressed(self):
        self.inventory.unselect()

    def begin_frame(self):
        if self.running:
            self.state_widget.animate()
