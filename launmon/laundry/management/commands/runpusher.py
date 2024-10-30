
from django.core.management.base import BaseCommand, CommandError
from pywebpush import webpush, WebPushException
from requests.exceptions import Timeout

from laundry.models import Location, Subscription

import laundry.vapidsecrets as vapidsecrets

import redis
import json

def push_main(subscription={},data={}):
    try:
        webpush(
            subscription_info=subscription,
            data=json.dumps(data),
            vapid_private_key=vapidsecrets.PRIVKEY,
            vapid_claims={
                    "sub": vapidsecrets.EMAIL,
                },
                timeout=1)
    except WebPushException as ex:
        # print("I'm sorry, Dave, but I can't do that: {}", repr(ex))
        # Mozilla returns additional information in the body of the response.
        print(f"web push failed: {ex}")
        Subscription.objects.filter(endpoint=subscription['endpoint']).delete()
    except Timeout:
        pass

class Webpusher:
    def __init__(self):
        self.redis = redis.Redis()
        self.p = self.redis.pubsub(ignore_subscribe_messages=True)
        self.p.psubscribe("launmon-status:*")

    def run(self):
        for msg in self.p.listen():

            _, location = str.split(msg['channel'].decode(),':')
            trans = msg['data'].decode()
            try:
                from_state,to_state = trans.split(":")
            except ValueError:
                from_state = "none"
                to_state = trans
                
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

            for s in Subscription.objects.filter(location=loc).all():
                sub = json.loads(s.subscription)
                payload['location'] = loc.name
                push_main(sub,payload)

            # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            #     futures = []

            #     for s in Subscription.objects(location=loc).all():
            #         sub = json.loads(s.subscription)
            #         payload['location'] = loc.nickname

            #         futures.append(executor.submit(push_main,sub,payload))
            #     for f in futures:
            #         try:
            #             res = f.result()
            #             print(res)
            #         except Exception:
            #             print(sub['endpoint'])
            #             db.deleteSubscription(sub['endpoint'],location)
 

class Command(BaseCommand):
    help = "Run the webpush daemon"

    def handle(self, *args, **options):
        w = Webpusher()
        w.run()
