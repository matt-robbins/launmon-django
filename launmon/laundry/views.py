from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.cache import cache_page
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required

from .models import Location, Issue, Subscription, UserSite, Event, Rawcurrent
from .forms import ReportForm, FixForm

from datetime import datetime, timezone


@login_required
def index(request):
    try:
        message = request.GET['message']
    except Exception:
        message = None

    user = request.user
    try:
        sites = [u.site_id for u in UserSite.objects.filter(user=user)]
        locs = Location.objects.filter(site__in=sites)
    except Exception as e:
        locs = []
        sites = None
    
    context = {"locations": locs, "sites": sites, "message": message}

    return render(request,"laundry/index.html",context)

@cache_page(60 * 15)
def status_css(request):
    return render(request, "laundry/status.css", {'map': Event.EVENT_STATUS_CHOICES}, content_type="text/css")

def index_json(request):
    locs = Location.objects.all()
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


def details(request, location=None):
    try:
        message = request.GET['message']
    except Exception:
        message = None

    loc = Location.objects.get(pk=location)
    events = Event.objects.filter(location=loc)

    return render(request,"laundry/details.html", {"location":loc,"events":events,"day":0,"message": message}, )

def histogram_json(request):
    loc = request.GET['location']
    dow = request.GET['weekday']
    jso = {"histogram": Event.get_histogram(location=loc,dow=dow)}

    return JsonResponse(jso)

def report(request, location=None):
    form = ReportForm()
    try:
        redirect_url = request.GET['from']
        print(f"from {redirect_url}")
    except KeyError:
        redirect_url = reverse("index")

    context = {"form": form, "next_url": redirect_url}


    if request.method == "GET":
        return render(request,"laundry/report.html", context)
    elif request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            obj = Issue()
            obj.description = form.cleaned_data['issue']
            obj.code = form.cleaned_data['code']
            obj.location = Location.objects.get(pk=location)
            obj.site = obj.location.site
            obj.time = datetime.now(timezone.utc)
            obj.save()
            return HttpResponseRedirect(redirect_url+'?message=Issue Reported!')
        
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

            obj = Issue.objects.get(pk=issue)
            obj.fix_description = form.cleaned_data['fix_description']
            obj.fix_time = datetime.now(timezone.utc)
            obj.save()

            return HttpResponseRedirect(reverse("index")+'?message=Issue Marked Fixed!')

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

