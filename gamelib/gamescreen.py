# gamescreen.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game

from state import initial_state, Item
from hand import HandButton
from popupmenu import PopupMenu
from constants import BUTTON_SIZE

from pygame.color import Color
from pygame import Rect
from pygame.locals import BLEND_ADD
from albow.screen import Screen
from albow.resource import get_font
from albow.controls import Button, Label, Widget
from albow.layout import Column
from albow.palette_view import PaletteView


class InventoryView(PaletteView):

    sel_color = Color("yellow")
    sel_width = 2

    def __init__(self, state, handbutton):
        PaletteView.__init__(self, (BUTTON_SIZE, BUTTON_SIZE), 1, 6, scrolling=True)
        self.state = state
        self.selection = None
        self.handbutton = handbutton

    def num_items(self):
        return len(self.state.inventory)

    def draw_item(self, surface, item_no, rect):
        item_image = self.state.inventory[item_no].get_inventory_image()
        surface.blit(item_image, rect, None, BLEND_ADD)

    def click_item(self, item_no, event):
        self.selection = item_no
        self.handbutton.unselect()

    def item_is_selected(self, item_no):
        return self.selection == item_no

    def unselect(self):
        self.selection = None


class StateWidget(Widget):

    def __init__(self, state):
        Widget.__init__(self, Rect(0, 0, 800, 600 - BUTTON_SIZE))
        self.state = state
        # current mouse-over thing description
        self.description = None

    def draw(self, surface):
        self.state.draw(surface)
        if self.description:
            print self.description
        msg = self.state.get_message()
        if msg:
            # FIXME: add some timer to invalidate msgs
            print msg
            self.state.clear_message()

    def mouse_move(self, event):
        old_desc = self.description
        self.description = self.state.get_description(event.pos)
        if self.description != old_desc:
            # queue a redraw
            self.invalidate()

class GameScreen(Screen):
    def __init__(self, shell):
        Screen.__init__(self, shell)

        # TODO: Randomly plonk the state here for now
        self.state = initial_state()
        self.state_widget = StateWidget(self.state)
        self.add(self.state_widget)

        AddItemButton = Button('Add item', action = self.add_item)
        menu = Column([
            AddItemButton,
            Button('Use hand', action = lambda: self.state.scenes['cryo'].things['cryo.door'].interact(None)),
            Button('Use triangle', action = lambda: self.state.scenes['cryo'].things['cryo.door'].interact(self.state.items['triangle'])),
            Button('Use titanium_leg', action = lambda: self.state.scenes['cryo'].things['cryo.door'].interact(self.state.items['titanium_leg'])),
            ], align='l', spacing=20)
        self.add_centered(menu)
        self.popup_menu = PopupMenu(shell)
        self.menubutton = Button('Menu', action=self.popup_menu.show_menu)
        self.menubutton.font = get_font(16, 'Vera.ttf')
        self.menubutton.set_rect(Rect(0, 0, BUTTON_SIZE, BUTTON_SIZE))
        self.menubutton.bottomleft = self.bottomleft
        self.menubutton.margin = (BUTTON_SIZE - self.menubutton.font.get_linesize()) / 2
        self.add(self.menubutton)
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
        self.state.add_inventory_item('titanium_leg')


    # Albow uses magic method names (command + '_cmd'). Yay.
    # Albow's search order means they need to be defined here, not in
    # PopMenu, which is annoying.
    def hide_cmd(self):
        # This option does nothing, but the method needs to exist for albow
        return

    def main_menu_cmd(self):
        self.shell.show_screen(self.shell.menu_screen)

    def add_item(self):
        self.state.add_inventory_item("triangle")

    def hand_pressed(self):
        self.handbutton.toggle_selected()
        self.inventory.unselect()


