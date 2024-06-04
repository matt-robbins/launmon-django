from .SignalProcessor import State, SignalProcessor

class SimpleSignalProcessor(SignalProcessor):
    def __init__(self, thresh=0.5, timeout=5, type='dryer'):
        super().__init__()

        self.thresh = thresh
        self.type = type
        self.state = State.NONE
        self.active_state = State.DRY
        self.timeout = timeout

        self.count = 0

        if (self.type == 'washer'):
            self.active_state = State.WASH

    def reset(self):
        self.count = 0
        self.state = State.NONE

    def _process_sample(self, sample):                        
        new_state = self.state
        
        if (self.state == State.NONE):
            self.count = 0
            if (sample > self.thresh):
                new_state = self.active_state

        elif (self.state == self.active_state):

            self.count = (self.count + 1 if sample < self.thresh else 0)
            
            if (sample < self.thresh and self.count > self.timeout):
                new_state = State.NONE

        self.state = new_state
        return new_state

if __name__ == "__main__":
    p = SimpleSignalProcessor()
    p.test_stdin()
