
import asyncio
import aiomqtt
from daemon.DataMuncher import DataMuncher
from datetime import datetime
import daemon.mqttsecrets as secrets

import time
from datetime import datetime, timezone
import traceback
import sys
from laundry.models import Device

from django.core.management.base import BaseCommand, CommandError

async def mqtt_main(devices,rate):
    async with aiomqtt.Client(secrets.HOST,username=secrets.USER,password=secrets.PASS) as client:

        while True:
            for d in devices:
                await client.publish(f"launmon-{d}/sensor/current/state", payload=0.0)
            await asyncio.sleep(rate)

class Command(BaseCommand):
    help = "Send data to mqtt, mocking all sensors"

    def add_arguments(self, parser):
        parser.add_argument("rate", type=float)

    def handle(self, *args, **options):

        rate = options['rate']
        devices = [d.device for d in Device.objects.all()]


        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(mqtt_main(devices,rate))

        loop.run_forever()


