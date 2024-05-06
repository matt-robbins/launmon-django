
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("report", views.report, name="report"),
    path("issues", views.issues, name="issues"),
    path("issues/<str:location>", views.issues, name="issues"),
    path("issue_fix/<int:id>", views.issue_fix)
]