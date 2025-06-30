"""A2SL URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from . import views

admin.site.site_header = "Voice to ISL Converter Admin"
admin.site.site_title = "Voice to ISL Converter Admin Portal"
admin.site.index_title = "Welcome to Voice to ISL Converter Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('animation/', views.animation_view, name='animation'),
    path('manual/',views.manual_view, name='manual'),
    path('', views.home_view, name='home'),
    path('gesture/', views.gesture_input_view, name='gesture'),
    path('gesture-feed/', views.gesture_feed_view, name='gesture_feed'),

]

