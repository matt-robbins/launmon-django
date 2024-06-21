from enum import Enum
import sys
import math

class State(Enum):
    OFFLINE = -1
    NONE = 0
    WASH = 1
    DRY = 2
    BOTH = 3


class SignalProcessor:
    def __init__(self):
        self._state = State.NONE
        self._count = 0
        self.type = None

    def reset(self):
        self._state = State.NONE

    def _process_sample(self,sample):
        return self._state
    
    def process_sample(self, sample, only_diff=True):
        self._count += 1
        # use nan to represent a gap in data
        if math.isnan(sample):
            print("NAN!!!!")
            old_state = self._state
            if (self._state != State.NONE):
                self.reset()
                self._state = State.NONE
            return None if (only_diff or old_state == self._state) else self._state

        new_state = self._process_sample(sample)
        if new_state != self._state:
            self._state = new_state
            return self._state
        
        return None if only_diff else self._state
    
    def test_stdin(self):
        lc = 0
        for line in sys.stdin:

            ns = self.process_sample(float(line))
            lc += 1
            if (ns is not None):
                print("%d: %s" % (lc,ns.value))
