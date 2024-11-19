"""
URL configuration for launmon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from laundry import views as launviews
from sesame.views import LoginView

from rest_framework import routers

from laundry import rest_views

router = routers.DefaultRouter()
router.register(r'locations', rest_views.LocationViewSet)
router.register(r'location-types', rest_views.LocationTypeViewSet)
router.register(r'sites', rest_views.SiteViewSet)
router.register(r'issues', rest_views.IssueViewSet)


urlpatterns = [
    path('', include("laundry.urls")),
    path('v1/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('accounts/', include("allauth.urls")),
    path("laundry/", include("laundry.urls")),
    path("sesame/login/", LoginView.as_view(), name="sesame-login"),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('sw.js', (TemplateView.as_view(template_name="laundry/sw.js", 
        content_type='application/javascript', )), name='sw.js'),
]
