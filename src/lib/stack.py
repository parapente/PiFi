# -*- coding: utf-8

from array import array
import Queue

__author__="Theofilos Intzoglou"
__date__ ="$7 Ιουλ 2009 3:35:43 μμ$"

class ZStack:
    top = None
    queue = None
    frames = None
    local_vars = None
    local_vars_num = 15

    def __init__(self):
        self.queue = Queue.LifoQueue(100*1024*1024)
        self.frames = Queue.LifoQueue(10*1024*1024)
        self.local_vars = array('H')
        for i in range(15):
            self.local_vars.append(0)

    def push(self,n):
        self.queue.put(n)

    def pop(self):
        return self.queue.get()

    def push_frame(self,n):
        self.frames.put(n)

    def pop_frame(self):
        return self.frames.get()

    def push_local_vars(self):
        for i in range(15):
            #print "Pushed:", self.local_vars[i]
            self.frames.put(self.local_vars[i])

    def pop_local_vars(self):
        for i in range(15):
            n = self.frames.get()
            #print n
            self.local_vars[14 - i] = n
        #for i in range(15):
        #    print "Popped:", self.local_vars[i]
