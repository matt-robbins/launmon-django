from django.contrib import admin

# Register your models here.
from laundry.models import Device,Location,Calibration,Event,Rawcurrent,Issue,Subscription

admin.site.register(Location)
admin.site.register(Device)
admin.site.register(Calibration)
admin.site.register(Event)
admin.site.register(Rawcurrent)
admin.site.register(Issue)
admin.site.register(Subscription)

