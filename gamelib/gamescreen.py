# menu.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game

from state import initial_state, Item
from hand import HandButton

from pygame.color import Color
from pygame import Rect
from pygame.locals import BLEND_ADD
from albow.screen import Screen
from albow.controls import Button, Label, Widget
from albow.layout import Column
from albow.palette_view import PaletteView


class InventoryView(PaletteView):

    sel_color = Color("yellow")
    sel_width = 2

    def __init__(self, state, handbutton):
        PaletteView.__init__(self, (50, 50), 1, 6, scrolling=True)
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
        Widget.__init__(self, Rect(0, 0, 800, 550))
        self.state = state

    def draw(self, surface):
        self.state.draw(surface)


class GameScreen(Screen):
    def __init__(self, shell):
        Screen.__init__(self, shell)

        # TODO: Randomly plonk the state here for now
        self.state = initial_state()
        self.state_widget = StateWidget(self.state)
        self.add(self.state_widget)

        StartButton = Button('Main Menu', action = self.main_menu)
        QuitButton = Button('Quit', action = shell.quit)
        AddItemButton = Button('Add item', action = self.add_item)
        Title = Label('Caught! ... In SPAACE')
        menu = Column([
            Title,
            StartButton,
            QuitButton,
            AddItemButton,
            ], align='l', spacing=20)
        self.add_centered(menu)
        self.menubutton = Button('M', action=self.main_menu)
        self.menubutton.bottomleft = self.bottomleft
        self.add(self.menubutton)
        self.handbutton = HandButton(action=self.hand_pressed)
        self.handbutton.bottomleft = self.bottomleft
        self.handbutton.get_rect().move_ip(50, 0)
        self.add(self.handbutton)
        self.inventory = InventoryView(self.state, self.handbutton)

        self.inventory.bottomleft = self.bottomleft
        self.inventory.get_rect().move_ip(100, 0)
        self.add(self.inventory)

        # Test items
        self.state.add_inventory_item('triangle')
        self.state.add_inventory_item('square')

    def main_menu(self):
        print 'Returning to menu'
        self.shell.show_screen(self.shell.menu_screen)

    def add_item(self):
        self.state.add_inventory_item("triangle")

    def hand_pressed(self):
        self.handbutton.toggle_selected()
        self.inventory.unselect()

