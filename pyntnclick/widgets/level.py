from pygame.rect import Rect
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from pygame.key import set_repeat

from mamba.widgets.base import Widget
from mamba.constants import TILE_SIZE
from mamba.snake import Snake
from mamba.engine import FlipArrowsEvent, ReplayEvent


class EditLevelWidget(Widget):
    def __init__(self, level, offset=(0, 0)):
        self.level = level
        level_rect = Rect(offset, level.get_size())
        self.main_tool = None
        self.tool = None
        self.drawing = False
        self.last_click_pos = None
        self.tile_mode = True  # Flag for sprite interactions
        super(EditLevelWidget, self).__init__(level_rect)
        self.add_callback(MOUSEBUTTONDOWN, self.place_tile)
        self.add_callback(MOUSEBUTTONUP, self.end_draw)
        self.add_callback(MOUSEMOTION, self.draw_tiles)
        self.add_callback(FlipArrowsEvent, self.flip_arrows)
        self.add_callback(ReplayEvent, self.handle_replay)
        self.snake = None
        self.snake_alive = False
        self.replay_data = []
        self.last_run = []
        self.replay_pos = 0

    def get_replay(self):
        return self.replay_data[:]

    def replay(self, run=None):
        if run is None:
            # We exclude the last couple of steps, so we don't redo
            # the final crash in this run
            run = self.last_run[:-4]
        if len(run) > 0:
            self.start_test()
            ReplayEvent.post(run, 0)

    def handle_replay(self, ev, widget):
        self.apply_action(ev.run[ev.replay_pos])
        if ev.replay_pos < len(ev.run) - 1:
            ReplayEvent.post(ev.run, ev.replay_pos + 1)

    def start_test(self):
        self.level.update_tiles_ascii()
        self.last_run = self.replay_data
        self.replay_data = []
        self.level.restart()
        tile_pos, orientation = self.level.get_entry()
        self.snake = Snake(tile_pos, orientation)
        set_repeat(40, 100)
        self.snake_alive = True

    def stop_test(self):
        self.snake = None
        self.snake_alive = False
        self.level.restart()
        set_repeat(0, 0)

    def draw(self, surface):
        self.level.draw(surface)
        if self.snake:
            self.snake.draw(surface)

    def kill_snake(self):
        """Prevent user interaction while snake is dead"""
        self.snake_alive = False

    def restart(self):
        self.start_test()

    def interact(self, segment):
        if not self.snake or not self.snake_alive:
            return
        tiles = segment.filter_collisions(self.level.sprites)
        for tile in tiles:
            tile.interact(self, segment)

    def get_sprite(self, sprite_id):
        return self.level.extra_sprites[sprite_id]

    def apply_action(self, orientation):
        self.replay_data.append(orientation)
        if not self.snake or not self.snake_alive:
            return
        # We choose numbers that are close to, but not exactly, move 0.5 tiles
        # to avoid a couple of rounding corner cases in the snake code
        if orientation is None or orientation == self.snake.orientation:
            self.snake.update(9.99 / self.snake.speed, self)
        else:
            self.snake.send_new_direction(orientation)
            self.snake.update(9.99 / self.snake.speed, self)

    def set_tool(self, new_tool):
        self.main_tool = new_tool
        self.tool = new_tool

    def end_draw(self, event, widget):
        self.drawing = False

    def draw_tiles(self, event, widget):
        if self.drawing and self.tool:
            # FIXME: Need to consider leaving and re-entering the widget
            self.update_tile(self.convert_pos(event.pos))

    def flip_arrows(self, ev, widget):
        self.level.flip_arrows()

    def place_tile(self, event, widget):
        if self.tile_mode:
            if event.button == 1:  # Left button
                self.tool = self.main_tool
            else:
                self.tool = '.'
            self.drawing = True
            if self.tool:
                self.update_tile(self.convert_pos(event.pos))
        else:
            self.last_click_pos = self.convert_pos(event.pos)
            self.drawing = False

    def convert_pos(self, pos):
        return (pos[0] / TILE_SIZE[0], pos[1] / TILE_SIZE[1])

    def update_tile(self, tile_pos):
        """Update the tile at the current mouse position"""
        if self.check_paused():
            return  # Do nothing if dialogs showing
        # We convert our current position into a tile position
        # and replace the tile with the current tool
        old_tile = self.level.get_tile(tile_pos)
        if self.tool == '.' and old_tile is None:
            return
        elif old_tile is not None and old_tile.tile_char == self.tool:
            return
        self.level.replace_tile(tile_pos, self.tool)

    def check_paused(self):
        return hasattr(self.parent, 'paused') and self.parent.paused
