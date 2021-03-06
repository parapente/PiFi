# -*- coding: utf-8

__author__="Theofilos Intzoglou"
__date__ ="$29 Σεπ 2010 10:46:21 πμ$"

import Queue

class ZUndo:
    pcstk = None
    stackstk = None
    changestk = None
    retval = None

    def __init__(self):
        self.pcstk = Queue.LifoQueue(0) # Infinite queue
        self.stackstk = Queue.LifoQueue(0)
        self.changestk = Queue.LifoQueue(0)
        self.retval = Queue.LifoQueue(3)

    def push(self,pc,stack,changes):
        self.pcstk.put(pc)
        self.stackstk.put(stack)
        self.changestk.put(changes)

    def pop(self):
        # I have to return the values of 3 different queues
        self.retval.put(self.pcstk.get())
        self.retval.put(self.stackstk.get())
        self.retval.put(self.changestk.get())
        return self.retval