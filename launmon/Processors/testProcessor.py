import unittest
from Processors.ProcessorFactory import ProcessorFactory
from Processors.SignalProcessor import State
#from HistogramSignalProcessor import HistogramSignalProcessor
import os

class TestProcessor(unittest.TestCase):
    def setUp(self):
        self.factory = ProcessorFactory()  
        self.p = self.factory.get_processor('maytag_stack')
    
    def read_labels(self, file):
        ret = {}
        try:
            with open(file+'.labels') as f:
                for line in f:
                    ln, state = [s.strip() for s in line.split(":")]
                    ret[int(ln)] = State(int(state))

        except FileNotFoundError:
            pass
        return ret

    def test_files(self):
        dir = os.path.dirname(os.path.realpath(__file__)) + "/data/maytag_stack"
        
        for file in os.listdir(dir):
            if ('.labels' in file or file.startswith('.')):
                continue

            labels = self.read_labels(os.path.join(dir,file))

            print(file)
            ds = State.NONE
            s = State.NONE

            equal_count = 0
            count = 0
            transitions = 0

            with open(os.path.join(dir,file)) as f:
                self.p.reset()
                self.p.cal = 1.0
                for line in f:
                    ns = self.p.process_sample(float(line))

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
            self.assertTrue(equal_count/count > 0.95)
            self.assertTrue(transitions <= len(labels.keys())+1)
