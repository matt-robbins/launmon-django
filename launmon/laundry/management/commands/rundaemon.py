
import asyncio
import aiomqtt
from daemon.DataMuncher import DataMuncher
from datetime import datetime
import daemon.mqttsecrets as secrets

import os.path
from datetime import datetime, timezone
import traceback
import sys
from laundry.models import Device

from django.core.management.base import BaseCommand, CommandError

async def mqtt_main(muncher):
    print("calling mqtt_main")
    async with aiomqtt.Client(secrets.HOST,username=secrets.USER,password=secrets.PASS) as client:
        
        await client.subscribe("+/sensor/current/state")
        async for msg in client.messages:
            try:
                sample = float(msg.payload.decode())
            except ValueError:
                print("bad message %s" % msg.payload)
                continue
            try: 
                device = msg.topic.value.split("/")[0].split('-')[-1]
                await muncher.process_sample(device,sample,datetime.now(tz=timezone.utc))

            except Device.DoesNotExist:
                continue

            except Exception as e:
                print("yoopsy: %s" % e)
                traceback.print_exc(file=sys.stdout)
                await asyncio.sleep(1)

        

async def checker(muncher):
    while True:
        await muncher.checkOffline(datetime.now(tz=timezone.utc))
        await asyncio.sleep(10)

class Command(BaseCommand):
    help = "Run the parser daemon"

    def handle(self, *args, **options):

        m = DataMuncher()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # loop = asyncio.get_event_loop()

        # t = loop.create_datagram_endpoint(lambda: V2Protocol(m), local_addr=('0.0.0.0', 5555))
        # loop.run_until_complete(t)

        loop.create_task(mqtt_main(m))
        loop.create_task(checker(m))
        loop.run_forever()