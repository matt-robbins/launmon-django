
from django.urls import path

from . import views
from django.views.generic import TemplateView


urlpatterns = [
    path("", views.index, name="index"),
    path("json", views.index_json, name="json"),
    path("report", views.report, name="report"),
    path("issues", views.issues, name="issues"),
    path("issues/<str:location>", views.issues, name="issues"),
    path("fix/<str:issue>", views.issue_fix),
    path("issues/fix/<str:issue>", views.issue_fix),
    path("subscribe", views.subscribe, name="subscribe"),
    path("unsubscribe", views.unsubscribe, name="unsubscribe"),
    path("check-subscription", views.check_subscription, name="check-subscription"),
    path('webpush.js', (TemplateView.as_view(template_name="laundry/webpush.js", 
        content_type='application/javascript', )), name='webpush.js'),
    path('util.js', (TemplateView.as_view(template_name="laundry/util.js", 
        content_type='application/javascript', )), name='util.js'),
    path('status.js', (TemplateView.as_view(template_name="laundry/status.js", 
        content_type='application/javascript', )), name='status.js'),
]