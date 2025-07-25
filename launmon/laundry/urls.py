
from django.urls import path

from . import views
from django.views.generic import TemplateView


urlpatterns = [
    path("", views.index, name="index"),
    path("details/<str:location>", views.details, name="details"),
    path("timeline/<str:location>", views.timeline, name="timeline"),
    path("notify/<str:location>", views.push_notify, name="push_notify"),
    path("vapid-pubkey", views.vapid_pubkey, name="vapid-pubkey"),
    path("json", views.index_json, name="json"),
    path("histogram-json", views.histogram_json, name="histogram_json"),
    path("cycles-json", views.cycles_json, name="cycles_json"),
    path("rawcurrent-json", views.rawcurrent_json, name="current_json"),
    path("report/<str:location>", views.report, name="report"),
    path("issues", views.issues, name="issues"),
    path("issues/<str:location>", views.issues, name="issues"),
    path("fix/<str:issue>", views.issue_fix),
    path("add-site", views.add_site, name="add-site"),
    path("gen-qr/<str:site>", views.gen_qr, name="gen-qr"),
    path("site-qr", views.site_qr, name="site-qr"),
    path("issues/fix/<str:issue>", views.issue_fix, name="issue-fix"),
    path("subscribe", views.subscribe, name="subscribe"),
    path("unsubscribe", views.unsubscribe, name="unsubscribe"),
    path("check-subscription", views.check_subscription, name="check-subscription"),
    path('webpush.js', (TemplateView.as_view(template_name="laundry/webpush.js", 
        content_type='application/javascript', )), name='webpush.js'),
    path('util.js', (TemplateView.as_view(template_name="laundry/util.js", 
        content_type='application/javascript', )), name='util.js'),
    path('status.js', (TemplateView.as_view(template_name="laundry/status.js", 
        content_type='application/javascript', )), name='status.js'),
    path('status.css', views.status_css, name='status.css'),
]