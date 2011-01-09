# -*- coding: utf-8

__author__="Theofilos Intzoglou"
__date__ ="$9 Ιαν 2011 1:56:17 πμ$"

class PlugSkel:
    level = None

    def set_debug_level(self,lvl):
        self.level = lvl

    def debugprint(self,msg,lvl):
        if (lvl <= self.level):
            print msg