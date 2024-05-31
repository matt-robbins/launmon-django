from .SignalProcessor import SignalProcessor, State as LaundryState
from collections import deque
import statistics as st
from enum import Enum

class BinaryStateTimer():
    def __init__(self):
        self.count = 0

    def process(self,state):
        self.count = self.count + 1 if state else 0
        return self.count
    
class State(Enum):
    idle = 0
    start = 1
    spikes = 2
    high = 3
    spin = 4
    gap = 5
    end = 6

class StateSignalProcessor(SignalProcessor):
    def __init__(self, 
            trig_thresh=0.05, 
            high_thresh=0.5, 
            spike_thresh=1.0,
            spin_thresh=2.0,
            flat_thresh=0.05, 
            idle_thresh=0.15,
            spike_time=100,
            high_time=20,
            spin_time=20,
            gap_time=150,
            end_time=20,
            idle_time=200,
            buflen=30,
            dead_time=60):
        super().__init__()

        self.trig_th = trig_thresh
        self.spike_th = spike_thresh
        self.high_th = high_thresh
        self.spin_th = spin_thresh
        self.flat_th = flat_thresh
        self.idle_th = idle_thresh

        self.spike_time = spike_time
        self.high_time = high_time
        self.spin_time = spin_time
        self.gap_time = gap_time
        self.idle_time = idle_time
        self.end_time = end_time
        self.dead_time = dead_time

        self.state = State.idle
        self.old_state = State.idle
        self.count = 0

        self.buf = deque(maxlen=buflen)
        self.buf.extend([0,0])

        self.spikeTimer = BinaryStateTimer()
        self.spinTimer = BinaryStateTimer()
        self.highTimer = BinaryStateTimer()
        self.idleTimer = BinaryStateTimer()
        self.stateTimer = BinaryStateTimer()

    def reset(self):
        self.__init__()
    
    def change_state(self, to):
        # print("%s -> %s" % (self.state, to))
        self.old_state = self.state
        self.state = to
        self.stateTimer.process(False)
        if self.state == State.idle:
            self.count = 0
    
    def _process_sample(self, sample):

        self.buf.append(sample)
        self.count += 1
        if (self.count < self.dead_time):
            return LaundryState.NONE
        
        mn = min(self.buf)
        mx = max(self.buf)

        qtl = st.quantiles(self.buf,n=4,method='inclusive')
        iqr = qtl[2]-qtl[0]
        spike = (mx-mn)/(1+iqr)

        spike_time = self.spikeTimer.process(spike > self.spike_th)
        high_time = self.highTimer.process(mn > self.high_th)
        spin_time = self.spinTimer.process(mn > self.spin_th and iqr < self.flat_th)
        idle_time = self.idleTimer.process(mx < self.idle_th)

        state_time = self.stateTimer.process(True)

        if self.state == State.idle:
            if spike > self.trig_th:
                self.change_state(State.start)

        elif self.state == State.start:
            if spike_time > self.spike_time:
                self.change_state(State.spikes)
            elif high_time > self.high_time:
                self.change_state(State.high)

        elif self.state == State.spikes:
            if high_time > self.high_time:
                self.change_state(State.high)

        elif self.state == State.high:
            if spin_time > self.spin_time:
                self.change_state(State.spin)
            elif spike_time > self.spike_time:
                self.change_state(State.spikes)

        elif self.state == State.spin:
            if spike_time > self.spike_time:
                self.change_state(State.spikes)
            elif mx < self.high_th:
                self.change_state(State.gap)

        elif self.state == State.gap:
            if state_time > self.gap_time and mx < self.high_th:
                self.change_state(State.idle)
            if sample > self.high_th:
                self.change_state(State.end)

        elif self.state == State.end:
            if state_time > self.end_time or sample < self.high_th:
                self.change_state(State.idle)

        if (self.state != State.idle) and idle_time > self.idle_time:
            self.change_state(State.idle)

        return LaundryState.NONE if self.state == State.idle else LaundryState.WASH

if __name__ == "__main__":
    p = StateSignalProcessor()
    p.test_stdin()
