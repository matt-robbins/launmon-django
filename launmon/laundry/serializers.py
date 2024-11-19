from rest_framework import serializers
from laundry.models import Location, LocationType, Site, Issue

class IssueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Issue
        fields = ['pk','description','code','ooo','time','fix_description','fix_time']

class LocationTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LocationType
        fields = ['pk','name','type']

class SiteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Site
        fields = ['pk', 'name', 'address']   

class LocationSerializer(serializers.ModelSerializer):
    issues = IssueSerializer(many=True)
    latest_issue = IssueSerializer()
    latest_time = serializers.DateTimeField()
    type = LocationTypeSerializer()
    site = SiteSerializer()
    class Meta:
        model = Location
        fields = ['pk', 'site', 'name', 'type', 'issues', 'latest_issue', 'latest_status','latest_time']


 

