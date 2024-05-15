from django.contrib import admin

# Register your models here.
from laundry.models import Device,Site,Location,LocationType,Calibration,Event,Rawcurrent,Issue,Subscription,UserSite

admin.site.register(Site)
admin.site.register(Location)
admin.site.register(LocationType)
admin.site.register(Device)
admin.site.register(Calibration)
admin.site.register(Event)
admin.site.register(Rawcurrent)
admin.site.register(Issue)
admin.site.register(Subscription)
admin.site.register(UserSite)

