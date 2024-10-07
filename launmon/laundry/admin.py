from django.contrib import admin
from django import forms

# Register your models here.
from laundry.models import Device,Site,Section,Location,LocationType,Calibration,Event,Rawcurrent,Issue,Subscription,UserSite

from django.contrib.auth.admin import UserAdmin
from Accounts.models import User

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = "__all__"
    device = forms.ModelChoiceField(queryset=Device.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sites = [usersite.site for usersite in UserSite.objects.filter(user=self.current_user)]
        site_ids = [s.id for s in sites]

        self.fields['site'].queryset = Site.objects.filter(pk__in=site_ids)
        self.fields['device'].queryset = Device.objects.filter(site=self.instance.site)

        try:
            self.fields['device'].initial = Device.objects.get(location=self.instance)
        except Exception as e:
            print("init: %s"%e)

    def save(self,commit=True):
        try:
            old_device = Device.objects.get(location=self.instance)
            old_device.location = None
            old_device.save()
        except Exception as e:
            pass
        try:

            device_str = self.cleaned_data.get('device', None)

            device = Device.objects.get(device=device_str)
            device.location = self.instance
            device.save()
        except Exception as e:
            print("save(): %s"%e)

        return super(LocationForm,self).save(commit=commit)
    
class LocationAdmin(admin.ModelAdmin):
    form = LocationForm
    list_display = ("pk", "name", "site")

    def get_form(self, request, obj=None, **kwargs):
        form = super(LocationAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        sites=[s.site for s in UserSite.objects.filter(user=request.user)]

        return qs.filter(site__in=sites)
    
class DeviceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sites = [usersite.site for usersite in UserSite.objects.filter(user=self.current_user)]
        site_ids = [s.id for s in sites]

        print(sites)
        if self.current_user.is_superuser:
            return
        
        self.fields['site'].queryset = Site.objects.filter(pk__in=site_ids)
        self.fields['location'].queryset = Location.objects.filter(site=self.instance.site)
    
class DeviceAdmin(admin.ModelAdmin):
    form=DeviceForm
    list_display = ("device", "location", "site")

    def get_form(self, request, obj=None, **kwargs):
        form = super(DeviceAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        sites=[s.site for s in UserSite.objects.filter(user=request.user)]
        return qs.filter(site__in=sites)

class IssueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sites = [usersite.site for usersite in UserSite.objects.filter(user=self.current_user)]
        site_ids = [s.id for s in sites]

        print(sites)
        if self.current_user.is_superuser:
            return
        
        self.fields['site'].queryset = Site.objects.filter(pk__in=site_ids)
        self.fields['location'].queryset = Location.objects.filter(site=self.instance.site)

class IssueAdmin(admin.ModelAdmin):
    exclude = ["site","location"]

    list_display = ("location", "description", "code", "site")

    def has_add_permission(self, request):
        return False
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        sites=[s.site for s in UserSite.objects.filter(user=request.user)]
        return qs.filter(site__in=sites)
    
class EventAdmin(admin.ModelAdmin):
    list_display = ("location","status","time")

class RawcurrentAdmin(admin.ModelAdmin):
    list_display = ("location","current","time")

class SectionAdmin(admin.ModelAdmin):
    list_display = ("name","site")

class UserSiteAdmin(admin.ModelAdmin):
    list_display = ("user", "site", "sesame_key")

admin.site.register(Site)
admin.site.register(Section, SectionAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(LocationType)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Calibration)
admin.site.register(Event, EventAdmin)
admin.site.register(Rawcurrent,RawcurrentAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Subscription)
admin.site.register(UserSite, UserSiteAdmin)
admin.site.register(User, UserAdmin)

