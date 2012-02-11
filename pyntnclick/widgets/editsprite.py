from mamba.widgets.base import Box
from mamba.widgets.text import TextWidget, TextButton, EntryTextWidget


class EditSpriteBox(Box):
    """Edit details for a special sprite on the level map"""

    def __init__(self, rect, sprite_pos, sprite_info, post_callback=None):
        super(EditSpriteBox, self).__init__(rect)
        self.sprite_pos = sprite_pos
        sprite_cls_name, sprite_cls, sprite_id, args = sprite_info
        self.sprite_cls_name = sprite_cls_name
        self.sprite_cls = sprite_cls
        if sprite_id:
            self.sprite_id = sprite_id
        else:
            self.sprite_id = ''
        self.sprite_parameters = args
        self.new_sprite_parameters = []
        self.post_callback = post_callback
        self.parameter_widgets = []
        self.prepare()
        self.modal = True

    def prepare(self):
        title = TextWidget(self.rect, "Specify Sprite Details")
        self.add(title)
        height = self.rect.top + title.rect.height + 2
        self.edit_sprite_name = TextWidget((self.rect.left, height),
                'Sprite Class: %s' % self.sprite_cls.name)
        self.add(self.edit_sprite_name)
        height += self.edit_sprite_name.rect.height + 2
        self.edit_sprite_id = EntryTextWidget((self.rect.left + 20, height),
                self.sprite_id, prompt='Sprite Id (required):')
        self.add(self.edit_sprite_id)
        height += self.edit_sprite_id.rect.height + 2
        poss_params = self.sprite_cls.get_sprite_args()
        if not poss_params:
            self.sprite_param = TextWidget((self.rect.left, height),
                    'No Parameters')
            self.add(self.sprite_param)
            height += self.sprite_param.rect.height + 2
        else:
            self.sprite_param = TextWidget((self.rect.left, height),
                    'Parameters')
            self.add(self.sprite_param)
            height += self.sprite_param.rect.height + 2
            for i, param_tuple in enumerate(poss_params):
                if len(self.sprite_parameters) > i:
                    value = self.sprite_parameters[i]
                else:
                    value = None
                if param_tuple[1] is None:
                    # Text Entry Parameter
                    if value is None:
                        value = ''
                    edit_widget = EntryTextWidget(
                            (self.rect.left + 20, height),
                            value, prompt=param_tuple[0])
                    self.parameter_widgets.append(edit_widget)
                    self.add(edit_widget)
                    height += edit_widget.rect.height
                elif isinstance(param_tuple[1], tuple):
                    # We have a list of possible values
                    if value is None:
                        value = param_tuple[1][0]  # Take the first
                    mylist = []
                    list_width = 0
                    list_height = 0
                    for choice in param_tuple[1]:
                        list_parameter = TextWidget(
                                (self.rect.left + 20, height),
                                '%s: %s' % (param_tuple[0], choice))
                        # So we can pull it out of this later
                        list_parameter.choice = choice
                        list_width = max(list_width, list_parameter.rect.width)
                        change_list = TextButton(
                                (list_parameter.rect.right + 5, height),
                                'Next Option')
                        change_list.add_callback('clicked', self.change_list,
                                choice, param_tuple[1], mylist)
                        mylist.append((list_parameter, change_list))
                        list_height = max(list_height, change_list.rect.height,
                                list_parameter.rect.height)
                        if choice == value:
                            self.add(list_parameter)
                            self.add(change_list)
                    for x in mylist:
                        x[1].rect.left = self.rect.left + list_width + 25
                        if x[0].rect.height < list_height:
                            x[0].rect.top += (list_height -
                                    x[0].rect.height) / 2
                    height += max(list_parameter.rect.height,
                            change_list.rect.height)
                    self.parameter_widgets.append(mylist)
                # FIXME: Other cases
        height += 20
        self.ok_button = TextButton((self.rect.left + 10, height), 'OK')
        self.ok_button.add_callback('clicked', self.close, True)
        self.add(self.ok_button)
        cancel_button = TextButton((self.ok_button.rect.right + 10, height),
                'Cancel')
        cancel_button.add_callback('clicked', self.close, False)
        self.add(cancel_button)
        self.rect.width = max(self.rect.width, 400)
        self.rect.height += 5

    def change_list(self, ev, widget, cur_choice, all_choices, widget_list):
        pos = all_choices.index(cur_choice)
        if pos == len(all_choices) - 1:
            next_pos = 0
        else:
            next_pos = pos + 1
        self.remove(widget_list[pos][0])
        self.remove(widget_list[pos][1])
        self.add(widget_list[next_pos][0])
        self.add(widget_list[next_pos][1])

    def close(self, ev, widget, do_update):
        if do_update:
            self.new_sprite_parameters = []
            for param in self.parameter_widgets:
                if hasattr(param, 'value'):
                    self.new_sprite_parameters.append(param.value)
                elif isinstance(param, list):
                    # Find the selected one
                    for choice, _ in param:
                        if choice in self.children:
                            # Is selected, so we grab this choice
                            self.new_sprite_parameters.append(choice.choice)
                            break
            self.sprite_id = self.edit_sprite_id.value
            sprite = self.make_sprite()
            if not self.post_callback(sprite):
                return  # Call-back failed, so don't remove
        self.parent.paused = False
        self.parent.remove(self)
        return True

    def make_sprite(self):
        """Convert values to a sprite line"""
        pos = "%s, %s" % self.sprite_pos
        sprite_string = "%s: %s %s %s" % (pos, self.sprite_cls_name,
                self.sprite_id, " ".join(self.new_sprite_parameters))
        return sprite_string

    def grab_focus(self):
        return self.ok_button.grab_focus()
