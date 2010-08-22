# menu.py
# Copyright Boomslang team, 2010 (see COPYING File)
# Main menu for the game

from state import initial_state

from pygame.color import Color
from pygame import Rect
from albow.screen import Screen
from albow.controls import Button, Label, Widget
from albow.layout import Column
from albow.palette_view import PaletteView


class InventoryView(PaletteView):

    info = ["red", "green", "blue", "cyan", "magenta", "yellow"]

    sel_color = Color("white")
    sel_width = 2

    def __init__(self):
        PaletteView.__init__(self, (50, 50), 1, 6, scrolling=True)
        self.selection = None

    def num_items(self):
        return len(self.info)

    def draw_item(self, surface, item_no, rect):
        d = -2 * self.sel_width
        r = rect.inflate(d, d)
        color = Color(self.info[item_no])
        surface.fill(color, r)

    def click_item(self, item_no, event):
        self.selection = item_no

    def item_is_selected(self, item_no):
        return self.selection == item_no

    def add_item(self, colstr):
        self.info.append(colstr)


class StateWidget(Widget):

    def __init__(self, state):
        Widget.__init__(self, Rect(0, 0, 800, 600))
        self.state = state

    def draw(self, surface):
        self.state.draw(surface)


class GameScreen(Screen):
    def __init__(self, shell):
        Screen.__init__(self, shell)
        self.shell = shell

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

        self.inventory = InventoryView()
        self.inventory.bottomleft = self.bottomleft
        self.add(self.inventory)

    def main_menu(self):
        print 'Returning to menu'
        self.shell.show_screen(self.shell.menu_screen)

    def add_item(self):
        self.inventory.add_item("white")
