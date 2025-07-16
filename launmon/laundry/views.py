from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import json
from redis import Redis
from daemon.DataSink import RedisPublisher
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from .models import Location, Issue, Subscription, UserSite, Site, Event, Rawcurrent
from .forms import ReportForm, FixForm

from datetime import datetime, timezone, timedelta
from laundry import vapidsecrets
import qrcode

from .serializers import LocationSerializer

def get_back_link(request):
    try:
        redirect_url = request.GET['from']
        print(f"from {redirect_url}")
    except KeyError:
        redirect_url = reverse("index")

    return redirect_url

def get_request_user_and_sites(request, refresh=False):
    try:
        siteid = request.GET['site']
        request.session["site"] = siteid
    except Exception:
        siteid = None

    user = request.user

    try:
        qs = Site.objects.filter(usersite__user=user)
        sites = qs.all()
        if siteid is not None:
            site = Site.objects.filter(id=siteid).first()
        else:
            try:
                site = Site.objects.filter(id=request.session['site']).first()
            except Exception:
                site = qs.first()

        locs = Location.objects.filter(site=site)
    except Exception as e:
        print(e)
        locs = []
        sites = None
        site = None

    return (locs,sites,site)

def get_location_dict(locs):
    return [loc.to_dict() for loc in locs]

@login_required
def index(request):
    locs,sites,site = get_request_user_and_sites(request)

    try:
        message = request.GET['message']
    except Exception:
        message = None

    nsections = len(set([l.section for l in locs]))

    # locd = site.to_dict() if site else []

    locd = LocationSerializer(Location.objects.filter(site_id=site), many=True).data
    context = {"locations": locd, "sites": sites, "site": site, "nsections": nsections, "message": message, "message_type": 0}

    ret = render(request, "laundry/index.html", context)
    return ret

def vapid_pubkey(request):
    return HttpResponse(vapidsecrets.PUBKEY)

@cache_page(60 * 15)
def status_css(request):
    return render(request, "laundry/status.css", {'map': Event.EVENT_STATUS_CHOICES}, content_type="text/css")


def index_json(request):
    locs,_,site = get_request_user_and_sites(request)
    #locs = Location.objects.all()
    locd = site.to_dict() if site else []
    return JsonResponse(locd, safe=False)


def details(request, location=None):
    try:
        message = request.GET['message']
    except Exception:
        message = None

    loc = LocationSerializer(Location.objects.get(pk=location)).data
    events = Event.objects.filter(location_id=location)

    return render(request,"laundry/details.html", {"location":loc,"events":events,"day":0,"message": message},)

def timeline(request, location=None):
    loc = Location.objects.get(pk=location)
    events = Event.objects.filter(location=loc)

    return render(request,"laundry/timeline.html", {"location":loc,"events":events},)

def push_notify(request, location=None):
    p = RedisPublisher()
    #r = Redis()
    p.publish(['remind', location], "notify")
    #r.publish(f"launmon-status:{location}","notify")
    return JsonResponse({'status': 'ok'})

def cycles_json(request):

    loc = request.GET['location']
    try:
        hrs = int(request.GET['hours'])
    except Exception as e:
        hrs = 96

    cycles = Event.get_cycles2(loc,datetime.now(timezone.utc)-timedelta(hours=hrs),datetime.now(timezone.utc))

    return JsonResponse({'cycles':cycles})

def rawcurrent_json(request):
    loc = request.GET['location']
    try:
        start = datetime.strptime(request.GET['start'], "%Y-%m-%dT%H:%M:%S.%fZ")
    except Exception as e:
        start = None
    try:
        end = datetime.strptime(request.GET['end'], "%Y-%m-%dT%H:%M:%S.%fZ")
    except Exception as e:
        end = datetime.now(timezone.utc)

    try:
        dur_min = int(request.GET['minutes'])
    except Exception as e:
        dur_min = None

    if all([start is None, end is None]):
        dur_min = 30

    if dur_min is not None:
        end = datetime.now(timezone.utc)
        start = end - timedelta(minutes=dur_min)

    print(f"{start}-{end}")
    
    cur = Rawcurrent.objects.filter(location=loc).filter(time__lt=end).filter(time__gt=start).order_by('time').values()

    dict = {"time": [c['time'] for c in cur], "current": [c['current'] for c in cur]}

    return JsonResponse(dict)


def histogram_json(request):
    loc = request.GET['location']
    dow = request.GET['weekday']
    jso = {"histogram": Event.get_histogram(location=loc,dow=dow)}

    return JsonResponse(jso)

def report(request, location=None):
    form = ReportForm()
    redirect_url = get_back_link(request)
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

    redirect_url = get_back_link(request)
    context = {"issues": issues, "next_url": redirect_url}
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

@login_required
def add_site(request):
    user = request.user
    print(user)
    try:
        sitekey = request.GET['site-key']
    except Exception:
        sitekey = None
    
    if sitekey is None:
        return HttpResponseRedirect(reverse('index')+"?message=You don't have permission to add this site!")
    
    us = UserSite()
    us.user = user
    try:
        us.site = Site.objects.get(pk=sitekey)
    except Exception as e:
        return HttpResponseRedirect(reverse('index')+"?message=Invalid site key!")
    try:
        us.save()
    except Exception as e:
        return HttpResponseRedirect(reverse('index')+"?message=You're already following this site!")

    return HttpResponseRedirect(reverse('index')+f'?message=Added {us.site.name}!')

@staff_member_required
def gen_qr(request,site):

    url = request.build_absolute_uri(f'/laundry/add-site?site-key={site}')
    print(url)
    img = qrcode.make(url)
    resp = HttpResponse(content_type="image/png")
    img.save(resp,"PNG")

    return resp

@staff_member_required
def site_qr(request):
    sites = Site.objects.all()
    return render(request,"laundry/qrcode.html",{'sites': sites})



def subscribe(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        ep = data['subscription']['endpoint']
        sub = json.dumps(data['subscription'])
        loc = data['machine']

        Subscription(endpoint=ep,location=Location.objects.get(pk=loc),subscription=sub).save()

        k = f'location-serializer:{loc}'
        print(f"sub: deleting {k}")

        cache.delete(k)

        p = RedisPublisher()
        p.publish(["subscriber",loc],"sub")

        return HttpResponse("")
    return HttpResponse(status=204)

def unsubscribe(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        ep = data['endpoint']
        loc = data['machine']

        k = f'location-serializer:{loc}'
        print(f"unsub: deleting {k}")

        cache.delete(k)

        p = RedisPublisher()
        p.publish(["subscriber",loc],"un")

        # just in case it gets signed up multiple times...
        Subscription.objects.filter(location=loc,endpoint=ep).all().delete()
        return HttpResponse("")
    return HttpResponse(status=204)

def check_subscription(request,endpoint=""):
    endpoint = request.GET['url']
    try:
        val = []
        for s in Subscription.objects.filter(endpoint=endpoint).all():
            count = s.location.subscriber_count()
            val.append({"subscription": s.subscription,
                "count": count,
                "location": s.location.pk,
                "endpoint": s.endpoint})
    except Exception as e:
        print(e)
        val = {}
    
    return JsonResponse(val,safe=False)

