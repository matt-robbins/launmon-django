from django.contrib import admin
from django import forms
from django_reverse_admin import ReverseModelAdmin

# Register your models here.
from laundry.models import Device,Site,Location,LocationType,Calibration,Event,Rawcurrent,Issue,Subscription,UserSite
from django.contrib.auth.models import User


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = "__all__"
    device = forms.ModelChoiceField(queryset=Device.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
    
class DeviceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['location'].queryset = Location.objects.filter(site=self.instance.site)


class DeviceInline(admin.TabularInline):
    # form = DeviceAdminInlineForm
    model = Device

class LocationAdmin(admin.ModelAdmin):
    form = LocationForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        sites=[s.site for s in UserSite.objects.filter(user=request.user)]

        return qs.filter(site__in=sites)
    
class DeviceAdmin(admin.ModelAdmin):
    form=DeviceForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        sites=[s.site for s in UserSite.objects.filter(user=request.user)]
        return qs.filter(site__in=sites)


class IssueAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        sites=[s.site for s in UserSite.objects.filter(user=request.user)]
        return qs.filter(site__in=sites)

admin.site.register(Site)
admin.site.register(Location, LocationAdmin)
admin.site.register(LocationType)
admin.site.register(Device, DeviceAdmin)
admin.site.register(Calibration)
admin.site.register(Event)
admin.site.register(Rawcurrent)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Subscription)
admin.site.register(UserSite)

