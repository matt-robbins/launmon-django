from django.db import models, connection
from datetime import datetime, timezone, timedelta
from django.core.cache import cache
from django.contrib.auth.models import User
from Processors.ProcessorFactory import ProcessorFactory


class Site(models.Model):
    name = models.TextField()
    address = models.TextField(null=True)
    def __str__(self):
        return self.name
    
class UserSite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    def __str__(self):
        return "%s -> %s"%(self.user.username,self.site.name)
    
class Section(models.Model):
    class Meta:
        ordering = ["site", "display_order", "name"]
    name = models.CharField(max_length=32)
    display_order = models.IntegerField(blank=True,null=True)
    site = models.ForeignKey(Site,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.name

class LocationType(models.Model):
    factory = ProcessorFactory()

    name = models.TextField()
    type = models.TextField(default='dryer', choices={'W':"washer", "D": "dryer", "S": "stack"})
    processor = models.TextField(choices=factory.get_choices(), default=factory.get_default())
    def __str__(self):
        return self.name

class Location(models.Model):
    class Meta:
        ordering = ["site", "section", "display_order", "name"]
    name = models.CharField(blank=True, null=True, max_length=32)
    tzoffset = models.IntegerField(blank=True, null=True)
    lastseen = models.DateTimeField(blank=True, null=True)
    type = models.ForeignKey(LocationType, on_delete=models.PROTECT, null=True)
    site = models.ForeignKey(Site, on_delete=models.PROTECT, null=True,blank=True)
    section = models.ForeignKey(Section, on_delete=models.PROTECT, null=True,blank=True)
    display_order = models.IntegerField(blank=True,null=True)

    def __str__(self):
        if (self.name is not None):
            ret = self.name
        else:
            ret = str(self.id)

        return ret
    
    def write_lastseen(pk=None):
        cache.set("%s_lastseen:%s"%(Location.__name__,pk), datetime.now(tz=timezone.utc))

    def latest_time(self):
        try:
            return Event.objects.filter(location=self).order_by("-time")[0].time
        except IndexError as e:
            print(e)
            return None
    
    def latest_status(self):
        lastseen = cache.get("%s_lastseen:%s"%(Location.__name__,self.pk))
        if lastseen is None:
            lastseen = datetime.now(tz=timezone.utc) - timedelta(seconds=86100)

        issue = self.latest_issue()
        if (issue is not None and issue.ooo == True):
            return 'ooo'

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
    location = models.OneToOneField(Location, on_delete=models.CASCADE, null=True, blank=True)
    port = models.CharField(blank=True, null=True, max_length=6)
    calibration = models.FloatField(blank=True, null=True)
    cal_pow = models.FloatField(blank=True, null=True)
    changed = models.DateTimeField(blank=True, null=True, auto_now=True)
    site = models.ForeignKey(Site, on_delete=models.PROTECT, null=True, blank=True)

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
        if (self.location is not None):
            self.site = self.location.site
        super().save(*args, **kwargs)  # Call the "real" save() method.

        self.cache_write()

class Calibration(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    calibration = models.FloatField(blank=True, null=True)


class Rawcurrent(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['time'], name='time_idx'),
        ]
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    current = models.FloatField(null=True)
    time = models.DateTimeField()


class Event(models.Model):
    EVENT_STATUS_CHOICES = {
        "wash": "washing",
        "dry": "drying",
        "both": "both",
        "none": "idle",
        "offline": "offline",
        "ooo": "out of order"
    }
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    status = models.TextField(blank=True, null=True, choices=EVENT_STATUS_CHOICES)
    time = models.DateTimeField(blank=True, null=True) 

    def status_str(str):
        try:
            return Event.EVENT_STATUS_CHOICES[str]
        except Exception:
            return "unknown"

    def get_histogram(location, dow):
        table_name = Event.objects.model._meta.db_table
        sql = f"""SELECT EXTRACT(HOUR FROM time) AS hour, count(*)/12.0 perhour
                FROM {table_name} 
                WHERE location_id=%s 
                AND EXTRACT(DOW FROM time)=%s 
                GROUP BY hour ORDER BY hour;
                """

        with connection.cursor() as cursor:
            cursor.execute(sql, [location, dow])
            rows = cursor.fetchall()
            ret = [0]*24
            for r in rows:
                ret[int(r[0])] = float(r[1])

            return ret

class Issue(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.PROTECT, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    code = models.TextField(blank=True, null=True)
    ooo = models.BooleanField(blank=True, null=True)
    time = models.DateTimeField(unique=True, blank=True, null=True)  
    fix_description = models.TextField(blank=True, null=True)
    fix_time = models.DateTimeField(blank=True, null=True) 

    def save(self, *args, **kwargs):
        if (self.location is not None):
            self.site = self.location.site
        super().save(*args, **kwargs)  # Call the "real" save() method.


class Subscription(models.Model):
    endpoint = models.TextField(blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    subscription = models.TextField(blank=True, null=True)

