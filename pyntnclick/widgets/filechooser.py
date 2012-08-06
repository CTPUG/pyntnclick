# Display a paged lsit of files and directories
# Allow moving up and down directory trees

import os

from pyntnclick.widgets.base import Box
from pyntnclick.widgets.text import TextButton, LabelWidget


class FileChooser(Box):

    def __init__(self, rect, gd, curdir, ok_callback,
            page_length=12, padding=2):
        super(FileChooser, self).__init__(rect, gd)
        self.page_length = page_length
        self.page = 0
        self.ok_callback = ok_callback
        self.curdir = os.path.realpath(os.path.normpath(curdir))
        self.selected = None
        self.padding = padding
        self.dirs = []
        self.files = []
        self.modal = True
        self.prev_but = None
        self.next_but = None
        self.get_lists()
        self.fill_page()

    def get_lists(self):
        self.dirs = []
        self.files = []
        for entry in sorted(os.listdir(self.curdir)):
            path = os.path.join(self.curdir, entry)
            if os.path.isdir(path):
                self.dirs.append(entry)
            else:
                self.files.append(entry)

    def refresh(self):
        self.page = 0
        self.selected = None
        self.get_lists()
        self.fill_page()

    def _dir_button(self, entry):
        widget = TextButton((0, 0), self.gd, entry + '/',
                fontname=self.gd.constants.bold_font,
                fontsize=10)
        widget.add_callback('clicked', self.change_dir, entry)
        return widget

    def _file_button(self, entry):
        if entry == self.selected:
            # highlight
            widget = TextButton((0, 0), self.gd, entry,
                    fontsize=10, border=2, color='yellow')
        else:
            widget = TextButton((0, 0), self.gd, entry, border=0,
                    fontsize=10)
        widget.add_callback('clicked', self.change_selection, entry)
        return widget

    def fill_page(self):
        for widget in self.children[:]:
            self.remove(widget)
        start_page = self.page * self.page_length
        end_page = start_page + self.page_length
        entries = self.dirs + self.files
        top = self.rect.top + self.padding
        left = self.rect.left + self.padding
        # Add current directory at the top
        widget = LabelWidget((0, 0), self.gd, self.curdir[-30:], color='black')
        widget.rect.topleft = (left, top)
        self.add(widget)
        upbut = TextButton((left + 2 * self.padding + widget.rect.width, top),
                self.gd, u'\N{LEFTWARDS ARROW WITH HOOK}Back one level')
        upbut.add_callback('clicked', self.change_dir, os.pardir)
        self.add(upbut)
        top += max(widget.rect.height, upbut.rect.height) + 4 * self.padding
        page_top = top
        page_left = left
        top += self.padding
        for entry in entries[start_page:end_page]:
            if entry in self.dirs:
                widget = self._dir_button(entry)
            else:
                widget = self._file_button(entry)
            widget.rect.topleft = (left, top)
            self.add(widget)
            top += widget.rect.height + self.padding
            page_left = max(page_left, left + widget.rect.width + self.padding)
        # Add page list buttons
        if not self.prev_but:
            self.prev_but = TextButton((0, 0), self.gd, u'\N{UPWARDS ARROW}')
            self.prev_but.add_callback('clicked', self.change_page, -1)
        self.prev_but.rect.topleft = (page_left, page_top)
        if not self.next_but:
            self.next_but = TextButton((0, 0), self.gd, u'\N{DOWNWARDS ARROW}')
            self.next_but.add_callback('clicked', self.change_page, +1)
        page_top = max(top - self.next_but.rect.height,
                self.prev_but.rect.bottom + self.padding)
        self.next_but.rect.topleft = (page_left, page_top)
        if self.page > 0:
            self.prev_but.enable()
        else:
            self.prev_but.disable()
        if end_page + 1 < len(entries):
            self.next_but.enable()
        else:
            self.next_but.disable()
        self.add(self.next_but)
        self.add(self.prev_but)
        # Add OK and Cancel buttons
        top = max(self.prev_but.rect.bottom + self.padding,
                top + 2 * self.padding)
        ok_but = TextButton((left, top), self.gd, 'OK')
        ok_but.add_callback('clicked', self.ok)
        self.add(ok_but)
        cancel_but = TextButton(
                (left + ok_but.rect.width + 4 * self.padding, top),
                self.gd, 'Cancel')
        cancel_but.add_callback('clicked', self.cancel)
        self.add(cancel_but)

    def change_page(self, ev, widget, change):
        self.page += change
        self.fill_page()
        return True

    def change_dir(self, ev, widget, newdir):
        """Change directory and refresh the widget."""
        self.curdir = os.path.normpath(os.path.join(self.curdir, newdir))
        self.page = 0
        self.selected = None
        self.get_lists()
        self.fill_page()

    def change_selection(self, ev, widget, entry):
        """Update selection"""
        self.selected = entry
        self.fill_page()

    def cancel(self, ev, widget):
        if hasattr(self.parent, 'paused'):
            self.parent.paused = False
        self.parent.remove(self)
        return True

    def ok(self, ev, widget):
        if hasattr(self.parent, 'paused'):
            self.parent.paused = False
        self.parent.remove(self)
        if self.selected:
            self.ok_callback(os.path.normpath(os.path.join(self.curdir,
                self.selected)))
        return True
