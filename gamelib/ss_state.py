"""The Custom state object for Suspended Sentence"""

from pyntnclick.state import GameState

class SSState(GameState):

   def get_jim_state(self):
       """Check JIM's health"""
       return self['bridge']['ai status']

   def loop_ai(self):
       """Make JIM loopy"""
       self['bridge']['ai status'] = 'looping'

   def break_ai(self):
       self['bridge']['ai status'] = 'dead'
