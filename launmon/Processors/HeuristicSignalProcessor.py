from .SignalProcessor import State, SignalProcessor
from .SpikeDetector import SpikeDetector
import sys
import math

# "Expert System" classifier for laundry status given current.
class HeuristicSignalProcessor(SignalProcessor):
    def __init__(self, 
            spike_max=1.0, spike_th=0.05, wash_th=0.25, dry_th=5, 
            idle_time=30, both_idle_time=30, cal=1.0):
        super().__init__()

        self.count = 0
        self.spike_max = spike_max
        self.wash_spike_idle = 0
        self.wash_th = wash_th
        self.wash_time = 0
        self.dry_time = 0
        self.dry_th = dry_th
        self.null_count = 0
        self.idle_time = idle_time
        self.both_idle_time = both_idle_time
        self.both_idle_count = 0
        self.dry_min = 0
        self.cal = cal
        self.prev_sample = 0
        self.state = State.NONE
        self.spike_det = SpikeDetector(thresh=spike_th,rthresh=wash_th)

    def reset(self):
        super().reset()
        self.__init__()
        self.spike_det.reset()

    def _process_sample(self, sample):

        spike,spike_count = self.spike_det.process_sample(sample)

        self.wash_spike_idle +=1
        if (spike > 0 and spike < self.spike_max*1.5 and (self.dry_time == 0 or self.dry_time > 10)):
            # print("%d: washy spike! %dx%dx%d" % (self.count,spike,spike_count,self.wash_spike_idle))
            self.wash_spike_idle = 0

        diff = sample - self.prev_sample
        self.prev_sample = sample

        self.count += 1
        if self.count < 30:
            return State.NONE

        state = self.state
        new_state = state

        # keep track of how long we've been under the wash threshold
        self.null_count = self.null_count + 1 if sample < self.wash_th else 0

        if (state == State.NONE): # NONE
            if (sample > self.dry_th):
                new_state = State.DRY
            elif (spike > self.wash_th):
                new_state = State.WASH
    
        elif (state == State.WASH): # WASH
            self.wash_time += 1
            if (diff > self.dry_th or (spike > self.dry_th and spike_count <= 3)):
                new_state = State.BOTH
                self.dry_time = 0
            elif (self.wash_time > 120 and self.null_count > 10):
                new_state = State.NONE

        elif (state == State.DRY): # DRY
            self.dry_time += 1
            if sample < self.dry_th:
                new_state = State.NONE
            if sample < self.dry_min:
                self.dry_min = sample
            if spike > self.wash_th and spike < self.spike_max and self.dry_time > 10:
                new_state = State.BOTH
            
        elif (state == State.BOTH): # BOTH    
            self.dry_time += 1      
            # failsafe timeout -- if we don't see any wash-y spikes for 400 seconds, we're not washing
            if (self.wash_spike_idle > 400):
                print("WASH SPIKE TIMEOUT!")
                new_state = State.DRY      

            if (self.wash_time > 1200 and self.dry_time > 20):
                if (sample < (self.dry_min + self.wash_th)):
                    self.both_idle_count += 1
                    if (self.both_idle_count > self.both_idle_time):
                        new_state = State.DRY
                else:
                    self.both_idle_count = 0

            if (sample < self.dry_th):
                new_state = State.WASH
            elif (sample < self.dry_min):
                self.dry_min = sample
           
                
        # regardless of current state, reset to null if we time out on low current
        if (self.null_count >= self.idle_time and self.state != State.NONE):
            new_state = State.NONE

        # cycle timer on washer
        if (self.state == State.WASH or self.state == State.BOTH):
            self.wash_time += 1
            pass

        # STATE TRANSITION EXTRA OPERATIONS
        if new_state != state:
            if (new_state == State.NONE):
                self.wash_time = 0
                self.wash_spike_idle = 0
                self.count = 0
            if (new_state == State.DRY):
                self.wash_time = 0
                self.dry_time = 0
                self.dry_min = sample
            if (new_state == State.BOTH):
                self.both_idle_count = 0
                if (self.dry_min == 0):
                    self.dry_min = sample

        self.state = new_state
        return new_state

if __name__ == "__main__":


    p = HeuristicSignalProcessor()
    p.test_stdin()