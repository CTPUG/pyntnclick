from pyntnclick.constants import GameConstants

# Anything here has to be explicitly translated
# This module is imported before we've set up i18n
_ = lambda x: x


class SSConstants(GameConstants):
    title = _('Suspended Sentence')
    icon = 'suspended_sentence24x24.png'
    short_name = 'suspended-sentence'
