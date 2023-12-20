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
    path("",views.dashboard_system_info,name="dashboard_main"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("sys_info/",views.system_info,name="sysinformation"),
    path("installed_apps/",views.installed_apps,name="installed_apps"),
    path("windows_license/",views.windows_info,name="windowslic"),
    path('custom_license',views.upload_csv,name="custom_license"),
    path('custom_license_update',views.custom_license_update,name="custom_license_update"),
    path('receive_windows_information/', views.receive_windows_information, name='receive_windows_information'),
    path('receive_system_usage/', views.receive_system_usage, name='receive_system_usage'),
    path('license_data/', views.license_data_view, name='license_data'),
    path('system-status/', views.receive_system_status, name='receive_system_status'),
    path('system-status_view/', views.system_status_view, name='system_status_view'),
     path('export_csv/', views.export_csv, name='export_csv'),
    # path('update_system_status/', views.update_system_status, name='update_system_status'),
    #firewall path
    path('create/', views.firewall_create, name='firewall_create'),
    path('create1/', views.firewall_create1, name='firewall_create1'),
    path('list/', views.firewall_list, name='firewall_list'),
    path('list1/', views.firewall_list1, name='firewall_list1'),
    path('<int:pk>/edit/', views.firewall_edit, name='firewall_edit'),
    path('<int:pk>/edit1/', views.firewall_edit1, name='firewall_edit1'),
    path('<int:pk>/delete/', views.firewall_delete, name='firewall_delete'),
    path('<int:pk>/delete1/', views.firewall_delete1, name='firewall_delete1'),
    path('device_detail/<str:mac_address>/', views.device_detail, name='device_detail'),
    path('monitoring-data/', views.monitoring_data_view, name='monitoring_data'),
    path('linux_detail/<str:mac_address>/', views.linux_detail, name='linux_detail'),
    path('router/',views.routerview,name='router'),
     path('router_detail/<str:Name>/', views.router_detail, name='router_detail'),
      path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'), 
    path('upload_and_display_log/', views.upload_and_display_log, name='upload_and_display_log'),
    
    
    
    ### change of the roles and their path
     path("windows_license1/",views.windows_info1,name="windowslic1"),
     path('monitoring-data1/', views.monitoring_data_view1, name='monitoring_data1'),
    path('linux_detail1/<str:mac_address>/', views.linux_detail1, name='linux_detail1'),
    path('license_data1/', views.license_data_view1, name='license_data1'),
    path('custom_license1',views.upload_csv1,name="custom_license1"),
    path('device_detail1/<str:mac_address>/', views.device_detail1, name='device_detail1'),
    path('system-status_view1/', views.system_status_view1, name='system_status_view1'),
]
