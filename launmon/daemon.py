import os.path
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launmon.settings')

import django
django.setup()

from laundry.models import Rawcurrent, Event, Location, Device

loc = Device.objects.get(device='00000006').location
r = Rawcurrent(current=1,time=datetime.datetime.now(datetime.timezone.utc), location=loc)
print(r.current,r.time)
r.save()