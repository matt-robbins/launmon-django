from .HeuristicSignalProcessor import HeuristicSignalProcessor
from .SimpleSignalProcessor import SimpleSignalProcessor
from .StateSignalProcessor import StateSignalProcessor
from .SignalProcessor import State
import os
import sys

class ProcessorFactory:

    PROCESSORS = {
        'generic': {'class': SimpleSignalProcessor, 'args': {}},
        'generic_dryer': {'class': SimpleSignalProcessor, 'args': {}},
        'generic_washer': {'class': SimpleSignalProcessor, 'args': {}},
        'whirlpool_washer': {
            'class': StateSignalProcessor,'args': {'trig_thresh':0.05, 
                'high_thresh': 0.5, 
                'spike_thresh': 1.0,
                'spin_thresh': 2.0,
                'flat_thresh': 0.05, 
                'idle_thresh': 0.15,
                'spike_time': 100,
                'high_time': 20,
                'spin_time': 20,
                'gap_time': 150,
                'end_time': 20,
                'idle_time': 200,
                'buflen': 30,
                'dead_time': 60}},
        'maytag_stack': {
            'class': HeuristicSignalProcessor, 'args': {
                'spike_max':1.0, 
                'spike_th':0.05, 
                'wash_th':0.25, 
                'dry_th':5, 
                'idle_time':30, 
                'both_idle_time':30}},
    }

    def get_default(self):
        return 'generic'
    
    def get_choices(self):
        names = self.PROCESSORS.keys()
        ret = {n: n.replace('_',' ').title() for n in names}
        return ret

    def get_processor(self,type):
        try:
            return self.PROCESSORS[type]['class'](**self.PROCESSORS[type]['args'])
        except KeyError:
            raise ValueError("no processor for machine type '%s'" % type)

    def read_labels(self,file):
        ret = {}
        try:
            with open(file) as f:
                for line in f:
                    ln, state = [s.strip() for s in line.split(":")]
                    ret[int(ln)] = State(int(state))

        except FileNotFoundError:
            pass
        return ret

    def test_files(self,type=None):
        if (type is None or type == 'ALL'):
            for type in self.PROCESSORS.keys():
                self.test_files(type)
            return
        
        p = self.get_processor(type)    
        directory = os.path.join(os.path.dirname(__file__),'data',type)

        for file in os.listdir(directory):
            ext = os.path.splitext(file)[1]
            if ext in ['.labels', '.py'] or os.path.isdir(file):
                continue
            
            labels = self.read_labels(file+".labels")

            ds = State.NONE
            s = State.NONE

            equal_count = 0
            count = 0
            transitions = 0

            with open(os.path.join(directory,file)) as f:
                p.reset()
                ns = s
                for line in f:
                    ns = p.process_sample(float(line))

                    try:
                        ds = labels[count]
                    except KeyError:
                        pass

                    count += 1
                    if (ns is not None):
                        print("%d: %s (%s)" %(count,ns.name,ds.name))
                        s = ns
                        transitions += 1
                    if (s == ds):
                        equal_count += 1

            print("accuracy: %d%%" %(100*equal_count / count,))
            print(equal_count/count > 0.95)
            print(transitions <= len(labels.keys())+1)

if __name__ == "__main__":
    type = None
    if len(sys.argv) > 1:
        type = sys.argv[1]
    p = ProcessorFactory()

    p.test_files(type)