from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.cache import cache_page
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from .models import Location, Issue, Subscription, UserSite, Site, Event, Rawcurrent
from .forms import ReportForm, FixForm

from datetime import datetime, timezone, timedelta
from laundry import vapidsecrets
import qrcode

def get_back_link(request):
    try:
        redirect_url = request.GET['from']
        print(f"from {redirect_url}")
    except KeyError:
        redirect_url = reverse("index")

    return redirect_url

@login_required
def index(request):
    try:
        message = request.GET['message']
    except Exception:
        message = None

    try:
        siteid = request.GET['site']
        request.session["site"] = siteid
    except Exception:
        siteid = None

    print(f"siteid={siteid}")

    user = request.user
    try:
        sites = [u.site_id for u in UserSite.objects.filter(user=user)]
        qs = Site.objects.filter(pk__in=sites)
        sites = qs.all()
        if siteid is not None:
            site = Site.objects.filter(id=siteid).first()
        else:
            try:
                site = Site.objects.filter(id=request.session['site']).first()
            except Exception:
                site = qs.first()

        locs = Location.objects.filter(site=site)
        print(site)
    except Exception as e:
        print(e)
        locs = []
        sites = None
        site = None

    print(f"sites={sites}")
    print(f"site={site}")

    nsections = len(set([l.section for l in locs]))
    
    context = {"locations": locs, "sites": sites, "site": site, "nsections": nsections, "message": message, "message_type": 0}

    return render(request,"laundry/index.html",context)

def vapid_pubkey(request):
    return HttpResponse(vapidsecrets.PUBKEY)

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
                    "name": loc.name,
                    "site": loc.site.name,
                    "section": loc.section.name if loc.section is not None else "",
                    "type": loc.type.name,
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

    return render(request,"laundry/details.html", {"location":loc,"events":events,"day":0,"message": message},)

def timeline(request, location=None):
    loc = Location.objects.get(pk=location)
    events = Event.objects.filter(location=loc)

    return render(request,"laundry/timeline.html", {"location":loc,"events":events},)

def cycles_json(request):

    loc = request.GET['location']
    hrs = request.GET['hours']

    cycles = Event.get_cycles(loc,hrs)
    print(cycles)

    ret = [{'start': c[0],'end': c[1],'type': c[2]} for c in cycles]

    return JsonResponse({'cycles':ret})

def rawcurrent_json(request):
    loc = request.GET['location']
    try:
        start = datetime.strptime(request.GET['start'], "%Y-%m-%dT%H:%M:%S.%f%Z")
        end = datetime.strptime(request.GET['end'], "%Y-%m-%dT%H:%M:%S.%f%Z")
    except Exception as e:
        start = None
        end = None
    try:
        dur_min = request.GET['minutes']
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
    us.site = Site.objects.get(pk=sitekey)
    try:
        us.save()
    except Exception as e:
        print(e)

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

