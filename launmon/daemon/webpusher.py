#!/usr/bin/env python
import redis
import json
from pywebpush import webpush, WebPushException
from requests.exceptions import Timeout
import concurrent.futures

import os.path
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'launmon.settings')

import django
django.setup()

from laundry.models import Rawcurrent, Event, Location, Device, Subscription

def push_main(subscription={},data={}):
    try:
        webpush(
            subscription_info=subscription,
            data=json.dumps(data),
            vapid_private_key="m1Wni8qP-jjDa0jPaczGSZRsulQHAm5olCv7bXO81Go",
            vapid_claims={
                    "sub": "mailto:matthew.robbins@gmail.com",
                },
                timeout=1)
    except WebPushException as ex:
        # print("I'm sorry, Dave, but I can't do that: {}", repr(ex))
        # Mozilla returns additional information in the body of the response.
        raise Exception("web push failed: %s" % ex)
    except Timeout:
        pass

class Webpusher:
    def __init__(self):
        self.redis = redis.Redis()
        self.p = self.redis.pubsub(ignore_subscribe_messages=True)
        self.p.psubscribe("status:*")

    def run(self):
        for msg in self.p.listen():

            _, location = str.split(msg['channel'].decode(),':')
            trans = msg['data'].decode()

            from_state,to_state = trans.split(":")

            event_text = ""
            sass = "Get it!"
            if (trans in ["none:wash", "dry:both"]):
                event_text = "Washer Started"
                sass = "Woohoo!"
            elif (trans in ["none:dry","wash:both"]):
                event_text = "Dryer Started"
                sass = "Okay!"
            elif (trans in ["both:wash","dry:none"]):
                event_text = "Dryer Done"
                sass = "Get it while it's hot!"
            elif (trans in ["both:dry","wash:none"]):
                event_text = "Washer Done"
                sass = "Squeaky Clean!"
            elif (trans == "both:none"):
                event_text = "Done"
            elif (to_state == "offline"):
                event_text = "Went Offline"
                sass = "Oh no!"
            elif (to_state == "ooo"):
                event_text = "Is Out of Order"
                sass = "Oh no!"
            elif (from_state == "offline"):
                event_text = "Came Back Online"
                sass = "Yay!!"
            elif (from_state == "ooo"):
                event_text = "Is Back"
                sass = "Yay!!"

            payload = {"location":"","message":event_text, "sass":sass}

            loc = Location.objects.get(id=location)

            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = []

                for s in Subscription.objects(location=loc).all():
                    sub = json.loads(s.subscription)
                    payload['location'] = loc.nickname

                    futures.append(executor.submit(push_main,sub,payload))
                for f in futures:
                    try:
                        res = f.result()
                        print(res)
                    except Exception:
                        print(sub['endpoint'])
                        db.deleteSubscription(sub['endpoint'],location)
 
        
if __name__ == "__main__":
    w = Webpusher()
    w.run()