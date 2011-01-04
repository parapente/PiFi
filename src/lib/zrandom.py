# -*- coding: utf-8

import random

__author__="oscar"
__date__ ="$22 Ιουν 2009 12:28:10 πμ$"

class ZRandom:
    mode = 0; # Random Mode Enabled by default
    r = None;
    start = 1;
    end = 0;
    def __init__(self):
        self.r = random.Random();
        self.r.seed();

    def set_seed(self,s):
        self.r.seed(s);

    def set_range(self,e):
        self.end = e;

    def set_mode(self,m):
        self.mode = m;
        if m == 0: # Mode 0 is Random Mode, Mode 1 is Predictable (use a given seed)
            self.r.seed();

    def get_random(self):
        return self.r.randint(self.start, self.end);