# -*- coding: utf-8

import random

__author__ = "Theofilos Intzoglou"
__date__ = "$22 Ιουν 2009 12:28:10 πμ$"


class ZRandom:
    mode = 0  # Random Mode Enabled by default
    r = None

    def __init__(self):
        self.r = random.Random()

    def set_seed(self, s):
        if s == 0:
            self.r.seed()
        else:
            self.r.seed(s)
        self.mode = s

    def get_random(self, e):
        return self.r.randint(1, e)
