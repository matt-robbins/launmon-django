
from datetime import datetime, timedelta
from daemon.HeuristicSignalProcessor import HeuristicSignalProcessor, SimpleSignalProcessor
from daemon.DataSink import CurrentSink, StatusSink

import os.path
from datetime import datetime, timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '..launmon.settings')

import django
django.setup()

from laundry.models import Location, Device

from asgiref.sync import sync_to_async
from django.core.cache import cache


OFFLINE_THRESHOLD_S = 10

class DataMuncher:

    @sync_to_async
    def checkOffline(self,time=datetime.now(tz=timezone.utc)):
        
        for loc in self.locations:
            td = time - loc.lastseen

            if (td > timedelta(seconds=OFFLINE_THRESHOLD_S)):
                if (self.event_sink):
                    self.event_sink.process_data(loc, "offline", time)
    
    @sync_to_async
    def process_sample(self, device, data, time):
        loc_id = cache.get("%s_%s:%s"%(Device.__name__,Location.__name__,device))
                           
        # print("%s->%s"%(device,loc_id))
        if loc_id is None:
            return
    
        cache.set("%s_lastseen:%s"%(Location.__name__,loc_id), datetime.now(tz=timezone.utc))

        if (self.cur_sink):
            self.cur_sink.process_data(loc_id,data,time)

        only_diff = (time - self.lastseen[loc_id]).total_seconds() < OFFLINE_THRESHOLD_S
        self.lastseen[loc_id] = time

        cal = cache.get("%s_calibration:%s"%(Device.__name__,device))
        if cal is None:
            cal = 1.0

        cpow = cache.get("%s_cal_pow:%s"%(Device.__name__,device))
        if cpow is None:
            cpow = 1.0

        if not cpow == 1.0:
            data = pow(data,cpow)

        status = self.processors[loc_id].process_sample(data*cal, only_diff=only_diff)
        if status is None:
            return
        
        if (self.event_sink):
            self.event_sink.process_data(loc_id, status.name.lower(), time)


    def __init__(self, cur_sink=CurrentSink(),event_sink=StatusSink()):

        self.locations = Location.objects.all()
        self.devices = Device.objects.all()
        self.cur_sink = cur_sink
        self.event_sink = event_sink

        for device in self.devices:
            device.cache_write()


        self.lastseen = {}
        self.processors = {}
        now = datetime.now(tz=timezone.utc)
        for loc in self.locations:
            if loc.type.name == 'stack':
                self.processors[loc.pk] = HeuristicSignalProcessor()
            else:
                self.processors[loc.pk] = SimpleSignalProcessor(thresh=0.2,type=loc.type.name)
            self.lastseen[loc.pk] = now - timedelta(days=1)

