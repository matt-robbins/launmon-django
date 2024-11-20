
from django.core.cache import cache

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from laundry.models import Location, Event, Issue
from .serializers import LocationSerializer
from django.core.signals import request_finished


@receiver(post_save, sender=Event)
def eventSaved(sender, **kwargs):
    if not 'instance' in kwargs.keys():
        return 
    try:
        LocationSerializer().to_representation(kwargs['instance'].location,refresh=True)
    except Exception as e:
        print(f'exception during eventSaved signal receiver {kwargs}')

@receiver(post_save, sender=Issue)
def issueSaved(sender, **kwargs):
    if not 'instance' in kwargs.keys():
        return 
    try:
        LocationSerializer().to_representation(kwargs['instance'].location,refresh=True)
    except Exception as e:
        print(f'exception during issueSaved signal receiver {kwargs}')

request_finished.connect(eventSaved, dispatch_uid="unique")
request_finished.connect(issueSaved, dispatch_uid="unique")