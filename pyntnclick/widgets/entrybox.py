from pygame.constants import K_ESCAPE, K_RETURN, K_KP_ENTER, KEYDOWN

from mamba.widgets.base import Box
from mamba.widgets.text import TextWidget, TextButton, EntryTextWidget


class EntryBox(Box):

    def __init__(self, rect, text, init_value, accept_callback=None,
            color='white', entry_color='red'):
        super(EntryBox, self).__init__(rect)
        self.text = text
        self.accept_callback = accept_callback
        self.color = color
        self.entry_color = entry_color
        self.value = init_value
        self.prepare()
        self.modal = True

    def prepare(self):
        message = TextWidget((self.rect.left + 50, self.rect.top + 2),
                self.text, color=self.color)
        self.rect.width = message.rect.width + 100
        self.add(message)
        self.entry_text = EntryTextWidget((self.rect.left + 5,
            self.rect.top + message.rect.height + 5), self.value,
            focus_color=self.entry_color)
        self.add_callback(KEYDOWN, self.edit)
        self.add(self.entry_text)
        ok_button = TextButton((self.rect.left + 50,
            self.entry_text.rect.bottom), 'Accept')
        ok_button.add_callback('clicked', self.close, True)
        self.add(ok_button)
        cancel_button = ok_button = TextButton(
                (ok_button.rect.right + 10, self.entry_text.rect.bottom),
                'Cancel')
        cancel_button.add_callback('clicked', self.close, False)
        self.add(cancel_button)
        self.rect.height += 5

    def close(self, ev, widget, ok):
        if self.accept_callback and ok:
            self.value = self.entry_text.value
            if self.accept_callback(self.value):
                if self.parent:
                    if hasattr(self.parent, 'paused'):
                        self.parent.paused = False
                    self.parent.remove(self)
            # Don't remove if the accept callback failed
            return
        if hasattr(self.parent, 'paused'):
            self.parent.paused = False
        self.parent.remove(self)
        return True

    def edit(self, ev, widget):
        if ev.key == K_ESCAPE:
            self.close(ev, widget, False)
            return True
        elif ev.key in (K_RETURN, K_KP_ENTER):
            self.close(ev, widget, True)
            return True
        return False  # pass this up to parent

    def grab_focus(self):
        self.entry_text.grab_focus()
