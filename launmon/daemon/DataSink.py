from redis import Redis

from laundry.models import Rawcurrent, Event, Location, Device
from django.db import transaction

from datetime import datetime, timezone, timedelta


class DataSink:
    def process_data(self,location,data,time):
        pass
    def __init__(self):
        pass

class Publisher:
    def publish(channel,data):
        pass
    def __init__(Self):
        pass

class RedisPublisher(Publisher):
    def publish(self,channel,data):
        channel = ':'.join([str(c) for c in channel])
        try:
            self.r.publish(channel,data)
        except Exception as e:
            print ("failed to publish data %s" % e)
            pass
    def __init__(self):
        self.r = Redis()

class CurrentSink(DataSink):
    # We batch current data to reduce number of db transactions
    def process_data(self,loc_id,data,time, record=True):
        self.publisher.publish([self.channel,str(loc_id)],data)
        if not record:
            return
        
        cur = Rawcurrent(current=data,location_id=loc_id,time=time)
        self.buf.append(cur)

        if (len(self.buf) > self.bufsize):
            self.save_buf()

    @transaction.atomic
    def save_buf(self):
        Rawcurrent.objects.filter(time__lt=datetime.now(tz=timezone.utc)-timedelta(days=2)).delete()

        while len(self.buf) > 0:
            cur = self.buf.pop()
            cur.save()
            
    def __init__(self,channel="current", publisher=RedisPublisher(), bufsize=100):
        self.channel=channel
        self.publisher=publisher
        self.buf = []
        self.bufsize = bufsize


class StatusSink(DataSink):
    def process_data(self,loc_id,data,time):
        location = Location.objects.get(pk=loc_id)
        
        status = data
        try:
            oldstatus = location.event_set.order_by('-time').first().status
        except AttributeError:
            oldstatus = "none"
        
        if (oldstatus == status):
            return
        
        print("machine %s changed state: %s" % (location, status))
        
        event = Event(location=location,status=status,time=time)
        event.save()

        if location.is_ooo():
            return

        self.publisher.publish([self.channel,location.pk], oldstatus+":"+status)

    def __init__(self,channel="status", publisher=RedisPublisher()):
        self.channel=channel
        self.publisher = publisher
