# widgets.py
# Copyright Boomslang team, 2010 (see COPYING File)

"""Custom Albow widgets"""

import albow.controls


class BoomLabel(albow.controls.Label):

    def set_margin(self, margin):
        """Add a set_margin method that recalculates the label size"""
        old_margin = self.margin
        w, h = self.size
        d = margin - old_margin
        self.margin = margin
        self.size = (w + 2 * d, h + 2 * d)

