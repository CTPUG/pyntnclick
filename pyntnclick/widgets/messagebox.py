from pyntnclick.constants import FONT_SIZE
from pyntnclick.widgets.base import Box
from pyntnclick.widgets.text import TextWidget, TextButton


class MessageBox(Box):

    def __init__(self, rect, text, post_callback=None, color='red',
            fontsize=FONT_SIZE):
        super(MessageBox, self).__init__(rect)
        self.text = text
        self.font_size = fontsize
        self.post_callback = post_callback
        self.color = color
        self.prepare()
        self.modal = True

    def prepare(self):
        cont = TextWidget((0, 0), "Press [OK] or Enter to continue",
                fontsize=self.font_size)
        widgets = []
        width = cont.rect.width
        for line in self.text.split('\n'):
            message = TextWidget((0, 0), line, color=self.color,
                    fontsize=self.font_size)
            widgets.append(message)
            width = max(width, message.rect.width)
        widgets.append(cont)
        top = self.rect.top + 10
        left = self.rect.left + 5
        for widget in widgets:
            pos = (left + width / 2 - widget.rect.width / 2, top)
            widget.rect.topleft = pos
            top += widget.rect.height + 5
            self.add(widget)
        self.ok_button = ok_button = TextButton((0, 0), 'OK')
        ok_pos = (self.rect.left + 5 + width / 2 - ok_button.rect.width / 2,
                top + 5)
        ok_button.rect.topleft = ok_pos
        ok_button.add_callback('clicked', self.close)
        self.add(ok_button)
        self.rect.height += 5

    def close(self, ev, widget):
        if hasattr(self.parent, 'paused'):
            self.parent.paused = False
        self.parent.remove(self)
        if self.post_callback:
            self.post_callback()
        if getattr(self, 'parent_modal', False):
            self.parent.modal = True

    def grab_focus(self):
        return self.ok_button.grab_focus()
