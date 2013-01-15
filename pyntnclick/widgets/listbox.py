from pyntnclick.widgets.base import Box
from pyntnclick.widgets.toollist import ToolListWidget
from pyntnclick.widgets.text import TextWidget, TextButton


class ListBox(Box):

    def __init__(self, rect, gd, text, widget_list, page_length=8):
        super(ListBox, self).__init__(rect, gd)
        self.message = TextWidget(rect, text)
        self.toolbar = ToolListWidget(rect, widget_list, page_length)
        self.modal = True

    def prepare(self):
        width = max(self.toolbar.rect.width, self.message.rect.width)
        if width > self.message.rect.width:
            message_pos = (self.rect.left + width / 2
                    - self.message.rect.width / 2, self.rect.top)
        else:
            message_pos = (self.rect.left, self.rect.top + 5)
        tool_pos = (self.rect.left,
                self.rect.top + self.message.rect.height + 2)
        self.message.rect.topleft = message_pos
        self.toolbar.rect.topleft = tool_pos
        self.toolbar.fill_page()  # Fix alignment
        self.add(self.message)
        self.add(self.toolbar)
        self.ok_button = ok_button = TextButton((0, 0), 'OK')
        ok_pos = (self.rect.left + width / 2 - ok_button.rect.width / 2,
                tool_pos[1] + 2 + self.toolbar.rect.height)
        ok_button.rect.topleft = ok_pos
        ok_button.add_callback('clicked', self.close)
        self.add(ok_button)
        self.rect.height += 5

    def close(self, ev, widget):
        if hasattr(self.parent, 'paused'):
            self.parent.paused = False
        self.parent.remove(self)
        return True
