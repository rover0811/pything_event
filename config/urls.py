"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from common import views as common_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', common_views.home, name='home'),
    path('about/', common_views.about, name='about'),
    path('posts/', common_views.posts, name='posts'),
    path('events/', common_views.events, name='events'),
    path('people/', common_views.people, name='people'),
    path('api/users/', include('users.urls')),  # users URL 추가
    path('api/locations/', include('locations.urls')),  # locations URL 추가
    path('api/presentations/', include('presentations.urls')),
    path('api/', include('events.urls')),  # events URL 추가
]
