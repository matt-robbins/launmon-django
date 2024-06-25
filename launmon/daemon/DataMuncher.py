
from datetime import datetime, timedelta, timezone
from daemon.DataSink import CurrentSink, StatusSink

from laundry.models import Location, Device, Rawcurrent
from Processors.ProcessorFactory import ProcessorFactory

from asgiref.sync import sync_to_async
from django.core.cache import cache


OFFLINE_THRESHOLD_S = 10

class DataMuncher:
    lastseen = {}
    processors = {}
    record = {}

    @sync_to_async
    def checkOffline(self,time=datetime.now(tz=timezone.utc)):

        self.reload()
        
        for loc in self.locations:

            lastseen = cache.get("%s_lastseen:%s"%(Location.__name__,loc.pk))
            try:
                td = time - lastseen
            except TypeError:
                print(f"location {loc} was never seen")
                td = timedelta(seconds=86400)
                pass

            if (td > timedelta(seconds=OFFLINE_THRESHOLD_S)):
                if (self.event_sink):
                    self.event_sink.process_data(loc.pk, "offline", time)
    
    @sync_to_async
    def process_sample(self, device, data, time):
        loc_id = cache.get("%s_%s:%s"%(Device.__name__,Location.__name__,device))
                           
        # print("%s->%s"%(device,loc_id))
        if loc_id is None:
            return
        
        cache.set("%s_lastseen:%s"%(Location.__name__,loc_id), time)

        if (self.cur_sink):
            self.cur_sink.process_data(loc_id,data,time, record=self.record[loc_id])

        # if it's been offline, return status directly
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

    def reload(self):
        self.locations = Location.objects.all()
        self.devices = Device.objects.all()

        for device in self.devices:
            device.cache_write()

        now = datetime.now(tz=timezone.utc)

        for loc in self.locations:
            #handle location changes or additions
            if not loc in self.processors.keys() or self.processors[loc.pk] != loc.type:
                self.processors[loc.pk] = self.factory.get_processor(loc.type.processor)
                self.lastseen[loc.pk] = now - timedelta(days=1)
                self.record[loc.pk] = loc.record_enable
            

    def __init__(self, cur_sink=CurrentSink(),event_sink=StatusSink()):
        self.cur_sink = cur_sink
        self.event_sink = event_sink
        self.factory = ProcessorFactory()
        self.reload()
