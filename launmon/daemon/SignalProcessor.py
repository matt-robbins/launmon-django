

from enum import Enum

class State(Enum):
    OFFLINE = -1
    NONE = 0
    WASH = 1
    DRY = 2
    BOTH = 3

class SignalProcessor:
    def __init__(self):
        self.state = State.NONE
    def reset(self):
        self.state = State.NONE
    def process_sample(self, sample, only_diff=True):
        return self.state
