# Quickly hacked together helper for working out
# interactive regions in Suspended Sentence

import sys
import os.path

script_path = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(script_path)

from albow.root import RootWidget
from albow.utils import frame_rect
from albow.widget import Widget
from albow.controls import Button
from albow.palette_view import PaletteView
from pygame.locals import SWSURFACE
import pygame
from pygame.colordict import THECOLORS

from gamelib.state import initial_state
from gamelib import constants

constants.DEBUG = True



class AppPalette(PaletteView):

    sel_width = 5

    colors = [
            'red', 'maroon1', 'palevioletred1', 'moccasin', 'orange',
            'honeydew', 'yellow', 'gold', 'goldenrod', 'brown',
            'blue', 'purple', 'darkorchid4', 'thistle', 'skyblue1',
            'green', 'palegreen1', 'darkgreen', 'aquamarine', 'darkolivegreen',
            ]

    def __init__(self, app_image):
        self.image = app_image
        super(AppPalette, self).__init__((35, 35), 5, 5, margin=2)
        self.selection = 0
        self.image.rect_color = pygame.color.Color(self.colors[self.selection])

    def num_items(self):
        return len(self.colors)

    def draw_item(self, surface, item_no, rect):
        d = -2 * self.sel_width
        r = rect.inflate(d, d)
        surface.fill(pygame.color.Color(self.colors[item_no]), r)

    def click_item(self, item_no, event):
        self.selection = item_no
        self.image.rect_color = pygame.color.Color(self.colors[item_no])

    def item_is_selected(self, item_no):
        return self.selection == item_no



class AppImage(Widget):

    rect_thick = 3
    draw_thick = 1

    def __init__(self, state):
        self.state = state
        super(AppImage, self).__init__(pygame.rect.Rect(0, 0, 800, 600))
        self.mode = 'draw'
        self.rects = []
        self.start_pos = None
        self.end_pos = None
        self.draw_color = pygame.color.Color('white')
        self.rect_color = pygame.color.Color('white')

    def draw_mode(self):
        self.mode = 'draw'

    def del_mode(self):
        self.mode = 'del'
        self.start_pos = None
        self.end_pos = None

    def draw(self, surface):
        self.state.draw(surface, None)
        if self.mode == 'draw' and self.start_pos:
            rect = pygame.rect.Rect(self.start_pos[0], self.start_pos[1],
                    self.end_pos[0] - self.start_pos[0],
                    self.end_pos[1] - self.start_pos[1])
            frame_rect(surface, self.draw_color, rect, self.draw_thick)
        for (col, rect) in self.rects:
            frame_rect(surface, col, rect, self.rect_thick)

    def _make_dict(self):
        d = {}
        for col, rect in self.rects:
            d.setdefault(col, [])
            d[col].append(rect)
        return d

    def print_rects(self):
        d = self._make_dict()
        for (num, col) in enumerate(d):
            print 'Rect %d : ' % num
            for r in d[col]:
                print '   (%d, %d, %d, %d),' % (r.x, r.y, r.w, r.h)
            print

    def mouse_down(self, e):
        if self.mode == 'del':
            pos = e.pos
            cand = None
            for (col, rect) in self.rects:
                if rect.collidepoint(pos):
                    cand = (col, rect)
                    break
            if cand:
                self.rects.remove(cand)
                self.invalidate()
        elif self.mode == 'draw':
            self.start_pos = e.pos
            self.end_pos = e.pos

    def mouse_up(self, e):
        if self.mode == 'draw':
            rect = pygame.rect.Rect(self.start_pos[0], self.start_pos[1],
                    self.end_pos[0] - self.start_pos[0],
                    self.end_pos[1] - self.start_pos[1])
            rect.normalize()
            self.rects.append((self.rect_color, rect))
            self.start_pos = self.end_pos = None

    def mouse_drag(self, e):
        if self.mode == 'draw':
            self.end_pos = e.pos
            self.invalidate()

def make_button(text, action, ypos):
    button = Button(text, action=action)
    button.align = 'l'
    button.rect = pygame.rect.Rect(0, 0, 200, 40)
    button.rect.move_ip(805, ypos)
    return button

if __name__ == "__main__":
    # FIXME: should load an actual scene with current things, not just a
    # background image
    if len(sys.argv) < 2:
        print 'Please provide a scene name'
        sys.exit(0)
    pygame.display.init()
    pygame.font.init()
    display = pygame.display.set_mode((1000, 600))
    state = initial_state()
    try:
        state.set_current_scene(sys.argv[1])
        state.do_check = None
    except KeyError:
        print 'Invalid scene name'
        sys.exit(1)
    app = RootWidget(display)
    image = AppImage(state)
    app.add(image)
    draw = make_button('Draw Rect', image.draw_mode, 0)
    app.add(draw)
    delete = make_button('Del Rect', image.del_mode, 40)
    app.add(delete)
    palette = AppPalette(image)
    palette.rect.move_ip(810, 80)
    app.add(palette)
    print_rects = make_button("Print rects", image.print_rects, 240)
    app.add(print_rects)
    quit_but = make_button("Quit", app.quit, 560)
    app.add(quit_but)
    app.run()
