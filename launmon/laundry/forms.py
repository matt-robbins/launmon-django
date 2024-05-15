
from django import forms
from .models import Location, Issue

class NameForm(forms.Form):
    your_name = forms.CharField(label="Your name", max_length=100)

class ReportForm(forms.Form):
    location = forms.ModelChoiceField(queryset=Location.objects.order_by("nickname"))
    issue = forms.CharField(widget=forms.Textarea())
    code = forms.CharField()

class FixForm(forms.Form):
    fix_description = forms.CharField(widget=forms.Textarea())
