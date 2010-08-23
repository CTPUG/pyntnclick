# gamescreen.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game

from albow.controls import Button, Label, Widget
from albow.layout import Column
from albow.palette_view import PaletteView
from albow.dialogs import Dialog
from pygame import Rect
from pygame.color import Color
from pygame.locals import BLEND_ADD

from constants import BUTTON_SIZE
from cursor import CursorSpriteScreen, CursorWidget
from hand import HandButton
from popupmenu import PopupMenu, PopupMenuButton
from state import initial_state, Item

class InventoryView(PaletteView, CursorWidget):

    sel_color = Color("yellow")
    sel_width = 2

    def __init__(self, state, handbutton):
        PaletteView.__init__(self, (BUTTON_SIZE, BUTTON_SIZE), 1, 6, scrolling=True)
        self.state = state
        self.handbutton = handbutton

    def num_items(self):
        return len(self.state.inventory)

    def draw_item(self, surface, item_no, rect):
        item_image = self.state.inventory[item_no].get_inventory_image()
        surface.blit(item_image, rect, None, BLEND_ADD)

    def click_item(self, item_no, event):
        self.state.set_tool(self.state.inventory[item_no])
        self.handbutton.unselect()

    def item_is_selected(self, item_no):
        return self.state.tool is self.state.inventory[item_no]

    def unselect(self):
        self.state.set_tool(None)


class StateWidget(CursorWidget):

    def __init__(self, state):
        Widget.__init__(self, Rect(0, 0, 800, 600 - BUTTON_SIZE))
        self.state = state

    def draw(self, surface):
        self.state.draw(surface)

    def mouse_down(self, event):
        self.state.interact(event.pos)

    def mouse_move(self, event):
        self.state.mouse_move(event.pos)
        CursorWidget.mouse_move(self, event)


class DetailWindow(CursorWidget):
    def mouse_down(self, e):
        if e not in self:
            self.dismiss()

    def draw(self, surface):
        surface.fill(Color('green'))


class GameScreen(CursorSpriteScreen):
    def __init__(self, shell):
        CursorSpriteScreen.__init__(self, shell)

        # TODO: Randomly plonk the state here for now
        self.state = initial_state()
        self.state_widget = StateWidget(self.state)
        self.add(self.state_widget)

        self.popup_menu = PopupMenu(shell)
        self.menubutton = PopupMenuButton('Menu',
                action=self.popup_menu.show_menu)
        self.menubutton.bottomleft = self.bottomleft
        self.add(self.menubutton)

        self.detail = DetailWindow()
        self.detail.rect = Rect(0, 0, 200, 200)

        self.testbutton = Button('Test', action=self.detail.present)
        self.testbutton.bottomright = self.bottomright
        self.add(self.testbutton)

        self.handbutton = HandButton(action=self.hand_pressed)
        self.handbutton.bottomleft = self.bottomleft
        self.handbutton.get_rect().move_ip(BUTTON_SIZE, 0)
        self.add(self.handbutton)

        self.inventory = InventoryView(self.state, self.handbutton)
        self.inventory.bottomleft = self.bottomleft
        self.inventory.get_rect().move_ip(2 * BUTTON_SIZE, 0)
        self.add(self.inventory)

        # Test items
        self.state.add_inventory_item('triangle')


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

    def add_item(self):
        self.state.add_inventory_item("triangle")

    def hand_pressed(self):
        self.handbutton.toggle_selected()
        self.inventory.unselect()


