
from django import forms
from .models import Location, Issue

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login


class NameForm(forms.Form):
    your_name = forms.CharField(label="Your name", max_length=100)

class ReportForm(forms.Form):
    location = forms.ModelChoiceField(queryset=Location.objects.order_by("nickname"))
    issue = forms.CharField(widget=forms.Textarea())
    code = forms.CharField()

class FixForm(forms.Form):
    fix_description = forms.CharField(widget=forms.Textarea())

class RegisterForm(forms.Form):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """

    username = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = ["username"]

    def save(self, commit=True):
        print(self.cleaned_data)
        user = User.objects.create(username=self.cleaned_data['username'])
        user.set_unusable_password()
        if commit:
            user.save()
        user = authenticate(self.cleaned_data['username'], password=None)
        return user