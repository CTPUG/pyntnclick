# 10 minute to help working out interactive regions in Suspended Sentence

import sys

from albow.root import RootWidget
from albow.utils import frame_rect
from albow.controls import Image, Button
from albow.palette_view import PaletteView
from pygame.locals import SWSURFACE
import pygame
from pygame.colordict import THECOLORS

class AppImage(Image):

    def __init__(self, filename):
        image = pygame.image.load(filename)
        super(AppImage, self).__init__(image)
        self.mode = 'draw'
        self.rects = []
        self.start_pos = None
        self.end_pos = None
        self.draw_color = pygame.color.Color('white')
        self.rect_color = pygame.color.Color('red')

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

    def print_rects(self):
        for (col, rect) in self.rects:
            print col, rect

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
    pygame.display.init()
    pygame.font.init()
    display = pygame.display.set_mode((1000, 600))
    filename = sys.argv[1]
    app = RootWidget(display)
    image = AppImage(filename)
    app.add(image)
    draw = Button('Draw Rect', action=image.draw_mode)
    app.add(draw)
    draw.rect.move_ip(810, 0)
    delete = Button('Del Rect', action=image.del_mode)
    app.add(delete)
    delete.rect.move_ip(810, 50)
    print_rects = Button("Print rects", action=image.print_rects)
    app.add(print_rects)
    print_rects.rect.move_ip(810, 100)
    quit_but = Button("Quit", action=app.quit)
    app.add(quit_but)
    quit_but.rect.move_ip(810, 500)
    app.run()
