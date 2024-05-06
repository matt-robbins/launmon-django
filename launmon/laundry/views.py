from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

from django.shortcuts import render

from .models import Location, Issue
from .forms import ReportForm, FixForm

from datetime import datetime, timezone

def index(request):
    locs = Location.objects.order_by("nickname")
    context = {"locations": locs}

    return render(request,"laundry/index.html",context)

def report(request):
    form = ReportForm()
    context = {"form": form}

    if request.method == "GET":
        return render(request,"laundry/report.html", context)
    elif request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            obj = Issue()
            obj.description = form.cleaned_data['issue']
            obj.code = form.cleaned_data['code']
            obj.location = Location.objects.get(pk=form.cleaned_data['location'])
            obj.time = datetime.now(timezone.utc)
            obj.save()
            return render(request,"laundry/report_confirm.html")
        
def issues(request,location=None):
    if location is not None:
        issues = Issue.objects.filter(location=location).order_by("-time")
    else:
        issues = Issue.objects.order_by("-time")
    context = {"issues": issues}
    return render(request,"laundry/issues.html", context)

def issue_fix(request,id=0):
    form = FixForm()
    context = {"form": form, "issue_id": id}
    if request.method == "GET":
        return render(request,"laundry/issue_fix.html", context)
    elif request.method == "POST":
        form = FixForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)

            obj = Issue.objects.get(pk=id)
            obj.fix_description = form.cleaned_data['fix_description']
            obj.fix_time = datetime.now(timezone.utc)
            obj.save()

            return render(request, "laundry/report_confirm.html")

    return
