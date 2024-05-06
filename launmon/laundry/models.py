from django.db import models

class Location(models.Model):
    location = models.TextField(primary_key=True, blank=True)
    nickname = models.TextField(blank=True, null=True)
    tzoffset = models.IntegerField(blank=True, null=True)
    lastseen = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'locations'

    def __str__(self):
        if (self.nickname is not None):
            return self.nickname
        
        return self.location
    
    def latest_status(self):
        return Event.objects.filter(location=self).order_by("-time")[0]
    
    def latest_issue(self):
        issues = Issue.objects.filter(location=self).filter(fix_time__isnull=True).order_by("-time")
        try:
            return issues[0]
        except IndexError:
            return None
    
class Device(models.Model):
    device = models.CharField(primary_key=True, blank=True, max_length=16)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, db_column="location")
    port = models.CharField(blank=True, null=True, max_length=6)
    calibration = models.FloatField(blank=True, null=True)
    cal_pow = models.FloatField(blank=True, null=True)
    changed = models.DateTimeField(blank=True, null=True) 

    class Meta:
        db_table = 'devices'

    def __str__(self):
        return self.device

class Calibration(models.Model):
    id = models.IntegerField(primary_key=True, db_column="ROWID")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, db_column="location")
    calibration = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'calibration'

class Rawcurrent(models.Model):
    id = models.IntegerField(primary_key=True,db_column='ROWID')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, db_column="location")
    current = models.FloatField(blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'rawcurrent'

class Event(models.Model):
    EVENT_STATUS_CHOICES = {
        "wash": "washing",
        "dry": "drying",
        "both": "both",
        "none": "idle"
    }
    id = models.IntegerField(primary_key=True,db_column='ROWID')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, db_column="location")
    status = models.TextField(blank=True, null=True, choices=EVENT_STATUS_CHOICES)
    time = models.DateTimeField(blank=True, null=True) 

    class Meta:
        db_table = 'events'


class Issue(models.Model):
    id = models.IntegerField(primary_key=True, db_column="ROWID")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, db_column="location")
    description = models.TextField(blank=True, null=True)
    code = models.TextField(blank=True, null=True)
    time = models.DateTimeField(unique=True, blank=True, null=True)  
    fix_description = models.TextField(blank=True, null=True)
    fix_time = models.DateTimeField(blank=True, null=True) 

    class Meta:
        db_table = 'issues'

class Subscription(models.Model):
    id = models.IntegerField(primary_key=True, db_column="ROWID")
    endpoint = models.TextField(blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, db_column="location")
    subscription = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'subscriptions'
