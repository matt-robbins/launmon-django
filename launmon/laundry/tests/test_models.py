from django.test import TestCase
from laundry.models import Location, Rawcurrent, Event, Site, Device
from datetime import datetime,timezone,timedelta
from django.db.models import Avg, F, Window
from django.db.models.functions import Lag


t1 = datetime.fromisoformat("2024-01-01T10:00:00.0Z")
t2 = t1-timedelta(minutes=1)

class CurrentTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        l1 = Location.objects.create(name="machine1")
        l2 = Location.objects.create(name="machine2")

        Event.objects.create(location=l1,time=t1-timedelta(hours=2),status="none")
        Event.objects.create(location=l1,time=t1-timedelta(hours=1),status="dry")
        Event.objects.create(location=l1,time=t1-timedelta(minutes=45),status="both")
        Event.objects.create(location=l1,time=t1-timedelta(minutes=44),status="both") # oopsy LOL
        Event.objects.create(location=l1,time=t1-timedelta(minutes=33),status="offline")
        Event.objects.create(location=l1,time=t1-timedelta(minutes=29),status="both")
        Event.objects.create(location=l1,time=t1-timedelta(minutes=15),status="wash")
        Event.objects.create(location=l1,time=t1,status="none")

        Event.objects.create(location=l2,time=t2-timedelta(hours=2),status="none")
        Event.objects.create(location=l2,time=t2-timedelta(hours=1),status="dry")
        Event.objects.create(location=l2,time=t2-timedelta(minutes=45),status="both")
        Event.objects.create(location=l2,time=t2-timedelta(minutes=15),status="dry")
        Event.objects.create(location=l2,time=t2,status="none")

    def setUp(self):
        pass

    def test_cycle_query(self):
        l = Location.objects.get(name='machine1')

        cycles = Event.get_cycles2(l.pk,t1-timedelta(hours=1), t1-timedelta(minutes=14))

        for cycle in cycles:
            print(f"{cycle['type']}: {cycle['start']} -- {cycle['end']}")
        self.assertTrue(cycles[0]['start'] is None)
        self.assertTrue(cycles[0]['end'] == t1-timedelta(minutes=15))
        self.assertTrue(cycles[0]['type'] == 'dry')

        self.assertTrue(cycles[1]['start'] == t1-timedelta(minutes=45))
        self.assertTrue(cycles[1]['end'] is None)
        self.assertTrue(cycles[1]['type'] == 'wash')

    # def test_false_is_true(self):
    #     print("Method: test_false_is_true.")
    #     self.assertTrue(False)

    # def test_one_plus_one_equals_two(self):
    #     print("Method: test_one_plus_one_equals_two.")
    #     self.assertEqual(1 + 1, 2)
