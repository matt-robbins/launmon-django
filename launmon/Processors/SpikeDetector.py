import sys

class SpikeDetector():
    def __init__(self,thresh,rthresh,allow_neg=False):
        self.thresh = thresh
        self.rthresh = rthresh
        self.prev_sample = 0
        self.pcount = 0
        self.ncout = 0
        self.start = None
        self.allow_neg = allow_neg

    def process_sample(self,sample):
        rv = 0
        if (sample - self.prev_sample > self.thresh):
            if (self.start is None):
                self.pcount = 0
                self.start = self.prev_sample
            self.pcount += 1
        elif (self.allow_neg and (sample - self.prev_sample < -self.thresh)):
            if (self.start is None):
                self.ncount = 0
                self.start = self.prev_sample
            self.pcount += 1

        elif (self.start is not None):
            rv = self.prev_sample - self.start
            self.start = None

        self.prev_sample = sample   
        if (rv > self.rthresh or rv < -self.rthresh): 
            return rv,self.pcount
        else:
            return 0,0
        
    def reset(self):
        self.__init__(self.thresh,self.rthresh)

if __name__ == "__main__":
    p = SpikeDetector(10,60)
    p.cal = 1
    lc = 0
    for line in sys.stdin:

        spike,count = p.process_sample(float(line))
        lc += 1
        if (spike):
            print("%d: %dx%d" % (lc,spike,count))