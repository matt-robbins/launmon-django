from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
import json

from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required

from .models import Location, Issue, Subscription, Site, UserSite
from .forms import ReportForm, FixForm

from datetime import datetime, timezone

@login_required
def index(request):
    user = request.user
    site = UserSite.objects.get(user=user).site
    locs = Location.objects.filter(site=site).order_by("nickname")
    context = {"locations": locs}

    return render(request,"laundry/index.html",context)

def index_json(request):
    locs = Location.objects.order_by("nickname")
    jso = []
    for loc in locs:
        try:
            datestr = loc.latest_time().isoformat()
        except AttributeError:
            datestr = None

        jso.append({"location": loc.pk, 
                    "status": loc.latest_status(), 
                    "issues": loc.latest_issue() is not None, 
                    "lastseen": datestr})

    return JsonResponse(jso, safe=False)

def report(request):
    form = ReportForm()
    context = {"form": form}

    if request.method == "GET":
        return render(request,"laundry/report.html", context)
    elif request.method == "POST":
        form = ReportForm(request.POST)
        print(form)
        if form.is_valid():
            obj = Issue()
            obj.description = form.cleaned_data['issue']
            obj.code = form.cleaned_data['code']
            obj.location = Location.objects.get(pk=form.cleaned_data['location'].pk)
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

def issue_fix(request,issue=None):
    form = FixForm()
    context = {"form": form, "issue_id": id}
    if request.method == "GET":
        return render(request,"laundry/issue_fix.html", context)
    elif request.method == "POST":
        form = FixForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)

            obj = Issue.objects.get(pk=form.cleaned_data['issue'].id)
            obj.fix_description = form.cleaned_data['fix_description']
            obj.fix_time = datetime.now(timezone.utc)
            obj.save()

            return render(request, "laundry/report_confirm.html")

    return

def subscribe(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        ep = data['subscription']['endpoint']
        sub = json.dumps(data['subscription'])
        loc = data['machine']

        Subscription(endpoint=ep,location=Location.objects.get(pk=loc),subscription=sub).save()

        return HttpResponse("")
    return HttpResponse(status=204)

def unsubscribe(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        ep = data['endpoint']
        loc = data['machine']
        # just in case it gets signed up multiple times...
        Subscription.objects.filter(location=loc,endpoint=ep).all().delete()
        return HttpResponse("")
    return HttpResponse(status=204)

def check_subscription(request,endpoint=""):
    endpoint = request.GET['url']
    try:
        val = []
        for s in Subscription.objects.filter(endpoint=endpoint).all():
            val.append({"subscription": s.subscription,
                "location": s.location.pk,
                "endpoint": s.endpoint})
    except Exception as e:
        print(e)
        val = {}
    
    return JsonResponse(val,safe=False)

