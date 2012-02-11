from pyntntclick.widgets.base import Container
from pyntntclick.widgets.text import TextButton


class ToolListWidget(Container):
    """List of other widgets, with some paging trickery"""

    def __init__(self, rect, widget_list, page_length,
                 padding=2):
        widget_list.sort(key=lambda w: w.text)
        self.widget_list = widget_list
        self.page_length = page_length
        self.padding = padding
        self.page = 0
        super(ToolListWidget, self).__init__(rect)
        self.prev_but = None
        self.next_but = None
        self.fill_page()
        self.focussable = True

    def fill_page(self):
        for widget in self.children[:]:
            self.remove(widget)
        start_page = self.page * self.page_length
        end_page = start_page + self.page_length
        button_height = self.rect.top + self.padding
        button_left = self.rect.left + self.padding
        for widget in self.widget_list[start_page:end_page]:
            widget.rect.topleft = (button_left, button_height)
            self.add(widget)
            button_height += widget.rect.height + self.padding
        if not self.prev_but:
            self.prev_but = TextButton((button_left, button_height),
                                       u'\N{LEFTWARDS ARROW}')
            self.prev_but.add_callback('clicked', self.change_page, -1)
        else:
            self.prev_but.rect.top = max(button_height, self.prev_but.rect.top)
        if not self.next_but:
            self.next_but = TextButton((button_left + 100, button_height),
                    u'\N{RIGHTWARDS ARROW}')
            self.next_but.add_callback('clicked', self.change_page, 1)
        else:
            self.next_but.rect.top = max(button_height, self.next_but.rect.top)
        if start_page > 0:
            self.prev_but.enable()
        else:
            self.prev_but.disable()
        if end_page < len(self.widget_list):
            self.next_but.enable()
        else:
            self.next_but.disable()
        self.add(self.prev_but)
        self.add(self.next_but)
        for widget in self.children[:]:
            if widget in self.widget_list:
                # Standardise widdths
                widget.rect.width = self.rect.width - 2
                widget.prepare()

    def change_page(self, ev, widget, change):
        self.page += change
        self.fill_page()
        return True
