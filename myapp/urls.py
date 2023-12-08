"""SIH URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from . import views
from django.urls import path

urlpatterns = [
    # path("",views.homepage,name="homepage"),
    path("main/",views.mainhtml,name="mainpage"),
    path("",views.dashboard_system_info,name="dashboard"),
    path("sys_info/",views.system_info,name="sysinformation"),
    path("installed_apps/",views.installed_apps,name="installed_apps"),
    path("windows_license/",views.windows_info,name="windowslic"),
]
