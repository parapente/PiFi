# -*- coding: utf-8

from array import array
#import Queue

__author__="Theofilos Intzoglou"
__date__ ="$7 Ιουλ 2009 3:35:43 μμ$"

class ZStack:
    top = None
    queue = None
    frames = None
    local_vars = None
    local_vars_num = 15

    def __init__(self):
        #self.queue = Queue.LifoQueue(100*1024*1024)
        #self.frames = Queue.LifoQueue(10*1024*1024)
        self.queue = []
        self.frames = []
        self.local_vars = array('H')
        for i in xrange(15):
            self.local_vars.append(0)

    def push(self,n):
        self.queue.append(n)

    def pop(self):
        return self.queue.pop()

    def push_frame(self,n):
        self.frames.append(n)

    def pop_frame(self):
        return self.frames.pop()

    def push_local_vars(self):
        for i in xrange(15):
            #print "Pushed:", self.local_vars[i]
            self.frames.append(self.local_vars[i])
        #self.frames.append(self.local_vars)

    def pop_local_vars(self):
        for i in xrange(15):
            self.local_vars[14 - i] = self.frames.pop()
        #for i in xrange(15):
        #    print "Popped:", self.local_vars[i]
        #self.local_vars = self.frames.pop()
