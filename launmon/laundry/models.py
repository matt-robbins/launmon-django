from django.db import models
from datetime import datetime, timezone, timedelta
from django.core.cache import cache
from django.contrib.auth.models import User


class Site(models.Model):
    name = models.TextField()
    address = models.TextField(null=True)
    def __str__(self):
        return self.name
    
class UserSite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

class LocationType(models.Model):
    name = models.TextField()
    def __str__(self):
        return self.name

class Location(models.Model):
    nickname = models.TextField(blank=True, null=True)
    tzoffset = models.IntegerField(blank=True, null=True)
    lastseen = models.DateTimeField(blank=True, null=True)
    type = models.ForeignKey(LocationType, on_delete=models.PROTECT, null=True)
    site = models.ForeignKey(Site, on_delete=models.PROTECT, null=True)

    def __str__(self):
        if (self.nickname is not None):
            return self.nickname
        
        return str(self.id)
    
    def write_lastseen(pk=None):
        cache.set("%s_lastseen:%s"%(Location.__name__,pk), datetime.now(tz=timezone.utc))

    def latest_time(self):
        try:
            return Event.objects.filter(location=self).order_by("-time")[0].time
        except IndexError:
            return None
    
    def latest_status(self):
        lastseen = cache.get("%s_lastseen:%s"%(Location.__name__,self.pk))
        if lastseen is None:
            lastseen = datetime.now(tz=timezone.utc) - timedelta(seconds=86100)

        if (datetime.now(tz=timezone.utc)-lastseen).total_seconds() > 60:
            return 'offline'

        try:
            return Event.objects.filter(location=self).order_by("-time")[0].status
        except Exception as e:
            return 'none'
    
    def latest_issue(self):
        issues = Issue.objects.filter(location=self).filter(fix_time__isnull=True).order_by("-time")
        try:
            return issues[0]
        except IndexError:
            return None
        
    def get_baseline_current(self):
        # use the cache cause this is expensive
        cache_key = "%s_baseline:%s"%(Location.__name__,self.pk)

        baseline = cache.get(cache_key)
        if (baseline is not None):
            return baseline

        # grab 10th percentile of current data. This will provide some kind of measure of baseline
        secs_per_day = 86400
        pct_ix = int(secs_per_day / 10)
        qs = Rawcurrent.objects.filter(location=self).filter(
            time__gt=datetime.now(tz=timezone.utc)-timedelta(seconds=secs_per_day)
            ).order_by(
                'current').all()
        
        baseline = 1.0
        if len(qs) == 0:
            return baseline
        try:
            baseline = qs[pct_ix].current
        except IndexError:
            baseline = qs[0].current

        cache.set(cache_key, baseline)
        return baseline

    
class Device(models.Model):
    device = models.CharField(primary_key=True, blank=True, max_length=16)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, null=True, blank=True)
    port = models.CharField(blank=True, null=True, max_length=6)
    calibration = models.FloatField(blank=True, null=True)
    cal_pow = models.FloatField(blank=True, null=True)
    changed = models.DateTimeField(blank=True, null=True, auto_now=True) 

    def cache_write(self):
        key = "%s_%s:%s"%(Device.__name__,Location.__name__,self.device)
        val = None
        if (self.location):
            val = self.location.pk

        cache.set(key, val, timeout=None)

        key = "%s_%s:%s"%(Device.__name__,"calibration",self.device)
        cache.set(key,self.calibration,timeout=None)
        key = "%s_%s:%s"%(Device.__name__,"cal_pow",self.device)
        cache.set(key,self.cal_pow,timeout=None)


    def __str__(self):
        return self.device
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.
        self.cache_write()

class Calibration(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    calibration = models.FloatField(blank=True, null=True)


class Rawcurrent(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    current = models.FloatField(null=True)
    time = models.DateTimeField()


class Event(models.Model):
    EVENT_STATUS_CHOICES = {
        "wash": "washing",
        "dry": "drying",
        "both": "both",
        "none": "idle"
    }
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    status = models.TextField(blank=True, null=True, choices=EVENT_STATUS_CHOICES)
    time = models.DateTimeField(blank=True, null=True) 


class Issue(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    code = models.TextField(blank=True, null=True)
    time = models.DateTimeField(unique=True, blank=True, null=True)  
    fix_description = models.TextField(blank=True, null=True)
    fix_time = models.DateTimeField(blank=True, null=True) 


class Subscription(models.Model):
    endpoint = models.TextField(blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    subscription = models.TextField(blank=True, null=True)

