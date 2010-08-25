# Quickly hacked together helper for working out
# interactive regions in Suspended Sentence

import sys

from albow.root import RootWidget
from albow.utils import frame_rect
from albow.controls import Image, Button
from albow.palette_view import PaletteView
from pygame.locals import SWSURFACE
import pygame
from pygame.colordict import THECOLORS


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



class AppImage(Image):

    def __init__(self, filename):
        draw_image = pygame.image.load(filename)
        super(AppImage, self).__init__(draw_image)
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
        super(AppImage, self).draw(surface)
        if self.mode == 'draw' and self.start_pos:
            rect = pygame.rect.Rect(self.start_pos[0], self.start_pos[1],
                    self.end_pos[0] - self.start_pos[0],
                    self.end_pos[1] - self.start_pos[1])
            frame_rect(surface, self.draw_color, rect, 2)
        for (col, rect) in self.rects:
            frame_rect(surface, col, rect, 1)

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
                print '   (%d, %d, %d, %d)' % (r.x, r.y, r.w, r.h)
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


if __name__ == "__main__":
    # FIXME: should load an actual scene with current things, not just a
    # background image
    pygame.display.init()
    pygame.font.init()
    display = pygame.display.set_mode((1000, 600))
    imagefile = sys.argv[1]
    app = RootWidget(display)
    image = AppImage(imagefile)
    app.add(image)
    draw = Button('Draw Rect', action=image.draw_mode)
    app.add(draw)
    draw.rect.move_ip(810, 0)
    delete = Button('Del Rect', action=image.del_mode)
    app.add(delete)
    delete.rect.move_ip(810, 50)
    palette = AppPalette(image)
    palette.rect.move_ip(810, 100)
    app.add(palette)
    print_rects = Button("Print rects", action=image.print_rects)
    app.add(print_rects)
    print_rects.rect.move_ip(810, 300)
    quit_but = Button("Quit", action=app.quit)
    app.add(quit_but)
    quit_but.rect.move_ip(810, 500)
    app.run()
