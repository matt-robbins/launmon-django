from rest_framework import permissions, viewsets, filters
from laundry.models import Location, Site, Issue, LocationType
from django_filters.rest_framework import DjangoFilterBackend
from laundry.serializers import LocationSerializer, SiteSerializer, IssueSerializer, LocationTypeSerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['site']
    def get_queryset(self):
        queryset = self.queryset
        us = Site.objects.filter(usersite__user=self.request.user)
        query_set = queryset.filter(site__in=us)

        return query_set
    
    def list(self, request):
        print(f"overridden 'list' function! ${request}")
        resp = super().list(request)
        print(f'response of length ${resp}')
        return resp


class LocationTypeViewSet(viewsets.ModelViewSet):
    queryset = LocationType.objects.all()
    serializer_class = LocationTypeSerializer
    permission_classes = [permissions.IsAuthenticated]

class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated]

class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated]