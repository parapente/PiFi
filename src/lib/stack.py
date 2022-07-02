# -*- coding: utf-8

from array import array
#import Queue

__author__ = "Theofilos Intzoglou"
__date__ = "$7 Ιουλ 2009 3:35:43 μμ$"


class ZStack:
    top = None
    queue = None
    frames = None
    local_vars = None
    local_vars_num = 15

    def __init__(self):
        #self.queue = Queue.LifoQueue(100*1024*1024)
        #self.frames = Queue.LifoQueue(10*1024*1024)
        self.queue = [0]*1000
        self.queuepos = 0
        self.queuemaxpos = 1000
        self.frames = [0]*3000
        self.framespos = 0
        self.framesmaxpos = 3000
        self.local_vars = []
        self.local_vars_num = 0
        #self.local_vars = array('H')
        # for i in xrange(15):
        #    self.local_vars.append(0)

    def push(self, n):
        if (self.queuepos < self.queuemaxpos):
            self.queue[self.queuepos] = n
            self.queuepos += 1
        else:
            self.queue.append(n)
            self.queuepos += 1
            self.queuemaxpos += 1

    def pop(self):
        self.queuepos -= 1
        return self.queue[self.queuepos]

    def push_frame(self, n):
        if (self.framespos < self.framesmaxpos):
            self.frames[self.framespos] = n
            self.framespos += 1
        else:
            self.frames.append(n)
            self.framespos += 1
            self.framesmaxpos += 1

    def pop_frame(self):
        self.framespos -= 1
        return self.frames[self.framespos]

    def push_local_vars(self):
        if (self.framespos < self.framesmaxpos):
            #self.frames[self.framespos] = self.local_vars.tolist()
            self.frames[self.framespos] = self.local_vars[:]
            self.framespos += 1
        else:
            # self.frames.append(self.local_vars.tolist())
            self.frames.append(self.local_vars[:])
            self.framespos += 1
            self.framesmaxpos += 1

    def pop_local_vars(self):
        self.framespos -= 1
        self.local_vars = self.frames[self.framespos]
        #data = self.frames[self.framespos]
        # for i in xrange(15):
        #    self.local_vars[i] = data[i]

    def push_eval_stack(self):
        self.push_frame(list(self.queue[:self.queuepos]))
        self.queuepos = 0
        self.queuemaxpos = 1000
        self.queue = [0]*1000

    def pop_eval_stack(self):
        self.queue = self.pop_frame()
        self.queuepos = len(self.queue)
        self.queuemaxpos = self.queuepos
