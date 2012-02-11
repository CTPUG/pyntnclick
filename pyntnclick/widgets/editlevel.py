from mamba.data import get_tileset_list, get_track_list
from mamba.widgets.base import Box
from mamba.widgets.text import TextWidget, TextButton, EntryTextWidget
from mamba.widgets.listbox import ListBox


class EditLevelBox(Box):
    """Edit details for a level map"""

    button_padding = 2

    def __init__(self, rect, level, post_callback=None):
        super(EditLevelBox, self).__init__(rect)
        self.level = level
        self.level_tileset = self.level.tileset.name
        self.level_track = self.level.background_track
        self.post_callback = post_callback
        self.prepare()
        self.modal = True

    def add_widget(self, cls, *args, **kw):
        clicked = kw.pop('clicked', None)
        offset = kw.pop('offset', (0, 0))
        pos = (self.widget_left + offset[0],
               self.widget_top + offset[1])
        widget = cls(pos, *args, **kw)
        if clicked:
            widget.add_callback('clicked', *clicked)
        self.add(widget)
        self.widget_top += widget.rect.height + self.button_padding
        return widget

    def prepare(self):
        self.widget_left = self.rect.left
        self.widget_top = self.rect.top

        self.add_widget(TextWidget, "Specify Level Details")

        self.filename = self.add_widget(
            EntryTextWidget, self.level.level_name, prompt="File:")

        self.levelname = self.add_widget(
            EntryTextWidget, self.level.name, prompt='Level Title:')

        self.authorname = self.add_widget(
            EntryTextWidget, self.level.author, prompt='Author:')

        # self.tileset = self.add_widget(
        #     TextButton, 'Tileset: %s' % self.level_tileset,
        #     color='white', clicked=(self.list_tilesets,))

        self.trackname = self.add_widget(
            TextButton, 'Music: %s' % self.level_track,
            color='white', clicked=(self.list_tracks,))

        self.ok_button = self.add_widget(
            TextButton, 'OK', offset=(10, 0), clicked=(self.close, True))

        self.cancel_button = self.add_widget(
            TextButton, 'Cancel', offset=(10, 0), clicked=(self.close, False))

        self.rect.width = max(self.rect.width, 400)
        self.rect.height += 5

    def change_tileset(self, ev, widget, name):
        self.level_tileset = name
        self.tileset.text = 'Tileset: %s' % name
        self.tileset.prepare()

    def change_track(self, ev, widget, name):
        self.level_track = name
        self.trackname.text = 'Music: %s' % name
        self.trackname.prepare()

    def mk_loadlist(self, title, items, callback):
        load_list = []
        for name in items:
            load_button = TextButton((0, 0), name)
            load_button.add_callback('clicked', callback, name)
            load_list.append(load_button)
        lb = ListBox((200, 200), title, load_list, 6)
        lb.parent_modal = self.modal
        self.modal = False
        self.parent.add(lb)
        lb.grab_focus()

    def list_tilesets(self, ev, widget):
        tilesets = [i for i in get_tileset_list() if i != 'common']
        self.mk_loadlist('Select Tileset', tilesets, self.change_tileset)

    def list_tracks(self, ev, widget):
        tracks = get_track_list()
        self.mk_loadlist('Select Music', tracks, self.change_track)

    def close(self, ev, widget, do_update):
        self.modal = False
        self.parent.remove(self)
        if do_update:
            self.post_callback(
                self.filename.value,
                self.levelname.value,
                self.authorname.value,
                self.level_tileset,
                self.level_track)
        return True

    def grab_focus(self):
        return self.ok_button.grab_focus()
